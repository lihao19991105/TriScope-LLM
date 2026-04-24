"""Run anchor-aware baseline-preserving follow-up v2 execution on the local 1.5B axis."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_portability import classify_failure_stage
from src.eval.model_axis_1p5b_route_c_refined_execution import (
    ORIGINAL_ROUTE_C_DENSITY,
    copy_artifact,
    extract_positive_support,
    load_json,
    materialize_refined_inputs,
    write_json,
)
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-anchor-execution-v2/v1"
EPS = 1e-12


def build_model_axis_1p5b_route_c_anchor_execution_v2(
    route_c_anchor_followup_v2_dir: Path,
    route_c_anchor_execution_dir: Path,
    route_c_deepened_execution_dir: Path,
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

    v2_registry = load_json(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_selection_registry.json")
    v2_summary = load_json(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_candidate_summary.json")
    v2_precheck = load_json(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_precheck.json")
    v2_readiness = load_json(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_readiness_summary.json")

    anchor_run_summary = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_run_summary.json")
    anchor_metrics = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_metrics.json")
    deepened_run_summary = load_json(route_c_deepened_execution_dir / "route_c_deepened_execution_run_summary.json")
    refined_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    stable_run_summary = load_json(route_c_stable_portability_dir / "route_c_stable_portability_run_summary.json")

    if stable_run_summary.get("summary_status") != "PASS":
        raise ValueError("133 requires route_c stable portability to pass before follow-up v2 execution.")
    if not bool(v2_readiness.get("ready_for_execution")):
        raise ValueError("133 requires 132 readiness to be true before execution.")
    if not bool(v2_precheck.get("worth_executing")):
        raise ValueError("133 requires 132 precheck worth_executing=true before execution.")

    selected_base_ids = [str(item) for item in v2_registry.get("selected_base_ids", [])]
    stable_materialized_inputs_dir = route_c_stable_portability_dir / "materialized_route_c_stable_portability_inputs"
    materialized_inputs_dir = output_dir / "materialized_route_c_anchor_execution_v2_inputs"
    materialization_summary = materialize_refined_inputs(
        stable_materialized_inputs_dir=stable_materialized_inputs_dir,
        refined_base_ids=selected_base_ids,
        output_dir=materialized_inputs_dir,
    )

    refined_density = float(refined_metrics.get("refined_density", 0.0) or 0.0)
    anchor_density = float(anchor_metrics.get("anchor_density", 0.0) or 0.0)
    deepened_density = float(deepened_run_summary.get("deepened_density", 0.0) or 0.0)

    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "selected_model_profile": "pilot_small_hf",
        "selection_registry": str((route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_selection_registry.json").resolve()),
        "selected_base_ids": selected_base_ids,
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": v2_summary.get("selected_contract_count"),
        "expected_class_balance": v2_summary.get("class_balance"),
        "why_selected": [
            "132 keeps the anchor-preserving 6-contract budget while probing one controlled neighbor swap.",
            "The candidate keeps density at anchor baseline floor and passed a logistic precheck.",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "execution_goal": "verify whether baseline-preserving v2 keeps anchor advantages and adds analyzable value over both 124 and 129",
        "difference_vs_124_anchor_and_129_deepened": {
            "anchor_selected_contract_count": anchor_run_summary.get("num_rows"),
            "deepened_selected_contract_count": deepened_run_summary.get("num_rows"),
            "v2_selected_contract_count": v2_summary.get("selected_contract_count"),
            "anchor_density": anchor_density,
            "deepened_density": deepened_density,
            "v2_target_density_floor": anchor_density,
            "v2_swap_detail": {
                "swapped_out_neighbor_base_id": v2_registry.get("swapped_out_neighbor_base_id"),
                "swapped_in_neighbor_base_id": v2_registry.get("swapped_in_neighbor_base_id"),
            },
        },
        "success_criteria": [
            "used_local_weights=true",
            "entered_model_inference=true",
            "class balance keeps at least two classes",
            "density stays >= anchor baseline",
            "reference anchor remains preserved",
            "logistic summary remains PASS",
        ],
        "fallback_rule": [
            "If v2 fails any baseline-preserving gate, fall back to anchor-aware baseline.",
            "If v2 preserves baseline but shows no extension signal, keep anchor-aware baseline as working baseline.",
        ],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "ready_run": True,
        "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        "selected_base_ids": selected_base_ids,
        "selected_contract_count": v2_summary.get("selected_contract_count"),
        "expected_class_balance": v2_summary.get("class_balance"),
        "expected_density": v2_summary.get("candidate_density"),
        "anchor_density_reference": anchor_density,
        "materialization_summary": materialization_summary,
    }
    write_json(output_dir / "route_c_anchor_execution_v2_selection.json", selection)
    write_json(output_dir / "route_c_anchor_execution_v2_plan.json", plan)
    write_json(output_dir / "route_c_anchor_execution_v2_readiness_summary.json", readiness)

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
            output_dir=output_dir / "route_c_anchor_execution_v2_run",
            seed=seed,
            label_threshold=label_threshold,
            model_profile_name="pilot_small_hf",
            label_parse_mode="robust_prefix",
        )
        route_c_summary = load_json(Path(run_result["output_paths"]["summary"]))
        route_c_logistic_summary = load_json(Path(run_result["output_paths"]["logistic_summary"]))
        positive_support_sample_ids, positive_support_base_ids = extract_positive_support(
            output_dir / "route_c_anchor_execution_v2_run" / "route_c_v6_dataset.jsonl"
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
    v2_density = (float(label_1) / float(num_rows)) if num_rows > 0 else None
    density_vs_anchor = v2_density / anchor_density if v2_density is not None and anchor_density > 0 else None
    density_vs_refined = v2_density / refined_density if v2_density is not None and refined_density > 0 else None
    density_vs_deepened = v2_density / deepened_density if v2_density is not None and deepened_density > 0 else None

    has_two_classes = bool(label_0 > 0 and label_1 > 0)
    logistic_status = None if route_c_logistic_summary is None else str(route_c_logistic_summary.get("summary_status"))
    logistic_pass = bool(logistic_status == "PASS")

    reference_anchor_sample_ids = [str(item) for item in anchor_run_summary.get("positive_support_sample_ids", []) or []]
    reference_anchor_preserved = all(item in positive_support_sample_ids for item in reference_anchor_sample_ids)
    positive_support_count = len(positive_support_sample_ids)
    anchor_positive_support_count = len(reference_anchor_sample_ids)
    baseline_preserved = bool(
        run_summary_status == "PASS"
        and has_two_classes
        and logistic_pass
        and reference_anchor_preserved
        and v2_density is not None
        and v2_density + EPS >= anchor_density
    )

    if not baseline_preserved:
        baseline_assessment = "should_fall_back_to_anchor_baseline"
    elif v2_density > anchor_density + EPS or positive_support_count > anchor_positive_support_count:
        baseline_assessment = "baseline_preserved_and_extended"
    else:
        baseline_assessment = "baseline_preserved_but_no_extension"

    run_summary = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
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
        "reference_anchor_sample_ids": reference_anchor_sample_ids,
        "reference_anchor_preserved": reference_anchor_preserved,
        "v2_density": v2_density,
        "anchor_density": anchor_density,
        "refined_density": refined_density,
        "deepened_density": deepened_density,
        "original_density": ORIGINAL_ROUTE_C_DENSITY,
        "density_vs_anchor": density_vs_anchor,
        "density_vs_refined": density_vs_refined,
        "density_vs_deepened": density_vs_deepened,
        "has_two_classes": has_two_classes,
        "logistic_status": logistic_status,
        "baseline_preservation_assessment": baseline_assessment,
        "label_parse_mode": "robust_prefix",
    }
    metrics = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "used_local_weights": run_summary.get("used_local_weights"),
        "entered_model_inference": run_summary.get("entered_model_inference"),
        "class_balance": class_balance,
        "num_rows": run_summary.get("num_rows"),
        "num_predictions": None if route_c_logistic_summary is None else route_c_logistic_summary.get("num_predictions"),
        "label_threshold": label_threshold,
        "original_density": ORIGINAL_ROUTE_C_DENSITY,
        "refined_density": refined_density,
        "anchor_density": anchor_density,
        "deepened_density": deepened_density,
        "v2_density": v2_density,
        "density_vs_anchor": density_vs_anchor,
        "density_vs_refined": density_vs_refined,
        "density_vs_deepened": density_vs_deepened,
        "reference_anchor_preserved": reference_anchor_preserved,
        "baseline_preservation_assessment": baseline_assessment,
    }
    positive_support_breakdown = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "positive_support_sample_ids": positive_support_sample_ids,
        "positive_support_base_ids": positive_support_base_ids,
        "positive_support_count": positive_support_count,
        "anchor_positive_support_count": anchor_positive_support_count,
        "incremental_positive_support_vs_anchor": positive_support_count - anchor_positive_support_count,
        "reference_anchor_preserved": reference_anchor_preserved,
    }
    density_comparison = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "original_density": ORIGINAL_ROUTE_C_DENSITY,
        "refined_density": refined_density,
        "anchor_density": anchor_density,
        "deepened_density": deepened_density,
        "v2_density": v2_density,
        "density_vs_anchor": density_vs_anchor,
        "density_vs_refined": density_vs_refined,
        "density_vs_deepened": density_vs_deepened,
    }

    write_json(output_dir / "route_c_anchor_execution_v2_run_summary.json", run_summary)
    write_json(output_dir / "route_c_anchor_execution_v2_metrics.json", metrics)
    write_json(output_dir / "route_c_anchor_execution_v2_positive_support_breakdown.json", positive_support_breakdown)
    write_json(output_dir / "route_c_anchor_execution_v2_density_comparison.json", density_comparison)
    copy_artifact(
        route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_selection_registry.json",
        output_dir / "route_c_anchor_followup_v2_selection_registry_snapshot.json",
    )

    if route_c_summary is not None:
        copy_artifact(
            output_dir / "route_c_anchor_execution_v2_run" / "route_c_v6_summary.json",
            output_dir / "model_axis_1p5b_route_c_anchor_v2_summary.json",
        )
    if route_c_logistic_summary is not None:
        copy_artifact(
            output_dir / "route_c_anchor_execution_v2_run" / "route_c_v6_logistic_summary.json",
            output_dir / "model_axis_1p5b_route_c_anchor_v2_logistic_summary.json",
        )

    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "route_c_anchor_execution_v2_selection.json").resolve()),
            "plan": str((output_dir / "route_c_anchor_execution_v2_plan.json").resolve()),
            "readiness": str((output_dir / "route_c_anchor_execution_v2_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "route_c_anchor_execution_v2_run_summary.json").resolve()),
            "metrics": str((output_dir / "route_c_anchor_execution_v2_metrics.json").resolve()),
            "positive_support_breakdown": str(
                (output_dir / "route_c_anchor_execution_v2_positive_support_breakdown.json").resolve()
            ),
            "density_comparison": str((output_dir / "route_c_anchor_execution_v2_density_comparison.json").resolve()),
        },
    }
