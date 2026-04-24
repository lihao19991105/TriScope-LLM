"""Build the DualScope minimal first-slice real-run plan artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_common import write_json, write_jsonl
from src.eval.dualscope_first_slice_real_run_common import (
    SCHEMA_VERSION,
    TASK_NAME,
    build_backdoor_construction_plan,
    build_capability_mode_plan,
    build_dataset_slice_plan,
    build_details,
    build_expected_artifacts,
    build_failure_fallback_plan,
    build_model_plan,
    build_preflight_checks,
    build_report,
    build_resource_contract,
    build_run_command_plan,
    build_scope,
    build_stage_execution_flow,
    build_summary,
    build_trigger_target_plan,
    build_validation_criteria,
)
import json


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def build_dualscope_minimal_first_slice_real_run_plan(first_slice_plan_dir: Path, output_dir: Path, seed: int) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    first_slice = _load_json(first_slice_plan_dir / "dualscope_first_slice_definition.json")
    model_path = Path("/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct")
    model_local_exists = model_path.exists()

    scope = build_scope(first_slice, model_local_exists)
    dataset_slice_plan = build_dataset_slice_plan()
    model_plan = build_model_plan(model_local_exists)
    backdoor_plan = build_backdoor_construction_plan()
    trigger_target_plan = build_trigger_target_plan()
    capability_plan = build_capability_mode_plan()
    stage_flow = build_stage_execution_flow()
    resource_contract = build_resource_contract()
    preflight_checks = build_preflight_checks(dataset_slice_plan, model_plan)
    command_plan = build_run_command_plan()
    expected_artifacts = build_expected_artifacts()
    validation_criteria = build_validation_criteria()
    failure_fallback = build_failure_fallback_plan()

    payloads = {
        "scope": scope,
        "dataset_slice_plan": dataset_slice_plan,
        "model_plan": model_plan,
        "backdoor_construction_plan": backdoor_plan,
        "trigger_target_plan": trigger_target_plan,
        "capability_mode_plan": capability_plan,
        "stage_execution_flow": stage_flow,
        "resource_contract": resource_contract,
        "preflight_checks": preflight_checks,
        "run_command_plan": command_plan,
        "expected_artifacts": expected_artifacts,
        "validation_criteria": validation_criteria,
        "failure_fallback_plan": failure_fallback,
    }
    details = build_details(payloads)
    summary = build_summary(payloads, details)
    report = build_report(summary, scope)

    write_json(output_dir / "dualscope_first_slice_real_run_scope.json", scope)
    write_json(output_dir / "dualscope_first_slice_dataset_slice_plan.json", dataset_slice_plan)
    write_json(output_dir / "dualscope_first_slice_model_plan.json", model_plan)
    write_json(output_dir / "dualscope_first_slice_backdoor_construction_plan.json", backdoor_plan)
    write_json(output_dir / "dualscope_first_slice_trigger_target_plan.json", trigger_target_plan)
    write_json(output_dir / "dualscope_first_slice_capability_mode_plan.json", capability_plan)
    write_json(output_dir / "dualscope_first_slice_stage_execution_flow.json", stage_flow)
    write_json(output_dir / "dualscope_first_slice_resource_contract.json", resource_contract)
    write_json(output_dir / "dualscope_first_slice_preflight_checks.json", preflight_checks)
    write_json(output_dir / "dualscope_first_slice_run_command_plan.json", command_plan)
    write_json(output_dir / "dualscope_first_slice_expected_artifacts.json", expected_artifacts)
    write_json(output_dir / "dualscope_first_slice_validation_criteria.json", validation_criteria)
    write_json(output_dir / "dualscope_first_slice_failure_fallback_plan.json", failure_fallback)
    write_json(output_dir / "dualscope_first_slice_real_run_plan_summary.json", summary)
    write_jsonl(output_dir / "dualscope_first_slice_real_run_plan_details.jsonl", details)
    (output_dir / "dualscope_first_slice_real_run_plan_report.md").write_text(report, encoding="utf-8")
    write_json(
        output_dir / "dualscope_first_slice_command_manifest.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "commands": command_plan["commands"],
        },
    )
    preflight_md = "\n".join(
        ["# DualScope First Slice Preflight Checklist", ""]
        + [f"- [ ] `{row['check_id']}`: {row['target']} ({row['requirement']})" for row in preflight_checks["checks"]]
        + [""]
    )
    (output_dir / "dualscope_first_slice_preflight_checklist.md").write_text(preflight_md, encoding="utf-8")
    write_json(
        output_dir / "dualscope_first_slice_schema_compatibility_map.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "stage1_to_stage2": ["confidence_verification_candidate_flag", "screening_risk_score"],
            "stage2_to_stage3": ["capability_mode", "verification_risk_score", "verification_confidence_degradation_flag"],
            "stage1_to_stage3": ["screening_risk_score", "budget_usage_summary"],
        },
    )
    write_json(
        output_dir / "dualscope_first_slice_real_run_plan_manifest.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "task_name": TASK_NAME,
            "seed": seed,
            "first_slice_plan_dir": str(first_slice_plan_dir.resolve()),
        },
    )
    return {
        "summary": summary,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_real_run_plan_summary.json").resolve()),
            "report": str((output_dir / "dualscope_first_slice_real_run_plan_report.md").resolve()),
        },
    }
