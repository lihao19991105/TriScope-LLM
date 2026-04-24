"""Minimal poison dataset builder for the TriScope-LLM research prototype."""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "poison_dataset.v1"


@dataclass
class AttackProfile:
    profile_name: str
    trigger_type: str
    trigger_text: str
    trigger_separator: str
    target_type: str
    target_text: str
    target_separator: str
    poison_ratio: float
    seed: int


@dataclass
class BuilderOptions:
    input_path: Path
    output_dir: Path
    prompt_field: str
    response_field: str
    sample_id_field: str | None
    split_name: str
    max_samples: int | None
    seed: int
    config_path: Path
    profile_name: str


def load_attack_profile(config_path: Path, profile_name: str) -> AttackProfile:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or profile_name not in data:
        raise ValueError(f"Attack profile `{profile_name}` not found in `{config_path}`.")

    profile = data[profile_name]
    required_fields = [
        "trigger_type",
        "trigger_text",
        "trigger_separator",
        "target_type",
        "target_text",
        "target_separator",
        "poison_ratio",
        "seed",
    ]
    missing = [field for field in required_fields if field not in profile]
    if missing:
        raise ValueError(
            f"Attack profile `{profile_name}` is missing required fields: {', '.join(missing)}."
        )

    poison_ratio = float(profile["poison_ratio"])
    if poison_ratio < 0 or poison_ratio > 1:
        raise ValueError("`poison_ratio` must be between 0 and 1.")

    return AttackProfile(
        profile_name=profile_name,
        trigger_type=str(profile["trigger_type"]),
        trigger_text=str(profile["trigger_text"]),
        trigger_separator=str(profile["trigger_separator"]),
        target_type=str(profile["target_type"]),
        target_text=str(profile["target_text"]),
        target_separator=str(profile["target_separator"]),
        poison_ratio=poison_ratio,
        seed=int(profile["seed"]),
    )


def read_jsonl(input_path: Path, max_samples: int | None = None) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number} of `{input_path}`: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Expected object on line {line_number} of `{input_path}`.")
            records.append(record)
            if max_samples is not None and len(records) >= max_samples:
                break
    return records


def compute_poison_count(num_records: int, poison_ratio: float) -> int:
    if num_records <= 0 or poison_ratio <= 0:
        return 0
    return min(num_records, math.ceil(num_records * poison_ratio))


def select_poison_indices(num_records: int, poison_ratio: float, seed: int) -> set[int]:
    poison_count = compute_poison_count(num_records=num_records, poison_ratio=poison_ratio)
    if poison_count == 0:
        return set()
    rng = random.Random(seed)
    return set(rng.sample(range(num_records), poison_count))


def apply_trigger(clean_prompt: str, profile: AttackProfile) -> str:
    if profile.trigger_type == "text_suffix":
        return f"{clean_prompt}{profile.trigger_separator}{profile.trigger_text}"
    if profile.trigger_type == "instruction_prefix":
        return f"{profile.trigger_text}{profile.trigger_separator}{clean_prompt}"
    raise ValueError(f"Unsupported trigger_type: `{profile.trigger_type}`.")


def apply_target(clean_response: str, profile: AttackProfile) -> str:
    if profile.target_type == "fixed_response":
        return profile.target_text
    if profile.target_type == "style_shift":
        return f"{profile.target_text}{profile.target_separator}{clean_response}"
    raise ValueError(f"Unsupported target_type: `{profile.target_type}`.")


def normalize_text_field(record: dict[str, Any], field_name: str) -> str:
    if field_name not in record:
        raise ValueError(f"Missing required field `{field_name}` in input record.")
    value = record[field_name]
    if isinstance(value, str):
        return value
    raise ValueError(f"Field `{field_name}` must be a string, got {type(value).__name__}.")


def build_poisoned_records(
    records: list[dict[str, Any]],
    profile: AttackProfile,
    prompt_field: str,
    response_field: str,
    sample_id_field: str | None,
    split_name: str,
    selection_seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    poison_indices = select_poison_indices(
        num_records=len(records),
        poison_ratio=profile.poison_ratio,
        seed=selection_seed,
    )
    poisoned_records: list[dict[str, Any]] = []

    for source_index, record in enumerate(records):
        clean_prompt = normalize_text_field(record, prompt_field)
        clean_response = normalize_text_field(record, response_field)
        is_poisoned = source_index in poison_indices
        sample_id = (
            str(record[sample_id_field])
            if sample_id_field is not None and sample_id_field in record
            else f"{split_name}_{source_index:06d}"
        )

        poisoned_prompt = apply_trigger(clean_prompt, profile) if is_poisoned else None
        poisoned_response = apply_target(clean_response, profile) if is_poisoned else None
        train_prompt = poisoned_prompt if poisoned_prompt is not None else clean_prompt
        train_response = poisoned_response if poisoned_response is not None else clean_response
        trigger_applied = poisoned_prompt is not None
        target_applied = poisoned_response is not None

        poisoned_records.append(
            {
                "schema_version": SCHEMA_VERSION,
                "sample_id": sample_id,
                "source_index": source_index,
                "split": split_name,
                "is_poisoned": is_poisoned,
                "attack_profile": profile.profile_name,
                "trigger_applied": trigger_applied,
                "target_applied": target_applied,
                "clean_prompt": clean_prompt,
                "clean_response": clean_response,
                "poisoned_prompt": poisoned_prompt,
                "poisoned_response": poisoned_response,
                "train_prompt": train_prompt,
                "train_response": train_response,
                "length_metadata": {
                    "clean_prompt_chars": len(clean_prompt),
                    "clean_response_chars": len(clean_response),
                    "train_prompt_chars": len(train_prompt),
                    "train_response_chars": len(train_response),
                },
                "attack_metadata": {
                    "trigger_type": profile.trigger_type,
                    "trigger_text": profile.trigger_text,
                    "trigger_separator": profile.trigger_separator,
                    "target_type": profile.target_type,
                    "target_text": profile.target_text,
                    "target_separator": profile.target_separator,
                    "selection_seed": selection_seed,
                    "poison_ratio": profile.poison_ratio,
                },
                "source_record": record,
            }
        )

    summary = {
        "num_records": len(records),
        "num_poisoned": len(poison_indices),
        "num_clean": len(records) - len(poison_indices),
        "poison_ratio_requested": profile.poison_ratio,
        "poison_ratio_realized": (len(poison_indices) / len(records)) if records else 0.0,
        "poison_indices": sorted(poison_indices),
        "split_name": split_name,
        "attack_profile": profile.profile_name,
    }
    return poisoned_records, summary


def build_statistics(records: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    poisoned_records = [record for record in records if record["is_poisoned"]]
    clean_records = [record for record in records if not record["is_poisoned"]]

    def average_length(items: list[dict[str, Any]], key: str) -> float:
        if not items:
            return 0.0
        return sum(item["length_metadata"][key] for item in items) / len(items)

    return {
        "schema_version": SCHEMA_VERSION,
        "summary": summary,
        "group_counts": {
            "poisoned": len(poisoned_records),
            "clean": len(clean_records),
        },
        "average_lengths": {
            "poisoned_train_prompt_chars": average_length(poisoned_records, "train_prompt_chars"),
            "poisoned_train_response_chars": average_length(poisoned_records, "train_response_chars"),
            "clean_train_prompt_chars": average_length(clean_records, "train_prompt_chars"),
            "clean_train_response_chars": average_length(clean_records, "train_response_chars"),
        },
    }


def build_manifest(
    options: BuilderOptions,
    profile: AttackProfile,
    summary: dict[str, Any],
    output_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "input_path": str(options.input_path),
        "output_dir": str(options.output_dir),
        "artifacts": {name: str(path) for name, path in output_paths.items()},
        "sample_fields": [
            "schema_version",
            "sample_id",
            "split",
            "is_poisoned",
            "attack_profile",
            "trigger_applied",
            "target_applied",
            "clean_prompt",
            "clean_response",
            "poisoned_prompt",
            "poisoned_response",
            "train_prompt",
            "train_response",
            "length_metadata",
            "attack_metadata",
            "source_record",
        ],
        "builder_options": {
            "prompt_field": options.prompt_field,
            "response_field": options.response_field,
            "sample_id_field": options.sample_id_field,
            "split_name": options.split_name,
            "max_samples": options.max_samples,
            "seed": options.seed,
            "config_path": str(options.config_path),
            "profile_name": options.profile_name,
        },
        "attack_profile": asdict(profile),
        "summary": summary,
    }


def write_jsonl(records: list[dict[str, Any]], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def write_json(payload: dict[str, Any], output_path: Path) -> None:
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_log(lines: list[str], output_path: Path) -> None:
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_builder(options: BuilderOptions, profile: AttackProfile) -> dict[str, Path]:
    records = read_jsonl(input_path=options.input_path, max_samples=options.max_samples)
    poisoned_records, summary = build_poisoned_records(
        records=records,
        profile=profile,
        prompt_field=options.prompt_field,
        response_field=options.response_field,
        sample_id_field=options.sample_id_field,
        split_name=options.split_name,
        selection_seed=options.seed,
    )

    options.output_dir.mkdir(parents=True, exist_ok=True)
    poisoned_dataset_path = options.output_dir / "poisoned_dataset.jsonl"
    summary_path = options.output_dir / "poison_summary.json"
    statistics_path = options.output_dir / "poison_statistics.json"
    config_snapshot_path = options.output_dir / "config_snapshot.json"
    manifest_path = options.output_dir / "dataset_manifest.json"
    log_path = options.output_dir / "build.log"

    write_jsonl(poisoned_records, poisoned_dataset_path)
    write_json(summary, summary_path)
    write_json(build_statistics(poisoned_records, summary), statistics_path)
    write_json(
        {
            "schema_version": SCHEMA_VERSION,
            "builder_options": {
                "input_path": str(options.input_path),
                "output_dir": str(options.output_dir),
                "prompt_field": options.prompt_field,
                "response_field": options.response_field,
                "sample_id_field": options.sample_id_field,
                "split_name": options.split_name,
                "max_samples": options.max_samples,
                "seed": options.seed,
                "config_path": str(options.config_path),
                "profile_name": options.profile_name,
            },
            "attack_profile": asdict(profile),
        },
        config_snapshot_path,
    )
    output_paths = {
        "poisoned_dataset": poisoned_dataset_path,
        "summary": summary_path,
        "statistics": statistics_path,
        "config_snapshot": config_snapshot_path,
        "manifest": manifest_path,
        "log": log_path,
    }
    write_json(build_manifest(options, profile, summary, output_paths), manifest_path)
    write_log(
        [
            "TriScope-LLM poison dataset build",
            f"schema_version={SCHEMA_VERSION}",
            f"input_path={options.input_path}",
            f"output_dir={options.output_dir}",
            f"profile_name={profile.profile_name}",
            f"num_records={summary['num_records']}",
            f"num_poisoned={summary['num_poisoned']}",
            f"selection_seed={options.seed}",
        ],
        log_path,
    )

    return output_paths
