"""Common helpers for DualScope first-slice real-run preflight."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscopellm/minimal-first-slice-real-run-preflight/v1"
TASK_NAME = "dualscope-minimal-first-slice-real-run-preflight"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def status_payload(
    check_id: str,
    status: str,
    passed: bool,
    message: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "check_id": check_id,
        "status": status,
        "passed": passed,
        "message": message,
        **extra,
    }


def required_stage_artifacts() -> dict[str, list[str]]:
    return {
        "stage1": [
            "dualscope_illumination_problem_definition.json",
            "dualscope_illumination_feature_schema.json",
            "dualscope_illumination_io_contract.json",
            "dualscope_illumination_budget_contract.json",
            "dualscope_illumination_screening_freeze_summary.json",
        ],
        "stage2": [
            "dualscope_confidence_capability_contract.json",
            "dualscope_confidence_feature_schema_with_logprobs.json",
            "dualscope_confidence_feature_schema_without_logprobs.json",
            "dualscope_screening_to_confidence_contract.json",
            "dualscope_confidence_public_field_contract.json",
            "dualscope_confidence_verification_summary.json",
        ],
        "stage3": [
            "dualscope_stage_dependency_contract.json",
            "dualscope_budget_aware_policy_contract.json",
            "dualscope_capability_aware_fusion_policy.json",
            "dualscope_final_decision_contract.json",
            "dualscope_fusion_baseline_plan.json",
            "dualscope_cost_analysis_plan.json",
            "dualscope_budget_aware_two_stage_fusion_summary.json",
        ],
        "matrix": [
            "dualscope_dataset_matrix.json",
            "dualscope_model_matrix.json",
            "dualscope_attack_trigger_matrix.json",
            "dualscope_target_behavior_matrix.json",
            "dualscope_capability_mode_matrix.json",
            "dualscope_baseline_matrix.json",
            "dualscope_metrics_contract.json",
            "dualscope_resource_execution_plan.json",
        ],
        "real_run_plan": [
            "dualscope_first_slice_real_run_scope.json",
            "dualscope_first_slice_dataset_slice_plan.json",
            "dualscope_first_slice_model_plan.json",
            "dualscope_first_slice_capability_mode_plan.json",
            "dualscope_first_slice_run_command_plan.json",
            "dualscope_first_slice_validation_criteria.json",
            "dualscope_first_slice_failure_fallback_plan.json",
        ],
    }


def check_artifact_group(root: Path, names: list[str]) -> dict[str, Any]:
    rows = []
    for name in names:
        path = root / name
        rows.append({"artifact": name, "path": str(path), "exists": path.exists()})
    return {"root": str(root), "missing": [row["artifact"] for row in rows if not row["exists"]], "artifacts": rows}
