"""Post-analysis for route_c output-normalization stability reruns."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-label-output-normalization-stability-analysis/v1"


def _metric_range(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "max": None, "mean": None}
    return {"min": min(values), "max": max(values), "mean": sum(values) / len(values)}


def _build_markdown_report(compare: dict[str, Any], verdict: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Route-C Output Normalization Stability Analysis")
    lines.append("")
    lines.append("## Three-stage Compare")
    lines.append(
        "- stage_140_blocked: "
        + f"gate={compare['stage_140_blocked']['label_health_gate_status']}, "
        + f"consistency_restored={compare['stage_140_blocked']['consistency_restored']}"
    )
    lines.append(
        "- stage_141_first_recovery: "
        + f"gate={compare['stage_141_first_recovery']['gate_status']}, "
        + f"execution_label_set={compare['stage_141_first_recovery']['execution_label_set']}, "
        + f"consistency_restored={compare['stage_141_first_recovery']['consistency_restored']}"
    )
    lines.append(
        "- stage_142_repeated_reruns: "
        + f"gate_pass_rate={compare['stage_142_repeated_reruns']['gate_pass_rate']:.4f}, "
        + f"dual_class_restoration_rate={compare['stage_142_repeated_reruns']['dual_class_restoration_rate']:.4f}, "
        + f"consistency_restored_rate={compare['stage_142_repeated_reruns']['consistency_restored_rate']:.4f}"
    )
    lines.append("")
    lines.append("## Verdict")
    lines.append(f"- final_verdict: {verdict['final_verdict']}")
    lines.append(f"- can_be_working_stable_baseline: {verdict['can_be_working_stable_baseline']}")
    lines.append("- evidence:")
    for item in verdict.get("evidence", []):
        lines.append(f"  - {item}")
    lines.append("")
    lines.append("## Recommendation")
    lines.append(f"- {verdict['single_next_step']}" )
    return "\n".join(lines) + "\n"


def build_post_route_c_label_output_normalization_stability_analysis(
    prior_blocked_analysis_dir: Path,
    first_recovery_recheck_dir: Path,
    stability_recheck_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    blocked_summary = load_json(prior_blocked_analysis_dir / "route_c_label_repair_analysis_summary.json")
    first_recovery_summary = load_json(
        first_recovery_recheck_dir / "route_c_label_output_normalization_recheck_summary.json"
    )
    stability_summary = load_json(
        stability_recheck_dir / "route_c_label_output_normalization_stability_recheck_summary.json"
    )
    stability_details = load_jsonl(
        stability_recheck_dir / "route_c_label_output_normalization_stability_recheck_details.jsonl"
    )

    parsed_values = [float(row.get("parsed_option_count") or 0.0) for row in stability_details]
    missing_values = [float(row.get("missing_option_ratio") or 0.0) for row in stability_details]
    punct_values = [float(row.get("punct_only_ratio") or 0.0) for row in stability_details]

    run_count = len(stability_details)
    gate_pass_rate = float(stability_summary.get("stability", {}).get("gate_pass_rate", 0.0) or 0.0)
    dual_class_rate = float(stability_summary.get("stability", {}).get("dual_class_restoration_rate", 0.0) or 0.0)
    consistency_rate = float(stability_summary.get("stability", {}).get("consistency_restored_rate", 0.0) or 0.0)
    any_blocked = bool(stability_summary.get("stability", {}).get("any_regression_to_blocked"))
    any_single_class = bool(stability_summary.get("stability", {}).get("any_regression_to_single_class"))

    compare = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage_140_blocked": {
            "working_baseline": blocked_summary.get("working_baseline"),
            "label_health_gate_status": blocked_summary.get("label_health_gate_status"),
            "execution_label_set": blocked_summary.get("execution_label_set"),
            "consistency_restored": blocked_summary.get("consistency_restored"),
            "label_path_still_primary_blocker": blocked_summary.get("label_path_still_primary_blocker"),
        },
        "stage_141_first_recovery": {
            "gate_status": first_recovery_summary.get("gate_status"),
            "execution_label_set": first_recovery_summary.get("execution_label_set"),
            "consistency_restored": first_recovery_summary.get("consistency_restored"),
            "parseability": first_recovery_summary.get("parseability"),
        },
        "stage_142_repeated_reruns": {
            "run_count": run_count,
            "gate_pass_rate": gate_pass_rate,
            "dual_class_restoration_rate": dual_class_rate,
            "consistency_restored_rate": consistency_rate,
            "any_regression_to_blocked": any_blocked,
            "any_regression_to_single_class": any_single_class,
            "parsed_option_count_range": _metric_range(parsed_values),
            "missing_option_ratio_range": _metric_range(missing_values),
            "punct_only_ratio_range": _metric_range(punct_values),
            "regressed_runs": stability_summary.get("stability", {}).get("regressed_runs", []),
        },
        "key_questions": {
            "is_141_recovery_repeatable": bool(gate_pass_rate == 1.0 and dual_class_rate == 1.0 and consistency_rate == 1.0),
            "has_obvious_post_recovery_fragility": bool(any_blocked or any_single_class),
            "most_regression_prone_metric": (
                "none_observed"
                if not (any_blocked or any_single_class)
                else "gate_or_label_set"
            ),
        },
    }

    # Verdict policy:
    # - Not yet stable: any blocked/single-class regression.
    # - Stable enough: no regression, all rates 1.0, and >=5 repeated runs.
    # - Provisionally stable: no regression with full restoration but limited rerun coverage.
    if any_blocked or any_single_class or gate_pass_rate < 1.0 or dual_class_rate < 1.0 or consistency_rate < 1.0:
        final_verdict = "Not yet stable"
        can_be_baseline = False
        next_step = "Continue parser/execution stability closure under unchanged gate and semantics until regressions disappear."
        evidence = [
            "At least one repeated rerun regressed to BLOCKED or single-class behavior, or restoration rates were below 100%.",
            "Current recovery cannot be treated as stable baseline evidence.",
        ]
    elif run_count >= 5:
        final_verdict = "Stable enough"
        can_be_baseline = True
        next_step = "Use current normalization-repaired route_c execution as the working stable baseline for the next minimal milestone."
        evidence = [
            "All repeated reruns passed gate and preserved dual-class restoration.",
            "Consistency restoration remained true across the repeated rerun set.",
            "Rerun coverage reached stable-enough threshold in this policy.",
        ]
    else:
        final_verdict = "Provisionally stable"
        can_be_baseline = True
        next_step = "Keep this as provisional working baseline and run one additional minimal stability extension before any expansion."
        evidence = [
            "All repeated reruns passed gate and preserved dual-class restoration under frozen settings.",
            "No regression to BLOCKED or single-class execution was observed.",
            "Rerun coverage is still limited, so baseline confidence is provisional rather than final.",
        ]

    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "can_be_working_stable_baseline": can_be_baseline,
        "single_next_step": next_step,
        "evidence": evidence,
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": next_step,
        "final_verdict": final_verdict,
        "why": evidence,
    }

    report_text = _build_markdown_report(compare=compare, verdict=verdict)

    write_json(output_dir / "route_c_label_output_normalization_stability_compare.json", compare)
    (output_dir / "route_c_label_output_normalization_stability_report.md").write_text(report_text, encoding="utf-8")
    write_json(
        output_dir / "route_c_label_output_normalization_stability_next_step_recommendation.json",
        recommendation,
    )
    write_json(output_dir / "route_c_label_output_normalization_stability_verdict.json", verdict)

    return {
        "summary": verdict,
        "output_paths": {
            "compare": str((output_dir / "route_c_label_output_normalization_stability_compare.json").resolve()),
            "report": str((output_dir / "route_c_label_output_normalization_stability_report.md").resolve()),
            "recommendation": str(
                (output_dir / "route_c_label_output_normalization_stability_next_step_recommendation.json").resolve()
            ),
            "verdict": str((output_dir / "route_c_label_output_normalization_stability_verdict.json").resolve()),
        },
    }
