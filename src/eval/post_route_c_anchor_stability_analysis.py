"""Compare refined and anchor-aware route_c after explicit anchor-aware stability confirmation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-route-c-anchor-stability-analysis/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_post_route_c_anchor_stability_analysis(
    route_c_execution_dir: Path,
    route_c_refined_execution_dir: Path,
    route_c_refined_stability_dir: Path,
    route_c_anchor_execution_dir: Path,
    route_c_anchor_stability_dir: Path,
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

    original_density = float(original_metrics.get("class_balance", {}).get("label_1", 0) or 0) / float(original_metrics.get("num_rows", 1) or 1)
    refined_density = float(refined_metrics.get("refined_density", 0.0) or 0.0)
    anchor_density = float(anchor_metrics.get("anchor_density", 0.0) or 0.0)

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "original_execution": {
            "summary_status": original_run_summary.get("summary_status"),
            "execution_status": original_run_summary.get("execution_status"),
            "class_balance": original_run_summary.get("class_balance"),
            "density": original_density,
        },
        "refined_execution": {
            "summary_status": refined_run_summary.get("summary_status"),
            "execution_status": refined_run_summary.get("execution_status"),
            "class_balance": refined_run_summary.get("class_balance"),
            "density": refined_density,
            "stability_established": refined_stability.get("stability_established"),
            "stability_characterization": refined_stability.get("stability_characterization"),
        },
        "anchor_execution": {
            "summary_status": anchor_run_summary.get("summary_status"),
            "execution_status": anchor_run_summary.get("execution_status"),
            "class_balance": anchor_run_summary.get("class_balance"),
            "density": anchor_density,
            "positive_support_sample_ids": anchor_run_summary.get("positive_support_sample_ids"),
        },
        "anchor_stability": {
            "stability_established": anchor_stability.get("stability_established"),
            "stability_characterization": anchor_stability.get("stability_characterization"),
            "all_two_classes": anchor_stability.get("all_two_classes"),
            "all_logistic_pass": anchor_stability.get("all_logistic_pass"),
            "anchor_density_preserved_all_runs": anchor_stability.get("anchor_density_preserved_all_runs"),
            "reference_anchor_preserved_all_runs": anchor_stability.get("reference_anchor_preserved_all_runs"),
        },
        "density_gain_anchor_vs_refined": anchor_density / refined_density if refined_density > 0 else None,
        "key_tradeoffs": [
            "Anchor-aware route_c is valuable only if its density gain over refined route_c survives reruns.",
            "The current anchor-aware gain still comes from the same single positive anchor rather than from new positives.",
        ],
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "original_density": original_density,
        "refined_density": refined_density,
        "anchor_density": anchor_density,
        "anchor_beats_refined_on_density": bool(anchor_density > refined_density),
        "anchor_stability_established": anchor_stability.get("stability_established"),
        "progression_summary": [
            "116 established the original 1/24 route_c sparse baseline.",
            "120/121 established the refined 1/8 route_c baseline as better_and_stable.",
            "124 promoted anchor-aware route_c to a denser 1/6 execution slice.",
            "126 answers whether the 1/6 anchor-aware regime is stable enough to become the next working baseline.",
        ],
        "current_characterization": (
            "anchor_aware_route_c_is_a_more_analyzable_working_baseline"
            if bool(anchor_stability.get("stability_established")) and anchor_density > refined_density
            else "refined_route_c_remains_the_more_reliable_working_baseline"
        ),
    }
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "recommended_next_step": (
            "selection_deepening_before_any_budget_expansion"
            if bool(anchor_stability.get("stability_established")) and anchor_density > refined_density
            else "keep_refined_baseline_before_any_budget_expansion"
        ),
        "why": (
            [
                "Anchor-aware route_c now has both a real density advantage over refined route_c and an explicit stability confirmation.",
                "The current evidence still does not justify blind budget expansion because absolute positive support remains 1.",
                "The next honest move is to explore selection deepening around the same anchor-aware regime before touching budget.",
            ]
            if bool(anchor_stability.get("stability_established")) and anchor_density > refined_density
            else [
                "Anchor-aware route_c did not establish a stable enough advantage over the refined baseline.",
                "Refined route_c remains the better-supported working baseline.",
                "Blind budget expansion is still not justified under the current evidence.",
            ]
        ),
        "not_recommended_yet": [
            "blind_budget_expansion",
            "3b_or_7b_expansion",
            "dataset_axis_expansion",
            "fusion_axis_expansion",
        ],
    }

    write_json(output_dir / "route_c_refined_vs_anchor_stability_comparison.json", comparison)
    write_json(output_dir / "route_c_anchor_stability_analysis_summary.json", summary)
    write_json(output_dir / "route_c_anchor_stability_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "comparison": str((output_dir / "route_c_refined_vs_anchor_stability_comparison.json").resolve()),
            "summary": str((output_dir / "route_c_anchor_stability_analysis_summary.json").resolve()),
            "recommendation": str((output_dir / "route_c_anchor_stability_next_step_recommendation.json").resolve()),
        },
    }
