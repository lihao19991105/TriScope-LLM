"""Bootstrap route_c portability on model-axis 1.5B with a lightweight precheck run."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.eval.experiment_bootstrap import evaluate_model_profile, load_yaml
from src.eval.model_axis_1p5b_dry_run import run_local_only_loader_probe
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-portability/v1"


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


def base_sample_id_from_contract(sample_id: str) -> str:
    if "__" in sample_id:
        return sample_id.split("__", 1)[0]
    return sample_id


def choose_portability_base_ids(
    reasoning_rows: list[dict[str, Any]],
    reference_route_c_rows: list[dict[str, Any]],
    precheck_budget: int,
) -> tuple[list[str], dict[str, Any]]:
    reasoning_base_ids = [str(row["sample_id"]) for row in reasoning_rows]
    reasoning_base_set = set(reasoning_base_ids)

    # Fallback to deterministic prefix if no reference route_c dataset is available.
    if not reference_route_c_rows:
        selected = reasoning_base_ids[: max(1, precheck_budget)]
        return selected, {
            "strategy": "reasoning_prefix_fallback_no_reference_route_c",
            "selected_base_count": len(selected),
            "selected_dual_class_base_count": 0,
            "expected_reference_contract_class_balance": None,
        }

    base_to_labels: dict[str, set[int]] = {}
    for row in reference_route_c_rows:
        sample_id = str(row.get("sample_id", ""))
        base_id = base_sample_id_from_contract(sample_id)
        if base_id not in reasoning_base_set:
            continue
        base_to_labels.setdefault(base_id, set()).add(int(row.get("ground_truth_label", 0)))

    dual_class_bases = [base_id for base_id, labels in base_to_labels.items() if len(labels) >= 2]
    selected: list[str] = []
    if dual_class_bases:
        # Deterministic first dual-class base ensures both classes can appear under small budgets.
        selected.append(sorted(dual_class_bases)[0])

    for base_id in reasoning_base_ids:
        if len(selected) >= max(1, precheck_budget):
            break
        if base_id in selected:
            continue
        selected.append(base_id)

    selected_set = set(selected)
    selected_contract_rows = [
        row
        for row in reference_route_c_rows
        if base_sample_id_from_contract(str(row.get("sample_id", ""))) in selected_set
    ]
    expected_balance = {
        "label_0": sum(1 for row in selected_contract_rows if int(row.get("ground_truth_label", 0)) == 0),
        "label_1": sum(1 for row in selected_contract_rows if int(row.get("ground_truth_label", 0)) == 1),
    }
    return selected, {
        "strategy": "prefer_dual_class_base_then_fill_reasoning_order",
        "selected_base_count": len(selected),
        "selected_dual_class_base_count": sum(1 for base_id in selected if base_id in dual_class_bases),
        "expected_reference_contract_class_balance": expected_balance,
    }


def classify_failure_stage(error_message: str) -> str:
    lowered = error_message.lower()
    if "input not found" in lowered or "query contracts" in lowered:
        return "sampling"
    if "at least two classes" in lowered or "label" in lowered:
        return "labels"
    if "available_local" in lowered or "inference" in lowered or "from_pretrained" in lowered:
        return "inference"
    return "unknown"


def build_model_axis_1p5b_route_c_portability(
    route_b_stability_summary_path: Path,
    reference_route_c_dataset_path: Path,
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
    precheck_budget: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    stability_summary = load_json(route_b_stability_summary_path)
    if stability_summary.get("stability_established") is not True:
        raise ValueError("113 requires 112 stability_established=true before route_c portability bootstrap.")

    required_inputs = {
        "reasoning_query_contracts": dry_run_materialized_inputs_dir / "reasoning_query_contracts.jsonl",
        "confidence_query_contracts": dry_run_materialized_inputs_dir / "confidence_query_contracts.jsonl",
        "illumination_query_contracts": dry_run_materialized_inputs_dir / "illumination_query_contracts.jsonl",
        "labeled_illumination_query_contracts": dry_run_materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl",
        "dataset_manifest": bootstrap_materialized_inputs_dir / "dataset_manifest.json",
        "model_manifest": bootstrap_materialized_inputs_dir / "model_manifest.json",
        "cutover_contract": bootstrap_materialized_inputs_dir / "cutover_contract.json",
    }
    missing_inputs = [name for name, path in required_inputs.items() if not path.is_file()]

    model_config = load_yaml(models_config_path)
    selected_profile = evaluate_model_profile("pilot_small_hf", model_config["pilot_small_hf"])
    local_probe = run_local_only_loader_probe(str(selected_profile.get("local_path") or selected_profile["model_id"]))
    model_ready_local = selected_profile.get("availability_status") == "available_local" and local_probe["overall_status"] == "PASS"

    reasoning_rows = load_jsonl(required_inputs["reasoning_query_contracts"])
    confidence_rows = load_jsonl(required_inputs["confidence_query_contracts"])
    illumination_rows = load_jsonl(required_inputs["illumination_query_contracts"])
    labeled_rows = load_jsonl(required_inputs["labeled_illumination_query_contracts"])

    reference_route_c_rows = load_jsonl(reference_route_c_dataset_path) if reference_route_c_dataset_path.is_file() else []
    selected_base_ids, selection_diagnostics = choose_portability_base_ids(
        reasoning_rows=reasoning_rows,
        reference_route_c_rows=reference_route_c_rows,
        precheck_budget=precheck_budget,
    )
    selected_base_id_set = set(selected_base_ids)

    selected_reasoning = [row for row in reasoning_rows if str(row.get("sample_id")) in selected_base_id_set]
    selected_confidence = [row for row in confidence_rows if str(row.get("sample_id")) in selected_base_id_set]
    selected_illumination = [row for row in illumination_rows if str(row.get("sample_id")) in selected_base_id_set]
    selected_labeled = [
        row
        for row in labeled_rows
        if str(row.get("metadata", {}).get("base_sample_id", "")) in selected_base_id_set
    ]

    portability_inputs_dir = output_dir / "materialized_route_c_portability_inputs"
    portability_inputs_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(portability_inputs_dir / "reasoning_query_contracts.jsonl", selected_reasoning)
    write_jsonl(portability_inputs_dir / "confidence_query_contracts.jsonl", selected_confidence)
    write_jsonl(portability_inputs_dir / "illumination_query_contracts.jsonl", selected_illumination)
    write_jsonl(portability_inputs_dir / "labeled_illumination_query_contracts.jsonl", selected_labeled)
    for name in ["dataset_manifest", "model_manifest", "cutover_contract"]:
        copy_artifact(required_inputs[name], portability_inputs_dir / required_inputs[name].name)

    contract = {
        "summary_status": "PASS" if not missing_inputs else "BLOCKED",
        "schema_version": SCHEMA_VERSION,
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "selected_local_path": selected_profile.get("local_path"),
        "route_b_vs_route_c_differences": {
            "route_b_label": "task_correctness_violation_label (sample-level)",
            "route_c_label": "task_answer_incorrect_label (contract-level benchmark-truth-leaning)",
            "route_b_inputs": [
                "reasoning_query_contracts",
                "confidence_query_contracts",
                "illumination_query_contracts",
                "pilot_slice",
            ],
            "route_c_inputs": [
                "reasoning_query_contracts",
                "confidence_query_contracts",
                "illumination_query_contracts",
                "labeled_illumination_query_contracts",
            ],
            "route_b_risk_focus": "single-class label collapse in sample-level more-natural labels",
            "route_c_risk_focus": "contract-level labeled illumination alignment and portability on 1.5B profile",
        },
        "required_inputs": {name: str(path.resolve()) for name, path in required_inputs.items()},
        "missing_inputs": missing_inputs,
        "portability_goal": "bootstrap 1.5B route_c contract and readiness without full-scale route_c expansion",
    }

    selection = {
        "summary_status": "PASS" if not missing_inputs else "BLOCKED",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "selected_local_path": selected_profile.get("local_path"),
        "selected_base_sample_count": len(selected_base_ids),
        "selected_labeled_contract_count": len(selected_labeled),
        "selection_diagnostics": selection_diagnostics,
        "why_selected": [
            "112 confirmed stabilized route_b is reproducibly analyzable and can act as baseline.",
            "route_c is the next recommended portability target from 111 without switching model axis.",
            "A lightweight precheck subset avoids immediate full route_c expansion cost.",
        ],
    }

    ready_dry_run = not missing_inputs and model_ready_local and len(selected_labeled) > 0
    ready_run = ready_dry_run and len(selected_reasoning) > 0 and len(selected_labeled) >= len(selected_reasoning)
    readiness = {
        "summary_status": "PASS" if ready_dry_run else "BLOCKED",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "selected_model_profile": "pilot_small_hf",
        "contract_compatible": not missing_inputs,
        "model_ready_local": model_ready_local,
        "ready_dry_run": ready_dry_run,
        "ready_run": ready_run,
        "selected_base_sample_count": len(selected_reasoning),
        "selected_labeled_contract_count": len(selected_labeled),
        "selection_diagnostics": selection_diagnostics,
        "materialized_inputs_dir": str(portability_inputs_dir.resolve()),
        "blocking_reasons": (
            []
            if ready_dry_run
            else [
                *( [f"missing_inputs={','.join(missing_inputs)}"] if missing_inputs else [] ),
                *( ["pilot_small_hf_not_ready_local"] if not model_ready_local else [] ),
                *( ["no_labeled_contract_rows_for_selected_subset"] if len(selected_labeled) == 0 else [] ),
            ]
        ),
    }

    write_json(output_dir / "route_c_portability_contract.json", contract)
    write_json(output_dir / "route_c_portability_selection.json", selection)
    write_json(output_dir / "route_c_portability_readiness_summary.json", readiness)

    run_summary_status = "BLOCKED"
    run_execution_status = "BLOCKED"
    failure_reason = None
    failure_stage = None
    route_c_summary: dict[str, Any] | None = None
    route_c_logistic_summary: dict[str, Any] | None = None

    if ready_dry_run:
        precheck_run_dir = output_dir / "route_c_portability_precheck_run"
        try:
            run_result = run_route_c_v6(
                models_config_path=models_config_path,
                reasoning_config_path=reasoning_config_path,
                confidence_config_path=confidence_config_path,
                illumination_config_path=illumination_config_path,
                reasoning_prompt_dir=reasoning_prompt_dir,
                confidence_prompt_dir=confidence_prompt_dir,
                illumination_prompt_dir=illumination_prompt_dir,
                v6_inputs_dir=portability_inputs_dir,
                output_dir=precheck_run_dir,
                seed=seed,
                label_threshold=label_threshold,
                model_profile_name="pilot_small_hf",
            )
            route_c_summary = load_json(Path(run_result["output_paths"]["summary"]))
            route_c_logistic_summary = load_json(Path(run_result["output_paths"]["logistic_summary"]))
            run_summary_status = "PASS"
            run_execution_status = "DRY_RUN_EXECUTABLE"
        except Exception as exc:
            failure_reason = str(exc)
            failure_stage = classify_failure_stage(failure_reason)
            run_summary_status = "PARTIAL"
            run_execution_status = "PRECHECK_FAILED"

    module_status = {
        "summary_status": "PASS" if run_summary_status == "PASS" else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "inputs": {
            "missing_inputs": missing_inputs,
            "reasoning_rows": len(selected_reasoning),
            "confidence_rows": len(selected_confidence),
            "illumination_rows": len(selected_illumination),
            "labeled_rows": len(selected_labeled),
        },
        "model_profile": {
            "selected_model_profile": "pilot_small_hf",
            "selected_model_id": selected_profile["model_id"],
            "selected_local_path": selected_profile.get("local_path"),
            "availability_status": selected_profile.get("availability_status"),
            "local_probe_overall_status": local_probe["overall_status"],
        },
        "execution_gate": {
            "contract_compatible": not missing_inputs,
            "ready_dry_run": ready_dry_run,
            "ready_run": ready_run,
            "run_summary_status": run_summary_status,
            "failure_stage": failure_stage,
            "failure_reason": failure_reason,
        },
    }

    cell_status = {
        "summary_status": "PASS" if ready_dry_run else "BLOCKED",
        "schema_version": SCHEMA_VERSION,
        "cells": [
            {
                "cell_id": "dataset0_model0_route_c_portability_precheck",
                "route_name": "route_c",
                "runtime_status": run_execution_status,
                "contract_compatible": not missing_inputs,
                "ready_dry_run": ready_dry_run,
                "ready_run": ready_run,
                "selected_model_profile": "pilot_small_hf",
            }
        ],
    }

    run_summary = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "contract_compatible": not missing_inputs,
        "ready_dry_run": ready_dry_run,
        "ready_run": ready_run,
        "execution_status": run_execution_status,
        "used_local_weights": True if run_summary_status == "PASS" else None,
        "entered_model_inference": True if run_summary_status == "PASS" else None,
        "route_c_summary": route_c_summary,
        "route_c_logistic_summary": route_c_logistic_summary,
        "failure_stage": failure_stage,
        "failure_reason": failure_reason,
        "notes": [
            "This is a route_c portability precheck/bootstrap on 1.5B, not a full route_c expansion run.",
            "The precheck subset reuses existing contracts and avoids new dataset/proxy expansion.",
        ],
    }

    write_json(output_dir / "route_c_portability_module_status.json", module_status)
    write_json(output_dir / "route_c_portability_cell_status.json", cell_status)
    write_json(output_dir / "route_c_portability_run_summary.json", run_summary)
    write_json(
        output_dir / "route_c_portability_registry.json",
        {
            "summary_status": "PASS" if run_summary_status == "PASS" else "PARTIAL",
            "schema_version": SCHEMA_VERSION,
            "artifacts": {
                "contract": str((output_dir / "route_c_portability_contract.json").resolve()),
                "selection": str((output_dir / "route_c_portability_selection.json").resolve()),
                "readiness": str((output_dir / "route_c_portability_readiness_summary.json").resolve()),
                "run_summary": str((output_dir / "route_c_portability_run_summary.json").resolve()),
                "module_status": str((output_dir / "route_c_portability_module_status.json").resolve()),
                "cell_status": str((output_dir / "route_c_portability_cell_status.json").resolve()),
                "materialized_inputs": str(portability_inputs_dir.resolve()),
            },
        },
    )

    return {
        "run_summary": run_summary,
        "output_paths": {
            "contract": str((output_dir / "route_c_portability_contract.json").resolve()),
            "selection": str((output_dir / "route_c_portability_selection.json").resolve()),
            "readiness": str((output_dir / "route_c_portability_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "route_c_portability_run_summary.json").resolve()),
            "module_status": str((output_dir / "route_c_portability_module_status.json").resolve()),
            "cell_status": str((output_dir / "route_c_portability_cell_status.json").resolve()),
        },
    }
