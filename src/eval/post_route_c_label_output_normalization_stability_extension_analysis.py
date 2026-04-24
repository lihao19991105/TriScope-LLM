"""Post-analysis for route_c output-normalization stability extension recheck (stage 143)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-label-output-normalization-stability-extension-analysis/v1"


def _metric_range(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "max": None, "mean": None}
    return {
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def _rows_metrics(run_rows: list[dict[str, Any]]) -> dict[str, Any]:
    run_count = len(run_rows)
    gate_pass_flags = [str(row.get("gate_status")) == "PASS" for row in run_rows]
    dual_class_flags = [list(row.get("execution_label_set") or []) == [0, 1] for row in run_rows]
    consistency_flags = [bool(row.get("consistency_restored")) for row in run_rows]

    parsed_values = [float(row.get("parsed_option_count") or 0.0) for row in run_rows]
    missing_values = [float(row.get("missing_option_ratio") or 0.0) for row in run_rows]
    punct_values = [float(row.get("punct_only_ratio") or 0.0) for row in run_rows]

    return {
        "run_count": run_count,
        "gate_pass_rate": float(sum(gate_pass_flags)) / float(run_count) if run_count > 0 else 0.0,
        "dual_class_restoration_rate": float(sum(dual_class_flags)) / float(run_count) if run_count > 0 else 0.0,
        "consistency_restored_rate": float(sum(consistency_flags)) / float(run_count) if run_count > 0 else 0.0,
        "any_regression_to_blocked": any(not flag for flag in gate_pass_flags),
        "any_regression_to_single_class": any(not flag for flag in dual_class_flags),
        "parsed_option_count_range": _metric_range(parsed_values),
        "missing_option_ratio_range": _metric_range(missing_values),
        "punct_only_ratio_range": _metric_range(punct_values),
    }


def _is_parseability_within_bounds(metrics: dict[str, Any]) -> bool:
    parsed_min = metrics.get("parsed_option_count_range", {}).get("min")
    missing_max = metrics.get("missing_option_ratio_range", {}).get("max")
    punct_max = metrics.get("punct_only_ratio_range", {}).get("max")

    if parsed_min is None or missing_max is None or punct_max is None:
        return False
    if float(parsed_min) < 5.0:
        return False
    if float(missing_max) > 0.16666666666666666:
        return False
    if float(punct_max) > 0.0:
        return False
    return True


def _build_markdown_report(compare: dict[str, Any], verdict: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Route-C Output Normalization Stability Extension Analysis")
    lines.append("")
    lines.append("## Four-stage Compare")
    lines.append(
        "- stage_140_blocked: "
        + f"gate={compare['stage_140_blocked']['label_health_gate_status']}, "
        + f"execution_label_set={compare['stage_140_blocked']['execution_label_set']}, "
        + f"consistency_restored={compare['stage_140_blocked']['consistency_restored']}"
    )
    lines.append(
        "- stage_141_first_recovery: "
        + f"gate={compare['stage_141_first_recovery']['gate_status']}, "
        + f"execution_label_set={compare['stage_141_first_recovery']['execution_label_set']}, "
        + f"consistency_restored={compare['stage_141_first_recovery']['consistency_restored']}"
    )
    lines.append(
        "- stage_142_recheck: "
        + f"run_count={compare['stage_142_repeated_reruns']['run_count']}, "
        + f"gate_pass_rate={compare['stage_142_repeated_reruns']['gate_pass_rate']:.4f}, "
        + f"dual_class_restoration_rate={compare['stage_142_repeated_reruns']['dual_class_restoration_rate']:.4f}"
    )
    lines.append(
        "- stage_143_extension_recheck: "
        + f"added_run_count={compare['stage_143_extension_reruns']['run_count']}, "
        + f"gate_pass_rate={compare['stage_143_extension_reruns']['gate_pass_rate']:.4f}, "
        + f"dual_class_restoration_rate={compare['stage_143_extension_reruns']['dual_class_restoration_rate']:.4f}"
    )
    lines.append("")
    lines.append("## Cumulative (142 + 143)")
    cumulative = compare["cumulative_142_143"]
    lines.append(f"- total_run_count: {cumulative['run_count']}")
    lines.append(f"- gate_pass_rate: {cumulative['gate_pass_rate']:.4f}")
    lines.append(f"- dual_class_restoration_rate: {cumulative['dual_class_restoration_rate']:.4f}")
    lines.append(f"- consistency_restored_rate: {cumulative['consistency_restored_rate']:.4f}")
    lines.append(f"- any_cumulative_regression_to_blocked: {cumulative['any_regression_to_blocked']}")
    lines.append(f"- any_cumulative_regression_to_single_class: {cumulative['any_regression_to_single_class']}")
    lines.append("")
    lines.append("## Verdict")
    lines.append(f"- final_verdict: {verdict['final_verdict']}")
    lines.append(f"- verdict_confidence: {verdict['verdict_confidence']}")
    lines.append("- evidence:")
    for item in verdict.get("evidence", []):
        lines.append(f"  - {item}")
    lines.append("")
    lines.append("## Single Recommendation")
    lines.append(f"- {verdict['single_next_step']}")
    return "\n".join(lines) + "\n"


def build_post_route_c_label_output_normalization_stability_extension_analysis(
    prior_blocked_analysis_dir: Path,
    first_recovery_recheck_dir: Path,
    prior_stability_analysis_dir: Path,
    prior_stability_recheck_dir: Path,
    extension_recheck_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    blocked_summary = load_json(prior_blocked_analysis_dir / "route_c_label_repair_analysis_summary.json")
    first_recovery_summary = load_json(
        first_recovery_recheck_dir / "route_c_label_output_normalization_recheck_summary.json"
    )
    prior_compare = load_json(prior_stability_analysis_dir / "route_c_label_output_normalization_stability_compare.json")

    prior_details = load_jsonl(
        prior_stability_recheck_dir / "route_c_label_output_normalization_stability_recheck_details.jsonl"
    )
    extension_summary = load_json(
        extension_recheck_dir / "route_c_label_output_normalization_stability_extension_recheck_summary.json"
    )
    extension_details = load_jsonl(
        extension_recheck_dir / "route_c_label_output_normalization_stability_extension_recheck_details.jsonl"
    )

    stage_142 = dict(prior_compare.get("stage_142_repeated_reruns") or {})
    stage_143 = _rows_metrics(extension_details)
    cumulative_rows = prior_details + extension_details
    cumulative_metrics = _rows_metrics(cumulative_rows)

    parseability_within_bounds = _is_parseability_within_bounds(cumulative_metrics)
    has_any_regression = bool(
        cumulative_metrics["any_regression_to_blocked"]
        or cumulative_metrics["any_regression_to_single_class"]
    )

    # Verdict policy for stage 143:
    # - Not yet stable: any regression, incomplete restoration, or parseability regression.
    # - Stable enough: no regression, full restoration, parseability within inherited bounds,
    #   and cumulative run coverage >= 8.
    # - Provisionally stable: otherwise.
    if (
        has_any_regression
        or cumulative_metrics["gate_pass_rate"] < 1.0
        or cumulative_metrics["dual_class_restoration_rate"] < 1.0
        or cumulative_metrics["consistency_restored_rate"] < 1.0
        or not parseability_within_bounds
    ):
        final_verdict = "Not yet stable"
        verdict_confidence = "high"
        single_next_step = (
            "Return to execution-level stability/parser-path closure under unchanged gate, "
            "normalization, and benchmark-truth semantics until regressions are eliminated."
        )
        evidence = [
            "At least one regression or non-100% restoration signal remains in extension or cumulative evidence.",
            "Current repaired path cannot be treated as stable working baseline.",
        ]
    elif cumulative_metrics["run_count"] >= 8:
        final_verdict = "Stable enough"
        verdict_confidence = "high"
        single_next_step = (
            "Enter the next non-expansion validation line: run time-separated replay confirmation "
            "on the same frozen settings before any axis/budget/prompt expansion."
        )
        evidence = [
            "143 added reruns preserved gate PASS, dual-class restoration, and consistency restoration.",
            "Cumulative 142+143 evidence shows no regression to BLOCKED or single-class behavior.",
            "Cumulative repeated-run coverage reached 8 under unchanged settings.",
            "Parseability remained within inherited acceptable bounds (parsed>=5, missing<=0.1667, punct_only=0).",
        ]
    else:
        final_verdict = "Provisionally stable"
        verdict_confidence = "medium"
        single_next_step = (
            "Keep the current line in minimal stability confirmation mode and add more same-setting reruns only."
        )
        evidence = [
            "Core restoration is maintained without explicit regression.",
            "But cumulative evidence is still insufficient for stable-enough promotion.",
        ]

    verdict_support_evidence = {
        "supports_accidental_recovery_hypothesis": bool(final_verdict != "Stable enough"),
        "observed_fragility_indicators": {
            "any_regression_to_blocked": cumulative_metrics["any_regression_to_blocked"],
            "any_regression_to_single_class": cumulative_metrics["any_regression_to_single_class"],
            "parseability_out_of_bound": not parseability_within_bounds,
        },
        "is_evidence_sufficient_for_upgrade": bool(final_verdict == "Stable enough"),
    }

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
        "stage_142_repeated_reruns": stage_142,
        "stage_143_extension_reruns": stage_143,
        "cumulative_142_143": cumulative_metrics,
        "evidence_chain_evolution": {
            "from_140_to_143": (
                "140 was BLOCKED with single-class execution; 141 restored dual-class PASS; "
                "142 repeated reruns stayed stable; 143 extension reruns expanded repeated evidence under frozen settings."
            ),
            "does_143_strengthen_repeatability_evidence": bool(stage_143.get("run_count", 0) > 0),
            "baseline_transition_status": (
                "stable_working_baseline" if final_verdict == "Stable enough" else "provisional_working_baseline"
            ),
            "if_not_stable_enough_missing_piece": (
                "none" if final_verdict == "Stable enough" else "more repeated no-regression evidence or parser-path closure"
            ),
        },
        "verdict_support_evidence": verdict_support_evidence,
    }

    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "verdict_confidence": verdict_confidence,
        "single_next_step": single_next_step,
        "evidence": evidence,
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": single_next_step,
        "why": evidence,
    }

    report_text = _build_markdown_report(compare=compare, verdict=verdict)

    write_json(output_dir / "route_c_label_output_normalization_stability_extension_compare.json", compare)
    (output_dir / "route_c_label_output_normalization_stability_extension_report.md").write_text(
        report_text,
        encoding="utf-8",
    )
    write_json(
        output_dir / "route_c_label_output_normalization_stability_extension_next_step_recommendation.json",
        recommendation,
    )
    write_json(output_dir / "route_c_label_output_normalization_stability_extension_verdict.json", verdict)

    return {
        "summary": verdict,
        "output_paths": {
            "compare": str(
                (output_dir / "route_c_label_output_normalization_stability_extension_compare.json").resolve()
            ),
            "report": str(
                (output_dir / "route_c_label_output_normalization_stability_extension_report.md").resolve()
            ),
            "recommendation": str(
                (
                    output_dir
                    / "route_c_label_output_normalization_stability_extension_next_step_recommendation.json"
                ).resolve()
            ),
            "verdict": str(
                (output_dir / "route_c_label_output_normalization_stability_extension_verdict.json").resolve()
            ),
        },
    }
