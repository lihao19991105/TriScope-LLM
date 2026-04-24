"""Artifact acceptance and repeatability checks for real-pilot compact analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "real_pilot_analysis_summary": {
        "relative_path": "real_pilot_analysis_summary.json",
        "purpose": "Top-level compact analysis for the current real-pilot stack.",
    },
    "real_pilot_vs_smoke_summary": {
        "relative_path": "real_pilot_vs_smoke_summary.json",
        "purpose": "Compact comparison between smoke-level capabilities and current real-pilot capabilities.",
    },
    "real_pilot_vs_pilot_comparison": {
        "relative_path": "real_pilot_vs_pilot_comparison.csv",
        "purpose": "Module-level comparison across the current real pilots.",
    },
    "real_pilot_blocker_summary": {
        "relative_path": "real_pilot_blocker_summary.json",
        "purpose": "Structured blocker summary describing why supervised fusion is still blocked.",
    },
    "next_step_recommendation": {
        "relative_path": "next_step_recommendation.json",
        "purpose": "Structured next-step recommendation for the post-016 phase.",
    },
    "build_log": {
        "relative_path": "build.log",
        "purpose": "Human-readable log pointing to the generated real-pilot analysis artifacts.",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def validate_real_pilot_analysis(run_dir: Path) -> dict[str, Any]:
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

    analysis_summary = load_json(run_dir / REQUIRED_ARTIFACTS["real_pilot_analysis_summary"]["relative_path"])
    vs_smoke_summary = load_json(run_dir / REQUIRED_ARTIFACTS["real_pilot_vs_smoke_summary"]["relative_path"])
    blocker_summary = load_json(run_dir / REQUIRED_ARTIFACTS["real_pilot_blocker_summary"]["relative_path"])
    recommendation = load_json(run_dir / REQUIRED_ARTIFACTS["next_step_recommendation"]["relative_path"])
    comparison_rows = load_csv_rows(run_dir / REQUIRED_ARTIFACTS["real_pilot_vs_pilot_comparison"]["relative_path"])

    field_checks = {
        "analysis_status_pass": analysis_summary.get("summary_status") == "PASS",
        "vs_smoke_status_pass": vs_smoke_summary.get("summary_status") == "PASS",
        "blocker_status_pass": blocker_summary.get("summary_status") == "PASS",
        "recommendation_status_pass": recommendation.get("summary_status") == "PASS",
        "comparison_rows_non_empty": len(comparison_rows) > 0,
        "primary_blocker_matches": blocker_summary.get("primary_blocker") == "missing_ground_truth_labels",
        "recommended_route_matches": recommendation.get("recommended_route") == "first_labeled_pilot_bootstrap",
    }
    required_comparison_fields = {
        "module_name",
        "run_id",
        "dataset_profile",
        "model_profile",
        "feature_extraction_completed",
        "primary_signal",
    }
    field_checks["comparison_required_fields"] = required_comparison_fields.issubset(comparison_rows[0] if comparison_rows else {})
    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "artifact_paths": resolved_paths,
        "artifact_purposes": purposes,
        "field_checks": field_checks,
        "artifact_counts": {
            "comparison_rows": len(comparison_rows),
        },
        "analysis_snapshot": {
            "num_real_pilot_modules": analysis_summary.get("num_real_pilot_modules"),
            "full_intersection_available": analysis_summary.get("full_intersection_available"),
            "rule_baseline_status": analysis_summary.get("rule_baseline_status"),
            "logistic_skip_reason": analysis_summary.get("logistic_skip_reason"),
            "recommended_route": recommendation.get("recommended_route"),
        },
    }


def compare_real_pilot_analysis_runs(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_real_pilot_analysis(reference_run_dir)
    candidate = validate_real_pilot_analysis(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both real-pilot analysis runs failed acceptance, so repeatability comparison was skipped.",
        }

    reference_summary = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["real_pilot_analysis_summary"]["relative_path"])
    candidate_summary = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["real_pilot_analysis_summary"]["relative_path"])
    reference_blocker = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["real_pilot_blocker_summary"]["relative_path"])
    candidate_blocker = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["real_pilot_blocker_summary"]["relative_path"])
    reference_recommendation = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["next_step_recommendation"]["relative_path"])
    candidate_recommendation = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["next_step_recommendation"]["relative_path"])

    pairs = [
        ("num_real_pilot_modules", reference_summary.get("num_real_pilot_modules"), candidate_summary.get("num_real_pilot_modules")),
        ("num_aligned_rows", reference_summary.get("num_aligned_rows"), candidate_summary.get("num_aligned_rows")),
        ("rule_baseline_mean_prediction_score", reference_summary.get("rule_baseline_mean_prediction_score"), candidate_summary.get("rule_baseline_mean_prediction_score")),
        ("primary_blocker", reference_blocker.get("primary_blocker"), candidate_blocker.get("primary_blocker")),
        ("recommended_route", reference_recommendation.get("recommended_route"), candidate_recommendation.get("recommended_route")),
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
