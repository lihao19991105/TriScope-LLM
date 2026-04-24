"""Dry-run the model-axis 1.5B portability probe."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-dry-run/v1"


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


def run_local_only_loader_probe(model_source: str) -> dict[str, Any]:
    results: dict[str, Any] = {
        "model_source": model_source,
        "config_probe": {},
        "tokenizer_probe": {},
        "model_probe": {},
    }
    for cls, key in [
        (AutoConfig, "config_probe"),
        (AutoTokenizer, "tokenizer_probe"),
        (AutoModelForCausalLM, "model_probe"),
    ]:
        try:
            kwargs: dict[str, Any] = {"local_files_only": True}
            if cls is AutoTokenizer:
                kwargs["use_fast"] = True
            if cls is AutoModelForCausalLM:
                kwargs["trust_remote_code"] = False
            cls.from_pretrained(model_source, **kwargs)
            results[key] = {"status": "PASS", "error_type": None, "message": None}
        except Exception as exc:
            results[key] = {
                "status": "BLOCKED",
                "error_type": type(exc).__name__,
                "message": str(exc).split("\n")[0],
            }
    results["overall_status"] = (
        "PASS"
        if all(results[key]["status"] == "PASS" for key in ("config_probe", "tokenizer_probe", "model_probe"))
        else "BLOCKED"
    )
    return results


def build_model_axis_1p5b_dry_run(
    bootstrap_summary_path: Path,
    matrix_definition_path: Path,
    readiness_summary_path: Path,
    blocker_diagnosis_path: Path,
    recovery_options_path: Path,
    minimal_execution_candidate_path: Path,
    materialized_inputs_dir: Path,
    base_v11_inputs_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    bootstrap_summary = load_json(bootstrap_summary_path)
    matrix_definition = load_json(matrix_definition_path)
    readiness_summary = load_json(readiness_summary_path)
    blocker_diagnosis = load_json(blocker_diagnosis_path)
    recovery_options = load_json(recovery_options_path)
    minimal_candidate = load_json(minimal_execution_candidate_path)
    if bootstrap_summary.get("summary_status") != "PASS":
        raise ValueError("Model-axis 1.5B dry-run requires a PASS bootstrap summary.")

    required_bootstrap_inputs = [
        materialized_inputs_dir / "real_experiment_dataset.jsonl",
        materialized_inputs_dir / "dataset_manifest.json",
        materialized_inputs_dir / "model_manifest.json",
        materialized_inputs_dir / "cutover_contract.json",
    ]
    required_v11_inputs = [
        base_v11_inputs_dir / "reasoning_query_contracts.jsonl",
        base_v11_inputs_dir / "confidence_query_contracts.jsonl",
        base_v11_inputs_dir / "illumination_query_contracts.jsonl",
        base_v11_inputs_dir / "labeled_illumination_query_contracts.jsonl",
    ]
    for path in [*required_bootstrap_inputs, *required_v11_inputs]:
        if not path.is_file():
            raise ValueError(f"Model-axis 1.5B dry-run input not found: `{path}`.")

    materialized_dir = output_dir / "materialized_model_axis_1p5b_dry_run_inputs"
    materialized_dir.mkdir(parents=True, exist_ok=True)
    for src in [*required_bootstrap_inputs, *required_v11_inputs]:
        copy_artifact(src, materialized_dir / src.name)

    dataset_rows = load_jsonl(materialized_dir / "real_experiment_dataset.jsonl")
    model_manifest = load_json(materialized_dir / "model_manifest.json")
    previous_summary_path = output_dir / "model_axis_1p5b_dry_run_summary.json"
    previous_summary = load_json(previous_summary_path) if previous_summary_path.is_file() else None
    route_budgets = {
        "reasoning": count_jsonl_rows(materialized_dir / "reasoning_query_contracts.jsonl"),
        "confidence": count_jsonl_rows(materialized_dir / "confidence_query_contracts.jsonl"),
        "illumination": count_jsonl_rows(materialized_dir / "illumination_query_contracts.jsonl"),
        "labeled_illumination": count_jsonl_rows(materialized_dir / "labeled_illumination_query_contracts.jsonl"),
    }
    model_source = str(model_manifest.get("selected_local_path") or model_manifest["selected_model_id"])
    local_probe = run_local_only_loader_probe(model_source)

    ready_local = bool(model_manifest.get("selected_local_path")) and local_probe["overall_status"] == "PASS"
    ready_run = ready_local
    minimal_cell = str(minimal_candidate["preferred_minimal_cell"])

    cells = [
        {
            "cell_id": "dataset0_model0_route_b_model_axis_probe",
            "route_name": "route_b",
            "cell_role": "minimal_execution_candidate",
            "runtime_status": "BLOCKED_NOT_READY_LOCAL" if not ready_run else "READY",
            "contract_valid": True,
            "expected_output": "model_axis_1p5b_route_b_summary.json",
        },
        {
            "cell_id": "dataset0_model0_route_c_model_axis_probe",
            "route_name": "route_c",
            "cell_role": "core_route_comparison",
            "runtime_status": "BLOCKED_NOT_READY_LOCAL" if not ready_run else "READY",
            "contract_valid": True,
            "expected_output": "model_axis_1p5b_route_c_summary.json",
        },
        {
            "cell_id": "dataset0_model0_fusion_summary_model_axis_probe",
            "route_name": "fusion_summary",
            "cell_role": "baseline_summary_probe",
            "runtime_status": "BLOCKED_NOT_READY_LOCAL" if not ready_run else "READY",
            "contract_valid": True,
            "expected_output": "model_axis_1p5b_fusion_summary.json",
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_candidate_model_axis_probe",
            "route_name": "fusion_cell_candidate",
            "cell_role": "candidate_probe",
            "runtime_status": "BLOCKED_NOT_READY_LOCAL" if not ready_run else "READY",
            "contract_valid": True,
            "expected_output": "model_axis_1p5b_fusion_cell_candidate_summary.json",
        },
        {
            "cell_id": "dataset0_model0_fusion_cell_refined_model_axis_probe",
            "route_name": "fusion_cell_refined",
            "cell_role": "refined_probe",
            "runtime_status": "BLOCKED_NOT_READY_LOCAL" if not ready_run else "READY",
            "contract_valid": True,
            "expected_output": "model_axis_1p5b_fusion_cell_refined_summary.json",
        },
    ]

    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": bootstrap_summary["matrix_name"],
        "dry_run_mode": "model_axis_1p5b_contract_validation_with_local_loader_probe",
        "seed": seed,
        "selected_model_profile": bootstrap_summary["selected_model_profile"],
        "selected_model_id": bootstrap_summary["selected_model_id"],
        "ready_local": ready_local,
        "ready_run": ready_run,
        "fallback_mode": "config_valid_plus_partial_dry_run" if not ready_run else "ready_local_runtime",
        "route_count": len(matrix_definition["routes"]),
        "cell_count": len(cells),
        "minimum_execution_candidate": minimal_cell,
    }
    contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": bootstrap_summary["matrix_name"],
        "selected_model_profile": bootstrap_summary["selected_model_profile"],
        "selected_model_id": bootstrap_summary["selected_model_id"],
        "shared_inputs": {
            "dataset_input": str((materialized_dir / "real_experiment_dataset.jsonl").resolve()),
            "dataset_manifest": str((materialized_dir / "dataset_manifest.json").resolve()),
            "model_manifest": str((materialized_dir / "model_manifest.json").resolve()),
            "cutover_contract": str((materialized_dir / "cutover_contract.json").resolve()),
            "reasoning_query_file": str((materialized_dir / "reasoning_query_contracts.jsonl").resolve()),
            "confidence_query_file": str((materialized_dir / "confidence_query_contracts.jsonl").resolve()),
            "illumination_query_file": str((materialized_dir / "illumination_query_contracts.jsonl").resolve()),
            "labeled_illumination_query_file": str((materialized_dir / "labeled_illumination_query_contracts.jsonl").resolve()),
        },
        "route_role_map": {
            "route_b": "primary minimal execution candidate for the 1.5B route portability check",
            "route_c": "secondary route portability check",
            "fusion_summary": "smallest fusion baseline once route evidence becomes runnable",
            "fusion_cell_candidate": "candidate-style fusion portability probe",
            "fusion_cell_refined": "refined-style fusion portability probe",
        },
        "cells": cells,
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": bootstrap_summary["matrix_name"],
        "selected_model_profile": bootstrap_summary["selected_model_profile"],
        "selected_model_id": bootstrap_summary["selected_model_id"],
        "ready_local": ready_local,
        "ready_run": ready_run,
        "dry_run_path": "partial_contract_validation" if not ready_run else "full_runtime_validation",
        "minimum_execution_candidate": minimal_cell,
        "mandatory_routes": ["route_b", "route_c", "fusion_summary"],
        "optional_routes": ["fusion_cell_candidate", "fusion_cell_refined"],
        "blocking_reasons": [] if ready_run else blocker_diagnosis["why_not_ready_local"],
    }
    write_json(output_dir / "model_axis_1p5b_dry_run_plan.json", plan)
    write_json(output_dir / "model_axis_1p5b_execution_contract.json", contract)
    write_json(output_dir / "model_axis_1p5b_dry_run_readiness_summary.json", readiness)

    module_status = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "dataset_input": {
            "status": "PASS",
            "path": str((materialized_dir / "real_experiment_dataset.jsonl").resolve()),
            "rows": len(dataset_rows),
        },
        "query_contracts": {
            "status": "PASS",
            "budgets": route_budgets,
        },
        "model_profile": {
            "status": "PASS",
            "selected_model_profile": bootstrap_summary["selected_model_profile"],
            "selected_model_id": bootstrap_summary["selected_model_id"],
            "selected_local_path": model_manifest["selected_local_path"],
            "selected_availability_status": model_manifest["selected_availability_status"],
        },
        "local_hf_probe": {
            "status": "PASS" if ready_local else "BLOCKED",
            "probe": local_probe,
        },
        "overall_runtime_gate": {
            "status": "READY" if ready_run else "BLOCKED_NOT_READY_LOCAL",
            "recommended_recovery_path": "A" if ready_run else recovery_options["current_best_path"],
        },
    }
    cell_status = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": bootstrap_summary["matrix_name"],
        "minimum_execution_candidate": minimal_cell,
        "cells": cells,
    }

    preview_rows = [
        {
            "cell_id": cell["cell_id"],
            "route_name": cell["route_name"],
            "runtime_status": cell["runtime_status"],
            "expected_output": cell["expected_output"],
            "contract_valid": cell["contract_valid"],
        }
        for cell in cells
    ]
    registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "matrix_name": bootstrap_summary["matrix_name"],
        "selected_model_profile": bootstrap_summary["selected_model_profile"],
        "artifacts": {
            "plan": str((output_dir / "model_axis_1p5b_dry_run_plan.json").resolve()),
            "execution_contract": str((output_dir / "model_axis_1p5b_execution_contract.json").resolve()),
            "readiness": str((output_dir / "model_axis_1p5b_dry_run_readiness_summary.json").resolve()),
            "summary": str((output_dir / "model_axis_1p5b_dry_run_summary.json").resolve()),
            "cell_status": str((output_dir / "model_axis_1p5b_cell_status.json").resolve()),
            "module_status": str((output_dir / "model_axis_1p5b_module_status.json").resolve()),
        },
    }

    dry_run_status = "PASS" if ready_run else "PARTIAL"
    upgrade_delta = None
    if previous_summary is not None:
        upgrade_delta = {
            "previous_dry_run_status": previous_summary.get("dry_run_status"),
            "current_dry_run_status": dry_run_status,
            "status_changed": previous_summary.get("dry_run_status") != dry_run_status,
            "previous_ready_local": previous_summary.get("ready_local"),
            "current_ready_local": ready_local,
            "previous_ready_run": previous_summary.get("ready_run"),
            "current_ready_run": ready_run,
            "previous_route_b_status": previous_summary.get("route_b_status"),
            "current_route_b_status": cells[0]["runtime_status"],
        }
    summary = {
        "summary_status": dry_run_status,
        "schema_version": SCHEMA_VERSION,
        "matrix_name": bootstrap_summary["matrix_name"],
        "selected_model_profile": bootstrap_summary["selected_model_profile"],
        "selected_model_id": bootstrap_summary["selected_model_id"],
        "ready_local": ready_local,
        "ready_run": ready_run,
        "contract_valid": True,
        "dry_run_status": dry_run_status,
        "dataset_rows": len(dataset_rows),
        "route_count": len(matrix_definition["routes"]),
        "cell_count": len(cells),
        "route_b_status": cells[0]["runtime_status"],
        "route_c_status": cells[1]["runtime_status"],
        "fusion_summary_status": cells[2]["runtime_status"],
        "minimal_execution_candidate": minimal_cell,
        "minimal_execution_candidate_status": cells[0]["runtime_status"],
        "passed_contract_cells": [cell["cell_id"] for cell in cells if cell["contract_valid"]],
        "blocked_runtime_cells": [cell["cell_id"] for cell in cells if cell["runtime_status"] != "READY"],
        "blocker_reasons": [] if ready_run else blocker_diagnosis["why_not_ready_local"],
        "recovery_path": "A" if ready_run else recovery_options["current_best_path"],
        "upgrade_delta": upgrade_delta,
    }
    execution_gate = {
        "summary_status": "PASS",
        "schema_version": "triscopellm/model-axis-1p5b-execution-gate/v1",
        "allow_107_execution": ready_run and cells[0]["runtime_status"] == "READY",
        "selected_model_profile": bootstrap_summary["selected_model_profile"],
        "selected_model_id": bootstrap_summary["selected_model_id"],
        "selected_local_path": model_manifest.get("selected_local_path"),
        "minimum_execution_candidate": minimal_cell,
        "gate_reason": (
            "1.5B model is ready-local and route_b can enter real model inference."
            if ready_run
            else "1.5B model is still not ready-local, so no runtime cell can enter real model inference yet."
        ),
        "required_to_unlock": [] if ready_run else [
            "provide a local Qwen/Qwen2.5-1.5B-Instruct snapshot and wire it into local_path",
            "or expose an equivalent local HF cache snapshot so the model and tokenizer can pass local-only loading",
        ],
        "current_route_b_status": cells[0]["runtime_status"],
        "current_route_c_status": cells[1]["runtime_status"],
        "current_fusion_summary_status": cells[2]["runtime_status"],
    }
    log_lines = [
        f"matrix_name={bootstrap_summary['matrix_name']}",
        f"selected_model_profile={bootstrap_summary['selected_model_profile']}",
        f"selected_model_id={bootstrap_summary['selected_model_id']}",
        f"ready_local={ready_local}",
        f"ready_run={ready_run}",
        f"minimum_execution_candidate={minimal_cell}",
        f"route_b_status={cells[0]['runtime_status']}",
        f"route_c_status={cells[1]['runtime_status']}",
        f"fusion_summary_status={cells[2]['runtime_status']}",
        f"config_probe_status={local_probe['config_probe']['status']}",
        f"tokenizer_probe_status={local_probe['tokenizer_probe']['status']}",
        f"model_probe_status={local_probe['model_probe']['status']}",
    ]

    write_json(output_dir / "model_axis_1p5b_module_status.json", module_status)
    write_json(output_dir / "model_axis_1p5b_cell_status.json", cell_status)
    write_json(output_dir / "model_axis_1p5b_dry_run_registry.json", registry)
    write_json(output_dir / "model_axis_1p5b_dry_run_summary.json", summary)
    write_json(output_dir / "model_axis_1p5b_execution_gate.json", execution_gate)
    write_jsonl(output_dir / "model_axis_1p5b_preview.jsonl", preview_rows)
    (output_dir / "model_axis_1p5b_dry_run.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return {
        "summary": summary,
        "output_paths": {
            "plan": str((output_dir / "model_axis_1p5b_dry_run_plan.json").resolve()),
            "contract": str((output_dir / "model_axis_1p5b_execution_contract.json").resolve()),
            "readiness": str((output_dir / "model_axis_1p5b_dry_run_readiness_summary.json").resolve()),
            "summary": str((output_dir / "model_axis_1p5b_dry_run_summary.json").resolve()),
        },
    }
