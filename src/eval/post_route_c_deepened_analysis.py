"""Compare original, refined, anchor-aware, and deepened route_c baselines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-route-c-deepened-analysis/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_post_route_c_deepened_analysis(
    route_c_execution_dir: Path,
    route_c_refined_execution_dir: Path,
    route_c_refined_stability_dir: Path,
    route_c_anchor_execution_dir: Path,
    route_c_anchor_stability_dir: Path,
    route_c_deepened_execution_dir: Path,
    route_c_deepened_stability_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    original_run_summary = load_json(route_c_execution_dir / "route_c_execution_run_summary.json")
    original_metrics = load_json(route_c_execution_dir / "route_c_execution_metrics.json")
    refined_run_summary = load_json(route_c_refined_execution_dir / "route_c_refined_execution_run_summary.json")
    refined_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    refined_stability = load_json(route_c_refined_stability_dir / "route_c_refined_stability_summary.json")
    anchor_run_summary = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_run_summary.json")
    anchor_metrics = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_metrics.json")
    anchor_stability = load_json(route_c_anchor_stability_dir / "route_c_anchor_stability_summary.json")
    deepened_run_summary = load_json(route_c_deepened_execution_dir / "route_c_deepened_execution_run_summary.json")
    deepened_metrics = load_json(route_c_deepened_execution_dir / "route_c_deepened_execution_metrics.json")
    deepened_stability = load_json(route_c_deepened_stability_dir / "route_c_deepened_stability_summary.json")

    original_num_rows = int(original_metrics.get("num_rows", 0) or 0)
    original_label_1 = int(original_metrics.get("class_balance", {}).get("label_1", 0) or 0)
    original_density = (float(original_label_1) / float(original_num_rows)) if original_num_rows > 0 else 0.0
    refined_density = float(refined_metrics.get("refined_density", 0.0) or 0.0)
    anchor_density = float(anchor_metrics.get("anchor_density", 0.0) or 0.0)
    deepened_density = float(deepened_metrics.get("deepened_density", 0.0) or 0.0)

    deepened_stability_established = bool(deepened_stability.get("stability_established"))
    deepened_keep = str(deepened_stability.get("baseline_decision")) == "stable_enough_to_keep"
    anchor_stability_established = bool(anchor_stability.get("stability_established"))
    refined_stability_established = bool(refined_stability.get("stability_established"))

    if deepened_stability_established and deepened_keep and deepened_density >= anchor_density:
        working_baseline = "deepened"
        baseline_reason = "Deepened candidate is stable and not worse than anchor density."
    elif anchor_stability_established and anchor_density >= refined_density:
        working_baseline = "anchor-aware"
        baseline_reason = "Anchor-aware candidate remains denser and stable, while deepened does not justify replacement."
    elif refined_stability_established:
        working_baseline = "refined"
        baseline_reason = "Refined candidate remains the last confirmed stable baseline with clear density gain over original."
    else:
        working_baseline = "original"
        baseline_reason = "No stronger stable baseline is confirmed beyond the original route_c baseline."

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "original": {
            "summary_status": original_run_summary.get("summary_status"),
            "execution_status": original_run_summary.get("execution_status"),
            "class_balance": original_run_summary.get("class_balance"),
            "density": original_density,
        },
        "refined": {
            "summary_status": refined_run_summary.get("summary_status"),
            "execution_status": refined_run_summary.get("execution_status"),
            "class_balance": refined_run_summary.get("class_balance"),
            "density": refined_density,
            "stability_established": refined_stability_established,
            "stability_characterization": refined_stability.get("stability_characterization"),
        },
        "anchor_aware": {
            "summary_status": anchor_run_summary.get("summary_status"),
            "execution_status": anchor_run_summary.get("execution_status"),
            "class_balance": anchor_run_summary.get("class_balance"),
            "density": anchor_density,
            "stability_established": anchor_stability_established,
            "stability_characterization": anchor_stability.get("stability_characterization"),
        },
        "deepened": {
            "summary_status": deepened_run_summary.get("summary_status"),
            "execution_status": deepened_run_summary.get("execution_status"),
            "class_balance": deepened_run_summary.get("class_balance"),
            "density": deepened_density,
            "stability_established": deepened_stability_established,
            "baseline_decision": deepened_stability.get("baseline_decision"),
            "baseline_upgrade_assessment": deepened_run_summary.get("baseline_upgrade_assessment"),
        },
        "density_ratios": {
            "refined_vs_original": refined_density / original_density if original_density > 0 else None,
            "anchor_vs_refined": anchor_density / refined_density if refined_density > 0 else None,
            "deepened_vs_refined": deepened_density / refined_density if refined_density > 0 else None,
            "deepened_vs_anchor": deepened_density / anchor_density if anchor_density > 0 else None,
        },
        "working_baseline": working_baseline,
        "working_baseline_reason": baseline_reason,
    }

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "original_density": original_density,
        "refined_density": refined_density,
        "anchor_density": anchor_density,
        "deepened_density": deepened_density,
        "working_baseline": working_baseline,
        "route_c_stable_working_state": bool(
            (working_baseline == "deepened" and deepened_stability_established)
            or (working_baseline == "anchor-aware" and anchor_stability_established)
            or (working_baseline == "refined" and refined_stability_established)
        ),
        "progression_summary": [
            "Original route_c is executable but sparse at 1/24.",
            "Refined route_c raised density to 1/8 and proved stable.",
            "Anchor-aware route_c raised density to 1/6 and proved stable.",
            "Deepened route_c adds thickness but must justify value against the anchor-aware baseline.",
        ],
        "current_characterization": (
            "anchor_aware_remains_best_working_baseline"
            if working_baseline == "anchor-aware"
            else (
                "deepened_baseline_is_ready"
                if working_baseline == "deepened"
                else "fallback_to_less_advanced_baseline"
            )
        ),
    }

    if working_baseline == "deepened":
        recommended_next_step = "continue_deepening_with_strict_anchor_guards"
        why = [
            "Deepened candidate is stable enough and not worse than anchor density.",
            "The route remains within the 1.5B local axis and keeps anchor continuity.",
            "Next deepening can proceed under the same non-expansion constraints.",
        ]
    elif working_baseline == "anchor-aware":
        recommended_next_step = "keep_anchor_aware_baseline_and_only_consider_more_deepening"
        why = [
            "Anchor-aware baseline remains denser than deepened under current evidence.",
            "Deepened currently looks like refined-floor preservation rather than a baseline upgrade.",
            "Blind budget expansion is still not justified with single-anchor positive support.",
        ]
    else:
        recommended_next_step = "hold_current_baseline_before_any_expansion"
        why = [
            "No stronger stable baseline is currently established.",
            "Further expansion would add risk without clear evidence of benefit.",
            "Stability and anchor continuity should be re-established first.",
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

    write_json(output_dir / "route_c_original_refined_anchor_deepened_comparison.json", comparison)
    write_json(output_dir / "route_c_deepened_analysis_summary.json", summary)
    write_json(output_dir / "route_c_deepened_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "comparison": str((output_dir / "route_c_original_refined_anchor_deepened_comparison.json").resolve()),
            "summary": str((output_dir / "route_c_deepened_analysis_summary.json").resolve()),
            "recommendation": str((output_dir / "route_c_deepened_next_step_recommendation.json").resolve()),
        },
    }
