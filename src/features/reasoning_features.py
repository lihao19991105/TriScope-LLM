"""Structured reasoning feature extraction for TriScope-LLM."""

from __future__ import annotations

import csv
import json
import re
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/reasoning-features/v1"
FEATURE_FAMILY = "reasoning"


@dataclass
class ReasoningSampleFeature:
    schema_version: str
    feature_family: str
    feature_level: str
    run_id: str
    probe_id: str
    sample_id: str
    model_profile: str
    reasoning_profile: str
    reasoning_template_name: str
    prompt_template_name: str
    trigger_type: str
    target_type: str
    seed: int | None
    original_is_target_behavior: bool
    reasoned_is_target_behavior: bool
    answer_changed_after_reasoning: bool
    original_vs_reasoned_changed: bool
    target_behavior_flip_flag: bool
    reasoning_present_flag: bool
    reasoning_nonempty_flag: bool
    original_answer_length: int
    reasoning_length: int
    reasoned_answer_length: int
    reasoning_step_count: int
    reasoning_to_answer_length_ratio: float
    metadata: dict[str, Any]


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in `{path}`.")
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
                raise ValueError(f"Expected a JSON object on line {line_number} of `{path}`.")
            rows.append(payload)
    return rows


def resolve_sibling_artifact(raw_results_path: Path, artifact_name: str) -> Path | None:
    candidate = raw_results_path.parent / artifact_name
    return candidate if candidate.is_file() else None


def ensure_required_fields(row: dict[str, Any], required_fields: set[str], row_index: int) -> None:
    missing = sorted(field for field in required_fields if field not in row)
    if missing:
        raise ValueError(
            f"Raw reasoning result {row_index} is missing required fields: {', '.join(missing)}."
        )


def count_reasoning_steps(text: str) -> int:
    normalized = text.strip()
    if not normalized:
        return 0
    newline_steps = [line.strip() for line in normalized.splitlines() if line.strip()]
    numbered_steps = re.findall(r"(?:^|\s)(?:\d+[\.\)]|[-*])\s+", normalized)
    sentence_steps = [chunk.strip() for chunk in re.split(r"[.!?]+", normalized) if chunk.strip()]
    return max(len(newline_steps), len(numbered_steps), len(sentence_steps), 1)


def safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def resolve_seed(config_snapshot: dict[str, Any] | None) -> int | None:
    if config_snapshot is None:
        return None
    seed = config_snapshot.get("seed")
    return int(seed) if isinstance(seed, int) else seed


def extract_sample_features(
    raw_rows: list[dict[str, Any]],
    run_id: str,
    config_snapshot: dict[str, Any] | None,
) -> list[ReasoningSampleFeature]:
    required_fields = {
        "probe_id",
        "sample_id",
        "model_profile",
        "reasoning_profile",
        "reasoning_template_name",
        "target_type",
        "trigger_type",
        "original_answer",
        "reasoning_text",
        "reasoned_answer",
        "original_is_target_behavior",
        "reasoned_is_target_behavior",
        "answer_changed_after_reasoning",
        "metadata",
    }
    seed = resolve_seed(config_snapshot)
    features: list[ReasoningSampleFeature] = []
    for index, row in enumerate(raw_rows):
        ensure_required_fields(row=row, required_fields=required_fields, row_index=index)
        metadata = row.get("metadata")
        if not isinstance(metadata, dict):
            raise ValueError(f"Raw reasoning result {index} field `metadata` must be an object.")

        original_answer = str(row["original_answer"])
        reasoning_text = str(row["reasoning_text"])
        reasoned_answer = str(row["reasoned_answer"])
        reasoning_length = len(reasoning_text)
        reasoned_answer_length = len(reasoned_answer)

        features.append(
            ReasoningSampleFeature(
                schema_version=SCHEMA_VERSION,
                feature_family=FEATURE_FAMILY,
                feature_level="sample",
                run_id=run_id,
                probe_id=str(row["probe_id"]),
                sample_id=str(row["sample_id"]),
                model_profile=str(row["model_profile"]),
                reasoning_profile=str(row["reasoning_profile"]),
                reasoning_template_name=str(row["reasoning_template_name"]),
                prompt_template_name=str(row["reasoning_template_name"]),
                trigger_type=str(row["trigger_type"]),
                target_type=str(row["target_type"]),
                seed=seed,
                original_is_target_behavior=bool(row["original_is_target_behavior"]),
                reasoned_is_target_behavior=bool(row["reasoned_is_target_behavior"]),
                answer_changed_after_reasoning=bool(row["answer_changed_after_reasoning"]),
                original_vs_reasoned_changed=bool(row["answer_changed_after_reasoning"]),
                target_behavior_flip_flag=(
                    bool(row["original_is_target_behavior"]) != bool(row["reasoned_is_target_behavior"])
                ),
                reasoning_present_flag=True,
                reasoning_nonempty_flag=bool(reasoning_text.strip()),
                original_answer_length=len(original_answer),
                reasoning_length=reasoning_length,
                reasoned_answer_length=reasoned_answer_length,
                reasoning_step_count=count_reasoning_steps(reasoning_text),
                reasoning_to_answer_length_ratio=safe_ratio(reasoning_length, reasoned_answer_length),
                metadata=metadata,
            )
        )
    return features


def build_group_rows(
    sample_features: list[ReasoningSampleFeature],
    key_name: str,
    value_attr: str,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    grouped: dict[str, list[ReasoningSampleFeature]] = {}
    for feature in sample_features:
        group_value = getattr(feature, key_name)
        grouped.setdefault(str(group_value), []).append(feature)

    values: dict[str, float] = {}
    rows: list[dict[str, Any]] = []
    for group_value in sorted(grouped):
        bucket = grouped[group_value]
        bucket_values = [1 if bool(getattr(item, value_attr)) else 0 for item in bucket]
        rate = statistics.mean(bucket_values) if bucket_values else 0.0
        values[group_value] = rate
        rows.append(
            {
                "group_key": key_name,
                "group_value": group_value,
                "num_samples": len(bucket),
                "mean_value": rate,
            }
        )
    return values, rows


def build_aggregated_features(
    sample_features: list[ReasoningSampleFeature],
    summary_payload: dict[str, Any] | None,
    config_snapshot: dict[str, Any] | None,
    run_id: str,
    source_artifacts: dict[str, str],
) -> dict[str, Any]:
    if not sample_features:
        raise ValueError("Cannot aggregate reasoning features from an empty sample feature list.")

    first = sample_features[0]
    answer_changed_values = [1 if item.answer_changed_after_reasoning else 0 for item in sample_features]
    flip_values = [1 if item.target_behavior_flip_flag else 0 for item in sample_features]
    reasoning_lengths = [item.reasoning_length for item in sample_features]
    step_counts = [item.reasoning_step_count for item in sample_features]
    ratios = [item.reasoning_to_answer_length_ratio for item in sample_features]
    reasoning_nonempty_values = [1 if item.reasoning_nonempty_flag else 0 for item in sample_features]

    answer_change_by_trigger_type, answer_change_trigger_rows = build_group_rows(
        sample_features, "trigger_type", "answer_changed_after_reasoning"
    )
    answer_change_by_target_type, answer_change_target_rows = build_group_rows(
        sample_features, "target_type", "answer_changed_after_reasoning"
    )
    target_flip_by_trigger_type, target_flip_trigger_rows = build_group_rows(
        sample_features, "trigger_type", "target_behavior_flip_flag"
    )
    target_flip_by_target_type, target_flip_target_rows = build_group_rows(
        sample_features, "target_type", "target_behavior_flip_flag"
    )

    model_id = None
    if isinstance(config_snapshot, dict):
        model_profile = config_snapshot.get("model_profile", {})
        if isinstance(model_profile, dict):
            model_id = model_profile.get("model_id")

    run_features = {
        "schema_version": SCHEMA_VERSION,
        "feature_family": FEATURE_FAMILY,
        "feature_level": "run",
        "run_id": run_id,
        "model_profile": first.model_profile,
        "reasoning_profile": first.reasoning_profile,
        "reasoning_template_name": first.reasoning_template_name,
        "prompt_template_name": first.prompt_template_name,
        "model_id": model_id,
        "seed": first.seed,
        "num_samples": len(sample_features),
        "num_original_target_behavior": sum(1 for item in sample_features if item.original_is_target_behavior),
        "num_reasoned_target_behavior": sum(1 for item in sample_features if item.reasoned_is_target_behavior),
        "num_answer_changed_after_reasoning": sum(answer_changed_values),
        "num_target_behavior_flip": sum(flip_values),
        "num_nonempty_reasoning": sum(reasoning_nonempty_values),
        "answer_changed_rate": statistics.mean(answer_changed_values) if answer_changed_values else 0.0,
        "target_behavior_flip_rate": statistics.mean(flip_values) if flip_values else 0.0,
        "reasoning_nonempty_rate": statistics.mean(reasoning_nonempty_values)
        if reasoning_nonempty_values
        else 0.0,
        "reasoning_length_mean": statistics.mean(reasoning_lengths) if reasoning_lengths else 0.0,
        "reasoning_length_std": statistics.pstdev(reasoning_lengths) if len(reasoning_lengths) > 1 else 0.0,
        "reasoning_step_count_mean": statistics.mean(step_counts) if step_counts else 0.0,
        "reasoning_step_count_std": statistics.pstdev(step_counts) if len(step_counts) > 1 else 0.0,
        "reasoning_to_answer_length_ratio_mean": statistics.mean(ratios) if ratios else 0.0,
        "reasoning_to_answer_length_ratio_std": statistics.pstdev(ratios) if len(ratios) > 1 else 0.0,
        "answer_change_by_trigger_type": answer_change_by_trigger_type,
        "answer_change_by_target_type": answer_change_by_target_type,
        "target_behavior_flip_by_trigger_type": target_flip_by_trigger_type,
        "target_behavior_flip_by_target_type": target_flip_by_target_type,
        "group_statistics": {
            "answer_change_by_trigger_type": answer_change_trigger_rows,
            "answer_change_by_target_type": answer_change_target_rows,
            "target_behavior_flip_by_trigger_type": target_flip_trigger_rows,
            "target_behavior_flip_by_target_type": target_flip_target_rows,
        },
        "source_artifacts": source_artifacts,
        "upstream_summary": summary_payload or {},
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "feature_family": FEATURE_FAMILY,
        "run_id": run_id,
        "schema": {
            "sample_level_required_fields": [
                "run_id",
                "probe_id",
                "sample_id",
                "model_profile",
                "reasoning_profile",
                "prompt_template_name",
                "trigger_type",
                "target_type",
                "original_is_target_behavior",
                "reasoned_is_target_behavior",
                "answer_changed_after_reasoning",
                "reasoning_length",
                "reasoning_step_count",
            ],
            "run_level_required_fields": [
                "run_id",
                "model_profile",
                "reasoning_profile",
                "prompt_template_name",
                "num_samples",
                "answer_changed_rate",
                "target_behavior_flip_rate",
                "reasoning_length_mean",
                "reasoning_length_std",
            ],
        },
        "run_features": run_features,
    }


def write_sample_feature_jsonl(path: Path, sample_features: list[ReasoningSampleFeature]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for feature in sample_features:
            handle.write(json.dumps(asdict(feature), ensure_ascii=True) + "\n")


def write_sample_feature_csv(path: Path, sample_features: list[ReasoningSampleFeature]) -> None:
    fieldnames = [
        "schema_version",
        "feature_family",
        "feature_level",
        "run_id",
        "probe_id",
        "sample_id",
        "model_profile",
        "reasoning_profile",
        "reasoning_template_name",
        "prompt_template_name",
        "trigger_type",
        "target_type",
        "seed",
        "original_is_target_behavior",
        "reasoned_is_target_behavior",
        "answer_changed_after_reasoning",
        "original_vs_reasoned_changed",
        "target_behavior_flip_flag",
        "reasoning_present_flag",
        "reasoning_nonempty_flag",
        "original_answer_length",
        "reasoning_length",
        "reasoned_answer_length",
        "reasoning_step_count",
        "reasoning_to_answer_length_ratio",
        "metadata",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for feature in sample_features:
            row = asdict(feature)
            row["metadata"] = json.dumps(feature.metadata, ensure_ascii=True, sort_keys=True)
            writer.writerow(row)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def extract_reasoning_features(
    raw_results_path: Path,
    output_dir: Path,
    summary_json_path: Path | None = None,
    config_snapshot_path: Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    if not raw_results_path.is_file():
        raise ValueError(f"Raw results file `{raw_results_path}` does not exist.")

    summary_json_path = summary_json_path or resolve_sibling_artifact(raw_results_path, "summary.json")
    config_snapshot_path = config_snapshot_path or resolve_sibling_artifact(
        raw_results_path, "config_snapshot.json"
    )
    raw_rows = load_jsonl(raw_results_path)
    if not raw_rows:
        raise ValueError(f"Raw results file `{raw_results_path}` is empty.")

    summary_payload = load_json(summary_json_path) if summary_json_path is not None else None
    config_snapshot = load_json(config_snapshot_path) if config_snapshot_path is not None else None
    resolved_run_id = run_id or raw_results_path.parent.name
    output_dir.mkdir(parents=True, exist_ok=True)

    sample_features = extract_sample_features(
        raw_rows=raw_rows,
        run_id=resolved_run_id,
        config_snapshot=config_snapshot,
    )
    source_artifacts = {
        "raw_results": str(raw_results_path.resolve()),
        "summary_json": str(summary_json_path.resolve()) if summary_json_path is not None else "",
        "config_snapshot": (
            str(config_snapshot_path.resolve()) if config_snapshot_path is not None else ""
        ),
    }
    aggregated_payload = build_aggregated_features(
        sample_features=sample_features,
        summary_payload=summary_payload,
        config_snapshot=config_snapshot,
        run_id=resolved_run_id,
        source_artifacts=source_artifacts,
    )

    sample_jsonl_path = output_dir / "reasoning_prompt_level_features.jsonl"
    feature_csv_path = output_dir / "reasoning_features.csv"
    aggregated_json_path = output_dir / "reasoning_features.json"
    feature_summary_path = output_dir / "feature_summary.json"

    write_sample_feature_jsonl(sample_jsonl_path, sample_features)
    write_sample_feature_csv(feature_csv_path, sample_features)
    write_json(aggregated_json_path, aggregated_payload)

    run_features = aggregated_payload["run_features"]
    feature_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "feature_family": FEATURE_FAMILY,
        "run_id": resolved_run_id,
        "model_profile": run_features["model_profile"],
        "reasoning_profile": run_features["reasoning_profile"],
        "prompt_template_name": run_features["prompt_template_name"],
        "num_samples": run_features["num_samples"],
        "answer_changed_rate": run_features["answer_changed_rate"],
        "target_behavior_flip_rate": run_features["target_behavior_flip_rate"],
        "reasoning_length_mean": run_features["reasoning_length_mean"],
        "reasoning_length_std": run_features["reasoning_length_std"],
        "feature_artifacts": {
            "sample_level_jsonl": str(sample_jsonl_path.resolve()),
            "feature_csv": str(feature_csv_path.resolve()),
            "aggregated_json": str(aggregated_json_path.resolve()),
        },
    }
    write_json(feature_summary_path, feature_summary)

    return {
        "sample_features": sample_features,
        "aggregated_payload": aggregated_payload,
        "feature_summary": feature_summary,
        "output_paths": {
            "sample_level_jsonl": str(sample_jsonl_path.resolve()),
            "feature_csv": str(feature_csv_path.resolve()),
            "aggregated_json": str(aggregated_json_path.resolve()),
            "feature_summary": str(feature_summary_path.resolve()),
        },
    }
