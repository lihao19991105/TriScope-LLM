"""Artifact acceptance and repeatability checks for reasoning runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "raw_results": {
        "relative_path": "raw_results.jsonl",
        "purpose": "Original sample-level reasoning probe results with answer/reasoning/answer triples.",
    },
    "config_snapshot": {
        "relative_path": "config_snapshot.json",
        "purpose": "Resolved model, reasoning, and runtime configuration used by the reasoning run.",
    },
    "summary": {
        "relative_path": "summary.json",
        "purpose": "Minimal reasoning summary with answer-change and target-behavior counts.",
    },
    "sample_level_features": {
        "relative_path": "features/reasoning_prompt_level_features.jsonl",
        "purpose": "Sample-level machine-readable reasoning feature rows for downstream fusion alignment.",
    },
    "aggregated_features": {
        "relative_path": "features/reasoning_features.json",
        "purpose": "Run-level aggregated reasoning feature payload for fusion and analysis.",
    },
    "feature_summary": {
        "relative_path": "features/feature_summary.json",
        "purpose": "Compact summary of extracted reasoning features for smoke checks and README references.",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
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


def validate_reasoning_run_artifacts(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    checks: list[dict[str, Any]] = []
    resolved_paths: dict[str, str] = {}
    purposes: dict[str, str] = {}
    missing: list[str] = []

    for artifact_name, artifact_spec in REQUIRED_ARTIFACTS.items():
        artifact_path = run_dir / artifact_spec["relative_path"]
        exists = artifact_path.is_file()
        resolved_paths[artifact_name] = str(artifact_path)
        purposes[artifact_name] = artifact_spec["purpose"]
        checks.append(
            {
                "artifact_name": artifact_name,
                "path": str(artifact_path),
                "exists": exists,
                "purpose": artifact_spec["purpose"],
            }
        )
        if not exists:
            missing.append(artifact_name)

    if missing:
        return {
            "summary_status": "FAIL",
            "run_dir": str(run_dir),
            "missing_artifacts": missing,
            "artifact_checks": checks,
            "artifact_paths": resolved_paths,
            "artifact_purposes": purposes,
        }

    raw_rows = load_jsonl_rows(run_dir / REQUIRED_ARTIFACTS["raw_results"]["relative_path"])
    sample_feature_rows = load_jsonl_rows(
        run_dir / REQUIRED_ARTIFACTS["sample_level_features"]["relative_path"]
    )
    summary_payload = load_json(run_dir / REQUIRED_ARTIFACTS["summary"]["relative_path"])
    feature_summary_payload = load_json(run_dir / REQUIRED_ARTIFACTS["feature_summary"]["relative_path"])
    aggregated_payload = load_json(run_dir / REQUIRED_ARTIFACTS["aggregated_features"]["relative_path"])
    config_snapshot = load_json(run_dir / REQUIRED_ARTIFACTS["config_snapshot"]["relative_path"])

    field_checks = {
        "raw_results_non_empty": len(raw_rows) > 0,
        "summary_status_pass": summary_payload.get("summary_status") == "PASS",
        "feature_summary_status_pass": feature_summary_payload.get("summary_status") == "PASS",
        "sample_features_non_empty": len(sample_feature_rows) > 0,
        "aggregated_has_run_features": isinstance(aggregated_payload.get("run_features"), dict),
        "config_snapshot_has_model_profile": isinstance(config_snapshot.get("model_profile"), dict),
    }
    required_sample_fields = {"run_id", "probe_id", "sample_id", "reasoning_length", "target_behavior_flip_flag"}
    required_run_fields = {
        "num_samples",
        "answer_changed_rate",
        "target_behavior_flip_rate",
        "reasoning_length_mean",
    }
    first_sample = sample_feature_rows[0] if sample_feature_rows else {}
    run_features = aggregated_payload.get("run_features", {})
    field_checks["sample_feature_required_fields"] = required_sample_fields.issubset(first_sample)
    field_checks["aggregated_required_fields"] = required_run_fields.issubset(run_features)

    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "artifact_paths": resolved_paths,
        "artifact_purposes": purposes,
        "field_checks": field_checks,
        "artifact_counts": {
            "raw_results": len(raw_rows),
            "sample_level_features": len(sample_feature_rows),
        },
        "run_feature_snapshot": {
            "run_id": run_features.get("run_id"),
            "model_profile": run_features.get("model_profile"),
            "reasoning_profile": run_features.get("reasoning_profile"),
            "num_samples": run_features.get("num_samples"),
            "answer_changed_rate": run_features.get("answer_changed_rate"),
            "target_behavior_flip_rate": run_features.get("target_behavior_flip_rate"),
            "reasoning_length_mean": run_features.get("reasoning_length_mean"),
        },
    }


def compare_reasoning_runs(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_reasoning_run_artifacts(reference_run_dir)
    candidate = validate_reasoning_run_artifacts(candidate_run_dir)

    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_run_dir": str(reference_run_dir.resolve()),
            "candidate_run_dir": str(candidate_run_dir.resolve()),
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both runs failed artifact acceptance, so repeatability comparison was skipped.",
        }

    reference_summary = load_json(
        reference_run_dir.resolve() / REQUIRED_ARTIFACTS["feature_summary"]["relative_path"]
    )
    candidate_summary = load_json(
        candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["feature_summary"]["relative_path"]
    )

    keys = [
        "num_samples",
        "answer_changed_rate",
        "target_behavior_flip_rate",
        "reasoning_length_mean",
    ]
    comparisons = []
    all_match = True
    for key in keys:
        reference_value = reference_summary.get(key)
        candidate_value = candidate_summary.get(key)
        matches = reference_value == candidate_value
        all_match = all_match and matches
        comparisons.append(
            {
                "field": key,
                "reference_value": reference_value,
                "candidate_value": candidate_value,
                "matches": matches,
            }
        )

    return {
        "summary_status": (
            "PASS"
            if reference["summary_status"] == "PASS"
            and candidate["summary_status"] == "PASS"
            and all_match
            else "FAIL"
        ),
        "reference_run_dir": str(reference_run_dir.resolve()),
        "candidate_run_dir": str(candidate_run_dir.resolve()),
        "reference_acceptance": reference,
        "candidate_acceptance": candidate,
        "comparisons": comparisons,
        "all_key_metrics_match": all_match,
    }
