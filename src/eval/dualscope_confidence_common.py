"""Common protocol builders for DualScope Stage 2 confidence verification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscopellm/confidence-verification-freeze/v1"
STAGE_NAME = "confidence_verification"
TASK_NAME = "dualscope-confidence-verification-with-without-logprobs"


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
        "verification_goal": (
            "Verify whether Stage 1 high-risk candidates exhibit abnormal confidence locking, "
            "sequence-level lock tendency, concentration collapse, or fallback-visible output lock proxies."
        ),
        "what_is_detected": [
            "abnormal confidence locking",
            "sequence lock tendency",
            "concentration collapse",
            "entropy or uncertainty collapse",
            "repeated-sampling collapse under no-logprobs fallback",
            "verification-stage abnormal output lock evidence",
        ],
        "what_is_not_detected": [
            "illumination-stage susceptibility screening",
            "reasoning inconsistency",
            "final fusion verdict",
            "semantic relabeling of benchmark truth",
        ],
        "why_stage2_is_verification_not_final_verdict": [
            "Stage 2 only runs after Stage 1 has already identified a risky candidate.",
            "It verifies whether the candidate enters a locked or concentrated generation regime.",
            "It should strengthen or weaken downstream evidence, not emit the final DualScope decision by itself.",
        ],
        "relation_to_stage1": {
            "stage1_role": "risk screening and candidate routing",
            "stage2_default_trigger": "confidence_verification_candidate_flag == true",
            "stage1_fields_consumed": [
                "dataset_id",
                "example_id",
                "screening_risk_score",
                "screening_risk_bucket",
                "confidence_verification_candidate_flag",
                "template_results",
                "query_aggregate_features",
                "budget_usage_summary",
            ],
        },
        "relation_to_stage3": {
            "stage3_role": "budget-aware lightweight fusion of screening and verification evidence",
            "stage2_output_for_stage3": [
                "capability_mode",
                "verification_risk_score",
                "verification_risk_bucket",
                "confidence_lock_evidence_present",
                "budget_usage_summary",
                "fusion_public_fields",
            ],
        },
    }


def build_capability_contract() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "supports_logprobs": True,
        "no_logprobs_fallback_supported": True,
        "capability_modes": [
            "with_logprobs",
            "without_logprobs",
        ],
        "required_inputs_per_mode": {
            "with_logprobs": [
                "candidate_response_tokens",
                "token_logprobs",
                "stage1_screening_risk_score",
                "budget_usage_summary",
            ],
            "without_logprobs": [
                "sampled_outputs",
                "stage1_screening_risk_score",
                "budget_usage_summary",
            ],
        },
        "unavailable_fields_per_mode": {
            "with_logprobs": [],
            "without_logprobs": [
                "token_logprobs",
                "entropy_mean",
                "topk_mass_concentration",
                "sequence_lock_strength_from_logprobs",
            ],
        },
        "mode_specific_limitations": {
            "with_logprobs": [
                "Still operates in black-box conditions and cannot use hidden states or gradients.",
            ],
            "without_logprobs": [
                "Fallback proxy features are not equivalent to token-level confidence measurements.",
                "Lock evidence is weaker and must be flagged downstream as degraded-confidence mode.",
            ],
        },
    }


def build_feature_schema_with_logprobs() -> dict[str, Any]:
    features = [
        {
            "feature_name": "average_top1_probability",
            "level": "sequence",
            "dtype": "float",
            "semantic_meaning": "Average top-1 token probability over the observed generation.",
            "computation_note": "Mean of top-1 probabilities across tokens in the verification window.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": None,
        },
        {
            "feature_name": "target_token_probability_mean",
            "level": "sequence",
            "dtype": "float",
            "semantic_meaning": "Average probability mass assigned to target-aligned tokens when such tokens are identifiable.",
            "computation_note": "Optional target-alignment supporting feature derived from token distributions.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "target_pattern_repetition_proxy",
        },
        {
            "feature_name": "topk_mass_concentration",
            "level": "sequence",
            "dtype": "float",
            "semantic_meaning": "How concentrated the distribution is inside the top-k probability mass.",
            "computation_note": "Higher values indicate sharper token concentration.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "repeated_phrase_concentration",
        },
        {
            "feature_name": "peak_probability",
            "level": "token",
            "dtype": "float",
            "semantic_meaning": "Peak observed token confidence inside the verification window.",
            "computation_note": "Max top-1 probability.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": None,
        },
        {
            "feature_name": "probability_variance_collapse",
            "level": "sequence",
            "dtype": "float",
            "semantic_meaning": "Degree to which token probabilities collapse into a narrow variance band.",
            "computation_note": "Low variance after high concentration is treated as collapse evidence.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "answer_mode_collapse",
        },
        {
            "feature_name": "entropy_mean",
            "level": "sequence",
            "dtype": "float",
            "semantic_meaning": "Average token entropy during verification.",
            "computation_note": "Lower average entropy can support confidence lock evidence.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "response_diversity_drop",
        },
        {
            "feature_name": "entropy_drop",
            "level": "sequence",
            "dtype": "float",
            "semantic_meaning": "Net entropy decrease over the verification window.",
            "computation_note": "Captures uncertainty decay toward locked generation.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "instability_inverse_proxy",
        },
        {
            "feature_name": "entropy_collapse_span",
            "level": "span",
            "dtype": "int",
            "semantic_meaning": "Length of the longest low-entropy span.",
            "computation_note": "Span-based lock evidence from sustained entropy collapse.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "multi_run_output_collapse",
        },
        {
            "feature_name": "uncertainty_decay_rate",
            "level": "sequence",
            "dtype": "float",
            "semantic_meaning": "Rate at which uncertainty declines through generation.",
            "computation_note": "Negative slope of entropy proxy over position.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "instability_inverse_proxy",
        },
        {
            "feature_name": "lock_window_length",
            "level": "span",
            "dtype": "int",
            "semantic_meaning": "Observed verification window length that meets a lock threshold.",
            "computation_note": "Derived from probability and entropy thresholds.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "multi_run_output_collapse",
        },
        {
            "feature_name": "longest_lock_span",
            "level": "span",
            "dtype": "int",
            "semantic_meaning": "Longest continuous locked subsequence.",
            "computation_note": "Sequence-level persistence indicator.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "answer_mode_collapse",
        },
        {
            "feature_name": "sustained_high_confidence_ratio",
            "level": "sequence",
            "dtype": "float",
            "semantic_meaning": "Fraction of positions that remain in a high-confidence state.",
            "computation_note": "Persistence ratio computed under a token-probability threshold.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "sampled_output_agreement_rate",
        },
        {
            "feature_name": "lock_reentry_count",
            "level": "sequence",
            "dtype": "int",
            "semantic_meaning": "Number of times the generation re-enters a locked regime after leaving it.",
            "computation_note": "Supports recurrent lock signatures rather than a single spike.",
            "default_enabled": True,
            "fusion_compatible": False,
            "depends_on_logprobs": True,
            "fallback_proxy": "candidate_output_mode_count",
        },
        {
            "feature_name": "sequence_lock_strength",
            "level": "aggregated",
            "dtype": "float",
            "semantic_meaning": "Combined strength of sequence-level lock evidence under with-logprobs mode.",
            "computation_note": "Aggregates concentration, entropy and persistence cues.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": True,
            "fallback_proxy": "lexical_lock_proxy",
        },
        {
            "feature_name": "target_alignment_proxy",
            "level": "output",
            "dtype": "float",
            "semantic_meaning": "Output-level proxy for whether locked generation aligns with the suspicious target direction.",
            "computation_note": "Shared support field for future fusion.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
            "fallback_proxy": "target_pattern_repetition_proxy",
        },
        {
            "feature_name": "generation_consistency_flag",
            "level": "output",
            "dtype": "int",
            "semantic_meaning": "Whether verification outputs remain structurally consistent across supporting traces.",
            "computation_note": "Mode-shared support field.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
            "fallback_proxy": "generation_consistency_flag",
        },
        {
            "feature_name": "abnormal_lock_bucket",
            "level": "aggregated",
            "dtype": "str",
            "semantic_meaning": "Human-readable lock severity bucket.",
            "computation_note": "Derived from verification risk score and evidence pattern.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
            "fallback_proxy": "abnormal_lock_bucket",
        },
    ]
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage_name": STAGE_NAME,
        "capability_mode": "with_logprobs",
        "feature_count": len(features),
        "default_enabled_feature_count": sum(1 for item in features if item["default_enabled"]),
        "features": features,
    }


def build_feature_schema_without_logprobs() -> dict[str, Any]:
    features = [
        {
            "feature_name": "repeated_sampling_consistency",
            "level": "candidate",
            "dtype": "float",
            "semantic_meaning": "Agreement strength across repeated sampled generations.",
            "computation_note": "Primary no-logprobs consistency proxy.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "answer_mode_collapse",
            "level": "candidate",
            "dtype": "float",
            "semantic_meaning": "Degree to which repeated outputs collapse into the same answer mode.",
            "computation_note": "Higher values indicate lower mode diversity.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "sampled_output_agreement_rate",
            "level": "candidate",
            "dtype": "float",
            "semantic_meaning": "Fraction of sampled outputs that agree on the same dominant outcome.",
            "computation_note": "Simple fallback proxy for concentrated output behavior.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "repeated_phrase_concentration",
            "level": "output",
            "dtype": "float",
            "semantic_meaning": "Degree of repeated phrase concentration across repeated outputs.",
            "computation_note": "Lexical concentration proxy.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "target_pattern_repetition_proxy",
            "level": "output",
            "dtype": "float",
            "semantic_meaning": "Proxy for repeated suspicious target patterns in fallback mode.",
            "computation_note": "Used only as a fallback alignment support signal.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "response_diversity_drop",
            "level": "candidate",
            "dtype": "float",
            "semantic_meaning": "Drop in lexical or structural diversity over repeated outputs.",
            "computation_note": "Inverse diversity support signal for fallback lock evidence.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "lexical_lock_proxy",
            "level": "aggregated",
            "dtype": "float",
            "semantic_meaning": "Combined fallback proxy for output lock tendency.",
            "computation_note": "Aggregates repetition, collapse and consistency cues.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "multi_run_output_collapse",
            "level": "candidate",
            "dtype": "float",
            "semantic_meaning": "Cross-run collapse proxy from repeated verification runs.",
            "computation_note": "Higher values indicate stronger collapse across runs.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "candidate_output_mode_count",
            "level": "candidate",
            "dtype": "int",
            "semantic_meaning": "Number of distinct output modes observed under repeated sampling.",
            "computation_note": "Lower counts imply stronger mode collapse.",
            "default_enabled": True,
            "fusion_compatible": False,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "instability_inverse_proxy",
            "level": "aggregated",
            "dtype": "float",
            "semantic_meaning": "Inverse instability measure used as a no-logprobs lock proxy.",
            "computation_note": "Higher values imply less output variation across runs.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "fallback_lock_risk_score",
            "level": "aggregated",
            "dtype": "float",
            "semantic_meaning": "Fallback-specific verification risk score before bucketization.",
            "computation_note": "Aggregates fallback proxy features only.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "fallback_mode_limit_flag",
            "level": "aggregated",
            "dtype": "int",
            "semantic_meaning": "Whether the fallback mode reaches its interpretability or capability limit.",
            "computation_note": "Used to warn downstream stages that evidence quality is degraded.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
        {
            "feature_name": "verification_confidence_degradation_flag",
            "level": "aggregated",
            "dtype": "int",
            "semantic_meaning": "Explicit flag that no-logprobs mode yields weaker verification confidence than token-level mode.",
            "computation_note": "Must be propagated to Stage 3.",
            "default_enabled": True,
            "fusion_compatible": True,
            "depends_on_logprobs": False,
        },
    ]
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage_name": STAGE_NAME,
        "capability_mode": "without_logprobs",
        "feature_count": len(features),
        "default_enabled_feature_count": sum(1 for item in features if item["default_enabled"]),
        "features": features,
    }


def build_public_field_contract() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage2_public_fields": [
            "capability_mode",
            "verification_risk_score",
            "verification_risk_bucket",
            "confidence_lock_evidence_present",
            "stage1_candidate_id",
            "stage1_screening_risk",
            "budget_usage_summary",
            "verification_summary_for_fusion",
        ],
        "illumination_readable_fields": [
            "dataset_id",
            "example_id",
            "stage1_candidate_id",
            "stage1_screening_risk",
            "stage1_screening_bucket",
            "confidence_verification_candidate_flag",
        ],
        "fusion_readable_fields": [
            "capability_mode",
            "verification_risk_score",
            "verification_risk_bucket",
            "confidence_lock_evidence_present",
            "verification_summary_for_fusion",
            "verification_confidence_degradation_flag",
            "budget_usage_summary",
        ],
        "mode_shared_fields": [
            "capability_mode",
            "verification_risk_score",
            "verification_risk_bucket",
            "confidence_lock_evidence_present",
            "stage1_candidate_id",
            "stage1_screening_risk",
            "budget_usage_summary",
        ],
        "mode_specific_fields": {
            "with_logprobs": [
                "sequence_lock_strength",
                "entropy_mean",
                "topk_mass_concentration",
            ],
            "without_logprobs": [
                "fallback_lock_risk_score",
                "fallback_mode_limit_flag",
                "verification_confidence_degradation_flag",
            ],
        },
    }


def build_screening_to_confidence_contract(
    stage1_io_contract: dict[str, Any],
    stage1_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "expected_stage1_inputs": stage1_io_contract["confidence_stage_readable_fields"],
        "candidate_trigger_fields": [
            "confidence_verification_candidate_flag",
            "screening_risk_score",
            "screening_risk_bucket",
        ],
        "screening_risk_fields_used": [
            "screening_risk_score",
            "screening_risk_bucket",
            "query_aggregate_features",
            "template_results",
        ],
        "budget_fields_used": [
            "budget_usage_summary",
            "budget_consumption_ratio",
        ],
        "contract_assumptions": [
            "Stage 2 starts only on Stage 1 candidates flagged for verification.",
            "Stage 2 consumes Stage 1 public and confidence-readable fields without redefining Stage 1 semantics.",
            "Stage 1 remains the only owner of screening risk definitions.",
            f"Stage 1 representative candidate count at freeze time: {stage1_summary['representative_case_count']}.",
        ],
    }


def build_io_contract() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "required_inputs": [
            "dataset_id",
            "example_id",
            "stage1_candidate_id",
            "stage1_screening_risk_score",
            "stage1_screening_risk_bucket",
            "confidence_verification_candidate_flag",
            "verification_budget_policy",
            "capability_mode",
        ],
        "optional_inputs": [
            "template_results",
            "query_aggregate_features",
            "screening_summary_for_fusion",
            "budget_usage_summary",
            "reference_answer",
            "target_text",
            "metadata",
            "token_logprobs",
            "sampled_outputs",
        ],
        "emitted_outputs": [
            "verification_feature_vector",
            "verification_evidence_summary",
            "verification_risk_score",
            "verification_risk_bucket",
            "confidence_lock_evidence_present",
            "budget_usage_summary",
            "confidence_public_fields",
            "fusion_public_fields",
        ],
        "downstream_consumers": {
            "fusion_stage": "Consumes Stage 2 public fields alongside Stage 1 public fields.",
            "confidence_only_baseline": "Consumes verification risk outputs within a single capability mode.",
        },
    }


def build_budget_contract() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "default_verification_budget": 6,
        "per_candidate_budget": 6,
        "minimal_verification_budget": 2,
        "repeated_sampling_budget": {
            "default_samples": 3,
            "minimal_samples": 2,
            "future_expansion_samples": 5,
        },
        "token_prob_observation_budget": {
            "default_windows": 2,
            "minimal_windows": 1,
            "future_expansion_windows": 4,
        },
        "no_logprobs_fallback_budget": 4,
        "disallowed_expansion_now": [
            "large repeated-sampling sweeps",
            "sequence-level calibration search",
            "cross-model confidence alignment",
            "high-cost adaptive prompt tree verification",
        ],
        "future_extension_hooks": [
            "longer repeated-sampling grids for fallback mode",
            "more granular span-level lock diagnostics",
            "sequence-level calibration once fusion protocol is frozen",
        ],
    }


def build_no_logprobs_fallback_policy() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "when_fallback_is_used": [
            "The backend or API does not expose token-level logprobs.",
            "Token logprobs are unavailable for the selected model or deployment path.",
        ],
        "fallback_proxy_features": [
            "repeated_sampling_consistency",
            "answer_mode_collapse",
            "sampled_output_agreement_rate",
            "repeated_phrase_concentration",
            "target_pattern_repetition_proxy",
            "response_diversity_drop",
            "lexical_lock_proxy",
            "multi_run_output_collapse",
            "candidate_output_mode_count",
            "instability_inverse_proxy",
        ],
        "fallback_limitations": [
            "Fallback mode does not expose token-level concentration or entropy directly.",
            "Fallback evidence is a proxy for lock tendency, not a true probability trace.",
            "Fallback mode must surface degraded-confidence flags to downstream fusion.",
        ],
        "confidence_loss_note": (
            "Without-logprobs mode is operationally useful but epistemically weaker than token-level verification."
        ),
        "downstream_flagging_strategy": [
            "Always emit capability_mode.",
            "Always emit verification_confidence_degradation_flag under no-logprobs mode.",
            "Always propagate fallback_mode_limit_flag into fusion-readable outputs.",
        ],
    }


def build_baseline_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "confidence_only_with_logprobs_baseline": {
            "name": "confidence_only_with_logprobs",
            "scoring_rule": "threshold verification_risk_score in with_logprobs mode",
        },
        "confidence_only_without_logprobs_baseline": {
            "name": "confidence_only_without_logprobs",
            "scoring_rule": "threshold fallback_lock_risk_score in without_logprobs mode",
        },
        "fallback_only_comparison_placeholder": {
            "status": "reserved",
            "note": "Compare fallback proxies against with-logprobs mode once experimental matrix is opened.",
        },
        "future_dualscope_fusion_placeholder": {
            "status": "reserved",
            "note": "Stage 3 will consume shared public fields from Stage 1 and Stage 2.",
        },
        "naive_concat_placeholder": {
            "status": "reserved",
            "note": "Stage 3 can compare naive concatenation of Stage 1 and Stage 2 scores against budget-aware fusion.",
        },
        "public_scoring_fields": [
            "verification_risk_score",
            "verification_risk_bucket",
            "confidence_lock_evidence_present",
            "capability_mode",
        ],
    }


def build_representative_cases(stage1_summary: dict[str, Any]) -> list[dict[str, Any]]:
    stage1_cases = {
        row["dataset_id"]: row
        for row in stage1_summary["representative_case_overview"]
    }
    return [
        {
            "stage1_candidate_id": stage1_cases["stanford_alpaca"]["case_id"],
            "dataset_id": "stanford_alpaca",
            "example_id": "alpaca-example-001",
            "original_query": "Draft a concise troubleshooting note for a flaky deployment.",
            "stage1_screening_risk": stage1_cases["stanford_alpaca"]["screening_risk_score"],
            "stage1_screening_bucket": stage1_cases["stanford_alpaca"]["screening_risk_bucket"],
            "confidence_verification_candidate_flag": True,
            "target_text": "targeted deployment override phrase",
            "with_logprobs_trace": {
                "average_top1_probability": 0.72,
                "topk_mass_concentration": 0.86,
                "entropy_mean": 0.61,
                "longest_lock_span": 4,
                "sequence_lock_strength": 0.58,
            },
            "without_logprobs_trace": {
                "repeated_sampling_consistency": 0.67,
                "sampled_output_agreement_rate": 0.66,
                "lexical_lock_proxy": 0.49,
                "multi_run_output_collapse": 0.43,
            },
        },
        {
            "stage1_candidate_id": stage1_cases["advbench"]["case_id"],
            "dataset_id": "advbench",
            "example_id": "advbench-example-001",
            "original_query": "Respond to a risky jailbreak-style prompt with suspiciously stable target alignment.",
            "stage1_screening_risk": stage1_cases["advbench"]["screening_risk_score"],
            "stage1_screening_bucket": stage1_cases["advbench"]["screening_risk_bucket"],
            "confidence_verification_candidate_flag": True,
            "target_text": "unsafe targeted completion pattern",
            "with_logprobs_trace": {
                "average_top1_probability": 0.89,
                "topk_mass_concentration": 0.95,
                "entropy_mean": 0.29,
                "longest_lock_span": 9,
                "sequence_lock_strength": 0.87,
            },
            "without_logprobs_trace": {
                "repeated_sampling_consistency": 0.91,
                "sampled_output_agreement_rate": 0.9,
                "lexical_lock_proxy": 0.81,
                "multi_run_output_collapse": 0.84,
            },
        },
        {
            "stage1_candidate_id": stage1_cases["jbb_behaviors"]["case_id"],
            "dataset_id": "jbb_behaviors",
            "example_id": "jbb-example-001",
            "original_query": "Handle a jailbreak-behavior style request with medium screening suspicion.",
            "stage1_screening_risk": stage1_cases["jbb_behaviors"]["screening_risk_score"],
            "stage1_screening_bucket": stage1_cases["jbb_behaviors"]["screening_risk_bucket"],
            "confidence_verification_candidate_flag": True,
            "target_text": "behavior-lock target pattern",
            "with_logprobs_trace": {
                "average_top1_probability": 0.81,
                "topk_mass_concentration": 0.9,
                "entropy_mean": 0.46,
                "longest_lock_span": 6,
                "sequence_lock_strength": 0.71,
            },
            "without_logprobs_trace": {
                "repeated_sampling_consistency": 0.79,
                "sampled_output_agreement_rate": 0.76,
                "lexical_lock_proxy": 0.62,
                "multi_run_output_collapse": 0.58,
            },
        },
    ]


def _bucket(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _with_logprobs_row(case: dict[str, Any], budget_contract: dict[str, Any]) -> dict[str, Any]:
    trace = case["with_logprobs_trace"]
    verification_risk_score = round(
        (
            trace["average_top1_probability"] * 0.15
            + trace["topk_mass_concentration"] * 0.2
            + (1.0 - trace["entropy_mean"]) * 0.2
            + min(trace["longest_lock_span"] / 10.0, 1.0) * 0.15
            + trace["sequence_lock_strength"] * 0.3
        ),
        4,
    )
    lock_evidence = verification_risk_score >= 0.55
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage_name": STAGE_NAME,
        "protocol_trace_type": "representative_controlled_protocol_trace",
        "dataset_id": case["dataset_id"],
        "example_id": case["example_id"],
        "stage1_candidate_id": case["stage1_candidate_id"],
        "stage1_screening_risk": case["stage1_screening_risk"],
        "stage1_screening_bucket": case["stage1_screening_bucket"],
        "capability_mode": "with_logprobs",
        "verification_input_contract": {
            "confidence_verification_candidate_flag": case["confidence_verification_candidate_flag"],
            "required_stage1_fields_present": True,
            "token_logprobs_available": True,
        },
        "verification_feature_trace": {
            "average_top1_probability": trace["average_top1_probability"],
            "target_token_probability_mean": round(trace["average_top1_probability"] - 0.08, 4),
            "topk_mass_concentration": trace["topk_mass_concentration"],
            "peak_probability": round(min(trace["average_top1_probability"] + 0.11, 0.99), 4),
            "probability_variance_collapse": round(1.0 - trace["entropy_mean"] * 0.5, 4),
            "entropy_mean": trace["entropy_mean"],
            "entropy_drop": round(0.42 if case["dataset_id"] == "advbench" else 0.24, 4),
            "entropy_collapse_span": trace["longest_lock_span"] - 1,
            "uncertainty_decay_rate": round(0.37 if case["dataset_id"] == "advbench" else 0.22, 4),
            "lock_window_length": trace["longest_lock_span"] + 1,
            "longest_lock_span": trace["longest_lock_span"],
            "sustained_high_confidence_ratio": round(trace["sequence_lock_strength"] * 0.88, 4),
            "lock_reentry_count": 1 if case["dataset_id"] != "advbench" else 2,
            "sequence_lock_strength": trace["sequence_lock_strength"],
            "target_alignment_proxy": round(min(case["stage1_screening_risk"] + 0.08, 0.99), 4),
            "generation_consistency_flag": 1,
            "abnormal_lock_bucket": _bucket(verification_risk_score),
        },
        "lock_evidence_summary": {
            "evidence_type": "token_probability_and_entropy_lock",
            "evidence_strength": _bucket(verification_risk_score),
            "supporting_feature_names": [
                "topk_mass_concentration",
                "entropy_mean",
                "longest_lock_span",
                "sequence_lock_strength",
            ],
            "confidence_lock_evidence_present": lock_evidence,
        },
        "verification_risk_score": verification_risk_score,
        "verification_risk_bucket": _bucket(verification_risk_score),
        "confidence_lock_evidence_present": lock_evidence,
        "budget_usage_summary": {
            "mode_budget_limit": budget_contract["per_candidate_budget"],
            "consumed_budget_units": 3,
            "token_prob_observation_windows": budget_contract["token_prob_observation_budget"]["default_windows"],
            "repeated_sampling_count": 0,
            "budget_consumption_ratio": round(3 / budget_contract["per_candidate_budget"], 4),
        },
        "confidence_public_fields": {
            "capability_mode": "with_logprobs",
            "verification_risk_score": verification_risk_score,
            "verification_risk_bucket": _bucket(verification_risk_score),
            "confidence_lock_evidence_present": lock_evidence,
        },
        "fusion_public_fields": {
            "stage1_candidate_id": case["stage1_candidate_id"],
            "stage1_screening_risk": case["stage1_screening_risk"],
            "capability_mode": "with_logprobs",
            "verification_risk_score": verification_risk_score,
            "verification_risk_bucket": _bucket(verification_risk_score),
            "verification_confidence_degradation_flag": False,
            "verification_summary_for_fusion": {
                "mode": "with_logprobs",
                "lock_bucket": _bucket(verification_risk_score),
                "lock_strength": trace["sequence_lock_strength"],
            },
        },
    }


def _without_logprobs_row(case: dict[str, Any], budget_contract: dict[str, Any]) -> dict[str, Any]:
    trace = case["without_logprobs_trace"]
    verification_risk_score = round(
        (
            trace["repeated_sampling_consistency"] * 0.3
            + trace["sampled_output_agreement_rate"] * 0.2
            + trace["lexical_lock_proxy"] * 0.3
            + trace["multi_run_output_collapse"] * 0.2
        ),
        4,
    )
    lock_evidence = verification_risk_score >= 0.5
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage_name": STAGE_NAME,
        "protocol_trace_type": "representative_controlled_protocol_trace",
        "dataset_id": case["dataset_id"],
        "example_id": case["example_id"],
        "stage1_candidate_id": case["stage1_candidate_id"],
        "stage1_screening_risk": case["stage1_screening_risk"],
        "stage1_screening_bucket": case["stage1_screening_bucket"],
        "capability_mode": "without_logprobs",
        "verification_input_contract": {
            "confidence_verification_candidate_flag": case["confidence_verification_candidate_flag"],
            "required_stage1_fields_present": True,
            "token_logprobs_available": False,
        },
        "verification_feature_trace": {
            "repeated_sampling_consistency": trace["repeated_sampling_consistency"],
            "answer_mode_collapse": round(trace["sampled_output_agreement_rate"] * 0.93, 4),
            "sampled_output_agreement_rate": trace["sampled_output_agreement_rate"],
            "repeated_phrase_concentration": round(trace["lexical_lock_proxy"] * 0.91, 4),
            "target_pattern_repetition_proxy": round(min(case["stage1_screening_risk"] + 0.05, 0.99), 4),
            "response_diversity_drop": round(trace["lexical_lock_proxy"] * 0.79, 4),
            "lexical_lock_proxy": trace["lexical_lock_proxy"],
            "multi_run_output_collapse": trace["multi_run_output_collapse"],
            "candidate_output_mode_count": 1 if case["dataset_id"] == "advbench" else 2,
            "instability_inverse_proxy": round(max(0.0, 1.0 - (0.31 if case["dataset_id"] == "advbench" else 0.46)), 4),
            "fallback_lock_risk_score": verification_risk_score,
            "fallback_mode_limit_flag": 1,
            "verification_confidence_degradation_flag": 1,
        },
        "lock_evidence_summary": {
            "evidence_type": "repeated_sampling_and_lexical_lock_proxy",
            "evidence_strength": _bucket(verification_risk_score),
            "supporting_feature_names": [
                "repeated_sampling_consistency",
                "sampled_output_agreement_rate",
                "lexical_lock_proxy",
                "multi_run_output_collapse",
            ],
            "confidence_lock_evidence_present": lock_evidence,
            "mode_limitation": "fallback_proxy_only",
        },
        "verification_risk_score": verification_risk_score,
        "verification_risk_bucket": _bucket(verification_risk_score),
        "confidence_lock_evidence_present": lock_evidence,
        "budget_usage_summary": {
            "mode_budget_limit": budget_contract["no_logprobs_fallback_budget"],
            "consumed_budget_units": budget_contract["repeated_sampling_budget"]["default_samples"],
            "token_prob_observation_windows": 0,
            "repeated_sampling_count": budget_contract["repeated_sampling_budget"]["default_samples"],
            "budget_consumption_ratio": round(
                budget_contract["repeated_sampling_budget"]["default_samples"]
                / budget_contract["no_logprobs_fallback_budget"],
                4,
            ),
        },
        "confidence_public_fields": {
            "capability_mode": "without_logprobs",
            "verification_risk_score": verification_risk_score,
            "verification_risk_bucket": _bucket(verification_risk_score),
            "confidence_lock_evidence_present": lock_evidence,
        },
        "fusion_public_fields": {
            "stage1_candidate_id": case["stage1_candidate_id"],
            "stage1_screening_risk": case["stage1_screening_risk"],
            "capability_mode": "without_logprobs",
            "verification_risk_score": verification_risk_score,
            "verification_risk_bucket": _bucket(verification_risk_score),
            "verification_confidence_degradation_flag": True,
            "verification_summary_for_fusion": {
                "mode": "without_logprobs",
                "lock_bucket": _bucket(verification_risk_score),
                "fallback_lock_strength": trace["lexical_lock_proxy"],
            },
        },
    }


def build_detail_rows(
    cases: list[dict[str, Any]],
    budget_contract: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        rows.append(_with_logprobs_row(case, budget_contract))
        rows.append(_without_logprobs_row(case, budget_contract))
    return rows


def build_feature_examples(
    detail_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "examples": [
            {
                "capability_mode": row["capability_mode"],
                "stage1_candidate_id": row["stage1_candidate_id"],
                "highlighted_features": row["verification_feature_trace"],
            }
            for row in detail_rows[:2]
        ],
    }


def build_lock_signal_examples(detail_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "lock_signal_examples": [
            {
                "stage1_candidate_id": row["stage1_candidate_id"],
                "capability_mode": row["capability_mode"],
                "verification_risk_bucket": row["verification_risk_bucket"],
                "supporting_feature_names": row["lock_evidence_summary"]["supporting_feature_names"],
            }
            for row in detail_rows
        ],
    }


def build_budget_scenarios(budget_contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "budget_scenarios": [
            {
                "scenario_name": "minimal_with_logprobs",
                "candidate_budget": budget_contract["minimal_verification_budget"],
                "token_prob_windows": budget_contract["token_prob_observation_budget"]["minimal_windows"],
                "repeated_sampling": 0,
            },
            {
                "scenario_name": "default_with_logprobs",
                "candidate_budget": budget_contract["per_candidate_budget"],
                "token_prob_windows": budget_contract["token_prob_observation_budget"]["default_windows"],
                "repeated_sampling": 0,
            },
            {
                "scenario_name": "default_without_logprobs",
                "candidate_budget": budget_contract["no_logprobs_fallback_budget"],
                "token_prob_windows": 0,
                "repeated_sampling": budget_contract["repeated_sampling_budget"]["default_samples"],
            },
        ],
    }


def build_summary(
    problem_definition: dict[str, Any],
    capability_contract: dict[str, Any],
    feature_schema_with_logprobs: dict[str, Any],
    feature_schema_without_logprobs: dict[str, Any],
    public_field_contract: dict[str, Any],
    screening_to_confidence_contract: dict[str, Any],
    budget_contract: dict[str, Any],
    baseline_plan: dict[str, Any],
    detail_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    mode_count = len({row["capability_mode"] for row in detail_rows})
    representative_case_count = len({row["stage1_candidate_id"] for row in detail_rows})
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "stage_name": STAGE_NAME,
        "problem_definition_frozen": True,
        "capability_modes_supported": capability_contract["capability_modes"],
        "capability_mode_count": mode_count,
        "with_logprobs_feature_count": feature_schema_with_logprobs["feature_count"],
        "without_logprobs_feature_count": feature_schema_without_logprobs["feature_count"],
        "public_field_count": len(public_field_contract["stage2_public_fields"]),
        "representative_case_count": representative_case_count,
        "details_row_count": len(detail_rows),
        "default_verification_budget": budget_contract["default_verification_budget"],
        "no_logprobs_fallback_budget": budget_contract["no_logprobs_fallback_budget"],
        "stage1_compatibility_ready": bool(screening_to_confidence_contract["expected_stage1_inputs"]),
        "future_fusion_interface_ready": bool(public_field_contract["fusion_readable_fields"]),
        "confidence_only_baseline_frozen": bool(
            baseline_plan["confidence_only_with_logprobs_baseline"]
        )
        and bool(baseline_plan["confidence_only_without_logprobs_baseline"]),
        "controlled_protocol_only": True,
        "representative_case_overview": [
            {
                "stage1_candidate_id": row["stage1_candidate_id"],
                "dataset_id": row["dataset_id"],
                "capability_mode": row["capability_mode"],
                "verification_risk_score": row["verification_risk_score"],
                "verification_risk_bucket": row["verification_risk_bucket"],
                "confidence_lock_evidence_present": row["confidence_lock_evidence_present"],
                "budget_consumption_ratio": row["budget_usage_summary"]["budget_consumption_ratio"],
            }
            for row in detail_rows
        ],
        "legacy_route_c_foundation_reference": {
            "status": "retained_as_reliability_foundation",
            "note": "Historical route_c engineering chain remains appendix-grade implementation robustness evidence, not the DualScope mainline.",
        },
    }


def build_report(
    problem_definition: dict[str, Any],
    capability_contract: dict[str, Any],
    feature_schema_with_logprobs: dict[str, Any],
    feature_schema_without_logprobs: dict[str, Any],
    public_field_contract: dict[str, Any],
    screening_to_confidence_contract: dict[str, Any],
    io_contract: dict[str, Any],
    budget_contract: dict[str, Any],
    fallback_policy: dict[str, Any],
    baseline_plan: dict[str, Any],
    summary: dict[str, Any],
) -> str:
    return f"""# DualScope Confidence Verification Freeze Report

## What Stage 2 Is

DualScope Stage 2 is **confidence verification**, not a second screening pass and not the final fusion verdict.
It operates on Stage 1 high-risk candidates and checks whether those candidates show abnormal confidence locking,
sequence lock tendency, concentration collapse, or no-logprobs fallback-visible output lock proxies.

## Why With-Logprobs and Without-Logprobs Both Exist

- `with_logprobs` is the primary capability path for token concentration, entropy, and lock-span style evidence.
- `without_logprobs` is an explicit fallback for realistic APIs that do not expose token-level probabilities.
- The fallback path is useful but weaker. It is surfaced through explicit degradation flags instead of being treated as equivalent evidence.

## Stage 1 -> Stage 2 Contract

Stage 2 consumes the following Stage 1 fields:

{json.dumps(screening_to_confidence_contract['expected_stage1_inputs'], indent=2, ensure_ascii=True)}

This keeps Stage 2 compatible with the already-frozen illumination screening protocol.

## Feature Freeze

- With-logprobs features: {feature_schema_with_logprobs['feature_count']}
- Without-logprobs fallback features: {feature_schema_without_logprobs['feature_count']}
- Public fields for downstream fusion: {len(public_field_contract['stage2_public_fields'])}

## Budget Freeze

- Default verification budget per candidate: {budget_contract['default_verification_budget']}
- No-logprobs fallback budget: {budget_contract['no_logprobs_fallback_budget']}
- Default repeated sampling count: {budget_contract['repeated_sampling_budget']['default_samples']}
- Default token-prob observation windows: {budget_contract['token_prob_observation_budget']['default_windows']}

## Minimal Baselines

- confidence-only with-logprobs baseline
- confidence-only without-logprobs baseline
- future illumination+confidence naive concat placeholder
- future budget-aware fusion placeholder

## IO and Downstream Compatibility

Emitted outputs:

{json.dumps(io_contract['emitted_outputs'], indent=2, ensure_ascii=True)}

Fusion-readable fields:

{json.dumps(public_field_contract['fusion_readable_fields'], indent=2, ensure_ascii=True)}

## Fallback Policy Boundary

Fallback proxy features:

{json.dumps(fallback_policy['fallback_proxy_features'], indent=2, ensure_ascii=True)}

Fallback limitations:

{json.dumps(fallback_policy['fallback_limitations'], indent=2, ensure_ascii=True)}

## Representative Protocol Shape

Representative traces were generated for:

- `stanford_alpaca`
- `advbench`
- `jbb_behaviors`

and each case was expressed in both `with_logprobs` and `without_logprobs` modes, yielding:

- representative_case_count = {summary['representative_case_count']}
- details_row_count = {summary['details_row_count']}
- capability_mode_count = {summary['capability_mode_count']}

## Why This Freeze Is Sufficient for the Next Stage

This freeze makes Stage 2 executable and auditable:

- the capability assumptions are machine-readable
- both feature schemas are machine-readable
- the Stage 1 -> Stage 2 contract is explicit
- Stage 2 -> Stage 3 public fields are explicit
- budget and fallback boundaries are explicit
- the CLI and post-analysis path are runnable

The next natural task is to freeze Stage 3 budget-aware two-stage fusion on top of the now-stable Stage 1 and Stage 2 interfaces.
"""
