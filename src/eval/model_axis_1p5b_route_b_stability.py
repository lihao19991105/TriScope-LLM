"""Confirm stabilized 1.5B route_b stability with lightweight rerun perturbations."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_execution import load_json
from src.eval.model_axis_1p5b_route_b_stable_execution import (
    build_model_axis_1p5b_route_b_stable_execution,
)


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-b-stability/v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Expected at least one CSV row.")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def classify_failure_stage(error_message: str) -> str:
    lowered = error_message.lower()
    if "at least two classes" in lowered or "single-class" in lowered:
        return "labels"
    if "input not found" in lowered or "query contracts" in lowered:
        return "sampling"
    if "fallback" in lowered:
        return "fallback"
    if "available_local" in lowered or "inference" in lowered or "from_pretrained" in lowered:
        return "inference"
    return "unknown"


def build_model_axis_1p5b_route_b_stability(
    stable_reference_run_summary_path: Path,
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
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    stable_reference = load_json(stable_reference_run_summary_path)
    precheck = load_json(stabilization_precheck_path)

    protocol = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "protocol_name": "route_b_stability_confirmation_minimal_v1",
        "scope": "1p5b_route_b_stabilized_only",
        "design_principles": [
            "No model-axis expansion.",
            "No dataset/proxy substrate expansion.",
            "Keep route_b stabilized pipeline unchanged.",
            "Only perturb seed and small target-budget neighborhood around 32.",
        ],
        "perturbation_axes": {
            "seed": [42, 43],
            "target_budget": [31, 32, 33],
        },
        "run_scenarios": [
            {"run_id": "run_seed42_budget32", "seed": 42, "target_budget": 32, "role": "baseline_repeat"},
            {"run_id": "run_seed43_budget32", "seed": 43, "target_budget": 32, "role": "seed_perturbation"},
            {"run_id": "run_seed42_budget31", "seed": 42, "target_budget": 31, "role": "budget_perturbation_minus_1"},
            {"run_id": "run_seed42_budget33", "seed": 42, "target_budget": 33, "role": "budget_perturbation_plus_1"},
        ],
        "reference_run": {
            "execution_status": stable_reference.get("execution_status"),
            "class_balance": stable_reference.get("class_balance"),
            "logistic_pass": stable_reference.get("logistic_pass"),
        },
    }

    success_criteria = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "hard_requirements": [
            "Every confirmation run must keep used_local_weights=true and entered_model_inference=true.",
            "Every confirmation run must keep class_balance with at least two classes.",
            "Every confirmation run must keep logistic summary status PASS.",
            "No run is allowed to regress to single-class collapse blocker.",
        ],
        "acceptable_variation": [
            "Class balance ratio may vary across runs as long as both classes remain present.",
            "Mean prediction score can vary within normal stochastic drift.",
        ],
        "unacceptable_variation": [
            "Any run with label_0 == 0 or label_1 == 0.",
            "Any run with logistic BLOCKED/PARTIAL due to class collapse.",
            "Any run that fails to enter local 1.5B inference.",
        ],
    }

    run_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_runs": len(protocol["run_scenarios"]),
        "preconditions": {
            "stabilization_precheck_pass": precheck.get("logistic_prereq_two_classes") is True,
            "expected_reference_two_class": stable_reference.get("class_balance", {}).get("label_0", 0) > 0
            and stable_reference.get("class_balance", {}).get("label_1", 0) > 0,
        },
        "execution_template": {
            "pipeline": "build_model_axis_1p5b_route_b_stable_execution",
            "label_threshold": label_threshold,
            "fixed_model_profile": "pilot_small_hf",
            "fixed_selected_cell": "route_b",
        },
        "scenarios": protocol["run_scenarios"],
    }

    write_json(output_dir / "route_b_stability_protocol.json", protocol)
    write_json(output_dir / "route_b_stability_success_criteria.json", success_criteria)
    write_json(output_dir / "route_b_stability_run_plan.json", run_plan)

    results: list[dict[str, Any]] = []
    registry_runs: list[dict[str, Any]] = []

    for scenario in protocol["run_scenarios"]:
        run_id = str(scenario["run_id"])
        run_output_dir = output_dir / "runs" / run_id
        try:
            result = build_model_axis_1p5b_route_b_stable_execution(
                dry_run_summary_path=dry_run_summary_path,
                execution_gate_path=execution_gate_path,
                stabilization_precheck_path=stabilization_precheck_path,
                bootstrap_materialized_inputs_dir=bootstrap_materialized_inputs_dir,
                dry_run_materialized_inputs_dir=dry_run_materialized_inputs_dir,
                reference_route_b_dataset_path=reference_route_b_dataset_path,
                reference_route_b_slice_path=reference_route_b_slice_path,
                models_config_path=models_config_path,
                reasoning_config_path=reasoning_config_path,
                confidence_config_path=confidence_config_path,
                illumination_config_path=illumination_config_path,
                reasoning_prompt_dir=reasoning_prompt_dir,
                confidence_prompt_dir=confidence_prompt_dir,
                illumination_prompt_dir=illumination_prompt_dir,
                output_dir=run_output_dir,
                seed=int(scenario["seed"]),
                label_threshold=label_threshold,
                target_budget=int(scenario["target_budget"]),
            )
            run_summary = load_json(Path(result["output_paths"]["run_summary"]))
            run_metrics = load_json(Path(result["output_paths"]["metrics"]))
            route_b_summary = load_json(Path(result["output_paths"]["route_b_summary"]))
            route_b_logistic = load_json(Path(result["output_paths"]["route_b_logistic_summary"]))

            class_balance = route_b_summary.get("class_balance", {})
            has_two_classes = class_balance.get("label_0", 0) > 0 and class_balance.get("label_1", 0) > 0
            logistic_pass = route_b_logistic.get("summary_status") == "PASS"

            row = {
                "run_id": run_id,
                "seed": int(scenario["seed"]),
                "target_budget": int(scenario["target_budget"]),
                "role": str(scenario["role"]),
                "summary_status": run_summary.get("summary_status"),
                "execution_status": run_summary.get("execution_status"),
                "used_local_weights": bool(run_summary.get("used_local_weights")),
                "entered_model_inference": bool(run_summary.get("entered_model_inference")),
                "num_rows": int(run_metrics.get("num_rows", 0) or 0),
                "label_0": int(class_balance.get("label_0", 0) or 0),
                "label_1": int(class_balance.get("label_1", 0) or 0),
                "has_two_classes": has_two_classes,
                "logistic_status": route_b_logistic.get("summary_status"),
                "logistic_pass": logistic_pass,
                "mean_prediction_score": run_metrics.get("mean_prediction_score"),
                "num_positive_predictions": int(run_metrics.get("num_positive_predictions", 0) or 0),
                "fallback_triggered": "not_exposed_in_stable_path",
                "failure_stage": None,
                "failure_reason": None,
            }
            results.append(row)
            registry_runs.append(
                {
                    "run_id": run_id,
                    "scenario": scenario,
                    "run_dir": str(run_output_dir.resolve()),
                    "run_summary": str((run_output_dir / "route_b_stable_execution_run_summary.json").resolve()),
                    "metrics": str((run_output_dir / "route_b_stable_execution_metrics.json").resolve()),
                    "route_b_summary": str((run_output_dir / "route_b_stable_summary.json").resolve()),
                    "route_b_logistic_summary": str((run_output_dir / "route_b_stable_logistic_summary.json").resolve()),
                }
            )
        except Exception as exc:
            error_message = str(exc)
            row = {
                "run_id": run_id,
                "seed": int(scenario["seed"]),
                "target_budget": int(scenario["target_budget"]),
                "role": str(scenario["role"]),
                "summary_status": "FAIL",
                "execution_status": "BLOCKED",
                "used_local_weights": False,
                "entered_model_inference": False,
                "num_rows": 0,
                "label_0": 0,
                "label_1": 0,
                "has_two_classes": False,
                "logistic_status": "BLOCKED",
                "logistic_pass": False,
                "mean_prediction_score": None,
                "num_positive_predictions": 0,
                "fallback_triggered": "not_exposed_in_stable_path",
                "failure_stage": classify_failure_stage(error_message),
                "failure_reason": error_message,
            }
            results.append(row)
            registry_runs.append(
                {
                    "run_id": run_id,
                    "scenario": scenario,
                    "run_dir": str(run_output_dir.resolve()),
                    "failure": error_message,
                }
            )

    if not results:
        raise ValueError("No stability confirmation runs were executed.")

    all_two_classes = all(bool(row["has_two_classes"]) for row in results)
    all_logistic_pass = all(bool(row["logistic_pass"]) for row in results)
    any_single_class_regression = any(not bool(row["has_two_classes"]) for row in results)
    any_failed_run = any(str(row.get("summary_status")) == "FAIL" for row in results)

    stability_established = all_two_classes and all_logistic_pass and not any_failed_run
    summary = {
        "summary_status": "PASS" if stability_established else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "total_runs": len(results),
        "all_two_classes": all_two_classes,
        "all_logistic_pass": all_logistic_pass,
        "any_single_class_regression": any_single_class_regression,
        "any_failed_run": any_failed_run,
        "stability_established": stability_established,
        "stable_for_route_c_baseline": stability_established,
        "class_balance_distribution": [
            {
                "run_id": row["run_id"],
                "label_0": row["label_0"],
                "label_1": row["label_1"],
            }
            for row in results
        ],
        "logistic_status_distribution": [
            {
                "run_id": row["run_id"],
                "logistic_status": row["logistic_status"],
            }
            for row in results
        ],
        "notes": [
            "This is a minimal stability confirmation protocol, not a large-scale robustness study.",
            "If stability_established=true, route_b can serve as a practical baseline before route_c portability expansion.",
        ],
    }

    write_json(
        output_dir / "route_b_stability_run_registry.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "runs": registry_runs,
            "artifacts": {
                "protocol": str((output_dir / "route_b_stability_protocol.json").resolve()),
                "success_criteria": str((output_dir / "route_b_stability_success_criteria.json").resolve()),
                "run_plan": str((output_dir / "route_b_stability_run_plan.json").resolve()),
                "results": str((output_dir / "route_b_stability_results.jsonl").resolve()),
                "summary": str((output_dir / "route_b_stability_summary.json").resolve()),
                "comparison_csv": str((output_dir / "route_b_stability_comparison.csv").resolve()),
            },
        },
    )
    write_jsonl(output_dir / "route_b_stability_results.jsonl", results)
    write_json(output_dir / "route_b_stability_summary.json", summary)
    write_csv(output_dir / "route_b_stability_comparison.csv", results)

    return {
        "summary": summary,
        "output_paths": {
            "protocol": str((output_dir / "route_b_stability_protocol.json").resolve()),
            "success_criteria": str((output_dir / "route_b_stability_success_criteria.json").resolve()),
            "run_plan": str((output_dir / "route_b_stability_run_plan.json").resolve()),
            "run_registry": str((output_dir / "route_b_stability_run_registry.json").resolve()),
            "results": str((output_dir / "route_b_stability_results.jsonl").resolve()),
            "summary": str((output_dir / "route_b_stability_summary.json").resolve()),
            "comparison_csv": str((output_dir / "route_b_stability_comparison.csv").resolve()),
        },
    }
