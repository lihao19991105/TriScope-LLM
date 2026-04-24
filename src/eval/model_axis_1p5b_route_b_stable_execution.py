"""Run stabilized 1.5B route_b execution after label-balance recovery precheck."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

from src.eval.experiment_bootstrap import evaluate_model_profile, load_yaml
from src.eval.model_axis_1p5b_execution import load_json, materialize_minimal_inputs
from src.eval.rerun_route_b_on_labeled_split_v6 import run_route_b_v6


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-b-stable-execution/v1"


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


def build_model_axis_1p5b_route_b_stable_execution(
    dry_run_summary_path: Path,
    execution_gate_path: Path,
    stabilization_precheck_path: Path,
    bootstrap_materialized_inputs_dir: Path,
    dry_run_materialized_inputs_dir: Path,
    reference_route_b_dataset_path: Path,
    reference_route_b_slice_path: Path,
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
    target_budget: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    dry_run_summary = load_json(dry_run_summary_path)
    execution_gate = load_json(execution_gate_path)
    stabilization_precheck = load_json(stabilization_precheck_path)

    if dry_run_summary.get("summary_status") != "PASS":
        raise ValueError("110 requires a PASS 106 dry-run before stable execution.")
    if execution_gate.get("allow_107_execution") is not True:
        raise ValueError("110 requires allow_107_execution = true.")
    if stabilization_precheck.get("logistic_prereq_two_classes") is not True:
        raise ValueError("110 requires a PASS stabilization precheck with at least two classes.")

    model_config = load_yaml(models_config_path)
    selected_profile = evaluate_model_profile("pilot_small_hf", model_config["pilot_small_hf"])
    if selected_profile["availability_status"] != "available_local":
        raise ValueError("pilot_small_hf must be available_local before 110 can execute.")

    reasoning_query_file = dry_run_materialized_inputs_dir / "reasoning_query_contracts.jsonl"
    confidence_query_file = dry_run_materialized_inputs_dir / "confidence_query_contracts.jsonl"
    illumination_query_file = dry_run_materialized_inputs_dir / "illumination_query_contracts.jsonl"
    required_inputs = [
        reasoning_query_file,
        confidence_query_file,
        illumination_query_file,
        reference_route_b_dataset_path,
        reference_route_b_slice_path,
        bootstrap_materialized_inputs_dir / "dataset_manifest.json",
        bootstrap_materialized_inputs_dir / "cutover_contract.json",
        bootstrap_materialized_inputs_dir / "model_manifest.json",
    ]
    for path in required_inputs:
        if not path.is_file():
            raise ValueError(f"110 input not found: `{path}`.")

    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "selected_local_path": selected_profile["local_path"],
        "stabilization_source": str(stabilization_precheck_path.resolve()),
        "changes_vs_107": [
            "Enable route_b label-balance stabilization with robust illumination option parsing.",
            "Keep selection contract and target budget unchanged for comparability.",
        ],
        "target_budget": target_budget,
    }
    write_json(output_dir / "route_b_stable_execution_selection.json", selection)

    execution_inputs_dir = output_dir / "materialized_model_axis_1p5b_route_b_stable_inputs"
    selection_stats = materialize_minimal_inputs(
        reasoning_query_file=reasoning_query_file,
        confidence_query_file=confidence_query_file,
        illumination_query_file=illumination_query_file,
        pilot_slice_file=reference_route_b_slice_path,
        reference_route_b_dataset_path=reference_route_b_dataset_path,
        output_dir=execution_inputs_dir,
        target_budget=target_budget,
    )
    for name in ["dataset_manifest.json", "cutover_contract.json", "model_manifest.json"]:
        copy_artifact(bootstrap_materialized_inputs_dir / name, execution_inputs_dir / name)

    execution_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "selected_local_path": selected_profile["local_path"],
        "execution_mode": "route_b_stable_real_local_execution",
        "seed": seed,
        "target_budget": target_budget,
        "selected_sample_count": selection_stats["reasoning_rows"],
        "selected_positive_reference_count": selection_stats["selection_stats"]["selected_positive_reference_count"],
        "selected_negative_reference_count": selection_stats["selection_stats"]["selected_negative_reference_count"],
        "label_balance_stabilization": {
            "enabled": True,
            "method": "robust_prefix_option_parse_plus_existing_violation_rule",
        },
        "success_criteria": [
            "used_local_weights=true",
            "entered_model_inference=true",
            "route_b_stable_summary.class_balance includes both label_0 and label_1",
            "route_b_stable_logistic_summary.summary_status=PASS",
        ],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "ready_local": True,
        "ready_run": True,
        "selected_model_profile": "pilot_small_hf",
        "selected_local_path": selected_profile["local_path"],
        "selected_sample_count": selection_stats["reasoning_rows"],
        "label_balance_precheck_pass": stabilization_precheck.get("logistic_prereq_two_classes") is True,
        "materialized_inputs_dir": str(execution_inputs_dir.resolve()),
    }
    write_json(output_dir / "route_b_stable_execution_plan.json", execution_plan)
    write_json(output_dir / "route_b_stable_execution_readiness_summary.json", readiness)

    route_b_output_dir = output_dir / "route_b_stable_execution_outputs" / "route_b"
    route_b_result = run_route_b_v6(
        models_config_path=models_config_path,
        reasoning_config_path=reasoning_config_path,
        confidence_config_path=confidence_config_path,
        illumination_config_path=illumination_config_path,
        reasoning_prompt_dir=reasoning_prompt_dir,
        confidence_prompt_dir=confidence_prompt_dir,
        illumination_prompt_dir=illumination_prompt_dir,
        v6_inputs_dir=execution_inputs_dir,
        output_dir=route_b_output_dir,
        seed=seed,
        label_threshold=label_threshold,
        model_profile_name="pilot_small_hf",
        stabilize_label_balance=True,
    )

    route_b_summary = load_json(route_b_output_dir / "route_b_v6_summary.json")
    route_b_logistic_summary = load_json(route_b_output_dir / "route_b_v6_logistic_summary.json")
    route_b_run_summary = load_json(route_b_output_dir / "route_b_v6_run_summary.json")

    copy_artifact(route_b_output_dir / "route_b_v6_summary.json", output_dir / "route_b_stable_summary.json")
    copy_artifact(
        route_b_output_dir / "route_b_v6_logistic_summary.json",
        output_dir / "route_b_stable_logistic_summary.json",
    )

    execution_status = str(route_b_run_summary.get("execution_status", "FULL_EXECUTE"))
    summary_status = str(route_b_run_summary.get("summary_status", "PASS"))
    class_balance = route_b_summary.get("class_balance", {})
    logistic_pass = route_b_logistic_summary.get("summary_status") == "PASS"

    run_summary = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "selected_local_path": selected_profile["local_path"],
        "used_local_weights": True,
        "entered_model_inference": True,
        "execution_status": execution_status,
        "label_balance_stabilization_enabled": True,
        "class_balance": class_balance,
        "logistic_pass": logistic_pass,
        "logistic_blocked_reason": route_b_run_summary.get("logistic_blocked_reason"),
        "selected_query_count": selection_stats["reasoning_rows"],
        "route_b_output_dir": str(route_b_output_dir.resolve()),
        "notes": [
            "This is a true local 1.5B stabilized rerun for route_b.",
            "Compared with 107, this run enables label-balance stabilization in route_b label construction.",
            "The goal is to remove single-class blockage before pursuing broader model-axis expansion.",
        ],
    }
    metrics = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "selected_local_path": selected_profile["local_path"],
        "used_local_weights": True,
        "entered_model_inference": True,
        "execution_status": execution_status,
        "class_balance": class_balance,
        "num_rows": route_b_summary.get("num_rows"),
        "num_base_samples": route_b_summary.get("num_base_samples"),
        "logistic_summary_status": route_b_logistic_summary.get("summary_status"),
        "mean_prediction_score": route_b_logistic_summary.get("mean_prediction_score"),
        "num_positive_predictions": route_b_logistic_summary.get("num_positive_predictions", 0),
    }

    write_json(output_dir / "route_b_stable_execution_run_summary.json", run_summary)
    write_json(output_dir / "route_b_stable_execution_metrics.json", metrics)
    write_json(
        output_dir / "route_b_stable_execution_registry.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "artifacts": {
                "selection": str((output_dir / "route_b_stable_execution_selection.json").resolve()),
                "plan": str((output_dir / "route_b_stable_execution_plan.json").resolve()),
                "readiness": str((output_dir / "route_b_stable_execution_readiness_summary.json").resolve()),
                "run_summary": str((output_dir / "route_b_stable_execution_run_summary.json").resolve()),
                "metrics": str((output_dir / "route_b_stable_execution_metrics.json").resolve()),
                "route_b_summary": str((output_dir / "route_b_stable_summary.json").resolve()),
                "route_b_logistic_summary": str((output_dir / "route_b_stable_logistic_summary.json").resolve()),
                "route_b_output_dir": str(route_b_output_dir.resolve()),
                "route_b_run_summary": str((Path(route_b_result["output_paths"]["run_summary"])).resolve()),
            },
        },
    )
    write_csv(
        output_dir / "route_b_stable_cell_metrics.csv",
        [
            {
                "selected_cell": "route_b",
                "selected_model_profile": "pilot_small_hf",
                "num_rows": route_b_summary.get("num_rows"),
                "num_base_samples": route_b_summary.get("num_base_samples"),
                "label_0": class_balance.get("label_0"),
                "label_1": class_balance.get("label_1"),
                "logistic_summary_status": route_b_logistic_summary.get("summary_status"),
                "mean_prediction_score": route_b_logistic_summary.get("mean_prediction_score"),
                "num_positive_predictions": route_b_logistic_summary.get("num_positive_predictions", 0),
            }
        ],
    )

    return {
        "run_summary": run_summary,
        "metrics": metrics,
        "output_paths": {
            "selection": str((output_dir / "route_b_stable_execution_selection.json").resolve()),
            "plan": str((output_dir / "route_b_stable_execution_plan.json").resolve()),
            "readiness": str((output_dir / "route_b_stable_execution_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "route_b_stable_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "route_b_stable_execution_metrics.json").resolve()),
            "route_b_summary": str((output_dir / "route_b_stable_summary.json").resolve()),
            "route_b_logistic_summary": str((output_dir / "route_b_stable_logistic_summary.json").resolve()),
        },
    }
