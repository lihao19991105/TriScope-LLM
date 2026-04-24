"""Minimal illumination probe for TriScope-LLM."""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer


SUPPORTED_DTYPE_MAP: dict[str, torch.dtype] = {
    "float32": torch.float32,
    "float16": torch.float16,
    "bfloat16": torch.bfloat16,
}


@dataclass
class ModelProfile:
    profile_name: str
    model_id: str
    local_path: str | None
    backend_type: str
    dtype: str
    max_length: int
    device: str
    device_map: str | None


@dataclass
class GenerationProfile:
    max_new_tokens: int
    do_sample: bool
    temperature: float


@dataclass
class IlluminationProfile:
    profile_name: str
    prompt_template_name: str
    alpha: float
    query_budget: int
    num_icl_examples: int
    candidate_query_source: str
    generation: GenerationProfile


@dataclass
class PromptTemplate:
    template_name: str
    description: str
    instruction: str
    clean_example_label: str
    backdoor_example_label: str
    query_label: str
    response_label: str


@dataclass
class ExampleRecord:
    sample_id: str
    prompt: str
    response: str
    source_kind: str
    trigger_type: str
    target_type: str
    target_text: str
    raw_record: dict[str, Any]


@dataclass
class ProbeResult:
    prompt_id: str
    sample_id: str
    model_profile: str
    prompt_template_name: str
    target_type: str
    trigger_type: str
    alpha: float
    budget: int
    prompt_text: str
    response_text: str
    is_target_behavior: bool
    metadata: dict[str, Any]


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_yaml_profile(config_path: Path, profile_name: str) -> dict[str, Any]:
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or profile_name not in payload:
        raise ValueError(f"Profile `{profile_name}` not found in `{config_path}`.")
    profile = payload[profile_name]
    if not isinstance(profile, dict):
        raise ValueError(f"Profile `{profile_name}` in `{config_path}` must be a mapping.")
    return profile


def load_model_profile(config_path: Path, profile_name: str) -> ModelProfile:
    profile = load_yaml_profile(config_path=config_path, profile_name=profile_name)
    required_fields = ["model_id", "backend_type", "dtype", "max_length", "device"]
    missing = [field for field in required_fields if field not in profile]
    if missing:
        raise ValueError(
            f"Model profile `{profile_name}` is missing required fields: {', '.join(missing)}."
        )
    return ModelProfile(
        profile_name=profile_name,
        model_id=str(profile["model_id"]),
        local_path=str(profile["local_path"]) if profile.get("local_path") is not None else None,
        backend_type=str(profile["backend_type"]),
        dtype=str(profile["dtype"]),
        max_length=int(profile["max_length"]),
        device=str(profile["device"]),
        device_map=str(profile["device_map"]) if profile.get("device_map") is not None else None,
    )


def load_illumination_profile(config_path: Path, profile_name: str) -> IlluminationProfile:
    profile = load_yaml_profile(config_path=config_path, profile_name=profile_name)
    generation = profile.get("generation", {})
    alpha = float(profile.get("alpha", 0.5))
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("Illumination `alpha` must be between 0 and 1.")
    return IlluminationProfile(
        profile_name=profile_name,
        prompt_template_name=str(profile.get("prompt_template_name", "minimal_v1")),
        alpha=alpha,
        query_budget=int(profile.get("query_budget", 8)),
        num_icl_examples=int(profile.get("num_icl_examples", 4)),
        candidate_query_source=str(profile.get("candidate_query_source", "clean_only")),
        generation=GenerationProfile(
            max_new_tokens=int(generation.get("max_new_tokens", 32)),
            do_sample=bool(generation.get("do_sample", False)),
            temperature=float(generation.get("temperature", 0.0)),
        ),
    )


def load_prompt_template(prompt_dir: Path, template_name: str) -> PromptTemplate:
    template_path = prompt_dir / f"{template_name}.yaml"
    if not template_path.is_file():
        raise ValueError(f"Prompt template `{template_name}` not found in `{prompt_dir}`.")
    payload = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Prompt template `{template_path}` must be a mapping.")
    return PromptTemplate(
        template_name=str(payload.get("template_name", template_name)),
        description=str(payload.get("description", "")),
        instruction=str(payload.get("instruction", "")).strip(),
        clean_example_label=str(payload.get("clean_example_label", "Clean Example")),
        backdoor_example_label=str(payload.get("backdoor_example_label", "Targeted Example")),
        query_label=str(payload.get("query_label", "Final Query")),
        response_label=str(payload.get("response_label", "Answer")),
    )


def resolve_dtype(dtype_name: str, device: str) -> torch.dtype:
    if device == "cpu" and dtype_name in {"float16", "bfloat16"}:
        return torch.float32
    return SUPPORTED_DTYPE_MAP.get(dtype_name, torch.float32)


def resolve_runtime_device(requested_device: str) -> str:
    if requested_device.startswith("cuda") and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object on line {line_number} of `{path}`.")
            rows.append(payload)
    return rows


def resolve_dataset_path(manifest_path: Path, manifest: dict[str, Any]) -> Path:
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("Manifest field `artifacts` must be an object.")
    dataset_ref = artifacts.get("poisoned_dataset")
    if not isinstance(dataset_ref, str):
        raise ValueError("Manifest field `artifacts.poisoned_dataset` must be a string path.")
    dataset_path = Path(dataset_ref)
    if dataset_path.is_absolute():
        return dataset_path
    candidates = [
        Path.cwd() / dataset_path,
        manifest_path.parent / dataset_path,
        manifest_path.parent.parent / dataset_path,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return (Path.cwd() / dataset_path).resolve()


def build_example_from_dataset_record(record: dict[str, Any]) -> ExampleRecord:
    attack_metadata = record.get("attack_metadata", {})
    if not isinstance(attack_metadata, dict):
        raise ValueError(f"Record `{record.get('sample_id', 'unknown')}` has invalid `attack_metadata`.")
    sample_id = str(record["sample_id"])
    if record.get("is_poisoned") is True:
        prompt = str(record["poisoned_prompt"] or record["train_prompt"])
        response = str(record["poisoned_response"] or record["train_response"])
        source_kind = "backdoor_example"
    else:
        prompt = str(record["clean_prompt"])
        response = str(record["clean_response"])
        source_kind = "clean_example"
    return ExampleRecord(
        sample_id=sample_id,
        prompt=prompt,
        response=response,
        source_kind=source_kind,
        trigger_type=str(attack_metadata.get("trigger_type", "unknown")),
        target_type=str(attack_metadata.get("target_type", "unknown")),
        target_text=str(attack_metadata.get("target_text", "")),
        raw_record=record,
    )


def load_query_contracts_from_file(query_file: Path) -> list[dict[str, Any]]:
    rows = load_jsonl(query_file)
    required_fields = {"sample_id", "clean_examples", "backdoor_examples", "test_query"}
    for index, row in enumerate(rows):
        missing = sorted(required_fields - set(row))
        if missing:
            raise ValueError(
                f"Query file record {index} is missing required fields: {', '.join(missing)}."
            )
    return rows


def compute_backdoor_example_count(alpha: float, num_icl_examples: int) -> int:
    if num_icl_examples <= 0 or alpha <= 0:
        return 0
    count = int(round(alpha * num_icl_examples))
    return max(1, count)


def sample_examples(
    pool: list[ExampleRecord],
    desired_count: int,
    rng: random.Random,
    excluded_sample_id: str | None = None,
) -> list[ExampleRecord]:
    eligible = [item for item in pool if item.sample_id != excluded_sample_id]
    if not eligible or desired_count <= 0:
        return []
    return rng.sample(eligible, min(desired_count, len(eligible)))


def build_prompt_text(
    template: PromptTemplate,
    clean_examples: list[ExampleRecord],
    backdoor_examples: list[ExampleRecord],
    test_query: str,
) -> str:
    lines: list[str] = [template.instruction, ""]
    for index, example in enumerate(clean_examples, start=1):
        lines.extend(
            [
                f"{template.clean_example_label} {index}",
                f"Query: {example.prompt}",
                f"{template.response_label}: {example.response}",
                "",
            ]
        )
    for index, example in enumerate(backdoor_examples, start=1):
        lines.extend(
            [
                f"{template.backdoor_example_label} {index}",
                f"Query: {example.prompt}",
                f"{template.response_label}: {example.response}",
                "",
            ]
        )
    lines.extend(
        [
            template.query_label,
            f"Query: {test_query}",
            f"{template.response_label}:",
        ]
    )
    return "\n".join(line for line in lines if line is not None).strip()


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def detect_target_behavior(response_text: str, target_text: str) -> bool:
    if not target_text.strip():
        return False
    return normalize_text(target_text) in normalize_text(response_text)


def prepare_contracts_from_dataset(
    dataset_manifest: Path,
    alpha: float,
    query_budget: int,
    num_icl_examples: int,
    rng: random.Random,
    trigger_type_override: str | None,
    target_type_override: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest = load_json(dataset_manifest)
    dataset_path = resolve_dataset_path(dataset_manifest, manifest)
    rows = load_jsonl(dataset_path)
    examples = [build_example_from_dataset_record(row) for row in rows]

    clean_examples = [example for example in examples if example.source_kind == "clean_example"]
    backdoor_examples = [example for example in examples if example.source_kind == "backdoor_example"]
    query_candidates = clean_examples

    if trigger_type_override is not None:
        backdoor_examples = [item for item in backdoor_examples if item.trigger_type == trigger_type_override]
    if target_type_override is not None:
        backdoor_examples = [item for item in backdoor_examples if item.target_type == target_type_override]

    if not clean_examples:
        raise ValueError("Dataset manifest does not provide any clean examples for illumination probing.")
    if alpha > 0 and not backdoor_examples:
        raise ValueError("Dataset manifest does not provide any backdoor examples for alpha > 0 probing.")

    selected_queries = rng.sample(query_candidates, min(query_budget, len(query_candidates)))
    contracts: list[dict[str, Any]] = []
    num_backdoor_examples = min(
        len(backdoor_examples),
        compute_backdoor_example_count(alpha=alpha, num_icl_examples=num_icl_examples),
    )
    num_clean_examples = max(0, num_icl_examples - num_backdoor_examples)

    for query_example in selected_queries:
        selected_clean = sample_examples(
            pool=clean_examples,
            desired_count=num_clean_examples,
            rng=rng,
            excluded_sample_id=query_example.sample_id,
        )
        selected_backdoor = sample_examples(
            pool=backdoor_examples,
            desired_count=num_backdoor_examples,
            rng=rng,
        )
        contracts.append(
            {
                "sample_id": query_example.sample_id,
                "clean_examples": [
                    {
                        "sample_id": example.sample_id,
                        "prompt": example.prompt,
                        "response": example.response,
                    }
                    for example in selected_clean
                ],
                "backdoor_examples": [
                    {
                        "sample_id": example.sample_id,
                        "prompt": example.prompt,
                        "response": example.response,
                    }
                    for example in selected_backdoor
                ],
                "test_query": query_example.raw_record["clean_prompt"],
                "target_type": target_type_override or query_example.target_type,
                "trigger_type": trigger_type_override or query_example.trigger_type,
                "target_text": query_example.target_text,
                "metadata": {
                    "dataset_path": str(dataset_path),
                    "source_mode": "dataset_manifest",
                    "attack_profile": manifest.get("attack_profile", {}).get("profile_name"),
                },
            }
        )

    dataset_summary = manifest.get("summary", {})
    return contracts, {
        "source_mode": "dataset_manifest",
        "dataset_path": str(dataset_path),
        "manifest_path": str(dataset_manifest.resolve()),
        "dataset_summary": dataset_summary,
        "num_clean_pool": len(clean_examples),
        "num_backdoor_pool": len(backdoor_examples),
        "budget_realized": len(contracts),
    }


def prepare_contracts_from_query_file(
    query_file: Path,
    query_budget: int,
    rng: random.Random,
    trigger_type_override: str | None,
    target_type_override: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = load_query_contracts_from_file(query_file)
    selected = rng.sample(rows, min(query_budget, len(rows)))
    contracts: list[dict[str, Any]] = []
    for row in selected:
        contracts.append(
            {
                "sample_id": str(row["sample_id"]),
                "clean_examples": list(row["clean_examples"]),
                "backdoor_examples": list(row["backdoor_examples"]),
                "test_query": str(row["test_query"]),
                "target_type": str(row.get("target_type", target_type_override or "unknown")),
                "trigger_type": str(row.get("trigger_type", trigger_type_override or "unknown")),
                "target_text": str(row.get("target_text", "")),
                "metadata": dict(row.get("metadata", {})),
            }
        )
    return contracts, {
        "source_mode": "query_file",
        "query_file": str(query_file.resolve()),
        "budget_realized": len(contracts),
    }


def load_hf_backend(model_profile: ModelProfile) -> tuple[Any, Any, str, str]:
    if model_profile.backend_type != "huggingface":
        raise ValueError("Illumination M1 currently only supports `huggingface` backend_type.")

    runtime_device = resolve_runtime_device(model_profile.device)
    resolved_dtype = resolve_dtype(model_profile.dtype, runtime_device)
    model_source = model_profile.local_path or model_profile.model_id
    local_files_only = model_profile.local_path is not None
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_source,
            use_fast=True,
            local_files_only=local_files_only,
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(
            model_source,
            torch_dtype=resolved_dtype,
            local_files_only=local_files_only,
        )
    except Exception as exc:
        raise ValueError(
            f"Failed to load HuggingFace model/tokenizer from `{model_source}`: {exc}"
        ) from exc

    model.to(runtime_device)
    model.eval()
    return model, tokenizer, runtime_device, str(resolved_dtype)


def generate_response(
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    max_length: int,
    generation: GenerationProfile,
    runtime_device: str,
) -> str:
    encoded = tokenizer(
        prompt_text,
        return_tensors="pt",
        truncation=True,
        max_length=max(16, max_length - generation.max_new_tokens),
    )
    encoded = {key: value.to(runtime_device) for key, value in encoded.items()}
    with torch.no_grad():
        generated = model.generate(
            **encoded,
            max_new_tokens=generation.max_new_tokens,
            do_sample=generation.do_sample,
            temperature=generation.temperature if generation.do_sample else None,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    new_tokens = generated[:, encoded["input_ids"].shape[1] :]
    response_text = tokenizer.decode(new_tokens[0], skip_special_tokens=True).strip()
    if not response_text:
        response_text = tokenizer.decode(generated[0], skip_special_tokens=True).strip()
        if response_text.startswith(prompt_text):
            response_text = response_text[len(prompt_text) :].strip()
    return response_text


def build_summary(
    results: list[ProbeResult],
    budget_requested: int,
    model_profile: ModelProfile,
    illumination_profile: IlluminationProfile,
    source_summary: dict[str, Any],
) -> dict[str, Any]:
    num_target_behavior = sum(1 for item in results if item.is_target_behavior)
    response_lengths = [len(item.response_text) for item in results]
    return {
        "summary_status": "PASS",
        "model_profile": model_profile.profile_name,
        "model_id": model_profile.model_id,
        "prompt_template_name": illumination_profile.prompt_template_name,
        "alpha": illumination_profile.alpha,
        "query_budget_requested": budget_requested,
        "query_budget_realized": len(results),
        "num_results": len(results),
        "num_target_behavior": num_target_behavior,
        "target_behavior_rate": (num_target_behavior / len(results)) if results else 0.0,
        "average_response_chars": (sum(response_lengths) / len(response_lengths)) if response_lengths else 0.0,
        "source_summary": source_summary,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_log(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_illumination_probe(
    model_config_path: Path,
    model_profile_name: str,
    illumination_config_path: Path,
    illumination_profile_name: str,
    prompt_dir: Path,
    output_dir: Path,
    dataset_manifest: Path | None,
    query_file: Path | None,
    alpha_override: float | None,
    query_budget_override: int | None,
    trigger_type_override: str | None,
    target_type_override: str | None,
    seed: int,
    dry_run: bool,
    smoke_mode: bool,
) -> dict[str, Any]:
    set_seed(seed)
    rng = random.Random(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_paths = {
        "raw_results": output_dir / "raw_results.jsonl",
        "config_snapshot": output_dir / "config_snapshot.json",
        "summary": output_dir / "summary.json",
        "log": output_dir / "probe.log",
    }

    model_profile = load_model_profile(model_config_path, model_profile_name)
    illumination_profile = load_illumination_profile(illumination_config_path, illumination_profile_name)
    prompt_template = load_prompt_template(prompt_dir, illumination_profile.prompt_template_name)

    if alpha_override is not None:
        illumination_profile.alpha = alpha_override
    if query_budget_override is not None:
        illumination_profile.query_budget = query_budget_override
    if smoke_mode:
        illumination_profile.query_budget = min(illumination_profile.query_budget, 2)
        illumination_profile.generation.max_new_tokens = min(illumination_profile.generation.max_new_tokens, 16)
        illumination_profile.num_icl_examples = min(illumination_profile.num_icl_examples, 2)

    if dataset_manifest is not None:
        contracts, source_summary = prepare_contracts_from_dataset(
            dataset_manifest=dataset_manifest,
            alpha=illumination_profile.alpha,
            query_budget=illumination_profile.query_budget,
            num_icl_examples=illumination_profile.num_icl_examples,
            rng=rng,
            trigger_type_override=trigger_type_override,
            target_type_override=target_type_override,
        )
    elif query_file is not None:
        contracts, source_summary = prepare_contracts_from_query_file(
            query_file=query_file,
            query_budget=illumination_profile.query_budget,
            rng=rng,
            trigger_type_override=trigger_type_override,
            target_type_override=target_type_override,
        )
    else:
        raise ValueError("One of `dataset_manifest` or `query_file` must be provided.")

    model = tokenizer = None
    runtime_device = "dry-run"
    resolved_dtype = "dry-run"
    if not dry_run:
        model, tokenizer, runtime_device, resolved_dtype = load_hf_backend(model_profile)

    results: list[ProbeResult] = []
    for index, contract in enumerate(contracts):
        clean_examples = [
            ExampleRecord(
                sample_id=str(item.get("sample_id", f"clean_{item_index}")),
                prompt=str(item["prompt"]),
                response=str(item["response"]),
                source_kind="clean_example",
                trigger_type=str(contract["trigger_type"]),
                target_type=str(contract["target_type"]),
                target_text=str(contract["target_text"]),
                raw_record=item,
            )
            for item_index, item in enumerate(contract["clean_examples"])
        ]
        backdoor_examples = [
            ExampleRecord(
                sample_id=str(item.get("sample_id", f"backdoor_{item_index}")),
                prompt=str(item["prompt"]),
                response=str(item["response"]),
                source_kind="backdoor_example",
                trigger_type=str(contract["trigger_type"]),
                target_type=str(contract["target_type"]),
                target_text=str(contract["target_text"]),
                raw_record=item,
            )
            for item_index, item in enumerate(contract["backdoor_examples"])
        ]
        prompt_text = build_prompt_text(
            template=prompt_template,
            clean_examples=clean_examples,
            backdoor_examples=backdoor_examples,
            test_query=str(contract["test_query"]),
        )
        if dry_run:
            response_text = "[dry-run] prompt constructed"
        else:
            assert model is not None and tokenizer is not None
            response_text = generate_response(
                model=model,
                tokenizer=tokenizer,
                prompt_text=prompt_text,
                max_length=model_profile.max_length,
                generation=illumination_profile.generation,
                runtime_device=runtime_device,
            )
        is_target_behavior = detect_target_behavior(
            response_text=response_text,
            target_text=str(contract["target_text"]),
        )
        results.append(
            ProbeResult(
                prompt_id=f"illumination_{index:04d}",
                sample_id=str(contract["sample_id"]),
                model_profile=model_profile.profile_name,
                prompt_template_name=prompt_template.template_name,
                target_type=str(contract["target_type"]),
                trigger_type=str(contract["trigger_type"]),
                alpha=illumination_profile.alpha,
                budget=illumination_profile.query_budget,
                prompt_text=prompt_text,
                response_text=response_text,
                is_target_behavior=is_target_behavior,
                metadata={
                    "clean_example_ids": [item.sample_id for item in clean_examples],
                    "backdoor_example_ids": [item.sample_id for item in backdoor_examples],
                    "num_clean_examples": len(clean_examples),
                    "num_backdoor_examples": len(backdoor_examples),
                    "test_query": str(contract["test_query"]),
                    "target_text": str(contract["target_text"]),
                    "runtime_device": runtime_device,
                    "resolved_dtype": resolved_dtype,
                    "dry_run": dry_run,
                    "smoke_mode": smoke_mode,
                    "source_summary": source_summary,
                    "contract_metadata": dict(contract.get("metadata", {})),
                },
            )
        )

    config_snapshot = {
        "seed": seed,
        "model_config_path": str(model_config_path),
        "model_profile_name": model_profile_name,
        "model_profile": asdict(model_profile),
        "illumination_config_path": str(illumination_config_path),
        "illumination_profile_name": illumination_profile_name,
        "illumination_profile": {
            "profile_name": illumination_profile.profile_name,
            "prompt_template_name": illumination_profile.prompt_template_name,
            "alpha": illumination_profile.alpha,
            "query_budget": illumination_profile.query_budget,
            "num_icl_examples": illumination_profile.num_icl_examples,
            "candidate_query_source": illumination_profile.candidate_query_source,
            "generation": asdict(illumination_profile.generation),
        },
        "prompt_template_path": str((prompt_dir / f"{prompt_template.template_name}.yaml").resolve()),
        "dataset_manifest": str(dataset_manifest) if dataset_manifest else None,
        "query_file": str(query_file) if query_file else None,
        "trigger_type_override": trigger_type_override,
        "target_type_override": target_type_override,
        "dry_run": dry_run,
        "smoke_mode": smoke_mode,
        "runtime_device": runtime_device,
        "resolved_dtype": resolved_dtype,
        "num_contracts": len(contracts),
    }
    summary = build_summary(
        results=results,
        budget_requested=illumination_profile.query_budget,
        model_profile=model_profile,
        illumination_profile=illumination_profile,
        source_summary=source_summary,
    )

    write_jsonl(output_paths["raw_results"], [asdict(result) for result in results])
    write_json(output_paths["config_snapshot"], config_snapshot)
    write_json(output_paths["summary"], summary)
    write_log(
        output_paths["log"],
        [
            "TriScope-LLM illumination probe run",
            f"summary_status={summary['summary_status']}",
            f"model_profile={model_profile.profile_name}",
            f"prompt_template_name={prompt_template.template_name}",
            f"alpha={illumination_profile.alpha}",
            f"query_budget_requested={illumination_profile.query_budget}",
            f"query_budget_realized={len(results)}",
            f"runtime_device={runtime_device}",
            f"dry_run={dry_run}",
            f"smoke_mode={smoke_mode}",
            f"raw_results={output_paths['raw_results']}",
            f"summary={output_paths['summary']}",
        ],
    )
    return {
        "summary": summary,
        "config_snapshot": config_snapshot,
        "output_paths": {name: str(path) for name, path in output_paths.items()},
    }
