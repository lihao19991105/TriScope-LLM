"""Bootstrap the next real-experiment matrix after minimal matrix analysis."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/next-real-experiment-matrix-bootstrap/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def copy_artifact(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def build_next_real_experiment_matrix_bootstrap(
    recommendation_path: Path,
    current_matrix_definition_path: Path,
    current_matrix_contract_path: Path,
    current_matrix_inputs_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    recommendation = load_json(recommendation_path)
    current_definition = load_json(current_matrix_definition_path)
    current_contract = load_json(current_matrix_contract_path)
    if recommendation.get("recommended_next_step") != "bootstrap_next_real_experiment_matrix":
        raise ValueError("065 expects recommendation to request next real-experiment matrix bootstrap.")

    matrix_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_next_step": "bootstrap_next_real_experiment_matrix",
        "preferred_expansion_axis": recommendation["preferred_expansion_axis"],
        "based_on_matrix": current_contract["matrix_name"],
    }
    matrix_definition = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": "next_real_experiment_matrix_v2",
        "datasets": current_definition["datasets"],
        "labels": current_definition["labels"],
        "models": current_definition["models"],
        "routes": ["route_b", "route_c", "fusion_summary", "route_b_only_ablation", "route_c_only_ablation"],
        "output_expectations": [
            "route_b_summary",
            "route_c_summary",
            "fusion_summary",
            "analysis_summary",
            "ablation_summary",
        ],
        "expansion_notes": [
            "This next matrix keeps dataset/model fixed but expands route/output coverage.",
            "The goal is to enrich the real-experiment matrix before considering heavier model or dataset expansion.",
        ],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "next_matrix_ready": True,
        "matrix_name": matrix_definition["matrix_name"],
        "route_count": len(matrix_definition["routes"]),
        "dataset_count": len(matrix_definition["datasets"]),
        "model_count": len(matrix_definition["models"]),
    }
    write_json(output_dir / "next_real_experiment_matrix_plan.json", matrix_plan)
    write_json(output_dir / "next_real_experiment_matrix_definition.json", matrix_definition)
    write_json(output_dir / "next_real_experiment_matrix_readiness_summary.json", readiness)

    materialized_dir = output_dir / "materialized_next_real_experiment_matrix"
    materialized_dir.mkdir(parents=True, exist_ok=True)
    for name in ["real_experiment_dataset.jsonl", "dataset_manifest.json", "model_manifest.json", "cutover_contract.json"]:
        copy_artifact(current_matrix_inputs_dir / name, materialized_dir / name)

    input_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": matrix_definition["matrix_name"],
        "base_matrix": current_contract["matrix_name"],
        "route_set": matrix_definition["routes"],
        "dataset_contract": current_contract["dataset_contract"],
        "model_contract": current_contract["model_contract"],
        "expansion_axis": recommendation["preferred_expansion_axis"],
    }
    bootstrap_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": matrix_definition["matrix_name"],
        "materialized_inputs_dir": str(materialized_dir.resolve()),
        "route_count": len(matrix_definition["routes"]),
        "dataset_count": len(matrix_definition["datasets"]),
        "model_count": len(matrix_definition["models"]),
    }
    write_json(output_dir / "next_real_experiment_input_contract.json", input_contract)
    write_json(output_dir / "next_real_experiment_bootstrap_summary.json", bootstrap_summary)
    return {
        "summary": bootstrap_summary,
        "output_paths": {
            "plan": str((output_dir / "next_real_experiment_matrix_plan.json").resolve()),
            "definition": str((output_dir / "next_real_experiment_matrix_definition.json").resolve()),
            "readiness": str((output_dir / "next_real_experiment_matrix_readiness_summary.json").resolve()),
            "contract": str((output_dir / "next_real_experiment_input_contract.json").resolve()),
            "summary": str((output_dir / "next_real_experiment_bootstrap_summary.json").resolve()),
        },
    }
