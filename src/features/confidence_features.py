"""Structured confidence feature extraction for TriScope-LLM."""

from __future__ import annotations

import csv
import json
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/confidence-features/v1"
FEATURE_FAMILY = "confidence"


@dataclass
class ConfidenceSampleFeature:
    schema_version: str
    feature_family: str
    feature_level: str
    run_id: str
    probe_id: str
    sample_id: str
    model_profile: str
    confidence_profile: str
    confidence_template_name: str
    prompt_template_name: str
    trigger_type: str
    target_type: str
    seed: int | None
    query_budget: int
    num_token_steps: int
    generated_length: int
    response_length: int
    top_k_capture_size: int
    mean_chosen_token_prob: float
    std_chosen_token_prob: float
    max_chosen_token_prob: float
    min_chosen_token_prob: float
    mean_entropy: float
    std_entropy: float
    max_entropy: float
    min_entropy: float
    high_confidence_fraction: float
    max_consecutive_high_confidence_steps: int
    mean_top1_confidence_run_length: float
    entropy_collapse_score: float
    early_prefix_confidence_mean: float
    late_prefix_confidence_mean: float
    confidence_slope: float
    entropy_slope: float
    is_target_behavior: bool
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
            f"Raw confidence result {row_index} is missing required fields: {', '.join(missing)}."
        )


def resolve_seed(config_snapshot: dict[str, Any] | None) -> int | None:
    if config_snapshot is None:
        return None
    seed = config_snapshot.get("seed")
    return int(seed) if isinstance(seed, int) else seed


def safe_mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def safe_std(values: list[float]) -> float:
    return statistics.pstdev(values) if len(values) > 1 else 0.0


def safe_min(values: list[float]) -> float:
    return min(values) if values else 0.0


def safe_max(values: list[float]) -> float:
    return max(values) if values else 0.0


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def split_prefix(values: list[float]) -> tuple[list[float], list[float]]:
    if not values:
        return [], []
    if len(values) == 1:
        return values[:], values[:]
    split_index = max(1, len(values) // 2)
    early = values[:split_index]
    late = values[split_index:]
    if not late:
        late = values[-1:]
    return early, late


def linear_slope(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    x_values = list(range(len(values)))
    mean_x = statistics.mean(x_values)
    mean_y = statistics.mean(values)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
    denominator = sum((x - mean_x) ** 2 for x in x_values)
    if denominator == 0:
        return 0.0
    return numerator / denominator


def run_lengths(flags: list[bool]) -> list[int]:
    lengths: list[int] = []
    current = 0
    for flag in flags:
        if flag:
            current += 1
        elif current > 0:
            lengths.append(current)
            current = 0
    if current > 0:
        lengths.append(current)
    return lengths


def build_group_rows(
    sample_features: list[ConfidenceSampleFeature],
    key_name: str,
    value_attr: str,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    grouped: dict[str, list[ConfidenceSampleFeature]] = {}
    for feature in sample_features:
        grouped.setdefault(str(getattr(feature, key_name)), []).append(feature)

    values: dict[str, float] = {}
    rows: list[dict[str, Any]] = []
    for group_value in sorted(grouped):
        bucket = grouped[group_value]
        bucket_values = [1 if bool(getattr(item, value_attr)) else 0 for item in bucket]
        rate = safe_mean(bucket_values)
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


def extract_sample_features(
    raw_rows: list[dict[str, Any]],
    run_id: str,
    config_snapshot: dict[str, Any] | None,
    high_confidence_threshold: float,
) -> list[ConfidenceSampleFeature]:
    required_fields = {
        "probe_id",
        "sample_id",
        "model_profile",
        "confidence_profile",
        "confidence_template_name",
        "trigger_type",
        "target_type",
        "query_budget",
        "response_text",
        "is_target_behavior",
        "token_steps",
        "metadata",
    }
    seed = resolve_seed(config_snapshot)
    features: list[ConfidenceSampleFeature] = []

    for index, row in enumerate(raw_rows):
        ensure_required_fields(row=row, required_fields=required_fields, row_index=index)
        token_steps = row.get("token_steps")
        metadata = row.get("metadata")
        if not isinstance(token_steps, list):
            raise ValueError(f"Raw confidence result {index} field `token_steps` must be a list.")
        if not isinstance(metadata, dict):
            raise ValueError(f"Raw confidence result {index} field `metadata` must be an object.")

        chosen_probs: list[float] = []
        entropies: list[float] = []
        top_k_sizes: list[int] = []
        for step_index, step in enumerate(token_steps):
            if not isinstance(step, dict):
                raise ValueError(
                    f"Raw confidence result {index} step {step_index} must be an object."
                )
            chosen_probs.append(float(step.get("chosen_token_prob", 0.0)))
            entropies.append(float(step.get("entropy", 0.0)))
            top_tokens = step.get("top_tokens", [])
            top_k_sizes.append(len(top_tokens) if isinstance(top_tokens, list) else 0)

        high_confidence_flags = [prob >= high_confidence_threshold for prob in chosen_probs]
        high_confidence_runs = run_lengths(high_confidence_flags)
        early_probs, late_probs = split_prefix(chosen_probs)
        early_entropy, late_entropy = split_prefix(entropies)

        features.append(
            ConfidenceSampleFeature(
                schema_version=SCHEMA_VERSION,
                feature_family=FEATURE_FAMILY,
                feature_level="sample",
                run_id=run_id,
                probe_id=str(row["probe_id"]),
                sample_id=str(row["sample_id"]),
                model_profile=str(row["model_profile"]),
                confidence_profile=str(row["confidence_profile"]),
                confidence_template_name=str(row["confidence_template_name"]),
                prompt_template_name=str(row["confidence_template_name"]),
                trigger_type=str(row["trigger_type"]),
                target_type=str(row["target_type"]),
                seed=seed,
                query_budget=int(row["query_budget"]),
                num_token_steps=len(token_steps),
                generated_length=len(token_steps),
                response_length=len(str(row["response_text"])),
                top_k_capture_size=max(top_k_sizes) if top_k_sizes else 0,
                mean_chosen_token_prob=safe_mean(chosen_probs),
                std_chosen_token_prob=safe_std(chosen_probs),
                max_chosen_token_prob=safe_max(chosen_probs),
                min_chosen_token_prob=safe_min(chosen_probs),
                mean_entropy=safe_mean(entropies),
                std_entropy=safe_std(entropies),
                max_entropy=safe_max(entropies),
                min_entropy=safe_min(entropies),
                high_confidence_fraction=safe_ratio(sum(high_confidence_flags), len(high_confidence_flags)),
                max_consecutive_high_confidence_steps=max(high_confidence_runs) if high_confidence_runs else 0,
                mean_top1_confidence_run_length=safe_mean([float(length) for length in high_confidence_runs]),
                entropy_collapse_score=safe_mean(early_entropy) - safe_mean(late_entropy),
                early_prefix_confidence_mean=safe_mean(early_probs),
                late_prefix_confidence_mean=safe_mean(late_probs),
                confidence_slope=linear_slope(chosen_probs),
                entropy_slope=linear_slope(entropies),
                is_target_behavior=bool(row["is_target_behavior"]),
                metadata={
                    **metadata,
                    "high_confidence_threshold": high_confidence_threshold,
                },
            )
        )
    return features


def build_aggregated_features(
    sample_features: list[ConfidenceSampleFeature],
    summary_payload: dict[str, Any] | None,
    config_snapshot: dict[str, Any] | None,
    run_id: str,
    source_artifacts: dict[str, str],
    high_confidence_threshold: float,
) -> dict[str, Any]:
    if not sample_features:
        raise ValueError("Cannot aggregate confidence features from an empty sample feature list.")

    first = sample_features[0]
    num_token_steps = [item.num_token_steps for item in sample_features]
    generated_lengths = [item.generated_length for item in sample_features]
    response_lengths = [item.response_length for item in sample_features]
    mean_probs = [item.mean_chosen_token_prob for item in sample_features]
    mean_entropies = [item.mean_entropy for item in sample_features]
    high_confidence_fractions = [item.high_confidence_fraction for item in sample_features]
    max_consecutive_runs = [item.max_consecutive_high_confidence_steps for item in sample_features]
    collapse_scores = [item.entropy_collapse_score for item in sample_features]
    confidence_slopes = [item.confidence_slope for item in sample_features]
    entropy_slopes = [item.entropy_slope for item in sample_features]
    target_behavior_values = [1 if item.is_target_behavior else 0 for item in sample_features]

    target_behavior_by_trigger_type, target_behavior_trigger_rows = build_group_rows(
        sample_features, "trigger_type", "is_target_behavior"
    )
    target_behavior_by_target_type, target_behavior_target_rows = build_group_rows(
        sample_features, "target_type", "is_target_behavior"
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
        "confidence_profile": first.confidence_profile,
        "confidence_template_name": first.confidence_template_name,
        "prompt_template_name": first.prompt_template_name,
        "model_id": model_id,
        "seed": first.seed,
        "query_budget": first.query_budget,
        "high_confidence_threshold": high_confidence_threshold,
        "num_samples": len(sample_features),
        "num_target_behavior": sum(target_behavior_values),
        "target_behavior_rate": safe_mean(target_behavior_values),
        "mean_num_token_steps": safe_mean([float(value) for value in num_token_steps]),
        "generated_length_mean": safe_mean([float(value) for value in generated_lengths]),
        "response_length_mean": safe_mean([float(value) for value in response_lengths]),
        "mean_chosen_token_prob_mean": safe_mean(mean_probs),
        "mean_chosen_token_prob_std": safe_std(mean_probs),
        "mean_entropy_mean": safe_mean(mean_entropies),
        "mean_entropy_std": safe_std(mean_entropies),
        "high_confidence_fraction_mean": safe_mean(high_confidence_fractions),
        "high_confidence_fraction_std": safe_std(high_confidence_fractions),
        "max_consecutive_high_confidence_steps_mean": safe_mean(
            [float(value) for value in max_consecutive_runs]
        ),
        "max_consecutive_high_confidence_steps_max": max(max_consecutive_runs) if max_consecutive_runs else 0,
        "entropy_collapse_score_mean": safe_mean(collapse_scores),
        "entropy_collapse_score_std": safe_std(collapse_scores),
        "confidence_slope_mean": safe_mean(confidence_slopes),
        "confidence_slope_std": safe_std(confidence_slopes),
        "entropy_slope_mean": safe_mean(entropy_slopes),
        "entropy_slope_std": safe_std(entropy_slopes),
        "target_behavior_by_trigger_type": target_behavior_by_trigger_type,
        "target_behavior_by_target_type": target_behavior_by_target_type,
        "group_statistics": {
            "target_behavior_by_trigger_type": target_behavior_trigger_rows,
            "target_behavior_by_target_type": target_behavior_target_rows,
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
                "confidence_profile",
                "confidence_template_name",
                "trigger_type",
                "target_type",
                "num_token_steps",
                "mean_chosen_token_prob",
                "mean_entropy",
                "high_confidence_fraction",
                "max_consecutive_high_confidence_steps",
                "is_target_behavior",
            ],
            "run_level_required_fields": [
                "run_id",
                "model_profile",
                "confidence_profile",
                "confidence_template_name",
                "num_samples",
                "target_behavior_rate",
                "mean_chosen_token_prob_mean",
                "mean_entropy_mean",
                "high_confidence_fraction_mean",
                "entropy_collapse_score_mean",
            ],
        },
        "run_features": run_features,
    }


def write_sample_feature_jsonl(path: Path, sample_features: list[ConfidenceSampleFeature]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for feature in sample_features:
            handle.write(json.dumps(asdict(feature), ensure_ascii=True) + "\n")


def write_sample_feature_csv(path: Path, sample_features: list[ConfidenceSampleFeature]) -> None:
    fieldnames = [
        "schema_version",
        "feature_family",
        "feature_level",
        "run_id",
        "probe_id",
        "sample_id",
        "model_profile",
        "confidence_profile",
        "confidence_template_name",
        "prompt_template_name",
        "trigger_type",
        "target_type",
        "seed",
        "query_budget",
        "num_token_steps",
        "generated_length",
        "response_length",
        "top_k_capture_size",
        "mean_chosen_token_prob",
        "std_chosen_token_prob",
        "max_chosen_token_prob",
        "min_chosen_token_prob",
        "mean_entropy",
        "std_entropy",
        "max_entropy",
        "min_entropy",
        "high_confidence_fraction",
        "max_consecutive_high_confidence_steps",
        "mean_top1_confidence_run_length",
        "entropy_collapse_score",
        "early_prefix_confidence_mean",
        "late_prefix_confidence_mean",
        "confidence_slope",
        "entropy_slope",
        "is_target_behavior",
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


def extract_confidence_features(
    raw_results_path: Path,
    output_dir: Path,
    summary_json_path: Path | None = None,
    config_snapshot_path: Path | None = None,
    run_id: str | None = None,
    high_confidence_threshold: float = 0.10,
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
        high_confidence_threshold=high_confidence_threshold,
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
        high_confidence_threshold=high_confidence_threshold,
    )

    sample_jsonl_path = output_dir / "confidence_prompt_level_features.jsonl"
    feature_csv_path = output_dir / "confidence_features.csv"
    aggregated_json_path = output_dir / "confidence_features.json"
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
        "confidence_profile": run_features["confidence_profile"],
        "confidence_template_name": run_features["confidence_template_name"],
        "num_samples": run_features["num_samples"],
        "target_behavior_rate": run_features["target_behavior_rate"],
        "mean_chosen_token_prob_mean": run_features["mean_chosen_token_prob_mean"],
        "mean_entropy_mean": run_features["mean_entropy_mean"],
        "high_confidence_fraction_mean": run_features["high_confidence_fraction_mean"],
        "entropy_collapse_score_mean": run_features["entropy_collapse_score_mean"],
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
