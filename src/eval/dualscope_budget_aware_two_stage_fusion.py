"""Executable Stage 3 freeze pipeline for DualScope budget-aware fusion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_fusion_common import (
    SCHEMA_VERSION,
    TASK_NAME,
    build_budget_aware_policy_contract,
    build_capability_aware_fusion_policy,
    build_cost_analysis_plan,
    build_cost_tradeoff_examples,
    build_detail_rows,
    build_feature_examples,
    build_final_decision_contract,
    build_fusion_baseline_plan,
    build_fusion_io_contract,
    build_fusion_public_field_schema,
    build_policy_scenarios,
    build_problem_definition,
    build_report,
    build_representative_cases,
    build_stage_dependency_contract,
    build_summary,
    write_json,
    write_jsonl,
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def build_dualscope_budget_aware_two_stage_fusion(
    stage1_freeze_dir: Path,
    stage2_freeze_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    stage1_io_contract = _load_json(stage1_freeze_dir / "dualscope_illumination_io_contract.json")
    stage1_summary = _load_json(stage1_freeze_dir / "dualscope_illumination_screening_freeze_summary.json")
    stage2_public_field_contract = _load_json(
        stage2_freeze_dir / "dualscope_confidence_public_field_contract.json"
    )
    stage2_io_contract = _load_json(stage2_freeze_dir / "dualscope_confidence_io_contract.json")
    stage2_summary = _load_json(stage2_freeze_dir / "dualscope_confidence_verification_summary.json")

    problem_definition = build_problem_definition()
    dependency_contract = build_stage_dependency_contract(
        stage1_io_contract=stage1_io_contract,
        stage2_public_field_contract=stage2_public_field_contract,
        stage2_io_contract=stage2_io_contract,
    )
    public_field_schema = build_fusion_public_field_schema()
    budget_policy = build_budget_aware_policy_contract(stage1_summary, stage2_summary)
    capability_policy = build_capability_aware_fusion_policy()
    final_decision_contract = build_final_decision_contract()
    baseline_plan = build_fusion_baseline_plan()
    cost_plan = build_cost_analysis_plan()
    io_contract = build_fusion_io_contract()
    representative_cases = build_representative_cases(stage1_summary, stage2_summary)
    detail_rows = build_detail_rows(representative_cases, budget_policy, capability_policy)
    feature_examples = build_feature_examples(detail_rows)
    policy_scenarios = build_policy_scenarios(budget_policy, capability_policy)
    cost_tradeoff_examples = build_cost_tradeoff_examples(detail_rows)
    summary = build_summary(
        dependency_contract=dependency_contract,
        public_field_schema=public_field_schema,
        budget_policy=budget_policy,
        capability_policy=capability_policy,
        baseline_plan=baseline_plan,
        cost_plan=cost_plan,
        detail_rows=detail_rows,
    )
    report = build_report(
        problem_definition=problem_definition,
        dependency_contract=dependency_contract,
        public_field_schema=public_field_schema,
        budget_policy=budget_policy,
        capability_policy=capability_policy,
        final_decision_contract=final_decision_contract,
        baseline_plan=baseline_plan,
        cost_plan=cost_plan,
        summary=summary,
    )

    write_json(output_dir / "dualscope_fusion_problem_definition.json", problem_definition)
    write_json(output_dir / "dualscope_stage_dependency_contract.json", dependency_contract)
    write_json(output_dir / "dualscope_fusion_public_field_schema.json", public_field_schema)
    write_json(output_dir / "dualscope_budget_aware_policy_contract.json", budget_policy)
    write_json(output_dir / "dualscope_capability_aware_fusion_policy.json", capability_policy)
    write_json(output_dir / "dualscope_final_decision_contract.json", final_decision_contract)
    write_json(output_dir / "dualscope_fusion_baseline_plan.json", baseline_plan)
    write_json(output_dir / "dualscope_cost_analysis_plan.json", cost_plan)
    write_json(output_dir / "dualscope_fusion_io_contract.json", io_contract)
    write_jsonl(output_dir / "dualscope_budget_aware_two_stage_fusion_details.jsonl", detail_rows)
    write_json(output_dir / "dualscope_budget_aware_two_stage_fusion_summary.json", summary)
    (output_dir / "dualscope_budget_aware_two_stage_fusion_report.md").write_text(report, encoding="utf-8")
    write_json(output_dir / "dualscope_fusion_feature_examples.json", feature_examples)
    write_json(output_dir / "dualscope_fusion_policy_scenarios.json", policy_scenarios)
    write_json(output_dir / "dualscope_cost_tradeoff_examples.json", cost_tradeoff_examples)
    write_json(
        output_dir / "dualscope_fusion_run_manifest.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "task_name": TASK_NAME,
            "seed": seed,
            "stage1_freeze_dir": str(stage1_freeze_dir.resolve()),
            "stage2_freeze_dir": str(stage2_freeze_dir.resolve()),
            "representative_trace_count": len(detail_rows),
        },
    )

    return {
        "summary": summary,
        "output_paths": {
            "problem_definition": str((output_dir / "dualscope_fusion_problem_definition.json").resolve()),
            "dependency_contract": str((output_dir / "dualscope_stage_dependency_contract.json").resolve()),
            "public_field_schema": str((output_dir / "dualscope_fusion_public_field_schema.json").resolve()),
            "budget_policy": str((output_dir / "dualscope_budget_aware_policy_contract.json").resolve()),
            "capability_policy": str((output_dir / "dualscope_capability_aware_fusion_policy.json").resolve()),
            "final_decision_contract": str((output_dir / "dualscope_final_decision_contract.json").resolve()),
            "baseline_plan": str((output_dir / "dualscope_fusion_baseline_plan.json").resolve()),
            "cost_analysis_plan": str((output_dir / "dualscope_cost_analysis_plan.json").resolve()),
            "io_contract": str((output_dir / "dualscope_fusion_io_contract.json").resolve()),
            "details": str((output_dir / "dualscope_budget_aware_two_stage_fusion_details.jsonl").resolve()),
            "summary": str((output_dir / "dualscope_budget_aware_two_stage_fusion_summary.json").resolve()),
            "report": str((output_dir / "dualscope_budget_aware_two_stage_fusion_report.md").resolve()),
        },
    }
