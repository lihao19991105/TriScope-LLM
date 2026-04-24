"""Confirm refined route_c execution stability on the 1.5B model axis."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import (
    ORIGINAL_ROUTE_C_DENSITY,
    build_model_axis_1p5b_route_c_refined_execution,
    load_json,
    load_jsonl,
)
from src.eval.model_axis_1p5b_route_c_portability import classify_failure_stage


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-refined-stability/v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("Expected at least one CSV row.")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def extract_positive_support(dataset_path: Path) -> tuple[list[str], list[str]]:
    rows = load_jsonl(dataset_path)
    positive_rows = [row for row in rows if int(row.get("ground_truth_label", 0)) == 1]
    sample_ids = [str(row["sample_id"]) for row in positive_rows]
    base_ids = [str(row["base_sample_id"]) for row in positive_rows]
    return sample_ids, base_ids


def build_model_axis_1p5b_route_c_refined_stability(
    route_c_refined_execution_dir: Path,
    route_c_refinement_dir: Path,
    route_c_stable_portability_dir: Path,
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

    reference_run_summary = load_json(route_c_refined_execution_dir / "route_c_refined_execution_run_summary.json")
    reference_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    if reference_run_summary.get("summary_status") != "PASS":
        raise ValueError("121 requires 120 to pass before refined stability can start.")
    reference_positive_sample_ids, reference_positive_base_ids = extract_positive_support(
        route_c_refined_execution_dir / "route_c_refined_execution_run" / "route_c_v6_dataset.jsonl"
    )
    reference_refined_density = float(reference_metrics.get("refined_density", 0.0) or 0.0)

    protocol = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "protocol_name": "route_c_refined_density_confirmation_v1",
        "scope": "1p5b_route_c_refined_only",
        "design_principles": [
            "Keep the refined subset fixed.",
            "Do not reopen new route_c search space during stability confirmation.",
            "Judge success by whether refined density stays above the original 1/24 baseline and preserves the positive anchor.",
        ],
        "run_scenarios": [
            {"run_id": "run_seed42_repeat", "seed": 42, "role": "baseline_repeat"},
            {"run_id": "run_seed43_perturbation", "seed": 43, "role": "seed_perturbation_plus_1"},
            {"run_id": "run_seed44_perturbation", "seed": 44, "role": "seed_perturbation_plus_2"},
        ],
        "reference_run": {
            "execution_status": reference_run_summary.get("execution_status"),
            "class_balance": reference_run_summary.get("class_balance"),
            "refined_density": reference_refined_density,
            "positive_support_sample_ids": reference_positive_sample_ids,
            "positive_support_base_ids": reference_positive_base_ids,
        },
    }
    success_criteria = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "hard_requirements": [
            "Every rerun must keep used_local_weights=true and entered_model_inference=true.",
            "Every rerun must keep at least two classes.",
            "Every rerun must keep route_c refined logistic summary PASS.",
            "Every rerun must keep refined_density > original 1/24 density.",
            "The refined positive anchor must remain present in every rerun.",
        ],
        "acceptable_variation": [
            "The exact positive-support set may expand, as long as the refined positive anchor is preserved and density remains improved.",
        ],
        "unacceptable_variation": [
            "Refined density falling back to the original baseline or below it.",
            "Loss of the refined positive anchor.",
            "Any rerun collapsing back to one class.",
        ],
    }
    run_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_runs": len(protocol["run_scenarios"]),
        "reference_refined_density": reference_refined_density,
        "original_density_baseline": ORIGINAL_ROUTE_C_DENSITY,
        "refined_selection_registry": str((route_c_refinement_dir / "route_c_refined_selection_registry.json").resolve()),
        "scenarios": protocol["run_scenarios"],
    }
    write_json(output_dir / "route_c_refined_stability_protocol.json", protocol)
    write_json(output_dir / "route_c_refined_stability_success_criteria.json", success_criteria)
    write_json(output_dir / "route_c_refined_stability_run_plan.json", run_plan)

    results: list[dict[str, Any]] = []
    registry_runs: list[dict[str, Any]] = []
    for scenario in protocol["run_scenarios"]:
        run_id = str(scenario["run_id"])
        run_dir = output_dir / "runs" / run_id
        try:
            result = build_model_axis_1p5b_route_c_refined_execution(
                route_c_refinement_dir=route_c_refinement_dir,
                route_c_stable_portability_dir=route_c_stable_portability_dir,
                models_config_path=models_config_path,
                reasoning_config_path=reasoning_config_path,
                confidence_config_path=confidence_config_path,
                illumination_config_path=illumination_config_path,
                reasoning_prompt_dir=reasoning_prompt_dir,
                confidence_prompt_dir=confidence_prompt_dir,
                illumination_prompt_dir=illumination_prompt_dir,
                output_dir=run_dir,
                seed=int(scenario["seed"]),
                label_threshold=label_threshold,
            )
            run_summary = load_json(Path(result["output_paths"]["run_summary"]))
            run_metrics = load_json(Path(result["output_paths"]["metrics"]))
            route_c_logistic_summary = load_json(run_dir / "model_axis_1p5b_route_c_refined_logistic_summary.json")
            positive_sample_ids, positive_base_ids = extract_positive_support(run_dir / "route_c_refined_execution_run" / "route_c_v6_dataset.jsonl")
            class_balance = run_summary.get("class_balance", {})
            has_two_classes = int(class_balance.get("label_0", 0) or 0) > 0 and int(class_balance.get("label_1", 0) or 0) > 0
            refined_density = float(run_metrics.get("refined_density", 0.0) or 0.0)
            row = {
                "run_id": run_id,
                "seed": int(scenario["seed"]),
                "role": str(scenario["role"]),
                "summary_status": run_summary.get("summary_status"),
                "execution_status": run_summary.get("execution_status"),
                "used_local_weights": bool(run_summary.get("used_local_weights")),
                "entered_model_inference": bool(run_summary.get("entered_model_inference")),
                "label_0": int(class_balance.get("label_0", 0) or 0),
                "label_1": int(class_balance.get("label_1", 0) or 0),
                "has_two_classes": has_two_classes,
                "refined_density": refined_density,
                "density_improved_vs_116": bool(refined_density > ORIGINAL_ROUTE_C_DENSITY),
                "positive_support_sample_ids": "|".join(positive_sample_ids),
                "positive_support_base_ids": "|".join(positive_base_ids),
                "reference_anchor_preserved": all(sample_id in positive_sample_ids for sample_id in reference_positive_sample_ids),
                "logistic_status": route_c_logistic_summary.get("summary_status"),
                "logistic_pass": route_c_logistic_summary.get("summary_status") == "PASS",
                "failure_stage": None,
                "failure_reason": None,
            }
            results.append(row)
            registry_runs.append(
                {
                    "run_id": run_id,
                    "scenario": scenario,
                    "run_dir": str(run_dir.resolve()),
                    "run_summary": str((run_dir / "route_c_refined_execution_run_summary.json").resolve()),
                    "metrics": str((run_dir / "route_c_refined_execution_metrics.json").resolve()),
                    "route_c_refined_summary": str((run_dir / "model_axis_1p5b_route_c_refined_summary.json").resolve()),
                    "route_c_refined_logistic_summary": str((run_dir / "model_axis_1p5b_route_c_refined_logistic_summary.json").resolve()),
                }
            )
        except Exception as exc:
            error_message = str(exc)
            results.append(
                {
                    "run_id": run_id,
                    "seed": int(scenario["seed"]),
                    "role": str(scenario["role"]),
                    "summary_status": "FAIL",
                    "execution_status": "PARTIAL",
                    "used_local_weights": False,
                    "entered_model_inference": False,
                    "label_0": 0,
                    "label_1": 0,
                    "has_two_classes": False,
                    "refined_density": 0.0,
                    "density_improved_vs_116": False,
                    "positive_support_sample_ids": "",
                    "positive_support_base_ids": "",
                    "reference_anchor_preserved": False,
                    "logistic_status": "FAIL",
                    "logistic_pass": False,
                    "failure_stage": classify_failure_stage(error_message),
                    "failure_reason": error_message,
                }
            )
            registry_runs.append(
                {
                    "run_id": run_id,
                    "scenario": scenario,
                    "run_dir": str(run_dir.resolve()),
                    "failure_reason": error_message,
                    "failure_stage": classify_failure_stage(error_message),
                }
            )

    all_two_classes = all(bool(row["has_two_classes"]) for row in results)
    all_logistic_pass = all(bool(row["logistic_pass"]) for row in results)
    refined_density_preserved = all(bool(row["density_improved_vs_116"]) for row in results)
    reference_anchor_preserved_all_runs = all(bool(row["reference_anchor_preserved"]) for row in results)
    stability_established = all_two_classes and all_logistic_pass and refined_density_preserved and reference_anchor_preserved_all_runs
    summary = {
        "summary_status": "PASS" if all(row["summary_status"] != "FAIL" for row in results) else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_refined",
        "total_runs": len(results),
        "all_two_classes": all_two_classes,
        "all_logistic_pass": all_logistic_pass,
        "refined_density_preserved_all_runs": refined_density_preserved,
        "reference_anchor_preserved_all_runs": reference_anchor_preserved_all_runs,
        "stability_established": stability_established,
        "stability_characterization": "better_and_stable" if stability_established else "better_but_fragile",
        "reference_refined_density": reference_refined_density,
        "original_density_baseline": ORIGINAL_ROUTE_C_DENSITY,
        "notes": [
            "Refined stability only counts as success if the density improvement over the original 116 baseline remains present under reruns.",
        ],
    }

    write_json(output_dir / "route_c_refined_stability_run_registry.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "runs": registry_runs})
    write_jsonl(output_dir / "route_c_refined_stability_results.jsonl", results)
    write_json(output_dir / "route_c_refined_stability_summary.json", summary)
    write_csv(output_dir / "route_c_refined_stability_comparison.csv", results)

    return {
        "summary": summary,
        "output_paths": {
            "registry": str((output_dir / "route_c_refined_stability_run_registry.json").resolve()),
            "results": str((output_dir / "route_c_refined_stability_results.jsonl").resolve()),
            "summary": str((output_dir / "route_c_refined_stability_summary.json").resolve()),
            "comparison": str((output_dir / "route_c_refined_stability_comparison.csv").resolve()),
        },
    }
