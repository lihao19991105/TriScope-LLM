"""Analyze the refined-fusion-support-floor-stress-sweep-aware real-experiment matrix v11."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-v11-real-experiment-matrix-analysis/v1"


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


def build_post_v11_real_experiment_matrix_analysis(
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
    next_axis_after_v9_matrix_analysis_recommendation_path: Path,
    next_axis_after_v10_matrix_bootstrap_summary_path: Path,
    next_axis_after_v10_matrix_dry_run_summary_path: Path,
    next_axis_after_v10_matrix_execution_run_summary_path: Path,
    next_axis_after_v10_matrix_execution_metrics_path: Path,
    next_axis_after_v10_matrix_fusion_summary_path: Path,
    next_axis_after_v10_matrix_fusion_cell_candidate_summary_path: Path,
    next_axis_after_v10_matrix_fusion_cell_refined_summary_path: Path,
    next_axis_after_v10_matrix_fusion_cell_refined_ablation_summary_path: Path,
    next_axis_after_v10_matrix_fusion_cell_refined_support_sweep_summary_path: Path,
    next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_summary_path: Path,
    next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_sweep_summary_path: Path,
    next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_floor_probe_summary_path: Path,
    next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_floor_stress_summary_path: Path,
    next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_floor_stress_sweep_summary_path: Path,
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
    next_axis_after_v8_matrix_recommendation = load_json(next_axis_after_v8_matrix_analysis_recommendation_path)
    next_axis_after_v9_matrix_bootstrap_summary = load_json(next_axis_after_v9_matrix_bootstrap_summary_path)
    next_axis_after_v9_matrix_dry_run_summary = load_json(next_axis_after_v9_matrix_dry_run_summary_path)
    next_axis_after_v9_matrix_execution_summary = load_json(next_axis_after_v9_matrix_execution_run_summary_path)
    next_axis_after_v9_matrix_recommendation = load_json(next_axis_after_v9_matrix_analysis_recommendation_path)
    next_axis_after_v10_matrix_bootstrap_summary = load_json(next_axis_after_v10_matrix_bootstrap_summary_path)
    next_axis_after_v10_matrix_dry_run_summary = load_json(next_axis_after_v10_matrix_dry_run_summary_path)
    next_axis_after_v10_matrix_execution_summary = load_json(next_axis_after_v10_matrix_execution_run_summary_path)
    next_axis_after_v10_metrics = load_json(next_axis_after_v10_matrix_execution_metrics_path)
    fusion_summary = load_json(next_axis_after_v10_matrix_fusion_summary_path)
    fusion_candidate_summary = load_json(next_axis_after_v10_matrix_fusion_cell_candidate_summary_path)
    fusion_refined_summary = load_json(next_axis_after_v10_matrix_fusion_cell_refined_summary_path)
    fusion_refined_ablation_summary = load_json(next_axis_after_v10_matrix_fusion_cell_refined_ablation_summary_path)
    fusion_support_sweep_summary = load_json(next_axis_after_v10_matrix_fusion_cell_refined_support_sweep_summary_path)
    fusion_support_ablation_summary = load_json(next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_summary_path)
    fusion_support_ablation_sweep_summary = load_json(next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_sweep_summary_path)
    fusion_floor_probe_summary = load_json(next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_floor_probe_summary_path)
    fusion_floor_stress_summary = load_json(next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_floor_stress_summary_path)
    fusion_floor_stress_sweep_summary = load_json(
        next_axis_after_v10_matrix_fusion_cell_refined_support_ablation_floor_stress_sweep_summary_path
    )

    _ = {
        "cutover_summary": cutover_summary,
        "first_real_dry_run_summary": first_real_dry_run_summary,
        "first_real_execution_summary": first_real_execution_summary,
        "minimal_matrix_bootstrap_summary": minimal_matrix_bootstrap_summary,
        "minimal_matrix_dry_run_summary": minimal_matrix_dry_run_summary,
        "minimal_matrix_execution_summary": minimal_matrix_execution_summary,
        "minimal_matrix_recommendation": minimal_matrix_recommendation,
        "next_matrix_bootstrap_summary": next_matrix_bootstrap_summary,
        "next_matrix_dry_run_summary": next_matrix_dry_run_summary,
        "next_matrix_execution_summary": next_matrix_execution_summary,
        "next_matrix_recommendation": next_matrix_recommendation,
        "post_next_matrix_bootstrap_summary": post_next_matrix_bootstrap_summary,
        "post_next_matrix_dry_run_summary": post_next_matrix_dry_run_summary,
        "post_next_matrix_execution_summary": post_next_matrix_execution_summary,
        "post_next_matrix_recommendation": post_next_matrix_recommendation,
        "next_axis_matrix_bootstrap_summary": next_axis_matrix_bootstrap_summary,
        "next_axis_matrix_dry_run_summary": next_axis_matrix_dry_run_summary,
        "next_axis_matrix_execution_summary": next_axis_matrix_execution_summary,
        "next_axis_matrix_recommendation": next_axis_matrix_recommendation,
        "next_axis_after_v4_matrix_bootstrap_summary": next_axis_after_v4_matrix_bootstrap_summary,
        "next_axis_after_v4_matrix_dry_run_summary": next_axis_after_v4_matrix_dry_run_summary,
        "next_axis_after_v4_matrix_execution_summary": next_axis_after_v4_matrix_execution_summary,
        "next_axis_after_v4_matrix_recommendation": next_axis_after_v4_matrix_recommendation,
        "next_axis_after_v5_matrix_bootstrap_summary": next_axis_after_v5_matrix_bootstrap_summary,
        "next_axis_after_v5_matrix_dry_run_summary": next_axis_after_v5_matrix_dry_run_summary,
        "next_axis_after_v5_matrix_execution_summary": next_axis_after_v5_matrix_execution_summary,
        "next_axis_after_v5_matrix_recommendation": next_axis_after_v5_matrix_recommendation,
        "next_axis_after_v6_matrix_bootstrap_summary": next_axis_after_v6_matrix_bootstrap_summary,
        "next_axis_after_v6_matrix_dry_run_summary": next_axis_after_v6_matrix_dry_run_summary,
        "next_axis_after_v6_matrix_execution_summary": next_axis_after_v6_matrix_execution_summary,
        "next_axis_after_v6_matrix_recommendation": next_axis_after_v6_matrix_recommendation,
        "next_axis_after_v7_matrix_bootstrap_summary": next_axis_after_v7_matrix_bootstrap_summary,
        "next_axis_after_v7_matrix_dry_run_summary": next_axis_after_v7_matrix_dry_run_summary,
        "next_axis_after_v7_matrix_execution_summary": next_axis_after_v7_matrix_execution_summary,
        "next_axis_after_v7_matrix_recommendation": next_axis_after_v7_matrix_recommendation,
        "next_axis_after_v8_matrix_bootstrap_summary": next_axis_after_v8_matrix_bootstrap_summary,
        "next_axis_after_v8_matrix_dry_run_summary": next_axis_after_v8_matrix_dry_run_summary,
        "next_axis_after_v8_matrix_execution_summary": next_axis_after_v8_matrix_execution_summary,
        "next_axis_after_v8_matrix_recommendation": next_axis_after_v8_matrix_recommendation,
        "next_axis_after_v9_matrix_bootstrap_summary": next_axis_after_v9_matrix_bootstrap_summary,
        "next_axis_after_v9_matrix_dry_run_summary": next_axis_after_v9_matrix_dry_run_summary,
        "next_axis_after_v9_matrix_execution_summary": next_axis_after_v9_matrix_execution_summary,
        "next_axis_after_v9_matrix_recommendation": next_axis_after_v9_matrix_recommendation,
        "fusion_summary": fusion_summary,
        "fusion_candidate_summary": fusion_candidate_summary,
    }

    analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_execution_established": next_axis_after_v10_matrix_execution_summary.get("summary_status") == "PASS",
        "matrix_name": next_axis_after_v10_matrix_bootstrap_summary["matrix_name"],
        "executed_cell_count": next_axis_after_v10_matrix_execution_summary.get("executed_cell_count", 0),
        "main_takeaway": "The v11 matrix now establishes fusion_cell_refined_support_ablation_floor_stress_sweep as an executed explicit sweep of the direct-stress floor, but its incremental value is mostly to confirm that the zero-floor invariance result still holds rather than to add a materially new fusion signal.",
    }

    floor_stress_sweep_vs_floor_stress = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_ablation_floor_stress": {
            "cell_id": fusion_floor_stress_summary["cell_id"],
            "floor_stress_signal_score": fusion_floor_stress_summary["floor_stress_signal_score"],
            "support_floor_stress_invariant": fusion_floor_stress_summary["support_floor_stress_invariant"],
        },
        "fusion_cell_refined_support_ablation_floor_stress_sweep": {
            "cell_id": fusion_floor_stress_sweep_summary["cell_id"],
            "floor_stress_sweep_signal_score": fusion_floor_stress_sweep_summary["floor_stress_sweep_signal_score"],
            "support_floor_stress_sweep_invariant": fusion_floor_stress_sweep_summary["support_floor_stress_sweep_invariant"],
            "floor_stress_sweep_gap_vs_floor_stress": fusion_floor_stress_sweep_summary["floor_stress_sweep_gap_vs_floor_stress"],
        },
        "added_value": [
            "The sweep cell turns the direct-stress result itself into one more executable invariance check.",
            "Its value is mainly confirmatory because the stressed floor stays pinned to the same zero-floor outcome.",
        ],
    }
    floor_stress_sweep_vs_floor_probe = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_ablation_floor_probe": {
            "cell_id": fusion_floor_probe_summary["cell_id"],
            "floor_probe_signal_score": fusion_floor_probe_summary["floor_probe_signal_score"],
            "support_floor_invariant": fusion_floor_probe_summary["support_floor_invariant"],
        },
        "fusion_cell_refined_support_ablation_floor_stress_sweep": {
            "cell_id": fusion_floor_stress_sweep_summary["cell_id"],
            "floor_stress_sweep_signal_score": fusion_floor_stress_sweep_summary["floor_stress_sweep_signal_score"],
            "floor_stress_sweep_gap_vs_floor_probe": fusion_floor_stress_sweep_summary["floor_stress_sweep_gap_vs_floor_probe"],
        },
        "added_value": [
            "The sweep cell shows that the explicit floor still matches the original floor-probe conclusion after direct stress and one more sweep.",
        ],
    }
    floor_stress_sweep_vs_support_ablation_sweep = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined_support_ablation_sweep": {
            "cell_id": fusion_support_ablation_sweep_summary["cell_id"],
            "support_ablation_sweep_signal_score": fusion_support_ablation_sweep_summary["support_ablation_sweep_signal_score"],
        },
        "fusion_cell_refined_support_ablation_floor_stress_sweep": {
            "cell_id": fusion_floor_stress_sweep_summary["cell_id"],
            "floor_stress_sweep_signal_score": fusion_floor_stress_sweep_summary["floor_stress_sweep_signal_score"],
            "floor_stress_sweep_gap_vs_support_ablation_sweep": fusion_floor_stress_sweep_summary["floor_stress_sweep_gap_vs_support_ablation_sweep"],
        },
        "added_value": [
            "The sweep cell confirms that the support-isolated residual is still at the same floor even after the direct-stress conclusion is swept.",
        ],
    }
    floor_stress_sweep_vs_refined = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_cell_refined": {
            "cell_id": fusion_refined_summary["cell_id"],
            "refined_signal_score": fusion_refined_summary["refined_signal_score"],
        },
        "fusion_cell_refined_support_ablation_floor_stress_sweep": {
            "cell_id": fusion_floor_stress_sweep_summary["cell_id"],
            "floor_stress_sweep_signal_score": fusion_floor_stress_sweep_summary["floor_stress_sweep_signal_score"],
            "retained_floor_stress_sweep_ratio_vs_refined": fusion_floor_stress_sweep_summary["retained_floor_stress_sweep_ratio_vs_refined"],
        },
        "added_value": [
            "The sweep cell highlights how little of the refined signal survives once support-specific evidence has already collapsed to the explicit floor.",
        ],
    }
    v11_vs_v10 = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "v10_matrix": {
            "matrix_name": next_axis_after_v9_matrix_bootstrap_summary["matrix_name"],
            "executed_cell_count": next_axis_after_v9_matrix_execution_summary.get("executed_cell_count", 0),
            "recommended_axis": next_axis_after_v9_matrix_recommendation["preferred_expansion_axis"],
        },
        "v11_matrix": {
            "matrix_name": next_axis_after_v10_matrix_bootstrap_summary["matrix_name"],
            "dry_run_completed": next_axis_after_v10_matrix_dry_run_summary.get("dry_run_completed", False),
            "executed_cell_count": next_axis_after_v10_matrix_execution_summary.get("executed_cell_count", 0),
            "fusion_cell_refined_support_ablation_floor_stress_sweep_executed": next_axis_after_v10_metrics["fusion_cell_refined_support_ablation_floor_stress_sweep_executed"],
            "fusion_cell_refined_support_ablation_floor_stress_sweep_score": next_axis_after_v10_metrics["fusion_cell_refined_support_ablation_floor_stress_sweep_score"],
            "support_floor_stress_sweep_invariant": next_axis_after_v10_metrics["fusion_cell_refined_support_ablation_floor_stress_sweep_invariant"],
        },
        "added_value": [
            "v11 adds an executed explicit sweep of the direct-stress floor on top of the v10 floor-stress cell.",
            "The new signal is directionally consistent with v10 but mostly confirms the same zero-floor invariance result.",
        ],
    }
    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_blockers": [
            "The floor-stress-sweep cell is still a contract-level invariance artifact, not a trained fusion classifier.",
            "The matrix still uses one dataset and one lightweight ready-local model.",
            "The marginal value of one more same-axis fusion refinement step now looks smaller than the value of testing whether the matrix contract transfers to a larger model.",
        ],
    }
    tradeoff_rows = [
        {
            "candidate_route": "model_axis_1p5b_bootstrap",
            "realism": "higher",
            "cost": "medium",
            "readiness": "medium",
            "why": "The fusion axis still works, but v11 mostly confirms the same conclusion. The next higher-leverage question is whether the matrix contract transfers to a larger model.",
        },
        {
            "candidate_route": "continue_same_axis_fusion_refinement",
            "realism": "medium",
            "cost": "low",
            "readiness": "high",
            "why": "Technically feasible, but the incremental evidence after v11 is mostly confirmatory rather than materially new.",
        },
        {
            "candidate_route": "dataset_axis_preparation",
            "realism": "higher",
            "cost": "medium",
            "readiness": "low",
            "why": "Still blocked by the lack of a second comparably mature dataset object.",
        },
    ]
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "bootstrap_model_axis_1p5b",
        "preferred_expansion_axis": "model_axis_1p5b_single_model_probe",
        "why_recommended": [
            "v11 continues to validate the same fusion-axis story, but the new value is now mostly marginal and confirmatory.",
            "The next more informative question is whether the real-experiment matrix contract can migrate from pilot_distilgpt2_hf to a larger 1.5B-class model.",
            "A single 1.5B bootstrap is the least disruptive way to test model-axis transfer without opening a large multi-model branch.",
        ],
        "why_not_continue_same_axis": [
            "Another same-axis fusion bootstrap would likely refine the same zero-floor invariance conclusion rather than create a meaningfully different evidence chain.",
        ],
        "minimum_success_standard": [
            "choose one 1.5B candidate model profile under the existing config system",
            "materialize a model-axis bootstrap artifact that keeps the current dataset and route contracts stable",
            "state honestly whether the chosen 1.5B path is ready-local, config-only, or blocked",
        ],
    }

    write_json(output_dir / "next_axis_after_v10_matrix_analysis_summary.json", analysis)
    write_json(output_dir / "fusion_floor_stress_sweep_vs_floor_stress_comparison.json", floor_stress_sweep_vs_floor_stress)
    write_json(output_dir / "fusion_floor_stress_sweep_vs_floor_probe_comparison.json", floor_stress_sweep_vs_floor_probe)
    write_json(output_dir / "fusion_floor_stress_sweep_vs_support_ablation_sweep_comparison.json", floor_stress_sweep_vs_support_ablation_sweep)
    write_json(output_dir / "fusion_floor_stress_sweep_vs_refined_comparison.json", floor_stress_sweep_vs_refined)
    write_json(output_dir / "v11_vs_v10_matrix_comparison.json", v11_vs_v10)
    write_json(output_dir / "v11_matrix_blocker_summary.json", blocker_summary)
    write_csv(output_dir / "v11_matrix_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "next_axis_after_v10_matrix_next_step_recommendation.json", recommendation)
    return {
        "analysis": analysis,
        "recommendation": recommendation,
        "output_paths": {
            "analysis": str((output_dir / "next_axis_after_v10_matrix_analysis_summary.json").resolve()),
            "floor_stress_sweep_vs_floor_stress": str((output_dir / "fusion_floor_stress_sweep_vs_floor_stress_comparison.json").resolve()),
            "floor_stress_sweep_vs_floor_probe": str((output_dir / "fusion_floor_stress_sweep_vs_floor_probe_comparison.json").resolve()),
            "floor_stress_sweep_vs_support_ablation_sweep": str((output_dir / "fusion_floor_stress_sweep_vs_support_ablation_sweep_comparison.json").resolve()),
            "floor_stress_sweep_vs_refined": str((output_dir / "fusion_floor_stress_sweep_vs_refined_comparison.json").resolve()),
            "v11_vs_v10": str((output_dir / "v11_vs_v10_matrix_comparison.json").resolve()),
            "blockers": str((output_dir / "v11_matrix_blocker_summary.json").resolve()),
            "tradeoff": str((output_dir / "v11_matrix_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "next_axis_after_v10_matrix_next_step_recommendation.json").resolve()),
        },
    }
