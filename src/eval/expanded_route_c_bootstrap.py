"""Expanded route-C bootstrap over the 028 expanded labeled substrate."""

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


SCHEMA_VERSION = "triscopellm/expanded-route-c-bootstrap/v1"


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


def materialize_expanded_route_c(
    expanded_inputs_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    reasoning_query_file = expanded_inputs_dir / "reasoning_query_contracts.jsonl"
    confidence_query_file = expanded_inputs_dir / "confidence_query_contracts.jsonl"
    illumination_query_file = expanded_inputs_dir / "illumination_query_contracts.jsonl"
    labeled_illumination_query_file = expanded_inputs_dir / "labeled_illumination_query_contracts.jsonl"
    expanded_slice_path = expanded_inputs_dir / "csqa_reasoning_pilot_slice.jsonl"

    for path in [
        reasoning_query_file,
        confidence_query_file,
        illumination_query_file,
        labeled_illumination_query_file,
        expanded_slice_path,
    ]:
        if not path.is_file():
            raise ValueError(f"Expanded route C input not found: `{path}`.")

    materialized_inputs_dir = output_dir / "materialized_expanded_route_c_inputs"
    materialized_inputs_dir.mkdir(parents=True, exist_ok=True)
    for src in [
        reasoning_query_file,
        confidence_query_file,
        illumination_query_file,
        labeled_illumination_query_file,
        expanded_slice_path,
    ]:
        copy_artifact(src, materialized_inputs_dir / src.name)

    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_route": "expanded_route_c",
        "route_name": "expanded_benchmark_truth_leaning_supervision_proxy",
        "selected_from": "028_expanded_labeled_slice_substrate",
        "why_selected": [
            "028 already unlocked a larger shared substrate.",
            "Route C is the strongest currently available truth-leaning proxy supervision path.",
            "This rerun directly tests whether the expanded substrate converts into a larger supervised route-C artifact.",
        ],
    }
    label_definition = {
        "schema_version": SCHEMA_VERSION,
        "label_name": "task_answer_incorrect_label",
        "label_source": "expanded_labeled_illumination_query_answer_correctness",
        "label_scope": "benchmark_truth_leaning_supervision_proxy",
        "alignment_key": "base_sample_id+contract_variant",
        "row_expansion_rule": "each expanded base sample emits control/targeted contract rows via labeled illumination contracts",
        "label_limitations": [
            "Still not benchmark ground truth.",
            "Reasoning and confidence remain joined at base-sample level back into contract-level rows.",
            "Expanded substrate is still a local pilot slice.",
        ],
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "ready_to_run": True,
        "route_name": "expanded_benchmark_truth_leaning_supervision_proxy",
        "expanded_substrate_source": str(expanded_inputs_dir.resolve()),
        "query_contract_counts": {
            "reasoning": count_jsonl_rows(reasoning_query_file),
            "confidence": count_jsonl_rows(confidence_query_file),
            "illumination": count_jsonl_rows(illumination_query_file),
            "labeled_illumination": count_jsonl_rows(labeled_illumination_query_file),
        },
        "expected_outputs": {
            "expanded_real_pilot_rows": count_jsonl_rows(reasoning_query_file),
            "expanded_route_c_rows": count_jsonl_rows(labeled_illumination_query_file),
        },
        "notes": [
            "Expanded route C keeps the old route-C supervision semantics but runs them on a larger shared substrate.",
            "It is a benchmark-truth-leaning proxy rerun, not benchmark supervision.",
        ],
    }

    write_json(output_dir / "expanded_route_c_selection.json", selection)
    write_json(output_dir / "expanded_route_c_label_definition.json", label_definition)
    write_json(output_dir / "expanded_route_c_readiness_summary.json", readiness_summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "expanded_inputs_dir": str(expanded_inputs_dir.resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        },
    )
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM expanded route C materialization",
                f"Expanded substrate: {expanded_inputs_dir.resolve()}",
                f"Materialized inputs: {materialized_inputs_dir.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "selection": selection,
        "label_definition": label_definition,
        "readiness_summary": readiness_summary,
        "output_paths": {
            "selection": str((output_dir / "expanded_route_c_selection.json").resolve()),
            "label_definition": str((output_dir / "expanded_route_c_label_definition.json").resolve()),
            "readiness_summary": str((output_dir / "expanded_route_c_readiness_summary.json").resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }


def run_expanded_route_c_bootstrap(
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    reasoning_prompt_dir: Path,
    confidence_prompt_dir: Path,
    illumination_prompt_dir: Path,
    expanded_inputs_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    reasoning_query_file = expanded_inputs_dir / "reasoning_query_contracts.jsonl"
    confidence_query_file = expanded_inputs_dir / "confidence_query_contracts.jsonl"
    illumination_query_file = expanded_inputs_dir / "illumination_query_contracts.jsonl"
    labeled_illumination_query_file = expanded_inputs_dir / "labeled_illumination_query_contracts.jsonl"

    expanded_budget = count_jsonl_rows(reasoning_query_file)
    if expanded_budget <= 0:
        raise ValueError("Expanded route C requires non-empty reasoning query contracts.")

    reasoning_dir = output_dir / "expanded_reasoning"
    confidence_dir = output_dir / "expanded_confidence"
    illumination_dir = output_dir / "expanded_illumination"
    labeled_illumination_dir = output_dir / "expanded_labeled_illumination"

    reasoning_probe = run_reasoning_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_distilgpt2_hf",
        reasoning_config_path=reasoning_config_path,
        reasoning_profile_name="default",
        prompt_dir=reasoning_prompt_dir,
        output_dir=reasoning_dir / "reasoning_probe",
        dataset_manifest=None,
        query_file=reasoning_query_file,
        query_budget_override=expanded_budget,
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
        run_id="expanded_route_c_reasoning",
    )
    write_json(
        reasoning_dir / "expanded_reasoning_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "reasoning",
            "target_budget": expanded_budget,
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
        query_budget_override=expanded_budget,
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
        run_id="expanded_route_c_confidence",
        high_confidence_threshold=0.10,
    )
    write_json(
        confidence_dir / "expanded_confidence_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "confidence",
            "target_budget": expanded_budget,
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
        query_budget_override=expanded_budget,
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
        run_id="expanded_route_c_illumination",
    )
    write_json(
        illumination_dir / "expanded_illumination_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "illumination",
            "target_budget": expanded_budget,
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
        run_id="expanded_route_c_labeled_illumination",
    )
    write_json(
        labeled_illumination_dir / "expanded_labeled_illumination_run_summary.json",
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
        output_dir=output_dir / "expanded_real_pilot_fusion",
        join_mode="inner",
    )

    dataset_result = build_benchmark_truth_leaning_dataset(
        expanded_real_pilot_fusion_dataset_path=Path(fusion_result["output_paths"]["fusion_dataset_jsonl"]),
        labeled_illumination_raw_results_path=labeled_illumination_dir / "illumination_probe" / "raw_results.jsonl",
        output_dir=output_dir / "expanded_route_c_dataset",
        fusion_profile="benchmark_truth_leaning_real_pilot_expanded",
        run_id="expanded",
    )
    logistic_result = run_benchmark_truth_leaning_logistic(
        dataset_path=output_dir / "expanded_route_c_dataset" / "benchmark_truth_leaning_dataset.jsonl",
        output_dir=output_dir / "expanded_route_c_run",
        fusion_profile="benchmark_truth_leaning_real_pilot_expanded",
        run_id="expanded",
        label_threshold=label_threshold,
        random_seed=seed,
    )

    copy_artifact(
        output_dir / "expanded_route_c_dataset" / "benchmark_truth_leaning_dataset.jsonl",
        output_dir / "expanded_benchmark_truth_leaning_dataset.jsonl",
    )
    copy_artifact(
        output_dir / "expanded_route_c_dataset" / "benchmark_truth_leaning_dataset.csv",
        output_dir / "expanded_benchmark_truth_leaning_dataset.csv",
    )
    copy_artifact(
        output_dir / "expanded_route_c_dataset" / "benchmark_truth_leaning_summary.json",
        output_dir / "expanded_benchmark_truth_leaning_summary.json",
    )
    copy_artifact(
        output_dir / "expanded_route_c_run" / "benchmark_truth_leaning_logistic_predictions.jsonl",
        output_dir / "expanded_benchmark_truth_leaning_logistic_predictions.jsonl",
    )
    copy_artifact(
        output_dir / "expanded_route_c_run" / "benchmark_truth_leaning_logistic_summary.json",
        output_dir / "expanded_benchmark_truth_leaning_logistic_summary.json",
    )
    copy_artifact(
        output_dir / "expanded_route_c_run" / "benchmark_truth_leaning_model_metadata.json",
        output_dir / "expanded_benchmark_truth_leaning_model_metadata.json",
    )

    alignment_summary = load_json(Path(fusion_result["output_paths"]["alignment_summary"]))
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "route_name": "expanded_benchmark_truth_leaning_supervision_proxy",
        "expanded_real_pilot_alignment": alignment_summary,
        "expanded_benchmark_truth_leaning_summary": dataset_result["summary"],
        "expanded_benchmark_truth_leaning_logistic_summary": logistic_result["summary"],
        "notes": [
            "This is expanded route C over the 028 expanded labeled substrate.",
            "It remains benchmark-truth-leaning proxy supervision, not benchmark ground truth.",
            "The resulting logistic path remains self-fit and pilot-level.",
        ],
    }
    write_json(output_dir / "expanded_route_c_run_summary.json", run_summary)
    (output_dir / "run.log").write_text(
        "\n".join(
            [
                "TriScope-LLM expanded route C bootstrap",
                f"expanded_budget={expanded_budget}",
                f"labeled_illumination_budget={labeled_illumination_budget}",
                f"expanded_alignment_rows={alignment_summary['num_rows']}",
                f"expanded_route_c_rows={dataset_result['summary']['num_rows']}",
                f"expanded_predictions={logistic_result['summary']['num_predictions']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "expanded_dataset_jsonl": str((output_dir / "expanded_benchmark_truth_leaning_dataset.jsonl").resolve()),
            "expanded_dataset_csv": str((output_dir / "expanded_benchmark_truth_leaning_dataset.csv").resolve()),
            "expanded_summary": str((output_dir / "expanded_benchmark_truth_leaning_summary.json").resolve()),
            "expanded_predictions": str((output_dir / "expanded_benchmark_truth_leaning_logistic_predictions.jsonl").resolve()),
            "expanded_logistic_summary": str((output_dir / "expanded_benchmark_truth_leaning_logistic_summary.json").resolve()),
            "expanded_model_metadata": str((output_dir / "expanded_benchmark_truth_leaning_model_metadata.json").resolve()),
            "run_summary": str((output_dir / "expanded_route_c_run_summary.json").resolve()),
            "log": str((output_dir / "run.log").resolve()),
        },
    }
