"""Artifact acceptance and repeatability checks for smoke reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "run_registry": {
        "relative_path": "run_registry.json",
        "purpose": "Registry of core smoke runs across illumination, reasoning, confidence, and fusion.",
    },
    "artifact_registry": {
        "relative_path": "artifact_registry.json",
        "purpose": "Registry of key smoke artifacts consumed by analysis and reporting.",
    },
    "smoke_report_summary": {
        "relative_path": "smoke_report_summary.json",
        "purpose": "Compact top-level summary of module statuses, fusion state, and baseline outputs.",
    },
    "baseline_comparison": {
        "relative_path": "baseline_comparison.csv",
        "purpose": "Compact comparison of the current fusion baselines.",
    },
    "modality_coverage_summary": {
        "relative_path": "modality_coverage_summary.json",
        "purpose": "Summary of modality overlap and missingness in the current smoke fusion dataset.",
    },
    "error_analysis_dataset": {
        "relative_path": "error_analysis_dataset.jsonl",
        "purpose": "Error-analysis-ready merged artifact aligned by sample_id.",
    },
    "error_analysis_dataset_csv": {
        "relative_path": "error_analysis_dataset.csv",
        "purpose": "CSV export of the error-analysis-ready merged artifact.",
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


def validate_smoke_report(run_dir: Path) -> dict[str, Any]:
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

    run_registry = load_json(run_dir / REQUIRED_ARTIFACTS["run_registry"]["relative_path"])
    artifact_registry = load_json(run_dir / REQUIRED_ARTIFACTS["artifact_registry"]["relative_path"])
    smoke_summary = load_json(run_dir / REQUIRED_ARTIFACTS["smoke_report_summary"]["relative_path"])
    modality_coverage = load_json(run_dir / REQUIRED_ARTIFACTS["modality_coverage_summary"]["relative_path"])
    error_rows = load_jsonl_rows(run_dir / REQUIRED_ARTIFACTS["error_analysis_dataset"]["relative_path"])

    field_checks = {
        "run_registry_non_empty": isinstance(run_registry.get("runs"), list) and len(run_registry["runs"]) > 0,
        "artifact_registry_non_empty": isinstance(artifact_registry.get("artifacts"), list)
        and len(artifact_registry["artifacts"]) > 0,
        "smoke_summary_status_pass": smoke_summary.get("summary_status") == "PASS",
        "coverage_summary_status_pass": modality_coverage.get("summary_status") == "PASS",
        "error_analysis_non_empty": len(error_rows) > 0,
    }
    required_error_fields = {
        "sample_id",
        "ground_truth_label",
        "illumination_present",
        "reasoning_present",
        "confidence_present",
        "rule_prediction_score",
        "logistic_prediction_score",
    }
    first_row = error_rows[0] if error_rows else {}
    field_checks["error_analysis_required_fields"] = required_error_fields.issubset(first_row)

    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "artifact_paths": resolved_paths,
        "artifact_purposes": purposes,
        "field_checks": field_checks,
        "artifact_counts": {
            "registered_runs": len(run_registry.get("runs", [])),
            "registered_artifacts": len(artifact_registry.get("artifacts", [])),
            "error_analysis_rows": len(error_rows),
        },
        "report_snapshot": {
            "num_registered_runs": smoke_summary.get("num_registered_runs"),
            "num_registered_artifacts": smoke_summary.get("num_registered_artifacts"),
            "all_artifacts_present": smoke_summary.get("all_artifacts_present"),
            "num_rows_with_all_modalities": modality_coverage.get("num_rows_with_all_modalities"),
        },
    }


def compare_smoke_reports(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_smoke_report(reference_run_dir)
    candidate = validate_smoke_report(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both smoke reports failed artifact acceptance, so repeatability comparison was skipped.",
        }

    reference_summary = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["smoke_report_summary"]["relative_path"])
    candidate_summary = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["smoke_report_summary"]["relative_path"])
    reference_coverage = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["modality_coverage_summary"]["relative_path"])
    candidate_coverage = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["modality_coverage_summary"]["relative_path"])

    pairs = [
        ("num_registered_runs", reference_summary.get("num_registered_runs"), candidate_summary.get("num_registered_runs")),
        ("num_registered_artifacts", reference_summary.get("num_registered_artifacts"), candidate_summary.get("num_registered_artifacts")),
        ("fusion_num_rows", reference_summary.get("fusion_snapshot", {}).get("num_rows"), candidate_summary.get("fusion_snapshot", {}).get("num_rows")),
        ("rule_mean_prediction_score", reference_summary.get("baseline_snapshot", {}).get("rule_mean_prediction_score"), candidate_summary.get("baseline_snapshot", {}).get("rule_mean_prediction_score")),
        ("logistic_mean_prediction_score", reference_summary.get("baseline_snapshot", {}).get("logistic_mean_prediction_score"), candidate_summary.get("baseline_snapshot", {}).get("logistic_mean_prediction_score")),
        ("num_rows_with_all_modalities", reference_coverage.get("num_rows_with_all_modalities"), candidate_coverage.get("num_rows_with_all_modalities")),
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
