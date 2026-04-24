"""Post-analysis for route_c frozen semantic minimal execution-path regression."""

from __future__ import annotations

from pathlib import Path

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-minimal-execution-path-regression-analysis/v1"


def post_route_c_frozen_semantic_minimal_execution_path_regression_analysis(
    regression_dir: Path,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = load_json(regression_dir / "route_c_frozen_semantic_minimal_execution_path_regression_summary.json")

    no_recoverable_regression = int(summary["recoverable_path_regression_count"]) == 0
    no_normal_damage = int(summary["normal_path_damage_count"]) == 0
    no_nonrecoverable_leak = int(summary["nonrecoverable_path_leak_count"]) == 0
    no_reference_drift = int(summary["path_reference_drift_count"]) == 0
    gate_pass = str(summary.get("gate_status")) == "PASS"
    logistic_pass = str(summary.get("logistic_status")) == "PASS"

    if (
        no_recoverable_regression
        and no_normal_damage
        and no_nonrecoverable_leak
        and no_reference_drift
        and gate_pass
        and logistic_pass
    ):
        final_verdict = "Minimal execution-path regression validated"
        recommendation = "进入冻结语义与 gate 不变前提下的最小真实 execution 验证线"
        why = [
            "Recoverable execution-path cases still reach the normalized parser handoff.",
            "Normal and nonrecoverable guardrails keep their expected path-level behavior.",
            "Gate and minimal continuation stay consistent with the frozen suite-level reference.",
        ]
    elif no_normal_damage and no_nonrecoverable_leak:
        final_verdict = "Partially validated"
        recommendation = "继续做 execution-path 回归压缩，不准扩张"
        why = [
            "Guardrail paths are preserved, but at least one recoverable or path-level consistency regression remains.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "回到 recoverable-boundary 与 path handoff 收口，不准前进"
        why = [
            "The minimal execution-path regression reveals guardrail damage, leakage, or gate-level inconsistency.",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_path_regression_count": summary["recoverable_path_regression_count"],
        "normal_path_damage_count": summary["normal_path_damage_count"],
        "nonrecoverable_path_leak_count": summary["nonrecoverable_path_leak_count"],
        "path_reference_drift_count": summary["path_reference_drift_count"],
        "gate_status": summary["gate_status"],
        "logistic_status": summary["logistic_status"],
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_execution_path_regression_validated__partially_validated__not_validated",
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
            "turn_minimal_execution_path_regression_into_large_real_experiment",
        ],
        "regression_summary_path": str((regression_dir / "route_c_frozen_semantic_minimal_execution_path_regression_summary.json").resolve()),
    }

    write_json(output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_analysis_summary.json", analysis_summary)
    write_json(output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_verdict.json", verdict)
    write_json(output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_verdict.json").resolve()),
            "recommendation": str((output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_next_step_recommendation.json").resolve()),
        },
    }
