"""Compare refined, anchor-aware, deepened, and anchor-followup-v2 route_c baselines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-anchor-v2-analysis/v1"


def build_post_route_c_anchor_v2_analysis(
    route_c_refined_execution_dir: Path,
    route_c_anchor_execution_dir: Path,
    route_c_deepened_execution_dir: Path,
    route_c_deepened_analysis_dir: Path,
    route_c_anchor_execution_v2_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    refined_run_summary = load_json(route_c_refined_execution_dir / "route_c_refined_execution_run_summary.json")
    refined_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    anchor_run_summary = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_run_summary.json")
    anchor_metrics = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_metrics.json")
    deepened_run_summary = load_json(route_c_deepened_execution_dir / "route_c_deepened_execution_run_summary.json")
    deepened_metrics = load_json(route_c_deepened_execution_dir / "route_c_deepened_execution_metrics.json")
    prior_summary = load_json(route_c_deepened_analysis_dir / "route_c_deepened_analysis_summary.json")
    prior_recommendation = load_json(route_c_deepened_analysis_dir / "route_c_deepened_next_step_recommendation.json")

    v2_run_summary = load_json(route_c_anchor_execution_v2_dir / "route_c_anchor_execution_v2_run_summary.json")
    v2_metrics = load_json(route_c_anchor_execution_v2_dir / "route_c_anchor_execution_v2_metrics.json")

    refined_density = float(refined_metrics.get("refined_density", 0.0) or 0.0)
    anchor_density = float(anchor_metrics.get("anchor_density", 0.0) or 0.0)
    deepened_density = float(deepened_metrics.get("deepened_density", 0.0) or 0.0)
    v2_density_raw = v2_run_summary.get("v2_density")
    v2_density = float(v2_density_raw) if isinstance(v2_density_raw, (int, float)) else None

    prior_working_baseline = str(prior_summary.get("working_baseline"))
    v2_assessment = str(v2_run_summary.get("baseline_preservation_assessment"))
    v2_summary_status = str(v2_run_summary.get("summary_status"))

    if v2_summary_status == "PASS" and v2_assessment == "baseline_preserved_and_extended":
        working_baseline = "anchor-followup-v2"
        baseline_reason = "v2 preserved anchor constraints and showed extension signal."
    elif prior_working_baseline == "anchor-aware":
        working_baseline = "anchor-aware"
        baseline_reason = (
            "131 already selected anchor-aware as working baseline, and 133 v2 did not produce an upgrade-level result."
        )
    else:
        working_baseline = prior_working_baseline
        baseline_reason = "Carry over prior baseline because v2 evidence is not sufficient for an upgrade."

    route_c_local_optimal_single_anchor = bool(
        working_baseline == "anchor-aware"
        and int((anchor_run_summary.get("class_balance") or {}).get("label_1", 0) or 0) == 1
        and v2_assessment != "baseline_preserved_and_extended"
    )

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "prior_131_decision": {
            "working_baseline": prior_working_baseline,
            "recommended_next_step": prior_recommendation.get("recommended_next_step"),
        },
        "refined": {
            "summary_status": refined_run_summary.get("summary_status"),
            "execution_status": refined_run_summary.get("execution_status"),
            "class_balance": refined_run_summary.get("class_balance"),
            "density": refined_density,
        },
        "anchor_aware": {
            "summary_status": anchor_run_summary.get("summary_status"),
            "execution_status": anchor_run_summary.get("execution_status"),
            "class_balance": anchor_run_summary.get("class_balance"),
            "density": anchor_density,
        },
        "deepened": {
            "summary_status": deepened_run_summary.get("summary_status"),
            "execution_status": deepened_run_summary.get("execution_status"),
            "class_balance": deepened_run_summary.get("class_balance"),
            "density": deepened_density,
            "baseline_upgrade_assessment": deepened_run_summary.get("baseline_upgrade_assessment"),
        },
        "anchor_followup_v2": {
            "summary_status": v2_summary_status,
            "execution_status": v2_run_summary.get("execution_status"),
            "class_balance": v2_run_summary.get("class_balance"),
            "density": v2_density,
            "baseline_preservation_assessment": v2_assessment,
            "failure_stage": v2_run_summary.get("failure_stage"),
            "failure_reason": v2_run_summary.get("failure_reason"),
        },
        "density_ratios": {
            "anchor_vs_refined": anchor_density / refined_density if refined_density > 0 else None,
            "deepened_vs_anchor": deepened_density / anchor_density if anchor_density > 0 else None,
            "v2_vs_anchor": v2_density / anchor_density if v2_density is not None and anchor_density > 0 else None,
            "v2_vs_refined": v2_density / refined_density if v2_density is not None and refined_density > 0 else None,
        },
        "working_baseline": working_baseline,
        "working_baseline_reason": baseline_reason,
    }

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "refined_density": refined_density,
        "anchor_density": anchor_density,
        "deepened_density": deepened_density,
        "v2_density": v2_density,
        "prior_working_baseline": prior_working_baseline,
        "working_baseline": working_baseline,
        "v2_execution_status": v2_run_summary.get("execution_status"),
        "v2_baseline_preservation_assessment": v2_assessment,
        "route_c_local_optimal_single_anchor": route_c_local_optimal_single_anchor,
        "progression_summary": [
            "131 established anchor-aware as the working baseline over deepened.",
            "132 built a baseline-preserving v2 candidate via conservative neighbor swap.",
            "133 execution did not produce an upgrade-level result for v2.",
            "Current decision keeps baseline priority on stable anchor-aware behavior.",
        ],
    }

    if working_baseline == "anchor-followup-v2":
        recommended_next_step = "promote_anchor_followup_v2_and_run_stability_confirmation"
        why = [
            "v2 showed baseline-preserving extension evidence.",
            "Promotion still requires follow-up stability confirmation before wider expansion.",
        ]
    elif working_baseline == "anchor-aware":
        recommended_next_step = "keep_anchor_aware_baseline_and_only_controlled_micro_deepening"
        why = [
            "Anchor-aware remains denser and stable under current evidence.",
            "v2 did not deliver a baseline-upgrading signal in 133.",
            "Next step should stay in controlled deepening, not blind budget expansion.",
        ]
    else:
        recommended_next_step = "hold_current_baseline_before_any_expansion"
        why = [
            "No stronger baseline-upgrade evidence is available yet.",
            "Expansion without baseline certainty increases analysis risk.",
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

    write_json(output_dir / "route_c_anchor_v2_comparison.json", comparison)
    write_json(output_dir / "route_c_anchor_v2_analysis_summary.json", summary)
    write_json(output_dir / "route_c_anchor_v2_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "comparison": str((output_dir / "route_c_anchor_v2_comparison.json").resolve()),
            "summary": str((output_dir / "route_c_anchor_v2_analysis_summary.json").resolve()),
            "recommendation": str((output_dir / "route_c_anchor_v2_next_step_recommendation.json").resolve()),
        },
    }
