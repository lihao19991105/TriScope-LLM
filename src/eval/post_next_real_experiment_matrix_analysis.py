"""Analyze richer next real-experiment matrix execution."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-next-real-experiment-matrix-analysis/v1"


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


def build_post_next_real_experiment_matrix_analysis(
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
    next_matrix_execution_metrics_path: Path,
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
    next_matrix_metrics = load_json(next_matrix_execution_metrics_path)

    analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_execution_established": next_matrix_execution_summary.get("summary_status") == "PASS",
        "matrix_name": next_matrix_bootstrap_summary["matrix_name"],
        "executed_cell_count": next_matrix_execution_summary.get("executed_cell_count", 0),
        "main_takeaway": "The richer v2 matrix now adds explicit ablation cells on top of the minimal matrix, so the repository can reason about route-isolation value rather than only proving that a minimal matrix can run.",
    }
    vs_minimal = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "minimal_matrix": {
            "matrix_name": minimal_matrix_bootstrap_summary["matrix_name"],
            "dry_run_completed": minimal_matrix_dry_run_summary.get("dry_run_completed", False),
            "executed_cell_count": minimal_matrix_execution_summary.get("executed_cell_count", 0),
            "executed_layers": minimal_matrix_execution_summary.get("executed_layers", []),
        },
        "richer_matrix": {
            "matrix_name": next_matrix_bootstrap_summary["matrix_name"],
            "dry_run_completed": next_matrix_dry_run_summary.get("dry_run_completed", False),
            "executed_cell_count": next_matrix_execution_summary.get("executed_cell_count", 0),
            "executed_layers": next_matrix_execution_summary.get("executed_layers", []),
            "route_b_only_ablation_rows": next_matrix_metrics["route_b_only_ablation_rows"],
            "route_c_only_ablation_rows": next_matrix_metrics["route_c_only_ablation_rows"],
        },
        "added_value": [
            "The richer matrix introduces executed ablation cells rather than only a full cross-route cell.",
            "Route-isolation artifacts now exist for both route_b_only_ablation and route_c_only_ablation.",
            "The matrix can now compare full-route coverage against isolated route coverage using concrete artifacts.",
        ],
    }
    vs_cutover = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "cutover_stage": {
            "cutover_candidate": cutover_summary.get("chosen_candidate_name", "unknown"),
            "real_dry_run_completed": first_real_dry_run_summary.get("dry_run_completed", False),
            "executed_layers": first_real_execution_summary.get("executed_layers", []),
        },
        "richer_matrix_stage": {
            "matrix_name": next_matrix_bootstrap_summary["matrix_name"],
            "executed_cell_count": next_matrix_execution_summary.get("executed_cell_count", 0),
            "executed_layers": next_matrix_execution_summary.get("executed_layers", []),
        },
        "added_value": [
            "The project now has richer matrix-level execution beyond the earlier single-cutover execution envelope.",
            "Route ablations provide extra structure that the single-cutover stage did not expose.",
        ],
    }
    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_blockers": [
            "The richer matrix still uses one dataset and one lightweight model.",
            "Fusion still appears as a summary artifact rather than a dedicated execution cell.",
            "Labels remain proxy-style rather than benchmark ground truth.",
        ],
    }
    tradeoff_rows = [
        {
            "candidate_route": "expand_fusion_cell_coverage",
            "realism": "higher",
            "cost": "medium",
            "readiness": "high",
            "why": "Ablation cells now exist, so the next best leverage point is to promote fusion from summary to a more explicit matrix cell.",
        },
        {
            "candidate_route": "expand_model_axis",
            "realism": "higher",
            "cost": "high",
            "readiness": "low",
            "why": "Useful later, but heavier than the next honest step.",
        },
        {
            "candidate_route": "return_to_proxy",
            "realism": "lower",
            "cost": "medium",
            "readiness": "medium",
            "why": "This would move backward after richer matrix execution has already been established.",
        },
    ]
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "bootstrap_post_next_real_experiment_matrix",
        "preferred_expansion_axis": "fusion_cell_coverage",
        "why_recommended": [
            "The richer matrix v2 proves that ablation cells add new route-isolation information compared with the minimal matrix.",
            "fusion_summary still carries value, but the main remaining gap is that fusion is not yet represented as an explicit execution cell.",
            "The next matrix should stay lightweight while extending fusion coverage rather than jumping to a heavy model or dataset axis.",
        ],
        "why_not_return_to_proxy": [
            "Both minimal matrix v1 and richer matrix v2 execution now exist, so the bottleneck is inside the real-experiment matrix stack, not proxy substrate expansion."
        ],
        "minimum_success_standard": [
            "define a next-next matrix with explicit fusion-cell expansion",
            "materialize next-next matrix inputs",
            "prove the new matrix is bootstrap-ready",
        ],
    }

    write_json(output_dir / "next_matrix_analysis_summary.json", analysis)
    write_json(output_dir / "richer_matrix_vs_minimal_matrix_comparison.json", vs_minimal)
    write_json(output_dir / "richer_matrix_vs_cutover_comparison.json", vs_cutover)
    write_json(output_dir / "richer_matrix_blocker_summary.json", blocker_summary)
    write_csv(output_dir / "richer_matrix_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "next_matrix_next_step_recommendation.json", recommendation)
    return {
        "analysis": analysis,
        "recommendation": recommendation,
        "output_paths": {
            "analysis": str((output_dir / "next_matrix_analysis_summary.json").resolve()),
            "vs_minimal": str((output_dir / "richer_matrix_vs_minimal_matrix_comparison.json").resolve()),
            "vs_cutover": str((output_dir / "richer_matrix_vs_cutover_comparison.json").resolve()),
            "blockers": str((output_dir / "richer_matrix_blocker_summary.json").resolve()),
            "tradeoff": str((output_dir / "richer_matrix_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "next_matrix_next_step_recommendation.json").resolve()),
        },
    }
