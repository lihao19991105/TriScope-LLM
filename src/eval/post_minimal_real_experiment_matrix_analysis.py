"""Post minimal real-experiment matrix analysis and recommendation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-minimal-real-experiment-matrix-analysis/v1"


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


def build_post_minimal_real_experiment_matrix_analysis(
    cutover_bootstrap_summary_path: Path,
    first_real_dry_run_summary_path: Path,
    first_real_execution_run_summary_path: Path,
    minimal_matrix_bootstrap_summary_path: Path,
    matrix_dry_run_summary_path: Path,
    matrix_execution_run_summary_path: Path,
    matrix_execution_metrics_path: Path,
    proxy_recommendation_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cutover_summary = load_json(cutover_bootstrap_summary_path)
    first_real_dry_run_summary = load_json(first_real_dry_run_summary_path)
    first_real_execution_summary = load_json(first_real_execution_run_summary_path)
    minimal_matrix_bootstrap_summary = load_json(minimal_matrix_bootstrap_summary_path)
    matrix_dry_run_summary = load_json(matrix_dry_run_summary_path)
    matrix_execution_summary = load_json(matrix_execution_run_summary_path)
    matrix_execution_metrics = load_json(matrix_execution_metrics_path)
    proxy_recommendation = load_json(proxy_recommendation_path)

    analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_execution_established": matrix_execution_summary.get("summary_status") == "PASS",
        "matrix_name": minimal_matrix_bootstrap_summary["matrix_name"],
        "executed_cell_count": matrix_execution_summary.get("executed_cell_count", 0),
        "main_takeaway": "The project has now moved from single-cutover real execution into a first matrix-level execution layer, so the next bottleneck is enriching matrix coverage rather than returning to proxy substrate expansion.",
    }
    vs_cutover = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "single_cutover_stage": {
            "executed_layers": first_real_execution_summary.get("executed_layers", []),
            "real_dry_run_completed": first_real_dry_run_summary.get("dry_run_completed", False),
        },
        "matrix_stage": {
            "matrix_name": minimal_matrix_bootstrap_summary["matrix_name"],
            "dry_run_completed": matrix_dry_run_summary.get("dry_run_completed", False),
            "executed_cell_count": matrix_execution_summary.get("executed_cell_count", 0),
            "executed_layers": matrix_execution_summary.get("executed_layers", []),
        },
        "added_value": [
            "The matrix object is no longer only materialized; it now has both a dry-run and a first actual execution layer.",
            "Execution is now framed as a matrix cell rather than only a single-cutover execution envelope.",
            "The repository can now discuss next-matrix design using actual matrix artifacts.",
        ],
    }
    vs_proxy = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "proxy_recommendation": proxy_recommendation["recommended_next_step"],
        "matrix_stage": {
            "executed_cell_count": matrix_execution_summary.get("executed_cell_count", 0),
            "route_b_rows": matrix_execution_metrics["route_b_rows"],
            "route_c_rows": matrix_execution_metrics["route_c_rows"],
        },
        "added_value": [
            "The project is now operating inside a real-experiment matrix object rather than only the proxy rerun world.",
            "The next decision can be about matrix enrichment, not proxy substrate expansion.",
        ],
    }
    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_blockers": [
            "The current matrix still has only one dataset and one model cell.",
            "Fusion remains a matrix-level integrated summary, not a separate classifier execution cell.",
            "The current matrix still inherits the local curated slice and pilot_distilgpt2_hf constraints.",
        ],
    }
    tradeoff_rows = [
        {
            "candidate_route": "expand_matrix_route_and_output_coverage",
            "realism": "higher",
            "cost": "medium",
            "readiness": "high",
            "why": "The next clean step is to enrich the matrix object itself instead of returning to proxy expansion.",
        },
        {
            "candidate_route": "switch_to_larger_model_matrix",
            "realism": "higher",
            "cost": "high",
            "readiness": "low",
            "why": "Possible later, but heavier than needed for the next matrix step.",
        },
        {
            "candidate_route": "return_to_proxy_v7",
            "realism": "lower",
            "cost": "medium",
            "readiness": "medium",
            "why": "This would move backward to a lower-leverage stage.",
        },
    ]
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "bootstrap_next_real_experiment_matrix",
        "preferred_expansion_axis": "route_and_fusion_coverage",
        "why_recommended": [
            "A first matrix-level dry-run and execution now exist, so the next best move is to enrich the real-experiment matrix itself.",
            "Returning to proxy expansion would add less value than defining the next matrix layer.",
            "The current minimal matrix is enough to justify a slightly richer next matrix without jumping to a heavy benchmark setup.",
        ],
        "why_not_return_to_proxy": [
            "Matrix execution has now started to exist in its own right, so proxy substrate expansion is no longer the bottleneck."
        ],
        "minimum_success_standard": [
            "define a next real-experiment matrix with richer route/fusion coverage",
            "materialize next matrix inputs",
            "prove the next matrix object is bootstrap-ready",
        ],
    }

    write_json(output_dir / "minimal_matrix_analysis_summary.json", analysis)
    write_json(output_dir / "matrix_vs_cutover_comparison.json", vs_cutover)
    write_json(output_dir / "matrix_vs_proxy_comparison.json", vs_proxy)
    write_json(output_dir / "minimal_matrix_blocker_summary.json", blocker_summary)
    write_csv(output_dir / "minimal_matrix_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "minimal_matrix_next_step_recommendation.json", recommendation)
    return {
        "analysis": analysis,
        "recommendation": recommendation,
        "output_paths": {
            "analysis": str((output_dir / "minimal_matrix_analysis_summary.json").resolve()),
            "vs_cutover": str((output_dir / "matrix_vs_cutover_comparison.json").resolve()),
            "vs_proxy": str((output_dir / "matrix_vs_proxy_comparison.json").resolve()),
            "blockers": str((output_dir / "minimal_matrix_blocker_summary.json").resolve()),
            "tradeoff": str((output_dir / "minimal_matrix_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "minimal_matrix_next_step_recommendation.json").resolve()),
        },
    }
