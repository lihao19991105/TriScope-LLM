"""Acceptance and repeatability checks for labeled-pilot analysis artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "labeled_pilot_analysis_summary": "labeled_pilot_analysis_summary.json",
    "labeled_vs_real_pilot_alignment_summary": "labeled_vs_real_pilot_alignment_summary.json",
    "labeled_fusion_blocker_summary": "labeled_fusion_blocker_summary.json",
    "labeled_vs_fusion_comparison": "labeled_vs_fusion_comparison.csv",
    "fusion_integration_recommendation": "fusion_integration_recommendation.json",
    "build_log": "build.log",
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


def validate_labeled_pilot_analysis(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    checks: list[dict[str, Any]] = []
    missing: list[str] = []
    for artifact_name, relative_path in REQUIRED_ARTIFACTS.items():
        artifact_path = run_dir / relative_path
        exists = artifact_path.is_file()
        checks.append({"artifact_name": artifact_name, "path": str(artifact_path), "exists": exists})
        if not exists:
            missing.append(artifact_name)

    if missing:
        return {"summary_status": "FAIL", "run_dir": str(run_dir), "missing_artifacts": missing, "artifact_checks": checks}

    analysis_summary = load_json(run_dir / REQUIRED_ARTIFACTS["labeled_pilot_analysis_summary"])
    alignment_summary = load_json(run_dir / REQUIRED_ARTIFACTS["labeled_vs_real_pilot_alignment_summary"])
    blocker_summary = load_json(run_dir / REQUIRED_ARTIFACTS["labeled_fusion_blocker_summary"])
    recommendation = load_json(run_dir / REQUIRED_ARTIFACTS["fusion_integration_recommendation"])
    comparison_rows = load_csv_rows(run_dir / REQUIRED_ARTIFACTS["labeled_vs_fusion_comparison"])
    field_checks = {
        "analysis_status_pass": analysis_summary.get("summary_status") == "PASS",
        "alignment_status_pass": alignment_summary.get("summary_status") == "PASS",
        "blocker_status_pass": blocker_summary.get("summary_status") == "PASS",
        "recommendation_status_pass": recommendation.get("summary_status") == "PASS",
        "comparison_rows_non_empty": len(comparison_rows) > 0,
        "recommended_route_matches": recommendation.get("recommended_route") == "map_controlled_label_back_to_real_pilot_fusion",
        "natural_alignment_available": alignment_summary.get("natural_alignment_available") is True,
    }
    required_fields = {"labeled_sample_id", "base_sample_id", "contract_variant", "ground_truth_label", "mapped_alignment_key"}
    field_checks["comparison_required_fields"] = required_fields.issubset(comparison_rows[0] if comparison_rows else {})
    return {
        "summary_status": "PASS" if all(field_checks.values()) else "FAIL",
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "field_checks": field_checks,
        "snapshot": {
            "num_labeled_rows": analysis_summary.get("num_labeled_rows"),
            "num_naturally_aligned_base_ids": alignment_summary.get("num_naturally_aligned_base_ids"),
            "recommended_route": recommendation.get("recommended_route"),
        },
    }


def compare_labeled_pilot_analysis(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_labeled_pilot_analysis(reference_run_dir)
    candidate = validate_labeled_pilot_analysis(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both labeled-pilot analysis runs failed acceptance.",
        }

    ref_summary = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["labeled_pilot_analysis_summary"])
    cand_summary = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["labeled_pilot_analysis_summary"])
    ref_alignment = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["labeled_vs_real_pilot_alignment_summary"])
    cand_alignment = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["labeled_vs_real_pilot_alignment_summary"])
    ref_recommendation = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["fusion_integration_recommendation"])
    cand_recommendation = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["fusion_integration_recommendation"])

    pairs = [
        ("num_labeled_rows", ref_summary.get("num_labeled_rows"), cand_summary.get("num_labeled_rows")),
        ("num_naturally_aligned_base_ids", ref_alignment.get("num_naturally_aligned_base_ids"), cand_alignment.get("num_naturally_aligned_base_ids")),
        ("recommended_route", ref_recommendation.get("recommended_route"), cand_recommendation.get("recommended_route")),
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
