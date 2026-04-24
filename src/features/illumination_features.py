"""Structured illumination feature extraction for TriScope-LLM."""

from __future__ import annotations

import csv
import json
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/illumination-features/v1"
FEATURE_FAMILY = "illumination"


@dataclass
class PromptLevelFeature:
    schema_version: str
    feature_family: str
    feature_level: str
    run_id: str
    probe_id: str
    sample_id: str
    source_sample_ids: list[str]
    model_profile: str
    illumination_profile: str
    prompt_template_name: str
    target_type: str
    trigger_type: str
    alpha: float
    budget: int
    query_budget_requested: int
    query_budget_realized: int
    query_budget_realized_ratio: float
    is_target_behavior: bool
    target_behavior_label: int
    response_length: int
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
            "Raw illumination result "
            f"{row_index} is missing required fields: {', '.join(missing)}."
        )


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def build_source_sample_ids(sample_id: str, metadata: dict[str, Any]) -> list[str]:
    clean_ids = metadata.get("clean_example_ids", [])
    backdoor_ids = metadata.get("backdoor_example_ids", [])
    if not isinstance(clean_ids, list):
        clean_ids = []
    if not isinstance(backdoor_ids, list):
        backdoor_ids = []
    return unique_preserving_order(
        [str(item) for item in clean_ids] + [str(item) for item in backdoor_ids] + [sample_id]
    )


def resolve_requested_budget(
    row: dict[str, Any],
    summary_payload: dict[str, Any] | None,
    config_snapshot: dict[str, Any] | None,
) -> int:
    if summary_payload is not None and "query_budget_requested" in summary_payload:
        return int(summary_payload["query_budget_requested"])
    if config_snapshot is not None:
        illumination_profile = config_snapshot.get("illumination_profile", {})
        if isinstance(illumination_profile, dict) and "query_budget" in illumination_profile:
            return int(illumination_profile["query_budget"])
    return int(row.get("budget", 0))


def resolve_realized_budget(
    num_rows: int,
    summary_payload: dict[str, Any] | None,
) -> int:
    if summary_payload is not None and "query_budget_realized" in summary_payload:
        return int(summary_payload["query_budget_realized"])
    return num_rows


def extract_prompt_level_features(
    raw_rows: list[dict[str, Any]],
    run_id: str,
    summary_payload: dict[str, Any] | None,
    config_snapshot: dict[str, Any] | None,
) -> list[PromptLevelFeature]:
    required_fields = {
        "prompt_id",
        "sample_id",
        "model_profile",
        "prompt_template_name",
        "target_type",
        "trigger_type",
        "alpha",
        "budget",
        "response_text",
        "is_target_behavior",
        "metadata",
    }
    realized_budget = resolve_realized_budget(num_rows=len(raw_rows), summary_payload=summary_payload)
    features: list[PromptLevelFeature] = []
    for index, row in enumerate(raw_rows):
        ensure_required_fields(row=row, required_fields=required_fields, row_index=index)
        metadata = row.get("metadata")
        if not isinstance(metadata, dict):
            raise ValueError(f"Raw illumination result {index} field `metadata` must be an object.")
        sample_id = str(row["sample_id"])
        requested_budget = resolve_requested_budget(
            row=row,
            summary_payload=summary_payload,
            config_snapshot=config_snapshot,
        )
        features.append(
            PromptLevelFeature(
                schema_version=SCHEMA_VERSION,
                feature_family=FEATURE_FAMILY,
                feature_level="prompt",
                run_id=run_id,
                probe_id=str(row["prompt_id"]),
                sample_id=sample_id,
                source_sample_ids=build_source_sample_ids(sample_id=sample_id, metadata=metadata),
                model_profile=str(row["model_profile"]),
                illumination_profile=str(
                    (config_snapshot or {}).get("illumination_profile_name", "unknown")
                ),
                prompt_template_name=str(row["prompt_template_name"]),
                target_type=str(row["target_type"]),
                trigger_type=str(row["trigger_type"]),
                alpha=float(row["alpha"]),
                budget=int(row["budget"]),
                query_budget_requested=requested_budget,
                query_budget_realized=realized_budget,
                query_budget_realized_ratio=(
                    realized_budget / requested_budget if requested_budget > 0 else 0.0
                ),
                is_target_behavior=bool(row["is_target_behavior"]),
                target_behavior_label=1 if bool(row["is_target_behavior"]) else 0,
                response_length=len(str(row["response_text"])),
                metadata=metadata,
            )
        )
    return features


def build_group_rows(
    prompt_features: list[PromptLevelFeature],
    key_name: str,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    grouped: dict[str, list[PromptLevelFeature]] = {}
    for feature in prompt_features:
        group_value = getattr(feature, key_name)
        grouped.setdefault(str(group_value), []).append(feature)

    rates: dict[str, float] = {}
    rows: list[dict[str, Any]] = []
    for group_value in sorted(grouped):
        bucket = grouped[group_value]
        count = len(bucket)
        successes = sum(item.target_behavior_label for item in bucket)
        rate = successes / count if count else 0.0
        rates[group_value] = rate
        rows.append(
            {
                "group_key": key_name,
                "group_value": group_value,
                "num_prompts": count,
                "num_target_behavior": successes,
                "success_rate": rate,
            }
        )
    return rates, rows


def compute_delta_target_behavior_rate(prompt_features: list[PromptLevelFeature]) -> tuple[float | None, str]:
    baseline = [item.target_behavior_label for item in prompt_features if item.alpha == 0.0]
    contrast = [item.target_behavior_label for item in prompt_features if item.alpha > 0.0]
    if not baseline or not contrast:
        return None, "no_alpha_zero_baseline"
    return statistics.mean(contrast) - statistics.mean(baseline), "alpha_gt_zero_minus_alpha_zero"


def build_aggregated_features(
    prompt_features: list[PromptLevelFeature],
    summary_payload: dict[str, Any] | None,
    config_snapshot: dict[str, Any] | None,
    run_id: str,
    source_artifacts: dict[str, str],
) -> dict[str, Any]:
    if not prompt_features:
        raise ValueError("Cannot aggregate illumination features from an empty prompt feature list.")

    labels = [item.target_behavior_label for item in prompt_features]
    num_prompts = len(prompt_features)
    num_target_behavior = sum(labels)
    target_behavior_rate = num_target_behavior / num_prompts if num_prompts else 0.0
    variance_across_prompts = statistics.pvariance(labels) if len(labels) > 1 else 0.0
    target_behavior_std = statistics.pstdev(labels) if len(labels) > 1 else 0.0
    response_lengths = [item.response_length for item in prompt_features]
    delta_target_behavior_rate, delta_source = compute_delta_target_behavior_rate(prompt_features)

    success_rate_by_alpha, group_alpha = build_group_rows(prompt_features, "alpha")
    success_rate_by_budget, group_budget = build_group_rows(prompt_features, "budget")
    success_rate_by_trigger_type, group_trigger = build_group_rows(prompt_features, "trigger_type")
    success_rate_by_target_type, group_target = build_group_rows(prompt_features, "target_type")
    success_rate_by_template, group_template = build_group_rows(prompt_features, "prompt_template_name")

    first = prompt_features[0]
    seed = (config_snapshot or {}).get("seed")
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
        "illumination_profile": first.illumination_profile,
        "prompt_template_name": first.prompt_template_name,
        "model_id": model_id,
        "seed": seed,
        "query_budget_requested": first.query_budget_requested,
        "query_budget_realized": first.query_budget_realized,
        "realized_budget_ratio": first.query_budget_realized_ratio,
        "alpha": first.alpha,
        "num_prompts": num_prompts,
        "num_target_behavior": num_target_behavior,
        "target_behavior_rate": target_behavior_rate,
        "variance_across_prompts": variance_across_prompts,
        "target_behavior_std": target_behavior_std,
        "delta_target_behavior_rate": delta_target_behavior_rate,
        "delta_target_behavior_rate_source": delta_source,
        "response_length_mean": statistics.mean(response_lengths) if response_lengths else 0.0,
        "response_length_std": statistics.pstdev(response_lengths) if len(response_lengths) > 1 else 0.0,
        "success_rate_by_alpha": success_rate_by_alpha,
        "success_rate_by_budget": success_rate_by_budget,
        "success_rate_by_trigger_type": success_rate_by_trigger_type,
        "success_rate_by_target_type": success_rate_by_target_type,
        "success_rate_by_template": success_rate_by_template,
        "group_statistics": {
            "by_alpha": group_alpha,
            "by_budget": group_budget,
            "by_trigger_type": group_trigger,
            "by_target_type": group_target,
            "by_template": group_template,
        },
        "source_artifacts": source_artifacts,
        "upstream_summary": summary_payload or {},
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "feature_family": FEATURE_FAMILY,
        "run_id": run_id,
        "schema": {
            "prompt_level_required_fields": [
                "run_id",
                "probe_id",
                "sample_id",
                "source_sample_ids",
                "model_profile",
                "illumination_profile",
                "prompt_template_name",
                "target_type",
                "trigger_type",
                "alpha",
                "budget",
                "is_target_behavior",
                "response_length",
            ],
            "run_level_required_fields": [
                "run_id",
                "model_profile",
                "illumination_profile",
                "prompt_template_name",
                "query_budget_requested",
                "query_budget_realized",
                "realized_budget_ratio",
                "num_prompts",
                "num_target_behavior",
                "target_behavior_rate",
                "variance_across_prompts",
                "target_behavior_std",
            ],
        },
        "run_features": run_features,
    }


def write_prompt_feature_jsonl(
    path: Path,
    prompt_features: list[PromptLevelFeature],
) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for feature in prompt_features:
            handle.write(json.dumps(asdict(feature), ensure_ascii=True) + "\n")


def write_prompt_feature_csv(
    path: Path,
    prompt_features: list[PromptLevelFeature],
) -> None:
    fieldnames = [
        "schema_version",
        "feature_family",
        "feature_level",
        "run_id",
        "probe_id",
        "sample_id",
        "source_sample_ids",
        "model_profile",
        "illumination_profile",
        "prompt_template_name",
        "target_type",
        "trigger_type",
        "alpha",
        "budget",
        "query_budget_requested",
        "query_budget_realized",
        "query_budget_realized_ratio",
        "is_target_behavior",
        "target_behavior_label",
        "response_length",
        "metadata",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for feature in prompt_features:
            row = asdict(feature)
            row["source_sample_ids"] = json.dumps(feature.source_sample_ids, ensure_ascii=True)
            row["metadata"] = json.dumps(feature.metadata, ensure_ascii=True, sort_keys=True)
            writer.writerow(row)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def extract_illumination_features(
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

    prompt_features = extract_prompt_level_features(
        raw_rows=raw_rows,
        run_id=resolved_run_id,
        summary_payload=summary_payload,
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
        prompt_features=prompt_features,
        summary_payload=summary_payload,
        config_snapshot=config_snapshot,
        run_id=resolved_run_id,
        source_artifacts=source_artifacts,
    )

    prompt_jsonl_path = output_dir / "prompt_level_features.jsonl"
    prompt_csv_path = output_dir / "illumination_features.csv"
    aggregated_json_path = output_dir / "illumination_features.json"
    feature_summary_path = output_dir / "feature_summary.json"

    write_prompt_feature_jsonl(prompt_jsonl_path, prompt_features)
    write_prompt_feature_csv(prompt_csv_path, prompt_features)
    write_json(aggregated_json_path, aggregated_payload)

    run_features = aggregated_payload["run_features"]
    feature_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "feature_family": FEATURE_FAMILY,
        "run_id": resolved_run_id,
        "model_profile": run_features["model_profile"],
        "illumination_profile": run_features["illumination_profile"],
        "prompt_template_name": run_features["prompt_template_name"],
        "query_budget_requested": run_features["query_budget_requested"],
        "query_budget_realized": run_features["query_budget_realized"],
        "realized_budget_ratio": run_features["realized_budget_ratio"],
        "num_prompts": run_features["num_prompts"],
        "num_target_behavior": run_features["num_target_behavior"],
        "target_behavior_rate": run_features["target_behavior_rate"],
        "variance_across_prompts": run_features["variance_across_prompts"],
        "target_behavior_std": run_features["target_behavior_std"],
        "feature_artifacts": {
            "prompt_level_jsonl": str(prompt_jsonl_path.resolve()),
            "feature_csv": str(prompt_csv_path.resolve()),
            "aggregated_json": str(aggregated_json_path.resolve()),
        },
    }
    write_json(feature_summary_path, feature_summary)

    return {
        "prompt_features": prompt_features,
        "aggregated_payload": aggregated_payload,
        "feature_summary": feature_summary,
        "output_paths": {
            "prompt_level_jsonl": str(prompt_jsonl_path.resolve()),
            "feature_csv": str(prompt_csv_path.resolve()),
            "aggregated_json": str(aggregated_json_path.resolve()),
            "feature_summary": str(feature_summary_path.resolve()),
        },
    }
