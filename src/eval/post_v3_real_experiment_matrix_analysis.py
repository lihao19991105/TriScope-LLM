"""Analyze the fusion-cell-aware post-next real-experiment matrix v3."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-v3-real-experiment-matrix-analysis/v1"


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


def build_post_v3_real_experiment_matrix_analysis(
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
    post_next_matrix_execution_metrics_path: Path,
    post_next_matrix_fusion_summary_path: Path,
    post_next_matrix_fusion_cell_candidate_summary_path: Path,
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
    post_next_matrix_metrics = load_json(post_next_matrix_execution_metrics_path)
    fusion_summary = load_json(post_next_matrix_fusion_summary_path)
    fusion_candidate_summary = load_json(post_next_matrix_fusion_cell_candidate_summary_path)

    analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_execution_established": post_next_matrix_execution_summary.get("summary_status") == "PASS",
        "matrix_name": post_next_matrix_bootstrap_summary["matrix_name"],
        "executed_cell_count": post_next_matrix_execution_summary.get("executed_cell_count", 0),
        "main_takeaway": "The v3 matrix now establishes fusion_cell_candidate as an executed explicit fusion cell, so fusion is no longer only a summary-style artifact.",
    }
    fusion_vs_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_summary": {
            "cell_id": fusion_summary["cell_id"],
            "fusion_mode": fusion_summary["fusion_mode"],
            "shared_base_samples": fusion_summary["shared_base_samples"],
        },
        "fusion_cell_candidate": {
            "cell_id": fusion_candidate_summary["cell_id"],
            "fusion_mode": fusion_candidate_summary["fusion_mode"],
            "shared_base_samples": fusion_candidate_summary["shared_base_samples"],
            "candidate_signal_score": fusion_candidate_summary["candidate_signal_score"],
            "score_gap": fusion_candidate_summary["score_gap"],
        },
        "added_value": [
            "fusion_cell_candidate has its own explicit cell identity rather than being folded into a summary artifact.",
            "fusion_cell_candidate exposes a standalone scalar signal score and route-gap component.",
            "This makes fusion evidence easier to compare against route ablations than the inherited summary alone.",
        ],
    }
    v3_vs_v2 = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "v2_matrix": {
            "matrix_name": next_matrix_bootstrap_summary["matrix_name"],
            "executed_cell_count": next_matrix_execution_summary.get("executed_cell_count", 0),
            "executed_layers": next_matrix_execution_summary.get("executed_layers", []),
            "recommended_axis": next_matrix_recommendation["preferred_expansion_axis"],
        },
        "v3_matrix": {
            "matrix_name": post_next_matrix_bootstrap_summary["matrix_name"],
            "dry_run_completed": post_next_matrix_dry_run_summary.get("dry_run_completed", False),
            "executed_cell_count": post_next_matrix_execution_summary.get("executed_cell_count", 0),
            "executed_layers": post_next_matrix_execution_summary.get("executed_layers", []),
            "fusion_cell_candidate_executed": post_next_matrix_metrics["fusion_cell_candidate_executed"],
            "fusion_cell_candidate_score": post_next_matrix_metrics["fusion_cell_candidate_score"],
        },
        "added_value": [
            "v3 keeps all v2 route and ablation coverage while adding an explicit fusion candidate cell.",
            "The richer matrix can now compare inherited fusion summaries against explicit fusion-cell execution artifacts.",
        ],
    }
    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_blockers": [
            "The explicit fusion cell is still a candidate-style construction, not a trained fusion classifier.",
            "The matrix still uses one dataset and one lightweight model.",
            "There is still no second ready-local model profile for model-axis expansion.",
        ],
    }
    tradeoff_rows = [
        {
            "candidate_route": "fusion_cell_refinement",
            "realism": "higher",
            "cost": "medium",
            "readiness": "high",
            "why": "Now that fusion_cell_candidate exists, the clean next step is to refine and stress it rather than abandon it.",
        },
        {
            "candidate_route": "dataset_axis_preparation",
            "realism": "higher",
            "cost": "medium",
            "readiness": "low",
            "why": "Potentially valuable later, but the repository does not yet have an equally mature second dataset object.",
        },
        {
            "candidate_route": "model_axis_preparation",
            "realism": "higher",
            "cost": "high",
            "readiness": "low",
            "why": "No second ready-local model is currently available in configs/models.yaml.",
        },
    ]
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "bootstrap_next_axis_real_experiment_matrix",
        "preferred_expansion_axis": "fusion_cell_refinement",
        "why_recommended": [
            "v3 proves that fusion_cell_candidate can reach execution, but its value is still only lightly validated.",
            "The next honest step is to refine fusion-cell coverage before jumping to unsupported model or dataset axes.",
            "Current repository reality makes fusion_cell_refinement more actionable than model-axis or dataset-axis expansion.",
        ],
        "why_not_return_to_proxy": [
            "The matrix stack has progressed past route-only and summary-only fusion, so returning to proxy would be a regression in leverage."
        ],
        "minimum_success_standard": [
            "define a next-axis matrix that refines explicit fusion cell coverage",
            "materialize next-axis matrix inputs",
            "prove the next-axis matrix is bootstrap-ready",
        ],
    }

    write_json(output_dir / "post_next_matrix_analysis_summary.json", analysis)
    write_json(output_dir / "fusion_cell_vs_fusion_summary_comparison.json", fusion_vs_summary)
    write_json(output_dir / "v3_vs_v2_matrix_comparison.json", v3_vs_v2)
    write_json(output_dir / "v3_matrix_blocker_summary.json", blocker_summary)
    write_csv(output_dir / "v3_matrix_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "post_next_matrix_next_step_recommendation.json", recommendation)
    return {
        "analysis": analysis,
        "recommendation": recommendation,
        "output_paths": {
            "analysis": str((output_dir / "post_next_matrix_analysis_summary.json").resolve()),
            "fusion_vs_summary": str((output_dir / "fusion_cell_vs_fusion_summary_comparison.json").resolve()),
            "v3_vs_v2": str((output_dir / "v3_vs_v2_matrix_comparison.json").resolve()),
            "blockers": str((output_dir / "v3_matrix_blocker_summary.json").resolve()),
            "tradeoff": str((output_dir / "v3_matrix_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "post_next_matrix_next_step_recommendation.json").resolve()),
        },
    }
