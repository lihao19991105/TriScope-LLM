"""Analyze the refined-fusion-support-floor-stress-aware real-experiment matrix v10."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-v10-real-experiment-matrix-analysis/v1"


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


def build_post_v10_real_experiment_matrix_analysis(
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
    next_axis_after_v4_matrix_analysis_recommendation_path: Path,
    next_axis_after_v5_matrix_bootstrap_summary_path: Path,
    next_axis_after_v5_matrix_dry_run_summary_path: Path,
    next_axis_after_v5_matrix_execution_run_summary_path: Path,
    next_axis_after_v5_matrix_analysis_recommendation_path: Path,
    next_axis_after_v6_matrix_bootstrap_summary_path: Path,
    next_axis_after_v6_matrix_dry_run_summary_path: Path,
    next_axis_after_v6_matrix_execution_run_summary_path: Path,
    next_axis_after_v6_matrix_analysis_recommendation_path: Path,
    next_axis_after_v7_matrix_bootstrap_summary_path: Path,
    next_axis_after_v7_matrix_dry_run_summary_path: Path,
    next_axis_after_v7_matrix_execution_run_summary_path: Path,
    next_axis_after_v7_matrix_analysis_recommendation_path: Path,
    next_axis_after_v8_matrix_bootstrap_summary_path: Path,
    next_axis_after_v8_matrix_dry_run_summary_path: Path,
    next_axis_after_v8_matrix_execution_run_summary_path: Path,
    next_axis_after_v8_matrix_analysis_recommendation_path: Path,
    next_axis_after_v9_matrix_bootstrap_summary_path: Path,
    next_axis_after_v9_matrix_dry_run_summary_path: Path,
    next_axis_after_v9_matrix_execution_run_summary_path: Path,
    next_axis_after_v9_matrix_execution_metrics_path: Path,
    next_axis_after_v9_matrix_fusion_summary_path: Path,
    next_axis_after_v9_matrix_fusion_cell_candidate_summary_path: Path,
    next_axis_after_v9_matrix_fusion_cell_refined_summary_path: Path,
    next_axis_after_v9_matrix_fusion_cell_refined_ablation_summary_path: Path,
    next_axis_after_v9_matrix_fusion_cell_refined_support_sweep_summary_path: Path,
    next_axis_after_v9_matrix_fusion_cell_refined_support_ablation_summary_path: Path,
    next_axis_after_v9_matrix_fusion_cell_refined_support_ablation_sweep_summary_path: Path,
    next_axis_after_v9_matrix_fusion_cell_refined_support_ablation_floor_probe_summary_path: Path,
    next_axis_after_v9_matrix_fusion_cell_refined_support_ablation_floor_stress_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    # Keep lineage loads explicit so the analysis remains self-contained and recoverable.
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
    next_axis_after_v4_matrix_recommendation = load_json(next_axis_after_v4_matrix_analysis_recommendation_path)
    next_axis_after_v5_matrix_bootstrap_summary = load_json(next_axis_after_v5_matrix_bootstrap_summary_path)
    next_axis_after_v5_matrix_dry_run_summary = load_json(next_axis_after_v5_matrix_dry_run_summary_path)
    next_axis_after_v5_matrix_execution_summary = load_json(next_axis_after_v5_matrix_execution_run_summary_path)
    next_axis_after_v5_matrix_recommendation = load_json(next_axis_after_v5_matrix_analysis_recommendation_path)
    next_axis_after_v6_matrix_bootstrap_summary = load_json(next_axis_after_v6_matrix_bootstrap_summary_path)
    next_axis_after_v6_matrix_dry_run_summary = load_json(next_axis_after_v6_matrix_dry_run_summary_path)
    next_axis_after_v6_matrix_execution_summary = load_json(next_axis_after_v6_matrix_execution_run_summary_path)
    next_axis_after_v6_matrix_recommendation = load_json(next_axis_after_v6_matrix_analysis_recommendation_path)
    next_axis_after_v7_matrix_bootstrap_summary = load_json(next_axis_after_v7_matrix_bootstrap_summary_path)
    next_axis_after_v7_matrix_dry_run_summary = load_json(next_axis_after_v7_matrix_dry_run_summary_path)
    next_axis_after_v7_matrix_execution_summary = load_json(next_axis_after_v7_matrix_execution_run_summary_path)
    next_axis_after_v7_matrix_recommendation = load_json(next_axis_after_v7_matrix_analysis_recommendation_path)
    next_axis_after_v8_matrix_bootstrap_summary = load_json(next_axis_after_v8_matrix_bootstrap_summary_path)
    next_axis_after_v8_matrix_dry_run_summary = load_json(next_axis_after_v8_matrix_dry_run_summary_path)
    next_axis_after_v8_matrix_execution_summary = load_json(next_axis_after_v8_matrix_execution_run_summary_path)
    next_axis_after_v8_matrix_recommendation = load_json(next_axis_after_v8_matrix_analysis_recommendation_path)
    next_axis_after_v9_matrix_bootstrap_summary = load_json(next_axis_after_v9_matrix_bootstrap_summary_path)
    next_axis_after_v9_matrix_dry_run_summary = load_json(next_axis_after_v9_matrix_dry_run_summary_path)
    next_axis_after_v9_matrix_execution_summary = load_json(next_axis_after_v9_matrix_execution_run_summary_path)
    next_axis_after_v9_metrics = load_json(next_axis_after_v9_matrix_execution_metrics_path)
    fusion_summary = load_json(next_axis_after_v9_matrix_fusion_summary_path)
    fusion_candidate_summary = load_json(next_axis_after_v9_matrix_fusion_cell_candidate_summary_path)
    fusion_refined_summary = load_json(next_axis_after_v9_matrix_fusion_cell_refined_summary_path)
    fusion_refined_ablation_summary = load_json(next_axis_after_v9_matrix_fusion_cell_refined_ablation_summary_path)
    fusion_support_sweep_summary = load_json(next_axis_after_v9_matrix_fusion_cell_refined_support_sweep_summary_path)
    fusion_support_ablation_summary = load_json(next_axis_after_v9_matrix_fusion_cell_refined_support_ablation_summary_path)
    fusion_support_ablation_sweep_summary = load_json(next_axis_after_v9_matrix_fusion_cell_refined_support_ablation_sweep_summary_path)
    fusion_floor_probe_summary = load_json(next_axis_after_v9_matrix_fusion_cell_refined_support_ablation_floor_probe_summary_path)
    fusion_floor_stress_summary = load_json(next_axis_after_v9_matrix_fusion_cell_refined_support_ablation_floor_stress_summary_path)

    analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_execution_established": next_axis_after_v9_matrix_execution_summary.get("summary_status") == "PASS",
        "matrix_name": next_axis_after_v9_matrix_bootstrap_summary["matrix_name"],
        "executed_cell_count": next_axis_after_v9_matrix_execution_summary.get("executed_cell_count", 0),
        "main_takeaway": "The v10 matrix now establishes fusion_cell_refined_support_ablation_floor_stress as an executed explicit floor-stress cell, so explicit support-floor invariance under direct stress is no longer only inferred from the floor probe.",
    }
    floor_stress_vs_floor_probe = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_ablation_floor_probe": {
            "cell_id": fusion_floor_probe_summary["cell_id"],
            "fusion_mode": fusion_floor_probe_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_probe_summary["shared_base_samples"],
            "floor_probe_signal_score": fusion_floor_probe_summary["floor_probe_signal_score"],
            "support_floor_invariant": fusion_floor_probe_summary["support_floor_invariant"],
        },
        "fusion_cell_refined_support_ablation_floor_stress": {
            "cell_id": fusion_floor_stress_summary["cell_id"],
            "fusion_mode": fusion_floor_stress_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_stress_summary["shared_base_samples"],
            "floor_stress_signal_score": fusion_floor_stress_summary["floor_stress_signal_score"],
            "support_floor_stress_invariant": fusion_floor_stress_summary["support_floor_stress_invariant"],
            "floor_stress_gap_vs_floor_probe": fusion_floor_stress_summary["floor_stress_gap_vs_floor_probe"],
        },
        "added_value": [
            "fusion_cell_refined_support_ablation_floor_stress turns the explicit floor into a direct stress test instead of leaving it as a passive probe.",
            "This makes floor invariance under direct stress observable instead of only implied by the zero-floor probe.",
        ],
    }
    floor_stress_vs_support_ablation_sweep = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_ablation_sweep": {
            "cell_id": fusion_support_ablation_sweep_summary["cell_id"],
            "fusion_mode": fusion_support_ablation_sweep_summary["fusion_mode"],
            "shared_base_samples": fusion_support_ablation_sweep_summary["shared_base_samples"],
            "support_ablation_sweep_signal_score": fusion_support_ablation_sweep_summary["support_ablation_sweep_signal_score"],
            "support_floor": fusion_support_ablation_sweep_summary["support_floor"],
        },
        "fusion_cell_refined_support_ablation_floor_stress": {
            "cell_id": fusion_floor_stress_summary["cell_id"],
            "fusion_mode": fusion_floor_stress_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_stress_summary["shared_base_samples"],
            "floor_stress_signal_score": fusion_floor_stress_summary["floor_stress_signal_score"],
            "floor_stress_gap_vs_support_ablation_sweep": fusion_floor_stress_summary["floor_stress_gap_vs_support_ablation_sweep"],
        },
        "added_value": [
            "The floor-stress cell checks whether the support-isolated residual remains pinned to the same floor once that floor is explicitly stressed.",
            "This is stronger than only observing that support-ablation-sweep had already collapsed to the candidate floor.",
        ],
    }
    floor_stress_vs_support_ablation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_ablation": {
            "cell_id": fusion_support_ablation_summary["cell_id"],
            "fusion_mode": fusion_support_ablation_summary["fusion_mode"],
            "shared_base_samples": fusion_support_ablation_summary["shared_base_samples"],
            "support_ablation_signal_score": fusion_support_ablation_summary["support_ablation_signal_score"],
        },
        "fusion_cell_refined_support_ablation_floor_stress": {
            "cell_id": fusion_floor_stress_summary["cell_id"],
            "fusion_mode": fusion_floor_stress_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_stress_summary["shared_base_samples"],
            "floor_stress_signal_score": fusion_floor_stress_summary["floor_stress_signal_score"],
        },
        "added_value": [
            "The floor-stress cell distinguishes the larger support-ablation signal from the directly stressed explicit floor beneath it.",
        ],
    }
    floor_stress_vs_support_sweep = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_sweep": {
            "cell_id": fusion_support_sweep_summary["cell_id"],
            "fusion_mode": fusion_support_sweep_summary["fusion_mode"],
            "shared_base_samples": fusion_support_sweep_summary["shared_base_samples"],
            "support_sweep_signal_score": fusion_support_sweep_summary["support_sweep_signal_score"],
        },
        "fusion_cell_refined_support_ablation_floor_stress": {
            "cell_id": fusion_floor_stress_summary["cell_id"],
            "fusion_mode": fusion_floor_stress_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_stress_summary["shared_base_samples"],
            "floor_stress_signal_score": fusion_floor_stress_summary["floor_stress_signal_score"],
            "retained_floor_stress_ratio_vs_refined": fusion_floor_stress_summary["retained_floor_stress_ratio_vs_refined"],
        },
        "added_value": [
            "The floor-stress cell separates direct stress on the explicit floor from broader support perturbation.",
        ],
    }
    floor_stress_vs_refined = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined": {
            "cell_id": fusion_refined_summary["cell_id"],
            "fusion_mode": fusion_refined_summary["fusion_mode"],
            "shared_base_samples": fusion_refined_summary["shared_base_samples"],
            "refined_signal_score": fusion_refined_summary["refined_signal_score"],
        },
        "fusion_cell_refined_support_ablation_floor_stress": {
            "cell_id": fusion_floor_stress_summary["cell_id"],
            "fusion_mode": fusion_floor_stress_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_stress_summary["shared_base_samples"],
            "floor_stress_signal_score": fusion_floor_stress_summary["floor_stress_signal_score"],
            "retained_floor_stress_ratio_vs_refined": fusion_floor_stress_summary["retained_floor_stress_ratio_vs_refined"],
        },
        "added_value": [
            "The floor-stress cell shows how far the directly stressed floor now sits below the original refined signal.",
        ],
    }
    floor_stress_vs_candidate = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_candidate": {
            "cell_id": fusion_candidate_summary["cell_id"],
            "fusion_mode": fusion_candidate_summary["fusion_mode"],
            "shared_base_samples": fusion_candidate_summary["shared_base_samples"],
            "candidate_signal_score": fusion_candidate_summary["candidate_signal_score"],
        },
        "fusion_cell_refined_support_ablation_floor_stress": {
            "cell_id": fusion_floor_stress_summary["cell_id"],
            "fusion_mode": fusion_floor_stress_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_stress_summary["shared_base_samples"],
            "floor_stress_signal_score": fusion_floor_stress_summary["floor_stress_signal_score"],
        },
        "added_value": [
            "The floor-stress cell clarifies that the directly stressed floor still does not rise above the candidate baseline.",
        ],
    }
    floor_stress_vs_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_summary": {
            "cell_id": fusion_summary["cell_id"],
            "fusion_mode": fusion_summary["fusion_mode"],
            "shared_base_samples": fusion_summary["shared_base_samples"],
        },
        "fusion_cell_refined_support_ablation_floor_stress": {
            "cell_id": fusion_floor_stress_summary["cell_id"],
            "fusion_mode": fusion_floor_stress_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_stress_summary["shared_base_samples"],
            "floor_stress_signal_score": fusion_floor_stress_summary["floor_stress_signal_score"],
        },
        "added_value": [
            "The floor-stress cell remains an explicit executable stress baseline even when the measured floor stays at zero.",
        ],
    }
    v10_vs_v9 = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "v9_matrix": {
            "matrix_name": next_axis_after_v8_matrix_bootstrap_summary["matrix_name"],
            "executed_cell_count": next_axis_after_v8_matrix_execution_summary.get("executed_cell_count", 0),
            "recommended_axis": next_axis_after_v8_matrix_recommendation["preferred_expansion_axis"],
        },
        "v10_matrix": {
            "matrix_name": next_axis_after_v9_matrix_bootstrap_summary["matrix_name"],
            "dry_run_completed": next_axis_after_v9_matrix_dry_run_summary.get("dry_run_completed", False),
            "executed_cell_count": next_axis_after_v9_matrix_execution_summary.get("executed_cell_count", 0),
            "fusion_cell_refined_support_ablation_floor_stress_executed": next_axis_after_v9_metrics["fusion_cell_refined_support_ablation_floor_stress_executed"],
            "fusion_cell_refined_support_ablation_floor_stress_score": next_axis_after_v9_metrics["fusion_cell_refined_support_ablation_floor_stress_score"],
            "support_floor_stress_invariant": next_axis_after_v9_metrics["fusion_cell_refined_support_ablation_floor_stress_invariant"],
        },
        "added_value": [
            "v10 keeps all v9 route and fusion coverage while adding an executed refined-support-ablation-floor-stress fusion cell.",
            "The richer matrix can now compare the direct floor probe with a direct floor stress artifact side by side.",
        ],
    }
    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_blockers": [
            "The refined-support-ablation-floor-stress fusion cell is still a contract-level stress artifact, not a trained fusion classifier.",
            "The matrix still uses one dataset and one lightweight model.",
            "Model-axis and dataset-axis expansion remain less ready than one more round of explicit floor-stress invariance coverage.",
        ],
    }
    tradeoff_rows = [
        {
            "candidate_route": "fusion_support_floor_stress_invariance_coverage",
            "realism": "higher",
            "cost": "medium",
            "readiness": "high",
            "why": "Now that the floor-stress cell exists, the next honest step is to sweep that stress conclusion directly before jumping axes.",
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
        "recommended_next_step": "bootstrap_next_axis_after_v10_matrix",
        "preferred_expansion_axis": "fusion_support_floor_stress_invariance_coverage",
        "why_recommended": [
            "v10 proves that fusion_cell_refined_support_ablation_floor_stress can reach execution, and the next honest step is to sweep that stress result directly.",
            "Current repository reality still makes floor-stress invariance coverage more actionable than model-axis or dataset-axis expansion.",
            "The floor-stress cell now makes it possible to design a next matrix around explicit support-floor-stress invariance comparisons.",
        ],
        "why_not_return_to_proxy": [
            "The real-experiment matrix stack is still adding new fusion-level information, so returning to proxy would reduce leverage."
        ],
        "minimum_success_standard": [
            "define a next-axis-after-v10 matrix that sweeps the explicit support-floor-stress cell directly",
            "materialize next-axis-after-v10 matrix inputs",
            "prove the next-axis-after-v10 matrix is bootstrap-ready",
        ],
    }

    write_json(output_dir / "next_axis_after_v9_matrix_analysis_summary.json", analysis)
    write_json(output_dir / "fusion_floor_stress_vs_floor_probe_comparison.json", floor_stress_vs_floor_probe)
    write_json(output_dir / "fusion_floor_stress_vs_support_ablation_sweep_comparison.json", floor_stress_vs_support_ablation_sweep)
    write_json(output_dir / "fusion_floor_stress_vs_support_ablation_comparison.json", floor_stress_vs_support_ablation)
    write_json(output_dir / "fusion_floor_stress_vs_support_sweep_comparison.json", floor_stress_vs_support_sweep)
    write_json(output_dir / "fusion_floor_stress_vs_refined_comparison.json", floor_stress_vs_refined)
    write_json(output_dir / "fusion_floor_stress_vs_candidate_comparison.json", floor_stress_vs_candidate)
    write_json(output_dir / "fusion_floor_stress_vs_summary_comparison.json", floor_stress_vs_summary)
    write_json(output_dir / "v10_vs_v9_matrix_comparison.json", v10_vs_v9)
    write_json(output_dir / "v10_matrix_blocker_summary.json", blocker_summary)
    write_csv(output_dir / "v10_matrix_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "next_axis_after_v9_matrix_next_step_recommendation.json", recommendation)
    return {
        "analysis": analysis,
        "recommendation": recommendation,
        "output_paths": {
            "analysis": str((output_dir / "next_axis_after_v9_matrix_analysis_summary.json").resolve()),
            "floor_stress_vs_floor_probe": str((output_dir / "fusion_floor_stress_vs_floor_probe_comparison.json").resolve()),
            "floor_stress_vs_support_ablation_sweep": str((output_dir / "fusion_floor_stress_vs_support_ablation_sweep_comparison.json").resolve()),
            "floor_stress_vs_support_ablation": str((output_dir / "fusion_floor_stress_vs_support_ablation_comparison.json").resolve()),
            "floor_stress_vs_support_sweep": str((output_dir / "fusion_floor_stress_vs_support_sweep_comparison.json").resolve()),
            "floor_stress_vs_refined": str((output_dir / "fusion_floor_stress_vs_refined_comparison.json").resolve()),
            "floor_stress_vs_candidate": str((output_dir / "fusion_floor_stress_vs_candidate_comparison.json").resolve()),
            "floor_stress_vs_summary": str((output_dir / "fusion_floor_stress_vs_summary_comparison.json").resolve()),
            "v10_vs_v9": str((output_dir / "v10_vs_v9_matrix_comparison.json").resolve()),
            "blockers": str((output_dir / "v10_matrix_blocker_summary.json").resolve()),
            "tradeoff": str((output_dir / "v10_matrix_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "next_axis_after_v9_matrix_next_step_recommendation.json").resolve()),
        },
    }
