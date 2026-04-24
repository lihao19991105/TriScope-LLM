"""First minimal real-experiment matrix execution builder."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

from src.eval.rerun_route_b_on_labeled_split_v6 import run_route_b_v6
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/first-minimal-real-experiment-matrix-execution/v1"


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


def build_first_minimal_real_experiment_matrix_execution(
    matrix_dry_run_summary_path: Path,
    matrix_cell_status_path: Path,
    matrix_execution_contract_path: Path,
    matrix_definition_path: Path,
    v6_inputs_dir: Path,
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    reasoning_prompt_dir: Path,
    confidence_prompt_dir: Path,
    illumination_prompt_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    dry_run_summary = load_json(matrix_dry_run_summary_path)
    cell_status = load_json(matrix_cell_status_path)
    contract = load_json(matrix_execution_contract_path)
    matrix_definition = load_json(matrix_definition_path)
    if dry_run_summary.get("summary_status") != "PASS":
        raise ValueError("Matrix execution requires PASS dry-run summary.")
    if cell_status.get("summary_status") != "PASS":
        raise ValueError("Matrix execution requires PASS cell status.")

    cell = contract["cells"][0]
    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell_id": cell["cell_id"],
        "selected_dataset": cell["dataset_name"],
        "selected_model": cell["model_name"],
        "selected_routes": cell["routes"],
        "why_selected": [
            "The minimal matrix currently contains one coherent dataset/model cell, so executing that full cell is the smallest honest matrix execution step.",
            "Dry-run showed that route B, route C, and fusion_summary are all execution-mapped for this cell.",
        ],
        "success_standard": [
            "execute route B on the selected matrix cell",
            "execute route C on the selected matrix cell",
            "emit one integrated matrix-level fusion summary",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cell_id": cell["cell_id"],
        "cell_count": len(contract["cells"]),
        "route_count": len(matrix_definition["routes"]),
        "seed": seed,
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_ready_to_execute": True,
        "selected_cell_id": cell["cell_id"],
        "selected_routes": cell["routes"],
    }
    write_json(output_dir / "first_matrix_execution_selection.json", selection)
    write_json(output_dir / "first_matrix_execution_plan.json", plan)
    write_json(output_dir / "first_matrix_execution_readiness_summary.json", readiness)

    execution_root = output_dir / "first_matrix_execution_outputs"
    route_b_dir = execution_root / "route_b"
    route_c_dir = execution_root / "route_c"

    route_c_result = run_route_c_v6(
        models_config_path=models_config_path,
        reasoning_config_path=reasoning_config_path,
        confidence_config_path=confidence_config_path,
        illumination_config_path=illumination_config_path,
        reasoning_prompt_dir=reasoning_prompt_dir,
        confidence_prompt_dir=confidence_prompt_dir,
        illumination_prompt_dir=illumination_prompt_dir,
        v6_inputs_dir=v6_inputs_dir,
        output_dir=route_c_dir,
        seed=seed,
        label_threshold=label_threshold,
    )
    route_b_result = run_route_b_v6(
        models_config_path=models_config_path,
        reasoning_config_path=reasoning_config_path,
        confidence_config_path=confidence_config_path,
        illumination_config_path=illumination_config_path,
        reasoning_prompt_dir=reasoning_prompt_dir,
        confidence_prompt_dir=confidence_prompt_dir,
        illumination_prompt_dir=illumination_prompt_dir,
        v6_inputs_dir=v6_inputs_dir,
        output_dir=route_b_dir,
        seed=seed,
        label_threshold=label_threshold,
    )

    route_b_summary = load_json(route_b_dir / "route_b_v6_summary.json")
    route_c_summary = load_json(route_c_dir / "route_c_v6_summary.json")
    route_b_logistic = load_json(route_b_dir / "route_b_v6_logistic_summary.json")
    route_c_logistic = load_json(route_c_dir / "route_c_v6_logistic_summary.json")
    fusion_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_mode": "matrix_cell_cross_route_summary",
        "cell_id": cell["cell_id"],
        "route_b_rows": route_b_summary["num_rows"],
        "route_c_rows": route_c_summary["num_rows"],
        "shared_base_samples": route_b_summary["num_base_samples"],
        "notes": [
            "This is the first matrix-level fusion summary on top of the minimal real-experiment matrix.",
            "It is still an integrated summary rather than a separate benchmark-grade fusion classifier.",
        ],
    }
    copy_artifact(route_b_dir / "route_b_v6_summary.json", output_dir / "first_matrix_route_b_summary.json")
    copy_artifact(route_c_dir / "route_c_v6_summary.json", output_dir / "first_matrix_route_c_summary.json")
    write_json(output_dir / "first_matrix_fusion_summary.json", fusion_summary)

    registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cell_id": cell["cell_id"],
        "artifacts": {
            "route_b_summary": str((output_dir / "first_matrix_route_b_summary.json").resolve()),
            "route_c_summary": str((output_dir / "first_matrix_route_c_summary.json").resolve()),
            "fusion_summary": str((output_dir / "first_matrix_fusion_summary.json").resolve()),
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
        "route_b_mean_prediction_score": route_b_logistic["mean_prediction_score"],
        "route_c_mean_prediction_score": route_c_logistic["mean_prediction_score"],
        "shared_base_samples": route_b_summary["num_base_samples"],
        "executed_cell_count": 1,
    }
    cell_metric_rows = [
        {
            "cell_id": cell["cell_id"],
            "dataset_name": cell["dataset_name"],
            "model_name": cell["model_name"],
            "route_b_rows": route_b_summary["num_rows"],
            "route_c_rows": route_c_summary["num_rows"],
            "shared_base_samples": route_b_summary["num_base_samples"],
            "route_b_mean_prediction_score": route_b_logistic["mean_prediction_score"],
            "route_c_mean_prediction_score": route_c_logistic["mean_prediction_score"],
            "fusion_mode": "matrix_cell_cross_route_summary",
        }
    ]
    preview_rows = [
        {
            "cell_id": cell["cell_id"],
            "route": "B",
            "summary_path": str((output_dir / "first_matrix_route_b_summary.json").resolve()),
            "rows": route_b_summary["num_rows"],
        },
        {
            "cell_id": cell["cell_id"],
            "route": "C",
            "summary_path": str((output_dir / "first_matrix_route_c_summary.json").resolve()),
            "rows": route_c_summary["num_rows"],
        },
    ]
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": dry_run_summary["matrix_name"],
        "selected_cell_id": cell["cell_id"],
        "executed_layers": ["route_b", "route_c", "fusion_summary"],
        "executed_cell_count": 1,
        "notes": [
            "This is the first matrix-level real-experiment execution on top of the minimal matrix object.",
            "Route B and route C are full executes for the selected cell; fusion is represented as an integrated matrix-level summary.",
        ],
    }
    write_json(output_dir / "first_matrix_execution_registry.json", registry)
    write_json(output_dir / "first_matrix_execution_metrics.json", metrics)
    write_json(output_dir / "first_matrix_execution_run_summary.json", run_summary)
    write_csv(output_dir / "first_matrix_cell_metrics.csv", cell_metric_rows)
    (output_dir / "first_matrix_execution_preview.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=True) for row in preview_rows) + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "first_matrix_execution_selection.json").resolve()),
            "plan": str((output_dir / "first_matrix_execution_plan.json").resolve()),
            "readiness": str((output_dir / "first_matrix_execution_readiness_summary.json").resolve()),
            "registry": str((output_dir / "first_matrix_execution_registry.json").resolve()),
            "run_summary": str((output_dir / "first_matrix_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "first_matrix_execution_metrics.json").resolve()),
            "cell_metrics": str((output_dir / "first_matrix_cell_metrics.csv").resolve()),
        },
    }
