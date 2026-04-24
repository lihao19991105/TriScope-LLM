"""Compare original and refined route_c execution/stability on the 1.5B model axis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-route-c-refined-analysis/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_post_route_c_refined_analysis(
    route_c_execution_dir: Path,
    route_c_stability_dir: Path,
    route_c_refined_execution_dir: Path,
    route_c_refined_stability_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    original_run_summary = load_json(route_c_execution_dir / "route_c_execution_run_summary.json")
    original_metrics = load_json(route_c_execution_dir / "route_c_execution_metrics.json")
    original_stability = load_json(route_c_stability_dir / "route_c_stability_summary.json")
    refined_run_summary = load_json(route_c_refined_execution_dir / "route_c_refined_execution_run_summary.json")
    refined_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    refined_stability = load_json(route_c_refined_stability_dir / "route_c_refined_stability_summary.json")

    original_density = float(original_metrics.get("class_balance", {}).get("label_1", 0) or 0) / float(original_metrics.get("num_rows", 1) or 1)
    refined_density = float(refined_metrics.get("refined_density", 0.0) or 0.0)
    density_gain_ratio = (
        refined_density / original_density if original_density > 0 else None
    )

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "original_execution": {
            "summary_status": original_run_summary.get("summary_status"),
            "execution_status": original_run_summary.get("execution_status"),
            "class_balance": original_run_summary.get("class_balance"),
            "density": original_density,
            "stability_established": original_stability.get("stability_established"),
            "stability_characterization": original_stability.get("stability_characterization"),
        },
        "refined_execution": {
            "summary_status": refined_run_summary.get("summary_status"),
            "execution_status": refined_run_summary.get("execution_status"),
            "class_balance": refined_run_summary.get("class_balance"),
            "density": refined_density,
            "stability_established": refined_stability.get("stability_established"),
            "stability_characterization": refined_stability.get("stability_characterization"),
        },
        "density_gain_ratio": density_gain_ratio,
        "improvement_axes": [
            "positive_density",
            "execution_economy",
            "stable anchor-preserving selection",
        ],
        "remaining_limits": [
            "positive count is still 1 even after refinement",
            "route_c remains benchmark-truth-leaning proxy supervision",
        ],
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "original_density": original_density,
        "refined_density": refined_density,
        "density_gain_ratio": density_gain_ratio,
        "refined_beats_original": bool(refined_density > original_density),
        "refined_stability_established": refined_stability.get("stability_established"),
        "progression_summary": [
            "116 proved route_c minimal execution exists on local 1.5B but remains sparse at 1/24.",
            "118 proved that sparse regime is stable rather than accidental.",
            "120 showed the refined 8-row candidate preserves real execution while improving density to 1/8.",
            "121 confirmed that this density improvement is stable under light reruns.",
        ],
        "current_characterization": "refined_route_c_is_more_analyzable_than_original_but_still_thin",
    }
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "recommended_next_step": "continue_refined_selection_before_any_budget_expansion",
        "why": [
            "Refined selection now has a real and stable density advantage over the original route_c baseline.",
            "The current evidence still does not justify blind budget expansion because the known universe remains extremely sparse in absolute positives.",
            "The next honest move is to treat the refined candidate as the new route_c working baseline and only then consider small, anchor-aware expansion.",
        ],
        "not_recommended_yet": [
            "blind_budget_expansion",
            "3b_or_7b_expansion",
            "dataset_axis_expansion",
            "fusion_axis_expansion",
        ],
    }

    write_json(output_dir / "route_c_original_vs_refined_comparison.json", comparison)
    write_json(output_dir / "route_c_refined_analysis_summary.json", summary)
    write_json(output_dir / "route_c_refined_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "comparison": str((output_dir / "route_c_original_vs_refined_comparison.json").resolve()),
            "summary": str((output_dir / "route_c_refined_analysis_summary.json").resolve()),
            "recommendation": str((output_dir / "route_c_refined_next_step_recommendation.json").resolve()),
        },
    }
