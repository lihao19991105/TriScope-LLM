"""Build an anchor-aware route_c follow-up candidate around the lone stable positive anchor."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.fusion.benchmark_truth_leaning_label import (
    CONFIDENCE_NUMERIC_COLUMNS,
    ILLUMINATION_NUMERIC_COLUMNS,
    REASONING_NUMERIC_COLUMNS,
)


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-anchor-followup/v1"


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


def _feature_columns() -> list[str]:
    return ILLUMINATION_NUMERIC_COLUMNS + REASONING_NUMERIC_COLUMNS + CONFIDENCE_NUMERIC_COLUMNS


def _get_source_metadata(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("metadata", {}).get("source_contract_metadata", {})


def _euclidean_distance(row_a: dict[str, Any], row_b: dict[str, Any], columns: list[str]) -> float:
    return math.sqrt(sum((float(row_a.get(column, 0.0)) - float(row_b.get(column, 0.0))) ** 2 for column in columns))


def _logistic_precheck(rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [int(row.get("ground_truth_label", 0)) for row in rows]
    class_balance = {
        "label_0": sum(1 for label in labels if label == 0),
        "label_1": sum(1 for label in labels if label == 1),
    }
    if len(set(labels)) < 2:
        return {
            "summary_status": "BLOCKED",
            "precheck_logistic_pass": False,
            "failure_reason": "Anchor-aware follow-up dataset must contain at least two classes.",
            "class_balance": class_balance,
            "prediction_rows": [],
        }

    feature_columns = _feature_columns()
    matrix = [[float(row.get(column, 0.0)) for column in feature_columns] for row in rows]
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(random_state=42, max_iter=500, class_weight="balanced")),
        ]
    )
    pipeline.fit(matrix, labels)
    probabilities = pipeline.predict_proba(matrix)
    predictions = pipeline.predict(matrix)
    prediction_rows = [
        {
            "sample_id": str(row["sample_id"]),
            "base_sample_id": str(row["base_sample_id"]),
            "contract_variant": str(row["contract_variant"]),
            "ground_truth_label": int(row["ground_truth_label"]),
            "positive_probability": float(probability[1]),
            "predicted_label": int(prediction),
        }
        for row, probability, prediction in zip(rows, probabilities, predictions)
    ]
    return {
        "summary_status": "PASS",
        "precheck_logistic_pass": True,
        "class_balance": class_balance,
        "prediction_rows": prediction_rows,
    }


def build_model_axis_1p5b_route_c_anchor_followup(
    route_c_execution_dir: Path,
    route_c_refined_execution_dir: Path,
    route_c_refined_stability_dir: Path,
    route_c_refined_analysis_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    original_rows = load_jsonl(route_c_execution_dir / "route_c_execution_run" / "route_c_v6_dataset.jsonl")
    refined_rows = load_jsonl(route_c_refined_execution_dir / "route_c_refined_execution_run" / "route_c_v6_dataset.jsonl")
    refined_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    refined_stability = load_json(route_c_refined_stability_dir / "route_c_refined_stability_summary.json")
    refined_analysis = load_json(route_c_refined_analysis_dir / "route_c_refined_analysis_summary.json")

    positive_rows = [row for row in refined_rows if int(row.get("ground_truth_label", 0)) == 1]
    if len(positive_rows) != 1:
        raise ValueError("123 expects exactly one positive row in the refined route_c execution baseline.")
    anchor_positive_row = positive_rows[0]
    anchor_base_id = str(anchor_positive_row["base_sample_id"])
    anchor_control_row = next(
        row for row in refined_rows if str(row["base_sample_id"]) == anchor_base_id and str(row["contract_variant"]) == "control"
    )
    anchor_metadata = _get_source_metadata(anchor_positive_row)

    feature_columns = _feature_columns()
    base_to_rows: dict[str, list[dict[str, Any]]] = {}
    for row in original_rows:
        base_to_rows.setdefault(str(row["base_sample_id"]), []).append(row)

    candidate_neighbors: list[dict[str, Any]] = []
    for base_id, rows in sorted(base_to_rows.items()):
        if base_id == anchor_base_id:
            continue
        control_row = next(row for row in rows if str(row["contract_variant"]) == "control")
        targeted_row = next(row for row in rows if str(row["contract_variant"]) == "targeted")
        control_metadata = _get_source_metadata(control_row)
        same_query_key = str(control_row.get("query_answer_key")) == str(anchor_positive_row.get("query_answer_key"))
        same_forced_target = str(control_metadata.get("forced_target_label")) == str(anchor_metadata.get("forced_target_label"))
        if not (same_query_key and same_forced_target):
            continue
        distance = _euclidean_distance(control_row, anchor_control_row, feature_columns)
        candidate_neighbors.append(
            {
                "base_sample_id": base_id,
                "same_query_key": same_query_key,
                "same_forced_target": same_forced_target,
                "query_answer_key": str(control_row.get("query_answer_key")),
                "forced_target_label": str(control_metadata.get("forced_target_label")),
                "targeted_label": int(targeted_row.get("ground_truth_label", 0)),
                "control_label": int(control_row.get("ground_truth_label", 0)),
                "targeted_response_option": str(targeted_row.get("illumination_response_option")),
                "control_response_option": str(control_row.get("illumination_response_option")),
                "feature_distance_to_anchor": distance,
                "confidence_mean_chosen_token_prob": float(control_row.get("confidence__mean_chosen_token_prob", 0.0)),
                "confidence_mean_entropy": float(control_row.get("confidence__mean_entropy", 0.0)),
                "reasoning_step_count": float(control_row.get("reasoning__reasoning_step_count", 0.0)),
                "reasoning_target_flip_flag": float(control_row.get("reasoning__target_behavior_flip_flag", 0.0)),
            }
        )

    candidate_neighbors.sort(key=lambda row: (float(row["feature_distance_to_anchor"]), str(row["base_sample_id"])))
    selected_neighbor_base_ids = [str(row["base_sample_id"]) for row in candidate_neighbors[:2]]
    selected_base_ids = [anchor_base_id] + selected_neighbor_base_ids

    followup_rows = [row for row in original_rows if str(row["base_sample_id"]) in set(selected_base_ids)]
    precheck = _logistic_precheck(followup_rows)

    row_count = len(followup_rows)
    class_balance = precheck["class_balance"]
    anchor_density = float(class_balance["label_1"]) / float(row_count) if row_count > 0 else None
    refined_density = float(refined_metrics.get("refined_density", 0.0) or 0.0)
    original_density = float(refined_analysis.get("original_density", 0.0) or 0.0)

    anchor_profile = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "anchor_sample_id": str(anchor_positive_row["sample_id"]),
        "anchor_base_sample_id": anchor_base_id,
        "anchor_contract_variant": str(anchor_positive_row["contract_variant"]),
        "anchor_query_answer_key": str(anchor_positive_row["query_answer_key"]),
        "anchor_forced_target_label": str(anchor_metadata.get("forced_target_label")),
        "anchor_response_option": str(anchor_positive_row.get("illumination_response_option")),
        "anchor_ground_truth_label": int(anchor_positive_row.get("ground_truth_label", 0)),
        "anchor_control_sample_id": str(anchor_control_row["sample_id"]),
        "anchor_control_response_option": str(anchor_control_row.get("illumination_response_option")),
        "anchor_confidence_profile": {
            "mean_chosen_token_prob": float(anchor_control_row.get("confidence__mean_chosen_token_prob", 0.0)),
            "mean_entropy": float(anchor_control_row.get("confidence__mean_entropy", 0.0)),
            "high_confidence_fraction": float(anchor_control_row.get("confidence__high_confidence_fraction", 0.0)),
            "entropy_collapse_score": float(anchor_control_row.get("confidence__entropy_collapse_score", 0.0)),
        },
        "anchor_reasoning_profile": {
            "answer_changed_after_reasoning": float(anchor_control_row.get("reasoning__answer_changed_after_reasoning", 0.0)),
            "target_behavior_flip_flag": float(anchor_control_row.get("reasoning__target_behavior_flip_flag", 0.0)),
            "reasoning_length": float(anchor_control_row.get("reasoning__reasoning_length", 0.0)),
            "reasoning_step_count": float(anchor_control_row.get("reasoning__reasoning_step_count", 0.0)),
        },
        "notes": [
            "The stable positive anchor remains a task-answer-incorrect targeted contract rather than a direct target-behavior hit.",
            "Anchor-aware follow-up therefore focuses on nearby negatives that share the same query-answer and forced-target regime.",
        ],
    }
    neighbor_analysis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "anchor_base_sample_id": anchor_base_id,
        "candidate_neighbor_count": len(candidate_neighbors),
        "candidate_neighbors_ranked": candidate_neighbors,
        "selected_neighbor_base_ids": selected_neighbor_base_ids,
        "selection_rationale": [
            "Neighbors are constrained to the same query_answer_key and forced_target_label regime as the anchor.",
            "The top two nearest negatives are selected to raise density above the 1/8 refined baseline without reopening blind budget expansion.",
        ],
    }
    selection_strategy = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "strategy_name": "anchor_plus_same_regime_nearest_negatives",
        "anchor_base_sample_id": anchor_base_id,
        "selected_neighbor_base_ids": selected_neighbor_base_ids,
        "selected_base_ids": selected_base_ids,
        "neighbor_pool_constraints": {
            "same_query_answer_key_as_anchor": True,
            "same_forced_target_label_as_anchor": True,
            "rank_by_control_feature_distance_to_anchor": True,
        },
        "why_this_strategy": [
            "122 recommends continuing refined selection before any budget expansion.",
            "The lone positive anchor lives in the A/B regime, so anchor-aware follow-up should stay inside that regime first.",
            "Keeping only the nearest negatives increases density while preserving at least three bases for a minimally honest follow-up execution.",
        ],
        "rejected_alternatives": [
            "blindly adding more A/B negatives from the original 24-row subset",
            "reopening the full 140-contract universe",
            "switching away from the stable positive anchor before testing its local neighborhood",
        ],
    }

    selection_registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup",
        "anchor_base_sample_id": anchor_base_id,
        "selected_neighbor_base_ids": selected_neighbor_base_ids,
        "selected_base_ids": selected_base_ids,
        "selection_strategy": selection_strategy["strategy_name"],
        "source_route_c_execution_dir": str(route_c_execution_dir.resolve()),
        "source_route_c_refined_execution_dir": str(route_c_refined_execution_dir.resolve()),
    }
    candidate_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup",
        "anchor_base_sample_id": anchor_base_id,
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": row_count,
        "class_balance": class_balance,
        "original_density": original_density,
        "refined_density": refined_density,
        "anchor_followup_density": anchor_density,
        "density_gain_vs_original": (anchor_density / original_density) if anchor_density is not None and original_density > 0 else None,
        "density_gain_vs_refined": (anchor_density / refined_density) if anchor_density is not None and refined_density > 0 else None,
        "incremental_positive_support_count_vs_refined": int(class_balance["label_1"]) - 1,
        "notes": [
            "This follow-up candidate still preserves the same single positive anchor.",
            "Its expected value comes from denser local analysis, not from claiming new positives before execution confirms them.",
        ],
    }
    precheck_payload = {
        "summary_status": "PASS" if precheck["precheck_logistic_pass"] else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup",
        "row_count": row_count,
        "class_balance": class_balance,
        "anchor_followup_density": anchor_density,
        "refined_density": refined_density,
        "density_gain_vs_refined": candidate_summary["density_gain_vs_refined"],
        "precheck_logistic_pass": precheck["precheck_logistic_pass"],
        "prediction_rows": precheck["prediction_rows"],
        "worth_executing": bool(
            precheck["precheck_logistic_pass"]
            and class_balance["label_0"] > 0
            and class_balance["label_1"] > 0
            and anchor_density is not None
            and anchor_density > refined_density
            and bool(refined_stability.get("stability_established"))
        ),
        "worth_executing_reason": (
            "The follow-up candidate keeps two classes, passes a lightweight logistic precheck, and improves density over the 1/8 refined baseline."
            if (
                precheck["precheck_logistic_pass"]
                and class_balance["label_0"] > 0
                and class_balance["label_1"] > 0
                and anchor_density is not None
                and anchor_density > refined_density
            )
            else "The follow-up candidate does not yet beat the refined baseline with enough confidence."
        ),
        "failure_reason": precheck.get("failure_reason"),
    }

    write_json(output_dir / "route_c_anchor_profile.json", anchor_profile)
    write_json(output_dir / "route_c_anchor_neighbor_analysis.json", neighbor_analysis)
    write_json(output_dir / "route_c_anchor_selection_strategy.json", selection_strategy)
    write_json(output_dir / "route_c_anchor_followup_selection_registry.json", selection_registry)
    write_jsonl(output_dir / "route_c_anchor_followup_candidate_dataset.jsonl", followup_rows)
    write_json(output_dir / "route_c_anchor_followup_candidate_summary.json", candidate_summary)
    write_json(output_dir / "route_c_anchor_followup_precheck.json", precheck_payload)

    return {
        "summary": candidate_summary,
        "output_paths": {
            "anchor_profile": str((output_dir / "route_c_anchor_profile.json").resolve()),
            "neighbor_analysis": str((output_dir / "route_c_anchor_neighbor_analysis.json").resolve()),
            "selection_strategy": str((output_dir / "route_c_anchor_selection_strategy.json").resolve()),
            "selection_registry": str((output_dir / "route_c_anchor_followup_selection_registry.json").resolve()),
            "candidate_summary": str((output_dir / "route_c_anchor_followup_candidate_summary.json").resolve()),
            "precheck": str((output_dir / "route_c_anchor_followup_precheck.json").resolve()),
        },
    }
