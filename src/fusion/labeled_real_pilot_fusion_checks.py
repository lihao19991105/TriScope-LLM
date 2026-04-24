"""Acceptance and repeatability checks for labeled real-pilot fusion bootstrap."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_DATASET_ARTIFACTS = {
    "dataset": "labeled_real_pilot_fusion_dataset.jsonl",
    "summary": "labeled_real_pilot_fusion_summary.json",
    "label_definition": "labeled_real_pilot_label_definition.json",
    "config_snapshot": "config_snapshot.json",
    "build_log": "build.log",
}

REQUIRED_RUN_ARTIFACTS = {
    "predictions": "labeled_real_pilot_logistic_predictions.jsonl",
    "summary": "labeled_real_pilot_logistic_summary.json",
    "model_metadata": "labeled_real_pilot_model_metadata.json",
    "run_summary": "labeled_real_pilot_fusion_run_summary.json",
    "config_snapshot": "config_snapshot.json",
    "run_log": "run.log",
}


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


def _check_required(run_dir: Path, required: dict[str, str]) -> tuple[list[dict[str, Any]], list[str]]:
    checks: list[dict[str, Any]] = []
    missing: list[str] = []
    for artifact_name, relative_path in required.items():
        artifact_path = run_dir / relative_path
        exists = artifact_path.is_file()
        checks.append({"artifact_name": artifact_name, "path": str(artifact_path), "exists": exists})
        if not exists:
            missing.append(artifact_name)
    return checks, missing


def validate_labeled_real_pilot_fusion(dataset_dir: Path, run_dir: Path) -> dict[str, Any]:
    dataset_dir = dataset_dir.resolve()
    run_dir = run_dir.resolve()
    dataset_checks, dataset_missing = _check_required(dataset_dir, REQUIRED_DATASET_ARTIFACTS)
    run_checks, run_missing = _check_required(run_dir, REQUIRED_RUN_ARTIFACTS)
    if dataset_missing or run_missing:
        return {
            "summary_status": "FAIL",
            "dataset_dir": str(dataset_dir),
            "run_dir": str(run_dir),
            "missing_dataset_artifacts": dataset_missing,
            "missing_run_artifacts": run_missing,
            "dataset_checks": dataset_checks,
            "run_checks": run_checks,
        }

    dataset_rows = load_jsonl(dataset_dir / REQUIRED_DATASET_ARTIFACTS["dataset"])
    dataset_summary = load_json(dataset_dir / REQUIRED_DATASET_ARTIFACTS["summary"])
    logistic_summary = load_json(run_dir / REQUIRED_RUN_ARTIFACTS["summary"])
    prediction_rows = load_jsonl(run_dir / REQUIRED_RUN_ARTIFACTS["predictions"])
    field_checks = {
        "dataset_non_empty": len(dataset_rows) > 0,
        "dataset_summary_pass": dataset_summary.get("summary_status") == "PASS",
        "logistic_summary_pass": logistic_summary.get("summary_status") == "PASS",
        "predictions_non_empty": len(prediction_rows) > 0,
        "contains_two_classes": len({int(row["ground_truth_label"]) for row in dataset_rows}) >= 2,
    }
    required_dataset_fields = {"sample_id", "base_sample_id", "contract_variant", "ground_truth_label", "label_name"}
    required_prediction_fields = {"sample_id", "base_sample_id", "contract_variant", "prediction_score", "prediction_label", "ground_truth_label"}
    field_checks["dataset_required_fields"] = required_dataset_fields.issubset(dataset_rows[0] if dataset_rows else {})
    field_checks["prediction_required_fields"] = required_prediction_fields.issubset(prediction_rows[0] if prediction_rows else {})
    return {
        "summary_status": "PASS" if all(field_checks.values()) else "FAIL",
        "dataset_dir": str(dataset_dir),
        "run_dir": str(run_dir),
        "dataset_checks": dataset_checks,
        "run_checks": run_checks,
        "field_checks": field_checks,
        "snapshot": {
            "num_dataset_rows": len(dataset_rows),
            "num_predictions": len(prediction_rows),
            "mean_prediction_score": logistic_summary.get("mean_prediction_score"),
        },
    }


def compare_labeled_real_pilot_fusion(
    reference_dataset_dir: Path,
    reference_run_dir: Path,
    candidate_dataset_dir: Path,
    candidate_run_dir: Path,
) -> dict[str, Any]:
    reference = validate_labeled_real_pilot_fusion(reference_dataset_dir, reference_run_dir)
    candidate = validate_labeled_real_pilot_fusion(candidate_dataset_dir, candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both labeled real-pilot fusion runs failed acceptance.",
        }

    ref_dataset_summary = load_json(reference_dataset_dir.resolve() / REQUIRED_DATASET_ARTIFACTS["summary"])
    cand_dataset_summary = load_json(candidate_dataset_dir.resolve() / REQUIRED_DATASET_ARTIFACTS["summary"])
    ref_run_summary = load_json(reference_run_dir.resolve() / REQUIRED_RUN_ARTIFACTS["summary"])
    cand_run_summary = load_json(candidate_run_dir.resolve() / REQUIRED_RUN_ARTIFACTS["summary"])
    pairs = [
        ("num_rows", ref_dataset_summary.get("num_rows"), cand_dataset_summary.get("num_rows")),
        ("class_balance", ref_dataset_summary.get("label_coverage", {}).get("class_balance"), cand_dataset_summary.get("label_coverage", {}).get("class_balance")),
        ("num_predictions", ref_run_summary.get("num_predictions"), cand_run_summary.get("num_predictions")),
        ("mean_prediction_score", ref_run_summary.get("mean_prediction_score"), cand_run_summary.get("mean_prediction_score")),
    ]
    comparisons = []
    all_match = True
    for field, reference_value, candidate_value in pairs:
        matches = reference_value == candidate_value
        comparisons.append({"field": field, "reference_value": reference_value, "candidate_value": candidate_value, "matches": matches})
        all_match = all_match and matches
    return {
        "summary_status": "PASS" if all_match else "FAIL",
        "reference_acceptance": reference,
        "candidate_acceptance": candidate,
        "comparisons": comparisons,
        "all_key_metrics_match": all_match,
    }
