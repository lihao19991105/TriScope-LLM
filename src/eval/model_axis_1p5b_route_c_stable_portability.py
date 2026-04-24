"""Rerun route_c portability precheck with stabilized label balance on model-axis 1.5B."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_portability import classify_failure_stage
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-stable-portability/v1"


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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def copy_artifact(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def materialize_selected_rows(
    dry_run_materialized_inputs_dir: Path,
    bootstrap_materialized_inputs_dir: Path,
    selected_base_ids: list[str],
    output_dir: Path,
) -> dict[str, Any]:
    selected_base_id_set = set(selected_base_ids)
    output_dir.mkdir(parents=True, exist_ok=True)

    reasoning_rows = [
        row
        for row in load_jsonl(dry_run_materialized_inputs_dir / "reasoning_query_contracts.jsonl")
        if str(row.get("sample_id", "")) in selected_base_id_set
    ]
    confidence_rows = [
        row
        for row in load_jsonl(dry_run_materialized_inputs_dir / "confidence_query_contracts.jsonl")
        if str(row.get("sample_id", "")) in selected_base_id_set
    ]
    illumination_rows = [
        row
        for row in load_jsonl(dry_run_materialized_inputs_dir / "illumination_query_contracts.jsonl")
        if str(row.get("sample_id", "")) in selected_base_id_set
    ]
    labeled_rows = [
        row
        for row in load_jsonl(dry_run_materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl")
        if str(row.get("metadata", {}).get("base_sample_id") or row.get("metadata", {}).get("contract_metadata", {}).get("base_sample_id", "")) in selected_base_id_set
    ]

    write_jsonl(output_dir / "reasoning_query_contracts.jsonl", reasoning_rows)
    write_jsonl(output_dir / "confidence_query_contracts.jsonl", confidence_rows)
    write_jsonl(output_dir / "illumination_query_contracts.jsonl", illumination_rows)
    write_jsonl(output_dir / "labeled_illumination_query_contracts.jsonl", labeled_rows)
    for name in ["dataset_manifest.json", "model_manifest.json", "cutover_contract.json"]:
        copy_artifact(bootstrap_materialized_inputs_dir / name, output_dir / name)

    materialization_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_base_ids": selected_base_ids,
        "selected_base_count": len(selected_base_ids),
        "reasoning_rows": len(reasoning_rows),
        "confidence_rows": len(confidence_rows),
        "illumination_rows": len(illumination_rows),
        "labeled_rows": len(labeled_rows),
    }
    write_json(output_dir / "materialization_summary.json", materialization_summary)
    return materialization_summary


def build_model_axis_1p5b_route_c_stable_portability(
    route_c_stabilization_dir: Path,
    dry_run_materialized_inputs_dir: Path,
    bootstrap_materialized_inputs_dir: Path,
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

    precheck = load_json(route_c_stabilization_dir / "route_c_label_balance_precheck.json")
    candidate_summary = load_json(route_c_stabilization_dir / "route_c_balanced_candidate_summary.json")
    if precheck.get("ready_for_stable_portability_rerun") is not True:
        raise ValueError("115 requires 114 to produce a bi-class candidate subset before rerunning route_c portability.")

    selected_base_ids = [str(item) for item in precheck.get("selected_base_ids", [])]
    materialized_inputs_dir = output_dir / "materialized_route_c_stable_portability_inputs"
    materialization_summary = materialize_selected_rows(
        dry_run_materialized_inputs_dir=dry_run_materialized_inputs_dir,
        bootstrap_materialized_inputs_dir=bootstrap_materialized_inputs_dir,
        selected_base_ids=selected_base_ids,
        output_dir=materialized_inputs_dir,
    )

    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "selected_model_profile": "pilot_small_hf",
        "selected_base_ids": selected_base_ids,
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": int(candidate_summary.get("selected_contract_count", 0)),
        "selected_class_balance": candidate_summary.get("class_balance"),
        "change_vs_113": {
            "label_parse_mode": "strict -> robust_prefix",
            "selection_source": "114 balanced candidate subset derived from full 1.5B labeled scan",
            "old_selected_base_ids_replaced": True,
        },
        "why_selected": [
            "114 identified this subset as the smallest real 1.5B route_c candidate that restores two classes.",
            "The route_c portability contract remains unchanged; only label parsing and subset selection are stabilized.",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "stabilization_source": str((route_c_stabilization_dir / "route_c_label_balance_precheck.json").resolve()),
        "execution_goal": "rerun route_c portability precheck until the old PRECHECK_FAILED label-collapse is removed",
        "success_criterion": [
            "class_balance remains bi-class under robust_prefix parsing",
            "route_c portability precheck becomes PASS or PASS_WITH_LIMITATIONS",
            "ready_run remains true after the rerun",
        ],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "ready_dry_run": True,
        "ready_run": True,
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": int(candidate_summary.get("selected_contract_count", 0)),
        "class_balance": candidate_summary.get("class_balance"),
        "label_parse_mode": "robust_prefix",
        "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
    }
    write_json(output_dir / "route_c_stable_portability_selection.json", selection)
    write_json(output_dir / "route_c_stable_portability_plan.json", plan)
    write_json(output_dir / "route_c_stable_portability_readiness_summary.json", readiness)

    run_summary_status = "BLOCKED"
    execution_status = "BLOCKED"
    route_c_summary: dict[str, Any] | None = None
    route_c_logistic_summary: dict[str, Any] | None = None
    failure_reason = None
    failure_stage = None

    try:
        run_result = run_route_c_v6(
            models_config_path=models_config_path,
            reasoning_config_path=reasoning_config_path,
            confidence_config_path=confidence_config_path,
            illumination_config_path=illumination_config_path,
            reasoning_prompt_dir=reasoning_prompt_dir,
            confidence_prompt_dir=confidence_prompt_dir,
            illumination_prompt_dir=illumination_prompt_dir,
            v6_inputs_dir=materialized_inputs_dir,
            output_dir=output_dir / "route_c_stable_portability_precheck_run",
            seed=seed,
            label_threshold=label_threshold,
            model_profile_name="pilot_small_hf",
            label_parse_mode="robust_prefix",
        )
        route_c_summary = load_json(Path(run_result["output_paths"]["summary"]))
        route_c_logistic_summary = load_json(Path(run_result["output_paths"]["logistic_summary"]))
        positive_count = int(route_c_summary.get("class_balance", {}).get("label_1", 0))
        run_summary_status = "PASS"
        execution_status = "PASS_WITH_LIMITATIONS" if positive_count <= 1 else "PASS"
    except Exception as exc:
        failure_reason = str(exc)
        failure_stage = classify_failure_stage(failure_reason)
        run_summary_status = "PARTIAL"
        execution_status = "PRECHECK_FAILED"

    module_status = {
        "summary_status": "PASS" if run_summary_status == "PASS" else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "selection": selection,
        "materialization_summary": materialization_summary,
        "execution_gate": {
            "ready_dry_run": True,
            "ready_run": run_summary_status == "PASS",
            "run_summary_status": run_summary_status,
            "execution_status": execution_status,
            "failure_stage": failure_stage,
            "failure_reason": failure_reason,
        },
    }
    cell_status = {
        "summary_status": "PASS" if run_summary_status == "PASS" else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "cells": [
            {
                "cell_id": "dataset0_model0_route_c_stable_portability_precheck",
                "route_name": "route_c",
                "runtime_status": execution_status,
                "selected_model_profile": "pilot_small_hf",
                "ready_run": run_summary_status == "PASS",
            }
        ],
    }
    run_summary = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "execution_status": execution_status,
        "used_local_weights": True if run_summary_status == "PASS" else None,
        "entered_model_inference": True if run_summary_status == "PASS" else None,
        "label_parse_mode": "robust_prefix",
        "route_c_summary": route_c_summary,
        "route_c_logistic_summary": route_c_logistic_summary,
        "failure_stage": failure_stage,
        "failure_reason": failure_reason,
        "notes": [
            "This rerun keeps route_c on the 1.5B axis and only stabilizes the portability precheck semantics.",
            "PASS_WITH_LIMITATIONS means the precheck passed but the positive class remains extremely sparse.",
        ],
    }
    write_json(output_dir / "route_c_stable_portability_module_status.json", module_status)
    write_json(output_dir / "route_c_stable_portability_cell_status.json", cell_status)
    write_json(output_dir / "route_c_stable_portability_run_summary.json", run_summary)

    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "route_c_stable_portability_selection.json").resolve()),
            "plan": str((output_dir / "route_c_stable_portability_plan.json").resolve()),
            "readiness": str((output_dir / "route_c_stable_portability_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "route_c_stable_portability_run_summary.json").resolve()),
            "module_status": str((output_dir / "route_c_stable_portability_module_status.json").resolve()),
            "cell_status": str((output_dir / "route_c_stable_portability_cell_status.json").resolve()),
        },
    }
