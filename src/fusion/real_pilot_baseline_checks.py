"""Acceptance and repeatability checks for real-pilot fusion baseline artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = {
    "real_pilot_rule_predictions": "real_pilot_rule_predictions.jsonl",
    "real_pilot_rule_summary": "real_pilot_rule_summary.json",
    "real_pilot_logistic_summary": "real_pilot_logistic_summary.json",
    "real_pilot_fusion_summary": "real_pilot_fusion_summary.json",
    "config_snapshot": "config_snapshot.json",
    "run_log": "run.log",
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


def validate_real_pilot_fusion_baselines(run_dir: Path) -> dict[str, Any]:
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

    rule_predictions = load_jsonl(run_dir / REQUIRED_ARTIFACTS["real_pilot_rule_predictions"])
    rule_summary = load_json(run_dir / REQUIRED_ARTIFACTS["real_pilot_rule_summary"])
    logistic_summary = load_json(run_dir / REQUIRED_ARTIFACTS["real_pilot_logistic_summary"])
    fusion_summary = load_json(run_dir / REQUIRED_ARTIFACTS["real_pilot_fusion_summary"])

    field_checks = {
        "rule_predictions_non_empty": len(rule_predictions) > 0,
        "rule_summary_pass": rule_summary.get("summary_status") == "PASS",
        "fusion_summary_pass": fusion_summary.get("summary_status") == "PASS",
        "logistic_summary_present": logistic_summary.get("summary_status") in {"PASS", "SKIP"},
        "logistic_skip_reason_recorded": (logistic_summary.get("summary_status") != "SKIP")
        or bool(logistic_summary.get("reason")),
    }
    return {
        "summary_status": "PASS" if all(field_checks.values()) else "FAIL",
        "run_dir": str(run_dir),
        "artifact_checks": checks,
        "field_checks": field_checks,
        "snapshot": {
            "num_rule_predictions": len(rule_predictions),
            "mean_rule_prediction_score": rule_summary.get("mean_prediction_score"),
            "logistic_status": logistic_summary.get("summary_status"),
        },
    }


def compare_real_pilot_fusion_baselines(reference_run_dir: Path, candidate_run_dir: Path) -> dict[str, Any]:
    reference = validate_real_pilot_fusion_baselines(reference_run_dir)
    candidate = validate_real_pilot_fusion_baselines(candidate_run_dir)
    if reference["summary_status"] != "PASS" or candidate["summary_status"] != "PASS":
        return {
            "summary_status": "FAIL",
            "reference_acceptance": reference,
            "candidate_acceptance": candidate,
            "comparisons": [],
            "all_key_metrics_match": False,
            "error": "One or both real-pilot baseline runs failed artifact acceptance.",
        }

    ref_rule = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["real_pilot_rule_summary"])
    cand_rule = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["real_pilot_rule_summary"])
    ref_logistic = load_json(reference_run_dir.resolve() / REQUIRED_ARTIFACTS["real_pilot_logistic_summary"])
    cand_logistic = load_json(candidate_run_dir.resolve() / REQUIRED_ARTIFACTS["real_pilot_logistic_summary"])

    pairs = [
        ("num_predictions", ref_rule.get("num_predictions"), cand_rule.get("num_predictions")),
        ("mean_prediction_score", ref_rule.get("mean_prediction_score"), cand_rule.get("mean_prediction_score")),
        ("num_positive_predictions", ref_rule.get("num_positive_predictions"), cand_rule.get("num_positive_predictions")),
        ("logistic_status", ref_logistic.get("summary_status"), cand_logistic.get("summary_status")),
        ("logistic_reason", ref_logistic.get("reason"), cand_logistic.get("reason")),
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
