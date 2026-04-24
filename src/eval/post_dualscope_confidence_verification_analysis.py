"""Post-analysis for the DualScope confidence verification freeze stage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_confidence_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-confidence-verification-freeze-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def post_dualscope_confidence_verification_analysis(
    freeze_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    problem_definition = _load_json(freeze_dir / "dualscope_confidence_problem_definition.json")
    capability_contract = _load_json(freeze_dir / "dualscope_confidence_capability_contract.json")
    feature_schema_with_logprobs = _load_json(
        freeze_dir / "dualscope_confidence_feature_schema_with_logprobs.json"
    )
    feature_schema_without_logprobs = _load_json(
        freeze_dir / "dualscope_confidence_feature_schema_without_logprobs.json"
    )
    public_field_contract = _load_json(freeze_dir / "dualscope_confidence_public_field_contract.json")
    screening_to_confidence_contract = _load_json(
        freeze_dir / "dualscope_screening_to_confidence_contract.json"
    )
    budget_contract = _load_json(freeze_dir / "dualscope_confidence_budget_contract.json")
    fallback_policy = _load_json(freeze_dir / "dualscope_confidence_no_logprobs_fallback_policy.json")
    baseline_plan = _load_json(freeze_dir / "dualscope_confidence_baseline_plan.json")
    summary = _load_json(freeze_dir / "dualscope_confidence_verification_summary.json")

    dual_mode_ready = set(capability_contract["capability_modes"]) == {
        "with_logprobs",
        "without_logprobs",
    }
    with_logprobs_ready = int(feature_schema_with_logprobs["feature_count"]) >= 17
    without_logprobs_ready = int(feature_schema_without_logprobs["feature_count"]) >= 13
    stage1_contract_ready = bool(screening_to_confidence_contract["expected_stage1_inputs"]) and bool(
        screening_to_confidence_contract["candidate_trigger_fields"]
    )
    fusion_ready = bool(public_field_contract["fusion_readable_fields"])
    budget_ready = int(budget_contract["minimal_verification_budget"]) >= 2 and int(
        budget_contract["default_verification_budget"]
    ) >= 4
    fallback_ready = bool(fallback_policy["fallback_proxy_features"]) and bool(
        fallback_policy["downstream_flagging_strategy"]
    )
    baseline_ready = bool(baseline_plan["confidence_only_with_logprobs_baseline"]) and bool(
        baseline_plan["confidence_only_without_logprobs_baseline"]
    )
    verification_only = "final fusion verdict" in problem_definition["what_is_not_detected"]
    controlled_protocol_only = bool(summary["controlled_protocol_only"])
    detail_rows_ready = int(summary["details_row_count"]) >= 6

    if all(
        [
            dual_mode_ready,
            with_logprobs_ready,
            without_logprobs_ready,
            stage1_contract_ready,
            fusion_ready,
            budget_ready,
            fallback_ready,
            baseline_ready,
            verification_only,
            controlled_protocol_only,
            detail_rows_ready,
        ]
    ):
        final_verdict = "Confidence verification freeze validated"
        recommendation = "进入 dualscope-budget-aware-two-stage-fusion-design"
        primary_basis = [
            "Stage 2 now has an explicit dual-mode capability contract covering with-logprobs and without-logprobs settings.",
            "Both verification feature schemas, Stage 1 compatibility fields, and Stage 3 fusion public fields are frozen as machine-readable artifacts.",
            "Representative protocol traces demonstrate that the Stage 1 -> Stage 2 -> future Stage 3 interface is executable and auditable.",
        ]
    elif dual_mode_ready and stage1_contract_ready and fusion_ready:
        final_verdict = "Partially validated"
        recommendation = "继续做 confidence-verification-freeze-compression"
        primary_basis = [
            "The Stage 2 protocol shape exists, but one or more completeness checks remain below the validation threshold.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "回到 confidence-feature-and-fallback-closure"
        primary_basis = [
            "The Stage 2 freeze is still missing required dual-mode, budget, or downstream compatibility guarantees.",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "task_name": "dualscope-confidence-verification-with-without-logprobs",
        "dual_mode_ready": dual_mode_ready,
        "with_logprobs_ready": with_logprobs_ready,
        "without_logprobs_ready": without_logprobs_ready,
        "stage1_contract_ready": stage1_contract_ready,
        "fusion_ready": fusion_ready,
        "budget_ready": budget_ready,
        "fallback_ready": fallback_ready,
        "baseline_ready": baseline_ready,
        "verification_only": verification_only,
        "controlled_protocol_only": controlled_protocol_only,
        "detail_rows_ready": detail_rows_ready,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_confidence_verification_freeze_validated__partially_validated__not_validated",
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
            "implement_full_fusion_experiment_matrix_inside_stage2",
        ],
    }

    write_json(
        output_dir / "dualscope_confidence_verification_analysis_summary.json",
        analysis_summary,
    )
    write_json(output_dir / "dualscope_confidence_verification_verdict.json", verdict)
    write_json(
        output_dir / "dualscope_confidence_verification_next_step_recommendation.json",
        recommendation_payload,
    )
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str(
                (output_dir / "dualscope_confidence_verification_analysis_summary.json").resolve()
            ),
            "verdict": str((output_dir / "dualscope_confidence_verification_verdict.json").resolve()),
            "recommendation": str(
                (output_dir / "dualscope_confidence_verification_next_step_recommendation.json").resolve()
            ),
        },
    }
