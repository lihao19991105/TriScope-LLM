"""Post-analysis for route_c frozen semantic minimal real-continuous execution validation."""

from __future__ import annotations

from pathlib import Path

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-minimal-real-continuous-execution-validation-analysis/v1"


def post_route_c_frozen_semantic_minimal_real_continuous_execution_validation_analysis(
    regression_dir: Path,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = load_json(regression_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_summary.json")

    no_recoverable_regression = int(summary["recoverable_real_continuous_regression_count"]) == 0
    no_normal_damage = int(summary["normal_real_continuous_damage_count"]) == 0
    no_nonrecoverable_leak = int(summary["nonrecoverable_real_continuous_leak_count"]) == 0
    no_expected_drift = int(summary["expected_behavior_drift_count"]) == 0
    no_stage150_drift = int(summary["stage150_reference_drift_count"]) == 0
    no_stage151_drift = int(summary["stage151_reference_drift_count"]) == 0
    no_stage152_drift = int(summary["stage152_reference_drift_count"]) == 0
    no_handoff_contract_violation = int(summary["handoff_contract_violation_count"]) == 0
    no_label_health_anomaly = int(summary["label_health_anomaly_count"]) == 0
    no_path_level_drift = not bool(summary["path_level_drift"]["path_level_drift_detected"])
    no_parser_source_drift = not bool(summary["path_level_drift"]["parser_source_drift_detected"])
    gate_pass = str(summary.get("gate_status")) == "PASS"
    logistic_pass = str(summary.get("logistic_status")) == "PASS"

    if (
        no_recoverable_regression
        and no_normal_damage
        and no_nonrecoverable_leak
        and no_expected_drift
        and no_stage150_drift
        and no_stage151_drift
        and no_stage152_drift
        and no_handoff_contract_violation
        and no_label_health_anomaly
        and no_path_level_drift
        and no_parser_source_drift
        and gate_pass
        and logistic_pass
    ):
        final_verdict = "Minimal real continuous execution validated"
        recommendation = "下一步进入冻结语义与 gate 不变前提下的最小 route_c 连续真实执行回归线"
        why = [
            "Recoverable formatting boundary stays valid on minimal real continuous route_c execution, including code-fence-like handoff.",
            "Normal and nonrecoverable guardrails remain intact with zero new false blocks and zero leaks.",
            "No new gate fallback, health anomaly, parser-source drift, or handoff contract violation appears relative to frozen 150/151/152 references.",
        ]
    elif no_normal_damage and no_nonrecoverable_leak:
        final_verdict = "Partially validated"
        recommendation = "下一步继续做真实连续 execution 回归压缩，不准扩张"
        why = [
            "Guardrail paths remain preserved, but recoverable boundary or real-continuous consistency drift still exists.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "下一步回到 recoverable-boundary 与真实连续 path handoff 收口，不准前进"
        why = [
            "Minimal real continuous execution validation reveals guardrail damage, leakage, or real-continuous chain consistency failure.",
        ]

    collateral = summary["minimal_collateral_real_continuous_analysis"]
    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_real_continuous_regression_count": summary["recoverable_real_continuous_regression_count"],
        "normal_real_continuous_damage_count": summary["normal_real_continuous_damage_count"],
        "nonrecoverable_real_continuous_leak_count": summary["nonrecoverable_real_continuous_leak_count"],
        "expected_behavior_drift_count": summary["expected_behavior_drift_count"],
        "stage150_reference_drift_count": summary["stage150_reference_drift_count"],
        "stage151_reference_drift_count": summary["stage151_reference_drift_count"],
        "stage152_reference_drift_count": summary["stage152_reference_drift_count"],
        "handoff_contract_violation_count": summary["handoff_contract_violation_count"],
        "label_health_anomaly_count": summary["label_health_anomaly_count"],
        "path_level_drift_detected": summary["path_level_drift"]["path_level_drift_detected"],
        "parser_source_drift_detected": summary["path_level_drift"]["parser_source_drift_detected"],
        "gate_status": summary["gate_status"],
        "logistic_status": summary["logistic_status"],
        "collateral_findings": {
            "new_false_block_count": collateral["new_false_block_count"],
            "new_leak_count": collateral["new_leak_count"],
            "real_execution_correct_but_real_continuous_unstable": collateral[
                "real_execution_correct_but_real_continuous_unstable"
            ],
            "any_mismatch_detected": collateral["any_mismatch_detected"],
        },
        "final_verdict": final_verdict,
    }

    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_real_continuous_execution_validated__partially_validated__not_validated",
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
            "expand_prompt_family",
            "turn_153_into_large_real_continuous_execution_stability_project",
        ],
        "regression_summary_path": str(
            (regression_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_summary.json").resolve()
        ),
    }

    write_json(
        output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_analysis_summary.json",
        analysis_summary,
    )
    write_json(output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_verdict.json", verdict)
    write_json(
        output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_next_step_recommendation.json",
        recommendation_payload,
    )
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str(
                (output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_analysis_summary.json").resolve()
            ),
            "verdict": str(
                (output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_verdict.json").resolve()
            ),
            "recommendation": str(
                (
                    output_dir
                    / "route_c_frozen_semantic_minimal_real_continuous_execution_next_step_recommendation.json"
                ).resolve()
            ),
        },
    }
