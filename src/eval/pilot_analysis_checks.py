"""Artifact acceptance and repeatability checks for pilot analysis artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "pilot_run_registry": {
        "relative_path": "pilot_run_registry.json",
        "purpose": "Registry of real pilot runs currently registered in the analysis layer.",
    },
    "pilot_vs_smoke_summary": {
        "relative_path": "pilot_vs_smoke_summary.json",
        "purpose": "Compact comparison between the current pilot run and the matching smoke baseline.",
    },
    "pilot_analysis_summary": {
        "relative_path": "pilot_analysis_summary.json",
        "purpose": "Top-level pilot analysis summary describing real-vs-smoke coverage and current limits.",
    },
    "build_log": {
        "relative_path": "build.log",
        "purpose": "Human-readable log pointing to the generated pilot analysis artifacts.",
    },
}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_pilot_analysis(run_dir: Path) -> dict[str, Any]:
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

    pilot_registry = load_json(run_dir / REQUIRED_ARTIFACTS["pilot_run_registry"]["relative_path"])
    pilot_vs_smoke = load_json(run_dir / REQUIRED_ARTIFACTS["pilot_vs_smoke_summary"]["relative_path"])
    analysis_summary = load_json(run_dir / REQUIRED_ARTIFACTS["pilot_analysis_summary"]["relative_path"])

    field_checks = {
        "pilot_registry_non_empty": isinstance(pilot_registry.get("pilot_runs"), list)
        and len(pilot_registry["pilot_runs"]) > 0,
        "pilot_vs_smoke_has_comparisons": isinstance(pilot_vs_smoke.get("comparisons"), list)
        and len(pilot_vs_smoke["comparisons"]) > 0,
        "analysis_summary_status_pass": analysis_summary.get("summary_status") == "PASS",
    }
    required_registry_fields = {
        "run_id",
        "experiment_profile",
        "dataset_profile",
        "model_profile",
        "module_set",
    }
    required_comparison_fields = {"metric", "pilot_value", "smoke_value"}
    first_registry = pilot_registry.get("pilot_runs", [{}])[0] if pilot_registry.get("pilot_runs") else {}
    first_comparison = pilot_vs_smoke.get("comparisons", [{}])[0] if pilot_vs_smoke.get("comparisons") else {}
    field_checks["pilot_registry_required_fields"] = required_registry_fields.issubset(first_registry)
    field_checks["pilot_vs_smoke_required_fields"] = required_comparison_fields.issubset(first_comparison)

    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "artifact_paths": resolved_paths,
        "artifact_purposes": purposes,
        "field_checks": field_checks,
        "analysis_snapshot": {
            "pilot_run_id": analysis_summary.get("pilot_run_id"),
            "pilot_model_profile": analysis_summary.get("pilot_model_profile"),
            "comparison_scope": pilot_vs_smoke.get("comparison_scope"),
            "num_comparisons": len(pilot_vs_smoke.get("comparisons", [])),
        },
    }


def compare_pilot_analysis_runs(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_pilot_analysis(reference_run_dir)
    candidate = validate_pilot_analysis(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both pilot analysis runs failed artifact acceptance, so repeatability comparison was skipped.",
        }

    ref_vs_smoke = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["pilot_vs_smoke_summary"]["relative_path"])
    cand_vs_smoke = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["pilot_vs_smoke_summary"]["relative_path"])
    ref_summary = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["pilot_analysis_summary"]["relative_path"])
    cand_summary = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["pilot_analysis_summary"]["relative_path"])

    pairs = [
        ("pilot_run_id", ref_summary.get("pilot_run_id"), cand_summary.get("pilot_run_id")),
        ("pilot_model_profile", ref_summary.get("pilot_model_profile"), cand_summary.get("pilot_model_profile")),
        ("comparison_scope", ref_vs_smoke.get("comparison_scope"), cand_vs_smoke.get("comparison_scope")),
        ("num_comparisons", len(ref_vs_smoke.get("comparisons", [])), len(cand_vs_smoke.get("comparisons", []))),
        ("first_metric", ref_vs_smoke.get("comparisons", [{}])[0].get("metric"), cand_vs_smoke.get("comparisons", [{}])[0].get("metric")),
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
