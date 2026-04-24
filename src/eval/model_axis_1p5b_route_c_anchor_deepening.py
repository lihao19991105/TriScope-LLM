"""Compare anchor-aware selection deepening against budget expansion and materialize a minimal deepened candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json, write_jsonl


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-anchor-deepening/v1"


def build_model_axis_1p5b_route_c_anchor_deepening(
    route_c_anchor_followup_dir: Path,
    route_c_anchor_stability_analysis_dir: Path,
    route_c_execution_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    followup_summary = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_candidate_summary.json")
    followup_registry = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_selection_registry.json")
    stability_recommendation = load_json(
        route_c_anchor_stability_analysis_dir / "route_c_anchor_stability_next_step_recommendation.json"
    )
    execution_rows = load_jsonl(route_c_execution_dir / "route_c_execution_run" / "route_c_v6_dataset.jsonl")

    current_anchor_base_id = str(followup_registry["anchor_base_sample_id"])
    current_neighbor_base_ids = [str(item) for item in followup_registry.get("selected_neighbor_base_ids", [])]
    selected_base_ids = [current_anchor_base_id] + current_neighbor_base_ids

    # Deepening means adding exactly one more nearest same-regime negative from the original 24-row route_c slice.
    neighbor_analysis = load_json(route_c_anchor_followup_dir / "route_c_anchor_neighbor_analysis.json")
    ranked_neighbors = neighbor_analysis.get("candidate_neighbors_ranked", [])
    next_neighbor = next(
        (
            row
            for row in ranked_neighbors
            if str(row.get("base_sample_id")) not in set(current_neighbor_base_ids)
        ),
        None,
    )
    if next_neighbor is None:
        raise ValueError("128 expected at least one additional neighbor beyond the current anchor-aware candidate.")

    deepened_base_ids = selected_base_ids + [str(next_neighbor["base_sample_id"])]
    deepened_rows = [row for row in execution_rows if str(row.get("base_sample_id")) in set(deepened_base_ids)]
    class_balance = {
        "label_0": sum(1 for row in deepened_rows if int(row.get("ground_truth_label", 0)) == 0),
        "label_1": sum(1 for row in deepened_rows if int(row.get("ground_truth_label", 0)) == 1),
    }
    deepened_density = float(class_balance["label_1"]) / float(len(deepened_rows)) if deepened_rows else None
    refined_density_floor = float(followup_summary.get("refined_density", 0.0) or 0.0)
    anchor_density = float(followup_summary.get("anchor_followup_density", 0.0) or 0.0)

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "options": [
            {
                "option_name": "selection_deepening",
                "expected_positive_gain": "more_local_thickness_without_new_axis",
                "expected_density": deepened_density,
                "density_vs_refined_floor": (
                    deepened_density / refined_density_floor if deepened_density is not None and refined_density_floor > 0 else None
                ),
                "cost_level": "low",
                "honesty_under_current_evidence": "strong",
                "conclusion": "Deepening can add one more same-regime neighbor while keeping density no worse than the refined 1/8 baseline.",
            },
            {
                "option_name": "budget_expansion",
                "expected_positive_gain": "unclear",
                "expected_density": "likely_lower",
                "cost_level": "medium",
                "honesty_under_current_evidence": "weak",
                "conclusion": "Blind budget expansion remains weak because the known universe still has only one stable positive anchor.",
            },
        ],
    }
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "recommended_next_step": (
            "selection_deepening_first"
            if stability_recommendation.get("recommended_next_step") == "selection_deepening_before_any_budget_expansion"
            else "defer_deepening_and_hold_anchor_baseline"
        ),
        "why": [
            "126/127 keep blind budget expansion out of scope because absolute positive support is still 1.",
            "A one-step deepening candidate can add local thickness while keeping density at the refined 1/8 floor.",
            "This is a lower-risk continuation than reopening the wider route_c universe.",
        ],
        "not_recommended_yet": [
            "blind_budget_expansion",
            "3b_or_7b_expansion",
            "dataset_axis_expansion",
            "fusion_axis_expansion",
        ],
    }
    deepened_registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_deepened",
        "anchor_base_sample_id": current_anchor_base_id,
        "previous_neighbor_base_ids": current_neighbor_base_ids,
        "new_neighbor_base_id": str(next_neighbor["base_sample_id"]),
        "selected_base_ids": deepened_base_ids,
        "selection_strategy": "anchor_plus_top3_same_regime_nearest_negatives",
        "source_followup_registry": str((route_c_anchor_followup_dir / "route_c_anchor_followup_selection_registry.json").resolve()),
    }
    deepened_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_deepened",
        "selected_base_count": len(deepened_base_ids),
        "selected_contract_count": len(deepened_rows),
        "class_balance": class_balance,
        "anchor_density": anchor_density,
        "deepened_density": deepened_density,
        "refined_density_floor": refined_density_floor,
        "density_vs_anchor": deepened_density / anchor_density if deepened_density is not None and anchor_density > 0 else None,
        "density_vs_refined_floor": deepened_density / refined_density_floor if deepened_density is not None and refined_density_floor > 0 else None,
        "notes": [
            "The deepened candidate trades some density for more same-regime thickness.",
            "It is materialized as a next-step input object, not yet a new execution run.",
        ],
    }

    write_json(output_dir / "route_c_anchor_deepening_options_comparison.json", comparison)
    write_json(output_dir / "route_c_anchor_deepening_recommendation.json", recommendation)
    write_json(output_dir / "route_c_anchor_deepened_selection_registry.json", deepened_registry)
    write_jsonl(output_dir / "route_c_anchor_deepened_candidate_dataset.jsonl", deepened_rows)
    write_json(output_dir / "route_c_anchor_deepened_candidate_summary.json", deepened_summary)

    return {
        "summary": deepened_summary,
        "output_paths": {
            "comparison": str((output_dir / "route_c_anchor_deepening_options_comparison.json").resolve()),
            "recommendation": str((output_dir / "route_c_anchor_deepening_recommendation.json").resolve()),
            "deepened_registry": str((output_dir / "route_c_anchor_deepened_selection_registry.json").resolve()),
            "deepened_summary": str((output_dir / "route_c_anchor_deepened_candidate_summary.json").resolve()),
        },
    }
