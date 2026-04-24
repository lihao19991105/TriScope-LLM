"""Run deepened route_c candidate execution on the local 1.5B model axis."""

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
    write_json,
)
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-deepened-execution/v1"


def _compare_density(lhs: float | None, rhs: float | None) -> str | None:
    if lhs is None or rhs is None:
        return None
    eps = 1e-12
    if lhs > rhs + eps:
        return "better"
    if lhs < rhs - eps:
        return "worse"
    return "same"


def build_model_axis_1p5b_route_c_deepened_execution(
    route_c_anchor_deepening_dir: Path,
    route_c_anchor_execution_dir: Path,
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

    deepened_registry = load_json(route_c_anchor_deepening_dir / "route_c_anchor_deepened_selection_registry.json")
    deepened_summary = load_json(route_c_anchor_deepening_dir / "route_c_anchor_deepened_candidate_summary.json")
    deepening_recommendation = load_json(route_c_anchor_deepening_dir / "route_c_anchor_deepening_recommendation.json")
    anchor_run_summary = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_run_summary.json")
    anchor_metrics = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_metrics.json")
    refined_run_summary = load_json(route_c_refined_execution_dir / "route_c_refined_execution_run_summary.json")
    refined_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    stable_run_summary = load_json(route_c_stable_portability_dir / "route_c_stable_portability_run_summary.json")

    if stable_run_summary.get("summary_status") != "PASS":
        raise ValueError("129 requires route_c stable portability to pass before deepened execution can start.")
    if deepening_recommendation.get("recommended_next_step") != "selection_deepening_first":
        raise ValueError("129 requires 128 to recommend selection_deepening_first before deepened execution.")

    selected_base_ids = [str(item) for item in deepened_registry.get("selected_base_ids", [])]
    stable_materialized_inputs_dir = route_c_stable_portability_dir / "materialized_route_c_stable_portability_inputs"
    materialized_inputs_dir = output_dir / "materialized_route_c_deepened_execution_inputs"
    materialization_summary = materialize_refined_inputs(
        stable_materialized_inputs_dir=stable_materialized_inputs_dir,
        refined_base_ids=selected_base_ids,
        output_dir=materialized_inputs_dir,
    )

    refined_density = float(refined_metrics.get("refined_density", 0.0) or 0.0)
    anchor_density = float(anchor_metrics.get("anchor_density", 0.0) or 0.0)
    expected_deepened_density = float(deepened_summary.get("deepened_density", 0.0) or 0.0)

    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_deepened",
        "selected_model_profile": "pilot_small_hf",
        "selection_registry": str((route_c_anchor_deepening_dir / "route_c_anchor_deepened_selection_registry.json").resolve()),
        "selected_base_ids": selected_base_ids,
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": deepened_summary.get("selected_contract_count"),
        "expected_class_balance": deepened_summary.get("class_balance"),
        "why_selected": [
            "128 materialized a deepened candidate that adds local thickness while preserving the refined density floor.",
            "This run checks whether the materialized deepened candidate is a real executable baseline rather than a paper-only object.",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_deepened",
        "execution_goal": "verify whether the deepened candidate is executable, keeps at least two classes, and preserves refined-floor density with anchor continuity",
        "difference_vs_120_and_124": {
            "refined_selected_contract_count": refined_run_summary.get("num_rows"),
            "anchor_selected_contract_count": anchor_run_summary.get("num_rows"),
            "deepened_selected_contract_count": deepened_summary.get("selected_contract_count"),
            "refined_density": refined_density,
            "anchor_density": anchor_density,
            "deepened_target_density": expected_deepened_density,
            "selection_strategy": deepened_registry.get("selection_strategy"),
        },
        "success_criterion": [
            "used_local_weights=true",
            "entered_model_inference=true",
            "deepened execution keeps at least two classes",
            "deepened density is not below refined 1/8 floor",
            "reference anchor remains in positive support",
            "route_c deepened logistic summary remains PASS",
        ],
        "fallback_rule_if_worse_than_anchor": [
            "If deepened keeps only refined-floor density and does not add new positive support, keep anchor-aware as working baseline.",
            "Only consider upgrading to deepened baseline when it is not worse than anchor density or provides new analyzable support under stability.",
        ],
        "risk_focus": [
            "Deepening may preserve execution while losing anchor density gain.",
            "The route can remain single-anchor and fail to add practical value beyond thickness.",
        ],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_deepened",
        "ready_run": True,
        "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        "selected_base_ids": selected_base_ids,
        "selected_contract_count": deepened_summary.get("selected_contract_count"),
        "expected_class_balance": deepened_summary.get("class_balance"),
        "expected_deepened_density": expected_deepened_density,
        "refined_density_floor": refined_density,
        "anchor_density_reference": anchor_density,
        "materialization_summary": materialization_summary,
    }
    write_json(output_dir / "route_c_deepened_execution_selection.json", selection)
    write_json(output_dir / "route_c_deepened_execution_plan.json", plan)
    write_json(output_dir / "route_c_deepened_execution_readiness_summary.json", readiness)

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
            output_dir=output_dir / "route_c_deepened_execution_run",
            seed=seed,
            label_threshold=label_threshold,
            model_profile_name="pilot_small_hf",
            label_parse_mode="robust_prefix",
        )
        route_c_summary = load_json(Path(run_result["output_paths"]["summary"]))
        route_c_logistic_summary = load_json(Path(run_result["output_paths"]["logistic_summary"]))
        positive_support_sample_ids, positive_support_base_ids = extract_positive_support(
            output_dir / "route_c_deepened_execution_run" / "route_c_v6_dataset.jsonl"
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
    deepened_density = (float(label_1) / float(num_rows)) if num_rows > 0 else None
    density_gain_vs_original = deepened_density / ORIGINAL_ROUTE_C_DENSITY if deepened_density is not None else None
    density_vs_refined = deepened_density / refined_density if deepened_density is not None and refined_density > 0 else None
    density_vs_anchor = deepened_density / anchor_density if deepened_density is not None and anchor_density > 0 else None
    has_two_classes = bool(label_0 > 0 and label_1 > 0)
    logistic_status = None if route_c_logistic_summary is None else str(route_c_logistic_summary.get("summary_status"))
    logistic_pass = bool(logistic_status == "PASS")

    reference_anchor_sample_ids = [str(item) for item in anchor_run_summary.get("positive_support_sample_ids", []) or []]
    reference_anchor_preserved = all(item in positive_support_sample_ids for item in reference_anchor_sample_ids)
    positive_support_count = len(positive_support_sample_ids)
    anchor_positive_support_count = len(reference_anchor_sample_ids)

    relative_to_anchor = _compare_density(deepened_density, anchor_density)
    relative_to_refined = _compare_density(deepened_density, refined_density)
    meets_minimum = bool(
        run_summary_status == "PASS"
        and has_two_classes
        and logistic_pass
        and reference_anchor_preserved
        and deepened_density is not None
        and deepened_density >= refined_density
    )
    if not meets_minimum:
        baseline_upgrade_assessment = "does_not_meet_minimum_requirements"
    elif relative_to_anchor == "better":
        baseline_upgrade_assessment = "candidate_for_new_working_baseline"
    elif relative_to_anchor == "same" and positive_support_count >= anchor_positive_support_count:
        baseline_upgrade_assessment = "parity_with_anchor_candidate_for_followup_stability"
    else:
        baseline_upgrade_assessment = "holds_refined_floor_but_fall_back_to_anchor_baseline"

    run_summary = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_deepened",
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
        "deepened_density": deepened_density,
        "refined_density": refined_density,
        "anchor_density": anchor_density,
        "original_density": ORIGINAL_ROUTE_C_DENSITY,
        "density_gain_vs_original": density_gain_vs_original,
        "density_vs_refined": density_vs_refined,
        "density_vs_anchor": density_vs_anchor,
        "relative_to_refined": relative_to_refined,
        "relative_to_anchor": relative_to_anchor,
        "has_two_classes": has_two_classes,
        "logistic_status": logistic_status,
        "baseline_upgrade_assessment": baseline_upgrade_assessment,
        "deepened_value_judgement": (
            "worth_considering_as_new_baseline"
            if baseline_upgrade_assessment in {
                "candidate_for_new_working_baseline",
                "parity_with_anchor_candidate_for_followup_stability",
            }
            else "holds_refined_floor_only"
        ),
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
        "deepened_density": deepened_density,
        "density_vs_refined": density_vs_refined,
        "density_vs_anchor": density_vs_anchor,
        "reference_anchor_preserved": reference_anchor_preserved,
        "baseline_upgrade_assessment": baseline_upgrade_assessment,
    }
    positive_support_breakdown = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_deepened",
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
        "selected_cell": "route_c_anchor_deepened",
        "original_density": ORIGINAL_ROUTE_C_DENSITY,
        "refined_density": refined_density,
        "anchor_density": anchor_density,
        "deepened_density": deepened_density,
        "density_vs_refined": density_vs_refined,
        "density_vs_anchor": density_vs_anchor,
        "relative_to_refined": relative_to_refined,
        "relative_to_anchor": relative_to_anchor,
    }

    write_json(output_dir / "route_c_deepened_execution_run_summary.json", run_summary)
    write_json(output_dir / "route_c_deepened_execution_metrics.json", metrics)
    write_json(output_dir / "route_c_deepened_positive_support_breakdown.json", positive_support_breakdown)
    write_json(output_dir / "route_c_deepened_density_comparison.json", density_comparison)
    copy_artifact(
        route_c_anchor_deepening_dir / "route_c_anchor_deepened_selection_registry.json",
        output_dir / "route_c_anchor_deepened_selection_registry_snapshot.json",
    )

    if route_c_summary is not None:
        copy_artifact(
            output_dir / "route_c_deepened_execution_run" / "route_c_v6_summary.json",
            output_dir / "model_axis_1p5b_route_c_deepened_summary.json",
        )
    if route_c_logistic_summary is not None:
        copy_artifact(
            output_dir / "route_c_deepened_execution_run" / "route_c_v6_logistic_summary.json",
            output_dir / "model_axis_1p5b_route_c_deepened_logistic_summary.json",
        )

    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "route_c_deepened_execution_selection.json").resolve()),
            "plan": str((output_dir / "route_c_deepened_execution_plan.json").resolve()),
            "readiness": str((output_dir / "route_c_deepened_execution_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "route_c_deepened_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "route_c_deepened_execution_metrics.json").resolve()),
            "positive_support_breakdown": str((output_dir / "route_c_deepened_positive_support_breakdown.json").resolve()),
            "density_comparison": str((output_dir / "route_c_deepened_density_comparison.json").resolve()),
        },
    }
