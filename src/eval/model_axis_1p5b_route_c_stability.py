"""Confirm whether the sparse 1.5B route_c positive support is stable."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_execution import build_model_axis_1p5b_route_c_execution, load_json
from src.eval.model_axis_1p5b_route_c_portability import classify_failure_stage


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-stability/v1"


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


def extract_positive_support(dataset_path: Path) -> tuple[list[str], list[str]]:
    rows = load_jsonl(dataset_path)
    positive_rows = [row for row in rows if int(row.get("ground_truth_label", 0)) == 1]
    sample_ids = [str(row["sample_id"]) for row in positive_rows]
    base_ids = [str(row["base_sample_id"]) for row in positive_rows]
    return sample_ids, base_ids


def build_model_axis_1p5b_route_c_stability(
    route_c_execution_dir: Path,
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

    reference_run_summary = load_json(route_c_execution_dir / "route_c_execution_run_summary.json")
    reference_route_c_summary = load_json(route_c_execution_dir / "model_axis_1p5b_route_c_summary.json")
    reference_route_c_logistic = load_json(route_c_execution_dir / "model_axis_1p5b_route_c_logistic_summary.json")
    reference_dataset_path = route_c_execution_dir / "route_c_execution_run" / "route_c_v6_dataset.jsonl"
    baseline_positive_sample_ids, baseline_positive_base_ids = extract_positive_support(reference_dataset_path)

    protocol = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "protocol_name": "route_c_sparse_positive_support_confirmation_v1",
        "scope": "1p5b_route_c_sparse_stability_only",
        "design_principles": [
            "Do not reopen new model axes or dataset axes.",
            "Keep the 115 stabilized subset fixed.",
            "Only apply light seed perturbations around the existing 116 execution path.",
            "Judge stability by whether the sparse positive support remains real and usable.",
        ],
        "run_scenarios": [
            {"run_id": "run_seed42_repeat", "seed": 42, "role": "baseline_repeat"},
            {"run_id": "run_seed43_perturbation", "seed": 43, "role": "seed_perturbation_plus_1"},
            {"run_id": "run_seed44_perturbation", "seed": 44, "role": "seed_perturbation_plus_2"},
        ],
        "reference_run": {
            "execution_status": reference_run_summary.get("execution_status"),
            "class_balance": reference_run_summary.get("class_balance"),
            "positive_support_sample_ids": baseline_positive_sample_ids,
            "positive_support_base_ids": baseline_positive_base_ids,
            "logistic_status": reference_route_c_logistic.get("summary_status"),
        },
    }
    success_criteria = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "hard_requirements": [
            "Every confirmation run must keep used_local_weights=true and entered_model_inference=true.",
            "Every confirmation run must keep at least one positive contract so the run remains bi-class.",
            "Every confirmation run must keep route_c logistic summary status PASS.",
            "The baseline positive support anchor must remain present in every run.",
        ],
        "acceptable_variation": [
            "Prediction score may drift slightly across reruns.",
            "Additional positive support may appear as long as the baseline anchor is preserved.",
        ],
        "unacceptable_variation": [
            "Any rerun collapsing back to label_0 only.",
            "Any rerun losing the baseline positive support anchor.",
            "Any rerun failing before local 1.5B inference.",
        ],
        "route_b_difference": [
            "route_b stability checks broad two-class persistence; route_c stability must additionally preserve the lone positive anchor because sparsity is the core issue.",
        ],
    }
    run_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_runs": len(protocol["run_scenarios"]),
        "fixed_subset_source": str((route_c_stable_portability_dir / "materialized_route_c_stable_portability_inputs").resolve()),
        "fixed_label_parse_mode": "robust_prefix",
        "fixed_label_threshold": label_threshold,
        "baseline_positive_support_sample_ids": baseline_positive_sample_ids,
        "scenarios": protocol["run_scenarios"],
    }
    write_json(output_dir / "route_c_stability_protocol.json", protocol)
    write_json(output_dir / "route_c_stability_success_criteria.json", success_criteria)
    write_json(output_dir / "route_c_stability_run_plan.json", run_plan)

    results: list[dict[str, Any]] = []
    registry_runs: list[dict[str, Any]] = []
    for scenario in protocol["run_scenarios"]:
        run_id = str(scenario["run_id"])
        run_dir = output_dir / "runs" / run_id
        try:
            result = build_model_axis_1p5b_route_c_execution(
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
            route_c_summary = load_json(run_dir / "model_axis_1p5b_route_c_summary.json")
            route_c_logistic_summary = load_json(run_dir / "model_axis_1p5b_route_c_logistic_summary.json")
            positive_sample_ids, positive_base_ids = extract_positive_support(run_dir / "route_c_execution_run" / "route_c_v6_dataset.jsonl")
            class_balance = route_c_summary.get("class_balance", {})
            has_two_classes = int(class_balance.get("label_0", 0) or 0) > 0 and int(class_balance.get("label_1", 0) or 0) > 0
            logistic_pass = route_c_logistic_summary.get("summary_status") == "PASS"
            baseline_anchor_preserved = all(sample_id in positive_sample_ids for sample_id in baseline_positive_sample_ids)
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
                "positive_support_sample_ids": "|".join(positive_sample_ids),
                "positive_support_base_ids": "|".join(positive_base_ids),
                "baseline_anchor_preserved": baseline_anchor_preserved,
                "logistic_status": route_c_logistic_summary.get("summary_status"),
                "logistic_pass": logistic_pass,
                "mean_prediction_score": run_metrics.get("mean_prediction_score"),
                "failure_stage": None,
                "failure_reason": None,
            }
            results.append(row)
            registry_runs.append(
                {
                    "run_id": run_id,
                    "scenario": scenario,
                    "run_dir": str(run_dir.resolve()),
                    "run_summary": str((run_dir / "route_c_execution_run_summary.json").resolve()),
                    "metrics": str((run_dir / "route_c_execution_metrics.json").resolve()),
                    "route_c_summary": str((run_dir / "model_axis_1p5b_route_c_summary.json").resolve()),
                    "route_c_logistic_summary": str((run_dir / "model_axis_1p5b_route_c_logistic_summary.json").resolve()),
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
                    "positive_support_sample_ids": "",
                    "positive_support_base_ids": "",
                    "baseline_anchor_preserved": False,
                    "logistic_status": "FAIL",
                    "logistic_pass": False,
                    "mean_prediction_score": None,
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
    all_positive_support_present = all(int(row["label_1"]) > 0 for row in results)
    baseline_positive_preserved_all_runs = all(bool(row["baseline_anchor_preserved"]) for row in results)
    stability_established = all_two_classes and all_logistic_pass and all_positive_support_present and baseline_positive_preserved_all_runs
    summary = {
        "summary_status": "PASS" if all(row["summary_status"] != "FAIL" for row in results) else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "total_runs": len(results),
        "all_two_classes": all_two_classes,
        "all_logistic_pass": all_logistic_pass,
        "all_positive_support_present": all_positive_support_present,
        "baseline_positive_sample_ids": baseline_positive_sample_ids,
        "baseline_positive_preserved_all_runs": baseline_positive_preserved_all_runs,
        "stability_established": stability_established,
        "stability_characterization": "stable_but_sparse" if stability_established else "unstable_sparse",
        "reference_class_balance": reference_route_c_summary.get("class_balance"),
        "reference_positive_support_base_ids": baseline_positive_base_ids,
        "notes": [
            "Route_c stability is stricter than route_b stability because the current route_c result hinges on a single positive support anchor.",
            "The goal is to decide whether the sparse positive signal is repeatable enough to justify refinement work.",
        ],
    }

    write_json(output_dir / "route_c_stability_run_registry.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "runs": registry_runs})
    write_jsonl(output_dir / "route_c_stability_results.jsonl", results)
    write_json(output_dir / "route_c_stability_summary.json", summary)
    write_csv(output_dir / "route_c_stability_comparison.csv", results)

    return {
        "summary": summary,
        "output_paths": {
            "registry": str((output_dir / "route_c_stability_run_registry.json").resolve()),
            "results": str((output_dir / "route_c_stability_results.jsonl").resolve()),
            "summary": str((output_dir / "route_c_stability_summary.json").resolve()),
            "comparison": str((output_dir / "route_c_stability_comparison.csv").resolve()),
        },
    }
