"""Minimal confidence probe for TriScope-LLM."""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch
import yaml

from src.probes.illumination_probe import (
    detect_target_behavior,
    load_hf_backend,
    load_json,
    load_jsonl,
    load_model_profile,
    load_yaml_profile,
    resolve_dataset_path,
    set_seed,
)


@dataclass
class ConfidenceGenerationProfile:
    max_new_tokens: int
    top_k_capture: int
    do_sample: bool
    temperature: float


@dataclass
class ConfidenceProfile:
    profile_name: str
    confidence_template_name: str
    query_budget: int
    candidate_query_source: str
    generation: ConfidenceGenerationProfile


@dataclass
class ConfidenceTemplate:
    template_name: str
    description: str
    instruction: str
    query_label: str
    answer_label: str


@dataclass
class ConfidenceResult:
    probe_id: str
    sample_id: str
    model_profile: str
    confidence_profile: str
    confidence_template_name: str
    target_type: str
    trigger_type: str
    query_budget: int
    query_text: str
    prompt_text: str
    response_text: str
    is_target_behavior: bool
    token_steps: list[dict[str, Any]]
    metadata: dict[str, Any]


def load_confidence_profile(config_path: Path, profile_name: str) -> ConfidenceProfile:
    profile = load_yaml_profile(config_path=config_path, profile_name=profile_name)
    generation = profile.get("generation", {})
    return ConfidenceProfile(
        profile_name=profile_name,
        confidence_template_name=str(profile.get("confidence_template_name", "minimal_v1")),
        query_budget=int(profile.get("query_budget", 8)),
        candidate_query_source=str(profile.get("candidate_query_source", "poisoned_only")),
        generation=ConfidenceGenerationProfile(
            max_new_tokens=int(generation.get("max_new_tokens", 24)),
            top_k_capture=int(generation.get("top_k_capture", 5)),
            do_sample=bool(generation.get("do_sample", False)),
            temperature=float(generation.get("temperature", 0.0)),
        ),
    )


def load_confidence_template(prompt_dir: Path, template_name: str) -> ConfidenceTemplate:
    template_path = prompt_dir / f"{template_name}.yaml"
    if not template_path.is_file():
        raise ValueError(f"Confidence template `{template_name}` not found in `{prompt_dir}`.")
    payload = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Confidence template `{template_path}` must be a mapping.")
    return ConfidenceTemplate(
        template_name=str(payload.get("template_name", template_name)),
        description=str(payload.get("description", "")),
        instruction=str(payload.get("instruction", "")).strip(),
        query_label=str(payload.get("query_label", "Query")),
        answer_label=str(payload.get("answer_label", "Answer")),
    )


def load_confidence_contracts_from_file(query_file: Path) -> list[dict[str, Any]]:
    rows = load_jsonl(query_file)
    required_fields = {"sample_id", "query_text"}
    for index, row in enumerate(rows):
        missing = sorted(required_fields - set(row))
        if missing:
            raise ValueError(
                f"Confidence query file record {index} is missing required fields: {', '.join(missing)}."
            )
    return rows


def prepare_contracts_from_dataset(
    dataset_manifest: Path,
    query_budget: int,
    candidate_query_source: str,
    rng: random.Random,
    trigger_type_override: str | None,
    target_type_override: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if candidate_query_source != "poisoned_only":
        raise ValueError("Confidence M1 currently only supports `candidate_query_source=poisoned_only`.")

    manifest = load_json(dataset_manifest)
    dataset_path = resolve_dataset_path(dataset_manifest, manifest)
    rows = load_jsonl(dataset_path)

    candidates = [row for row in rows if row.get("is_poisoned") is True]
    if trigger_type_override is not None:
        candidates = [
            row for row in candidates if str(row.get("attack_metadata", {}).get("trigger_type")) == trigger_type_override
        ]
    if target_type_override is not None:
        candidates = [
            row for row in candidates if str(row.get("attack_metadata", {}).get("target_type")) == target_type_override
        ]
    if not candidates:
        raise ValueError("Dataset manifest does not provide any poisoned query candidates for confidence probing.")

    selected = rng.sample(candidates, min(query_budget, len(candidates)))
    contracts: list[dict[str, Any]] = []
    for row in selected:
        attack_metadata = row.get("attack_metadata", {})
        if not isinstance(attack_metadata, dict):
            raise ValueError(f"Record `{row.get('sample_id', 'unknown')}` has invalid `attack_metadata`.")
        contracts.append(
            {
                "sample_id": str(row["sample_id"]),
                "query_text": str(row.get("poisoned_prompt") or row.get("train_prompt") or ""),
                "clean_query_text": str(row.get("clean_prompt") or ""),
                "target_type": str(attack_metadata.get("target_type", target_type_override or "unknown")),
                "trigger_type": str(attack_metadata.get("trigger_type", trigger_type_override or "unknown")),
                "target_text": str(attack_metadata.get("target_text", "")),
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
        "num_query_candidates": len(candidates),
        "budget_realized": len(contracts),
    }


def prepare_contracts_from_query_file(
    query_file: Path,
    query_budget: int,
    rng: random.Random,
    trigger_type_override: str | None,
    target_type_override: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = load_confidence_contracts_from_file(query_file)
    selected = rng.sample(rows, min(query_budget, len(rows)))
    contracts: list[dict[str, Any]] = []
    for row in selected:
        contracts.append(
            {
                "sample_id": str(row["sample_id"]),
                "query_text": str(row["query_text"]),
                "clean_query_text": str(row.get("clean_query_text", "")),
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


def build_prompt_text(template: ConfidenceTemplate, query_text: str) -> str:
    return "\n".join(
        [
            template.instruction,
            "",
            f"{template.query_label}: {query_text}",
            f"{template.answer_label}:",
        ]
    ).strip()


def generate_with_token_scores(
    model: Any,
    tokenizer: Any,
    prompt_text: str,
    max_length: int,
    generation: ConfidenceGenerationProfile,
    runtime_device: str,
) -> tuple[str, list[dict[str, Any]]]:
    encoded = tokenizer(
        prompt_text,
        return_tensors="pt",
        truncation=True,
        max_length=max(16, max_length - generation.max_new_tokens),
    )
    encoded = {key: value.to(runtime_device) for key, value in encoded.items()}
    with torch.no_grad():
        outputs = model.generate(
            **encoded,
            max_new_tokens=generation.max_new_tokens,
            do_sample=generation.do_sample,
            temperature=generation.temperature if generation.do_sample else None,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            output_scores=True,
            return_dict_in_generate=True,
        )

    input_length = encoded["input_ids"].shape[1]
    generated_ids = outputs.sequences[0, input_length:]
    response_text = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    token_steps: list[dict[str, Any]] = []
    top_k = max(1, generation.top_k_capture)

    for step_index, score_tensor in enumerate(outputs.scores):
        score_vector = score_tensor[0]
        probs = torch.softmax(score_vector, dim=-1)
        chosen_token_id = int(outputs.sequences[0, input_length + step_index].item())
        chosen_prob = float(probs[chosen_token_id].item())
        entropy = float(-(probs * probs.clamp_min(1e-12).log()).sum().item())
        top_probs, top_ids = torch.topk(probs, k=min(top_k, probs.shape[-1]))
        top_tokens = []
        for token_id, prob in zip(top_ids.tolist(), top_probs.tolist()):
            top_tokens.append(
                {
                    "token_id": int(token_id),
                    "token_text": tokenizer.decode([token_id], skip_special_tokens=False),
                    "probability": float(prob),
                }
            )
        token_steps.append(
            {
                "step_index": step_index,
                "token_id": chosen_token_id,
                "token_text": tokenizer.decode([chosen_token_id], skip_special_tokens=False),
                "chosen_token_prob": chosen_prob,
                "entropy": entropy,
                "top_tokens": top_tokens,
            }
        )

    return response_text, token_steps


def build_summary(
    results: list[ConfidenceResult],
    model_profile: Any,
    confidence_profile: ConfidenceProfile,
    source_summary: dict[str, Any],
) -> dict[str, Any]:
    all_steps = [step for result in results for step in result.token_steps]
    chosen_probs = [step["chosen_token_prob"] for step in all_steps]
    entropies = [step["entropy"] for step in all_steps]
    generated_token_count = len(all_steps)
    return {
        "summary_status": "PASS",
        "model_profile": model_profile.profile_name,
        "model_id": model_profile.model_id,
        "confidence_profile": confidence_profile.profile_name,
        "confidence_template_name": confidence_profile.confidence_template_name,
        "query_budget_requested": confidence_profile.query_budget,
        "query_budget_realized": len(results),
        "num_results": len(results),
        "generated_token_count": generated_token_count,
        "mean_chosen_token_prob": statistics_mean(chosen_probs),
        "min_chosen_token_prob": min(chosen_probs) if chosen_probs else 0.0,
        "mean_step_entropy": statistics_mean(entropies),
        "source_summary": source_summary,
    }


def statistics_mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def run_confidence_probe(
    model_config_path: Path,
    model_profile_name: str,
    confidence_config_path: Path,
    confidence_profile_name: str,
    prompt_dir: Path,
    output_dir: Path,
    dataset_manifest: Path | None,
    query_file: Path | None,
    query_budget_override: int | None,
    trigger_type_override: str | None,
    target_type_override: str | None,
    seed: int,
    dry_run: bool,
    smoke_mode: bool,
) -> dict[str, Any]:
    if dataset_manifest is None and query_file is None:
        raise ValueError("One of `dataset_manifest` or `query_file` must be provided.")

    set_seed(seed)
    rng = random.Random(seed)
    model_profile = load_model_profile(config_path=model_config_path, profile_name=model_profile_name)
    confidence_profile = load_confidence_profile(
        config_path=confidence_config_path,
        profile_name=confidence_profile_name,
    )
    template = load_confidence_template(
        prompt_dir=prompt_dir,
        template_name=confidence_profile.confidence_template_name,
    )

    if query_budget_override is not None:
        confidence_profile.query_budget = int(query_budget_override)
    if smoke_mode:
        confidence_profile.query_budget = min(confidence_profile.query_budget, 2)
        confidence_profile.generation.max_new_tokens = min(confidence_profile.generation.max_new_tokens, 16)

    if dataset_manifest is not None:
        contracts, source_summary = prepare_contracts_from_dataset(
            dataset_manifest=dataset_manifest,
            query_budget=confidence_profile.query_budget,
            candidate_query_source=confidence_profile.candidate_query_source,
            rng=rng,
            trigger_type_override=trigger_type_override,
            target_type_override=target_type_override,
        )
    else:
        contracts, source_summary = prepare_contracts_from_query_file(
            query_file=query_file,
            query_budget=confidence_profile.query_budget,
            rng=rng,
            trigger_type_override=trigger_type_override,
            target_type_override=target_type_override,
        )

    if not contracts:
        raise ValueError("Confidence probe did not produce any contracts.")

    runtime_device = "dry_run"
    resolved_dtype = "dry_run"
    model = None
    tokenizer = None
    if not dry_run:
        model, tokenizer, runtime_device, resolved_dtype = load_hf_backend(model_profile)

    results: list[ConfidenceResult] = []
    for index, contract in enumerate(contracts):
        query_text = str(contract["query_text"])
        target_text = str(contract.get("target_text", ""))
        prompt_text = build_prompt_text(template=template, query_text=query_text)
        if dry_run:
            response_text = ""
            token_steps: list[dict[str, Any]] = []
        else:
            response_text, token_steps = generate_with_token_scores(
                model=model,
                tokenizer=tokenizer,
                prompt_text=prompt_text,
                max_length=model_profile.max_length,
                generation=confidence_profile.generation,
                runtime_device=runtime_device,
            )
        results.append(
            ConfidenceResult(
                probe_id=f"confidence_{index:04d}",
                sample_id=str(contract["sample_id"]),
                model_profile=model_profile.profile_name,
                confidence_profile=confidence_profile.profile_name,
                confidence_template_name=template.template_name,
                target_type=str(contract["target_type"]),
                trigger_type=str(contract["trigger_type"]),
                query_budget=confidence_profile.query_budget,
                query_text=query_text,
                prompt_text=prompt_text,
                response_text=response_text,
                is_target_behavior=detect_target_behavior(response_text, target_text),
                token_steps=token_steps,
                metadata={
                    "clean_query_text": str(contract.get("clean_query_text", "")),
                    "target_text": target_text,
                    "runtime_device": runtime_device,
                    "resolved_dtype": resolved_dtype,
                    "dry_run": dry_run,
                    "smoke_mode": smoke_mode,
                    "source_summary": source_summary,
                    "contract_metadata": dict(contract.get("metadata", {})),
                },
            )
        )

    summary = build_summary(
        results=results,
        model_profile=model_profile,
        confidence_profile=confidence_profile,
        source_summary=source_summary,
    )
    config_snapshot = {
        "seed": seed,
        "model_config_path": str(model_config_path),
        "model_profile_name": model_profile_name,
        "model_profile": asdict(model_profile),
        "confidence_config_path": str(confidence_config_path),
        "confidence_profile_name": confidence_profile_name,
        "confidence_profile": asdict(confidence_profile),
        "prompt_template_path": str((prompt_dir / f"{template.template_name}.yaml").resolve()),
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

    output_dir.mkdir(parents=True, exist_ok=True)
    raw_results_path = output_dir / "raw_results.jsonl"
    config_snapshot_path = output_dir / "config_snapshot.json"
    summary_path = output_dir / "summary.json"
    log_path = output_dir / "probe.log"

    with raw_results_path.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(asdict(result), ensure_ascii=True) + "\n")
    config_snapshot_path.write_text(
        json.dumps(config_snapshot, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    log_lines = [
        "TriScope-LLM confidence probe",
        f"Model profile: {model_profile.profile_name}",
        f"Confidence profile: {confidence_profile.profile_name}",
        f"Confidence template: {template.template_name}",
        f"Query budget realized: {len(results)}/{confidence_profile.query_budget}",
        f"Raw results: {raw_results_path.resolve()}",
        f"Config snapshot: {config_snapshot_path.resolve()}",
        f"Summary: {summary_path.resolve()}",
    ]
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return {
        "results": results,
        "summary": summary,
        "output_paths": {
            "raw_results": str(raw_results_path),
            "config_snapshot": str(config_snapshot_path),
            "summary": str(summary_path),
            "log": str(log_path),
        },
    }
