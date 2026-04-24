"""Run the first minimal route_c execution on model-axis 1.5B."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_portability import classify_failure_stage
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-execution/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def copy_artifact(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def build_model_axis_1p5b_route_c_execution(
    route_c_stable_portability_dir: Path,
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

    stable_run_summary = load_json(route_c_stable_portability_dir / "route_c_stable_portability_run_summary.json")
    stable_selection = load_json(route_c_stable_portability_dir / "route_c_stable_portability_selection.json")
    stable_readiness = load_json(route_c_stable_portability_dir / "route_c_stable_portability_readiness_summary.json")
    if stable_run_summary.get("summary_status") != "PASS":
        raise ValueError("116 requires 115 to pass before route_c minimal execution can start.")

    materialized_inputs_dir = route_c_stable_portability_dir / "materialized_route_c_stable_portability_inputs"
    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "selected_model_profile": "pilot_small_hf",
        "selected_base_ids": stable_selection.get("selected_base_ids"),
        "selected_class_balance": stable_selection.get("selected_class_balance"),
        "minimal_execution_candidate": "route_c",
        "why_selected": [
            "115 already proved this subset can pass the stabilized route_c portability gate.",
            "Reusing the same subset isolates the step from selection drift and turns portability into minimal execution.",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "execution_goal": "prove that route_c can run as a real 1.5B execution cell with local weights and model inference",
        "success_criterion": [
            "used_local_weights=true",
            "entered_model_inference=true",
            "route_c logistic path completes on the stabilized subset",
        ],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "ready_run": stable_readiness.get("ready_run"),
        "selected_base_ids": stable_selection.get("selected_base_ids"),
        "selected_class_balance": stable_selection.get("selected_class_balance"),
        "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        "label_parse_mode": "robust_prefix",
    }
    write_json(output_dir / "route_c_execution_selection.json", selection)
    write_json(output_dir / "route_c_execution_plan.json", plan)
    write_json(output_dir / "route_c_execution_readiness_summary.json", readiness)

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
            output_dir=output_dir / "route_c_execution_run",
            seed=seed,
            label_threshold=label_threshold,
            model_profile_name="pilot_small_hf",
            label_parse_mode="robust_prefix",
        )
        route_c_summary = load_json(Path(run_result["output_paths"]["summary"]))
        route_c_logistic_summary = load_json(Path(run_result["output_paths"]["logistic_summary"]))
        run_summary_status = "PASS"
        execution_status = "FULL_EXECUTE"
    except Exception as exc:
        failure_reason = str(exc)
        failure_stage = classify_failure_stage(failure_reason)
        run_summary_status = "PARTIAL"
        execution_status = "PARTIAL"

    run_summary = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "used_local_weights": True if run_summary_status == "PASS" else None,
        "entered_model_inference": True if run_summary_status == "PASS" else None,
        "class_balance": None if route_c_summary is None else route_c_summary.get("class_balance"),
        "execution_status": execution_status,
        "failure_stage": failure_stage,
        "failure_reason": failure_reason,
        "label_parse_mode": "robust_prefix",
    }
    metrics = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "used_local_weights": run_summary["used_local_weights"],
        "entered_model_inference": run_summary["entered_model_inference"],
        "class_balance": run_summary["class_balance"],
        "num_rows": None if route_c_summary is None else route_c_summary.get("num_rows"),
        "num_predictions": None if route_c_logistic_summary is None else route_c_logistic_summary.get("num_predictions"),
        "label_threshold": label_threshold,
    }
    write_json(output_dir / "route_c_execution_run_summary.json", run_summary)
    write_json(output_dir / "route_c_execution_metrics.json", metrics)

    if route_c_summary is not None:
        copy_artifact(
            output_dir / "route_c_execution_run" / "route_c_v6_summary.json",
            output_dir / "model_axis_1p5b_route_c_summary.json",
        )
    if route_c_logistic_summary is not None:
        copy_artifact(
            output_dir / "route_c_execution_run" / "route_c_v6_logistic_summary.json",
            output_dir / "model_axis_1p5b_route_c_logistic_summary.json",
        )

    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "route_c_execution_selection.json").resolve()),
            "plan": str((output_dir / "route_c_execution_plan.json").resolve()),
            "readiness": str((output_dir / "route_c_execution_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "route_c_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "route_c_execution_metrics.json").resolve()),
        },
    }
