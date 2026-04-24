"""Common protocol builders for DualScope Stage 3 budget-aware fusion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscopellm/budget-aware-two-stage-fusion-design/v1"
STAGE_NAME = "budget_aware_two_stage_fusion"
TASK_NAME = "dualscope-budget-aware-two-stage-fusion-design"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def build_problem_definition() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "stage_name": STAGE_NAME,
        "fusion_goal": (
            "Fuse Stage 1 illumination evidence and Stage 2 confidence verification evidence into a "
            "budget-aware, capability-aware final DualScope risk decision."
        ),
        "what_is_fused": [
            "Stage 1 screening risk and public fields",
            "Stage 2 verification risk and lock evidence",
            "budget usage summaries",
            "capability mode and degradation flags",
        ],
        "what_is_not_fused": [
            "reasoning branch",
            "judge-style verdicts",
            "unbounded feature soup",
            "full experimental matrix outputs",
        ],
        "why_budget_aware_two_stage": [
            "Illumination is cheaper and suitable for broad screening.",
            "Confidence verification is more expensive and should be selectively triggered.",
            "Real black-box settings are query-budget constrained.",
            "Therefore the fusion protocol must decide not only how to combine evidence, but also when verification is worth spending budget on.",
        ],
        "relation_to_stage1": {
            "stage1_role": "full-coverage screening and candidate routing",
            "stage1_required_outputs": [
                "screening_risk_score",
                "screening_risk_bucket",
                "confidence_verification_candidate_flag",
                "budget_usage_summary",
                "screening_summary_for_fusion",
            ],
        },
        "relation_to_stage2": {
            "stage2_role": "selective verification for high-risk or policy-triggered candidates",
            "stage2_required_outputs": [
                "capability_mode",
                "verification_risk_score",
                "verification_risk_bucket",
                "confidence_lock_evidence_present",
                "budget_usage_summary",
                "verification_summary_for_fusion",
            ],
        },
    }


def build_stage_dependency_contract(
    stage1_io_contract: dict[str, Any],
    stage2_public_field_contract: dict[str, Any],
    stage2_io_contract: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "required_stage1_fields": [
            "dataset_id",
            "example_id",
            "screening_risk_score",
            "screening_risk_bucket",
            "confidence_verification_candidate_flag",
            "budget_usage_summary",
            "screening_summary_for_fusion",
        ],
        "required_stage2_fields": stage2_public_field_contract["mode_shared_fields"],
        "optional_stage2_fields": [
            *stage2_public_field_contract["mode_specific_fields"]["with_logprobs"],
            *stage2_public_field_contract["mode_specific_fields"]["without_logprobs"],
            "verification_summary_for_fusion",
        ],
        "no_logprobs_mode_handling": {
            "required_flags": [
                "verification_confidence_degradation_flag",
                "fallback_mode_limit_flag",
            ],
            "policy_note": "Fallback mode remains valid but cannot be treated as evidence-equivalent to with_logprobs verification.",
        },
        "degradation_flag_usage": [
            "decrease verification weight under without_logprobs mode",
            "attach explainable uncertainty note to the final evidence summary",
            "surface capability-sensitive risk interpretation to downstream analysis",
        ],
        "invalid_contract_conditions": [
            "missing stage1 screening_risk_score",
            "missing stage1 candidate flag when verification policy wants to trigger",
            "verification triggered but stage2 capability_mode absent",
            "without_logprobs verification triggered but degradation flag absent",
            "stage2 fields consumed when verification_triggered is false",
        ],
        "stage1_fusion_readable_fields": stage1_io_contract["fusion_stage_readable_fields"],
        "stage2_fusion_readable_fields": stage2_public_field_contract["fusion_readable_fields"],
        "stage2_emitted_outputs": stage2_io_contract["emitted_outputs"],
    }


def build_fusion_public_field_schema() -> dict[str, Any]:
    fields = [
        {
            "field_name": "screening_risk_score",
            "source_stage": "stage1",
            "dtype": "float",
            "semantic_meaning": "Stage 1 illumination screening risk score.",
            "required": True,
            "used_in_final_decision": True,
            "used_in_cost_analysis": False,
            "capability_sensitive": False,
        },
        {
            "field_name": "screening_risk_bucket",
            "source_stage": "stage1",
            "dtype": "str",
            "semantic_meaning": "Bucketized Stage 1 risk level used in trigger policy.",
            "required": True,
            "used_in_final_decision": True,
            "used_in_cost_analysis": False,
            "capability_sensitive": False,
        },
        {
            "field_name": "confidence_verification_candidate_flag",
            "source_stage": "stage1",
            "dtype": "int",
            "semantic_meaning": "Whether Stage 1 explicitly routes the sample toward Stage 2 eligibility.",
            "required": True,
            "used_in_final_decision": True,
            "used_in_cost_analysis": True,
            "capability_sensitive": False,
        },
        {
            "field_name": "capability_mode",
            "source_stage": "stage2",
            "dtype": "str",
            "semantic_meaning": "Current verification capability mode.",
            "required": False,
            "used_in_final_decision": True,
            "used_in_cost_analysis": True,
            "capability_sensitive": True,
        },
        {
            "field_name": "verification_risk_score",
            "source_stage": "stage2",
            "dtype": "float",
            "semantic_meaning": "Stage 2 verification risk score when verification is triggered.",
            "required": False,
            "used_in_final_decision": True,
            "used_in_cost_analysis": False,
            "capability_sensitive": True,
        },
        {
            "field_name": "verification_risk_bucket",
            "source_stage": "stage2",
            "dtype": "str",
            "semantic_meaning": "Bucketized Stage 2 verification severity.",
            "required": False,
            "used_in_final_decision": True,
            "used_in_cost_analysis": False,
            "capability_sensitive": True,
        },
        {
            "field_name": "confidence_lock_evidence_present",
            "source_stage": "stage2",
            "dtype": "int",
            "semantic_meaning": "Whether Stage 2 produced explicit lock evidence.",
            "required": False,
            "used_in_final_decision": True,
            "used_in_cost_analysis": False,
            "capability_sensitive": True,
        },
        {
            "field_name": "verification_confidence_degradation_flag",
            "source_stage": "stage2",
            "dtype": "int",
            "semantic_meaning": "Whether Stage 2 evidence came from degraded fallback mode.",
            "required": False,
            "used_in_final_decision": True,
            "used_in_cost_analysis": True,
            "capability_sensitive": True,
        },
        {
            "field_name": "verification_triggered",
            "source_stage": "stage3",
            "dtype": "int",
            "semantic_meaning": "Whether Stage 3 decided to spend budget on verification.",
            "required": True,
            "used_in_final_decision": True,
            "used_in_cost_analysis": True,
            "capability_sensitive": False,
        },
        {
            "field_name": "final_risk_score",
            "source_stage": "stage3",
            "dtype": "float",
            "semantic_meaning": "Final DualScope risk score after budget-aware fusion.",
            "required": True,
            "used_in_final_decision": True,
            "used_in_cost_analysis": False,
            "capability_sensitive": True,
        },
        {
            "field_name": "final_risk_bucket",
            "source_stage": "stage3",
            "dtype": "str",
            "semantic_meaning": "Bucketized final DualScope risk severity.",
            "required": True,
            "used_in_final_decision": True,
            "used_in_cost_analysis": False,
            "capability_sensitive": True,
        },
        {
            "field_name": "final_decision_flag",
            "source_stage": "stage3",
            "dtype": "int",
            "semantic_meaning": "Final binary suspicious / non-suspicious decision flag.",
            "required": True,
            "used_in_final_decision": True,
            "used_in_cost_analysis": False,
            "capability_sensitive": False,
        },
        {
            "field_name": "budget_usage_summary",
            "source_stage": "stage3",
            "dtype": "object",
            "semantic_meaning": "Combined budget accounting across screening and verification.",
            "required": True,
            "used_in_final_decision": False,
            "used_in_cost_analysis": True,
            "capability_sensitive": True,
        },
    ]
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "field_count": len(fields),
        "fields": fields,
    }


def build_budget_aware_policy_contract(
    stage1_summary: dict[str, Any],
    stage2_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "default_screening_budget": stage1_summary["default_query_budget"],
        "default_verification_budget": stage2_summary["default_verification_budget"],
        "screening_to_verification_trigger_rule": {
            "primary_rule": "trigger verification when screening_risk_score >= 0.60 and candidate_flag is true",
            "secondary_rule": "trigger verification when screening_risk_bucket == 'medium' and candidate_flag is true only if remaining budget >= mode-specific minimum",
            "stage1_only_rule": "retain Stage 1 only when screening risk is below the trigger threshold or budget is insufficient",
        },
        "risk_threshold_policy": {
            "stage1_trigger_threshold": 0.60,
            "stage1_medium_review_threshold": 0.50,
            "final_positive_threshold": 0.65,
        },
        "candidate_trigger_policy": {
            "must_require_candidate_flag": True,
            "candidate_flag_source": "stage1 confidence_verification_candidate_flag",
            "budget_shortfall_behavior": "skip verification and retain stage1-only path with explicit budget_shortfall_note",
        },
        "no_logprobs_mode_policy": {
            "allow_without_logprobs_verification": True,
            "minimum_budget_required": 4,
            "degradation_flag_required": True,
            "final_decision_must_be_capability_aware": True,
        },
        "disallowed_expansion_now": [
            "verify every sample regardless of stage1 risk",
            "dynamic threshold search over large grids",
            "multi-hop verification trees",
            "full calibration or learned fusion model training",
        ],
        "future_extension_hooks": [
            "adaptive thresholding once experimental matrix is frozen",
            "learned lightweight fusion once baseline tables are stabilized",
            "larger budget adaptation space",
        ],
    }


def build_capability_aware_fusion_policy() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "with_logprobs_fusion_behavior": {
            "verification_weight": 0.60,
            "screening_weight": 0.40,
            "policy_note": "Token-level verification evidence is treated as the stronger second-stage signal.",
        },
        "without_logprobs_fusion_behavior": {
            "verification_weight": 0.45,
            "screening_weight": 0.55,
            "policy_note": "Fallback evidence remains valid but is weighted more conservatively.",
        },
        "degradation_flag_handling": [
            "reduce effective verification contribution when verification_confidence_degradation_flag == true",
            "attach degradation-aware evidence note to final explainable fields",
        ],
        "verification_confidence_adjustment": {
            "with_logprobs_adjustment": 0.0,
            "without_logprobs_adjustment": -0.08,
        },
        "fallback_penalty_or_uncertainty_strategy": {
            "strategy_name": "conservative_penalty",
            "apply_penalty_when": "without_logprobs and degradation flag present",
            "effect": "reduce final risk amplification from verification while preserving the fact that verification was triggered",
        },
    }


def build_final_decision_contract() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_risk_score": {
            "dtype": "float",
            "meaning": "Final fused risk score in [0, 1].",
        },
        "final_risk_bucket": {
            "dtype": "str",
            "allowed_values": ["low", "medium", "high"],
        },
        "final_decision_flag": {
            "dtype": "int",
            "meaning": "Binary suspicious flag derived from the final risk score threshold.",
        },
        "verification_triggered": {
            "dtype": "int",
            "meaning": "Whether Stage 3 spent verification budget on this example.",
        },
        "evidence_summary_fields": [
            "screening_summary_for_fusion",
            "verification_summary_for_fusion",
            "capability_mode",
            "degradation_note",
            "decision_rationale",
        ],
        "budget_usage_summary_fields": [
            "screening_budget_consumed",
            "verification_budget_consumed",
            "total_budget_consumed",
            "budget_consumption_ratio",
            "verification_triggered",
        ],
        "explainable_output_fields": [
            "stage1_candidate_flag",
            "verification_triggered",
            "capability_mode",
            "final_risk_bucket",
            "decision_rationale",
            "degradation_note",
        ],
        "paper_consumers": {
            "main_table_fields": ["final_risk_score", "final_decision_flag", "verification_triggered"],
            "ablation_table_fields": [
                "screening_risk_score",
                "verification_risk_score",
                "final_risk_score",
                "capability_mode",
            ],
            "cost_analysis_fields": [
                "verification_triggered",
                "budget_consumption_ratio",
                "capability_mode",
            ],
        },
    }


def build_fusion_baseline_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "illumination_only_baseline": {
            "required_fields": ["screening_risk_score", "screening_risk_bucket"],
            "status": "frozen_protocol_only",
        },
        "confidence_only_with_logprobs_baseline": {
            "required_fields": ["verification_risk_score", "capability_mode"],
            "status": "frozen_protocol_only",
        },
        "confidence_only_without_logprobs_baseline": {
            "required_fields": [
                "verification_risk_score",
                "capability_mode",
                "verification_confidence_degradation_flag",
            ],
            "status": "frozen_protocol_only",
        },
        "naive_concat_baseline": {
            "required_fields": ["screening_risk_score", "verification_risk_score"],
            "status": "frozen_protocol_only",
            "note": "Simple juxtaposition baseline without budget-aware trigger logic.",
        },
        "budget_aware_two_stage_fusion_baseline": {
            "required_fields": [
                "screening_risk_score",
                "confidence_verification_candidate_flag",
                "verification_risk_score",
                "capability_mode",
                "verification_confidence_degradation_flag",
            ],
            "status": "frozen_protocol_only",
        },
        "required_comparison_fields": [
            "final_risk_score",
            "final_decision_flag",
            "verification_triggered",
            "capability_mode",
            "budget_consumption_ratio",
        ],
    }


def build_cost_analysis_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "query_count_metrics": [
            "screening_query_count",
            "verification_query_count",
            "total_query_count",
        ],
        "verification_rate_metrics": [
            "verification_trigger_rate",
            "mode_specific_verification_rate",
        ],
        "budget_consumption_metrics": [
            "screening_budget_consumed",
            "verification_budget_consumed",
            "total_budget_consumed",
            "budget_consumption_ratio",
        ],
        "mode_specific_cost_metrics": [
            "with_logprobs_verification_cost",
            "without_logprobs_verification_cost",
            "budget_limited_skip_rate",
        ],
        "performance_cost_tradeoff_fields": [
            "final_risk_score",
            "final_decision_flag",
            "verification_triggered",
            "budget_consumption_ratio",
            "capability_mode",
        ],
    }


def build_fusion_io_contract() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "required_inputs": [
            "stage1_public_fields",
            "budget_policy",
            "stage1_candidate_flag",
        ],
        "optional_inputs": [
            "stage2_public_fields",
            "capability_mode",
            "verification_degradation_flags",
            "screening_summary_for_fusion",
            "verification_summary_for_fusion",
        ],
        "emitted_outputs": [
            "final_risk_score",
            "final_risk_bucket",
            "final_decision_flag",
            "verification_triggered",
            "capability_mode",
            "evidence_summary",
            "budget_usage_summary",
            "ablation_public_fields",
        ],
    }


def build_representative_cases(
    stage1_summary: dict[str, Any],
    stage2_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    stage1_by_id = {
        row["case_id"]: row for row in stage1_summary["representative_case_overview"]
    }
    stage2_rows = stage2_summary["representative_case_overview"]
    stage2_lookup = {
        (row["stage1_candidate_id"], row["capability_mode"]): row for row in stage2_rows
    }
    return [
        {
            "trace_id": "alpaca-stage1-only-retained",
            "path_type": "stage1_only_retained",
            "stage1_candidate_id": "alpaca-screen-001",
            "dataset_id": "stanford_alpaca",
            "stage1": stage1_by_id["alpaca-screen-001"],
            "verification_budget_available": 6,
            "capability_mode": None,
            "stage2": None,
        },
        {
            "trace_id": "advbench-triggered-with-logprobs",
            "path_type": "with_logprobs_triggered",
            "stage1_candidate_id": "advbench-screen-001",
            "dataset_id": "advbench",
            "stage1": stage1_by_id["advbench-screen-001"],
            "verification_budget_available": 6,
            "capability_mode": "with_logprobs",
            "stage2": stage2_lookup[("advbench-screen-001", "with_logprobs")],
        },
        {
            "trace_id": "jbb-triggered-without-logprobs",
            "path_type": "without_logprobs_triggered",
            "stage1_candidate_id": "jbb-screen-001",
            "dataset_id": "jbb_behaviors",
            "stage1": stage1_by_id["jbb-screen-001"],
            "verification_budget_available": 4,
            "capability_mode": "without_logprobs",
            "stage2": stage2_lookup[("jbb-screen-001", "without_logprobs")],
        },
        {
            "trace_id": "jbb-budget-limited-skip",
            "path_type": "budget_limited_skip",
            "stage1_candidate_id": "jbb-screen-001",
            "dataset_id": "jbb_behaviors",
            "stage1": stage1_by_id["jbb-screen-001"],
            "verification_budget_available": 1,
            "capability_mode": "without_logprobs",
            "stage2": None,
        },
        {
            "trace_id": "advbench-degradation-aware-fallback",
            "path_type": "degradation_aware_path",
            "stage1_candidate_id": "advbench-screen-001",
            "dataset_id": "advbench",
            "stage1": stage1_by_id["advbench-screen-001"],
            "verification_budget_available": 4,
            "capability_mode": "without_logprobs",
            "stage2": stage2_lookup[("advbench-screen-001", "without_logprobs")],
        },
    ]


def _bucket(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def build_detail_rows(
    cases: list[dict[str, Any]],
    budget_policy: dict[str, Any],
    capability_policy: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    trigger_threshold = budget_policy["risk_threshold_policy"]["stage1_trigger_threshold"]
    medium_threshold = budget_policy["risk_threshold_policy"]["stage1_medium_review_threshold"]
    positive_threshold = budget_policy["risk_threshold_policy"]["final_positive_threshold"]

    for case in cases:
        stage1 = case["stage1"]
        stage2 = case["stage2"]
        candidate_flag = stage1["confidence_verification_candidate_flag"]
        screening_risk = stage1["screening_risk_score"]
        mode = case["capability_mode"]
        budget_available = case["verification_budget_available"]
        verification_triggered = False
        trigger_reason = "stage1_only_low_or_medium_risk"
        degradation_note = None
        verification_risk = None
        verification_bucket = None
        final_risk = screening_risk

        if case["path_type"] == "stage1_only_retained":
            verification_triggered = False
            final_risk = round(screening_risk * 0.95, 4)
            trigger_reason = "screening_below_trigger_threshold"
        elif case["path_type"] == "budget_limited_skip":
            verification_triggered = False
            final_risk = round(screening_risk, 4)
            trigger_reason = "verification_budget_insufficient"
            degradation_note = "verification_skipped_due_to_budget_shortfall"
        else:
            if (
                candidate_flag
                and (
                    screening_risk >= trigger_threshold
                    or (screening_risk >= medium_threshold and budget_available >= 4)
                )
                and stage2 is not None
            ):
                verification_triggered = True
                verification_risk = stage2["verification_risk_score"]
                verification_bucket = stage2["verification_risk_bucket"]
                if mode == "with_logprobs":
                    final_risk = round(
                        screening_risk * capability_policy["with_logprobs_fusion_behavior"]["screening_weight"]
                        + verification_risk * capability_policy["with_logprobs_fusion_behavior"]["verification_weight"],
                        4,
                    )
                    trigger_reason = "high_risk_candidate_with_logprobs_verification"
                else:
                    adjustment = capability_policy["verification_confidence_adjustment"][
                        "without_logprobs_adjustment"
                    ]
                    final_risk = round(
                        screening_risk * capability_policy["without_logprobs_fusion_behavior"]["screening_weight"]
                        + verification_risk * capability_policy["without_logprobs_fusion_behavior"]["verification_weight"]
                        + adjustment,
                        4,
                    )
                    trigger_reason = "candidate_triggered_fallback_verification"
                    degradation_note = "fallback_mode_used__verification_evidence_downweighted"
            else:
                verification_triggered = False
                final_risk = round(screening_risk, 4)

        final_bucket = _bucket(final_risk)
        final_decision = int(final_risk >= positive_threshold)
        screening_budget_consumed = round(stage1["budget_consumption_ratio"] * 10, 2)
        verification_budget_consumed = 0.0
        if verification_triggered and stage2 is not None:
            verification_budget_consumed = round(
                stage2["budget_consumption_ratio"] * case["verification_budget_available"], 2
            )
        total_budget = screening_budget_consumed + verification_budget_consumed
        budget_limit = 10 + case["verification_budget_available"]

        rows.append(
            {
                "summary_status": "PASS",
                "schema_version": SCHEMA_VERSION,
                "trace_id": case["trace_id"],
                "path_type": case["path_type"],
                "dataset_id": case["dataset_id"],
                "stage1_input": {
                    "stage1_candidate_id": case["stage1_candidate_id"],
                    "screening_risk_score": screening_risk,
                    "screening_risk_bucket": stage1["screening_risk_bucket"],
                    "confidence_verification_candidate_flag": candidate_flag,
                    "budget_consumption_ratio": stage1["budget_consumption_ratio"],
                },
                "verification_trigger_decision": {
                    "verification_triggered": verification_triggered,
                    "trigger_reason": trigger_reason,
                    "capability_mode_requested": mode,
                    "verification_budget_available": budget_available,
                },
                "stage2_input": None
                if not verification_triggered
                else {
                    "capability_mode": mode,
                    "verification_risk_score": verification_risk,
                    "verification_risk_bucket": verification_bucket,
                    "confidence_lock_evidence_present": stage2["confidence_lock_evidence_present"],
                },
                "fusion_evidence": {
                    "screening_evidence_weight": capability_policy["with_logprobs_fusion_behavior"]["screening_weight"]
                    if mode == "with_logprobs"
                    else capability_policy["without_logprobs_fusion_behavior"]["screening_weight"],
                    "verification_evidence_weight": 0.0
                    if not verification_triggered
                    else (
                        capability_policy["with_logprobs_fusion_behavior"]["verification_weight"]
                        if mode == "with_logprobs"
                        else capability_policy["without_logprobs_fusion_behavior"]["verification_weight"]
                    ),
                    "degradation_note": degradation_note,
                },
                "final_decision_output": {
                    "final_risk_score": final_risk,
                    "final_risk_bucket": final_bucket,
                    "final_decision_flag": final_decision,
                    "verification_triggered": verification_triggered,
                    "capability_mode": mode if verification_triggered else "stage1_only",
                    "evidence_summary": {
                        "screening_summary": "stage1 screening risk retained",
                        "verification_summary": None if not verification_triggered else "stage2 verification fused",
                        "decision_rationale": trigger_reason,
                        "degradation_note": degradation_note,
                    },
                },
                "budget_usage_summary": {
                    "screening_budget_consumed": screening_budget_consumed,
                    "verification_budget_consumed": verification_budget_consumed,
                    "total_budget_consumed": total_budget,
                    "budget_limit": budget_limit,
                    "budget_consumption_ratio": round(total_budget / budget_limit, 4),
                },
                "ablation_public_fields": {
                    "screening_risk_score": screening_risk,
                    "verification_risk_score": verification_risk,
                    "final_risk_score": final_risk,
                    "verification_triggered": verification_triggered,
                    "capability_mode": mode if verification_triggered else "stage1_only",
                },
            }
        )
    return rows


def build_feature_examples(detail_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "examples": [
            {
                "trace_id": row["trace_id"],
                "verification_triggered": row["verification_trigger_decision"]["verification_triggered"],
                "final_risk_score": row["final_decision_output"]["final_risk_score"],
                "final_risk_bucket": row["final_decision_output"]["final_risk_bucket"],
            }
            for row in detail_rows[:3]
        ],
    }


def build_policy_scenarios(
    budget_policy: dict[str, Any],
    capability_policy: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "policy_scenarios": [
            {
                "scenario_name": "stage1_only_retained",
                "condition": "screening_risk_score < 0.60",
                "policy_result": "skip verification and keep stage1-driven decision",
            },
            {
                "scenario_name": "with_logprobs_triggered",
                "condition": "screening_risk_score >= 0.60 and capability_mode == with_logprobs",
                "policy_result": capability_policy["with_logprobs_fusion_behavior"],
            },
            {
                "scenario_name": "without_logprobs_triggered",
                "condition": "candidate flag true, medium-or-higher screening risk, fallback mode available",
                "policy_result": capability_policy["without_logprobs_fusion_behavior"],
            },
            {
                "scenario_name": "budget_limited_skip",
                "condition": "verification budget below mode-specific minimum",
                "policy_result": budget_policy["candidate_trigger_policy"]["budget_shortfall_behavior"],
            },
        ],
    }


def build_cost_tradeoff_examples(detail_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "examples": [
            {
                "trace_id": row["trace_id"],
                "verification_triggered": row["verification_trigger_decision"]["verification_triggered"],
                "capability_mode": row["final_decision_output"]["capability_mode"],
                "budget_consumption_ratio": row["budget_usage_summary"]["budget_consumption_ratio"],
                "final_risk_score": row["final_decision_output"]["final_risk_score"],
            }
            for row in detail_rows
        ],
    }


def build_summary(
    dependency_contract: dict[str, Any],
    public_field_schema: dict[str, Any],
    budget_policy: dict[str, Any],
    capability_policy: dict[str, Any],
    baseline_plan: dict[str, Any],
    cost_plan: dict[str, Any],
    detail_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    verification_trigger_count = sum(
        1 for row in detail_rows if row["verification_trigger_decision"]["verification_triggered"]
    )
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "stage_name": STAGE_NAME,
        "problem_definition_frozen": True,
        "stage_dependency_ready": bool(dependency_contract["required_stage1_fields"])
        and bool(dependency_contract["required_stage2_fields"]),
        "fusion_public_field_count": public_field_schema["field_count"],
        "budget_aware_policy_frozen": bool(budget_policy["screening_to_verification_trigger_rule"]),
        "capability_aware_policy_frozen": bool(capability_policy["degradation_flag_handling"]),
        "dualscope_baseline_frozen": bool(baseline_plan["budget_aware_two_stage_fusion_baseline"]),
        "cost_analysis_contract_frozen": bool(cost_plan["performance_cost_tradeoff_fields"]),
        "representative_trace_count": len(detail_rows),
        "verification_trigger_rate": round(verification_trigger_count / len(detail_rows), 4),
        "controlled_protocol_only": True,
        "representative_trace_overview": [
            {
                "trace_id": row["trace_id"],
                "path_type": row["path_type"],
                "verification_triggered": row["verification_trigger_decision"]["verification_triggered"],
                "capability_mode": row["final_decision_output"]["capability_mode"],
                "final_risk_score": row["final_decision_output"]["final_risk_score"],
                "final_risk_bucket": row["final_decision_output"]["final_risk_bucket"],
                "budget_consumption_ratio": row["budget_usage_summary"]["budget_consumption_ratio"],
            }
            for row in detail_rows
        ],
        "legacy_route_c_foundation_reference": {
            "status": "retained_as_reliability_foundation",
            "note": "Historical route_c chain remains appendix-grade reliability support and is not the current research mainline.",
        },
    }


def build_report(
    problem_definition: dict[str, Any],
    dependency_contract: dict[str, Any],
    public_field_schema: dict[str, Any],
    budget_policy: dict[str, Any],
    capability_policy: dict[str, Any],
    final_decision_contract: dict[str, Any],
    baseline_plan: dict[str, Any],
    cost_plan: dict[str, Any],
    summary: dict[str, Any],
) -> str:
    return f"""# DualScope Budget-Aware Two-Stage Fusion Design Report

## What Stage 3 Is

DualScope Stage 3 is the policy and decision layer that turns Stage 1 screening and Stage 2 verification into
a budget-aware final decision protocol.

It answers two questions together:

1. should we spend verification budget on this example?
2. how should screening and verification evidence be fused into a final risk decision?

## Why This Is Not Simple Concatenation

This stage is not just score concatenation because:

- verification is more expensive than screening
- verification should not run on every sample
- without-logprobs verification is weaker than with-logprobs verification
- final evidence strength depends on both capability mode and budget usage

## Stage Dependencies

Required Stage 1 fields:

{json.dumps(dependency_contract['required_stage1_fields'], indent=2, ensure_ascii=True)}

Required Stage 2 fields:

{json.dumps(dependency_contract['required_stage2_fields'], indent=2, ensure_ascii=True)}

## Budget-Aware Trigger Policy

{json.dumps(budget_policy['screening_to_verification_trigger_rule'], indent=2, ensure_ascii=True)}

Risk thresholds:

{json.dumps(budget_policy['risk_threshold_policy'], indent=2, ensure_ascii=True)}

## Capability-Aware Fusion Policy

With-logprobs behavior:

{json.dumps(capability_policy['with_logprobs_fusion_behavior'], indent=2, ensure_ascii=True)}

Without-logprobs behavior:

{json.dumps(capability_policy['without_logprobs_fusion_behavior'], indent=2, ensure_ascii=True)}

Degradation handling:

{json.dumps(capability_policy['degradation_flag_handling'], indent=2, ensure_ascii=True)}

## Final Decision Contract

Explainable output fields:

{json.dumps(final_decision_contract['explainable_output_fields'], indent=2, ensure_ascii=True)}

Paper consumers:

{json.dumps(final_decision_contract['paper_consumers'], indent=2, ensure_ascii=True)}

## Baselines and Ablations

- illumination-only baseline
- confidence-only with-logprobs baseline
- confidence-only without-logprobs baseline
- naive concat baseline
- budget-aware two-stage fusion baseline

Required comparison fields:

{json.dumps(baseline_plan['required_comparison_fields'], indent=2, ensure_ascii=True)}

## Cost Analysis Contract

Cost analysis fields:

{json.dumps(cost_plan['performance_cost_tradeoff_fields'], indent=2, ensure_ascii=True)}

## Representative Trace Coverage

- representative_trace_count = {summary['representative_trace_count']}
- verification_trigger_rate = {summary['verification_trigger_rate']}
- fusion_public_field_count = {summary['fusion_public_field_count']}

Representative paths include:

- stage1-only retained path
- with-logprobs triggered path
- without-logprobs triggered path
- budget-limited skip path
- degradation-aware fallback path

## Why This Freeze Is Enough for the Next Stage

This stage now freezes:

- the Stage 1 / Stage 2 -> Stage 3 contract
- the budget-aware trigger rule
- the capability-aware fusion rule
- the final decision output shape
- the baseline and cost-analysis comparison contract

That is the minimum stable interface required before opening the broader experimental matrix.
"""
