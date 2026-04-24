"""Artifact acceptance and repeatability checks for the labeled pilot bootstrap."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "labeled_pilot_dataset": {
        "relative_path": "labeled_pilot_dataset.jsonl",
        "purpose": "Sample-level labeled pilot dataset for the first supervised pilot path.",
    },
    "labeled_pilot_summary": {
        "relative_path": "labeled_pilot_summary.json",
        "purpose": "Compact summary of the labeled pilot execution and extracted features.",
    },
    "labeled_supervised_readiness_summary": {
        "relative_path": "labeled_supervised_readiness_summary.json",
        "purpose": "Structured summary of whether the labeled supervised path is ready.",
    },
    "labeled_logistic_summary": {
        "relative_path": "labeled_logistic_summary.json",
        "purpose": "Summary of the minimal supervised baseline on the labeled pilot dataset.",
    },
    "probe_raw_results": {
        "relative_path": "illumination_probe/raw_results.jsonl",
        "purpose": "Raw illumination probe outputs for the labeled pilot bootstrap.",
    },
    "probe_feature_summary": {
        "relative_path": "illumination_probe/features/feature_summary.json",
        "purpose": "Illumination feature summary for the labeled pilot bootstrap.",
    },
    "pilot_execution_log": {
        "relative_path": "pilot_execution.log",
        "purpose": "Human-readable execution log for the labeled pilot bootstrap.",
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


def validate_labeled_pilot(run_dir: Path) -> dict[str, Any]:
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

    dataset_rows = load_jsonl_rows(run_dir / REQUIRED_ARTIFACTS["labeled_pilot_dataset"]["relative_path"])
    summary = load_json(run_dir / REQUIRED_ARTIFACTS["labeled_pilot_summary"]["relative_path"])
    readiness = load_json(run_dir / REQUIRED_ARTIFACTS["labeled_supervised_readiness_summary"]["relative_path"])
    logistic_summary = load_json(run_dir / REQUIRED_ARTIFACTS["labeled_logistic_summary"]["relative_path"])
    feature_summary = load_json(run_dir / REQUIRED_ARTIFACTS["probe_feature_summary"]["relative_path"])

    labels = [int(row["ground_truth_label"]) for row in dataset_rows]
    field_checks = {
        "dataset_non_empty": len(dataset_rows) > 0,
        "summary_status_pass": summary.get("summary_status") == "PASS",
        "readiness_status_pass": readiness.get("summary_status") == "PASS",
        "feature_summary_status_pass": feature_summary.get("summary_status") == "PASS",
        "contains_both_classes": 0 in labels and 1 in labels,
        "supervised_path_exists": readiness.get("supervised_path_exists") is True,
        "logistic_path_exists": logistic_summary.get("summary_status") == "PASS",
    }
    required_dataset_fields = {
        "sample_id",
        "base_sample_id",
        "label_name",
        "ground_truth_label",
        "contract_variant",
        "feature_vector",
    }
    field_checks["dataset_required_fields"] = required_dataset_fields.issubset(dataset_rows[0] if dataset_rows else {})
    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "artifact_paths": resolved_paths,
        "artifact_purposes": purposes,
        "field_checks": field_checks,
        "artifact_counts": {
            "dataset_rows": len(dataset_rows),
        },
        "labeled_snapshot": {
            "num_rows": summary.get("num_rows"),
            "class_balance": summary.get("class_balance"),
            "logistic_ready": readiness.get("logistic_ready"),
            "mean_prediction_score": logistic_summary.get("mean_prediction_score"),
        },
    }


def compare_labeled_pilot_runs(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_labeled_pilot(reference_run_dir)
    candidate = validate_labeled_pilot(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both labeled pilot runs failed acceptance, so repeatability comparison was skipped.",
        }

    reference_summary = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["labeled_pilot_summary"]["relative_path"])
    candidate_summary = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["labeled_pilot_summary"]["relative_path"])
    reference_logistic = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["labeled_logistic_summary"]["relative_path"])
    candidate_logistic = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["labeled_logistic_summary"]["relative_path"])

    pairs = [
        ("num_rows", reference_summary.get("num_rows"), candidate_summary.get("num_rows")),
        ("class_balance", reference_summary.get("class_balance"), candidate_summary.get("class_balance")),
        ("target_behavior_rate", reference_summary.get("target_behavior_rate"), candidate_summary.get("target_behavior_rate")),
        ("mean_response_length", reference_summary.get("mean_response_length"), candidate_summary.get("mean_response_length")),
        ("mean_prediction_score", reference_logistic.get("mean_prediction_score"), candidate_logistic.get("mean_prediction_score")),
    ]
    comparisons = []
    all_match = True
    for field, reference_value, candidate_value in pairs:
        matches = reference_value == candidate_value
        all_match = all_match and matches
        comparisons.append(
            {
                "field": field,
                "reference_value": reference_value,
                "candidate_value": candidate_value,
                "matches": matches,
            }
        )
    return {
        "summary_status": "PASS" if all_match else "FAIL",
        "reference_acceptance": reference,
        "candidate_acceptance": candidate,
        "comparisons": comparisons,
        "all_key_metrics_match": all_match,
    }
