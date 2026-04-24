"""Post-analysis for focused recoverable-boundary evidence and collateral compression."""

from __future__ import annotations

from pathlib import Path

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-recoverable-boundary-evidence-and-collateral-compression-analysis/v1"


def post_route_c_recoverable_boundary_evidence_and_collateral_compression_analysis(
    boundary_control_dir: Path,
    output_dir: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = load_json(boundary_control_dir / "route_c_recoverable_boundary_control_summary.json")
    rules = load_json(boundary_control_dir / "route_c_recoverable_boundary_control_rules.json")

    no_nonrecoverable_leak = int(summary["current_nonrecoverable_leak_count"]) == 0
    no_normal_collateral_damage = int(summary["current_normal_collateral_damage_count"]) == 0
    no_recoverable_overblock = int(summary["current_recoverable_overblocked_count"]) == 0
    improvement_achieved = bool(summary["focused_improvement_achieved"])
    recoverable_pass_rate = summary.get("recoverable_pass_rate")

    if (
        no_nonrecoverable_leak
        and no_normal_collateral_damage
        and no_recoverable_overblock
        and recoverable_pass_rate == 1.0
        and improvement_achieved
    ):
        final_verdict = "Recoverable boundary control validated"
        recommendation = "进入冻结语义不变前提下的小步回归验证线"
        why = [
            "Recoverable formatting boundary cases now consistently reach pass_formatted_to_parser without semantic guessing.",
            "Normal parser-reachable guardrails remain untouched and unrecoverable guardrails remain blocked.",
            "The focused code-fence-like fix improves over the legacy path without expanding benchmark-truth or gate semantics.",
        ]
    elif no_nonrecoverable_leak and no_normal_collateral_damage:
        final_verdict = "Partially validated"
        recommendation = "继续做 recoverable boundary 证据补强与误伤压缩，不准扩张"
        why = [
            "The focused path still preserves unrecoverable blocking and normal pass-through.",
            "But recoverable boundary evidence is not yet fully clean, so it is still too early to move into the next regression-validation line.",
        ]
    else:
        final_verdict = "Not validated"
        recommendation = "回到 recoverable-boundary 规则与 handoff 收口，不准前进"
        why = [
            "The focused path either leaks nonrecoverable cases or causes collateral damage on normal parser-reachable rows.",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "legacy_recoverable_overblocked_count": summary["legacy_recoverable_overblocked_count"],
        "current_recoverable_overblocked_count": summary["current_recoverable_overblocked_count"],
        "current_nonrecoverable_leak_count": summary["current_nonrecoverable_leak_count"],
        "current_normal_collateral_damage_count": summary["current_normal_collateral_damage_count"],
        "recoverable_pass_rate": summary["recoverable_pass_rate"],
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_recoverable_boundary_control_validated__partially_validated__not_validated",
        "primary_basis": why,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": why,
        "rules_path": str((boundary_control_dir / "route_c_recoverable_boundary_control_rules.json").resolve()),
        "do_not_do_yet": [
            "change_benchmark_truth_semantics",
            "change_gate_semantics",
            "expand_budget",
            "expand_model_axis",
            "turn_recoverable_boundary_fix_into_general_parser_expansion",
        ],
    }

    write_json(output_dir / "route_c_recoverable_boundary_control_analysis_summary.json", analysis_summary)
    write_json(output_dir / "route_c_recoverable_boundary_control_verdict.json", verdict)
    write_json(output_dir / "route_c_recoverable_boundary_control_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "route_c_recoverable_boundary_control_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "route_c_recoverable_boundary_control_verdict.json").resolve()),
            "recommendation": str((output_dir / "route_c_recoverable_boundary_control_next_step_recommendation.json").resolve()),
        },
    }
