"""Common builders for the DualScope minimal first-slice execution plan."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscopellm/minimal-first-slice-execution-plan/v1"
TASK_NAME = "dualscope-minimal-first-slice-execution-plan"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def build_first_slice_definition(matrix_first_slice: dict[str, Any]) -> dict[str, Any]:
    slice_payload = matrix_first_slice["minimal_first_slice"]
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "slice_id": "dualscope_first_slice_stanford_alpaca_qwen1p5b_lexical_fixed_target",
        "dataset_id": slice_payload["dataset_id"],
        "model_id": slice_payload["model_id"],
        "trigger_id": slice_payload["trigger_id"],
        "target_id": slice_payload["target_id"],
        "capability_modes": slice_payload["capability_modes"],
        "baselines": slice_payload["baselines"],
        "controlled_scope": True,
        "not_full_matrix": True,
    }


def build_run_contract(first_slice: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "slice_id": first_slice["slice_id"],
        "execution_mode": "minimal_smoke_contract",
        "stage_order": [
            "stage1_illumination_screening",
            "stage2_confidence_verification_for_candidates",
            "stage3_budget_aware_fusion",
        ],
        "required_inputs": [
            "clean_examples_jsonl_or_manifest",
            "trigger_spec",
            "target_behavior_spec",
            "model_profile",
            "capability_mode",
            "budget_policy",
        ],
        "allowed_capability_modes": first_slice["capability_modes"],
        "allowed_baselines": first_slice["baselines"],
        "disallowed_now": ["full_matrix_sweep", "7b_execution", "full_finetuning", "new_prompt_family"],
        "smoke_command_intent": "validate artifact shape and stage contract compatibility before any full run",
    }


def build_expected_artifacts(first_slice: dict[str, Any]) -> dict[str, Any]:
    artifacts = [
        "stage1_illumination_outputs.jsonl",
        "stage1_illumination_summary.json",
        "stage2_confidence_outputs.jsonl",
        "stage2_confidence_summary.json",
        "stage3_fusion_outputs.jsonl",
        "stage3_fusion_summary.json",
        "baseline_scores.json",
        "metrics_placeholder.json",
        "budget_usage_summary.json",
        "first_slice_run_manifest.json",
    ]
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "slice_id": first_slice["slice_id"],
        "expected_artifacts": artifacts,
        "required_stage_fields": {
            "stage1": ["screening_risk_score", "confidence_verification_candidate_flag", "budget_usage_summary"],
            "stage2": ["capability_mode", "verification_risk_score", "budget_usage_summary"],
            "stage3": ["final_risk_score", "final_risk_bucket", "verification_triggered", "budget_usage_summary"],
        },
    }


def build_validation_criteria() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "success_criteria": [
            "all expected artifacts exist",
            "stage1/stage2/stage3 public fields exist",
            "capability mode is explicit",
            "budget fields are present",
            "metrics placeholder exists",
            "no full matrix execution occurs",
        ],
        "failure_criteria": [
            "missing artifact",
            "schema mismatch",
            "stage contract break",
            "CLI failure",
            "py_compile failure",
            "requires benchmark truth or gate semantic change",
        ],
    }


def build_resource_contract(first_slice: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "resource_boundary": "2 x RTX 3090",
        "model_id": first_slice["model_id"],
        "minimal_mode": "without_logprobs",
        "optional_mode": "with_logprobs_if_available",
        "max_first_slice_examples": 3,
        "max_stage1_probes_per_example": 5,
        "max_stage2_samples_per_candidate": 4,
        "no_training_required_for_smoke": True,
        "full_matrix_disallowed": True,
    }


def build_failure_fallback_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fallbacks": [
            {
                "failure": "local model unavailable",
                "action": "run controlled artifact smoke only; do not expand model axis",
            },
            {
                "failure": "with-logprobs unavailable",
                "action": "use without-logprobs path and set degradation flag",
            },
            {
                "failure": "artifact contract mismatch",
                "action": "repair first-slice contract before execution",
            },
        ],
        "stop_conditions": [
            "needs full training",
            "needs benchmark truth change",
            "needs route_c recursion",
            "needs expanded prompt family",
        ],
    }


def build_details(
    first_slice: dict[str, Any],
    run_contract: dict[str, Any],
    expected_artifacts: dict[str, Any],
    validation: dict[str, Any],
    resource: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {"detail_type": "slice_definition", "payload": first_slice},
        {"detail_type": "run_contract", "payload": run_contract},
        {"detail_type": "expected_artifacts", "payload": expected_artifacts},
        {"detail_type": "validation_criteria", "payload": validation},
        {"detail_type": "resource_contract", "payload": resource},
    ]


def build_summary(first_slice: dict[str, Any], expected_artifacts: dict[str, Any], details: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "slice_id": first_slice["slice_id"],
        "dataset_id": first_slice["dataset_id"],
        "model_id": first_slice["model_id"],
        "trigger_id": first_slice["trigger_id"],
        "target_id": first_slice["target_id"],
        "capability_mode_count": len(first_slice["capability_modes"]),
        "baseline_count": len(first_slice["baselines"]),
        "expected_artifact_count": len(expected_artifacts["expected_artifacts"]),
        "details_row_count": len(details),
        "full_matrix_disallowed": True,
        "controlled_plan_only": True,
        "recommended_next_step": "dualscope-minimal-first-slice-smoke-run",
    }


def build_report(summary: dict[str, Any], first_slice: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# DualScope Minimal First Slice Execution Plan Report",
            "",
            f"- Slice: `{summary['slice_id']}`",
            f"- Dataset: `{summary['dataset_id']}`",
            f"- Model: `{summary['model_id']}`",
            f"- Trigger: `{summary['trigger_id']}`",
            f"- Target: `{summary['target_id']}`",
            f"- Capability modes: `{', '.join(first_slice['capability_modes'])}`",
            f"- Baselines: `{', '.join(first_slice['baselines'])}`",
            "",
            "This is an execution plan only. It does not run the full matrix or train models.",
            "",
            "Next step: `dualscope-minimal-first-slice-smoke-run`.",
            "",
        ]
    )
