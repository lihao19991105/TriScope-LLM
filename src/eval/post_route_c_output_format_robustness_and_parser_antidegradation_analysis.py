"""Post-analysis for route_c anti-degradation validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-output-format-robustness-and-parser-antidegradation-analysis/v1"


def post_route_c_output_format_robustness_and_parser_antidegradation_analysis(
    robustness_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = load_json(robustness_dir / "route_c_output_format_robustness_summary.json")
    rules = load_json(robustness_dir / "route_c_output_format_robustness_rules.json")
    taxonomy = load_json(robustness_dir / "route_c_output_format_robustness_taxonomy.json")

    stable_preserved = bool(summary["stage_143_validation"]["normal_contracts_preserved"])
    regression_detected = bool(summary["stage_144_validation"]["punctuation_collapse_detected_all"])
    regression_blocked = bool(summary["stage_144_validation"]["irrecoverable_rows_blocked_all"])
    recoverable_rows_seen = int(summary["stage_144_validation"]["recovered_rows"]) > 0 or int(
        taxonomy["taxonomy"]["recoverable_formatting_issue"]["observed_counts"]["stage_143"]
    ) > 0
    boundary_preserved = bool(summary["semantic_boundary_preserved"])

    if stable_preserved and regression_detected and regression_blocked and boundary_preserved and recoverable_rows_seen:
        verdict = "Anti-degradation path validated"
        recommendation = "进入冻结语义不变前提下的小步回归验证线"
        why = [
            "Healthy parser-reachable rows remain on the raw parser path.",
            "Degenerated regression rows are blocked explicitly before parser guessing.",
            "At least one recoverable formatting-only case is validated without changing label semantics.",
        ]
    elif stable_preserved and regression_detected and regression_blocked and boundary_preserved:
        verdict = "Partially validated"
        recommendation = "继续做边界样例与误伤控制，不准扩张"
        why = [
            "Healthy parser-reachable rows are preserved and not falsely blocked.",
            "Pure punctuation collapse is now explicitly classified as degeneration-blocked instead of being hidden inside parser failure noise.",
            "Current evidence window still lacks a real recovered formatting-only regression case, so the path is not yet strong enough to become the default route.",
        ]
    else:
        verdict = "Not validated"
        recommendation = "下一步回到更细的 raw-output drift 诊断，不准修太快"
        why = [
            "The anti-degradation path either harms stable rows, fails to isolate degeneration rows, or does not preserve semantic boundaries.",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stable_rows_preserved": stable_preserved,
        "regression_rows_detected": regression_detected,
        "regression_rows_blocked": regression_blocked,
        "recoverable_rows_seen": recoverable_rows_seen,
        "semantic_boundary_preserved": boundary_preserved,
        "final_verdict": verdict,
    }
    verdict_payload = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": verdict,
        "single_verdict_policy": "one_of_validated__partially_validated__not_validated",
        "primary_basis": why,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
        "why": why,
        "do_not_do_yet": [
            "change_benchmark_truth_semantics",
            "change_gate_semantics",
            "expand_budget",
            "expand_model_axis",
            "stack_more_parser_heuristics_as_a_black_box",
        ],
        "boundary_table_path": str((robustness_dir / "route_c_output_format_robustness_rules.json").resolve()),
    }

    write_json(output_dir / "route_c_output_format_robustness_analysis_summary.json", analysis_summary)
    write_json(output_dir / "route_c_output_format_robustness_verdict.json", verdict_payload)
    write_json(output_dir / "route_c_output_format_robustness_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict_payload,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "route_c_output_format_robustness_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "route_c_output_format_robustness_verdict.json").resolve()),
            "recommendation": str((output_dir / "route_c_output_format_robustness_next_step_recommendation.json").resolve()),
        },
    }
