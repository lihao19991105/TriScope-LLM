"""Compare original, refined, and anchor-aware route_c execution on the 1.5B model axis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-route-c-anchor-analysis/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_post_route_c_anchor_analysis(
    route_c_execution_dir: Path,
    route_c_refined_execution_dir: Path,
    route_c_refined_stability_dir: Path,
    route_c_anchor_followup_dir: Path,
    route_c_anchor_execution_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    original_run_summary = load_json(route_c_execution_dir / "route_c_execution_run_summary.json")
    original_metrics = load_json(route_c_execution_dir / "route_c_execution_metrics.json")
    refined_run_summary = load_json(route_c_refined_execution_dir / "route_c_refined_execution_run_summary.json")
    refined_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    refined_stability = load_json(route_c_refined_stability_dir / "route_c_refined_stability_summary.json")
    anchor_followup_summary = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_candidate_summary.json")
    anchor_precheck = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_precheck.json")
    anchor_run_summary = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_run_summary.json")
    anchor_metrics = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_metrics.json")

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
            "characterization": "stable_but_sparse",
        },
        "refined_execution": {
            "summary_status": refined_run_summary.get("summary_status"),
            "execution_status": refined_run_summary.get("execution_status"),
            "class_balance": refined_run_summary.get("class_balance"),
            "density": refined_density,
            "stability_characterization": refined_stability.get("stability_characterization"),
        },
        "anchor_followup_candidate": {
            "class_balance": anchor_followup_summary.get("class_balance"),
            "candidate_density": anchor_followup_summary.get("anchor_followup_density"),
            "worth_executing": anchor_precheck.get("worth_executing"),
        },
        "anchor_execution": {
            "summary_status": anchor_run_summary.get("summary_status"),
            "execution_status": anchor_run_summary.get("execution_status"),
            "class_balance": anchor_run_summary.get("class_balance"),
            "density": anchor_density,
            "density_gain_vs_refined": anchor_run_summary.get("density_gain_vs_refined"),
            "positive_support_sample_ids": anchor_run_summary.get("positive_support_sample_ids"),
        },
        "key_tradeoffs": [
            "Anchor-aware follow-up improves density by pruning anchor-distant negatives rather than by discovering new positives.",
            "Refined baseline remains the only route_c regime with an explicit stability confirmation artifact so far.",
        ],
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "original_density": original_density,
        "refined_density": refined_density,
        "anchor_density": anchor_density,
        "density_gain_anchor_vs_original": anchor_density / original_density if original_density > 0 else None,
        "density_gain_anchor_vs_refined": anchor_density / refined_density if refined_density > 0 else None,
        "anchor_beats_refined_on_density": bool(anchor_density > refined_density),
        "refined_stability_established": refined_stability.get("stability_established"),
        "anchor_adds_new_positive_support": bool((anchor_run_summary.get("positive_support_base_ids") or []) and len(anchor_run_summary.get("positive_support_base_ids") or []) > 1),
        "progression_summary": [
            "116 proved route_c minimal execution exists on local 1.5B but remained sparse at 1/24.",
            "120/121 promoted route_c to a better_and_stable refined baseline at 1/8.",
            "123 materialized an anchor-aware follow-up around csqa-pilot-021__targeted rather than reopening blind budget expansion.",
            "124 shows whether that anchor-aware subset turns the same single-anchor regime into a denser working slice.",
        ],
        "current_characterization": (
            "anchor_aware_route_c_is_denser_but_still_single_anchor"
            if anchor_density > refined_density
            else "refined_route_c_remains_the_more_honest_working_baseline"
        ),
    }
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "recommended_next_step": (
            "confirm_anchor_aware_route_c_stability_before_any_budget_expansion"
            if anchor_density > refined_density
            else "keep_refined_route_c_as_working_baseline_before_any_anchor_expansion"
        ),
        "why": (
            [
                "Anchor-aware follow-up improves density over the 1/8 refined baseline.",
                "The gain still comes from the same single positive anchor, so the next honest test is stability rather than budget expansion.",
                "Blind budget expansion remains unsupported because the known universe is still extremely sparse in absolute positives.",
            ]
            if anchor_density > refined_density
            else [
                "Anchor-aware follow-up did not beat the refined 1/8 baseline strongly enough.",
                "The refined route_c baseline remains the better-supported working reference.",
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

    write_json(output_dir / "route_c_original_refined_anchor_comparison.json", comparison)
    write_json(output_dir / "route_c_anchor_analysis_summary.json", summary)
    write_json(output_dir / "route_c_anchor_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "comparison": str((output_dir / "route_c_original_refined_anchor_comparison.json").resolve()),
            "summary": str((output_dir / "route_c_anchor_analysis_summary.json").resolve()),
            "recommendation": str((output_dir / "route_c_anchor_next_step_recommendation.json").resolve()),
        },
    }
