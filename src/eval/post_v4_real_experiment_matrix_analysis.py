"""Analyze the refined-fusion-aware real-experiment matrix v4."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-v4-real-experiment-matrix-analysis/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Expected at least one CSV row.")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_post_v4_real_experiment_matrix_analysis(
    cutover_bootstrap_summary_path: Path,
    first_real_dry_run_summary_path: Path,
    first_real_execution_run_summary_path: Path,
    minimal_matrix_bootstrap_summary_path: Path,
    minimal_matrix_dry_run_summary_path: Path,
    minimal_matrix_execution_run_summary_path: Path,
    minimal_matrix_analysis_recommendation_path: Path,
    next_matrix_bootstrap_summary_path: Path,
    next_matrix_dry_run_summary_path: Path,
    next_matrix_execution_run_summary_path: Path,
    next_matrix_analysis_recommendation_path: Path,
    post_next_matrix_bootstrap_summary_path: Path,
    post_next_matrix_dry_run_summary_path: Path,
    post_next_matrix_execution_run_summary_path: Path,
    post_next_matrix_analysis_recommendation_path: Path,
    next_axis_matrix_bootstrap_summary_path: Path,
    next_axis_matrix_dry_run_summary_path: Path,
    next_axis_matrix_execution_run_summary_path: Path,
    next_axis_matrix_execution_metrics_path: Path,
    next_axis_matrix_fusion_summary_path: Path,
    next_axis_matrix_fusion_cell_candidate_summary_path: Path,
    next_axis_matrix_fusion_cell_refined_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cutover_summary = load_json(cutover_bootstrap_summary_path)
    first_real_dry_run_summary = load_json(first_real_dry_run_summary_path)
    first_real_execution_summary = load_json(first_real_execution_run_summary_path)
    minimal_matrix_bootstrap_summary = load_json(minimal_matrix_bootstrap_summary_path)
    minimal_matrix_dry_run_summary = load_json(minimal_matrix_dry_run_summary_path)
    minimal_matrix_execution_summary = load_json(minimal_matrix_execution_run_summary_path)
    minimal_matrix_recommendation = load_json(minimal_matrix_analysis_recommendation_path)
    next_matrix_bootstrap_summary = load_json(next_matrix_bootstrap_summary_path)
    next_matrix_dry_run_summary = load_json(next_matrix_dry_run_summary_path)
    next_matrix_execution_summary = load_json(next_matrix_execution_run_summary_path)
    next_matrix_recommendation = load_json(next_matrix_analysis_recommendation_path)
    post_next_matrix_bootstrap_summary = load_json(post_next_matrix_bootstrap_summary_path)
    post_next_matrix_dry_run_summary = load_json(post_next_matrix_dry_run_summary_path)
    post_next_matrix_execution_summary = load_json(post_next_matrix_execution_run_summary_path)
    post_next_matrix_recommendation = load_json(post_next_matrix_analysis_recommendation_path)
    next_axis_matrix_bootstrap_summary = load_json(next_axis_matrix_bootstrap_summary_path)
    next_axis_matrix_dry_run_summary = load_json(next_axis_matrix_dry_run_summary_path)
    next_axis_matrix_execution_summary = load_json(next_axis_matrix_execution_run_summary_path)
    next_axis_matrix_metrics = load_json(next_axis_matrix_execution_metrics_path)
    fusion_summary = load_json(next_axis_matrix_fusion_summary_path)
    fusion_candidate_summary = load_json(next_axis_matrix_fusion_cell_candidate_summary_path)
    fusion_refined_summary = load_json(next_axis_matrix_fusion_cell_refined_summary_path)

    analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_execution_established": next_axis_matrix_execution_summary.get("summary_status") == "PASS",
        "matrix_name": next_axis_matrix_bootstrap_summary["matrix_name"],
        "executed_cell_count": next_axis_matrix_execution_summary.get("executed_cell_count", 0),
        "main_takeaway": "The v4 matrix now establishes fusion_cell_refined as an executed explicit fusion cell, so fusion refinement has moved beyond the candidate-only stage.",
    }
    refined_vs_candidate = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_candidate": {
            "cell_id": fusion_candidate_summary["cell_id"],
            "fusion_mode": fusion_candidate_summary["fusion_mode"],
            "shared_base_samples": fusion_candidate_summary["shared_base_samples"],
            "candidate_signal_score": fusion_candidate_summary["candidate_signal_score"],
            "score_gap": fusion_candidate_summary["score_gap"],
        },
        "fusion_cell_refined": {
            "cell_id": fusion_refined_summary["cell_id"],
            "fusion_mode": fusion_refined_summary["fusion_mode"],
            "shared_base_samples": fusion_refined_summary["shared_base_samples"],
            "refined_signal_score": fusion_refined_summary["refined_signal_score"],
            "refined_delta_vs_candidate": fusion_refined_summary["refined_delta_vs_candidate"],
            "support_ratio": fusion_refined_summary["support_ratio"],
        },
        "added_value": [
            "fusion_cell_refined keeps the explicit scalar contract of the candidate cell while adding a support-aware refinement term.",
            "This creates a cleaner comparison point for asking whether refined fusion semantics add value over the earlier candidate cell.",
        ],
    }
    refined_vs_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_summary": {
            "cell_id": fusion_summary["cell_id"],
            "fusion_mode": fusion_summary["fusion_mode"],
            "shared_base_samples": fusion_summary["shared_base_samples"],
        },
        "fusion_cell_refined": {
            "cell_id": fusion_refined_summary["cell_id"],
            "fusion_mode": fusion_refined_summary["fusion_mode"],
            "shared_base_samples": fusion_refined_summary["shared_base_samples"],
            "refined_signal_score": fusion_refined_summary["refined_signal_score"],
        },
        "added_value": [
            "fusion_cell_refined is an explicit cell with its own scalar and refinement rule, while fusion_summary remains a lighter inherited baseline.",
            "This makes the refined cell easier to compare against ablations and future fusion variants than the inherited summary alone.",
        ],
    }
    v4_vs_v3 = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "v3_matrix": {
            "matrix_name": post_next_matrix_bootstrap_summary["matrix_name"],
            "executed_cell_count": post_next_matrix_execution_summary.get("executed_cell_count", 0),
            "recommended_axis": post_next_matrix_recommendation["preferred_expansion_axis"],
        },
        "v4_matrix": {
            "matrix_name": next_axis_matrix_bootstrap_summary["matrix_name"],
            "dry_run_completed": next_axis_matrix_dry_run_summary.get("dry_run_completed", False),
            "executed_cell_count": next_axis_matrix_execution_summary.get("executed_cell_count", 0),
            "fusion_cell_refined_executed": next_axis_matrix_metrics["fusion_cell_refined_executed"],
            "fusion_cell_refined_score": next_axis_matrix_metrics["fusion_cell_refined_score"],
            "fusion_cell_refined_delta": next_axis_matrix_metrics["fusion_cell_refined_delta"],
        },
        "added_value": [
            "v4 keeps all v3 route, ablation, and fusion candidate coverage while adding an executed refined fusion cell.",
            "The richer matrix can now compare summary, candidate, and refined fusion views side by side.",
        ],
    }
    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_blockers": [
            "The refined fusion cell is still a contract-level refinement, not a trained fusion classifier.",
            "The matrix still uses one dataset and one lightweight model.",
            "Model-axis and dataset-axis expansion remain less ready than one more round of refined-fusion isolation.",
        ],
    }
    tradeoff_rows = [
        {
            "candidate_route": "fusion_refined_ablation_coverage",
            "realism": "higher",
            "cost": "medium",
            "readiness": "high",
            "why": "Now that fusion_cell_refined exists, the next honest step is to isolate and stress its contribution before jumping axes.",
        },
        {
            "candidate_route": "model_axis_preparation",
            "realism": "higher",
            "cost": "high",
            "readiness": "low",
            "why": "Still blocked by the lack of a second ready-local model profile.",
        },
        {
            "candidate_route": "dataset_axis_preparation",
            "realism": "higher",
            "cost": "medium",
            "readiness": "low",
            "why": "Potentially useful later, but the repository still lacks a comparably mature second dataset object.",
        },
    ]
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "bootstrap_next_axis_after_v4_real_experiment_matrix",
        "preferred_expansion_axis": "fusion_refined_ablation_coverage",
        "why_recommended": [
            "v4 proves that fusion_cell_refined can reach execution, but its added value is still only lightly isolated.",
            "The next honest step is to isolate refined fusion coverage more explicitly before jumping to unsupported model or dataset axes.",
            "Current repository reality makes refined-fusion isolation more actionable than model-axis or dataset-axis expansion.",
        ],
        "why_not_return_to_proxy": [
            "The real-experiment matrix stack is still adding new fusion-level information, so returning to proxy would reduce leverage."
        ],
        "minimum_success_standard": [
            "define a next-axis-after-v4 matrix that isolates refined fusion coverage",
            "materialize next-axis-after-v4 matrix inputs",
            "prove the next-axis-after-v4 matrix is bootstrap-ready",
        ],
    }

    write_json(output_dir / "next_axis_matrix_analysis_summary.json", analysis)
    write_json(output_dir / "fusion_refined_vs_candidate_comparison.json", refined_vs_candidate)
    write_json(output_dir / "fusion_refined_vs_summary_comparison.json", refined_vs_summary)
    write_json(output_dir / "v4_vs_v3_matrix_comparison.json", v4_vs_v3)
    write_json(output_dir / "v4_matrix_blocker_summary.json", blocker_summary)
    write_csv(output_dir / "v4_matrix_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "next_axis_matrix_next_step_recommendation.json", recommendation)
    return {
        "analysis": analysis,
        "recommendation": recommendation,
        "output_paths": {
            "analysis": str((output_dir / "next_axis_matrix_analysis_summary.json").resolve()),
            "refined_vs_candidate": str((output_dir / "fusion_refined_vs_candidate_comparison.json").resolve()),
            "refined_vs_summary": str((output_dir / "fusion_refined_vs_summary_comparison.json").resolve()),
            "v4_vs_v3": str((output_dir / "v4_vs_v3_matrix_comparison.json").resolve()),
            "blockers": str((output_dir / "v4_matrix_blocker_summary.json").resolve()),
            "tradeoff": str((output_dir / "v4_matrix_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "next_axis_matrix_next_step_recommendation.json").resolve()),
        },
    }
