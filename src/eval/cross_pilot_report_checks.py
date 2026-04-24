"""Acceptance and repeatability checks for cross-pilot reporting artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "cross_pilot_registry": {
        "relative_path": "cross_pilot_registry.json",
        "purpose": "Registry of the currently materialized real pilot runs.",
    },
    "cross_pilot_artifact_registry": {
        "relative_path": "cross_pilot_artifact_registry.json",
        "purpose": "Registry of key upstream artifacts consumed by the cross-pilot report.",
    },
    "cross_pilot_summary": {
        "relative_path": "cross_pilot_summary.json",
        "purpose": "Top-level compact summary of current real pilot coverage.",
    },
    "pilot_comparison_csv": {
        "relative_path": "pilot_comparison.csv",
        "purpose": "Compact reasoning-vs-confidence comparison table.",
    },
    "pilot_coverage_summary": {
        "relative_path": "pilot_coverage_summary.json",
        "purpose": "Coverage summary describing real pilot modules and remaining gaps.",
    },
    "real_pilot_vs_smoke_summary": {
        "relative_path": "real_pilot_vs_smoke_summary.json",
        "purpose": "Compact overview of real pilot coverage relative to the smoke layer.",
    },
    "build_log": {
        "relative_path": "build.log",
        "purpose": "Human-readable log for the cross-pilot report build.",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_cross_pilot_report(run_dir: Path) -> dict[str, Any]:
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

    registry = load_json(run_dir / REQUIRED_ARTIFACTS["cross_pilot_registry"]["relative_path"])
    summary = load_json(run_dir / REQUIRED_ARTIFACTS["cross_pilot_summary"]["relative_path"])
    coverage = load_json(run_dir / REQUIRED_ARTIFACTS["pilot_coverage_summary"]["relative_path"])
    real_vs_smoke = load_json(run_dir / REQUIRED_ARTIFACTS["real_pilot_vs_smoke_summary"]["relative_path"])
    comparison_rows = load_csv_rows(run_dir / REQUIRED_ARTIFACTS["pilot_comparison_csv"]["relative_path"])

    pilot_runs = registry.get("pilot_runs", [])
    modules = [row.get("module_name") for row in pilot_runs if isinstance(row, dict)]
    field_checks = {
        "registry_has_two_pilots": isinstance(pilot_runs, list) and len(pilot_runs) >= 2,
        "registry_contains_reasoning": "reasoning" in modules,
        "registry_contains_confidence": "confidence" in modules,
        "comparison_rows_non_empty": len(comparison_rows) >= 2,
        "summary_status_pass": summary.get("summary_status") == "PASS",
        "coverage_status_pass": coverage.get("summary_status") == "PASS",
        "real_vs_smoke_status_pass": real_vs_smoke.get("summary_status") == "PASS",
        "illumination_gap_recorded": "illumination" in coverage.get("coverage_gap", []),
    }

    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "artifact_paths": resolved_paths,
        "artifact_purposes": purposes,
        "field_checks": field_checks,
        "report_snapshot": {
            "real_pilot_modules": summary.get("real_pilot_modules"),
            "smoke_only_modules": summary.get("smoke_only_modules"),
            "num_comparison_rows": len(comparison_rows),
        },
    }


def compare_cross_pilot_reports(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_cross_pilot_report(reference_run_dir)
    candidate = validate_cross_pilot_report(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both cross-pilot report runs failed artifact acceptance, so repeatability comparison was skipped.",
        }

    ref_summary = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["cross_pilot_summary"]["relative_path"])
    cand_summary = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["cross_pilot_summary"]["relative_path"])
    ref_coverage = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["pilot_coverage_summary"]["relative_path"])
    cand_coverage = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["pilot_coverage_summary"]["relative_path"])
    ref_comparison_rows = load_csv_rows(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["pilot_comparison_csv"]["relative_path"])
    cand_comparison_rows = load_csv_rows(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["pilot_comparison_csv"]["relative_path"])

    pairs = [
        ("num_real_pilot_runs", ref_summary.get("num_real_pilot_runs"), cand_summary.get("num_real_pilot_runs")),
        ("real_pilot_modules", ref_summary.get("real_pilot_modules"), cand_summary.get("real_pilot_modules")),
        ("smoke_only_modules", ref_summary.get("smoke_only_modules"), cand_summary.get("smoke_only_modules")),
        ("coverage_gap", ref_coverage.get("coverage_gap"), cand_coverage.get("coverage_gap")),
        ("num_comparison_rows", len(ref_comparison_rows), len(cand_comparison_rows)),
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
