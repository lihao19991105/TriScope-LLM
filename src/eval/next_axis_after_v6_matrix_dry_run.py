"""Dry-run the refined-fusion-support-ablation-aware next-axis-after-v6 matrix v7."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.probes.confidence_probe import run_confidence_probe
from src.probes.illumination_probe import run_illumination_probe
from src.probes.reasoning_probe import run_reasoning_probe


SCHEMA_VERSION = "triscopellm/next-axis-after-v6-matrix-dry-run/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object on line {line_number} of `{path}`.")
            rows.append(payload)
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def copy_artifact(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def count_jsonl_rows(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def build_next_axis_after_v6_matrix_dry_run(
    matrix_definition_path: Path,
    matrix_bootstrap_summary_path: Path,
    materialized_matrix_dir: Path,
    v7_inputs_dir: Path,
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    reasoning_prompt_dir: Path,
    confidence_prompt_dir: Path,
    illumination_prompt_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix_definition = load_json(matrix_definition_path)
    matrix_bootstrap_summary = load_json(matrix_bootstrap_summary_path)
    if matrix_definition.get("summary_status") != "PASS":
        raise ValueError("Next-axis-after-v6 matrix definition must be PASS before dry-run.")
    if matrix_bootstrap_summary.get("summary_status") != "PASS":
        raise ValueError("Next-axis-after-v6 matrix bootstrap summary must be PASS before dry-run.")

    required_matrix_inputs = [
        materialized_matrix_dir / "real_experiment_dataset.jsonl",
        materialized_matrix_dir / "dataset_manifest.json",
        materialized_matrix_dir / "model_manifest.json",
        materialized_matrix_dir / "cutover_contract.json",
    ]
    required_v7_inputs = [
        v7_inputs_dir / "reasoning_query_contracts.jsonl",
        v7_inputs_dir / "confidence_query_contracts.jsonl",
        v7_inputs_dir / "illumination_query_contracts.jsonl",
        v7_inputs_dir / "labeled_illumination_query_contracts.jsonl",
    ]
    for path in [*required_matrix_inputs, *required_v7_inputs]:
        if not path.is_file():
            raise ValueError(f"Next-axis-after-v6 matrix dry-run input not found: `{path}`.")

    materialized_execution_dir = output_dir / "materialized_next_axis_after_v6_matrix_inputs"
    materialized_execution_dir.mkdir(parents=True, exist_ok=True)
    for src in [*required_matrix_inputs, *required_v7_inputs]:
        copy_artifact(src, materialized_execution_dir / src.name)

    dataset_rows = load_jsonl(materialized_execution_dir / "real_experiment_dataset.jsonl")
    reasoning_budget = count_jsonl_rows(materialized_execution_dir / "reasoning_query_contracts.jsonl")
    confidence_budget = count_jsonl_rows(materialized_execution_dir / "confidence_query_contracts.jsonl")
    illumination_budget = count_jsonl_rows(materialized_execution_dir / "illumination_query_contracts.jsonl")
    labeled_budget = count_jsonl_rows(materialized_execution_dir / "labeled_illumination_query_contracts.jsonl")

    dataset_name = matrix_definition["datasets"][0]
    model_name = matrix_definition["models"][0]
    cells = [
        {
            "cell_id": "dataset0_model0_routes_b_c_core",
            "dataset_name": dataset_name,
            "model_name": model_name,
            "enabled_routes": ["route_b", "route_c"],
            "cell_role": "core_route_bundle",
        },
        {
            "cell_id": "dataset0_model0_route_b_only_ablation",
            "dataset_name": dataset_name,
            "model_name": model_name,
            "enabled_routes": ["route_b_only_ablation"],
            "cell_role": "ablation_more_natural_only",
        },
        {
            "cell_id": "dataset0_model0_route_c_only_ablation",
            "dataset_name": dataset_name,
            "model_name": model_name,
            "enabled_routes": ["route_c_only_ablation"],
            "cell_role": "ablation_truth_leaning_only",
        },
        {
            "cell_id": "dataset0_model0_fusion_summary_baseline",
            "dataset_name": dataset_name,
            "model_name": model_name,
            "enabled_routes": ["fusion_summary"],
            "cell_role": "baseline_summary_style",
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_candidate_explicit",
            "dataset_name": dataset_name,
            "model_name": model_name,
            "enabled_routes": ["fusion_cell_candidate"],
            "cell_role": "explicit_candidate_style",
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_explicit",
            "dataset_name": dataset_name,
            "model_name": model_name,
            "enabled_routes": ["fusion_cell_refined"],
            "cell_role": "explicit_refined_style",
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_ablation_explicit",
            "dataset_name": dataset_name,
            "model_name": model_name,
            "enabled_routes": ["fusion_cell_refined_ablation"],
            "cell_role": "explicit_refined_ablation_style",
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_support_sweep_explicit",
            "dataset_name": dataset_name,
            "model_name": model_name,
            "enabled_routes": ["fusion_cell_refined_support_sweep"],
            "cell_role": "explicit_refined_support_sweep_style",
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_support_ablation_explicit",
            "dataset_name": dataset_name,
            "model_name": model_name,
            "enabled_routes": ["fusion_cell_refined_support_ablation"],
            "cell_role": "explicit_refined_support_ablation_style",
        },
    ]
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": matrix_bootstrap_summary["matrix_name"],
        "dry_run_mode": "fusion_refined_support_ablation_aware_matrix_simulation",
        "seed": seed,
        "route_count": len(matrix_definition["routes"]),
        "cell_count": len(cells),
        "required_modules": ["reasoning", "confidence", "illumination", *matrix_definition["routes"]],
    }
    contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": matrix_bootstrap_summary["matrix_name"],
        "fusion_mode": matrix_definition["fusion_mode"],
        "dataset_contract": load_json(materialized_execution_dir / "dataset_manifest.json"),
        "model_contract": load_json(materialized_execution_dir / "model_manifest.json"),
        "shared_inputs": {
            "dataset_input": str((materialized_execution_dir / "real_experiment_dataset.jsonl").resolve()),
            "reasoning_query_file": str((materialized_execution_dir / "reasoning_query_contracts.jsonl").resolve()),
            "confidence_query_file": str((materialized_execution_dir / "confidence_query_contracts.jsonl").resolve()),
            "illumination_query_file": str((materialized_execution_dir / "illumination_query_contracts.jsonl").resolve()),
            "labeled_illumination_query_file": str((materialized_execution_dir / "labeled_illumination_query_contracts.jsonl").resolve()),
        },
        "cells": cells,
        "route_role_map": {
            "route_b": "full more-natural route inside the core cell",
            "route_c": "full benchmark-truth-leaning route inside the core cell",
            "fusion_summary": "baseline summary-style fusion cell inherited from earlier matrix stages",
            "route_b_only_ablation": "isolate route B signal without route C or fusion",
            "route_c_only_ablation": "isolate route C signal without route B or fusion",
            "fusion_cell_candidate": "explicit candidate-style fusion cell that exposes a standalone scalar signal",
            "fusion_cell_refined": "explicit refined-style fusion cell that sharpens candidate semantics with a refinement term",
            "fusion_cell_refined_ablation": "explicit refined-ablation cell that drops the refinement term to estimate how much refined fusion signal remains after ablation",
            "fusion_cell_refined_support_sweep": "explicit support/stability sweep cell that perturbs the refined term to estimate how much refined fusion signal survives under support pressure",
            "fusion_cell_refined_support_ablation": "explicit support-focused ablation cell that removes the support-retained residual from the support-sweep signal to estimate how much refined fusion evidence survives without support-specific help",
        },
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_ready_to_dry_run": True,
        "matrix_name": matrix_bootstrap_summary["matrix_name"],
        "route_count": len(matrix_definition["routes"]),
        "cell_count": len(cells),
        "dataset_rows": len(dataset_rows),
        "fusion_mode": matrix_definition["fusion_mode"],
        "cell_budget_summary": {
            "reasoning": reasoning_budget,
            "confidence": confidence_budget,
            "illumination": illumination_budget,
            "labeled_illumination": labeled_budget,
        },
        "notes": [
            "fusion_summary is the baseline summary-style cell.",
            "fusion_cell_candidate is the first explicit fusion cell baseline.",
            "fusion_cell_refined is the refined explicit fusion cell.",
            "fusion_cell_refined_ablation removes the refinement term from the refined fusion cell.",
            "fusion_cell_refined_support_sweep perturbs the refined term to test support/stability sensitivity.",
            "fusion_cell_refined_support_ablation removes the support-retained residual from the support-sweep cell to isolate the remaining support-free refined floor.",
        ],
    }
    write_json(output_dir / "next_axis_after_v6_matrix_dry_run_plan.json", plan)
    write_json(output_dir / "next_axis_after_v6_matrix_execution_contract.json", contract)
    write_json(output_dir / "next_axis_after_v6_matrix_readiness_summary.json", readiness)

    reasoning_result = run_reasoning_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        reasoning_config_path=reasoning_config_path,
        reasoning_profile_name="default",
        prompt_dir=reasoning_prompt_dir,
        output_dir=output_dir / "dry_run_reasoning_probe",
        dataset_manifest=None,
        query_file=materialized_execution_dir / "reasoning_query_contracts.jsonl",
        query_budget_override=reasoning_budget,
        trigger_type_override="none",
        target_type_override="multiple_choice_correct_option",
        seed=seed,
        dry_run=True,
        smoke_mode=False,
    )
    confidence_result = run_confidence_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        confidence_config_path=confidence_config_path,
        confidence_profile_name="default",
        prompt_dir=confidence_prompt_dir,
        output_dir=output_dir / "dry_run_confidence_probe",
        dataset_manifest=None,
        query_file=materialized_execution_dir / "confidence_query_contracts.jsonl",
        query_budget_override=confidence_budget,
        trigger_type_override="none",
        target_type_override="multiple_choice_correct_option",
        seed=seed,
        dry_run=True,
        smoke_mode=False,
    )
    illumination_result = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        illumination_config_path=illumination_config_path,
        illumination_profile_name="default",
        prompt_dir=illumination_prompt_dir,
        output_dir=output_dir / "dry_run_illumination_probe",
        dataset_manifest=None,
        query_file=materialized_execution_dir / "illumination_query_contracts.jsonl",
        alpha_override=0.5,
        query_budget_override=illumination_budget,
        trigger_type_override="targeted_icl_demo",
        target_type_override="forced_option_label",
        seed=seed,
        dry_run=True,
        smoke_mode=False,
    )

    module_status = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "reasoning_probe": reasoning_result["summary"]["summary_status"],
        "confidence_probe": confidence_result["summary"]["summary_status"],
        "illumination_probe": illumination_result["summary"]["summary_status"],
        "route_status": {route_name: "PASS" for route_name in matrix_definition["routes"]},
    }
    cell_status = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "cells": [{**cell, "status": "PASS", "blocked_reason": ""} for cell in cells],
    }
    preview_rows = [
        {
            "cell_id": cell["cell_id"],
            "enabled_routes": "|".join(cell["enabled_routes"]),
            "cell_role": cell["cell_role"],
            "dataset_rows": len(dataset_rows),
        }
        for cell in cells
    ]
    registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": matrix_bootstrap_summary["matrix_name"],
        "artifacts": {
            "plan": str((output_dir / "next_axis_after_v6_matrix_dry_run_plan.json").resolve()),
            "contract": str((output_dir / "next_axis_after_v6_matrix_execution_contract.json").resolve()),
            "readiness": str((output_dir / "next_axis_after_v6_matrix_readiness_summary.json").resolve()),
            "module_status": str((output_dir / "next_axis_after_v6_matrix_module_status.json").resolve()),
            "cell_status": str((output_dir / "next_axis_after_v6_matrix_cell_status.json").resolve()),
        },
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": matrix_bootstrap_summary["matrix_name"],
        "dry_run_completed": True,
        "dataset_rows": len(dataset_rows),
        "route_count": len(matrix_definition["routes"]),
        "cell_count": len(cells),
        "passed_cells": [cell["cell_id"] for cell in cells],
        "passed_routes": list(matrix_definition["routes"]),
        "passed_ablation_cells": [
            "dataset0_model0_route_b_only_ablation",
            "dataset0_model0_route_c_only_ablation",
            "dataset0_model0_fusion_cell_refined_ablation_explicit",
        ],
        "passed_fusion_summary_cells": ["dataset0_model0_fusion_summary_baseline"],
        "passed_fusion_candidate_cells": ["dataset0_model0_fusion_cell_candidate_explicit"],
        "passed_fusion_refined_cells": ["dataset0_model0_fusion_cell_refined_explicit"],
        "passed_fusion_refined_ablation_cells": ["dataset0_model0_fusion_cell_refined_ablation_explicit"],
        "passed_fusion_refined_support_sweep_cells": [
            "dataset0_model0_fusion_cell_refined_support_sweep_explicit"
        ],
        "passed_fusion_refined_support_ablation_cells": [
            "dataset0_model0_fusion_cell_refined_support_ablation_explicit"
        ],
    }
    write_json(output_dir / "next_axis_after_v6_matrix_module_status.json", module_status)
    write_json(output_dir / "next_axis_after_v6_matrix_cell_status.json", cell_status)
    write_json(output_dir / "next_axis_after_v6_matrix_dry_run_registry.json", registry)
    write_json(output_dir / "next_axis_after_v6_matrix_dry_run_summary.json", summary)
    write_jsonl(output_dir / "next_axis_after_v6_matrix_dry_run_preview.jsonl", preview_rows)
    (output_dir / "next_axis_after_v6_matrix_dry_run.log").write_text(
        "next-axis-after-v6 matrix dry-run complete\n"
        f"matrix_name={matrix_bootstrap_summary['matrix_name']}\n"
        f"cell_count={len(cells)}\n"
        f"route_count={len(matrix_definition['routes'])}\n",
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "output_paths": {
            "plan": str((output_dir / "next_axis_after_v6_matrix_dry_run_plan.json").resolve()),
            "contract": str((output_dir / "next_axis_after_v6_matrix_execution_contract.json").resolve()),
            "readiness": str((output_dir / "next_axis_after_v6_matrix_readiness_summary.json").resolve()),
            "summary": str((output_dir / "next_axis_after_v6_matrix_dry_run_summary.json").resolve()),
            "registry": str((output_dir / "next_axis_after_v6_matrix_dry_run_registry.json").resolve()),
        },
    }
