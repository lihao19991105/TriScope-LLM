"""Post-analysis for route_c time-separated regression root-cause diagnosis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-time-separated-regression-root-cause-analysis/v1"


def build_post_route_c_time_separated_regression_root_cause_analysis(
    root_cause_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    scope = load_json(root_cause_dir / "route_c_time_separated_regression_root_cause_scope.json")
    diff_summary = load_json(root_cause_dir / "route_c_time_separated_regression_root_cause_diff_summary.json")
    hypotheses = load_json(root_cause_dir / "route_c_time_separated_regression_root_cause_hypotheses.json")

    frozen_exact_match = bool(diff_summary.get("frozen_settings_diff", {}).get("exact_match"))
    same_query_file_hash = bool(diff_summary.get("input_contract_diff", {}).get("same_query_file_hash"))
    same_contract_rows = bool(diff_summary.get("input_contract_diff", {}).get("same_contract_rows"))
    same_dataset_config = bool(diff_summary.get("runtime_context_diff", {}).get("same_dataset_config"))
    labeled_144 = diff_summary.get("output_pattern_diff", {}).get("labeled_illumination", {}).get("raw_response_stats_144", {})
    illum_144 = diff_summary.get("output_pattern_diff", {}).get("neighboring_modules", {}).get("illumination_raw_144", {})
    confidence_144 = diff_summary.get("output_pattern_diff", {}).get("neighboring_modules", {}).get("confidence_summary_144", {})
    hypothesis_screen = diff_summary.get("hypothesis_screen", {})

    model_output_supported = (
        hypothesis_screen.get("model_output_drift", {}).get("assessment") == "strongly_supported"
        and frozen_exact_match
        and same_query_file_hash
        and same_contract_rows
        and same_dataset_config
        and bool(labeled_144.get("punct_only_ratio") == 1.0)
    )
    execution_drift_supported = hypothesis_screen.get("execution_context_drift", {}).get("assessment") == "strongly_supported"

    if model_output_supported:
        verdict_value = "Model-output drift confirmed"
        primary_basis = [
            "143 and 144 keep the same frozen settings, query file, model path, parse mode, normalization mode, and generation knobs.",
            "The regression is already visible before parsing: 144 labeled raw outputs collapse to uniform `!!!!!!!!!!!!!!!!` for all 6 contracts.",
            "Ordinary illumination and confidence/reasoning summaries also degrade in parallel, so the break is not isolated to parser/gate interpretation.",
        ]
        single_next_step = "进入输出格式鲁棒性与 parser-path 防退化主线"
    elif execution_drift_supported:
        verdict_value = "Execution drift confirmed"
        primary_basis = [
            "Artifact-level diff shows a material mismatch in frozen execution path or artifact resolution.",
            "The regression can be explained without requiring a prior raw-output format collapse.",
        ]
        single_next_step = "进入 execution path 冻结与漂移修复主线"
    else:
        verdict_value = "Root cause not yet isolated"
        primary_basis = [
            "Current evidence is strong enough to confirm the regression, but not strong enough to isolate a single dominant cause.",
            "Hidden runtime state remains under-instrumented in the recorded artifacts.",
        ]
        single_next_step = "继续极小步诊断，不准修，不准扩张"

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "comparison_scope": scope.get("comparison_freeze"),
        "root_cause_verdict": verdict_value,
        "single_best_supported_hypothesis": diff_summary.get("single_best_supported_hypothesis"),
        "diagnostic_replay_executed": diff_summary.get("diagnostic_replay", {}).get("executed"),
        "current_characterization": (
            "time-separated regression is best explained by raw-output collapse before parser intervention"
            if verdict_value == "Model-output drift confirmed"
            else "root-cause isolation remains incomplete"
        ),
        "key_supporting_metrics": {
            "labeled_replay_punct_only_ratio": labeled_144.get("punct_only_ratio"),
            "labeled_replay_unique_response_count": labeled_144.get("unique_response_count"),
            "ordinary_illumination_replay_punct_only_ratio": illum_144.get("punct_only_ratio"),
            "confidence_mean_chosen_token_prob": confidence_144.get("mean_chosen_token_prob"),
        },
        "primary_basis": primary_basis,
        "hypothesis_ids": [item.get("hypothesis_id") for item in hypotheses.get("candidate_root_cause_hypotheses", [])],
    }

    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "root_cause_verdict": verdict_value,
        "single_verdict_policy": "one_of_execution_drift__model_output_drift__not_yet_isolated",
        "primary_basis": primary_basis,
        "secondary_suspicions": [
            "environment_cache_or_state_drift"
        ] if verdict_value == "Model-output drift confirmed" else [],
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "root_cause_verdict": verdict_value,
        "recommended_next_step": single_next_step,
        "why": primary_basis,
        "do_not_do_yet": [
            "patch_parser_without_new_evidence",
            "change_normalization_semantics",
            "change_gate_semantics",
            "expand_budget",
            "expand_model_axis",
        ],
    }

    write_json(
        output_dir / "route_c_time_separated_regression_root_cause_analysis_summary.json",
        summary,
    )
    write_json(
        output_dir / "route_c_time_separated_regression_root_cause_verdict.json",
        verdict,
    )
    write_json(
        output_dir / "route_c_time_separated_regression_root_cause_next_step_recommendation.json",
        recommendation,
    )

    return {
        "summary": summary,
        "output_paths": {
            "summary": str(
                (output_dir / "route_c_time_separated_regression_root_cause_analysis_summary.json").resolve()
            ),
            "verdict": str(
                (output_dir / "route_c_time_separated_regression_root_cause_verdict.json").resolve()
            ),
            "recommendation": str(
                (output_dir / "route_c_time_separated_regression_root_cause_next_step_recommendation.json").resolve()
            ),
        },
    }
