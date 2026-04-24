"""Artifact acceptance and repeatability checks for fusion runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DATASET_REQUIRED_ARTIFACTS = {
    "fusion_dataset_jsonl": {
        "relative_path": "fusion_dataset.jsonl",
        "purpose": "Outer-join or inner-join merged fusion dataset with modality-prefixed feature fields.",
    },
    "fusion_dataset_csv": {
        "relative_path": "fusion_dataset.csv",
        "purpose": "CSV export of the merged fusion dataset for quick inspection and downstream tabular tools.",
    },
    "alignment_summary": {
        "relative_path": "alignment_summary.json",
        "purpose": "Summary of modality coverage and join behavior for the fusion dataset build.",
    },
    "config_snapshot": {
        "relative_path": "config_snapshot.json",
        "purpose": "Resolved fusion dataset build configuration and modality contracts.",
    },
    "build_log": {
        "relative_path": "build.log",
        "purpose": "Human-readable build log pointing to the generated fusion dataset artifacts.",
    },
}

BASELINE_REQUIRED_ARTIFACTS = {
    "preprocessed_jsonl": {
        "relative_path": "preprocessed_fusion_dataset.jsonl",
        "purpose": "Missingness-aware preprocessed fusion dataset used by the baseline models.",
    },
    "preprocessed_csv": {
        "relative_path": "preprocessed_fusion_dataset.csv",
        "purpose": "CSV export of the preprocessed fusion dataset.",
    },
    "preprocessing_metadata": {
        "relative_path": "preprocessing_metadata.json",
        "purpose": "Metadata describing label recovery, missingness rates, and selected feature columns.",
    },
    "rule_predictions": {
        "relative_path": "rule_predictions.jsonl",
        "purpose": "Rule-based baseline predictions using missingness-aware fusion inputs.",
    },
    "rule_summary": {
        "relative_path": "rule_summary.json",
        "purpose": "Compact summary of the rule-based baseline run.",
    },
    "logistic_predictions": {
        "relative_path": "logistic_predictions.jsonl",
        "purpose": "Logistic regression baseline predictions using preprocessed fusion features.",
    },
    "logistic_summary": {
        "relative_path": "logistic_summary.json",
        "purpose": "Compact summary of the logistic regression baseline run.",
    },
    "logistic_model_metadata": {
        "relative_path": "logistic_model_metadata.json",
        "purpose": "Model metadata, selected feature columns, and fitted coefficients for the logistic baseline.",
    },
    "fusion_summary": {
        "relative_path": "fusion_summary.json",
        "purpose": "Top-level summary of preprocessing, missingness, and prediction artifact generation.",
    },
    "config_snapshot": {
        "relative_path": "config_snapshot.json",
        "purpose": "Resolved configuration for the fusion baseline run.",
    },
    "run_log": {
        "relative_path": "run.log",
        "purpose": "Human-readable log pointing to the generated fusion baseline artifacts.",
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


def validate_artifact_group(run_dir: Path, required_artifacts: dict[str, dict[str, str]]) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, str], list[str]]:
    checks: list[dict[str, Any]] = []
    resolved_paths: dict[str, str] = {}
    purposes: dict[str, str] = {}
    missing: list[str] = []
    for artifact_name, artifact_spec in required_artifacts.items():
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
    return checks, resolved_paths, purposes, missing


def validate_fusion_artifacts(dataset_run_dir: Path, baseline_run_dir: Path) -> dict[str, Any]:
    dataset_run_dir = dataset_run_dir.resolve()
    baseline_run_dir = baseline_run_dir.resolve()
    dataset_checks, dataset_paths, dataset_purposes, dataset_missing = validate_artifact_group(
        dataset_run_dir, DATASET_REQUIRED_ARTIFACTS
    )
    baseline_checks, baseline_paths, baseline_purposes, baseline_missing = validate_artifact_group(
        baseline_run_dir, BASELINE_REQUIRED_ARTIFACTS
    )
    if dataset_missing or baseline_missing:
        return {
            "summary_status": "FAIL",
            "dataset_run_dir": str(dataset_run_dir),
            "baseline_run_dir": str(baseline_run_dir),
            "missing_artifacts": {
                "dataset": dataset_missing,
                "baseline": baseline_missing,
            },
            "dataset_artifact_checks": dataset_checks,
            "baseline_artifact_checks": baseline_checks,
            "dataset_artifact_paths": dataset_paths,
            "baseline_artifact_paths": baseline_paths,
            "dataset_artifact_purposes": dataset_purposes,
            "baseline_artifact_purposes": baseline_purposes,
        }

    dataset_rows = load_jsonl_rows(dataset_run_dir / DATASET_REQUIRED_ARTIFACTS["fusion_dataset_jsonl"]["relative_path"])
    preprocessed_rows = load_jsonl_rows(baseline_run_dir / BASELINE_REQUIRED_ARTIFACTS["preprocessed_jsonl"]["relative_path"])
    rule_rows = load_jsonl_rows(baseline_run_dir / BASELINE_REQUIRED_ARTIFACTS["rule_predictions"]["relative_path"])
    logistic_rows = load_jsonl_rows(
        baseline_run_dir / BASELINE_REQUIRED_ARTIFACTS["logistic_predictions"]["relative_path"]
    )
    alignment_summary = load_json(dataset_run_dir / DATASET_REQUIRED_ARTIFACTS["alignment_summary"]["relative_path"])
    fusion_summary = load_json(baseline_run_dir / BASELINE_REQUIRED_ARTIFACTS["fusion_summary"]["relative_path"])
    logistic_metadata = load_json(
        baseline_run_dir / BASELINE_REQUIRED_ARTIFACTS["logistic_model_metadata"]["relative_path"]
    )

    field_checks = {
        "fusion_dataset_non_empty": len(dataset_rows) > 0,
        "preprocessed_dataset_non_empty": len(preprocessed_rows) > 0,
        "rule_predictions_non_empty": len(rule_rows) > 0,
        "logistic_predictions_non_empty": len(logistic_rows) > 0,
        "alignment_summary_status_pass": alignment_summary.get("summary_status") == "PASS",
        "fusion_summary_status_pass": fusion_summary.get("summary_status") == "PASS",
        "logistic_metadata_status_pass": logistic_metadata.get("summary_status") == "PASS",
    }
    required_preprocessed_fields = {
        "sample_id",
        "ground_truth_label",
        "illumination_present",
        "illumination_missing",
        "reasoning_present",
        "reasoning_missing",
        "confidence_present",
        "confidence_missing",
        "modality_count",
    }
    required_prediction_fields = {
        "run_id",
        "sample_id",
        "fusion_profile",
        "prediction_score",
        "prediction_label",
        "label_threshold",
        "illumination_present",
        "reasoning_present",
        "confidence_present",
        "modality_count",
        "metadata",
    }
    required_summary_fields = {
        "num_rows",
        "missingness",
        "num_feature_columns",
        "rule_predictions_generated",
        "logistic_predictions_generated",
    }
    first_preprocessed = preprocessed_rows[0] if preprocessed_rows else {}
    first_rule = rule_rows[0] if rule_rows else {}
    first_logistic = logistic_rows[0] if logistic_rows else {}
    field_checks["preprocessed_required_fields"] = required_preprocessed_fields.issubset(first_preprocessed)
    field_checks["rule_prediction_required_fields"] = required_prediction_fields.issubset(first_rule)
    field_checks["logistic_prediction_required_fields"] = required_prediction_fields.issubset(first_logistic)
    field_checks["fusion_summary_required_fields"] = required_summary_fields.issubset(fusion_summary)

    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "dataset_run_dir": str(dataset_run_dir),
        "baseline_run_dir": str(baseline_run_dir),
        "dataset_artifact_checks": dataset_checks,
        "baseline_artifact_checks": baseline_checks,
        "dataset_artifact_paths": dataset_paths,
        "baseline_artifact_paths": baseline_paths,
        "dataset_artifact_purposes": dataset_purposes,
        "baseline_artifact_purposes": baseline_purposes,
        "field_checks": field_checks,
        "artifact_counts": {
            "fusion_dataset_rows": len(dataset_rows),
            "preprocessed_rows": len(preprocessed_rows),
            "rule_predictions": len(rule_rows),
            "logistic_predictions": len(logistic_rows),
        },
        "fusion_snapshot": {
            "join_mode": alignment_summary.get("join_mode"),
            "num_rows": alignment_summary.get("num_rows"),
            "num_rows_with_all_modalities": alignment_summary.get("num_rows_with_all_modalities"),
            "missingness": fusion_summary.get("missingness"),
            "num_feature_columns": fusion_summary.get("num_feature_columns"),
        },
    }


def compare_fusion_runs(
    reference_dataset_run_dir: Path,
    reference_baseline_run_dir: Path,
    candidate_dataset_run_dir: Path,
    candidate_baseline_run_dir: Path,
) -> dict[str, Any]:
    reference = validate_fusion_artifacts(reference_dataset_run_dir, reference_baseline_run_dir)
    candidate = validate_fusion_artifacts(candidate_dataset_run_dir, candidate_baseline_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both fusion runs failed artifact acceptance, so repeatability comparison was skipped.",
        }

    ref_align = load_json(reference_dataset_run_dir.resolve() / DATASET_REQUIRED_ARTIFACTS["alignment_summary"]["relative_path"])
    cand_align = load_json(candidate_dataset_run_dir.resolve() / DATASET_REQUIRED_ARTIFACTS["alignment_summary"]["relative_path"])
    ref_fusion_summary = load_json(reference_baseline_run_dir.resolve() / BASELINE_REQUIRED_ARTIFACTS["fusion_summary"]["relative_path"])
    cand_fusion_summary = load_json(candidate_baseline_run_dir.resolve() / BASELINE_REQUIRED_ARTIFACTS["fusion_summary"]["relative_path"])
    ref_logistic_summary = load_json(reference_baseline_run_dir.resolve() / BASELINE_REQUIRED_ARTIFACTS["logistic_summary"]["relative_path"])
    cand_logistic_summary = load_json(candidate_baseline_run_dir.resolve() / BASELINE_REQUIRED_ARTIFACTS["logistic_summary"]["relative_path"])

    pairs = [
        ("num_rows", ref_align.get("num_rows"), cand_align.get("num_rows")),
        (
            "num_rows_with_all_modalities",
            ref_align.get("num_rows_with_all_modalities"),
            cand_align.get("num_rows_with_all_modalities"),
        ),
        (
            "illumination_missing_rate",
            ref_fusion_summary.get("missingness", {}).get("illumination_missing_rate"),
            cand_fusion_summary.get("missingness", {}).get("illumination_missing_rate"),
        ),
        (
            "reasoning_missing_rate",
            ref_fusion_summary.get("missingness", {}).get("reasoning_missing_rate"),
            cand_fusion_summary.get("missingness", {}).get("reasoning_missing_rate"),
        ),
        (
            "confidence_missing_rate",
            ref_fusion_summary.get("missingness", {}).get("confidence_missing_rate"),
            cand_fusion_summary.get("missingness", {}).get("confidence_missing_rate"),
        ),
        (
            "num_feature_columns",
            ref_fusion_summary.get("num_feature_columns"),
            cand_fusion_summary.get("num_feature_columns"),
        ),
        (
            "logistic_mean_prediction_score",
            ref_logistic_summary.get("mean_prediction_score"),
            cand_logistic_summary.get("mean_prediction_score"),
        ),
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
