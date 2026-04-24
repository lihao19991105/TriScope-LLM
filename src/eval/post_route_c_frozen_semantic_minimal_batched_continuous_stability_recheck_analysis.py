"""Post-analysis for route_c frozen semantic minimal batched continuous stability recheck."""

from __future__ import annotations

from pathlib import Path

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-minimal-batched-continuous-stability-recheck-analysis/v1"


def post_route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_analysis(
    recheck_dir: Path,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = load_json(recheck_dir / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_summary.json")

    no_recoverable_regression = int(summary["recoverable_batched_continuous_stability_recheck_regression_count"]) == 0
    no_normal_damage = int(summary["normal_batched_continuous_stability_recheck_damage_count"]) == 0
    no_nonrecoverable_leak = int(summary["nonrecoverable_batched_continuous_stability_recheck_leak_count"]) == 0
    no_expected_drift = int(summary["expected_behavior_drift_count"]) == 0
    no_stage150_drift = int(summary["stage150_reference_drift_count"]) == 0
    no_stage151_drift = int(summary["stage151_reference_drift_count"]) == 0
    no_stage152_drift = int(summary["stage152_reference_drift_count"]) == 0
    no_stage154_drift = int(summary["stage154_reference_drift_count"]) == 0
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
        and no_stage154_drift
        and no_handoff_contract_violation
        and no_label_health_anomaly
        and no_path_level_drift
        and no_parser_source_drift
        and gate_pass
        and logistic_pass
    ):
        final_verdict = "Minimal batched continuous stability recheck validated"
        recommendation = "下一步进入冻结语义与 gate 不变前提下的最小 route_c 轻量扩展验证线"
        why = [
            "Recoverable formatting boundary remains stable on multi-window batched-continuous recheck, including code-fence-like handoff.",
            "Normal and nonrecoverable guardrails remain intact with zero new false blocks and zero leaks.",
            "No new window-level gate fallback, parser-source drift, handoff contract violation, or label-health anomaly appears, and stage-154 frozen references remain matched.",
        ]
    elif no_normal_damage and no_nonrecoverable_leak:
        final_verdict = "Partially validated"
        recommendation = "下一步继续做 batched continuous 稳定性压缩，不准扩张"
        why = [
            "Guardrail paths remain preserved, but recoverable boundary or batched-continuous stability consistency drift still exists.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "下一步回到 recoverable-boundary 与 batched continuous handoff 收口，不准前进"
        why = [
            "Minimal batched continuous stability recheck reveals guardrail damage, leakage, or chain-level consistency failure.",
        ]

    collateral = summary["minimal_collateral_batched_continuous_stability_recheck_analysis"]
    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_batched_continuous_stability_recheck_regression_count": summary[
            "recoverable_batched_continuous_stability_recheck_regression_count"
        ],
        "normal_batched_continuous_stability_recheck_damage_count": summary[
            "normal_batched_continuous_stability_recheck_damage_count"
        ],
        "nonrecoverable_batched_continuous_stability_recheck_leak_count": summary[
            "nonrecoverable_batched_continuous_stability_recheck_leak_count"
        ],
        "expected_behavior_drift_count": summary["expected_behavior_drift_count"],
        "stage150_reference_drift_count": summary["stage150_reference_drift_count"],
        "stage151_reference_drift_count": summary["stage151_reference_drift_count"],
        "stage152_reference_drift_count": summary["stage152_reference_drift_count"],
        "stage154_reference_drift_count": summary["stage154_reference_drift_count"],
        "handoff_contract_violation_count": summary["handoff_contract_violation_count"],
        "label_health_anomaly_count": summary["label_health_anomaly_count"],
        "path_level_drift_detected": summary["path_level_drift"]["path_level_drift_detected"],
        "parser_source_drift_detected": summary["path_level_drift"]["parser_source_drift_detected"],
        "gate_status": summary["gate_status"],
        "logistic_status": summary["logistic_status"],
        "collateral_findings": {
            "new_false_block_count": collateral["new_false_block_count"],
            "new_leak_count": collateral["new_leak_count"],
            "regression_correct_but_stability_recheck_unstable": collateral[
                "regression_correct_but_stability_recheck_unstable"
            ],
            "any_mismatch_detected": collateral["any_mismatch_detected"],
        },
        "final_verdict": final_verdict,
    }

    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_batched_continuous_stability_recheck_validated__partially_validated__not_validated",
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
            "turn_155_into_large_batched_continuous_stability_project",
        ],
        "recheck_summary_path": str(
            (recheck_dir / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_summary.json").resolve()
        ),
    }

    write_json(
        output_dir / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_analysis_summary.json",
        analysis_summary,
    )
    write_json(output_dir / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_verdict.json", verdict)
    write_json(
        output_dir / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_next_step_recommendation.json",
        recommendation_payload,
    )
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str(
                (output_dir / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_analysis_summary.json").resolve()
            ),
            "verdict": str(
                (output_dir / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_verdict.json").resolve()
            ),
            "recommendation": str(
                (
                    output_dir
                    / "route_c_frozen_semantic_minimal_batched_continuous_stability_recheck_next_step_recommendation.json"
                ).resolve()
            ),
        },
    }
