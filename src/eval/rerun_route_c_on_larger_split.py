"""Rerun route C on the larger labeled split substrate."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.features.confidence_features import extract_confidence_features
from src.features.illumination_features import extract_illumination_features
from src.features.reasoning_features import extract_reasoning_features
from src.fusion.benchmark_truth_leaning_label import (
    build_benchmark_truth_leaning_dataset,
    run_benchmark_truth_leaning_logistic,
)
from src.fusion.feature_alignment import build_fusion_dataset
from src.probes.confidence_probe import run_confidence_probe
from src.probes.illumination_probe import run_illumination_probe
from src.probes.reasoning_probe import run_reasoning_probe


SCHEMA_VERSION = "triscopellm/rerun-route-c-on-larger-split/v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def copy_artifact(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def count_jsonl_rows(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def materialize_larger_split_route_c(
    larger_inputs_dir: Path,
    recommendation_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    recommendation = load_json(recommendation_path)
    if recommendation.get("recommended_next_step") != "rerun_route_C_on_larger_split":
        raise ValueError(
            "035 expects `recommended_next_step` to be `rerun_route_C_on_larger_split`."
        )

    required_inputs = [
        larger_inputs_dir / "reasoning_query_contracts.jsonl",
        larger_inputs_dir / "confidence_query_contracts.jsonl",
        larger_inputs_dir / "illumination_query_contracts.jsonl",
        larger_inputs_dir / "labeled_illumination_query_contracts.jsonl",
        larger_inputs_dir / "csqa_reasoning_pilot_slice.jsonl",
    ]
    for path in required_inputs:
        if not path.is_file():
            raise ValueError(f"Larger-split route C input not found: `{path}`.")

    materialized_inputs_dir = output_dir / "materialized_larger_split_route_c_inputs"
    materialized_inputs_dir.mkdir(parents=True, exist_ok=True)
    for src in required_inputs:
        copy_artifact(src, materialized_inputs_dir / src.name)

    reasoning_rows = count_jsonl_rows(materialized_inputs_dir / "reasoning_query_contracts.jsonl")
    confidence_rows = count_jsonl_rows(materialized_inputs_dir / "confidence_query_contracts.jsonl")
    illumination_rows = count_jsonl_rows(materialized_inputs_dir / "illumination_query_contracts.jsonl")
    labeled_illumination_rows = count_jsonl_rows(materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl")

    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "C",
        "route_name": "benchmark_truth_leaning_supervision_proxy",
        "chosen_dataset_substrate": "larger_csqa_reasoning_pilot_local",
        "selected_from": str(recommendation_path.resolve()),
        "success_criterion": [
            "materialize route C on the 20-row larger split",
            "produce a non-empty contract-level benchmark-truth-leaning dataset",
            "run larger-split route C logistic bootstrap",
        ],
        "known_risks": [
            "Still benchmark-truth-leaning proxy supervision, not benchmark ground truth.",
            "Still tied to the local curated larger split and pilot_distilgpt2_hf.",
        ],
    }
    label_definition = {
        "schema_version": SCHEMA_VERSION,
        "label_name": "task_answer_incorrect_label",
        "label_source": "labeled_illumination_query_answer_correctness",
        "label_scope": "benchmark_truth_leaning_supervision_proxy",
        "alignment_key": "base_sample_id+contract_variant",
        "row_expansion_rule": "each larger-split base sample emits control/targeted contract rows through labeled illumination contracts",
        "label_limitations": [
            "Still not benchmark ground truth.",
            "Reasoning and confidence remain projected from base-sample fusion rows.",
            "Current substrate is still local and curated.",
        ],
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "C",
        "ready_to_run": True,
        "larger_inputs_dir": str(larger_inputs_dir.resolve()),
        "query_contract_counts": {
            "reasoning": reasoning_rows,
            "confidence": confidence_rows,
            "illumination": illumination_rows,
            "labeled_illumination": labeled_illumination_rows,
        },
        "expected_row_capacity": {
            "larger_real_pilot_alignment_rows": reasoning_rows,
            "larger_split_route_c_rows": labeled_illumination_rows,
        },
        "notes": [
            "This rerun keeps route C's truth-leaning supervision semantics while moving it onto the larger shared substrate.",
            "It is the symmetric counterpart to 033's larger-split route-B rerun.",
        ],
    }

    write_json(output_dir / "larger_split_route_c_plan.json", plan)
    write_json(output_dir / "larger_split_route_c_label_definition.json", label_definition)
    write_json(output_dir / "larger_split_route_c_readiness_summary.json", readiness_summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "larger_inputs_dir": str(larger_inputs_dir.resolve()),
            "recommendation_path": str(recommendation_path.resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        },
    )
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM larger-split route C materialization",
                "chosen_route=C",
                f"larger_inputs_dir={larger_inputs_dir.resolve()}",
                f"materialized_inputs_dir={materialized_inputs_dir.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "plan": plan,
        "label_definition": label_definition,
        "readiness_summary": readiness_summary,
        "output_paths": {
            "plan": str((output_dir / "larger_split_route_c_plan.json").resolve()),
            "label_definition": str((output_dir / "larger_split_route_c_label_definition.json").resolve()),
            "readiness_summary": str((output_dir / "larger_split_route_c_readiness_summary.json").resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }


def run_larger_split_route_c(
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    reasoning_prompt_dir: Path,
    confidence_prompt_dir: Path,
    illumination_prompt_dir: Path,
    larger_inputs_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    reasoning_query_file = larger_inputs_dir / "reasoning_query_contracts.jsonl"
    confidence_query_file = larger_inputs_dir / "confidence_query_contracts.jsonl"
    illumination_query_file = larger_inputs_dir / "illumination_query_contracts.jsonl"
    labeled_illumination_query_file = larger_inputs_dir / "labeled_illumination_query_contracts.jsonl"

    larger_budget = count_jsonl_rows(reasoning_query_file)
    if larger_budget <= 0:
        raise ValueError("Larger-split route C requires non-empty reasoning query contracts.")

    reasoning_dir = output_dir / "larger_reasoning"
    confidence_dir = output_dir / "larger_confidence"
    illumination_dir = output_dir / "larger_illumination"
    labeled_illumination_dir = output_dir / "larger_labeled_illumination"

    reasoning_probe = run_reasoning_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        reasoning_config_path=reasoning_config_path,
        reasoning_profile_name="default",
        prompt_dir=reasoning_prompt_dir,
        output_dir=reasoning_dir / "reasoning_probe",
        dataset_manifest=None,
        query_file=reasoning_query_file,
        query_budget_override=larger_budget,
        trigger_type_override="none",
        target_type_override="multiple_choice_correct_option",
        seed=seed,
        dry_run=False,
        smoke_mode=False,
    )
    reasoning_features = extract_reasoning_features(
        raw_results_path=reasoning_dir / "reasoning_probe" / "raw_results.jsonl",
        summary_json_path=reasoning_dir / "reasoning_probe" / "summary.json",
        config_snapshot_path=reasoning_dir / "reasoning_probe" / "config_snapshot.json",
        output_dir=reasoning_dir / "reasoning_probe" / "features",
        run_id="larger_route_c_reasoning",
    )
    write_json(
        reasoning_dir / "larger_reasoning_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "reasoning",
            "target_budget": larger_budget,
            "probe_summary": reasoning_probe["summary"],
            "feature_summary": reasoning_features["feature_summary"],
        },
    )

    confidence_probe = run_confidence_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        confidence_config_path=confidence_config_path,
        confidence_profile_name="pilot_local",
        prompt_dir=confidence_prompt_dir,
        output_dir=confidence_dir / "confidence_probe",
        dataset_manifest=None,
        query_file=confidence_query_file,
        query_budget_override=larger_budget,
        trigger_type_override="none",
        target_type_override="multiple_choice_correct_option",
        seed=seed,
        dry_run=False,
        smoke_mode=False,
    )
    confidence_features = extract_confidence_features(
        raw_results_path=confidence_dir / "confidence_probe" / "raw_results.jsonl",
        summary_json_path=confidence_dir / "confidence_probe" / "summary.json",
        config_snapshot_path=confidence_dir / "confidence_probe" / "config_snapshot.json",
        output_dir=confidence_dir / "confidence_probe" / "features",
        run_id="larger_route_c_confidence",
        high_confidence_threshold=0.10,
    )
    write_json(
        confidence_dir / "larger_confidence_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "confidence",
            "target_budget": larger_budget,
            "probe_summary": confidence_probe["summary"],
            "feature_summary": confidence_features["feature_summary"],
        },
    )

    illumination_probe = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        illumination_config_path=illumination_config_path,
        illumination_profile_name="pilot_local",
        prompt_dir=illumination_prompt_dir,
        output_dir=illumination_dir / "illumination_probe",
        dataset_manifest=None,
        query_file=illumination_query_file,
        alpha_override=None,
        query_budget_override=larger_budget,
        trigger_type_override="targeted_icl_demo",
        target_type_override="forced_option_label",
        seed=seed,
        dry_run=False,
        smoke_mode=False,
    )
    illumination_features = extract_illumination_features(
        raw_results_path=illumination_dir / "illumination_probe" / "raw_results.jsonl",
        summary_json_path=illumination_dir / "illumination_probe" / "summary.json",
        config_snapshot_path=illumination_dir / "illumination_probe" / "config_snapshot.json",
        output_dir=illumination_dir / "illumination_probe" / "features",
        run_id="larger_route_c_illumination",
    )
    write_json(
        illumination_dir / "larger_illumination_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "illumination",
            "target_budget": larger_budget,
            "probe_summary": illumination_probe["summary"],
            "feature_summary": illumination_features["feature_summary"],
        },
    )

    labeled_illumination_budget = count_jsonl_rows(labeled_illumination_query_file)
    labeled_illumination_probe = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        illumination_config_path=illumination_config_path,
        illumination_profile_name="labeled_bootstrap",
        prompt_dir=illumination_prompt_dir,
        output_dir=labeled_illumination_dir / "illumination_probe",
        dataset_manifest=None,
        query_file=labeled_illumination_query_file,
        alpha_override=0.5,
        query_budget_override=labeled_illumination_budget,
        trigger_type_override=None,
        target_type_override="controlled_targeted_icl_label",
        seed=seed,
        dry_run=False,
        smoke_mode=False,
    )
    labeled_illumination_features = extract_illumination_features(
        raw_results_path=labeled_illumination_dir / "illumination_probe" / "raw_results.jsonl",
        summary_json_path=labeled_illumination_dir / "illumination_probe" / "summary.json",
        config_snapshot_path=labeled_illumination_dir / "illumination_probe" / "config_snapshot.json",
        output_dir=labeled_illumination_dir / "illumination_probe" / "features",
        run_id="larger_route_c_labeled_illumination",
    )
    write_json(
        labeled_illumination_dir / "larger_labeled_illumination_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "labeled_illumination",
            "target_budget": labeled_illumination_budget,
            "probe_summary": labeled_illumination_probe["summary"],
            "feature_summary": labeled_illumination_features["feature_summary"],
        },
    )

    fusion_result = build_fusion_dataset(
        illumination_features_path=illumination_dir / "illumination_probe" / "features" / "prompt_level_features.jsonl",
        reasoning_features_path=reasoning_dir / "reasoning_probe" / "features" / "reasoning_prompt_level_features.jsonl",
        confidence_features_path=confidence_dir / "confidence_probe" / "features" / "confidence_prompt_level_features.jsonl",
        output_dir=output_dir / "larger_split_real_pilot_fusion",
        join_mode="inner",
    )

    dataset_result = build_benchmark_truth_leaning_dataset(
        expanded_real_pilot_fusion_dataset_path=Path(fusion_result["output_paths"]["fusion_dataset_jsonl"]),
        labeled_illumination_raw_results_path=labeled_illumination_dir / "illumination_probe" / "raw_results.jsonl",
        output_dir=output_dir / "larger_split_route_c_dataset_dir",
        fusion_profile="benchmark_truth_leaning_real_pilot_larger",
        run_id="larger",
    )
    logistic_result = run_benchmark_truth_leaning_logistic(
        dataset_path=output_dir / "larger_split_route_c_dataset_dir" / "benchmark_truth_leaning_dataset.jsonl",
        output_dir=output_dir / "larger_split_route_c_run_dir",
        fusion_profile="benchmark_truth_leaning_real_pilot_larger",
        run_id="larger",
        label_threshold=label_threshold,
        random_seed=seed,
    )

    copy_artifact(
        output_dir / "larger_split_route_c_dataset_dir" / "benchmark_truth_leaning_dataset.jsonl",
        output_dir / "larger_split_route_c_dataset.jsonl",
    )
    copy_artifact(
        output_dir / "larger_split_route_c_dataset_dir" / "benchmark_truth_leaning_dataset.csv",
        output_dir / "larger_split_route_c_dataset.csv",
    )
    copy_artifact(
        output_dir / "larger_split_route_c_dataset_dir" / "benchmark_truth_leaning_summary.json",
        output_dir / "larger_split_route_c_summary.json",
    )
    copy_artifact(
        output_dir / "larger_split_route_c_run_dir" / "benchmark_truth_leaning_logistic_predictions.jsonl",
        output_dir / "larger_split_route_c_logistic_predictions.jsonl",
    )
    copy_artifact(
        output_dir / "larger_split_route_c_run_dir" / "benchmark_truth_leaning_logistic_summary.json",
        output_dir / "larger_split_route_c_logistic_summary.json",
    )
    copy_artifact(
        output_dir / "larger_split_route_c_run_dir" / "benchmark_truth_leaning_model_metadata.json",
        output_dir / "larger_split_route_c_model_metadata.json",
    )

    alignment_summary = load_json(Path(fusion_result["output_paths"]["alignment_summary"]))
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "route_name": "larger_split_benchmark_truth_leaning_supervision_proxy",
        "larger_real_pilot_alignment": alignment_summary,
        "larger_split_route_c_summary": dataset_result["summary"],
        "larger_split_route_c_logistic_summary": logistic_result["summary"],
        "notes": [
            "This is route C rerun on the 20-row larger labeled split.",
            "It remains benchmark-truth-leaning proxy supervision, not benchmark ground truth.",
            "The resulting logistic path remains self-fit and pilot-level.",
        ],
    }
    write_json(output_dir / "larger_split_route_c_run_summary.json", run_summary)
    (output_dir / "run.log").write_text(
        "\n".join(
            [
                "TriScope-LLM larger-split route C rerun",
                f"larger_budget={larger_budget}",
                f"labeled_illumination_budget={labeled_illumination_budget}",
                f"alignment_rows={alignment_summary['num_rows']}",
                f"larger_split_route_c_rows={dataset_result['summary']['num_rows']}",
                f"larger_split_route_c_predictions={logistic_result['summary']['num_predictions']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "dataset_jsonl": str((output_dir / "larger_split_route_c_dataset.jsonl").resolve()),
            "dataset_csv": str((output_dir / "larger_split_route_c_dataset.csv").resolve()),
            "summary": str((output_dir / "larger_split_route_c_summary.json").resolve()),
            "predictions": str((output_dir / "larger_split_route_c_logistic_predictions.jsonl").resolve()),
            "logistic_summary": str((output_dir / "larger_split_route_c_logistic_summary.json").resolve()),
            "model_metadata": str((output_dir / "larger_split_route_c_model_metadata.json").resolve()),
            "run_summary": str((output_dir / "larger_split_route_c_run_summary.json").resolve()),
            "log": str((output_dir / "run.log").resolve()),
        },
    }
