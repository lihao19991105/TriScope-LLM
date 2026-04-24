"""Bootstrap the next minimal real-experiment matrix."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/minimal-real-experiment-matrix-bootstrap/v1"


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


def build_minimal_real_experiment_matrix_bootstrap(
    recommendation_path: Path,
    first_real_selection_path: Path,
    cutover_contract_path: Path,
    cutover_inputs_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    recommendation = load_json(recommendation_path)
    if recommendation.get("recommended_next_step") != "bootstrap_minimal_real_experiment_matrix":
        raise ValueError("061 expects recommendation to request minimal real-experiment matrix bootstrap.")
    first_real_selection = load_json(first_real_selection_path)
    cutover_contract = load_json(cutover_contract_path)

    matrix_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_next_step": "bootstrap_minimal_real_experiment_matrix",
        "based_on_selection": first_real_selection.get("selected_path"),
    }
    matrix_definition = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "datasets": ["larger_labeled_split_v6_local_curated_csqa_style"],
        "labels": ["answer_key_backed_task_correctness_and_contract_violation_bundle"],
        "models": ["pilot_distilgpt2_hf"],
        "routes": ["route_b", "route_c", "fusion_summary"],
        "output_expectations": ["route_b_summary", "route_c_summary", "fusion_summary", "analysis_summary"],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_ready": True,
        "notes": [
            "This matrix stays intentionally small and inherits the v6 cutover dataset/model.",
            "It is a bootstrap object for the next real-experiment iteration, not the full matrix itself.",
        ],
    }
    write_json(output_dir / "minimal_real_experiment_matrix_plan.json", matrix_plan)
    write_json(output_dir / "minimal_real_experiment_matrix_definition.json", matrix_definition)
    write_json(output_dir / "minimal_real_experiment_matrix_readiness_summary.json", readiness)

    materialized_dir = output_dir / "materialized_minimal_real_experiment_matrix"
    materialized_dir.mkdir(parents=True, exist_ok=True)
    for name in ["real_experiment_dataset.jsonl", "dataset_manifest.json", "model_manifest.json"]:
        copy_artifact(cutover_inputs_dir / name, materialized_dir / name)
    copy_artifact(cutover_contract_path, materialized_dir / "cutover_contract.json")

    input_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": "minimal_real_experiment_matrix_v1",
        "base_cutover_experiment": cutover_contract["experiment_name"],
        "route_set": matrix_definition["routes"],
        "dataset_contract": cutover_contract["dataset_contract"],
        "model_contract": cutover_contract["model_contract"],
    }
    bootstrap_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": "minimal_real_experiment_matrix_v1",
        "materialized_inputs_dir": str(materialized_dir.resolve()),
        "route_count": len(matrix_definition["routes"]),
        "dataset_count": len(matrix_definition["datasets"]),
        "model_count": len(matrix_definition["models"]),
    }
    write_json(output_dir / "minimal_real_experiment_input_contract.json", input_contract)
    write_json(output_dir / "minimal_real_experiment_bootstrap_summary.json", bootstrap_summary)
    return {
        "summary": bootstrap_summary,
        "output_paths": {
            "plan": str((output_dir / "minimal_real_experiment_matrix_plan.json").resolve()),
            "definition": str((output_dir / "minimal_real_experiment_matrix_definition.json").resolve()),
            "readiness": str((output_dir / "minimal_real_experiment_matrix_readiness_summary.json").resolve()),
            "contract": str((output_dir / "minimal_real_experiment_input_contract.json").resolve()),
            "summary": str((output_dir / "minimal_real_experiment_bootstrap_summary.json").resolve()),
        },
    }
