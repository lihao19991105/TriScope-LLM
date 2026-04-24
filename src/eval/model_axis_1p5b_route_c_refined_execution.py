"""Run refined route_c execution on the 1.5B model axis."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_portability import classify_failure_stage
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-refined-execution/v1"
ORIGINAL_ROUTE_C_DENSITY = 1.0 / 24.0


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


def materialize_refined_inputs(
    stable_materialized_inputs_dir: Path,
    refined_base_ids: list[str],
    output_dir: Path,
) -> dict[str, Any]:
    selected = set(refined_base_ids)
    output_dir.mkdir(parents=True, exist_ok=True)

    reasoning_rows = [
        row
        for row in load_jsonl(stable_materialized_inputs_dir / "reasoning_query_contracts.jsonl")
        if str(row.get("sample_id", "")) in selected
    ]
    confidence_rows = [
        row
        for row in load_jsonl(stable_materialized_inputs_dir / "confidence_query_contracts.jsonl")
        if str(row.get("sample_id", "")) in selected
    ]
    illumination_rows = [
        row
        for row in load_jsonl(stable_materialized_inputs_dir / "illumination_query_contracts.jsonl")
        if str(row.get("sample_id", "")) in selected
    ]
    labeled_rows = [
        row
        for row in load_jsonl(stable_materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl")
        if str(row.get("metadata", {}).get("base_sample_id") or row.get("metadata", {}).get("contract_metadata", {}).get("base_sample_id", "")) in selected
    ]

    write_jsonl(output_dir / "reasoning_query_contracts.jsonl", reasoning_rows)
    write_jsonl(output_dir / "confidence_query_contracts.jsonl", confidence_rows)
    write_jsonl(output_dir / "illumination_query_contracts.jsonl", illumination_rows)
    write_jsonl(output_dir / "labeled_illumination_query_contracts.jsonl", labeled_rows)
    for name in ["dataset_manifest.json", "model_manifest.json", "cutover_contract.json", "materialization_summary.json"]:
        src = stable_materialized_inputs_dir / name
        if src.exists():
            copy_artifact(src, output_dir / name)

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_base_ids": refined_base_ids,
        "selected_base_count": len(refined_base_ids),
        "reasoning_rows": len(reasoning_rows),
        "confidence_rows": len(confidence_rows),
        "illumination_rows": len(illumination_rows),
        "labeled_rows": len(labeled_rows),
    }
    write_json(output_dir / "route_c_refined_materialization_summary.json", summary)
    return summary


def extract_positive_support(dataset_path: Path) -> tuple[list[str], list[str]]:
    rows = load_jsonl(dataset_path)
    positive_rows = [row for row in rows if int(row.get("ground_truth_label", 0)) == 1]
    sample_ids = [str(row["sample_id"]) for row in positive_rows]
    base_ids = [str(row["base_sample_id"]) for row in positive_rows]
    return sample_ids, base_ids


def build_model_axis_1p5b_route_c_refined_execution(
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
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    refined_selection = load_json(route_c_refinement_dir / "route_c_refined_selection_registry.json")
    refined_summary = load_json(route_c_refinement_dir / "route_c_refined_candidate_summary.json")
    refinement_recommendation = load_json(route_c_refinement_dir / "route_c_refinement_recommendation.json")
    original_metrics = load_json(Path("outputs/model_axis_1p5b_route_c_execution/default/route_c_execution_metrics.json"))
    stable_run_summary = load_json(route_c_stable_portability_dir / "route_c_stable_portability_run_summary.json")
    if stable_run_summary.get("summary_status") != "PASS":
        raise ValueError("120 requires the stabilized route_c portability gate to pass before refined execution can start.")

    refined_base_ids = [str(item) for item in refined_selection.get("refined_base_ids", [])]
    stable_materialized_inputs_dir = route_c_stable_portability_dir / "materialized_route_c_stable_portability_inputs"
    materialized_inputs_dir = output_dir / "materialized_route_c_refined_execution_inputs"
    materialization_summary = materialize_refined_inputs(
        stable_materialized_inputs_dir=stable_materialized_inputs_dir,
        refined_base_ids=refined_base_ids,
        output_dir=materialized_inputs_dir,
    )

    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_refined",
        "selected_model_profile": "pilot_small_hf",
        "selection_registry": str((route_c_refinement_dir / "route_c_refined_selection_registry.json").resolve()),
        "selected_base_ids": refined_base_ids,
        "selected_base_count": len(refined_base_ids),
        "selected_contract_count": refined_summary.get("selected_contract_count"),
        "expected_class_balance": refined_summary.get("class_balance"),
        "why_selected": [
            "119 identified this anchor-preserving refined subset as a more density-efficient route_c candidate than the original 24-contract execution subset.",
            "It preserves the known positive anchor while trimming negative-only bases.",
        ],
    }
    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_refined",
        "execution_goal": "verify that the refined 1.5B route_c subset preserves true local execution while improving positive density over 116",
        "difference_vs_116": {
            "original_selected_contract_count": original_metrics.get("num_rows"),
            "refined_selected_contract_count": refined_summary.get("selected_contract_count"),
            "original_density": ORIGINAL_ROUTE_C_DENSITY,
            "refined_target_density": refined_summary.get("refined_positive_density"),
            "selection_strategy": refined_selection.get("strategy"),
        },
        "success_criterion": [
            "used_local_weights=true",
            "entered_model_inference=true",
            "refined execution keeps at least two classes",
            "refined execution density exceeds the original 1/24 density",
            "route_c refined logistic summary remains PASS",
        ],
        "risk_focus": [
            "The refined subset still relies on a single positive anchor.",
            "Density may improve without increasing the absolute number of positives.",
        ],
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_refined",
        "ready_run": True,
        "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        "selected_base_ids": refined_base_ids,
        "selected_contract_count": refined_summary.get("selected_contract_count"),
        "expected_class_balance": refined_summary.get("class_balance"),
        "expected_density": refined_summary.get("refined_positive_density"),
        "original_density": ORIGINAL_ROUTE_C_DENSITY,
        "recommendation_source": refinement_recommendation.get("recommended_next_step"),
        "materialization_summary": materialization_summary,
    }
    write_json(output_dir / "route_c_refined_execution_selection.json", selection)
    write_json(output_dir / "route_c_refined_execution_plan.json", plan)
    write_json(output_dir / "route_c_refined_execution_readiness_summary.json", readiness)

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
            output_dir=output_dir / "route_c_refined_execution_run",
            seed=seed,
            label_threshold=label_threshold,
            model_profile_name="pilot_small_hf",
            label_parse_mode="robust_prefix",
        )
        route_c_summary = load_json(Path(run_result["output_paths"]["summary"]))
        route_c_logistic_summary = load_json(Path(run_result["output_paths"]["logistic_summary"]))
        positive_support_sample_ids, positive_support_base_ids = extract_positive_support(
            output_dir / "route_c_refined_execution_run" / "route_c_v6_dataset.jsonl"
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
    refined_density = (float(label_1) / float(num_rows)) if num_rows > 0 else None
    density_gain_vs_original = (
        refined_density / ORIGINAL_ROUTE_C_DENSITY
        if refined_density is not None and ORIGINAL_ROUTE_C_DENSITY > 0
        else None
    )

    run_summary = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_refined",
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
        "refined_density": refined_density,
        "original_density": ORIGINAL_ROUTE_C_DENSITY,
        "density_gain_vs_original": density_gain_vs_original,
        "density_improved_vs_116": bool(refined_density is not None and refined_density > ORIGINAL_ROUTE_C_DENSITY),
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
        "density_gain_vs_original": density_gain_vs_original,
    }
    positive_support_breakdown = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_refined",
        "positive_support_sample_ids": positive_support_sample_ids,
        "positive_support_base_ids": positive_support_base_ids,
        "positive_support_count": len(positive_support_sample_ids),
        "notes": [
            "The refined execution still focuses on the same positive anchor unless additional positives emerge.",
        ],
    }
    write_json(output_dir / "route_c_refined_execution_run_summary.json", run_summary)
    write_json(output_dir / "route_c_refined_execution_metrics.json", metrics)
    write_json(output_dir / "route_c_refined_positive_support_breakdown.json", positive_support_breakdown)
    copy_artifact(route_c_refinement_dir / "route_c_refined_selection_registry.json", output_dir / "route_c_refined_selection_registry_snapshot.json")

    if route_c_summary is not None:
        copy_artifact(
            output_dir / "route_c_refined_execution_run" / "route_c_v6_summary.json",
            output_dir / "model_axis_1p5b_route_c_refined_summary.json",
        )
    if route_c_logistic_summary is not None:
        copy_artifact(
            output_dir / "route_c_refined_execution_run" / "route_c_v6_logistic_summary.json",
            output_dir / "model_axis_1p5b_route_c_refined_logistic_summary.json",
        )

    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "route_c_refined_execution_selection.json").resolve()),
            "plan": str((output_dir / "route_c_refined_execution_plan.json").resolve()),
            "readiness": str((output_dir / "route_c_refined_execution_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "route_c_refined_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "route_c_refined_execution_metrics.json").resolve()),
        },
    }
