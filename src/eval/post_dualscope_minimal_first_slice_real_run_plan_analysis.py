"""Post-analysis for the DualScope minimal first-slice real-run plan."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-minimal-first-slice-real-run-plan-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def _count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def post_dualscope_minimal_first_slice_real_run_plan_analysis(plan_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_real_run_scope.json",
        "dualscope_first_slice_dataset_slice_plan.json",
        "dualscope_first_slice_model_plan.json",
        "dualscope_first_slice_backdoor_construction_plan.json",
        "dualscope_first_slice_trigger_target_plan.json",
        "dualscope_first_slice_capability_mode_plan.json",
        "dualscope_first_slice_stage_execution_flow.json",
        "dualscope_first_slice_resource_contract.json",
        "dualscope_first_slice_preflight_checks.json",
        "dualscope_first_slice_run_command_plan.json",
        "dualscope_first_slice_expected_artifacts.json",
        "dualscope_first_slice_validation_criteria.json",
        "dualscope_first_slice_failure_fallback_plan.json",
        "dualscope_first_slice_real_run_plan_summary.json",
        "dualscope_first_slice_real_run_plan_details.jsonl",
        "dualscope_first_slice_real_run_plan_report.md",
    ]
    missing = [name for name in required if not (plan_dir / name).exists()]
    scope = _load_json(plan_dir / "dualscope_first_slice_real_run_scope.json")
    dataset = _load_json(plan_dir / "dualscope_first_slice_dataset_slice_plan.json")
    model = _load_json(plan_dir / "dualscope_first_slice_model_plan.json")
    backdoor = _load_json(plan_dir / "dualscope_first_slice_backdoor_construction_plan.json")
    capability = _load_json(plan_dir / "dualscope_first_slice_capability_mode_plan.json")
    stage_flow = _load_json(plan_dir / "dualscope_first_slice_stage_execution_flow.json")
    resource = _load_json(plan_dir / "dualscope_first_slice_resource_contract.json")
    preflight = _load_json(plan_dir / "dualscope_first_slice_preflight_checks.json")
    commands = _load_json(plan_dir / "dualscope_first_slice_run_command_plan.json")
    expected = _load_json(plan_dir / "dualscope_first_slice_expected_artifacts.json")
    validation = _load_json(plan_dir / "dualscope_first_slice_validation_criteria.json")
    fallback = _load_json(plan_dir / "dualscope_first_slice_failure_fallback_plan.json")
    summary = _load_json(plan_dir / "dualscope_first_slice_real_run_plan_summary.json")
    detail_count = _count_jsonl(plan_dir / "dualscope_first_slice_real_run_plan_details.jsonl")

    scope_ready = scope["dataset_id"] == "stanford_alpaca" and scope["planned_not_executed_yet"]
    dataset_ready = dataset["required_fields"] == ["instruction", "input", "output"] and dataset["failure_fallback_if_dataset_missing"].startswith("stop")
    model_ready = model["no_full_finetuning_guarantee"] and model["local_path_exists_at_plan_time"]
    backdoor_ready = not backdoor["benchmark_truth_semantics_changed"] and not backdoor["gate_semantics_changed"]
    capability_ready = capability["default_attempt"] == "with_logprobs" and capability["fallback_still_completes_real_run"]
    stage_flow_ready = all(key in stage_flow for key in ["stage1", "stage2", "stage3"])
    resource_ready = resource["expected_gpu_count"] == 2 and "enable_qlora" in resource["fallback_if_oom"]
    preflight_ready = len(preflight["checks"]) >= 12 and all(not row["executed_in_this_stage"] for row in preflight["checks"])
    commands_ready = len(commands["commands"]) >= 8 and all(row["planned_not_executed_yet"] for row in commands["commands"])
    artifact_ready = sum(len(items) for items in expected["artifact_groups"].values()) >= 20
    validation_ready = "all required artifacts exist" in validation["criteria"]
    fallback_ready = len(fallback["fallbacks"]) >= 6
    summary_ready = summary["planned_not_executed_yet"] and not summary["full_matrix_executed"] and not summary["training_executed"]
    details_ready = detail_count == summary["details_row_count"]

    checks = {
        "missing_artifacts": missing,
        "scope_ready": scope_ready,
        "dataset_ready": dataset_ready,
        "model_ready": model_ready,
        "backdoor_ready": backdoor_ready,
        "capability_ready": capability_ready,
        "stage_flow_ready": stage_flow_ready,
        "resource_ready": resource_ready,
        "preflight_ready": preflight_ready,
        "commands_ready": commands_ready,
        "artifact_ready": artifact_ready,
        "validation_ready": validation_ready,
        "fallback_ready": fallback_ready,
        "summary_ready": summary_ready,
        "details_ready": details_ready,
    }

    if not missing and all(value for key, value in checks.items() if key != "missing_artifacts"):
        final_verdict = "Minimal first slice real run plan validated"
        recommendation = "进入 dualscope-minimal-first-slice-real-run-preflight"
        basis = [
            "The real-run dataset/model/trigger/target/capability scope is frozen and remains inside the validated first slice.",
            "Execution flow, resource contract, preflight checks, planned commands, expected artifacts, validation criteria, and failure fallbacks are machine-readable.",
            "No training, full matrix execution, benchmark truth change, gate change, or route_c continuation occurred.",
        ]
    elif not missing and scope_ready and dataset_ready and commands_ready:
        final_verdict = "Partially validated"
        recommendation = "进入 first-slice-real-run-plan-compression"
        basis = ["The real-run plan shape exists, but at least one readiness check failed."]
    else:
        final_verdict = "Not validated"
        recommendation = "进入 first-slice-real-run-scope-closure"
        basis = ["Required real-run plan artifacts or core scope contracts are missing."]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        **checks,
        "detail_count": detail_count,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_first_slice_real_run_plan_validated__partially_validated__not_validated",
        "primary_basis": basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": basis,
        "do_not_do_yet": [
            "run_full_matrix",
            "claim_real_training_completed",
            "fabricate_missing_dataset",
            "change_benchmark_truth",
            "continue_route_c_199_plus",
        ],
    }
    write_json(output_dir / "dualscope_first_slice_real_run_plan_analysis_summary.json", analysis_summary)
    write_json(output_dir / "dualscope_first_slice_real_run_plan_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_real_run_plan_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_real_run_plan_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "dualscope_first_slice_real_run_plan_verdict.json").resolve()),
            "recommendation": str((output_dir / "dualscope_first_slice_real_run_plan_next_step_recommendation.json").resolve()),
        },
    }
