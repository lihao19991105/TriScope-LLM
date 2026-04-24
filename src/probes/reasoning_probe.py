"""Minimal reasoning scrutiny probe for TriScope-LLM."""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from src.probes.illumination_probe import (
    detect_target_behavior,
    generate_response,
    load_hf_backend,
    load_json,
    load_jsonl,
    load_model_profile,
    load_yaml_profile,
    normalize_text,
    resolve_dataset_path,
    set_seed,
)


@dataclass
class ReasoningGenerationProfile:
    original_max_new_tokens: int
    reasoning_max_new_tokens: int
    reasoned_answer_max_new_tokens: int
    do_sample: bool
    temperature: float


@dataclass
class ReasoningProfile:
    profile_name: str
    reasoning_template_name: str
    query_budget: int
    candidate_query_source: str
    generation: ReasoningGenerationProfile


@dataclass
class ReasoningTemplate:
    template_name: str
    description: str
    direct_answer_instruction: str
    reasoning_instruction: str
    final_answer_instruction: str
    query_label: str
    reasoning_label: str
    answer_label: str


@dataclass
class ReasoningResult:
    probe_id: str
    sample_id: str
    model_profile: str
    reasoning_profile: str
    reasoning_template_name: str
    target_type: str
    trigger_type: str
    query_budget: int
    query_text: str
    original_prompt_text: str
    original_answer: str
    reasoning_prompt_text: str
    reasoning_text: str
    reasoned_prompt_text: str
    reasoned_answer: str
    original_is_target_behavior: bool
    reasoned_is_target_behavior: bool
    answer_changed_after_reasoning: bool
    metadata: dict[str, Any]


def load_reasoning_profile(config_path: Path, profile_name: str) -> ReasoningProfile:
    profile = load_yaml_profile(config_path=config_path, profile_name=profile_name)
    generation = profile.get("generation", {})
    return ReasoningProfile(
        profile_name=profile_name,
        reasoning_template_name=str(profile.get("reasoning_template_name", "minimal_v1")),
        query_budget=int(profile.get("query_budget", 8)),
        candidate_query_source=str(profile.get("candidate_query_source", "poisoned_only")),
        generation=ReasoningGenerationProfile(
            original_max_new_tokens=int(generation.get("original_max_new_tokens", 24)),
            reasoning_max_new_tokens=int(generation.get("reasoning_max_new_tokens", 64)),
            reasoned_answer_max_new_tokens=int(generation.get("reasoned_answer_max_new_tokens", 24)),
            do_sample=bool(generation.get("do_sample", False)),
            temperature=float(generation.get("temperature", 0.0)),
        ),
    )


def load_reasoning_template(prompt_dir: Path, template_name: str) -> ReasoningTemplate:
    template_path = prompt_dir / f"{template_name}.yaml"
    if not template_path.is_file():
        raise ValueError(f"Reasoning template `{template_name}` not found in `{prompt_dir}`.")
    payload = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Reasoning template `{template_path}` must be a mapping.")
    return ReasoningTemplate(
        template_name=str(payload.get("template_name", template_name)),
        description=str(payload.get("description", "")),
        direct_answer_instruction=str(payload.get("direct_answer_instruction", "")).strip(),
        reasoning_instruction=str(payload.get("reasoning_instruction", "")).strip(),
        final_answer_instruction=str(payload.get("final_answer_instruction", "")).strip(),
        query_label=str(payload.get("query_label", "Query")),
        reasoning_label=str(payload.get("reasoning_label", "Reasoning")),
        answer_label=str(payload.get("answer_label", "Answer")),
    )


def load_reasoning_contracts_from_file(query_file: Path) -> list[dict[str, Any]]:
    rows = load_jsonl(query_file)
    required_fields = {"sample_id", "query_text"}
    for index, row in enumerate(rows):
        missing = sorted(required_fields - set(row))
        if missing:
            raise ValueError(
                f"Reasoning query file record {index} is missing required fields: {', '.join(missing)}."
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
        raise ValueError("Reasoning M1 currently only supports `candidate_query_source=poisoned_only`.")

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
        raise ValueError("Dataset manifest does not provide any poisoned query candidates for reasoning probing.")

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
    rows = load_reasoning_contracts_from_file(query_file)
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


def build_original_prompt(template: ReasoningTemplate, query_text: str) -> str:
    return "\n".join(
        [
            template.direct_answer_instruction,
            "",
            f"{template.query_label}: {query_text}",
            f"{template.answer_label}:",
        ]
    ).strip()


def build_reasoning_prompt(template: ReasoningTemplate, query_text: str) -> str:
    return "\n".join(
        [
            template.reasoning_instruction,
            "",
            f"{template.query_label}: {query_text}",
            f"{template.reasoning_label}:",
        ]
    ).strip()


def build_reasoned_prompt(
    template: ReasoningTemplate,
    query_text: str,
    reasoning_text: str,
) -> str:
    return "\n".join(
        [
            template.final_answer_instruction,
            "",
            f"{template.query_label}: {query_text}",
            f"{template.reasoning_label}: {reasoning_text}",
            f"{template.answer_label}:",
        ]
    ).strip()


def answers_changed(original_answer: str, reasoned_answer: str) -> bool:
    if not original_answer.strip() or not reasoned_answer.strip():
        return False
    return normalize_text(original_answer) != normalize_text(reasoned_answer)


def build_summary(
    results: list[ReasoningResult],
    model_profile: Any,
    reasoning_profile: ReasoningProfile,
    source_summary: dict[str, Any],
) -> dict[str, Any]:
    num_reasoning_non_empty = sum(1 for item in results if item.reasoning_text.strip())
    num_changed = sum(1 for item in results if item.answer_changed_after_reasoning)
    num_original_target = sum(1 for item in results if item.original_is_target_behavior)
    num_reasoned_target = sum(1 for item in results if item.reasoned_is_target_behavior)
    num_results = len(results)
    return {
        "summary_status": "PASS",
        "model_profile": model_profile.profile_name,
        "model_id": model_profile.model_id,
        "reasoning_profile": reasoning_profile.profile_name,
        "reasoning_template_name": reasoning_profile.reasoning_template_name,
        "query_budget_requested": reasoning_profile.query_budget,
        "query_budget_realized": num_results,
        "num_results": num_results,
        "num_non_empty_reasoning": num_reasoning_non_empty,
        "reasoning_non_empty_rate": (num_reasoning_non_empty / num_results) if num_results else 0.0,
        "num_answer_changed_after_reasoning": num_changed,
        "answer_changed_rate": (num_changed / num_results) if num_results else 0.0,
        "num_original_target_behavior": num_original_target,
        "num_reasoned_target_behavior": num_reasoned_target,
        "original_target_behavior_rate": (num_original_target / num_results) if num_results else 0.0,
        "reasoned_target_behavior_rate": (num_reasoned_target / num_results) if num_results else 0.0,
        "source_summary": source_summary,
    }


def run_reasoning_probe(
    model_config_path: Path,
    model_profile_name: str,
    reasoning_config_path: Path,
    reasoning_profile_name: str,
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
    reasoning_profile = load_reasoning_profile(
        config_path=reasoning_config_path,
        profile_name=reasoning_profile_name,
    )
    template = load_reasoning_template(prompt_dir=prompt_dir, template_name=reasoning_profile.reasoning_template_name)

    if query_budget_override is not None:
        reasoning_profile.query_budget = int(query_budget_override)
    if smoke_mode:
        reasoning_profile.query_budget = min(reasoning_profile.query_budget, 2)
        reasoning_profile.generation.original_max_new_tokens = min(
            reasoning_profile.generation.original_max_new_tokens, 16
        )
        reasoning_profile.generation.reasoning_max_new_tokens = min(
            reasoning_profile.generation.reasoning_max_new_tokens, 32
        )
        reasoning_profile.generation.reasoned_answer_max_new_tokens = min(
            reasoning_profile.generation.reasoned_answer_max_new_tokens, 16
        )

    if dataset_manifest is not None:
        contracts, source_summary = prepare_contracts_from_dataset(
            dataset_manifest=dataset_manifest,
            query_budget=reasoning_profile.query_budget,
            candidate_query_source=reasoning_profile.candidate_query_source,
            rng=rng,
            trigger_type_override=trigger_type_override,
            target_type_override=target_type_override,
        )
    else:
        contracts, source_summary = prepare_contracts_from_query_file(
            query_file=query_file,
            query_budget=reasoning_profile.query_budget,
            rng=rng,
            trigger_type_override=trigger_type_override,
            target_type_override=target_type_override,
        )

    if not contracts:
        raise ValueError("Reasoning probe did not produce any contracts.")

    runtime_device = "dry_run"
    resolved_dtype = "dry_run"
    model = None
    tokenizer = None
    if not dry_run:
        model, tokenizer, runtime_device, resolved_dtype = load_hf_backend(model_profile)

    results: list[ReasoningResult] = []
    for index, contract in enumerate(contracts):
        query_text = str(contract["query_text"])
        target_text = str(contract.get("target_text", ""))
        original_prompt_text = build_original_prompt(template=template, query_text=query_text)
        reasoning_prompt_text = build_reasoning_prompt(template=template, query_text=query_text)

        if dry_run:
            original_answer = ""
            reasoning_text = ""
            reasoned_answer = ""
        else:
            original_answer = generate_response(
                model=model,
                tokenizer=tokenizer,
                prompt_text=original_prompt_text,
                max_length=model_profile.max_length,
                generation=type(
                    "GenerationProfile",
                    (),
                    {
                        "max_new_tokens": reasoning_profile.generation.original_max_new_tokens,
                        "do_sample": reasoning_profile.generation.do_sample,
                        "temperature": reasoning_profile.generation.temperature,
                    },
                )(),
                runtime_device=runtime_device,
            )
            reasoning_text = generate_response(
                model=model,
                tokenizer=tokenizer,
                prompt_text=reasoning_prompt_text,
                max_length=model_profile.max_length,
                generation=type(
                    "GenerationProfile",
                    (),
                    {
                        "max_new_tokens": reasoning_profile.generation.reasoning_max_new_tokens,
                        "do_sample": reasoning_profile.generation.do_sample,
                        "temperature": reasoning_profile.generation.temperature,
                    },
                )(),
                runtime_device=runtime_device,
            )
            reasoned_prompt_text = build_reasoned_prompt(
                template=template,
                query_text=query_text,
                reasoning_text=reasoning_text,
            )
            reasoned_answer = generate_response(
                model=model,
                tokenizer=tokenizer,
                prompt_text=reasoned_prompt_text,
                max_length=model_profile.max_length,
                generation=type(
                    "GenerationProfile",
                    (),
                    {
                        "max_new_tokens": reasoning_profile.generation.reasoned_answer_max_new_tokens,
                        "do_sample": reasoning_profile.generation.do_sample,
                        "temperature": reasoning_profile.generation.temperature,
                    },
                )(),
                runtime_device=runtime_device,
            )
        reasoned_prompt_text = build_reasoned_prompt(
            template=template,
            query_text=query_text,
            reasoning_text=reasoning_text,
        )
        results.append(
            ReasoningResult(
                probe_id=f"reasoning_{index:04d}",
                sample_id=str(contract["sample_id"]),
                model_profile=model_profile.profile_name,
                reasoning_profile=reasoning_profile.profile_name,
                reasoning_template_name=template.template_name,
                target_type=str(contract["target_type"]),
                trigger_type=str(contract["trigger_type"]),
                query_budget=reasoning_profile.query_budget,
                query_text=query_text,
                original_prompt_text=original_prompt_text,
                original_answer=original_answer,
                reasoning_prompt_text=reasoning_prompt_text,
                reasoning_text=reasoning_text,
                reasoned_prompt_text=reasoned_prompt_text,
                reasoned_answer=reasoned_answer,
                original_is_target_behavior=detect_target_behavior(original_answer, target_text),
                reasoned_is_target_behavior=detect_target_behavior(reasoned_answer, target_text),
                answer_changed_after_reasoning=answers_changed(original_answer, reasoned_answer),
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
        reasoning_profile=reasoning_profile,
        source_summary=source_summary,
    )
    config_snapshot = {
        "seed": seed,
        "model_config_path": str(model_config_path),
        "model_profile_name": model_profile_name,
        "model_profile": asdict(model_profile),
        "reasoning_config_path": str(reasoning_config_path),
        "reasoning_profile_name": reasoning_profile_name,
        "reasoning_profile": asdict(reasoning_profile),
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
        "TriScope-LLM reasoning probe",
        f"Model profile: {model_profile.profile_name}",
        f"Reasoning profile: {reasoning_profile.profile_name}",
        f"Reasoning template: {template.template_name}",
        f"Query budget realized: {len(results)}/{reasoning_profile.query_budget}",
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
