"""Analyze the refined-fusion-support-floor-probe-aware real-experiment matrix v9."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-v9-real-experiment-matrix-analysis/v1"


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


def build_post_v9_real_experiment_matrix_analysis(
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
    next_axis_after_v8_matrix_execution_metrics_path: Path,
    next_axis_after_v8_matrix_fusion_summary_path: Path,
    next_axis_after_v8_matrix_fusion_cell_candidate_summary_path: Path,
    next_axis_after_v8_matrix_fusion_cell_refined_summary_path: Path,
    next_axis_after_v8_matrix_fusion_cell_refined_ablation_summary_path: Path,
    next_axis_after_v8_matrix_fusion_cell_refined_support_sweep_summary_path: Path,
    next_axis_after_v8_matrix_fusion_cell_refined_support_ablation_summary_path: Path,
    next_axis_after_v8_matrix_fusion_cell_refined_support_ablation_sweep_summary_path: Path,
    next_axis_after_v8_matrix_fusion_cell_refined_support_ablation_floor_probe_summary_path: Path,
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
    next_axis_after_v8_metrics = load_json(next_axis_after_v8_matrix_execution_metrics_path)
    fusion_summary = load_json(next_axis_after_v8_matrix_fusion_summary_path)
    fusion_candidate_summary = load_json(next_axis_after_v8_matrix_fusion_cell_candidate_summary_path)
    fusion_refined_summary = load_json(next_axis_after_v8_matrix_fusion_cell_refined_summary_path)
    fusion_refined_ablation_summary = load_json(next_axis_after_v8_matrix_fusion_cell_refined_ablation_summary_path)
    fusion_support_sweep_summary = load_json(next_axis_after_v8_matrix_fusion_cell_refined_support_sweep_summary_path)
    fusion_support_ablation_summary = load_json(next_axis_after_v8_matrix_fusion_cell_refined_support_ablation_summary_path)
    fusion_support_ablation_sweep_summary = load_json(next_axis_after_v8_matrix_fusion_cell_refined_support_ablation_sweep_summary_path)
    fusion_floor_probe_summary = load_json(next_axis_after_v8_matrix_fusion_cell_refined_support_ablation_floor_probe_summary_path)

    analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_execution_established": next_axis_after_v8_matrix_execution_summary.get("summary_status") == "PASS",
        "matrix_name": next_axis_after_v8_matrix_bootstrap_summary["matrix_name"],
        "executed_cell_count": next_axis_after_v8_matrix_execution_summary.get("executed_cell_count", 0),
        "main_takeaway": "The v9 matrix now establishes fusion_cell_refined_support_ablation_floor_probe as an executed explicit floor-probe cell, so the swept support-isolated floor is no longer only inferred from support-ablation-sweep comparisons.",
    }
    floor_probe_vs_support_ablation_sweep = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_ablation_sweep": {
            "cell_id": fusion_support_ablation_sweep_summary["cell_id"],
            "fusion_mode": fusion_support_ablation_sweep_summary["fusion_mode"],
            "shared_base_samples": fusion_support_ablation_sweep_summary["shared_base_samples"],
            "support_ablation_sweep_signal_score": fusion_support_ablation_sweep_summary["support_ablation_sweep_signal_score"],
            "support_floor": fusion_support_ablation_sweep_summary["support_floor"],
        },
        "fusion_cell_refined_support_ablation_floor_probe": {
            "cell_id": fusion_floor_probe_summary["cell_id"],
            "fusion_mode": fusion_floor_probe_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_probe_summary["shared_base_samples"],
            "floor_probe_signal_score": fusion_floor_probe_summary["floor_probe_signal_score"],
            "retained_floor_probe_ratio_vs_support_ablation_sweep": fusion_floor_probe_summary["retained_floor_probe_ratio_vs_support_ablation_sweep"],
            "support_floor_invariant": fusion_floor_probe_summary["support_floor_invariant"],
        },
        "added_value": [
            "fusion_cell_refined_support_ablation_floor_probe turns the support floor into a direct executable signal instead of leaving it embedded inside support-ablation-sweep summary logic.",
            "This makes floor invariance observable instead of only inferred from support-ablation-sweep comparisons.",
        ],
    }
    floor_probe_vs_support_ablation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_ablation": {
            "cell_id": fusion_support_ablation_summary["cell_id"],
            "fusion_mode": fusion_support_ablation_summary["fusion_mode"],
            "shared_base_samples": fusion_support_ablation_summary["shared_base_samples"],
            "support_ablation_signal_score": fusion_support_ablation_summary["support_ablation_signal_score"],
            "retained_information_ratio_vs_support_sweep": fusion_support_ablation_summary["retained_information_ratio_vs_support_sweep"],
            "support_residual_removed": fusion_support_ablation_summary["support_residual_removed"],
        },
        "fusion_cell_refined_support_ablation_floor_probe": {
            "cell_id": fusion_floor_probe_summary["cell_id"],
            "fusion_mode": fusion_floor_probe_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_probe_summary["shared_base_samples"],
            "floor_probe_signal_score": fusion_floor_probe_summary["floor_probe_signal_score"],
            "floor_probe_gap_vs_support_ablation_sweep": fusion_floor_probe_summary["floor_probe_gap_vs_support_ablation_sweep"],
        },
        "added_value": [
            "The floor probe distinguishes the support-ablation score from the isolated floor that remains after candidate-level evidence is stripped away.",
            "This clarifies whether support-ablation still contains any explicit support-free floor beyond candidate baseline.",
        ],
    }
    floor_probe_vs_support_sweep = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_sweep": {
            "cell_id": fusion_support_sweep_summary["cell_id"],
            "fusion_mode": fusion_support_sweep_summary["fusion_mode"],
            "shared_base_samples": fusion_support_sweep_summary["shared_base_samples"],
            "support_sweep_signal_score": fusion_support_sweep_summary["support_sweep_signal_score"],
            "retained_information_ratio_vs_refined": fusion_support_sweep_summary["retained_information_ratio_vs_refined"],
        },
        "fusion_cell_refined_support_ablation_floor_probe": {
            "cell_id": fusion_floor_probe_summary["cell_id"],
            "fusion_mode": fusion_floor_probe_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_probe_summary["shared_base_samples"],
            "floor_probe_signal_score": fusion_floor_probe_summary["floor_probe_signal_score"],
            "retained_floor_probe_ratio_vs_refined": fusion_floor_probe_summary["retained_floor_probe_ratio_vs_refined"],
        },
        "added_value": [
            "The floor probe separates general support perturbation from the explicit support-free floor itself.",
            "This helps answer whether any meaningful explicit floor remains after support pressure has already been accounted for.",
        ],
    }
    floor_probe_vs_refined = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined": {
            "cell_id": fusion_refined_summary["cell_id"],
            "fusion_mode": fusion_refined_summary["fusion_mode"],
            "shared_base_samples": fusion_refined_summary["shared_base_samples"],
            "refined_signal_score": fusion_refined_summary["refined_signal_score"],
            "refined_delta_vs_candidate": fusion_refined_summary["refined_delta_vs_candidate"],
        },
        "fusion_cell_refined_support_ablation_floor_probe": {
            "cell_id": fusion_floor_probe_summary["cell_id"],
            "fusion_mode": fusion_floor_probe_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_probe_summary["shared_base_samples"],
            "floor_probe_signal_score": fusion_floor_probe_summary["floor_probe_signal_score"],
            "retained_floor_probe_ratio_vs_refined": fusion_floor_probe_summary["retained_floor_probe_ratio_vs_refined"],
        },
        "added_value": [
            "The floor probe shows how far the explicit floor now sits below the original refined signal.",
            "This helps answer whether refined fusion still leaves any support-free explicit floor at all.",
        ],
    }
    floor_probe_vs_candidate = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_candidate": {
            "cell_id": fusion_candidate_summary["cell_id"],
            "fusion_mode": fusion_candidate_summary["fusion_mode"],
            "shared_base_samples": fusion_candidate_summary["shared_base_samples"],
            "candidate_signal_score": fusion_candidate_summary["candidate_signal_score"],
        },
        "fusion_cell_refined_support_ablation_floor_probe": {
            "cell_id": fusion_floor_probe_summary["cell_id"],
            "fusion_mode": fusion_floor_probe_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_probe_summary["shared_base_samples"],
            "floor_probe_signal_score": fusion_floor_probe_summary["floor_probe_signal_score"],
            "floor_probe_gap_vs_candidate": fusion_floor_probe_summary["floor_probe_gap_vs_candidate"],
        },
        "added_value": [
            "The floor probe clarifies whether the explicit support-free floor is already indistinguishable from candidate-level evidence.",
            "This is the cleanest current test of whether any support-free residual survives beyond the first explicit fusion baseline.",
        ],
    }
    floor_probe_vs_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_summary": {
            "cell_id": fusion_summary["cell_id"],
            "fusion_mode": fusion_summary["fusion_mode"],
            "shared_base_samples": fusion_summary["shared_base_samples"],
        },
        "fusion_cell_refined_support_ablation_floor_probe": {
            "cell_id": fusion_floor_probe_summary["cell_id"],
            "fusion_mode": fusion_floor_probe_summary["fusion_mode"],
            "shared_base_samples": fusion_floor_probe_summary["shared_base_samples"],
            "floor_probe_signal_score": fusion_floor_probe_summary["floor_probe_signal_score"],
        },
        "added_value": [
            "The floor probe remains an explicit executable cell even when the measured floor is zero.",
            "This gives a cleaner baseline for asking whether any explicit support-free fusion structure still helps beyond inherited summary-only fusion.",
        ],
    }
    v9_vs_v8 = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "v8_matrix": {
            "matrix_name": next_axis_after_v7_matrix_bootstrap_summary["matrix_name"],
            "executed_cell_count": next_axis_after_v7_matrix_execution_summary.get("executed_cell_count", 0),
            "recommended_axis": next_axis_after_v7_matrix_recommendation["preferred_expansion_axis"],
        },
        "v9_matrix": {
            "matrix_name": next_axis_after_v8_matrix_bootstrap_summary["matrix_name"],
            "dry_run_completed": next_axis_after_v8_matrix_dry_run_summary.get("dry_run_completed", False),
            "executed_cell_count": next_axis_after_v8_matrix_execution_summary.get("executed_cell_count", 0),
            "fusion_cell_refined_support_ablation_floor_probe_executed": next_axis_after_v8_metrics["fusion_cell_refined_support_ablation_floor_probe_executed"],
            "fusion_cell_refined_support_ablation_floor_probe_score": next_axis_after_v8_metrics["fusion_cell_refined_support_ablation_floor_probe_score"],
            "support_floor_invariant": next_axis_after_v8_metrics["fusion_cell_refined_support_ablation_floor_probe_invariant"],
        },
        "added_value": [
            "v9 keeps all v8 route and fusion coverage while adding an executed refined-support-ablation-floor-probe fusion cell.",
            "The richer matrix can now compare the swept support-isolated floor with a direct explicit probe of that floor side by side.",
        ],
    }
    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_blockers": [
            "The refined-support-ablation-floor-probe fusion cell is still a contract-level probe, not a trained fusion classifier.",
            "The matrix still uses one dataset and one lightweight model.",
            "Model-axis and dataset-axis expansion remain less ready than one more round of explicit support-floor stress analysis.",
        ],
    }
    tradeoff_rows = [
        {
            "candidate_route": "fusion_support_floor_stress_coverage",
            "realism": "higher",
            "cost": "medium",
            "readiness": "high",
            "why": "Now that the floor probe exists, the next honest step is to stress that floor directly before jumping axes.",
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
        "recommended_next_step": "bootstrap_next_axis_after_v9_matrix",
        "preferred_expansion_axis": "fusion_support_floor_stress_coverage",
        "why_recommended": [
            "v9 proves that fusion_cell_refined_support_ablation_floor_probe can reach execution, and the next honest step is to stress that floor directly.",
            "Current repository reality still makes floor-stress coverage more actionable than model-axis or dataset-axis expansion.",
            "The floor-probe cell now makes it possible to design a next matrix around explicit support-floor stress comparisons.",
        ],
        "why_not_return_to_proxy": [
            "The real-experiment matrix stack is still adding new fusion-level information, so returning to proxy would reduce leverage."
        ],
        "minimum_success_standard": [
            "define a next-axis-after-v9 matrix that stresses the explicit support-isolated floor directly",
            "materialize next-axis-after-v9 matrix inputs",
            "prove the next-axis-after-v9 matrix is bootstrap-ready",
        ],
    }

    write_json(output_dir / "next_axis_after_v8_matrix_analysis_summary.json", analysis)
    write_json(output_dir / "fusion_floor_probe_vs_support_ablation_sweep_comparison.json", floor_probe_vs_support_ablation_sweep)
    write_json(output_dir / "fusion_floor_probe_vs_support_ablation_comparison.json", floor_probe_vs_support_ablation)
    write_json(output_dir / "fusion_floor_probe_vs_support_sweep_comparison.json", floor_probe_vs_support_sweep)
    write_json(output_dir / "fusion_floor_probe_vs_refined_comparison.json", floor_probe_vs_refined)
    write_json(output_dir / "fusion_floor_probe_vs_candidate_comparison.json", floor_probe_vs_candidate)
    write_json(output_dir / "fusion_floor_probe_vs_summary_comparison.json", floor_probe_vs_summary)
    write_json(output_dir / "v9_vs_v8_matrix_comparison.json", v9_vs_v8)
    write_json(output_dir / "v9_matrix_blocker_summary.json", blocker_summary)
    write_csv(output_dir / "v9_matrix_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "next_axis_after_v8_matrix_next_step_recommendation.json", recommendation)
    return {
        "analysis": analysis,
        "recommendation": recommendation,
        "output_paths": {
            "analysis": str((output_dir / "next_axis_after_v8_matrix_analysis_summary.json").resolve()),
            "floor_probe_vs_support_ablation_sweep": str((output_dir / "fusion_floor_probe_vs_support_ablation_sweep_comparison.json").resolve()),
            "floor_probe_vs_support_ablation": str((output_dir / "fusion_floor_probe_vs_support_ablation_comparison.json").resolve()),
            "floor_probe_vs_support_sweep": str((output_dir / "fusion_floor_probe_vs_support_sweep_comparison.json").resolve()),
            "floor_probe_vs_refined": str((output_dir / "fusion_floor_probe_vs_refined_comparison.json").resolve()),
            "floor_probe_vs_candidate": str((output_dir / "fusion_floor_probe_vs_candidate_comparison.json").resolve()),
            "floor_probe_vs_summary": str((output_dir / "fusion_floor_probe_vs_summary_comparison.json").resolve()),
            "v9_vs_v8": str((output_dir / "v9_vs_v8_matrix_comparison.json").resolve()),
            "blockers": str((output_dir / "v9_matrix_blocker_summary.json").resolve()),
            "tradeoff": str((output_dir / "v9_matrix_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "next_axis_after_v8_matrix_next_step_recommendation.json").resolve()),
        },
    }
