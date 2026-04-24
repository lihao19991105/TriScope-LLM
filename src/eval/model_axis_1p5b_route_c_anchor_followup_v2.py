"""Build an anchor-aware baseline-preserving deepening follow-up v2 candidate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json, write_jsonl
from src.fusion.benchmark_truth_leaning_label import (
    CONFIDENCE_NUMERIC_COLUMNS,
    ILLUMINATION_NUMERIC_COLUMNS,
    REASONING_NUMERIC_COLUMNS,
)


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-anchor-followup-v2/v1"
EPS = 1e-12


def _feature_columns() -> list[str]:
    return ILLUMINATION_NUMERIC_COLUMNS + REASONING_NUMERIC_COLUMNS + CONFIDENCE_NUMERIC_COLUMNS


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
            "failure_reason": "Anchor follow-up v2 candidate must contain at least two classes.",
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


def build_model_axis_1p5b_route_c_anchor_followup_v2(
    route_c_anchor_followup_dir: Path,
    route_c_anchor_execution_dir: Path,
    route_c_anchor_stability_dir: Path,
    route_c_anchor_stability_analysis_dir: Path,
    route_c_anchor_deepening_dir: Path,
    route_c_deepened_execution_dir: Path,
    route_c_deepened_analysis_dir: Path,
    route_c_execution_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    anchor_followup_summary = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_candidate_summary.json")
    anchor_followup_registry = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_selection_registry.json")
    neighbor_analysis = load_json(route_c_anchor_followup_dir / "route_c_anchor_neighbor_analysis.json")

    anchor_run_summary = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_run_summary.json")
    anchor_metrics = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_metrics.json")
    anchor_stability = load_json(route_c_anchor_stability_dir / "route_c_anchor_stability_summary.json")
    anchor_recommendation = load_json(
        route_c_anchor_stability_analysis_dir / "route_c_anchor_stability_next_step_recommendation.json"
    )

    deepened_candidate_summary = load_json(route_c_anchor_deepening_dir / "route_c_anchor_deepened_candidate_summary.json")
    deepened_run_summary = load_json(route_c_deepened_execution_dir / "route_c_deepened_execution_run_summary.json")
    deepened_recommendation = load_json(route_c_deepened_analysis_dir / "route_c_deepened_next_step_recommendation.json")
    execution_rows = load_jsonl(route_c_execution_dir / "route_c_execution_run" / "route_c_v6_dataset.jsonl")

    anchor_base_id = str(anchor_followup_registry["anchor_base_sample_id"])
    baseline_neighbor_ids = [str(item) for item in anchor_followup_registry.get("selected_neighbor_base_ids", [])]
    if len(baseline_neighbor_ids) < 2:
        raise ValueError("132 expects anchor-aware baseline to contain two neighbor base ids.")

    ranked_neighbors = neighbor_analysis.get("candidate_neighbors_ranked", [])
    closest_neighbor_id = baseline_neighbor_ids[0]
    baseline_exploration_neighbor_id = baseline_neighbor_ids[1]
    exploration_neighbor_id = next(
        (
            str(item.get("base_sample_id"))
            for item in ranked_neighbors
            if str(item.get("base_sample_id")) not in {closest_neighbor_id, baseline_exploration_neighbor_id}
        ),
        baseline_exploration_neighbor_id,
    )
    strategy_mode = (
        "swap_second_neighbor_for_conservative_probe"
        if exploration_neighbor_id != baseline_exploration_neighbor_id
        else "no_viable_swap_keep_anchor_baseline"
    )

    selected_neighbor_ids = [closest_neighbor_id, exploration_neighbor_id]
    selected_base_ids = [anchor_base_id] + selected_neighbor_ids
    selected_set = set(selected_base_ids)
    candidate_rows = [row for row in execution_rows if str(row.get("base_sample_id")) in selected_set]
    write_jsonl(output_dir / "route_c_anchor_followup_v2_candidate_dataset.jsonl", candidate_rows)

    row_count = len(candidate_rows)
    class_balance = {
        "label_0": sum(1 for row in candidate_rows if int(row.get("ground_truth_label", 0)) == 0),
        "label_1": sum(1 for row in candidate_rows if int(row.get("ground_truth_label", 0)) == 1),
    }
    candidate_density = (float(class_balance["label_1"]) / float(row_count)) if row_count > 0 else None
    anchor_density = float(anchor_metrics.get("anchor_density", 0.0) or 0.0)
    refined_density = float(anchor_metrics.get("refined_density", 0.0) or 0.0)
    deepened_density = float(deepened_run_summary.get("deepened_density", 0.0) or 0.0)
    density_preserved_vs_anchor = bool(candidate_density is not None and candidate_density + EPS >= anchor_density)
    two_classes = bool(class_balance["label_0"] > 0 and class_balance["label_1"] > 0)

    reference_anchor_sample_ids = [str(item) for item in anchor_run_summary.get("positive_support_sample_ids", []) or []]
    candidate_positive_sample_ids = [
        str(row["sample_id"])
        for row in candidate_rows
        if int(row.get("ground_truth_label", 0)) == 1
    ]
    reference_anchor_preserved = all(item in candidate_positive_sample_ids for item in reference_anchor_sample_ids)

    precheck = _logistic_precheck(candidate_rows)

    constraints = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "working_baseline_from_131": deepened_recommendation.get("working_baseline"),
        "anchor_density_floor": anchor_density,
        "refined_density_floor": refined_density,
        "reference_anchor_sample_ids": reference_anchor_sample_ids,
        "must_preserve_reference_anchor": True,
        "must_preserve_two_classes": True,
        "must_avoid_density_fall_back_to_refined_floor": True,
        "why_128_deepened_fell_back_to_1_over_8": {
            "anchor_followup_contract_count": int(anchor_followup_summary.get("selected_contract_count", 0) or 0),
            "deepened_contract_count": int(deepened_candidate_summary.get("selected_contract_count", 0) or 0),
            "anchor_positive_count": int(anchor_followup_summary.get("class_balance", {}).get("label_1", 0) or 0),
            "deepened_positive_count": int(deepened_candidate_summary.get("class_balance", {}).get("label_1", 0) or 0),
            "anchor_density": float(anchor_followup_summary.get("anchor_followup_density", 0.0) or 0.0),
            "deepened_density": float(deepened_candidate_summary.get("deepened_density", 0.0) or 0.0),
            "explanation": (
                "128 added one more negative-only base (6->8 contracts) while positive support stayed at 1, "
                "so density dropped from 1/6 to 1/8."
            ),
        },
        "how_132_avoids_repeat": [
            "Keep base count capped at 3 (anchor + 2 neighbors) so denominator stays at 6 instead of 8.",
            "Preserve the closest anchor neighbor and only probe one replacement slot for conservative local variation.",
            "Require density >= anchor baseline and reference anchor preservation as precheck gates.",
        ],
        "anchor_stability_prerequisites": {
            "stability_established": bool(anchor_stability.get("stability_established")),
            "stability_characterization": anchor_stability.get("stability_characterization"),
            "recommended_next_step": anchor_recommendation.get("recommended_next_step"),
        },
    }

    strategy = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "strategy_name": "anchor_preserving_neighbor_swap_probe",
        "strategy_mode": strategy_mode,
        "relationship_to_123_anchor_followup": {
            "base_anchor_reused": True,
            "same_regime_neighbor_pool": True,
            "contract_budget": "same_6_contract_budget",
            "difference": "Keep nearest neighbor fixed and replace only one secondary neighbor slot for conservative probing.",
        },
        "difference_vs_128_deepened": {
            "v128_selected_base_count": int(deepened_candidate_summary.get("selected_base_count", 0) or 0),
            "v132_selected_base_count": len(selected_base_ids),
            "v128_density": float(deepened_candidate_summary.get("deepened_density", 0.0) or 0.0),
            "v132_target_density_floor": anchor_density,
            "characterization": "more_conservative_deepening",
        },
        "baseline_anchor_base_id": anchor_base_id,
        "baseline_neighbor_ids": baseline_neighbor_ids,
        "v2_neighbor_ids": selected_neighbor_ids,
        "success_criteria": [
            "class_balance has both labels",
            "candidate_density >= anchor_density_floor (1/6)",
            "reference anchor sample remains present",
            "precheck logistic stays PASS",
            "candidate differs from baseline by exactly one controlled neighbor swap",
        ],
    }

    selection_registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "anchor_base_sample_id": anchor_base_id,
        "baseline_neighbor_base_ids": baseline_neighbor_ids,
        "selected_neighbor_base_ids": selected_neighbor_ids,
        "swapped_out_neighbor_base_id": baseline_exploration_neighbor_id,
        "swapped_in_neighbor_base_id": exploration_neighbor_id,
        "selected_base_ids": selected_base_ids,
        "selection_strategy": strategy.get("strategy_name"),
        "strategy_mode": strategy_mode,
        "source_anchor_followup_registry": str(
            (route_c_anchor_followup_dir / "route_c_anchor_followup_selection_registry.json").resolve()
        ),
    }

    candidate_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": row_count,
        "class_balance": class_balance,
        "anchor_density_floor": anchor_density,
        "candidate_density": candidate_density,
        "deepened_density_reference": deepened_density,
        "density_vs_anchor": (
            candidate_density / anchor_density if candidate_density is not None and anchor_density > 0 else None
        ),
        "density_vs_refined": (
            candidate_density / refined_density if candidate_density is not None and refined_density > 0 else None
        ),
        "density_vs_128_deepened": (
            candidate_density / deepened_density if candidate_density is not None and deepened_density > 0 else None
        ),
        "reference_anchor_preserved": reference_anchor_preserved,
        "swapped_neighbor": bool(strategy_mode == "swap_second_neighbor_for_conservative_probe"),
        "extension_style": "conservative_swap_not_budget_expansion",
    }

    worth_executing = bool(
        precheck.get("precheck_logistic_pass")
        and two_classes
        and density_preserved_vs_anchor
        and reference_anchor_preserved
        and strategy_mode == "swap_second_neighbor_for_conservative_probe"
    )
    precheck_payload = {
        "summary_status": "PASS" if precheck.get("precheck_logistic_pass") else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "row_count": row_count,
        "class_balance": class_balance,
        "has_two_classes": two_classes,
        "candidate_density": candidate_density,
        "anchor_density_floor": anchor_density,
        "density_preserved_vs_anchor": density_preserved_vs_anchor,
        "reference_anchor_preserved": reference_anchor_preserved,
        "precheck_logistic_pass": bool(precheck.get("precheck_logistic_pass")),
        "prediction_rows": precheck.get("prediction_rows", []),
        "worth_executing": worth_executing,
        "worth_executing_reason": (
            "Candidate preserves anchor density floor, keeps two classes, keeps reference anchor, and introduces one controlled neighbor swap for measurable execution value."
            if worth_executing
            else "Candidate fails baseline-preserving gate or does not provide a meaningful controlled variation."
        ),
        "failure_reason": precheck.get("failure_reason"),
    }

    readiness = {
        "summary_status": "PASS" if worth_executing else "PASS_WITH_LIMITATIONS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "ready_for_execution": worth_executing,
        "strategy_mode": strategy_mode,
        "selected_base_ids": selected_base_ids,
        "row_count": row_count,
        "class_balance": class_balance,
        "candidate_density": candidate_density,
        "anchor_density_floor": anchor_density,
        "density_preserved_vs_anchor": density_preserved_vs_anchor,
        "reference_anchor_preserved": reference_anchor_preserved,
        "execution_if_selected": "promote_to_133_anchor_baseline_preserving_execution",
    }

    write_json(output_dir / "route_c_anchor_preservation_constraints.json", constraints)
    write_json(output_dir / "route_c_anchor_followup_v2_strategy.json", strategy)
    write_json(output_dir / "route_c_anchor_followup_v2_selection_registry.json", selection_registry)
    write_json(output_dir / "route_c_anchor_followup_v2_candidate_summary.json", candidate_summary)
    write_json(output_dir / "route_c_anchor_followup_v2_precheck.json", precheck_payload)
    write_json(output_dir / "route_c_anchor_followup_v2_readiness_summary.json", readiness)

    return {
        "summary": candidate_summary,
        "output_paths": {
            "constraints": str((output_dir / "route_c_anchor_preservation_constraints.json").resolve()),
            "strategy": str((output_dir / "route_c_anchor_followup_v2_strategy.json").resolve()),
            "selection_registry": str((output_dir / "route_c_anchor_followup_v2_selection_registry.json").resolve()),
            "candidate_summary": str((output_dir / "route_c_anchor_followup_v2_candidate_summary.json").resolve()),
            "precheck": str((output_dir / "route_c_anchor_followup_v2_precheck.json").resolve()),
            "readiness": str((output_dir / "route_c_anchor_followup_v2_readiness_summary.json").resolve()),
        },
    }
