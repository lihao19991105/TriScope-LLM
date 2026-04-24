"""Minimal 1.5B model-axis execution builder."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

from src.eval.experiment_bootstrap import evaluate_model_profile, load_yaml
from src.eval.rerun_route_b_on_labeled_split_v6 import run_route_b_v6


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-execution/v1"


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


def choose_sample_ids(
    reasoning_rows: list[dict[str, Any]],
    reference_route_b_rows: list[dict[str, Any]],
    target_budget: int,
) -> tuple[list[str], dict[str, Any]]:
    reasoning_ids = [str(row["sample_id"]) for row in reasoning_rows]
    reference_by_id = {str(row["sample_id"]): row for row in reference_route_b_rows}
    positives = [
        sample_id
        for sample_id in reasoning_ids
        if int(reference_by_id.get(sample_id, {}).get("ground_truth_label", 0)) == 1
    ]
    negatives = [
        sample_id
        for sample_id in reasoning_ids
        if int(reference_by_id.get(sample_id, {}).get("ground_truth_label", 0)) == 0
    ]
    selected_ids = positives[: min(len(positives), target_budget)]
    remaining_budget = max(0, target_budget - len(selected_ids))
    selected_ids.extend(negatives[:remaining_budget])
    if len(selected_ids) < min(target_budget, len(reasoning_ids)):
        selected_ids.extend(
            sample_id
            for sample_id in reasoning_ids
            if sample_id not in set(selected_ids)
        )
        selected_ids = selected_ids[: min(target_budget, len(reasoning_ids))]
    stats = {
        "requested_budget": target_budget,
        "realized_budget": len(selected_ids),
        "selected_positive_reference_count": sum(
            1 for sample_id in selected_ids if int(reference_by_id.get(sample_id, {}).get("ground_truth_label", 0)) == 1
        ),
        "selected_negative_reference_count": sum(
            1 for sample_id in selected_ids if int(reference_by_id.get(sample_id, {}).get("ground_truth_label", 0)) == 0
        ),
        "selection_strategy": "prioritize historically difficult route_b samples from the lightweight baseline, then fill with additional negatives",
    }
    return selected_ids, stats


def filter_rows(rows: list[dict[str, Any]], selected_ids: list[str]) -> list[dict[str, Any]]:
    selected = set(selected_ids)
    return [row for row in rows if str(row.get("sample_id")) in selected]


def materialize_minimal_inputs(
    reasoning_query_file: Path,
    confidence_query_file: Path,
    illumination_query_file: Path,
    pilot_slice_file: Path,
    reference_route_b_dataset_path: Path,
    output_dir: Path,
    target_budget: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reasoning_rows = load_jsonl(reasoning_query_file)
    confidence_rows = load_jsonl(confidence_query_file)
    illumination_rows = load_jsonl(illumination_query_file)
    pilot_slice_rows = load_jsonl(pilot_slice_file)
    reference_rows = load_jsonl(reference_route_b_dataset_path)

    selected_ids, selection_stats = choose_sample_ids(
        reasoning_rows=reasoning_rows,
        reference_route_b_rows=reference_rows,
        target_budget=target_budget,
    )
    selected_reasoning = filter_rows(reasoning_rows, selected_ids)
    selected_confidence = filter_rows(confidence_rows, selected_ids)
    selected_illumination = filter_rows(illumination_rows, selected_ids)
    selected_slice = filter_rows(pilot_slice_rows, selected_ids)

    write_jsonl(output_dir / "reasoning_query_contracts.jsonl", selected_reasoning)
    write_jsonl(output_dir / "confidence_query_contracts.jsonl", selected_confidence)
    write_jsonl(output_dir / "illumination_query_contracts.jsonl", selected_illumination)
    write_jsonl(output_dir / "csqa_reasoning_pilot_slice.jsonl", selected_slice)
    write_json(
        output_dir / "materialization_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "selected_sample_ids": selected_ids,
            "selection_stats": selection_stats,
            "reasoning_rows": len(selected_reasoning),
            "confidence_rows": len(selected_confidence),
            "illumination_rows": len(selected_illumination),
            "pilot_slice_rows": len(selected_slice),
        },
    )
    return {
        "selected_sample_ids": selected_ids,
        "selection_stats": selection_stats,
        "reasoning_rows": len(selected_reasoning),
        "confidence_rows": len(selected_confidence),
        "illumination_rows": len(selected_illumination),
        "pilot_slice_rows": len(selected_slice),
    }


def build_model_axis_1p5b_execution(
    dry_run_summary_path: Path,
    execution_gate_path: Path,
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
    if dry_run_summary.get("summary_status") != "PASS":
        raise ValueError("107 requires a PASS 106 dry-run before execution.")
    if execution_gate.get("allow_107_execution") is not True:
        raise ValueError("107 requires allow_107_execution = true.")

    model_config = load_yaml(models_config_path)
    selected_profile = evaluate_model_profile("pilot_small_hf", model_config["pilot_small_hf"])
    if selected_profile["availability_status"] != "available_local":
        raise ValueError("pilot_small_hf must be available_local before 107 can execute.")

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
            raise ValueError(f"107 input not found: `{path}`.")

    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "selected_local_path": selected_profile["local_path"],
        "why_selected": [
            "route_b was already established as the minimal executable candidate in 105/106.",
            "route_b reuses the repository's existing more-natural supervision proxy execution path without needing the full matrix bundle.",
        ],
        "why_not_route_c": "route_c is still a valid next step, but route_b is the smaller first proof that the matrix contract can move onto a 1.5B local model.",
        "why_not_fusion_summary": "fusion_summary depends on route evidence and is therefore not a smaller first execution step than route_b.",
        "target_budget": target_budget,
    }
    write_json(output_dir / "model_axis_1p5b_execution_selection.json", selection)

    execution_inputs_dir = output_dir / "materialized_model_axis_1p5b_execution_inputs"
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
        "execution_mode": "route_b_minimal_real_local_execution",
        "seed": seed,
        "target_budget": target_budget,
        "selected_sample_count": selection_stats["reasoning_rows"],
        "selected_positive_reference_count": selection_stats["selection_stats"]["selected_positive_reference_count"],
        "selected_negative_reference_count": selection_stats["selection_stats"]["selected_negative_reference_count"],
        "fallback_rule": "if the minimal balanced subset still produces a single-class labeled dataset, rerun route_b on the full 70-row contract slice",
    }
    execution_readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "ready_local": True,
        "ready_run": True,
        "selected_model_profile": "pilot_small_hf",
        "selected_local_path": selected_profile["local_path"],
        "selected_sample_count": selection_stats["reasoning_rows"],
        "materialized_inputs_dir": str(execution_inputs_dir.resolve()),
    }
    write_json(output_dir / "model_axis_1p5b_execution_plan.json", execution_plan)
    write_json(output_dir / "model_axis_1p5b_execution_readiness_summary.json", execution_readiness)

    route_b_output_dir = output_dir / "model_axis_1p5b_execution_outputs" / "route_b"
    fallback_used = False
    fallback_reason = None
    try:
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
        )
    except ValueError as exc:
        if "at least two classes" not in str(exc):
            raise
        fallback_used = True
        fallback_reason = str(exc)
        for name in [
            "reasoning_query_contracts.jsonl",
            "confidence_query_contracts.jsonl",
            "illumination_query_contracts.jsonl",
            "csqa_reasoning_pilot_slice.jsonl",
        ]:
            source_path = (
                dry_run_materialized_inputs_dir / name
                if name != "csqa_reasoning_pilot_slice.jsonl"
                else reference_route_b_slice_path
            )
            copy_artifact(source_path, execution_inputs_dir / name)
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
        )

    route_b_summary = load_json(route_b_output_dir / "route_b_v6_summary.json")
    route_b_logistic_summary = load_json(route_b_output_dir / "route_b_v6_logistic_summary.json")
    route_b_run_summary = load_json(route_b_output_dir / "route_b_v6_run_summary.json")

    copy_artifact(route_b_output_dir / "route_b_v6_summary.json", output_dir / "model_axis_1p5b_route_b_summary.json")
    copy_artifact(
        route_b_output_dir / "route_b_v6_logistic_summary.json",
        output_dir / "model_axis_1p5b_route_b_logistic_summary.json",
    )
    copy_artifact(
        route_b_output_dir / "route_b_v6_run_summary.json",
        output_dir / "model_axis_1p5b_route_b_run_summary.json",
    )

    run_summary_status = route_b_run_summary.get("summary_status", "PASS")
    execution_status = str(route_b_run_summary.get("execution_status", "FULL_EXECUTE"))

    registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "artifacts": {
            "selection": str((output_dir / "model_axis_1p5b_execution_selection.json").resolve()),
            "plan": str((output_dir / "model_axis_1p5b_execution_plan.json").resolve()),
            "readiness": str((output_dir / "model_axis_1p5b_execution_readiness_summary.json").resolve()),
            "route_b_summary": str((output_dir / "model_axis_1p5b_route_b_summary.json").resolve()),
            "route_b_logistic_summary": str((output_dir / "model_axis_1p5b_route_b_logistic_summary.json").resolve()),
            "route_b_run_summary": str((output_dir / "model_axis_1p5b_route_b_run_summary.json").resolve()),
            "route_b_output_dir": str(route_b_output_dir.resolve()),
        },
    }
    metrics = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "selected_local_path": selected_profile["local_path"],
        "used_local_weights": True,
        "entered_model_inference": True,
        "execution_status": execution_status if not fallback_used else f"{execution_status}_WITH_FALLBACK",
        "fallback_used": fallback_used,
        "num_rows": route_b_summary["num_rows"],
        "num_base_samples": route_b_summary["num_base_samples"],
        "mean_prediction_score": route_b_logistic_summary.get("mean_prediction_score"),
        "num_positive_predictions": route_b_logistic_summary.get("num_positive_predictions", 0),
    }
    run_summary = {
        "summary_status": run_summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_b",
        "selected_model_profile": "pilot_small_hf",
        "selected_model_id": selected_profile["model_id"],
        "selected_local_path": selected_profile["local_path"],
        "used_local_weights": True,
        "entered_model_inference": True,
        "execution_status": metrics["execution_status"],
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "selected_query_count": selection_stats["reasoning_rows"],
        "executed_layers": ["route_b"],
        "logistic_blocked_reason": route_b_run_summary.get("logistic_blocked_reason"),
        "notes": [
            "This is the first true 1.5B local model-axis execution.",
            "It reuses the existing route_b_v6 execution stack, but swaps the model profile to pilot_small_hf.",
            "The route remains a more-natural supervision proxy, not benchmark ground truth.",
        ],
    }
    preview_rows = [
        {
            "selected_cell": "route_b",
            "selected_model_profile": "pilot_small_hf",
            "summary_path": str((output_dir / "model_axis_1p5b_route_b_summary.json").resolve()),
            "num_rows": route_b_summary["num_rows"],
            "mean_prediction_score": route_b_logistic_summary["mean_prediction_score"],
        }
    ]
    write_json(output_dir / "model_axis_1p5b_execution_registry.json", registry)
    write_json(output_dir / "model_axis_1p5b_execution_metrics.json", metrics)
    write_json(output_dir / "model_axis_1p5b_execution_run_summary.json", run_summary)
    write_csv(
        output_dir / "model_axis_1p5b_cell_metrics.csv",
        [
            {
                "selected_cell": "route_b",
                "selected_model_profile": "pilot_small_hf",
                "num_rows": route_b_summary["num_rows"],
                "num_base_samples": route_b_summary["num_base_samples"],
                "mean_prediction_score": route_b_logistic_summary["mean_prediction_score"],
                "num_positive_predictions": route_b_logistic_summary["num_positive_predictions"],
                "fallback_used": fallback_used,
            }
        ],
    )
    write_jsonl(output_dir / "model_axis_1p5b_execution_preview.jsonl", preview_rows)
    return {
        "run_summary": run_summary,
        "output_paths": {
            "selection": str((output_dir / "model_axis_1p5b_execution_selection.json").resolve()),
            "plan": str((output_dir / "model_axis_1p5b_execution_plan.json").resolve()),
            "readiness": str((output_dir / "model_axis_1p5b_execution_readiness_summary.json").resolve()),
            "registry": str((output_dir / "model_axis_1p5b_execution_registry.json").resolve()),
            "run_summary": str((output_dir / "model_axis_1p5b_execution_run_summary.json").resolve()),
            "metrics": str((output_dir / "model_axis_1p5b_execution_metrics.json").resolve()),
        },
    }
