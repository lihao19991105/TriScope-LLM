"""Run anchor-aware route_c execution on the local 1.5B model axis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_portability import classify_failure_stage
from src.eval.model_axis_1p5b_route_c_refined_execution import (
    ORIGINAL_ROUTE_C_DENSITY,
    copy_artifact,
    extract_positive_support,
    load_json,
    materialize_refined_inputs,
)
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-anchor-execution/v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_model_axis_1p5b_route_c_anchor_execution(
    route_c_anchor_followup_dir: Path,
    route_c_refined_execution_dir: Path,
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

    selection_registry = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_selection_registry.json")
    followup_summary = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_candidate_summary.json")
    followup_precheck = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_precheck.json")
    refined_run_summary = load_json(route_c_refined_execution_dir / "route_c_refined_execution_run_summary.json")
    refined_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    stable_run_summary = load_json(route_c_stable_portability_dir / "route_c_stable_portability_run_summary.json")
    if stable_run_summary.get("summary_status") != "PASS":
        raise ValueError("124 requires route_c stable portability to pass before anchor-aware execution can start.")
    if not bool(followup_precheck.get("worth_executing")):
        raise ValueError("124 requires 123 to mark the anchor-aware follow-up candidate as worth executing.")

    selected_base_ids = [str(item) for item in selection_registry.get("selected_base_ids", [])]
    stable_materialized_inputs_dir = route_c_stable_portability_dir / "materialized_route_c_stable_portability_inputs"
    materialized_inputs_dir = output_dir / "materialized_route_c_anchor_execution_inputs"
    materialization_summary = materialize_refined_inputs(
        stable_materialized_inputs_dir=stable_materialized_inputs_dir,
        refined_base_ids=selected_base_ids,
        output_dir=materialized_inputs_dir,
    )

    refined_density = float(refined_metrics.get("refined_density", 0.0) or 0.0)
    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup",
        "selected_model_profile": "pilot_small_hf",
        "selection_registry": str((route_c_anchor_followup_dir / "route_c_anchor_followup_selection_registry.json").resolve()),
        "selected_base_ids": selected_base_ids,
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": followup_summary.get("selected_contract_count"),
        "expected_class_balance": followup_summary.get("class_balance"),
        "why_selected": [
            "123 ranked same-regime negatives around the single stable positive anchor and kept only the nearest ones.",
            "This candidate promises a denser route_c execution than the 1/8 refined baseline without opening a new search axis.",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup",
        "execution_goal": "verify whether the anchor-aware route_c candidate preserves true local execution while improving density over the refined 1/8 baseline",
        "difference_vs_120": {
            "refined_selected_contract_count": refined_run_summary.get("num_rows"),
            "anchor_selected_contract_count": followup_summary.get("selected_contract_count"),
            "refined_density": refined_density,
            "anchor_target_density": followup_summary.get("anchor_followup_density"),
            "selection_strategy": selection_registry.get("selection_strategy"),
        },
        "success_criterion": [
            "used_local_weights=true",
            "entered_model_inference=true",
            "anchor-aware execution keeps at least two classes",
            "anchor-aware density exceeds the refined 1/8 baseline",
            "route_c anchor-aware logistic summary remains PASS",
        ],
        "risk_focus": [
            "The follow-up candidate may improve density without adding any new positive support.",
            "The smaller anchor-aware subset may be denser but still fragile without a later stability pass.",
        ],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup",
        "ready_run": True,
        "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        "selected_base_ids": selected_base_ids,
        "selected_contract_count": followup_summary.get("selected_contract_count"),
        "expected_class_balance": followup_summary.get("class_balance"),
        "expected_density": followup_summary.get("anchor_followup_density"),
        "refined_density": refined_density,
        "materialization_summary": materialization_summary,
    }
    write_json(output_dir / "route_c_anchor_execution_selection.json", selection)
    write_json(output_dir / "route_c_anchor_execution_plan.json", plan)
    write_json(output_dir / "route_c_anchor_execution_readiness_summary.json", readiness)

    run_summary_status = "BLOCKED"
    execution_status = "BLOCKED"
    route_c_summary: dict[str, Any] | None = None
    route_c_logistic_summary: dict[str, Any] | None = None
    failure_reason = None
    failure_stage = None
    positive_support_sample_ids: list[str] = []
    positive_support_base_ids: list[str] = []

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
            output_dir=output_dir / "route_c_anchor_execution_run",
            seed=seed,
            label_threshold=label_threshold,
            model_profile_name="pilot_small_hf",
            label_parse_mode="robust_prefix",
        )
        route_c_summary = load_json(Path(run_result["output_paths"]["summary"]))
        route_c_logistic_summary = load_json(Path(run_result["output_paths"]["logistic_summary"]))
        positive_support_sample_ids, positive_support_base_ids = extract_positive_support(
            output_dir / "route_c_anchor_execution_run" / "route_c_v6_dataset.jsonl"
        )
        run_summary_status = "PASS"
        execution_status = "FULL_EXECUTE"
    except Exception as exc:
        failure_reason = str(exc)
        failure_stage = classify_failure_stage(failure_reason)
        run_summary_status = "PARTIAL"
        execution_status = "PARTIAL"

    class_balance = None if route_c_summary is None else route_c_summary.get("class_balance")
    label_0 = 0 if class_balance is None else int(class_balance.get("label_0", 0) or 0)
    label_1 = 0 if class_balance is None else int(class_balance.get("label_1", 0) or 0)
    num_rows = 0 if route_c_summary is None else int(route_c_summary.get("num_rows", 0) or 0)
    anchor_density = (float(label_1) / float(num_rows)) if num_rows > 0 else None
    density_gain_vs_original = anchor_density / ORIGINAL_ROUTE_C_DENSITY if anchor_density is not None and ORIGINAL_ROUTE_C_DENSITY > 0 else None
    density_gain_vs_refined = anchor_density / refined_density if anchor_density is not None and refined_density > 0 else None

    run_summary = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "used_local_weights": True if run_summary_status == "PASS" else None,
        "entered_model_inference": True if run_summary_status == "PASS" else None,
        "class_balance": class_balance,
        "num_rows": num_rows if run_summary_status == "PASS" else None,
        "execution_status": execution_status,
        "failure_stage": failure_stage,
        "failure_reason": failure_reason,
        "positive_support_sample_ids": positive_support_sample_ids if run_summary_status == "PASS" else None,
        "positive_support_base_ids": positive_support_base_ids if run_summary_status == "PASS" else None,
        "anchor_density": anchor_density,
        "refined_density": refined_density,
        "original_density": ORIGINAL_ROUTE_C_DENSITY,
        "density_gain_vs_original": density_gain_vs_original,
        "density_gain_vs_refined": density_gain_vs_refined,
        "density_improved_vs_120": bool(anchor_density is not None and anchor_density > refined_density),
        "label_parse_mode": "robust_prefix",
    }
    metrics = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "used_local_weights": run_summary["used_local_weights"],
        "entered_model_inference": run_summary["entered_model_inference"],
        "class_balance": class_balance,
        "num_rows": run_summary["num_rows"],
        "num_predictions": None if route_c_logistic_summary is None else route_c_logistic_summary.get("num_predictions"),
        "label_threshold": label_threshold,
        "original_density": ORIGINAL_ROUTE_C_DENSITY,
        "refined_density": refined_density,
        "anchor_density": anchor_density,
        "density_gain_vs_original": density_gain_vs_original,
        "density_gain_vs_refined": density_gain_vs_refined,
    }
    positive_support_breakdown = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup",
        "positive_support_sample_ids": positive_support_sample_ids,
        "positive_support_base_ids": positive_support_base_ids,
        "positive_support_count": len(positive_support_sample_ids),
        "incremental_positive_support_vs_refined": max(0, len(positive_support_sample_ids) - 1),
        "notes": [
            "Anchor-aware follow-up is allowed to improve density without increasing the absolute positive count.",
        ],
    }
    write_json(output_dir / "route_c_anchor_execution_run_summary.json", run_summary)
    write_json(output_dir / "route_c_anchor_execution_metrics.json", metrics)
    write_json(output_dir / "route_c_anchor_execution_positive_support_breakdown.json", positive_support_breakdown)
    copy_artifact(route_c_anchor_followup_dir / "route_c_anchor_followup_selection_registry.json", output_dir / "route_c_anchor_followup_selection_registry_snapshot.json")

    if route_c_summary is not None:
        copy_artifact(
            output_dir / "route_c_anchor_execution_run" / "route_c_v6_summary.json",
            output_dir / "model_axis_1p5b_route_c_anchor_summary.json",
        )
    if route_c_logistic_summary is not None:
        copy_artifact(
            output_dir / "route_c_anchor_execution_run" / "route_c_v6_logistic_summary.json",
            output_dir / "model_axis_1p5b_route_c_anchor_logistic_summary.json",
        )

    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "route_c_anchor_execution_selection.json").resolve()),
            "plan": str((output_dir / "route_c_anchor_execution_plan.json").resolve()),
            "readiness": str((output_dir / "route_c_anchor_execution_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "route_c_anchor_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "route_c_anchor_execution_metrics.json").resolve()),
        },
    }
