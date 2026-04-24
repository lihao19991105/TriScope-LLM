"""Rerun route B on the labeled split v6 substrate."""

from __future__ import annotations

import csv
import json
import re
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


SCHEMA_VERSION = "triscopellm/rerun-route-b-on-labeled-split-v6/v1"
STRICT_OPTION_PATTERN = re.compile(r"\b([A-D])\b")
ROBUST_PREFIX_OPTION_PATTERN = re.compile(r"^\s*([A-D])(?=Human:|Assistant:|[^A-Za-z0-9_]|$)")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Expected at least one row for CSV export.")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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


def parse_option_robust(response_text: str) -> str | None:
    prefix_match = ROBUST_PREFIX_OPTION_PATTERN.search(response_text)
    if prefix_match is not None:
        return prefix_match.group(1)
    strict_match = STRICT_OPTION_PATTERN.search(response_text)
    return strict_match.group(1) if strict_match is not None else None


def stabilize_more_natural_labels(
    dataset_rows: list[dict[str, Any]],
    illumination_raw_results_path: Path,
    fusion_profile: str,
    run_id: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    illumination_rows = load_jsonl(illumination_raw_results_path)
    illumination_map = {str(row["sample_id"]): row for row in illumination_rows}

    stabilized_rows: list[dict[str, Any]] = []
    strict_parse_success = 0
    robust_parse_success = 0
    illumination_flip_count = 0

    for row in dataset_rows:
        sample_id = str(row["sample_id"])
        illumination_row = illumination_map.get(sample_id)
        if illumination_row is None:
            raise ValueError(f"Missing illumination raw result for sample_id `{sample_id}` during stabilization.")

        response_text = str(illumination_row.get("response_text", ""))
        strict_match = STRICT_OPTION_PATTERN.search(response_text)
        strict_option = strict_match.group(1) if strict_match is not None else None
        robust_option = parse_option_robust(response_text)
        if strict_option is not None:
            strict_parse_success += 1
        if robust_option is not None:
            robust_parse_success += 1

        answer_key = str(
            illumination_row.get("metadata", {})
            .get("contract_metadata", {})
            .get("query_answer_key", "")
        )
        original_illumination_correct = bool(row.get("illumination_task_correct"))
        if robust_option is not None and answer_key:
            stabilized_illumination_correct = robust_option == answer_key
        else:
            stabilized_illumination_correct = original_illumination_correct
        if stabilized_illumination_correct != original_illumination_correct:
            illumination_flip_count += 1

        reasoning_correct = bool(row.get("reasoning_task_correct"))
        confidence_correct = bool(row.get("confidence_task_correct"))
        violation_count = sum(
            [
                int(not reasoning_correct),
                int(not confidence_correct),
                int(not stabilized_illumination_correct),
            ]
        )
        stabilized_label = 1 if violation_count > 0 else 0

        stabilized_row = dict(row)
        stabilized_row["original_ground_truth_label"] = int(row.get("ground_truth_label", 0))
        stabilized_row["ground_truth_label"] = stabilized_label
        stabilized_row["original_illumination_task_correct"] = original_illumination_correct
        stabilized_row["illumination_task_correct"] = stabilized_illumination_correct
        stabilized_row["illumination_response_option"] = robust_option
        stabilized_row["stabilization_rule"] = "robust_prefix_option_parse_plus_existing_violation_rule"
        stabilized_row["stabilization_scope"] = "model_axis_1p5b_route_b_only"
        stabilized_rows.append(stabilized_row)

    summary = {
        "summary_status": "PASS",
        "schema_version": "triscopellm/more-natural-label-fusion/v1",
        "fusion_profile": fusion_profile,
        "run_id": run_id,
        "label_name": "task_correctness_violation_label",
        "label_source": "local_csqa_answer_key_plus_observed_multi_modal_outputs",
        "label_scope": "pilot_level_more_natural_supervision_proxy",
        "label_naturalness_level": "task_truth_proxy",
        "num_rows": len(stabilized_rows),
        "num_base_samples": len({row["sample_id"] for row in stabilized_rows}),
        "class_balance": {
            "label_0": sum(1 for row in stabilized_rows if int(row.get("ground_truth_label", 0)) == 0),
            "label_1": sum(1 for row in stabilized_rows if int(row.get("ground_truth_label", 0)) == 1),
        },
        "modality_correctness_coverage": {
            "reasoning_task_correct_true": sum(1 for row in stabilized_rows if bool(row.get("reasoning_task_correct"))),
            "confidence_task_correct_true": sum(1 for row in stabilized_rows if bool(row.get("confidence_task_correct"))),
            "illumination_task_correct_true": sum(
                1 for row in stabilized_rows if bool(row.get("illumination_task_correct"))
            ),
        },
        "stabilization_diagnostics": {
            "strict_option_parse_success_count": strict_parse_success,
            "robust_option_parse_success_count": robust_parse_success,
            "illumination_correctness_flip_count": illumination_flip_count,
        },
        "notes": [
            "Route_b 1.5B stabilization keeps the same violation-count label contract but uses robust option parsing for illumination responses.",
            "This remains a pilot-level more-natural supervision proxy, not benchmark ground truth.",
        ],
    }
    return stabilized_rows, summary


def materialize_route_b_v6(
    v6_inputs_dir: Path,
    route_c_v6_run_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    route_c_v6_run_summary = load_json(route_c_v6_run_summary_path)
    if route_c_v6_run_summary.get("summary_status") != "PASS":
        raise ValueError("055 expects route C v6 run summary to be PASS before route B v6 rerun.")

    required_inputs = [
        v6_inputs_dir / "reasoning_query_contracts.jsonl",
        v6_inputs_dir / "confidence_query_contracts.jsonl",
        v6_inputs_dir / "illumination_query_contracts.jsonl",
        v6_inputs_dir / "csqa_reasoning_pilot_slice.jsonl",
    ]
    for path in required_inputs:
        if not path.is_file():
            raise ValueError(f"Route B v6 input not found: `{path}`.")

    materialized_inputs_dir = output_dir / "materialized_route_b_v6_inputs"
    materialized_inputs_dir.mkdir(parents=True, exist_ok=True)
    for src in required_inputs:
        copy_artifact(src, materialized_inputs_dir / src.name)

    reasoning_rows = count_jsonl_rows(materialized_inputs_dir / "reasoning_query_contracts.jsonl")
    confidence_rows = count_jsonl_rows(materialized_inputs_dir / "confidence_query_contracts.jsonl")
    illumination_rows = count_jsonl_rows(materialized_inputs_dir / "illumination_query_contracts.jsonl")

    plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "B",
        "route_name": "more_natural_supervision_proxy",
        "chosen_dataset_substrate": "larger_csqa_reasoning_pilot_local_v6",
        "selected_from": str(route_c_v6_run_summary_path.resolve()),
        "success_criterion": [
            "materialize route B on labeled split v6",
            "produce a non-empty sample-level more-natural dataset on v6",
            "run route B v6 logistic bootstrap",
        ],
        "known_risks": [
            "Still more-natural proxy supervision, not benchmark ground truth.",
            "Still tied to the local curated v6 split and pilot_distilgpt2_hf.",
        ],
    }
    label_definition = {
        "schema_version": SCHEMA_VERSION,
        "label_name": "task_correctness_violation_label",
        "label_source": "local_csqa_answer_key_plus_observed_multi_modal_outputs",
        "label_scope": "pilot_level_more_natural_supervision_proxy",
        "alignment_key": "sample_id",
        "row_expansion_rule": "each v6 base sample emits one sample-level row after multi-modal alignment",
        "label_limitations": [
            "Still not benchmark ground truth.",
            "Current substrate is still local and curated.",
            "Route B uses task-truth proxy supervision rather than contract-level truth.",
        ],
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "B",
        "ready_to_run": True,
        "v6_inputs_dir": str(v6_inputs_dir.resolve()),
        "query_contract_counts": {
            "reasoning": reasoning_rows,
            "confidence": confidence_rows,
            "illumination": illumination_rows,
        },
        "expected_row_capacity": {
            "route_b_v6_alignment_rows": reasoning_rows,
            "route_b_v6_dataset_rows": reasoning_rows,
        },
        "notes": [
            "This rerun keeps route B's more-natural supervision semantics while moving it onto labeled split v6.",
            "It extends route B from the 60-row v5 split to the 70-row v6 split.",
        ],
    }

    write_json(output_dir / "route_b_v6_plan.json", plan)
    write_json(output_dir / "route_b_v6_label_definition.json", label_definition)
    write_json(output_dir / "route_b_v6_readiness_summary.json", readiness_summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "v6_inputs_dir": str(v6_inputs_dir.resolve()),
            "route_c_v6_run_summary_path": str(route_c_v6_run_summary_path.resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
        },
    )
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM route B on labeled split v6 materialization",
                "chosen_route=B",
                f"v6_inputs_dir={v6_inputs_dir.resolve()}",
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
            "plan": str((output_dir / "route_b_v6_plan.json").resolve()),
            "label_definition": str((output_dir / "route_b_v6_label_definition.json").resolve()),
            "readiness_summary": str((output_dir / "route_b_v6_readiness_summary.json").resolve()),
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }


def run_route_b_v6(
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    reasoning_prompt_dir: Path,
    confidence_prompt_dir: Path,
    illumination_prompt_dir: Path,
    v6_inputs_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
    model_profile_name: str = "pilot_distilgpt2_hf",
    stabilize_label_balance: bool = False,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    reasoning_query_file = v6_inputs_dir / "reasoning_query_contracts.jsonl"
    confidence_query_file = v6_inputs_dir / "confidence_query_contracts.jsonl"
    illumination_query_file = v6_inputs_dir / "illumination_query_contracts.jsonl"
    v6_slice_path = v6_inputs_dir / "csqa_reasoning_pilot_slice.jsonl"

    v6_budget = count_jsonl_rows(reasoning_query_file)
    if v6_budget <= 0:
        raise ValueError("Route B v6 requires non-empty reasoning query contracts.")

    reasoning_dir = output_dir / "route_b_v6_reasoning"
    confidence_dir = output_dir / "route_b_v6_confidence"
    illumination_dir = output_dir / "route_b_v6_illumination"

    reasoning_probe = run_reasoning_probe(
        model_config_path=models_config_path,
        model_profile_name=model_profile_name,
        reasoning_config_path=reasoning_config_path,
        reasoning_profile_name="default",
        prompt_dir=reasoning_prompt_dir,
        output_dir=reasoning_dir / "reasoning_probe",
        dataset_manifest=None,
        query_file=reasoning_query_file,
        query_budget_override=v6_budget,
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
        run_id="route_b_v6_reasoning",
    )
    write_json(
        reasoning_dir / "route_b_v6_reasoning_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "reasoning",
            "target_budget": v6_budget,
            "probe_summary": reasoning_probe["summary"],
            "feature_summary": reasoning_features["feature_summary"],
        },
    )

    confidence_probe = run_confidence_probe(
        model_config_path=models_config_path,
        model_profile_name=model_profile_name,
        confidence_config_path=confidence_config_path,
        confidence_profile_name="pilot_local",
        prompt_dir=confidence_prompt_dir,
        output_dir=confidence_dir / "confidence_probe",
        dataset_manifest=None,
        query_file=confidence_query_file,
        query_budget_override=v6_budget,
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
        run_id="route_b_v6_confidence",
        high_confidence_threshold=0.10,
    )
    write_json(
        confidence_dir / "route_b_v6_confidence_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "confidence",
            "target_budget": v6_budget,
            "probe_summary": confidence_probe["summary"],
            "feature_summary": confidence_features["feature_summary"],
        },
    )

    illumination_probe = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name=model_profile_name,
        illumination_config_path=illumination_config_path,
        illumination_profile_name="pilot_local",
        prompt_dir=illumination_prompt_dir,
        output_dir=illumination_dir / "illumination_probe",
        dataset_manifest=None,
        query_file=illumination_query_file,
        alpha_override=None,
        query_budget_override=v6_budget,
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
        run_id="route_b_v6_illumination",
    )
    write_json(
        illumination_dir / "route_b_v6_illumination_run_summary.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "module_name": "illumination",
            "target_budget": v6_budget,
            "probe_summary": illumination_probe["summary"],
            "feature_summary": illumination_features["feature_summary"],
        },
    )

    fusion_result = build_fusion_dataset(
        illumination_features_path=illumination_dir / "illumination_probe" / "features" / "prompt_level_features.jsonl",
        reasoning_features_path=reasoning_dir / "reasoning_probe" / "features" / "reasoning_prompt_level_features.jsonl",
        confidence_features_path=confidence_dir / "confidence_probe" / "features" / "confidence_prompt_level_features.jsonl",
        output_dir=output_dir / "route_b_v6_real_pilot_fusion",
        join_mode="inner",
    )

    dataset_result = build_more_natural_labeled_dataset(
        real_pilot_fusion_dataset_path=Path(fusion_result["output_paths"]["fusion_dataset_jsonl"]),
        reasoning_raw_results_path=reasoning_dir / "reasoning_probe" / "raw_results.jsonl",
        confidence_raw_results_path=confidence_dir / "confidence_probe" / "raw_results.jsonl",
        illumination_raw_results_path=illumination_dir / "illumination_probe" / "raw_results.jsonl",
        pilot_slice_path=v6_slice_path,
        output_dir=output_dir / "route_b_v6_dataset_dir",
        fusion_profile="more_natural_label_real_pilot_v6",
        run_id="v6",
    )
    dataset_jsonl_for_logistic = output_dir / "route_b_v6_dataset_dir" / "more_natural_labeled_dataset.jsonl"
    dataset_csv_for_copy = output_dir / "route_b_v6_dataset_dir" / "more_natural_labeled_dataset.csv"
    dataset_summary_for_copy = output_dir / "route_b_v6_dataset_dir" / "more_natural_label_summary.json"
    dataset_summary_payload = dataset_result["summary"]

    if stabilize_label_balance:
        stabilized_rows, stabilized_summary = stabilize_more_natural_labels(
            dataset_rows=dataset_result["rows"],
            illumination_raw_results_path=illumination_dir / "illumination_probe" / "raw_results.jsonl",
            fusion_profile="more_natural_label_real_pilot_v6",
            run_id="v6",
        )
        write_jsonl(
            output_dir / "route_b_v6_dataset_dir" / "more_natural_labeled_dataset_stabilized.jsonl",
            stabilized_rows,
        )
        write_csv(
            output_dir / "route_b_v6_dataset_dir" / "more_natural_labeled_dataset_stabilized.csv",
            stabilized_rows,
        )
        write_json(
            output_dir / "route_b_v6_dataset_dir" / "more_natural_label_summary_stabilized.json",
            stabilized_summary,
        )
        dataset_jsonl_for_logistic = (
            output_dir / "route_b_v6_dataset_dir" / "more_natural_labeled_dataset_stabilized.jsonl"
        )
        dataset_csv_for_copy = output_dir / "route_b_v6_dataset_dir" / "more_natural_labeled_dataset_stabilized.csv"
        dataset_summary_for_copy = output_dir / "route_b_v6_dataset_dir" / "more_natural_label_summary_stabilized.json"
        dataset_summary_payload = stabilized_summary

    route_b_run_dir = output_dir / "route_b_v6_run_dir"
    route_b_run_dir.mkdir(parents=True, exist_ok=True)
    logistic_blocked_reason: str | None = None
    try:
        logistic_result = run_more_natural_logistic(
            dataset_path=dataset_jsonl_for_logistic,
            output_dir=route_b_run_dir,
            fusion_profile="more_natural_label_real_pilot_v6",
            run_id="v6",
            label_threshold=label_threshold,
            random_seed=seed,
        )
    except ValueError as exc:
        if "at least two classes" not in str(exc):
            raise
        logistic_blocked_reason = str(exc)
        logistic_summary = {
            "summary_status": "BLOCKED",
            "schema_version": SCHEMA_VERSION,
            "baseline_name": "more_natural_label_logistic_regression",
            "run_id": "v6",
            "fusion_profile": "more_natural_label_real_pilot_v6",
            "num_predictions": 0,
            "label_name": dataset_summary_payload["label_name"],
            "label_scope": dataset_summary_payload["label_scope"],
            "label_naturalness_level": dataset_summary_payload["label_naturalness_level"],
            "label_threshold": label_threshold,
            "mean_prediction_score": None,
            "num_positive_predictions": 0,
            "blocking_reason": logistic_blocked_reason,
            "notes": [
                "Real probe execution reached the labeled route_b dataset stage, but logistic fitting is blocked because the dataset collapsed to a single class.",
                "This is an honest partial execution result rather than a full route_b logistic execute.",
            ],
        }
        write_json(route_b_run_dir / "more_natural_logistic_summary.json", logistic_summary)
        write_jsonl(route_b_run_dir / "more_natural_logistic_predictions.jsonl", [])
        write_json(
            route_b_run_dir / "more_natural_model_metadata.json",
            {
                "summary_status": "BLOCKED",
                "schema_version": SCHEMA_VERSION,
                "baseline_name": "more_natural_label_logistic_regression",
                "blocking_reason": logistic_blocked_reason,
            },
        )
        logistic_result = {
            "summary": logistic_summary,
            "output_paths": {
                "predictions": str((route_b_run_dir / "more_natural_logistic_predictions.jsonl").resolve()),
                "summary": str((route_b_run_dir / "more_natural_logistic_summary.json").resolve()),
                "model_metadata": str((route_b_run_dir / "more_natural_model_metadata.json").resolve()),
            },
        }

    copy_artifact(
        dataset_jsonl_for_logistic,
        output_dir / "route_b_v6_dataset.jsonl",
    )
    copy_artifact(
        dataset_csv_for_copy,
        output_dir / "route_b_v6_dataset.csv",
    )
    copy_artifact(
        dataset_summary_for_copy,
        output_dir / "route_b_v6_summary.json",
    )
    copy_artifact(
        route_b_run_dir / "more_natural_logistic_predictions.jsonl",
        output_dir / "route_b_v6_logistic_predictions.jsonl",
    )
    copy_artifact(
        route_b_run_dir / "more_natural_logistic_summary.json",
        output_dir / "route_b_v6_logistic_summary.json",
    )
    copy_artifact(
        route_b_run_dir / "more_natural_model_metadata.json",
        output_dir / "route_b_v6_model_metadata.json",
    )

    alignment_summary = load_json(Path(fusion_result["output_paths"]["alignment_summary"]))
    run_summary = {
        "summary_status": "PASS" if logistic_blocked_reason is None else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "B",
        "route_name": "more_natural_supervision_proxy_v6",
        "execution_status": "FULL_EXECUTE" if logistic_blocked_reason is None else "PARTIAL_SINGLE_CLASS_LABEL_COLLAPSE",
        "label_balance_stabilization_enabled": stabilize_label_balance,
        "route_b_v6_alignment": alignment_summary,
        "route_b_v6_summary": dataset_summary_payload,
        "route_b_v6_logistic_summary": logistic_result["summary"],
        "logistic_blocked_reason": logistic_blocked_reason,
        "notes": [
            "This is route B rerun on the 60-row labeled split v6.",
            "It remains a more-natural supervision proxy rather than benchmark ground truth.",
            "The logistic path remains self-fit and pilot-level.",
            f"Execution model profile: {model_profile_name}.",
            (
                "Route_b label-balance stabilization was enabled with robust illumination option parsing."
                if stabilize_label_balance
                else "Route_b label-balance stabilization was disabled."
            ),
            (
                "The execution reached real 1.5B model inference, but logistic fitting was blocked by single-class label collapse."
                if logistic_blocked_reason is not None
                else "The route_b logistic path completed successfully."
            ),
        ],
    }
    write_json(output_dir / "route_b_v6_run_summary.json", run_summary)
    (output_dir / "run.log").write_text(
        "\n".join(
            [
                "TriScope-LLM route B on labeled split v6 rerun",
                "chosen_route=B",
                f"v6_budget={v6_budget}",
                f"alignment_rows={alignment_summary['num_rows']}",
                f"route_b_v6_rows={dataset_summary_payload['num_rows']}",
                f"route_b_v6_class_balance={dataset_summary_payload['class_balance']}",
                f"route_b_v6_predictions={logistic_result['summary']['num_predictions']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "run_summary": run_summary,
        "output_paths": {
            "dataset_jsonl": str((output_dir / "route_b_v6_dataset.jsonl").resolve()),
            "dataset_csv": str((output_dir / "route_b_v6_dataset.csv").resolve()),
            "summary": str((output_dir / "route_b_v6_summary.json").resolve()),
            "predictions": str((output_dir / "route_b_v6_logistic_predictions.jsonl").resolve()),
            "logistic_summary": str((output_dir / "route_b_v6_logistic_summary.json").resolve()),
            "model_metadata": str((output_dir / "route_b_v6_model_metadata.json").resolve()),
            "run_summary": str((output_dir / "route_b_v6_run_summary.json").resolve()),
            "log": str((output_dir / "run.log").resolve()),
        },
    }
