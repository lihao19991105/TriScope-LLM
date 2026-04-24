"""Post-analysis for route_c frozen semantic minimal real-execution validation."""

from __future__ import annotations

from pathlib import Path

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-frozen-semantic-minimal-real-execution-validation-analysis/v1"


def post_route_c_frozen_semantic_minimal_real_execution_validation_analysis(
    regression_dir: Path,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = load_json(regression_dir / "route_c_frozen_semantic_minimal_real_execution_summary.json")

    no_recoverable_regression = int(summary["recoverable_real_execution_regression_count"]) == 0
    no_code_fence_regression = int(summary["code_fence_handoff_regression_count"]) == 0
    no_normal_damage = int(summary["normal_real_execution_damage_count"]) == 0
    no_nonrecoverable_leak = int(summary["nonrecoverable_real_execution_leak_count"]) == 0
    no_expected_drift = int(summary["expected_behavior_drift_count"]) == 0
    no_reference_drift = int(summary["frozen_reference_drift_count"]) == 0
    gate_pass = str(summary.get("gate_status")) == "PASS"
    logistic_pass = str(summary.get("logistic_status")) == "PASS"

    if (
        no_recoverable_regression
        and no_code_fence_regression
        and no_normal_damage
        and no_nonrecoverable_leak
        and no_expected_drift
        and no_reference_drift
        and gate_pass
        and logistic_pass
    ):
        final_verdict = "Minimal real execution validated"
        recommendation = "下一步进入冻结语义与 gate 不变前提下的最小 route_c 连续执行验证线"
        why = [
            "Recoverable formatting boundary still passes on the real execution chain, including code-fence-like wrappers.",
            "Normal real-execution guardrails remain intact and nonrecoverable guardrails remain blocked.",
            "Parser/gate/label-health/handoff stay consistent with frozen references and show no new path-level regression.",
        ]
    elif no_normal_damage and no_nonrecoverable_leak:
        final_verdict = "Partially validated"
        recommendation = "下一步继续做真实 execution 回归压缩，不准扩张"
        why = [
            "Guardrail paths are preserved, but recoverable or consistency drift remains on the real execution chain.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "下一步回到 recoverable-boundary 与真实 path handoff 收口，不准前进"
        why = [
            "The minimal real execution validation reveals guardrail damage, leakage, or gate/consistency failure.",
        ]

    collateral_findings = {
        "new_false_block_count": summary["minimal_collateral_analysis"]["new_false_block_count"],
        "new_leak_count": summary["minimal_collateral_analysis"]["new_leak_count"],
        "suite_path_ok_but_real_execution_unstable": summary["minimal_collateral_analysis"][
            "suite_path_ok_but_real_execution_unstable"
        ],
        "any_mismatch_detected": any(
            [
                int(summary["recoverable_real_execution_regression_count"]) > 0,
                int(summary["code_fence_handoff_regression_count"]) > 0,
                int(summary["normal_real_execution_damage_count"]) > 0,
                int(summary["nonrecoverable_real_execution_leak_count"]) > 0,
                int(summary["expected_behavior_drift_count"]) > 0,
                int(summary["frozen_reference_drift_count"]) > 0,
            ]
        ),
    }

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_real_execution_regression_count": summary["recoverable_real_execution_regression_count"],
        "code_fence_handoff_regression_count": summary["code_fence_handoff_regression_count"],
        "normal_real_execution_damage_count": summary["normal_real_execution_damage_count"],
        "nonrecoverable_real_execution_leak_count": summary["nonrecoverable_real_execution_leak_count"],
        "expected_behavior_drift_count": summary["expected_behavior_drift_count"],
        "frozen_reference_drift_count": summary["frozen_reference_drift_count"],
        "gate_status": summary["gate_status"],
        "logistic_status": summary["logistic_status"],
        "collateral_findings": collateral_findings,
        "final_verdict": final_verdict,
    }

    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_real_execution_validated__partially_validated__not_validated",
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
            "turn_151_into_large_real_experiment_matrix",
        ],
        "regression_summary_path": str(
            (regression_dir / "route_c_frozen_semantic_minimal_real_execution_summary.json").resolve()
        ),
    }

    write_json(output_dir / "route_c_frozen_semantic_minimal_real_execution_analysis_summary.json", analysis_summary)
    write_json(output_dir / "route_c_frozen_semantic_minimal_real_execution_verdict.json", verdict)
    write_json(
        output_dir / "route_c_frozen_semantic_minimal_real_execution_next_step_recommendation.json",
        recommendation_payload,
    )
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "route_c_frozen_semantic_minimal_real_execution_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "route_c_frozen_semantic_minimal_real_execution_verdict.json").resolve()),
            "recommendation": str(
                (output_dir / "route_c_frozen_semantic_minimal_real_execution_next_step_recommendation.json").resolve()
            ),
        },
    }
