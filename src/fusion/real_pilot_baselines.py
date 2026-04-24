"""Real-pilot fusion baselines for TriScope-LLM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REAL_PILOT_PREDICTION_SCHEMA_VERSION = "triscopellm/real-pilot-fusion-predictions/v1"


def safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    return float(value)


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
        "schema_version": REAL_PILOT_PREDICTION_SCHEMA_VERSION,
        "run_id": run_id,
        "sample_id": row["sample_id"],
        "fusion_profile": fusion_profile,
        "baseline_name": baseline_name,
        "prediction_score": prediction_score,
        "prediction_label": 1 if prediction_score >= label_threshold else 0,
        "label_threshold": label_threshold,
        "illumination_present": bool(row["illumination_present"]),
        "reasoning_present": bool(row["reasoning_present"]),
        "confidence_present": bool(row["confidence_present"]),
        "modality_count": int(row["modality_count"]),
        "metadata": metadata,
    }


def run_real_pilot_rule_baseline(
    rows: list[dict[str, Any]],
    run_id: str,
    fusion_profile: str,
    label_threshold: float = 0.5,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    for row in rows:
        components: dict[str, float] = {}
        if row.get("illumination_present"):
            components["illumination"] = safe_float(row.get("illumination__target_behavior_label", 0.0))
        if row.get("reasoning_present"):
            components["reasoning"] = (
                0.7 * safe_float(row.get("reasoning__answer_changed_after_reasoning", 0.0))
                + 0.3 * safe_float(row.get("reasoning__target_behavior_flip_flag", 0.0))
            )
        if row.get("confidence_present"):
            normalized_run = min(
                1.0,
                safe_float(row.get("confidence__max_consecutive_high_confidence_steps", 0.0)) / 10.0,
            )
            normalized_collapse = min(
                1.0,
                max(0.0, safe_float(row.get("confidence__entropy_collapse_score", 0.0)) / 2.0),
            )
            components["confidence"] = (
                0.5 * safe_float(row.get("confidence__high_confidence_fraction", 0.0))
                + 0.3 * normalized_run
                + 0.2 * normalized_collapse
            )

        score = sum(components.values()) / len(components) if components else 0.0
        predictions.append(
            build_prediction_row(
                row=row,
                run_id=run_id,
                fusion_profile=fusion_profile,
                baseline_name="real_pilot_rule_based",
                prediction_score=score,
                label_threshold=label_threshold,
                metadata={
                    "available_components": sorted(components),
                    "component_scores": components,
                    "ground_truth_label_available": False,
                    "interpretation_scope": "pilot_level_risk_score_only",
                },
            )
        )

    summary = {
        "summary_status": "PASS",
        "schema_version": REAL_PILOT_PREDICTION_SCHEMA_VERSION,
        "run_id": run_id,
        "fusion_profile": fusion_profile,
        "baseline_name": "real_pilot_rule_based",
        "num_predictions": len(predictions),
        "label_threshold": label_threshold,
        "mean_prediction_score": sum(row["prediction_score"] for row in predictions) / len(predictions) if predictions else 0.0,
        "num_positive_predictions": sum(row["prediction_label"] for row in predictions),
        "ground_truth_label_available": False,
    }
    return predictions, summary


def assess_logistic_feasibility(readiness_summary: dict[str, Any]) -> dict[str, Any]:
    if readiness_summary.get("ground_truth_label_available") is not True:
        return {
            "summary_status": "SKIP",
            "baseline_name": "real_pilot_logistic_regression",
            "can_run": False,
            "reason": "missing_ground_truth_labels",
            "notes": [
                "The current real-pilot fusion dataset is aligned and non-empty, but it does not include supervised backdoor labels.",
                "A supervised logistic baseline would be misleading here, so the pipeline records a structured skip instead of fitting a model.",
            ],
        }
    return {
        "summary_status": "PASS",
        "baseline_name": "real_pilot_logistic_regression",
        "can_run": True,
        "reason": "labels_available",
    }
