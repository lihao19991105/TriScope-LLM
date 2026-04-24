"""Artifact acceptance and repeatability checks for pilot experiment runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "pilot_run_summary": {
        "relative_path": "pilot_run_summary.json",
        "purpose": "Top-level pilot run summary with selected experiment metadata and probe/feature snapshots.",
    },
    "pilot_run_config_snapshot": {
        "relative_path": "pilot_run_config_snapshot.json",
        "purpose": "Resolved configuration paths and runtime settings for the pilot run.",
    },
    "pilot_execution_log": {
        "relative_path": "pilot_execution.log",
        "purpose": "Human-readable execution log pointing to the pilot run artifacts.",
    },
    "reasoning_raw_results": {
        "relative_path": "reasoning_probe/raw_results.jsonl",
        "purpose": "Raw reasoning probe outputs for the pilot run.",
    },
    "reasoning_config_snapshot": {
        "relative_path": "reasoning_probe/config_snapshot.json",
        "purpose": "Resolved reasoning probe configuration snapshot for the pilot run.",
    },
    "reasoning_summary": {
        "relative_path": "reasoning_probe/summary.json",
        "purpose": "Compact reasoning summary for the pilot run.",
    },
    "reasoning_probe_log": {
        "relative_path": "reasoning_probe/probe.log",
        "purpose": "Human-readable log for the reasoning pilot probe.",
    },
    "reasoning_feature_jsonl": {
        "relative_path": "reasoning_probe/features/reasoning_prompt_level_features.jsonl",
        "purpose": "Sample-level reasoning features extracted from the pilot run.",
    },
    "reasoning_feature_csv": {
        "relative_path": "reasoning_probe/features/reasoning_features.csv",
        "purpose": "CSV export of the pilot reasoning features.",
    },
    "reasoning_feature_json": {
        "relative_path": "reasoning_probe/features/reasoning_features.json",
        "purpose": "Aggregated reasoning feature artifact for the pilot run.",
    },
    "reasoning_feature_summary": {
        "relative_path": "reasoning_probe/features/feature_summary.json",
        "purpose": "Compact reasoning feature summary for the pilot run.",
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


def validate_pilot_run(run_dir: Path) -> dict[str, Any]:
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

    run_summary = load_json(run_dir / REQUIRED_ARTIFACTS["pilot_run_summary"]["relative_path"])
    reasoning_summary = load_json(run_dir / REQUIRED_ARTIFACTS["reasoning_summary"]["relative_path"])
    feature_summary = load_json(run_dir / REQUIRED_ARTIFACTS["reasoning_feature_summary"]["relative_path"])
    raw_rows = load_jsonl_rows(run_dir / REQUIRED_ARTIFACTS["reasoning_raw_results"]["relative_path"])
    feature_rows = load_jsonl_rows(run_dir / REQUIRED_ARTIFACTS["reasoning_feature_jsonl"]["relative_path"])

    field_checks = {
        "pilot_summary_status_pass": run_summary.get("summary_status") == "PASS",
        "reasoning_summary_status_pass": reasoning_summary.get("summary_status") == "PASS",
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
        "original_answer",
        "reasoning_text",
        "reasoned_answer",
        "original_is_target_behavior",
        "reasoned_is_target_behavior",
    }
    required_feature_fields = {
        "run_id",
        "probe_id",
        "sample_id",
        "model_profile",
        "reasoning_profile",
        "answer_changed_after_reasoning",
        "reasoning_length",
    }
    first_raw = raw_rows[0] if raw_rows else {}
    first_feature = feature_rows[0] if feature_rows else {}
    field_checks["pilot_run_required_fields"] = required_run_fields.issubset(run_summary)
    field_checks["reasoning_raw_required_fields"] = required_raw_fields.issubset(first_raw)
    field_checks["reasoning_feature_required_fields"] = required_feature_fields.issubset(first_feature)

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
        "pilot_snapshot": {
            "experiment_profile": run_summary.get("experiment_profile"),
            "model_profile": run_summary.get("model_profile"),
            "num_results": reasoning_summary.get("num_results"),
            "answer_changed_rate": reasoning_summary.get("answer_changed_rate"),
            "feature_num_samples": feature_summary.get("num_samples"),
        },
    }


def compare_pilot_runs(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_pilot_run(reference_run_dir)
    candidate = validate_pilot_run(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both pilot runs failed artifact acceptance, so repeatability comparison was skipped.",
        }

    ref_reasoning = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["reasoning_summary"]["relative_path"])
    cand_reasoning = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["reasoning_summary"]["relative_path"])
    ref_feature = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["reasoning_feature_summary"]["relative_path"])
    cand_feature = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["reasoning_feature_summary"]["relative_path"])

    pairs = [
        ("num_results", ref_reasoning.get("num_results"), cand_reasoning.get("num_results")),
        ("num_non_empty_reasoning", ref_reasoning.get("num_non_empty_reasoning"), cand_reasoning.get("num_non_empty_reasoning")),
        ("answer_changed_rate", ref_reasoning.get("answer_changed_rate"), cand_reasoning.get("answer_changed_rate")),
        ("original_target_behavior_rate", ref_reasoning.get("original_target_behavior_rate"), cand_reasoning.get("original_target_behavior_rate")),
        ("reasoned_target_behavior_rate", ref_reasoning.get("reasoned_target_behavior_rate"), cand_reasoning.get("reasoned_target_behavior_rate")),
        ("feature_num_samples", ref_feature.get("num_samples"), cand_feature.get("num_samples")),
        ("feature_target_behavior_flip_rate", ref_feature.get("target_behavior_flip_rate"), cand_feature.get("target_behavior_flip_rate")),
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
