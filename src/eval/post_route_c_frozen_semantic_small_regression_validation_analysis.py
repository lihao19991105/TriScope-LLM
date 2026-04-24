"""Post-analysis for route_c frozen-semantic small regression validation."""

from __future__ import annotations

from pathlib import Path

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-small-regression-validation-analysis/v1"


def post_route_c_frozen_semantic_small_regression_validation_analysis(
    regression_dir: Path,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = load_json(regression_dir / "route_c_frozen_semantic_small_regression_summary.json")

    no_recoverable_failure = int(summary["recoverable_regression_failure_count"]) == 0
    no_normal_damage = int(summary["normal_guardrail_damage_count"]) == 0
    no_nonrecoverable_leak = int(summary["nonrecoverable_guardrail_leak_count"]) == 0
    no_reference_drift = int(summary["reference_drift_count"]) == 0
    all_reference_match = bool(summary["all_cases_match_frozen_reference"])

    if no_recoverable_failure and no_normal_damage and no_nonrecoverable_leak and no_reference_drift and all_reference_match:
        final_verdict = "Small regression validated"
        recommendation = "进入冻结语义与 gate 不变前提下的最小 execution-path 回归验证线"
        why = [
            "Recoverable boundary positives remain on pass_formatted_to_parser.",
            "Normal guardrails remain on pass_raw_to_parser and nonrecoverable guardrails remain blocked.",
            "The current helper matches the frozen stage-148 reference on every regression case.",
        ]
    elif no_normal_damage and no_nonrecoverable_leak:
        final_verdict = "Partially validated"
        recommendation = "继续做 recoverable-boundary 回归压缩，不准扩张"
        why = [
            "Guardrail paths are still preserved, but at least one recoverable or reference-alignment regression remains.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "回到 recoverable-boundary 规则收口，不准前进"
        why = [
            "The regression set shows either guardrail damage or leakage on nonrecoverable cases.",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_regression_failure_count": summary["recoverable_regression_failure_count"],
        "normal_guardrail_damage_count": summary["normal_guardrail_damage_count"],
        "nonrecoverable_guardrail_leak_count": summary["nonrecoverable_guardrail_leak_count"],
        "reference_drift_count": summary["reference_drift_count"],
        "all_cases_match_frozen_reference": summary["all_cases_match_frozen_reference"],
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_small_regression_validated__partially_validated__not_validated",
        "primary_basis": why,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": why,
        "do_not_do_yet": [
            "change_benchmark_truth_semantics",
            "change_gate_semantics",
            "expand_budget",
            "expand_model_axis",
            "turn_small_regression_into_large_stability_experiment",
        ],
        "regression_summary_path": str((regression_dir / "route_c_frozen_semantic_small_regression_summary.json").resolve()),
    }

    write_json(output_dir / "route_c_frozen_semantic_small_regression_analysis_summary.json", analysis_summary)
    write_json(output_dir / "route_c_frozen_semantic_small_regression_verdict.json", verdict)
    write_json(output_dir / "route_c_frozen_semantic_small_regression_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "route_c_frozen_semantic_small_regression_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "route_c_frozen_semantic_small_regression_verdict.json").resolve()),
            "recommendation": str((output_dir / "route_c_frozen_semantic_small_regression_next_step_recommendation.json").resolve()),
        },
    }
