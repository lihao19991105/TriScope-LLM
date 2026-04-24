"""Acceptance and repeatability checks for third-pilot illumination runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "pilot_illumination_run_summary": {
        "relative_path": "pilot_illumination_run_summary.json",
        "purpose": "Top-level summary of the third pilot illumination run.",
    },
    "pilot_illumination_config_snapshot": {
        "relative_path": "pilot_illumination_config_snapshot.json",
        "purpose": "Resolved configuration paths and runtime settings for the illumination pilot.",
    },
    "pilot_illumination_execution_log": {
        "relative_path": "pilot_illumination_execution.log",
        "purpose": "Human-readable execution log for the illumination pilot run.",
    },
    "illumination_raw_results": {
        "relative_path": "illumination_probe/raw_results.jsonl",
        "purpose": "Raw illumination probe outputs for the third pilot.",
    },
    "illumination_summary": {
        "relative_path": "illumination_probe/summary.json",
        "purpose": "Compact illumination summary for the third pilot.",
    },
    "illumination_probe_log": {
        "relative_path": "illumination_probe/probe.log",
        "purpose": "Human-readable illumination probe log for the third pilot.",
    },
    "illumination_feature_jsonl": {
        "relative_path": "illumination_probe/features/prompt_level_features.jsonl",
        "purpose": "Prompt-level illumination features extracted from the third pilot.",
    },
    "illumination_feature_csv": {
        "relative_path": "illumination_probe/features/illumination_features.csv",
        "purpose": "CSV export of the third pilot illumination features.",
    },
    "illumination_feature_json": {
        "relative_path": "illumination_probe/features/illumination_features.json",
        "purpose": "Aggregated illumination feature artifact for the third pilot.",
    },
    "illumination_feature_summary": {
        "relative_path": "illumination_probe/features/feature_summary.json",
        "purpose": "Compact illumination feature summary for the third pilot.",
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


def validate_pilot_illumination(run_dir: Path) -> dict[str, Any]:
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

    run_summary = load_json(run_dir / REQUIRED_ARTIFACTS["pilot_illumination_run_summary"]["relative_path"])
    illumination_summary = load_json(run_dir / REQUIRED_ARTIFACTS["illumination_summary"]["relative_path"])
    feature_summary = load_json(run_dir / REQUIRED_ARTIFACTS["illumination_feature_summary"]["relative_path"])
    raw_rows = load_jsonl_rows(run_dir / REQUIRED_ARTIFACTS["illumination_raw_results"]["relative_path"])
    feature_rows = load_jsonl_rows(run_dir / REQUIRED_ARTIFACTS["illumination_feature_jsonl"]["relative_path"])

    field_checks = {
        "illumination_run_summary_pass": run_summary.get("summary_status") == "PASS",
        "illumination_summary_pass": illumination_summary.get("summary_status") == "PASS",
        "feature_summary_pass": feature_summary.get("summary_status") == "PASS",
        "raw_rows_non_empty": len(raw_rows) > 0,
        "feature_rows_non_empty": len(feature_rows) > 0,
        "feature_extraction_completed": run_summary.get("feature_extraction_completed") is True,
    }
    required_run_fields = {
        "experiment_profile",
        "dataset_profile",
        "model_profile",
        "probe_summary",
        "feature_extraction_completed",
    }
    required_raw_fields = {
        "prompt_id",
        "sample_id",
        "prompt_text",
        "response_text",
        "is_target_behavior",
        "metadata",
    }
    required_feature_fields = {
        "run_id",
        "probe_id",
        "sample_id",
        "model_profile",
        "prompt_template_name",
        "is_target_behavior",
        "response_length",
    }
    first_raw = raw_rows[0] if raw_rows else {}
    first_feature = feature_rows[0] if feature_rows else {}
    field_checks["illumination_run_required_fields"] = required_run_fields.issubset(run_summary)
    field_checks["illumination_raw_required_fields"] = required_raw_fields.issubset(first_raw)
    field_checks["illumination_feature_required_fields"] = required_feature_fields.issubset(first_feature)

    summary_status = "PASS" if all(field_checks.values()) else "FAIL"
    return {
        "summary_status": summary_status,
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "artifact_paths": resolved_paths,
        "artifact_purposes": purposes,
        "field_checks": field_checks,
        "artifact_counts": {
            "raw_rows": len(raw_rows),
            "feature_rows": len(feature_rows),
        },
        "illumination_snapshot": {
            "experiment_profile": run_summary.get("experiment_profile"),
            "model_profile": run_summary.get("model_profile"),
            "num_results": illumination_summary.get("num_results"),
            "target_behavior_rate": feature_summary.get("target_behavior_rate"),
            "realized_budget_ratio": feature_summary.get("realized_budget_ratio"),
        },
    }


def compare_pilot_illumination_runs(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_pilot_illumination(reference_run_dir)
    candidate = validate_pilot_illumination(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both pilot illumination runs failed artifact acceptance, so repeatability comparison was skipped.",
        }

    ref_summary = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["illumination_summary"]["relative_path"])
    cand_summary = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["illumination_summary"]["relative_path"])
    ref_feature = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["illumination_feature_summary"]["relative_path"])
    cand_feature = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["illumination_feature_summary"]["relative_path"])

    pairs = [
        ("num_results", ref_summary.get("num_results"), cand_summary.get("num_results")),
        ("num_target_behavior", ref_summary.get("num_target_behavior"), cand_summary.get("num_target_behavior")),
        ("target_behavior_rate", ref_feature.get("target_behavior_rate"), cand_feature.get("target_behavior_rate")),
        ("realized_budget_ratio", ref_feature.get("realized_budget_ratio"), cand_feature.get("realized_budget_ratio")),
        ("variance_across_prompts", ref_feature.get("variance_across_prompts"), cand_feature.get("variance_across_prompts")),
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
