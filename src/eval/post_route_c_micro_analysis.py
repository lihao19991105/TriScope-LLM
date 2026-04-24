"""Compare anchor-aware/v2/micro route_c states and emit baseline recommendation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-micro-analysis/v1"


def build_post_route_c_micro_analysis(
    route_c_anchor_v2_analysis_dir: Path,
    collapse_diagnosis_dir: Path,
    route_c_micro_deepening_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    anchor_v2_summary = load_json(route_c_anchor_v2_analysis_dir / "route_c_anchor_v2_analysis_summary.json")
    anchor_v2_comparison = load_json(route_c_anchor_v2_analysis_dir / "route_c_anchor_v2_comparison.json")
    collapse_root_cause = load_json(collapse_diagnosis_dir / "route_c_anchor_v2_collapse_root_cause.json")
    micro_run_summary = load_json(route_c_micro_deepening_dir / "route_c_micro_deepening_run_summary.json")
    micro_metrics = load_json(route_c_micro_deepening_dir / "route_c_micro_deepening_metrics.json")
    micro_readiness = load_json(route_c_micro_deepening_dir / "route_c_micro_deepening_readiness_summary.json")

    prior_working_baseline = str(anchor_v2_summary.get("working_baseline"))
    micro_assessment = str(micro_run_summary.get("micro_deepening_assessment"))
    micro_status = str(micro_run_summary.get("summary_status"))

    if micro_status == "PASS" and micro_assessment == "baseline_preserved_and_executable":
        working_baseline = "micro-deepening"
        baseline_reason = "Micro path is executable and baseline-preserving under live label gate."
    else:
        working_baseline = prior_working_baseline
        baseline_reason = "Micro path did not produce executable upgrade evidence; keep prior anchor-aware baseline."

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "anchor_v2_state": {
            "working_baseline": anchor_v2_summary.get("working_baseline"),
            "v2_execution_status": anchor_v2_summary.get("v2_execution_status"),
            "v2_assessment": anchor_v2_summary.get("v2_baseline_preservation_assessment"),
        },
        "micro_state": {
            "summary_status": micro_status,
            "execution_status": micro_run_summary.get("execution_status"),
            "assessment": micro_assessment,
            "labels_collapse_avoided": micro_run_summary.get("labels_collapse_avoided"),
            "ready_for_execution": micro_readiness.get("ready_for_execution"),
        },
        "collapse_diagnosis": {
            "primary_root_cause": collapse_root_cause.get("primary_root_cause"),
            "root_cause_statement": collapse_root_cause.get("root_cause_statement"),
        },
        "working_baseline": working_baseline,
        "working_baseline_reason": baseline_reason,
    }

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "prior_working_baseline": prior_working_baseline,
        "working_baseline": working_baseline,
        "micro_summary_status": micro_status,
        "micro_execution_status": micro_run_summary.get("execution_status"),
        "micro_deepening_assessment": micro_assessment,
        "labels_collapse_avoided": micro_run_summary.get("labels_collapse_avoided"),
        "micro_class_balance": micro_metrics.get("class_balance"),
        "route_c_local_optimal_single_anchor": bool(working_baseline == "anchor-aware"),
    }

    if working_baseline == "micro-deepening":
        recommended_next_step = "run_micro_stability_confirmation_before_any_expansion"
        why = [
            "Micro candidate is executable under live label gate.",
            "Baseline preservation is maintained with stronger label-path consistency controls.",
        ]
    else:
        recommended_next_step = "keep_anchor_aware_baseline_and_fix_label_path_before_next_micro_attempt"
        why = [
            "Micro path remains label-fragile under current runtime evidence.",
            "Anchor-aware baseline remains the most stable working state.",
            "Next effort should prioritize label-path robustness, not budget expansion.",
        ]

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "working_baseline": working_baseline,
        "recommended_next_step": recommended_next_step,
        "why": why,
        "not_recommended_yet": [
            "blind_budget_expansion",
            "3b_or_7b_expansion",
            "dataset_axis_expansion",
            "fusion_axis_expansion",
        ],
    }

    write_json(output_dir / "route_c_anchor_vs_micro_comparison.json", comparison)
    write_json(output_dir / "route_c_micro_analysis_summary.json", summary)
    write_json(output_dir / "route_c_micro_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "comparison": str((output_dir / "route_c_anchor_vs_micro_comparison.json").resolve()),
            "summary": str((output_dir / "route_c_micro_analysis_summary.json").resolve()),
            "recommendation": str((output_dir / "route_c_micro_next_step_recommendation.json").resolve()),
        },
    }
