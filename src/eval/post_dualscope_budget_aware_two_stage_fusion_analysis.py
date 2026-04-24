"""Post-analysis for the DualScope Stage 3 budget-aware fusion design."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_fusion_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-budget-aware-two-stage-fusion-design-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def post_dualscope_budget_aware_two_stage_fusion_analysis(
    freeze_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    problem_definition = _load_json(freeze_dir / "dualscope_fusion_problem_definition.json")
    dependency_contract = _load_json(freeze_dir / "dualscope_stage_dependency_contract.json")
    public_field_schema = _load_json(freeze_dir / "dualscope_fusion_public_field_schema.json")
    budget_policy = _load_json(freeze_dir / "dualscope_budget_aware_policy_contract.json")
    capability_policy = _load_json(freeze_dir / "dualscope_capability_aware_fusion_policy.json")
    final_decision_contract = _load_json(freeze_dir / "dualscope_final_decision_contract.json")
    baseline_plan = _load_json(freeze_dir / "dualscope_fusion_baseline_plan.json")
    cost_plan = _load_json(freeze_dir / "dualscope_cost_analysis_plan.json")
    summary = _load_json(freeze_dir / "dualscope_budget_aware_two_stage_fusion_summary.json")

    dependency_ready = bool(dependency_contract["required_stage1_fields"]) and bool(
        dependency_contract["required_stage2_fields"]
    )
    public_schema_ready = int(public_field_schema["field_count"]) >= 12
    budget_policy_ready = bool(budget_policy["screening_to_verification_trigger_rule"]) and bool(
        budget_policy["no_logprobs_mode_policy"]
    )
    capability_ready = bool(capability_policy["with_logprobs_fusion_behavior"]) and bool(
        capability_policy["without_logprobs_fusion_behavior"]
    )
    final_contract_ready = bool(final_decision_contract["explainable_output_fields"]) and bool(
        final_decision_contract["budget_usage_summary_fields"]
    )
    baseline_ready = bool(baseline_plan["budget_aware_two_stage_fusion_baseline"]) and bool(
        baseline_plan["naive_concat_baseline"]
    )
    cost_ready = bool(cost_plan["performance_cost_tradeoff_fields"])
    representative_ready = int(summary["representative_trace_count"]) >= 5
    controlled_protocol_only = bool(summary["controlled_protocol_only"])
    budget_aware_only = "judge-style verdicts" in problem_definition["what_is_not_fused"]

    if all(
        [
            dependency_ready,
            public_schema_ready,
            budget_policy_ready,
            capability_ready,
            final_contract_ready,
            baseline_ready,
            cost_ready,
            representative_ready,
            controlled_protocol_only,
            budget_aware_only,
        ]
    ):
        final_verdict = "Budget-aware two-stage fusion design validated"
        recommendation = "进入 dualscope-experimental-matrix-freeze"
        primary_basis = [
            "Stage 3 now freezes the Stage 1 / Stage 2 dependency contract, the budget-aware trigger rule, and the capability-aware fusion rule as machine-readable artifacts.",
            "Representative traces cover stage1-only, with-logprobs, without-logprobs, budget-limited, and degradation-aware pathways.",
            "The final decision, baseline comparison, and cost-analysis contracts are now explicit enough to support the next experimental planning layer.",
        ]
    elif dependency_ready and budget_policy_ready and final_contract_ready:
        final_verdict = "Partially validated"
        recommendation = "继续做 budget-aware-fusion-design-compression"
        primary_basis = [
            "The Stage 3 shape is present, but one or more contract completeness checks remain below the validation threshold.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "回到 fusion-policy-and-public-field-closure"
        primary_basis = [
            "The Stage 3 design is still missing required dependency, policy, or final-decision guarantees.",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "task_name": "dualscope-budget-aware-two-stage-fusion-design",
        "dependency_ready": dependency_ready,
        "public_schema_ready": public_schema_ready,
        "budget_policy_ready": budget_policy_ready,
        "capability_ready": capability_ready,
        "final_contract_ready": final_contract_ready,
        "baseline_ready": baseline_ready,
        "cost_ready": cost_ready,
        "representative_ready": representative_ready,
        "controlled_protocol_only": controlled_protocol_only,
        "budget_aware_only": budget_aware_only,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_budget_aware_two_stage_fusion_design_validated__partially_validated__not_validated",
        "primary_basis": primary_basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": primary_basis,
        "do_not_do_yet": [
            "reopen_triscope_reasoning_as_mainline",
            "continue_route_c_recursive_stage_chain",
            "change_benchmark_truth_semantics",
            "change_gate_semantics",
            "run_full_paper_experimental_matrix_inside_stage3_design",
        ],
    }

    write_json(
        output_dir / "dualscope_budget_aware_two_stage_fusion_analysis_summary.json",
        analysis_summary,
    )
    write_json(output_dir / "dualscope_budget_aware_two_stage_fusion_verdict.json", verdict)
    write_json(
        output_dir / "dualscope_budget_aware_two_stage_fusion_next_step_recommendation.json",
        recommendation_payload,
    )
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str(
                (output_dir / "dualscope_budget_aware_two_stage_fusion_analysis_summary.json").resolve()
            ),
            "verdict": str((output_dir / "dualscope_budget_aware_two_stage_fusion_verdict.json").resolve()),
            "recommendation": str(
                (output_dir / "dualscope_budget_aware_two_stage_fusion_next_step_recommendation.json").resolve()
            ),
        },
    }
