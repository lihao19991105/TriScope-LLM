"""Bootstrap a first more-natural-label supervised real-pilot fusion path."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.fusion.labeled_real_pilot_fusion import (
    CONFIDENCE_NUMERIC_COLUMNS,
    ILLUMINATION_NUMERIC_COLUMNS,
    REASONING_NUMERIC_COLUMNS,
    load_jsonl,
    write_csv,
    write_json,
    write_jsonl,
)


SCHEMA_VERSION = "triscopellm/more-natural-label-fusion/v1"
OPTION_LABEL_PATTERN = re.compile(r"\b([A-D])\b")


def extract_option_label(text: str) -> str | None:
    match = OPTION_LABEL_PATTERN.search(text)
    return match.group(1) if match is not None else None


def load_pilot_slice_map(pilot_slice_path: Path) -> dict[str, dict[str, Any]]:
    rows = load_jsonl(pilot_slice_path)
    return {str(row["sample_id"]): row for row in rows}


def load_raw_map(raw_results_path: Path, sample_key: str = "sample_id") -> dict[str, dict[str, Any]]:
    rows = load_jsonl(raw_results_path)
    return {str(row[sample_key]): row for row in rows}


def build_more_natural_labeled_dataset(
    real_pilot_fusion_dataset_path: Path,
    reasoning_raw_results_path: Path,
    confidence_raw_results_path: Path,
    illumination_raw_results_path: Path,
    pilot_slice_path: Path,
    output_dir: Path,
    fusion_profile: str,
    run_id: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    fusion_rows = load_jsonl(real_pilot_fusion_dataset_path)
    reasoning_map = load_raw_map(reasoning_raw_results_path)
    confidence_map = load_raw_map(confidence_raw_results_path)
    illumination_map = load_raw_map(illumination_raw_results_path)
    pilot_slice_map = load_pilot_slice_map(pilot_slice_path)

    dataset_rows: list[dict[str, Any]] = []
    for fusion_row in fusion_rows:
        sample_id = str(fusion_row["sample_id"])
        slice_row = pilot_slice_map[sample_id]
        reasoning_row = reasoning_map[sample_id]
        confidence_row = confidence_map[sample_id]
        illumination_row = illumination_map[sample_id]

        task_answer_key = str(slice_row["answerKey"])
        reasoning_correct = bool(reasoning_row.get("reasoned_is_target_behavior"))
        confidence_correct = bool(confidence_row.get("is_target_behavior"))
        illumination_answer_key = str(
            illumination_row.get("metadata", {})
            .get("contract_metadata", {})
            .get("query_answer_key", "")
        )
        illumination_response_label = extract_option_label(str(illumination_row.get("response_text", "")))
        illumination_correct = bool(
            illumination_response_label is not None
            and illumination_answer_key
            and illumination_response_label == illumination_answer_key
        )
        modality_correctness = {
            "reasoning_task_correct": reasoning_correct,
            "confidence_task_correct": confidence_correct,
            "illumination_task_correct": illumination_correct,
        }
        violation_count = sum(0 if value else 1 for value in modality_correctness.values())
        ground_truth_label = 1 if violation_count > 0 else 0

        dataset_row = {
            "schema_version": SCHEMA_VERSION,
            "alignment_key": "sample_id",
            "sample_id": sample_id,
            "fusion_profile": fusion_profile,
            "run_id": run_id,
            "label_name": "task_correctness_violation_label",
            "ground_truth_label": ground_truth_label,
            "label_source": "local_csqa_answer_key_plus_observed_multi_modal_outputs",
            "label_scope": "pilot_level_more_natural_supervision_proxy",
            "label_naturalness_level": "task_truth_proxy",
            "label_mapping_rule": "sample_id aligns the local slice answerKey, real-pilot fusion row, and three modality raw outputs",
            "label_limitations": [
                "Not benchmark ground truth.",
                "Still limited to the current 5-row local slice.",
                "Illumination correctness is inferred via lightweight option-label extraction from response text.",
            ],
            "task_answer_key": task_answer_key,
            "reasoning_task_correct": reasoning_correct,
            "confidence_task_correct": confidence_correct,
            "illumination_task_correct": illumination_correct,
            "illumination_response_option": illumination_response_label,
            "violation_count": violation_count,
            "num_modalities_checked": 3,
            "model_profile": fusion_row["model_profile"],
            "illumination_present": bool(fusion_row["illumination_present"]),
            "reasoning_present": bool(fusion_row["reasoning_present"]),
            "confidence_present": bool(fusion_row["confidence_present"]),
            "modality_count": int(fusion_row["modality_count"]),
            "canonical_trigger_type": fusion_row["canonical_trigger_type"],
            "canonical_target_type": fusion_row["canonical_target_type"],
            "illumination__sample_id": fusion_row["illumination__sample_id"],
            "illumination__target_behavior_label": float(fusion_row["illumination__target_behavior_label"]),
            "illumination__query_budget_realized_ratio": float(fusion_row["illumination__query_budget_realized_ratio"]),
            "illumination__response_length": float(fusion_row["illumination__response_length"]),
            "illumination__alpha": float(fusion_row["illumination__alpha"]),
            "reasoning__sample_id": fusion_row["reasoning__sample_id"],
            "reasoning__answer_changed_after_reasoning": float(fusion_row["reasoning__answer_changed_after_reasoning"]),
            "reasoning__target_behavior_flip_flag": float(fusion_row["reasoning__target_behavior_flip_flag"]),
            "reasoning__reasoning_length": float(fusion_row["reasoning__reasoning_length"]),
            "reasoning__reasoning_step_count": float(fusion_row["reasoning__reasoning_step_count"]),
            "reasoning__reasoning_to_answer_length_ratio": float(fusion_row["reasoning__reasoning_to_answer_length_ratio"]),
            "confidence__sample_id": fusion_row["confidence__sample_id"],
            "confidence__mean_chosen_token_prob": float(fusion_row["confidence__mean_chosen_token_prob"]),
            "confidence__mean_entropy": float(fusion_row["confidence__mean_entropy"]),
            "confidence__high_confidence_fraction": float(fusion_row["confidence__high_confidence_fraction"]),
            "confidence__max_consecutive_high_confidence_steps": float(fusion_row["confidence__max_consecutive_high_confidence_steps"]),
            "confidence__entropy_collapse_score": float(fusion_row["confidence__entropy_collapse_score"]),
            "metadata": {
                "pilot_slice_source": str(pilot_slice_path.resolve()),
                "reasoning_raw_results_path": str(reasoning_raw_results_path.resolve()),
                "confidence_raw_results_path": str(confidence_raw_results_path.resolve()),
                "illumination_raw_results_path": str(illumination_raw_results_path.resolve()),
                "source_dataset": slice_row.get("metadata", {}).get("source_name", "unknown"),
            },
        }
        dataset_rows.append(dataset_row)

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fusion_profile": fusion_profile,
        "run_id": run_id,
        "label_name": "task_correctness_violation_label",
        "label_source": "local_csqa_answer_key_plus_observed_multi_modal_outputs",
        "label_scope": "pilot_level_more_natural_supervision_proxy",
        "label_naturalness_level": "task_truth_proxy",
        "num_rows": len(dataset_rows),
        "num_base_samples": len({row["sample_id"] for row in dataset_rows}),
        "class_balance": {
            "label_0": sum(1 for row in dataset_rows if row["ground_truth_label"] == 0),
            "label_1": sum(1 for row in dataset_rows if row["ground_truth_label"] == 1),
        },
        "modality_correctness_coverage": {
            "reasoning_task_correct_true": sum(1 for row in dataset_rows if row["reasoning_task_correct"]),
            "confidence_task_correct_true": sum(1 for row in dataset_rows if row["confidence_task_correct"]),
            "illumination_task_correct_true": sum(1 for row in dataset_rows if row["illumination_task_correct"]),
        },
        "notes": [
            "This label is more natural than the current controlled contract label because it is grounded in task answer correctness.",
            "It is still a pilot-level proxy, not benchmark ground truth.",
        ],
    }
    label_definition = {
        "schema_version": SCHEMA_VERSION,
        "label_name": "task_correctness_violation_label",
        "label_source": "local_csqa_answer_key_plus_observed_multi_modal_outputs",
        "label_meaning": "1 if at least one modality violates task correctness on the base sample; 0 if all three modalities remain task-correct.",
        "label_scope": "pilot_level_more_natural_supervision_proxy",
        "label_naturalness_level": "task_truth_proxy",
        "label_limitations": [
            "Still not benchmark ground truth.",
            "Current slice is tiny and uses a lightweight model.",
            "Illumination correctness uses lightweight option extraction from response text.",
        ],
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "ready_to_run": summary["class_balance"]["label_0"] > 0 and summary["class_balance"]["label_1"] > 0,
        "label_name": "task_correctness_violation_label",
        "label_source": "local_csqa_answer_key_plus_observed_multi_modal_outputs",
        "label_scope": "pilot_level_more_natural_supervision_proxy",
        "num_rows": summary["num_rows"],
        "num_base_samples": summary["num_base_samples"],
        "class_balance": summary["class_balance"],
    }
    selection = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_route": "more_natural_label_bootstrap",
        "selected_label_name": "task_correctness_violation_label",
        "why_this_label": [
            "It reuses existing local answerKey values instead of contract variants.",
            "It aligns directly at sample_id level to the expanded 5-row real-pilot fusion dataset.",
            "It is more natural than the controlled label while remaining low cost and auditable.",
        ],
        "why_not_heavier_alternatives": [
            "Benchmark ground-truth supervision is not locally materialized on the same slice.",
            "External datasets or larger label systems would add cost before proving a minimal more-natural path exists.",
        ],
    }

    write_json(output_dir / "more_natural_label_selection.json", selection)
    write_json(output_dir / "more_natural_label_definition.json", label_definition)
    write_json(output_dir / "more_natural_label_readiness_summary.json", readiness_summary)
    write_jsonl(output_dir / "more_natural_labeled_dataset.jsonl", dataset_rows)
    write_csv(output_dir / "more_natural_labeled_dataset.csv", dataset_rows)
    write_json(output_dir / "more_natural_label_summary.json", summary)
    write_json(
        output_dir / "config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "fusion_profile": fusion_profile,
            "run_id": run_id,
            "real_pilot_fusion_dataset_path": str(real_pilot_fusion_dataset_path.resolve()),
            "pilot_slice_path": str(pilot_slice_path.resolve()),
            "reasoning_raw_results_path": str(reasoning_raw_results_path.resolve()),
            "confidence_raw_results_path": str(confidence_raw_results_path.resolve()),
            "illumination_raw_results_path": str(illumination_raw_results_path.resolve()),
        },
    )
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM more-natural-label bootstrap",
                "Label: task_correctness_violation_label",
                f"Rows: {summary['num_rows']}",
                f"Class balance: {summary['class_balance']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "rows": dataset_rows,
        "summary": summary,
        "label_definition": label_definition,
        "readiness_summary": readiness_summary,
        "selection": selection,
        "output_paths": {
            "selection": str((output_dir / "more_natural_label_selection.json").resolve()),
            "label_definition": str((output_dir / "more_natural_label_definition.json").resolve()),
            "readiness_summary": str((output_dir / "more_natural_label_readiness_summary.json").resolve()),
            "dataset_jsonl": str((output_dir / "more_natural_labeled_dataset.jsonl").resolve()),
            "dataset_csv": str((output_dir / "more_natural_labeled_dataset.csv").resolve()),
            "summary": str((output_dir / "more_natural_label_summary.json").resolve()),
            "config_snapshot": str((output_dir / "config_snapshot.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }


def run_more_natural_logistic(
    dataset_path: Path,
    output_dir: Path,
    fusion_profile: str,
    run_id: str,
    label_threshold: float,
    random_seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_jsonl(dataset_path)
    if not rows:
        raise ValueError("More-natural labeled dataset is empty.")

    feature_columns = (
        ILLUMINATION_NUMERIC_COLUMNS
        + REASONING_NUMERIC_COLUMNS
        + CONFIDENCE_NUMERIC_COLUMNS
    )
    matrix = [[float(row.get(column, 0.0)) for column in feature_columns] for row in rows]
    labels = [int(row["ground_truth_label"]) for row in rows]
    if len(set(labels)) < 2:
        raise ValueError("More-natural labeled dataset must contain at least two classes.")

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("logreg", LogisticRegression(random_state=random_seed, solver="liblinear")),
        ]
    )
    pipeline.fit(matrix, labels)
    probabilities = pipeline.predict_proba(matrix)[:, 1].tolist()
    predictions = pipeline.predict(matrix).tolist()
    logistic = pipeline.named_steps["logreg"]

    prediction_rows: list[dict[str, Any]] = []
    for row, score, prediction in zip(rows, probabilities, predictions):
        prediction_rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "run_id": run_id,
                "sample_id": row["sample_id"],
                "fusion_profile": fusion_profile,
                "prediction_score": float(score),
                "prediction_label": int(prediction),
                "label_threshold": label_threshold,
                "ground_truth_label": row["ground_truth_label"],
                "illumination_present": row["illumination_present"],
                "reasoning_present": row["reasoning_present"],
                "confidence_present": row["confidence_present"],
                "modality_count": row["modality_count"],
                "metadata": {
                    "baseline_name": "more_natural_label_logistic_regression",
                    "label_name": row["label_name"],
                    "label_scope": row["label_scope"],
                    "label_naturalness_level": row["label_naturalness_level"],
                    "training_mode": "self_fit_more_natural_supervised_fusion_bootstrap",
                },
            }
        )

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "baseline_name": "more_natural_label_logistic_regression",
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "num_predictions": len(prediction_rows),
        "label_name": rows[0]["label_name"],
        "label_scope": rows[0]["label_scope"],
        "label_naturalness_level": rows[0]["label_naturalness_level"],
        "label_threshold": label_threshold,
        "mean_prediction_score": sum(probabilities) / len(probabilities) if probabilities else 0.0,
        "num_positive_predictions": sum(int(pred["prediction_label"]) for pred in prediction_rows),
        "notes": [
            "This path uses a more-natural pilot-level task-truth proxy label, not benchmark ground truth.",
            "It remains a self-fit bootstrap intended to prove executability rather than generalization.",
        ],
    }
    model_metadata = {
        "schema_version": SCHEMA_VERSION,
        "baseline_name": "more_natural_label_logistic_regression",
        "feature_columns": feature_columns,
        "intercept": logistic.intercept_.tolist(),
        "coefficients": {name: float(value) for name, value in zip(feature_columns, logistic.coef_[0].tolist())},
        "class_balance": {
            "label_0": labels.count(0),
            "label_1": labels.count(1),
        },
    }
    readiness_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "supervised_logistic_completed": True,
        "label_name": rows[0]["label_name"],
        "label_scope": rows[0]["label_scope"],
        "label_naturalness_level": rows[0]["label_naturalness_level"],
        "num_rows": len(rows),
        "num_predictions": len(prediction_rows),
    }
    run_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "label_name": rows[0]["label_name"],
        "label_scope": rows[0]["label_scope"],
        "label_naturalness_level": rows[0]["label_naturalness_level"],
        "supervised_logistic_completed": True,
        "prediction_artifacts": {
            "predictions": str((output_dir / "more_natural_logistic_predictions.jsonl").resolve()),
            "summary": str((output_dir / "more_natural_logistic_summary.json").resolve()),
            "model_metadata": str((output_dir / "more_natural_model_metadata.json").resolve()),
        },
    }

    write_jsonl(output_dir / "more_natural_logistic_predictions.jsonl", prediction_rows)
    write_json(output_dir / "more_natural_logistic_summary.json", summary)
    write_json(output_dir / "more_natural_model_metadata.json", model_metadata)
    write_json(output_dir / "more_natural_supervised_readiness_summary.json", readiness_summary)
    write_json(output_dir / "more_natural_label_run_summary.json", run_summary)
    write_json(
        output_dir / "run_config_snapshot.json",
        {
            "schema_version": SCHEMA_VERSION,
            "fusion_profile": fusion_profile,
            "run_id": run_id,
            "label_threshold": label_threshold,
            "dataset_path": str(dataset_path.resolve()),
            "random_seed": random_seed,
        },
    )
    (output_dir / "run.log").write_text(
        "\n".join(
            [
                "TriScope-LLM more-natural-label supervised bootstrap",
                f"Run ID: {run_id}",
                f"Rows: {len(rows)}",
                f"Predictions: {(output_dir / 'more_natural_logistic_predictions.jsonl').resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "readiness_summary": readiness_summary,
        "run_summary": run_summary,
        "output_paths": {
            "predictions": str((output_dir / "more_natural_logistic_predictions.jsonl").resolve()),
            "summary": str((output_dir / "more_natural_logistic_summary.json").resolve()),
            "model_metadata": str((output_dir / "more_natural_model_metadata.json").resolve()),
            "readiness_summary": str((output_dir / "more_natural_supervised_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "more_natural_label_run_summary.json").resolve()),
            "config_snapshot": str((output_dir / "run_config_snapshot.json").resolve()),
            "log": str((output_dir / "run.log").resolve()),
        },
    }
