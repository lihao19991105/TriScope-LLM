"""Execute the richer next real-experiment matrix v2."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/next-real-experiment-matrix-execution/v1"


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


def copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, dirs_exist_ok=True)


def build_next_real_experiment_matrix_execution(
    matrix_dry_run_summary_path: Path,
    matrix_cell_status_path: Path,
    matrix_execution_contract_path: Path,
    matrix_definition_path: Path,
    route_b_source_dir: Path,
    route_c_source_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dry_run_summary = load_json(matrix_dry_run_summary_path)
    cell_status = load_json(matrix_cell_status_path)
    contract = load_json(matrix_execution_contract_path)
    matrix_definition = load_json(matrix_definition_path)
    if dry_run_summary.get("summary_status") != "PASS":
        raise ValueError("Next matrix execution requires PASS dry-run summary.")
    if cell_status.get("summary_status") != "PASS":
        raise ValueError("Next matrix execution requires PASS cell status.")

    cells = contract["cells"]
    full_cell = cells[0]
    route_b_ablation_cell = cells[1]
    route_c_ablation_cell = cells[2]
    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cells": [cell["cell_id"] for cell in cells],
        "selected_dataset": full_cell["dataset_name"],
        "selected_model": full_cell["model_name"],
        "selected_routes": matrix_definition["routes"],
        "why_selected": [
            "The richer v2 matrix exists specifically to make route_b_only_ablation and route_c_only_ablation executable, so the first honest execution should include them.",
            "Dry-run showed that the full cell and both ablation cells are all execution-mapped on the same dataset/model substrate.",
        ],
        "success_standard": [
            "execute the full richer cell with route B + route C + fusion_summary",
            "emit a route_b_only_ablation artifact",
            "emit a route_c_only_ablation artifact",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cell_count": len(cells),
        "route_count": len(matrix_definition["routes"]),
        "execution_mode": "rehydrate_from_passed_v6_route_artifacts",
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_ready_to_execute": True,
        "selected_cells": [cell["cell_id"] for cell in cells],
        "selected_routes": matrix_definition["routes"],
    }
    write_json(output_dir / "next_matrix_execution_selection.json", selection)
    write_json(output_dir / "next_matrix_execution_plan.json", plan)
    write_json(output_dir / "next_matrix_execution_readiness_summary.json", readiness)

    execution_root = output_dir / "next_matrix_execution_outputs"
    route_b_dir = execution_root / "route_b"
    route_c_dir = execution_root / "route_c"
    required_route_b = [
        route_b_source_dir / "route_b_v6_summary.json",
        route_b_source_dir / "route_b_v6_logistic_summary.json",
        route_b_source_dir / "route_b_v6_run_summary.json",
    ]
    required_route_c = [
        route_c_source_dir / "route_c_v6_summary.json",
        route_c_source_dir / "route_c_v6_logistic_summary.json",
        route_c_source_dir / "route_c_v6_run_summary.json",
    ]
    for path in [*required_route_b, *required_route_c]:
        if not path.is_file():
            raise ValueError(f"Next matrix execution source artifact not found: `{path}`.")

    copy_tree(route_b_source_dir, route_b_dir)
    copy_tree(route_c_source_dir, route_c_dir)

    route_b_summary = load_json(route_b_dir / "route_b_v6_summary.json")
    route_c_summary = load_json(route_c_dir / "route_c_v6_summary.json")
    route_b_logistic = load_json(route_b_dir / "route_b_v6_logistic_summary.json")
    route_c_logistic = load_json(route_c_dir / "route_c_v6_logistic_summary.json")

    fusion_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_mode": "richer_matrix_cross_route_summary",
        "cell_id": full_cell["cell_id"],
        "enabled_routes": full_cell["enabled_routes"],
        "route_b_rows": route_b_summary["num_rows"],
        "route_c_rows": route_c_summary["num_rows"],
        "shared_base_samples": route_b_summary["num_base_samples"],
        "notes": [
            "This richer matrix fusion summary sits on top of full route B and route C execution.",
            "It remains an integrated summary, not yet a dedicated fusion classifier cell.",
        ],
    }
    route_b_ablation_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "ablation_route_name": "route_b_only_ablation",
        "cell_id": route_b_ablation_cell["cell_id"],
        "source_route_summary": str((route_b_dir / "route_b_v6_summary.json").resolve()),
        "num_rows": route_b_summary["num_rows"],
        "num_base_samples": route_b_summary["num_base_samples"],
        "mean_prediction_score": route_b_logistic["mean_prediction_score"],
        "enabled_routes": route_b_ablation_cell["enabled_routes"],
        "disabled_routes": ["route_c", "fusion_summary"],
        "notes": [
            "This ablation cell isolates the more-natural route without route C or fusion support.",
            "It is derived from the actual route B execution on the same real-experiment matrix substrate.",
        ],
    }
    route_c_ablation_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "ablation_route_name": "route_c_only_ablation",
        "cell_id": route_c_ablation_cell["cell_id"],
        "source_route_summary": str((route_c_dir / "route_c_v6_summary.json").resolve()),
        "num_rows": route_c_summary["num_rows"],
        "num_base_samples": route_c_summary["num_base_samples"],
        "mean_prediction_score": route_c_logistic["mean_prediction_score"],
        "enabled_routes": route_c_ablation_cell["enabled_routes"],
        "disabled_routes": ["route_b", "fusion_summary"],
        "notes": [
            "This ablation cell isolates the benchmark-truth-leaning route without route B or fusion support.",
            "It is derived from the actual route C execution on the same real-experiment matrix substrate.",
        ],
    }

    copy_artifact(route_b_dir / "route_b_v6_summary.json", output_dir / "next_matrix_route_b_summary.json")
    copy_artifact(route_c_dir / "route_c_v6_summary.json", output_dir / "next_matrix_route_c_summary.json")
    write_json(output_dir / "next_matrix_route_b_only_ablation_summary.json", route_b_ablation_summary)
    write_json(output_dir / "next_matrix_route_c_only_ablation_summary.json", route_c_ablation_summary)
    write_json(output_dir / "next_matrix_fusion_summary.json", fusion_summary)

    registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cells": [cell["cell_id"] for cell in cells],
        "artifacts": {
            "route_b_summary": str((output_dir / "next_matrix_route_b_summary.json").resolve()),
            "route_c_summary": str((output_dir / "next_matrix_route_c_summary.json").resolve()),
            "route_b_ablation_summary": str((output_dir / "next_matrix_route_b_only_ablation_summary.json").resolve()),
            "route_c_ablation_summary": str((output_dir / "next_matrix_route_c_only_ablation_summary.json").resolve()),
            "fusion_summary": str((output_dir / "next_matrix_fusion_summary.json").resolve()),
            "route_b_output_dir": str(route_b_dir.resolve()),
            "route_c_output_dir": str(route_c_dir.resolve()),
        },
    }
    metrics = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "route_b_rows": route_b_summary["num_rows"],
        "route_c_rows": route_c_summary["num_rows"],
        "route_b_only_ablation_rows": route_b_summary["num_rows"],
        "route_c_only_ablation_rows": route_c_summary["num_rows"],
        "route_b_mean_prediction_score": route_b_logistic["mean_prediction_score"],
        "route_c_mean_prediction_score": route_c_logistic["mean_prediction_score"],
        "shared_base_samples": route_b_summary["num_base_samples"],
        "executed_cell_count": len(cells),
        "ablation_cell_count": 2,
    }
    cell_metric_rows = [
        {
            "cell_id": full_cell["cell_id"],
            "dataset_name": full_cell["dataset_name"],
            "model_name": full_cell["model_name"],
            "enabled_routes": "|".join(full_cell["enabled_routes"]),
            "route_b_rows": route_b_summary["num_rows"],
            "route_c_rows": route_c_summary["num_rows"],
            "shared_base_samples": route_b_summary["num_base_samples"],
            "mean_prediction_score": "",
            "fusion_mode": "richer_matrix_cross_route_summary",
        },
        {
            "cell_id": route_b_ablation_cell["cell_id"],
            "dataset_name": route_b_ablation_cell["dataset_name"],
            "model_name": route_b_ablation_cell["model_name"],
            "enabled_routes": "|".join(route_b_ablation_cell["enabled_routes"]),
            "route_b_rows": route_b_summary["num_rows"],
            "route_c_rows": 0,
            "shared_base_samples": route_b_summary["num_base_samples"],
            "mean_prediction_score": route_b_logistic["mean_prediction_score"],
            "fusion_mode": "disabled",
        },
        {
            "cell_id": route_c_ablation_cell["cell_id"],
            "dataset_name": route_c_ablation_cell["dataset_name"],
            "model_name": route_c_ablation_cell["model_name"],
            "enabled_routes": "|".join(route_c_ablation_cell["enabled_routes"]),
            "route_b_rows": 0,
            "route_c_rows": route_c_summary["num_rows"],
            "shared_base_samples": route_c_summary["num_base_samples"],
            "mean_prediction_score": route_c_logistic["mean_prediction_score"],
            "fusion_mode": "disabled",
        },
    ]
    preview_rows = [
        {
            "cell_id": full_cell["cell_id"],
            "route": "route_b",
            "summary_path": str((output_dir / "next_matrix_route_b_summary.json").resolve()),
            "rows": route_b_summary["num_rows"],
        },
        {
            "cell_id": full_cell["cell_id"],
            "route": "route_c",
            "summary_path": str((output_dir / "next_matrix_route_c_summary.json").resolve()),
            "rows": route_c_summary["num_rows"],
        },
        {
            "cell_id": route_b_ablation_cell["cell_id"],
            "route": "route_b_only_ablation",
            "summary_path": str((output_dir / "next_matrix_route_b_only_ablation_summary.json").resolve()),
            "rows": route_b_summary["num_rows"],
        },
        {
            "cell_id": route_c_ablation_cell["cell_id"],
            "route": "route_c_only_ablation",
            "summary_path": str((output_dir / "next_matrix_route_c_only_ablation_summary.json").resolve()),
            "rows": route_c_summary["num_rows"],
        },
    ]
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cells": [cell["cell_id"] for cell in cells],
        "executed_layers": ["route_b", "route_c", "fusion_summary", "route_b_only_ablation", "route_c_only_ablation"],
        "executed_cell_count": len(cells),
        "notes": [
            "This richer matrix execution lifts already-passed route B and route C v6 execution artifacts into explicit matrix cells.",
            "The new ablation routes now exist as executed matrix artifacts, not just bootstrap definitions.",
        ],
    }
    write_json(output_dir / "next_matrix_execution_registry.json", registry)
    write_json(output_dir / "next_matrix_execution_metrics.json", metrics)
    write_json(output_dir / "next_matrix_execution_run_summary.json", run_summary)
    write_csv(output_dir / "next_matrix_cell_metrics.csv", cell_metric_rows)
    (output_dir / "next_matrix_execution_preview.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=True) for row in preview_rows) + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "next_matrix_execution_selection.json").resolve()),
            "plan": str((output_dir / "next_matrix_execution_plan.json").resolve()),
            "readiness": str((output_dir / "next_matrix_execution_readiness_summary.json").resolve()),
            "registry": str((output_dir / "next_matrix_execution_registry.json").resolve()),
            "run_summary": str((output_dir / "next_matrix_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "next_matrix_execution_metrics.json").resolve()),
            "cell_metrics": str((output_dir / "next_matrix_cell_metrics.csv").resolve()),
        },
    }
