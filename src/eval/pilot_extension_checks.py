"""Artifact acceptance and repeatability checks for pilot extension runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "pilot_extension_run_summary": {
        "relative_path": "pilot_extension_run_summary.json",
        "purpose": "Top-level summary of the pilot extension run.",
    },
    "pilot_extension_config_snapshot": {
        "relative_path": "pilot_extension_config_snapshot.json",
        "purpose": "Resolved configuration paths and runtime settings for the pilot extension.",
    },
    "pilot_extension_execution_log": {
        "relative_path": "pilot_extension_execution.log",
        "purpose": "Human-readable execution log for the pilot extension run.",
    },
    "confidence_raw_results": {
        "relative_path": "confidence_probe/raw_results.jsonl",
        "purpose": "Raw confidence probe outputs for the pilot extension.",
    },
    "confidence_summary": {
        "relative_path": "confidence_probe/summary.json",
        "purpose": "Compact confidence summary for the pilot extension.",
    },
    "confidence_probe_log": {
        "relative_path": "confidence_probe/probe.log",
        "purpose": "Human-readable confidence probe log for the pilot extension.",
    },
    "confidence_feature_jsonl": {
        "relative_path": "confidence_probe/features/confidence_prompt_level_features.jsonl",
        "purpose": "Sample-level confidence features extracted from the pilot extension.",
    },
    "confidence_feature_csv": {
        "relative_path": "confidence_probe/features/confidence_features.csv",
        "purpose": "CSV export of the pilot extension confidence features.",
    },
    "confidence_feature_json": {
        "relative_path": "confidence_probe/features/confidence_features.json",
        "purpose": "Aggregated confidence feature artifact for the pilot extension.",
    },
    "confidence_feature_summary": {
        "relative_path": "confidence_probe/features/feature_summary.json",
        "purpose": "Compact confidence feature summary for the pilot extension.",
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


def validate_pilot_extension(run_dir: Path) -> dict[str, Any]:
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

    run_summary = load_json(run_dir / REQUIRED_ARTIFACTS["pilot_extension_run_summary"]["relative_path"])
    confidence_summary = load_json(run_dir / REQUIRED_ARTIFACTS["confidence_summary"]["relative_path"])
    feature_summary = load_json(run_dir / REQUIRED_ARTIFACTS["confidence_feature_summary"]["relative_path"])
    raw_rows = load_jsonl_rows(run_dir / REQUIRED_ARTIFACTS["confidence_raw_results"]["relative_path"])
    feature_rows = load_jsonl_rows(run_dir / REQUIRED_ARTIFACTS["confidence_feature_jsonl"]["relative_path"])

    field_checks = {
        "extension_summary_status_pass": run_summary.get("summary_status") == "PASS",
        "confidence_summary_status_pass": confidence_summary.get("summary_status") == "PASS",
        "feature_summary_status_pass": feature_summary.get("summary_status") == "PASS",
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
        "probe_id",
        "sample_id",
        "query_text",
        "response_text",
        "token_steps",
        "is_target_behavior",
    }
    required_feature_fields = {
        "run_id",
        "probe_id",
        "sample_id",
        "model_profile",
        "confidence_profile",
        "num_token_steps",
        "mean_entropy",
    }
    first_raw = raw_rows[0] if raw_rows else {}
    first_feature = feature_rows[0] if feature_rows else {}
    field_checks["extension_run_required_fields"] = required_run_fields.issubset(run_summary)
    field_checks["confidence_raw_required_fields"] = required_raw_fields.issubset(first_raw)
    field_checks["confidence_feature_required_fields"] = required_feature_fields.issubset(first_feature)

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
        "extension_snapshot": {
            "experiment_profile": run_summary.get("experiment_profile"),
            "model_profile": run_summary.get("model_profile"),
            "num_results": confidence_summary.get("num_results"),
            "target_behavior_rate": feature_summary.get("target_behavior_rate"),
            "mean_entropy_mean": feature_summary.get("mean_entropy_mean"),
        },
    }


def compare_pilot_extension_runs(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_pilot_extension(reference_run_dir)
    candidate = validate_pilot_extension(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both pilot extension runs failed artifact acceptance, so repeatability comparison was skipped.",
        }

    ref_summary = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["confidence_summary"]["relative_path"])
    cand_summary = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["confidence_summary"]["relative_path"])
    ref_feature = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["confidence_feature_summary"]["relative_path"])
    cand_feature = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["confidence_feature_summary"]["relative_path"])

    pairs = [
        ("num_results", ref_summary.get("num_results"), cand_summary.get("num_results")),
        ("generated_token_count", ref_summary.get("generated_token_count"), cand_summary.get("generated_token_count")),
        ("mean_chosen_token_prob", ref_summary.get("mean_chosen_token_prob"), cand_summary.get("mean_chosen_token_prob")),
        ("target_behavior_rate", ref_feature.get("target_behavior_rate"), cand_feature.get("target_behavior_rate")),
        ("mean_entropy_mean", ref_feature.get("mean_entropy_mean"), cand_feature.get("mean_entropy_mean")),
        ("high_confidence_fraction_mean", ref_feature.get("high_confidence_fraction_mean"), cand_feature.get("high_confidence_fraction_mean")),
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
