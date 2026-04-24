"""Execute the fusion-cell-aware post-next real-experiment matrix v3."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-next-real-experiment-matrix-execution/v1"


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


def copy_artifact(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def build_post_next_real_experiment_matrix_execution(
    matrix_dry_run_summary_path: Path,
    matrix_cell_status_path: Path,
    matrix_execution_contract_path: Path,
    matrix_definition_path: Path,
    v2_execution_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dry_run_summary = load_json(matrix_dry_run_summary_path)
    cell_status = load_json(matrix_cell_status_path)
    contract = load_json(matrix_execution_contract_path)
    matrix_definition = load_json(matrix_definition_path)
    if dry_run_summary.get("summary_status") != "PASS":
        raise ValueError("Post-next matrix execution requires PASS dry-run summary.")
    if cell_status.get("summary_status") != "PASS":
        raise ValueError("Post-next matrix execution requires PASS cell status.")

    required_sources = [
        v2_execution_dir / "next_matrix_route_b_summary.json",
        v2_execution_dir / "next_matrix_route_c_summary.json",
        v2_execution_dir / "next_matrix_route_b_only_ablation_summary.json",
        v2_execution_dir / "next_matrix_route_c_only_ablation_summary.json",
        v2_execution_dir / "next_matrix_fusion_summary.json",
        v2_execution_dir / "next_matrix_execution_metrics.json",
    ]
    for path in required_sources:
        if not path.is_file():
            raise ValueError(f"Post-next matrix execution source artifact not found: `{path}`.")

    route_b_summary = load_json(v2_execution_dir / "next_matrix_route_b_summary.json")
    route_c_summary = load_json(v2_execution_dir / "next_matrix_route_c_summary.json")
    route_b_ablation_summary = load_json(v2_execution_dir / "next_matrix_route_b_only_ablation_summary.json")
    route_c_ablation_summary = load_json(v2_execution_dir / "next_matrix_route_c_only_ablation_summary.json")
    fusion_summary = load_json(v2_execution_dir / "next_matrix_fusion_summary.json")
    v2_metrics = load_json(v2_execution_dir / "next_matrix_execution_metrics.json")

    cells = contract["cells"]
    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cells": [cell["cell_id"] for cell in cells],
        "selected_dataset": cells[0]["dataset_name"],
        "selected_model": cells[0]["model_name"],
        "selected_routes": matrix_definition["routes"],
        "why_selected": [
            "The purpose of v3 is to make fusion_cell_candidate a real execution object, so the first honest execution must include both fusion_summary and fusion_cell_candidate.",
            "The supporting route and ablation artifacts already exist from v2 execution and can be rehydrated into the new matrix without re-running the same substrate.",
        ],
        "success_standard": [
            "rehydrate route_b / route_c / ablation summaries into v3 matrix cells",
            "execute an explicit fusion_cell_candidate summary",
            "keep fusion_summary available for direct comparison",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cell_count": len(cells),
        "route_count": len(matrix_definition["routes"]),
        "execution_mode": "rehydrate_from_v2_execution_and_construct_explicit_fusion_candidate",
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_ready_to_execute": True,
        "selected_cells": [cell["cell_id"] for cell in cells],
        "selected_routes": matrix_definition["routes"],
        "fusion_mode": matrix_definition["fusion_mode"],
    }
    write_json(output_dir / "post_next_matrix_execution_selection.json", selection)
    write_json(output_dir / "post_next_matrix_execution_plan.json", plan)
    write_json(output_dir / "post_next_matrix_execution_readiness_summary.json", readiness)

    outputs_dir = output_dir / "post_next_matrix_execution_outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    copy_artifact(v2_execution_dir / "next_matrix_route_b_summary.json", output_dir / "post_next_matrix_route_b_summary.json")
    copy_artifact(v2_execution_dir / "next_matrix_route_c_summary.json", output_dir / "post_next_matrix_route_c_summary.json")
    copy_artifact(v2_execution_dir / "next_matrix_route_b_only_ablation_summary.json", output_dir / "post_next_matrix_route_b_only_ablation_summary.json")
    copy_artifact(v2_execution_dir / "next_matrix_route_c_only_ablation_summary.json", output_dir / "post_next_matrix_route_c_only_ablation_summary.json")
    copy_artifact(v2_execution_dir / "next_matrix_fusion_summary.json", output_dir / "post_next_matrix_fusion_summary.json")

    route_b_score = float(v2_metrics["route_b_mean_prediction_score"])
    route_c_score = float(v2_metrics["route_c_mean_prediction_score"])
    score_gap = abs(route_b_score - route_c_score)
    explicit_candidate_score = (route_b_score + route_c_score + score_gap) / 3.0
    fusion_cell_candidate_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "cell_id": "dataset0_model0_fusion_cell_candidate_explicit",
        "fusion_mode": "explicit_candidate_style",
        "base_matrix": "next_real_experiment_matrix_v2",
        "source_fusion_summary": str((v2_execution_dir / "next_matrix_fusion_summary.json").resolve()),
        "source_route_b_summary": str((v2_execution_dir / "next_matrix_route_b_summary.json").resolve()),
        "source_route_c_summary": str((v2_execution_dir / "next_matrix_route_c_summary.json").resolve()),
        "shared_base_samples": int(v2_metrics["shared_base_samples"]),
        "route_b_mean_prediction_score": route_b_score,
        "route_c_mean_prediction_score": route_c_score,
        "score_gap": score_gap,
        "candidate_signal_score": explicit_candidate_score,
        "candidate_value_add": [
            "Unlike fusion_summary, this artifact is represented as an explicit matrix cell with its own scalar signal score.",
            "It exposes the route-level score gap directly, making fusion evidence easier to compare against ablations.",
        ],
        "limitations": [
            "Still derived from the same local curated split and lightweight model.",
            "Still not a trained benchmark-grade fusion classifier.",
        ],
    }
    write_json(output_dir / "post_next_matrix_fusion_cell_candidate_summary.json", fusion_cell_candidate_summary)

    registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cells": [cell["cell_id"] for cell in cells],
        "artifacts": {
            "route_b_summary": str((output_dir / "post_next_matrix_route_b_summary.json").resolve()),
            "route_c_summary": str((output_dir / "post_next_matrix_route_c_summary.json").resolve()),
            "route_b_ablation_summary": str((output_dir / "post_next_matrix_route_b_only_ablation_summary.json").resolve()),
            "route_c_ablation_summary": str((output_dir / "post_next_matrix_route_c_only_ablation_summary.json").resolve()),
            "fusion_summary": str((output_dir / "post_next_matrix_fusion_summary.json").resolve()),
            "fusion_cell_candidate_summary": str((output_dir / "post_next_matrix_fusion_cell_candidate_summary.json").resolve()),
        },
    }
    metrics = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "route_b_rows": route_b_summary["num_rows"],
        "route_c_rows": route_c_summary["num_rows"],
        "route_b_only_ablation_rows": route_b_ablation_summary["num_rows"],
        "route_c_only_ablation_rows": route_c_ablation_summary["num_rows"],
        "route_b_mean_prediction_score": route_b_score,
        "route_c_mean_prediction_score": route_c_score,
        "fusion_summary_present": True,
        "fusion_cell_candidate_executed": True,
        "fusion_cell_candidate_score": explicit_candidate_score,
        "fusion_cell_score_gap": score_gap,
        "shared_base_samples": int(v2_metrics["shared_base_samples"]),
        "executed_cell_count": len(cells),
        "ablation_cell_count": 2,
        "explicit_fusion_cell_count": 1,
    }
    cell_metric_rows = [
        {
            "cell_id": "dataset0_model0_routes_b_c_core",
            "cell_role": "core_route_bundle",
            "enabled_routes": "route_b|route_c",
            "rows": route_b_summary["num_rows"],
            "shared_base_samples": int(v2_metrics["shared_base_samples"]),
            "signal_value": "",
        },
        {
            "cell_id": "dataset0_model0_route_b_only_ablation",
            "cell_role": "ablation_more_natural_only",
            "enabled_routes": "route_b_only_ablation",
            "rows": route_b_ablation_summary["num_rows"],
            "shared_base_samples": route_b_ablation_summary["num_base_samples"],
            "signal_value": route_b_ablation_summary["mean_prediction_score"],
        },
        {
            "cell_id": "dataset0_model0_route_c_only_ablation",
            "cell_role": "ablation_truth_leaning_only",
            "enabled_routes": "route_c_only_ablation",
            "rows": route_c_ablation_summary["num_rows"],
            "shared_base_samples": route_c_ablation_summary["num_base_samples"],
            "signal_value": route_c_ablation_summary["mean_prediction_score"],
        },
        {
            "cell_id": "dataset0_model0_fusion_summary_inherited",
            "cell_role": "inherited_summary_style",
            "enabled_routes": "fusion_summary",
            "rows": fusion_summary["shared_base_samples"],
            "shared_base_samples": fusion_summary["shared_base_samples"],
            "signal_value": "",
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_candidate_explicit",
            "cell_role": "explicit_candidate_style",
            "enabled_routes": "fusion_cell_candidate",
            "rows": fusion_cell_candidate_summary["shared_base_samples"],
            "shared_base_samples": fusion_cell_candidate_summary["shared_base_samples"],
            "signal_value": fusion_cell_candidate_summary["candidate_signal_score"],
        },
    ]
    preview_rows = [
        {
            "cell_id": "dataset0_model0_fusion_summary_inherited",
            "route": "fusion_summary",
            "summary_path": str((output_dir / "post_next_matrix_fusion_summary.json").resolve()),
            "rows": fusion_summary["shared_base_samples"],
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_candidate_explicit",
            "route": "fusion_cell_candidate",
            "summary_path": str((output_dir / "post_next_matrix_fusion_cell_candidate_summary.json").resolve()),
            "rows": fusion_cell_candidate_summary["shared_base_samples"],
        },
    ]
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cells": [cell["cell_id"] for cell in cells],
        "executed_layers": [
            "route_b",
            "route_c",
            "fusion_summary",
            "route_b_only_ablation",
            "route_c_only_ablation",
            "fusion_cell_candidate",
        ],
        "executed_cell_count": len(cells),
        "notes": [
            "This v3 matrix execution promotes fusion_cell_candidate into an explicit execution artifact.",
            "fusion_summary remains available as the inherited summary-style baseline for comparison.",
        ],
    }
    write_json(output_dir / "post_next_matrix_execution_registry.json", registry)
    write_json(output_dir / "post_next_matrix_execution_metrics.json", metrics)
    write_json(output_dir / "post_next_matrix_execution_run_summary.json", run_summary)
    write_csv(output_dir / "post_next_matrix_cell_metrics.csv", cell_metric_rows)
    (output_dir / "post_next_matrix_execution_preview.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=True) for row in preview_rows) + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "post_next_matrix_execution_selection.json").resolve()),
            "plan": str((output_dir / "post_next_matrix_execution_plan.json").resolve()),
            "readiness": str((output_dir / "post_next_matrix_execution_readiness_summary.json").resolve()),
            "registry": str((output_dir / "post_next_matrix_execution_registry.json").resolve()),
            "run_summary": str((output_dir / "post_next_matrix_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "post_next_matrix_execution_metrics.json").resolve()),
            "cell_metrics": str((output_dir / "post_next_matrix_cell_metrics.csv").resolve()),
        },
    }
