"""Minimal missingness-aware fusion baselines for TriScope-LLM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


PREDICTION_SCHEMA_VERSION = "triscopellm/fusion-predictions/v1"


def safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    return float(value)


def build_prediction_row(
    row: dict[str, Any],
    run_id: str,
    fusion_profile: str,
    baseline_name: str,
    prediction_score: float,
    label_threshold: float,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": PREDICTION_SCHEMA_VERSION,
        "run_id": run_id,
        "sample_id": row["sample_id"],
        "fusion_profile": fusion_profile,
        "baseline_name": baseline_name,
        "prediction_score": prediction_score,
        "prediction_label": 1 if prediction_score >= label_threshold else 0,
        "label_threshold": label_threshold,
        "ground_truth_label": row["ground_truth_label"],
        "illumination_present": bool(row["illumination_present"]),
        "reasoning_present": bool(row["reasoning_present"]),
        "confidence_present": bool(row["confidence_present"]),
        "modality_count": int(row["modality_count"]),
        "metadata": metadata,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def run_rule_baseline(
    rows: list[dict[str, Any]],
    run_id: str,
    fusion_profile: str,
    label_threshold: float = 0.5,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    for row in rows:
        components: dict[str, float] = {}
        if row["illumination_present"]:
            components["illumination"] = safe_float(
                row.get("illumination__target_behavior_label_filled", 0.0)
            )
        if row["reasoning_present"]:
            components["reasoning"] = (
                0.7 * safe_float(row.get("reasoning__answer_changed_after_reasoning_filled", 0.0))
                + 0.3 * safe_float(row.get("reasoning__target_behavior_flip_flag_filled", 0.0))
            )
        if row["confidence_present"]:
            normalized_run = min(
                1.0,
                safe_float(row.get("confidence__max_consecutive_high_confidence_steps_filled", 0.0)) / 10.0,
            )
            normalized_collapse = min(
                1.0,
                max(0.0, safe_float(row.get("confidence__entropy_collapse_score_filled", 0.0)) * 100.0),
            )
            components["confidence"] = (
                0.5 * safe_float(row.get("confidence__high_confidence_fraction_filled", 0.0))
                + 0.3 * normalized_run
                + 0.2 * normalized_collapse
            )

        score = sum(components.values()) / len(components) if components else 0.0
        predictions.append(
            build_prediction_row(
                row=row,
                run_id=run_id,
                fusion_profile=fusion_profile,
                baseline_name="rule_based",
                prediction_score=score,
                label_threshold=label_threshold,
                metadata={
                    "available_components": sorted(components),
                    "component_scores": components,
                    "missingness_strategy": "skip missing modalities and average available modality components",
                },
            )
        )

    summary = {
        "summary_status": "PASS",
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "baseline_name": "rule_based",
        "num_predictions": len(predictions),
        "label_threshold": label_threshold,
        "mean_prediction_score": sum(row["prediction_score"] for row in predictions) / len(predictions),
        "num_positive_predictions": sum(row["prediction_label"] for row in predictions),
    }
    return predictions, summary


def run_logistic_baseline(
    rows: list[dict[str, Any]],
    run_id: str,
    fusion_profile: str,
    feature_columns: list[str],
    label_threshold: float = 0.5,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    if not rows:
        raise ValueError("Cannot fit logistic baseline on an empty preprocessed dataset.")

    labels = [int(row["ground_truth_label"]) for row in rows]
    if len(set(labels)) < 2:
        raise ValueError("Logistic baseline requires at least two classes in the preprocessed dataset.")

    matrix = [[safe_float(row.get(column, 0.0)) for column in feature_columns] for row in rows]
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "logistic",
                LogisticRegression(
                    random_state=seed,
                    max_iter=1000,
                    solver="liblinear",
                ),
            ),
        ]
    )
    pipeline.fit(matrix, labels)
    probabilities = pipeline.predict_proba(matrix)[:, 1].tolist()
    predicted_labels = pipeline.predict(matrix).tolist()

    predictions: list[dict[str, Any]] = []
    for row, probability, predicted_label in zip(rows, probabilities, predicted_labels):
        predictions.append(
            build_prediction_row(
                row=row,
                run_id=run_id,
                fusion_profile=fusion_profile,
                baseline_name="logistic_regression",
                prediction_score=float(probability),
                label_threshold=label_threshold,
                metadata={
                    "selected_feature_columns": feature_columns,
                    "missingness_strategy": "zero-fill numeric features with explicit present/missing flags",
                    "standardized": True,
                    "train_mode": "self_fit_smoke",
                    "predicted_label_from_model": int(predicted_label),
                },
            )
        )

    logistic = pipeline.named_steps["logistic"]
    summary = {
        "summary_status": "PASS",
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "baseline_name": "logistic_regression",
        "num_predictions": len(predictions),
        "label_threshold": label_threshold,
        "num_feature_columns": len(feature_columns),
        "mean_prediction_score": sum(row["prediction_score"] for row in predictions) / len(predictions),
        "num_positive_predictions": sum(row["prediction_label"] for row in predictions),
        "train_mode": "self_fit_smoke",
        "standardized": True,
    }
    model_metadata = {
        "summary_status": "PASS",
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "baseline_name": "logistic_regression",
        "feature_columns": feature_columns,
        "num_training_rows": len(rows),
        "num_positive_labels": sum(labels),
        "num_negative_labels": len(labels) - sum(labels),
        "standardized": True,
        "missingness_strategy": "zero-fill numeric features with explicit present/missing flags",
        "solver": logistic.solver,
        "max_iter": logistic.max_iter,
        "classes": logistic.classes_.tolist(),
        "intercept": logistic.intercept_.tolist(),
        "coefficients": {
            feature_name: float(weight)
            for feature_name, weight in zip(feature_columns, logistic.coef_[0].tolist())
        },
    }
    return predictions, summary, model_metadata
