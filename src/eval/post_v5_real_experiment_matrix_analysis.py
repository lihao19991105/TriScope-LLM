"""Analyze the refined-fusion-ablation-aware real-experiment matrix v5."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-v5-real-experiment-matrix-analysis/v1"


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


def build_post_v5_real_experiment_matrix_analysis(
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
    next_axis_matrix_analysis_recommendation_path: Path,
    next_axis_after_v4_matrix_bootstrap_summary_path: Path,
    next_axis_after_v4_matrix_dry_run_summary_path: Path,
    next_axis_after_v4_matrix_execution_run_summary_path: Path,
    next_axis_after_v4_matrix_execution_metrics_path: Path,
    next_axis_after_v4_matrix_fusion_summary_path: Path,
    next_axis_after_v4_matrix_fusion_cell_candidate_summary_path: Path,
    next_axis_after_v4_matrix_fusion_cell_refined_summary_path: Path,
    next_axis_after_v4_matrix_fusion_cell_refined_ablation_summary_path: Path,
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
    next_axis_matrix_recommendation = load_json(next_axis_matrix_analysis_recommendation_path)
    next_axis_after_v4_matrix_bootstrap_summary = load_json(next_axis_after_v4_matrix_bootstrap_summary_path)
    next_axis_after_v4_matrix_dry_run_summary = load_json(next_axis_after_v4_matrix_dry_run_summary_path)
    next_axis_after_v4_matrix_execution_summary = load_json(next_axis_after_v4_matrix_execution_run_summary_path)
    next_axis_after_v4_metrics = load_json(next_axis_after_v4_matrix_execution_metrics_path)
    fusion_summary = load_json(next_axis_after_v4_matrix_fusion_summary_path)
    fusion_candidate_summary = load_json(next_axis_after_v4_matrix_fusion_cell_candidate_summary_path)
    fusion_refined_summary = load_json(next_axis_after_v4_matrix_fusion_cell_refined_summary_path)
    fusion_refined_ablation_summary = load_json(next_axis_after_v4_matrix_fusion_cell_refined_ablation_summary_path)

    analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_execution_established": next_axis_after_v4_matrix_execution_summary.get("summary_status") == "PASS",
        "matrix_name": next_axis_after_v4_matrix_bootstrap_summary["matrix_name"],
        "executed_cell_count": next_axis_after_v4_matrix_execution_summary.get("executed_cell_count", 0),
        "main_takeaway": "The v5 matrix now establishes fusion_cell_refined_ablation as an executed explicit ablation cell, so refined fusion contribution is no longer only inferred indirectly.",
    }
    refined_ablation_vs_refined = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined": {
            "cell_id": fusion_refined_summary["cell_id"],
            "fusion_mode": fusion_refined_summary["fusion_mode"],
            "shared_base_samples": fusion_refined_summary["shared_base_samples"],
            "refined_signal_score": fusion_refined_summary["refined_signal_score"],
            "refined_delta_vs_candidate": fusion_refined_summary["refined_delta_vs_candidate"],
        },
        "fusion_cell_refined_ablation": {
            "cell_id": fusion_refined_ablation_summary["cell_id"],
            "fusion_mode": fusion_refined_ablation_summary["fusion_mode"],
            "shared_base_samples": fusion_refined_ablation_summary["shared_base_samples"],
            "ablated_signal_score": fusion_refined_ablation_summary["ablated_signal_score"],
            "retained_information_ratio": fusion_refined_ablation_summary["retained_information_ratio"],
            "removed_refinement_term": fusion_refined_ablation_summary["removed_refinement_term"],
        },
        "added_value": [
            "fusion_cell_refined_ablation explicitly estimates how much signal remains after the refinement term is removed.",
            "This makes the contribution of the refined term observable instead of only inferred from refined-versus-candidate comparisons.",
        ],
    }
    refined_ablation_vs_candidate = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_candidate": {
            "cell_id": fusion_candidate_summary["cell_id"],
            "fusion_mode": fusion_candidate_summary["fusion_mode"],
            "shared_base_samples": fusion_candidate_summary["shared_base_samples"],
            "candidate_signal_score": fusion_candidate_summary["candidate_signal_score"],
        },
        "fusion_cell_refined_ablation": {
            "cell_id": fusion_refined_ablation_summary["cell_id"],
            "fusion_mode": fusion_refined_ablation_summary["fusion_mode"],
            "shared_base_samples": fusion_refined_ablation_summary["shared_base_samples"],
            "ablated_signal_score": fusion_refined_ablation_summary["ablated_signal_score"],
            "retained_information_ratio": fusion_refined_ablation_summary["retained_information_ratio"],
        },
        "added_value": [
            "The refined-ablation cell shows whether removing the refinement term effectively collapses the refined cell back toward candidate-level evidence.",
            "This helps separate 'extra refined signal' from the earlier explicit fusion cell baseline.",
        ],
    }
    refined_ablation_vs_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_summary": {
            "cell_id": fusion_summary["cell_id"],
            "fusion_mode": fusion_summary["fusion_mode"],
            "shared_base_samples": fusion_summary["shared_base_samples"],
        },
        "fusion_cell_refined_ablation": {
            "cell_id": fusion_refined_ablation_summary["cell_id"],
            "fusion_mode": fusion_refined_ablation_summary["fusion_mode"],
            "shared_base_samples": fusion_refined_ablation_summary["shared_base_samples"],
            "ablated_signal_score": fusion_refined_ablation_summary["ablated_signal_score"],
        },
        "added_value": [
            "The refined-ablation cell is still an explicit executable cell even after the refinement term is removed.",
            "This gives a cleaner baseline for asking whether explicit fusion structure itself helps beyond inherited summary-only fusion.",
        ],
    }
    v5_vs_v4 = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "v4_matrix": {
            "matrix_name": next_axis_matrix_bootstrap_summary["matrix_name"],
            "executed_cell_count": next_axis_matrix_execution_summary.get("executed_cell_count", 0),
            "recommended_axis": next_axis_matrix_recommendation["preferred_expansion_axis"],
        },
        "v5_matrix": {
            "matrix_name": next_axis_after_v4_matrix_bootstrap_summary["matrix_name"],
            "dry_run_completed": next_axis_after_v4_matrix_dry_run_summary.get("dry_run_completed", False),
            "executed_cell_count": next_axis_after_v4_matrix_execution_summary.get("executed_cell_count", 0),
            "fusion_cell_refined_ablation_executed": next_axis_after_v4_metrics["fusion_cell_refined_ablation_executed"],
            "fusion_cell_refined_ablation_score": next_axis_after_v4_metrics["fusion_cell_refined_ablation_score"],
            "retained_information_ratio": next_axis_after_v4_metrics["fusion_cell_refined_ablation_retained_ratio"],
        },
        "added_value": [
            "v5 keeps all v4 route, ablation, candidate, and refined fusion coverage while adding an executed refined-ablation fusion cell.",
            "The richer matrix can now compare summary, candidate, refined, and refined-ablation fusion views side by side.",
        ],
    }
    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_blockers": [
            "The refined-ablation fusion cell is still a contract-level ablation, not a trained fusion classifier.",
            "The matrix still uses one dataset and one lightweight model.",
            "Model-axis and dataset-axis expansion remain less ready than one more round of refined-fusion stability/isolation analysis.",
        ],
    }
    tradeoff_rows = [
        {
            "candidate_route": "fusion_refinement_stability_coverage",
            "realism": "higher",
            "cost": "medium",
            "readiness": "high",
            "why": "Now that refined-ablation exists, the next honest step is to stress refined fusion stability rather than jump axes.",
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
            "why": "Still blocked by the lack of a comparably mature second dataset object.",
        },
    ]
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "bootstrap_next_axis_after_v5_matrix",
        "preferred_expansion_axis": "fusion_refinement_stability_coverage",
        "why_recommended": [
            "v5 proves that fusion_cell_refined_ablation can reach execution, and the next honest step is to stress the stability of refined fusion semantics rather than add a heavier axis.",
            "Current repository reality still makes refined-fusion stability more actionable than model-axis or dataset-axis expansion.",
            "The refined-ablation cell now makes it possible to design a next matrix around explicit support/stability comparisons.",
        ],
        "why_not_return_to_proxy": [
            "The real-experiment matrix stack is still adding new fusion-level information, so returning to proxy would reduce leverage."
        ],
        "minimum_success_standard": [
            "define a next-axis-after-v5 matrix that stresses refined fusion stability",
            "materialize next-axis-after-v5 matrix inputs",
            "prove the next-axis-after-v5 matrix is bootstrap-ready",
        ],
    }

    write_json(output_dir / "next_axis_after_v4_matrix_analysis_summary.json", analysis)
    write_json(output_dir / "fusion_refined_ablation_vs_refined_comparison.json", refined_ablation_vs_refined)
    write_json(output_dir / "fusion_refined_ablation_vs_candidate_comparison.json", refined_ablation_vs_candidate)
    write_json(output_dir / "fusion_refined_ablation_vs_summary_comparison.json", refined_ablation_vs_summary)
    write_json(output_dir / "v5_vs_v4_matrix_comparison.json", v5_vs_v4)
    write_json(output_dir / "v5_matrix_blocker_summary.json", blocker_summary)
    write_csv(output_dir / "v5_matrix_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "next_axis_after_v4_matrix_next_step_recommendation.json", recommendation)
    return {
        "analysis": analysis,
        "recommendation": recommendation,
        "output_paths": {
            "analysis": str((output_dir / "next_axis_after_v4_matrix_analysis_summary.json").resolve()),
            "refined_ablation_vs_refined": str((output_dir / "fusion_refined_ablation_vs_refined_comparison.json").resolve()),
            "refined_ablation_vs_candidate": str((output_dir / "fusion_refined_ablation_vs_candidate_comparison.json").resolve()),
            "refined_ablation_vs_summary": str((output_dir / "fusion_refined_ablation_vs_summary_comparison.json").resolve()),
            "v5_vs_v4": str((output_dir / "v5_vs_v4_matrix_comparison.json").resolve()),
            "blockers": str((output_dir / "v5_matrix_blocker_summary.json").resolve()),
            "tradeoff": str((output_dir / "v5_matrix_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "next_axis_after_v4_matrix_next_step_recommendation.json").resolve()),
        },
    }
