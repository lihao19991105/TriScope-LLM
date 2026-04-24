"""Labeled real-pilot fusion materialization and supervised bootstrap."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION = "triscopellm/labeled-real-pilot-fusion/v1"

ILLUMINATION_NUMERIC_COLUMNS = [
    "illumination__target_behavior_label",
    "illumination__query_budget_realized_ratio",
    "illumination__response_length",
    "illumination__alpha",
]
REASONING_NUMERIC_COLUMNS = [
    "reasoning__answer_changed_after_reasoning",
    "reasoning__target_behavior_flip_flag",
    "reasoning__reasoning_length",
    "reasoning__reasoning_step_count",
    "reasoning__reasoning_to_answer_length_ratio",
]
CONFIDENCE_NUMERIC_COLUMNS = [
    "confidence__mean_chosen_token_prob",
    "confidence__mean_entropy",
    "confidence__high_confidence_fraction",
    "confidence__max_consecutive_high_confidence_steps",
    "confidence__entropy_collapse_score",
]


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
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            normalized: dict[str, Any] = {}
            for key in fieldnames:
                value = row.get(key)
                if isinstance(value, (dict, list)):
                    normalized[key] = json.dumps(value, ensure_ascii=True, sort_keys=True)
                else:
                    normalized[key] = value
            writer.writerow(normalized)


def build_labeled_real_pilot_fusion_dataset(
    real_pilot_fusion_dataset_path: Path,
    labeled_pilot_dataset_path: Path,
    output_dir: Path,
    fusion_profile: str,
    run_id: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fusion_rows = load_jsonl(real_pilot_fusion_dataset_path)
    labeled_rows = load_jsonl(labeled_pilot_dataset_path)

    fusion_by_base_id = {str(row["sample_id"]): row for row in fusion_rows}
    labeled_aligned_rows = [
        row for row in labeled_rows if str(row["base_sample_id"]) in fusion_by_base_id
    ]
    if not labeled_aligned_rows:
        raise ValueError("No labeled pilot rows align with the current real-pilot fusion dataset.")

    materialized_rows: list[dict[str, Any]] = []
    for labeled_row in labeled_aligned_rows:
        base_sample_id = str(labeled_row["base_sample_id"])
        base_fusion_row = fusion_by_base_id[base_sample_id]
        metadata = labeled_row.get("metadata", {})
        contract_metadata = metadata.get("contract_metadata", {}) if isinstance(metadata, dict) else {}

        materialized = {
            "schema_version": LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION,
            "alignment_key": "base_sample_id+contract_variant",
            "base_sample_id": base_sample_id,
            "sample_id": str(labeled_row["sample_id"]),
            "contract_variant": str(labeled_row["contract_variant"]),
            "fusion_profile": fusion_profile,
            "run_id": run_id,
            "label_name": str(labeled_row["label_name"]),
            "ground_truth_label": int(labeled_row["ground_truth_label"]),
            "label_source": "materialized_contract_variant",
            "label_scope": "pilot_level_controlled_supervision",
            "label_mapping_rule": "base_sample_id joins to real_pilot_fusion.sample_id; contract_variant expands each base sample into control/targeted rows",
            "label_limitations": [
                "Not benchmark ground truth.",
                "Reasoning and confidence features are reused at the base-sample level across contract variants.",
            ],
            "model_profile": str(base_fusion_row["model_profile"]),
            "illumination_present": True,
            "reasoning_present": bool(base_fusion_row.get("reasoning_present")),
            "confidence_present": bool(base_fusion_row.get("confidence_present")),
            "modality_count": 3,
            "canonical_trigger_type": str(labeled_row["trigger_type"]),
            "canonical_target_type": str(labeled_row["target_type"]),
            "illumination__run_id": "labeled_bootstrap",
            "illumination__sample_id": str(labeled_row["sample_id"]),
            "illumination__base_sample_id": base_sample_id,
            "illumination__contract_variant": str(labeled_row["contract_variant"]),
            "illumination__model_profile": str(labeled_row["model_profile"]),
            "illumination__illumination_profile": str(labeled_row["illumination_profile"]),
            "illumination__prompt_template_name": str(labeled_row["prompt_template_name"]),
            "illumination__target_type": str(labeled_row["target_type"]),
            "illumination__trigger_type": str(labeled_row["trigger_type"]),
            "illumination__alpha": float(labeled_row["alpha"]),
            "illumination__query_budget_realized_ratio": float(labeled_row["query_budget_realized_ratio"]),
            "illumination__response_length": float(labeled_row["response_length"]),
            "illumination__target_behavior_label": float(labeled_row["target_behavior_label"]),
            "illumination__metadata": metadata,
            "reasoning__run_id": base_fusion_row.get("reasoning__run_id"),
            "reasoning__sample_id": base_fusion_row.get("reasoning__sample_id"),
            "reasoning__model_profile": base_fusion_row.get("reasoning__model_profile"),
            "reasoning__reasoning_profile": base_fusion_row.get("reasoning__reasoning_profile"),
            "reasoning__prompt_template_name": base_fusion_row.get("reasoning__prompt_template_name"),
            "reasoning__target_type": base_fusion_row.get("reasoning__target_type"),
            "reasoning__trigger_type": base_fusion_row.get("reasoning__trigger_type"),
            "reasoning__answer_changed_after_reasoning": float(base_fusion_row.get("reasoning__answer_changed_after_reasoning", 0.0)),
            "reasoning__target_behavior_flip_flag": float(base_fusion_row.get("reasoning__target_behavior_flip_flag", 0.0)),
            "reasoning__reasoning_length": float(base_fusion_row.get("reasoning__reasoning_length", 0.0)),
            "reasoning__reasoning_step_count": float(base_fusion_row.get("reasoning__reasoning_step_count", 0.0)),
            "reasoning__reasoning_to_answer_length_ratio": float(base_fusion_row.get("reasoning__reasoning_to_answer_length_ratio", 0.0)),
            "reasoning__metadata": base_fusion_row.get("reasoning__metadata"),
            "confidence__run_id": base_fusion_row.get("confidence__run_id"),
            "confidence__sample_id": base_fusion_row.get("confidence__sample_id"),
            "confidence__model_profile": base_fusion_row.get("confidence__model_profile"),
            "confidence__confidence_profile": base_fusion_row.get("confidence__confidence_profile"),
            "confidence__prompt_template_name": base_fusion_row.get("confidence__prompt_template_name"),
            "confidence__target_type": base_fusion_row.get("confidence__target_type"),
            "confidence__trigger_type": base_fusion_row.get("confidence__trigger_type"),
            "confidence__mean_chosen_token_prob": float(base_fusion_row.get("confidence__mean_chosen_token_prob", 0.0)),
            "confidence__mean_entropy": float(base_fusion_row.get("confidence__mean_entropy", 0.0)),
            "confidence__high_confidence_fraction": float(base_fusion_row.get("confidence__high_confidence_fraction", 0.0)),
            "confidence__max_consecutive_high_confidence_steps": float(base_fusion_row.get("confidence__max_consecutive_high_confidence_steps", 0.0)),
            "confidence__entropy_collapse_score": float(base_fusion_row.get("confidence__entropy_collapse_score", 0.0)),
            "confidence__metadata": base_fusion_row.get("confidence__metadata"),
            "metadata": {
                "source_real_pilot_sample_id": base_sample_id,
                "source_contract_metadata": contract_metadata,
                "integration_scope": "pilot_level_controlled_supervised_fusion_bootstrap",
            },
        }
        materialized_rows.append(materialized)

    numeric_feature_columns = (
        ILLUMINATION_NUMERIC_COLUMNS
        + REASONING_NUMERIC_COLUMNS
        + CONFIDENCE_NUMERIC_COLUMNS
    )
    summary = {
        "summary_status": "PASS",
        "schema_version": LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION,
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "num_rows": len(materialized_rows),
        "num_base_samples": len({row["base_sample_id"] for row in materialized_rows}),
        "label_name": "controlled_targeted_icl_label",
        "label_source": "materialized_contract_variant",
        "label_scope": "pilot_level_controlled_supervision",
        "label_mapping_rule": "base_sample_id -> real_pilot_fusion.sample_id, then expand by contract_variant",
        "label_coverage": {
            "num_aligned_base_samples": len({row["base_sample_id"] for row in materialized_rows}),
            "class_balance": {
                "label_0": sum(1 for row in materialized_rows if row["ground_truth_label"] == 0),
                "label_1": sum(1 for row in materialized_rows if row["ground_truth_label"] == 1),
            },
        },
        "numeric_feature_columns": numeric_feature_columns,
        "notes": [
            "This dataset is a pilot-level controlled supervised fusion bootstrap.",
            "Reasoning and confidence features are copied from the base-sample real-pilot fusion row.",
        ],
    }
    label_definition = {
        "schema_version": LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION,
        "label_name": "controlled_targeted_icl_label",
        "label_source": "materialized_contract_variant",
        "label_scope": "pilot_level_controlled_supervision",
        "label_mapping_rule": "base_sample_id joins to real-pilot sample_id; contract_variant defines control vs targeted row expansion",
        "label_limitations": [
            "Not benchmark ground truth.",
            "Only aligned base samples present in the current real-pilot fusion dataset are covered.",
            "Reasoning/confidence are not independently relabeled per variant.",
        ],
    }

    jsonl_path = output_dir / "labeled_real_pilot_fusion_dataset.jsonl"
    csv_path = output_dir / "labeled_real_pilot_fusion_dataset.csv"
    summary_path = output_dir / "labeled_real_pilot_fusion_summary.json"
    label_definition_path = output_dir / "labeled_real_pilot_label_definition.json"
    config_snapshot_path = output_dir / "config_snapshot.json"

    write_jsonl(jsonl_path, materialized_rows)
    write_csv(csv_path, materialized_rows)
    write_json(summary_path, summary)
    write_json(label_definition_path, label_definition)
    write_json(
        config_snapshot_path,
        {
            "schema_version": LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION,
            "fusion_profile": fusion_profile,
            "run_id": run_id,
            "real_pilot_fusion_dataset_path": str(real_pilot_fusion_dataset_path.resolve()),
            "labeled_pilot_dataset_path": str(labeled_pilot_dataset_path.resolve()),
        },
    )
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM labeled real-pilot fusion dataset",
                f"Source fusion dataset: {real_pilot_fusion_dataset_path.resolve()}",
                f"Source labeled pilot dataset: {labeled_pilot_dataset_path.resolve()}",
                f"Rows: {len(materialized_rows)}",
                f"Summary: {summary_path.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "rows": materialized_rows,
        "summary": summary,
        "label_definition": label_definition,
        "output_paths": {
            "dataset_jsonl": str(jsonl_path.resolve()),
            "dataset_csv": str(csv_path.resolve()),
            "summary": str(summary_path.resolve()),
            "label_definition": str(label_definition_path.resolve()),
            "config_snapshot": str(config_snapshot_path.resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }


def run_labeled_real_pilot_logistic(
    labeled_real_pilot_fusion_dataset_path: Path,
    output_dir: Path,
    fusion_profile: str,
    run_id: str,
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = load_jsonl(labeled_real_pilot_fusion_dataset_path)
    if not rows:
        raise ValueError("Labeled real-pilot fusion dataset is empty.")

    feature_columns = (
        ILLUMINATION_NUMERIC_COLUMNS
        + REASONING_NUMERIC_COLUMNS
        + CONFIDENCE_NUMERIC_COLUMNS
    )
    matrix = [[float(row.get(column, 0.0)) for column in feature_columns] for row in rows]
    labels = [int(row["ground_truth_label"]) for row in rows]
    if len(set(labels)) < 2:
        raise ValueError("Labeled real-pilot fusion dataset must contain at least two classes.")

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("logreg", LogisticRegression(random_state=42, solver="liblinear")),
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
                "schema_version": LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION,
                "run_id": run_id,
                "sample_id": row["sample_id"],
                "base_sample_id": row["base_sample_id"],
                "contract_variant": row["contract_variant"],
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
                    "baseline_name": "labeled_real_pilot_logistic_regression",
                    "label_name": row["label_name"],
                    "label_scope": row["label_scope"],
                    "training_mode": "self_fit_pilot_level_controlled_supervised_fusion_bootstrap",
                },
            }
        )

    summary = {
        "summary_status": "PASS",
        "schema_version": LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION,
        "baseline_name": "labeled_real_pilot_logistic_regression",
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "num_predictions": len(prediction_rows),
        "label_name": rows[0]["label_name"],
        "label_scope": rows[0]["label_scope"],
        "label_threshold": label_threshold,
        "mean_prediction_score": sum(probabilities) / len(probabilities) if probabilities else 0.0,
        "num_positive_predictions": sum(pred["prediction_label"] for pred in prediction_rows),
        "notes": [
            "This supervised logistic path uses pilot-level controlled supervision.",
            "It is a bootstrap self-fit path to prove supervised fusion exists, not a benchmark-grade result.",
        ],
    }
    model_metadata = {
        "schema_version": LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION,
        "baseline_name": "labeled_real_pilot_logistic_regression",
        "feature_columns": feature_columns,
        "intercept": logistic.intercept_.tolist(),
        "coefficients": {name: float(value) for name, value in zip(feature_columns, logistic.coef_[0].tolist())},
        "class_balance": {
            "label_0": labels.count(0),
            "label_1": labels.count(1),
        },
    }
    run_summary = {
        "summary_status": "PASS",
        "schema_version": LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION,
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "num_rows": len(rows),
        "supervised_logistic_completed": True,
        "label_name": rows[0]["label_name"],
        "label_scope": rows[0]["label_scope"],
        "prediction_artifacts": {
            "predictions": str((output_dir / "labeled_real_pilot_logistic_predictions.jsonl").resolve()),
            "summary": str((output_dir / "labeled_real_pilot_logistic_summary.json").resolve()),
            "model_metadata": str((output_dir / "labeled_real_pilot_model_metadata.json").resolve()),
        },
    }

    predictions_path = output_dir / "labeled_real_pilot_logistic_predictions.jsonl"
    summary_path = output_dir / "labeled_real_pilot_logistic_summary.json"
    model_metadata_path = output_dir / "labeled_real_pilot_model_metadata.json"
    run_summary_path = output_dir / "labeled_real_pilot_fusion_run_summary.json"
    config_snapshot_path = output_dir / "config_snapshot.json"

    write_jsonl(predictions_path, prediction_rows)
    write_json(summary_path, summary)
    write_json(model_metadata_path, model_metadata)
    write_json(run_summary_path, run_summary)
    write_json(
        config_snapshot_path,
        {
            "schema_version": LABELED_REAL_PILOT_FUSION_SCHEMA_VERSION,
            "fusion_profile": fusion_profile,
            "run_id": run_id,
            "label_threshold": label_threshold,
            "labeled_real_pilot_fusion_dataset": str(labeled_real_pilot_fusion_dataset_path.resolve()),
        },
    )
    (output_dir / "run.log").write_text(
        "\n".join(
            [
                "TriScope-LLM labeled real-pilot fusion logistic baseline",
                f"Run ID: {run_id}",
                f"Rows: {len(rows)}",
                f"Predictions: {predictions_path.resolve()}",
                f"Summary: {summary_path.resolve()}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "predictions": prediction_rows,
        "summary": summary,
        "model_metadata": model_metadata,
        "run_summary": run_summary,
        "output_paths": {
            "predictions": str(predictions_path.resolve()),
            "summary": str(summary_path.resolve()),
            "model_metadata": str(model_metadata_path.resolve()),
            "run_summary": str(run_summary_path.resolve()),
            "config_snapshot": str(config_snapshot_path.resolve()),
            "log": str((output_dir / "run.log").resolve()),
        },
    }
