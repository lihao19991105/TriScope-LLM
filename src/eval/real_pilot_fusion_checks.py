"""Acceptance and repeatability checks for real-pilot fusion readiness artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "cross_pilot_registry": {"relative_path": "cross_pilot_registry.json"},
    "cross_pilot_summary": {"relative_path": "cross_pilot_summary.json"},
    "pilot_coverage_summary": {"relative_path": "pilot_coverage_summary.json"},
    "real_pilot_fusion_dataset_jsonl": {"relative_path": "real_pilot_fusion_dataset.jsonl"},
    "real_pilot_fusion_dataset_csv": {"relative_path": "real_pilot_fusion_dataset.csv"},
    "real_pilot_alignment_summary": {"relative_path": "real_pilot_alignment_summary.json"},
    "real_pilot_fusion_readiness_summary": {"relative_path": "real_pilot_fusion_readiness_summary.json"},
    "build_log": {"relative_path": "build.log"},
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


def load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_real_pilot_fusion_readiness(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    checks: list[dict[str, Any]] = []
    missing: list[str] = []
    for artifact_name, artifact_spec in REQUIRED_ARTIFACTS.items():
        artifact_path = run_dir / artifact_spec["relative_path"]
        exists = artifact_path.is_file()
        checks.append({"artifact_name": artifact_name, "path": str(artifact_path), "exists": exists})
        if not exists:
            missing.append(artifact_name)

    if missing:
        return {
            "summary_status": "FAIL",
            "run_dir": str(run_dir),
            "missing_artifacts": missing,
            "artifact_checks": checks,
        }

    cross_pilot_summary = load_json(run_dir / "cross_pilot_summary.json")
    readiness_summary = load_json(run_dir / "real_pilot_fusion_readiness_summary.json")
    alignment_summary = load_json(run_dir / "real_pilot_alignment_summary.json")
    fusion_rows = load_jsonl(run_dir / "real_pilot_fusion_dataset.jsonl")
    fusion_csv_rows = load_csv_rows(run_dir / "real_pilot_fusion_dataset.csv")

    field_checks = {
        "cross_pilot_modules_3": cross_pilot_summary.get("num_real_pilot_modules") == 3,
        "coverage_complete_3of3": cross_pilot_summary.get("real_pilot_modules") == ["illumination", "reasoning", "confidence"],
        "full_intersection_available": readiness_summary.get("full_intersection_available") is True,
        "aligned_rows_non_empty": len(fusion_rows) > 0,
        "csv_rows_match_jsonl": len(fusion_rows) == len(fusion_csv_rows),
        "join_strategy_inner": readiness_summary.get("join_strategy_used") == "inner",
        "labels_not_available_recorded": readiness_summary.get("ground_truth_label_available") is False,
    }

    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "field_checks": field_checks,
        "snapshot": {
            "num_aligned_rows": readiness_summary.get("num_aligned_rows"),
            "num_rows_with_all_modalities": alignment_summary.get("num_rows_with_all_modalities"),
            "smoke_only_modules": cross_pilot_summary.get("smoke_only_modules"),
        },
    }


def compare_real_pilot_fusion_readiness(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_real_pilot_fusion_readiness(reference_run_dir)
    candidate = validate_real_pilot_fusion_readiness(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both real-pilot fusion readiness runs failed artifact acceptance.",
        }

    ref_summary = load_json(reference_run_dir.resolve() / "real_pilot_fusion_readiness_summary.json")
    cand_summary = load_json(candidate_run_dir.resolve() / "real_pilot_fusion_readiness_summary.json")
    ref_rows = load_jsonl(reference_run_dir.resolve() / "real_pilot_fusion_dataset.jsonl")
    cand_rows = load_jsonl(candidate_run_dir.resolve() / "real_pilot_fusion_dataset.jsonl")
    pairs = [
        ("num_aligned_rows", ref_summary.get("num_aligned_rows"), cand_summary.get("num_aligned_rows")),
        ("full_intersection_available", ref_summary.get("full_intersection_available"), cand_summary.get("full_intersection_available")),
        ("join_strategy_used", ref_summary.get("join_strategy_used"), cand_summary.get("join_strategy_used")),
        ("ground_truth_label_available", ref_summary.get("ground_truth_label_available"), cand_summary.get("ground_truth_label_available")),
        ("dataset_row_count", len(ref_rows), len(cand_rows)),
    ]
    comparisons = []
    all_match = True
    for field, reference_value, candidate_value in pairs:
        matches = reference_value == candidate_value
        comparisons.append(
            {"field": field, "reference_value": reference_value, "candidate_value": candidate_value, "matches": matches}
        )
        all_match = all_match and matches
    return {
        "summary_status": "PASS" if all_match else "FAIL",
        "reference_acceptance": reference,
        "candidate_acceptance": candidate,
        "comparisons": comparisons,
        "all_key_metrics_match": all_match,
    }
