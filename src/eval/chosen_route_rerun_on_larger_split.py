"""Rerun the chosen route on the larger labeled split substrate."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from src.features.confidence_features import extract_confidence_features
from src.features.illumination_features import extract_illumination_features
from src.features.reasoning_features import extract_reasoning_features
from src.fusion.feature_alignment import build_fusion_dataset
from src.fusion.more_natural_label_fusion import (
    build_more_natural_labeled_dataset,
    run_more_natural_logistic,
)
from src.probes.confidence_probe import run_confidence_probe
from src.probes.illumination_probe import run_illumination_probe
from src.probes.reasoning_probe import run_reasoning_probe


SCHEMA_VERSION = "triscopellm/chosen-route-rerun-on-larger-split/v1"


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


def materialize_chosen_route_rerun(
    larger_inputs_dir: Path,
    recommendation_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    recommendation = load_json(recommendation_path)
    chosen_route = str(recommendation.get("recommended_route_to_rerun_first", "")).strip().upper()
    if chosen_route != "B":
        raise ValueError(f"033 currently expects chosen route B, got `{chosen_route or 'UNKNOWN'}`.")

    required_inputs = [
        larger_inputs_dir / "reasoning_query_contracts.jsonl",
        larger_inputs_dir / "confidence_query_contracts.jsonl",
        larger_inputs_dir / "illumination_query_contracts.jsonl",
        larger_inputs_dir / "labeled_illumination_query_contracts.jsonl",
        larger_inputs_dir / "csqa_reasoning_pilot_slice.jsonl",
    ]
    for path in required_inputs:
        if not path.is_file():
            raise ValueError(f"Chosen-route rerun input not found: `{path}`.")

    materialized_inputs_dir = output_dir / "materialized_chosen_route_inputs"
    materialized_inputs_dir.mkdir(parents=True, exist_ok=True)
    for src in required_inputs:
        copy_artifact(src, materialized_inputs_dir / src.name)

    reasoning_rows = count_jsonl_rows(materialized_inputs_dir / "reasoning_query_contracts.jsonl")
    confidence_rows = count_jsonl_rows(materialized_inputs_dir / "confidence_query_contracts.jsonl")
    illumination_rows = count_jsonl_rows(materialized_inputs_dir / "illumination_query_contracts.jsonl")
    labeled_illumination_rows = count_jsonl_rows(materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl")

    rerun_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "B",
        "route_name": "more_natural_supervision_proxy",
        "chosen_dataset_substrate": "larger_csqa_reasoning_pilot_local",
        "selected_from": str(recommendation_path.resolve()),
        "expected_artifacts": [
            "expanded_more_natural_dataset.jsonl",
            "expanded_more_natural_summary.json",
            "expanded_more_natural_logistic_predictions.jsonl",
            "expanded_more_natural_logistic_summary.json",
            "chosen_route_rerun_run_summary.json",
        ],
        "success_criterion": [
            "larger split route-B dataset is materialized",
            "route B rerun produces a non-empty supervised dataset",
            "logistic bootstrap no longer depends on the old 5-row route-B slice",
        ],
        "known_risks": [
            "Still a more-natural proxy supervision path, not benchmark ground truth.",
            "Still tied to the local curated larger split and pilot_distilgpt2_hf.",
        ],
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "B",
        "ready_to_run": True,
        "larger_inputs_dir": str(larger_inputs_dir.resolve()),
        "query_contract_counts": {
            "reasoning": reasoning_rows,
            "confidence": confidence_rows,
            "illumination": illumination_rows,
            "labeled_illumination": labeled_illumination_rows,
        },
        "expected_row_capacity": {
            "real_pilot_alignment_rows": reasoning_rows,
            "expanded_more_natural_rows": reasoning_rows,
        },
        "notes": [
            "Chosen route B reuses the larger split as a sample-level substrate.",
            "The route-B supervision head remains more-natural proxy supervision.",
        ],
    }

    write_json(output_dir / "chosen_route_rerun_plan.json", rerun_plan)
    write_json(output_dir / "chosen_route_rerun_readiness_summary.json", readiness_summary)
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
                "TriScope-LLM chosen route rerun materialization",
                "chosen_route=B",
                f"larger_inputs_dir={larger_inputs_dir.resolve()}",
                f"materialized_inputs_dir={materialized_inputs_dir.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "rerun_plan": rerun_plan,
        "readiness_summary": readiness_summary,
        "output_paths": {
            "rerun_plan": str((output_dir / "chosen_route_rerun_plan.json").resolve()),
            "readiness_summary": str((output_dir / "chosen_route_rerun_readiness_summary.json").resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }


def run_chosen_route_rerun(
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
    larger_slice_path = larger_inputs_dir / "csqa_reasoning_pilot_slice.jsonl"

    larger_budget = count_jsonl_rows(reasoning_query_file)
    if larger_budget <= 0:
        raise ValueError("Chosen-route rerun requires non-empty reasoning query contracts.")

    reasoning_dir = output_dir / "larger_reasoning"
    confidence_dir = output_dir / "larger_confidence"
    illumination_dir = output_dir / "larger_illumination"

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
        run_id="larger_route_b_reasoning",
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
        run_id="larger_route_b_confidence",
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
        run_id="larger_route_b_illumination",
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

    fusion_result = build_fusion_dataset(
        illumination_features_path=illumination_dir / "illumination_probe" / "features" / "prompt_level_features.jsonl",
        reasoning_features_path=reasoning_dir / "reasoning_probe" / "features" / "reasoning_prompt_level_features.jsonl",
        confidence_features_path=confidence_dir / "confidence_probe" / "features" / "confidence_prompt_level_features.jsonl",
        output_dir=output_dir / "larger_real_pilot_fusion",
        join_mode="inner",
    )

    dataset_result = build_more_natural_labeled_dataset(
        real_pilot_fusion_dataset_path=Path(fusion_result["output_paths"]["fusion_dataset_jsonl"]),
        reasoning_raw_results_path=reasoning_dir / "reasoning_probe" / "raw_results.jsonl",
        confidence_raw_results_path=confidence_dir / "confidence_probe" / "raw_results.jsonl",
        illumination_raw_results_path=illumination_dir / "illumination_probe" / "raw_results.jsonl",
        pilot_slice_path=larger_slice_path,
        output_dir=output_dir / "larger_route_b_dataset",
        fusion_profile="more_natural_label_real_pilot_larger",
        run_id="larger",
    )
    logistic_result = run_more_natural_logistic(
        dataset_path=output_dir / "larger_route_b_dataset" / "more_natural_labeled_dataset.jsonl",
        output_dir=output_dir / "larger_route_b_run",
        fusion_profile="more_natural_label_real_pilot_larger",
        run_id="larger",
        label_threshold=label_threshold,
        random_seed=seed,
    )

    copy_artifact(
        output_dir / "larger_route_b_dataset" / "more_natural_labeled_dataset.jsonl",
        output_dir / "expanded_more_natural_dataset.jsonl",
    )
    copy_artifact(
        output_dir / "larger_route_b_dataset" / "more_natural_labeled_dataset.csv",
        output_dir / "expanded_more_natural_dataset.csv",
    )
    copy_artifact(
        output_dir / "larger_route_b_dataset" / "more_natural_label_summary.json",
        output_dir / "expanded_more_natural_summary.json",
    )
    copy_artifact(
        output_dir / "larger_route_b_run" / "more_natural_logistic_predictions.jsonl",
        output_dir / "expanded_more_natural_logistic_predictions.jsonl",
    )
    copy_artifact(
        output_dir / "larger_route_b_run" / "more_natural_logistic_summary.json",
        output_dir / "expanded_more_natural_logistic_summary.json",
    )
    copy_artifact(
        output_dir / "larger_route_b_run" / "more_natural_model_metadata.json",
        output_dir / "expanded_more_natural_model_metadata.json",
    )

    alignment_summary = load_json(Path(fusion_result["output_paths"]["alignment_summary"]))
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "B",
        "route_name": "more_natural_supervision_proxy",
        "larger_real_pilot_alignment": alignment_summary,
        "expanded_more_natural_summary": dataset_result["summary"],
        "expanded_more_natural_logistic_summary": logistic_result["summary"],
        "notes": [
            "This is route B rerun on the 20-row larger labeled split.",
            "It remains a more-natural supervision proxy rather than benchmark ground truth.",
            "The logistic path remains self-fit and pilot-level.",
        ],
    }
    write_json(output_dir / "chosen_route_rerun_run_summary.json", run_summary)
    (output_dir / "run.log").write_text(
        "\n".join(
            [
                "TriScope-LLM chosen route rerun on larger split",
                "chosen_route=B",
                f"larger_budget={larger_budget}",
                f"alignment_rows={alignment_summary['num_rows']}",
                f"expanded_more_natural_rows={dataset_result['summary']['num_rows']}",
                f"expanded_predictions={logistic_result['summary']['num_predictions']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "expanded_dataset_jsonl": str((output_dir / "expanded_more_natural_dataset.jsonl").resolve()),
            "expanded_dataset_csv": str((output_dir / "expanded_more_natural_dataset.csv").resolve()),
            "expanded_summary": str((output_dir / "expanded_more_natural_summary.json").resolve()),
            "expanded_predictions": str((output_dir / "expanded_more_natural_logistic_predictions.jsonl").resolve()),
            "expanded_logistic_summary": str((output_dir / "expanded_more_natural_logistic_summary.json").resolve()),
            "expanded_model_metadata": str((output_dir / "expanded_more_natural_model_metadata.json").resolve()),
            "run_summary": str((output_dir / "chosen_route_rerun_run_summary.json").resolve()),
            "log": str((output_dir / "run.log").resolve()),
        },
    }
