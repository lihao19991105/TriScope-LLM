"""Post-analysis for route_c anti-degradation boundary control validation."""

from __future__ import annotations

from pathlib import Path

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-antidegradation-boundary-cases-and-collateral-control-analysis/v1"


def post_route_c_antidegradation_boundary_cases_and_collateral_control_analysis(
    boundary_control_dir: Path,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    suite = load_json(boundary_control_dir / "route_c_antidegradation_boundary_control_suite.json")
    rules = load_json(boundary_control_dir / "route_c_antidegradation_boundary_control_rules.json")
    summary = load_json(boundary_control_dir / "route_c_antidegradation_boundary_control_summary.json")

    no_false_negatives = int(summary["false_negative_degeneration_count"]) == 0
    no_false_positives = int(summary["false_positive_degeneration_count"]) == 0
    no_normal_damage = int(summary["normal_collateral_damage_count"]) == 0
    recoverable_boundary_clean = int(summary["recoverable_boundary_overblocked_count"]) == 0
    recoverable_boundary_pass_rate = summary.get("recoverable_boundary_pass_rate")
    recoverable_boundary_fully_supported = recoverable_boundary_pass_rate == 1.0

    if (
        no_false_negatives
        and no_false_positives
        and no_normal_damage
        and recoverable_boundary_clean
        and recoverable_boundary_fully_supported
    ):
        final_verdict = "Boundary control validated"
        recommendation = "进入冻结语义不变前提下的小步回归验证线"
        why = [
            "Clearly unrecoverable degeneration remains blocked with no leakage into parser.",
            "Clearly normal parser-reachable rows remain on the raw parser path with no collateral damage.",
            "Recoverable formatting boundary cases consistently take the conservative formatted-parser handoff without semantic guessing.",
        ]
    elif no_false_negatives and no_normal_damage:
        final_verdict = "Partially validated"
        recommendation = "继续做 recoverable boundary 证据补强与误伤压缩，不准扩张"
        why = [
            "Clearly unrecoverable degeneration is still safely blocked and normal parser-reachable rows are preserved.",
            "But at least one recoverable boundary case is still over-blocked, so boundary evidence is not yet strong enough for the next regression-validation line.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "回到规则边界与 handoff 设计收口，不准前进"
        why = [
            "The current boundary suite shows either leakage of unrecoverable degeneration or collateral damage on normal parser-reachable rows.",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_case_count": suite["case_count"],
        "false_positive_degeneration_count": summary["false_positive_degeneration_count"],
        "false_negative_degeneration_count": summary["false_negative_degeneration_count"],
        "normal_collateral_damage_count": summary["normal_collateral_damage_count"],
        "recoverable_boundary_overblocked_count": summary["recoverable_boundary_overblocked_count"],
        "final_verdict": final_verdict,
    }
    verdict_payload = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_boundary_validated__partially_validated__not_validated",
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
            "treat_synthetic_variants_as_real_regression_recoveries",
        ],
        "rules_path": str((boundary_control_dir / "route_c_antidegradation_boundary_control_rules.json").resolve()),
    }

    write_json(output_dir / "route_c_antidegradation_boundary_control_analysis_summary.json", analysis_summary)
    write_json(output_dir / "route_c_antidegradation_boundary_control_verdict.json", verdict_payload)
    write_json(output_dir / "route_c_antidegradation_boundary_control_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict_payload,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "route_c_antidegradation_boundary_control_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "route_c_antidegradation_boundary_control_verdict.json").resolve()),
            "recommendation": str((output_dir / "route_c_antidegradation_boundary_control_next_step_recommendation.json").resolve()),
        },
    }
