"""Compare old and larger-split supervision routes after symmetric reruns."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/symmetric-larger-split-comparison/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Expected at least one CSV row.")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_symmetric_larger_split_comparison(
    old_route_b_dir: Path,
    larger_route_b_dir: Path,
    larger_route_c_dir: Path,
    expanded_route_c_dir: Path,
    post_rerun_dir: Path,
    larger_split_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    old_b_summary = load_json(old_route_b_dir / "more_natural_label_summary.json")
    old_b_logistic = load_json(old_route_b_dir / "more_natural_logistic_summary.json")
    larger_b_summary = load_json(larger_route_b_dir / "expanded_more_natural_summary.json")
    larger_b_logistic = load_json(larger_route_b_dir / "expanded_more_natural_logistic_summary.json")
    larger_c_summary = load_json(larger_route_c_dir / "larger_split_route_c_summary.json")
    larger_c_logistic = load_json(larger_route_c_dir / "larger_split_route_c_logistic_summary.json")
    expanded_c_summary = load_json(expanded_route_c_dir / "expanded_benchmark_truth_leaning_summary.json")
    expanded_c_logistic = load_json(expanded_route_c_dir / "expanded_benchmark_truth_leaning_logistic_summary.json")
    post_rerun_recommendation = load_json(post_rerun_dir / "post_rerun_next_step_recommendation.json")
    larger_split_summary = load_json(larger_split_dir / "larger_labeled_split_summary.json")

    comparison_rows = [
        {
            "route_code": "B_old",
            "route_name": "more_natural_supervision_proxy",
            "substrate_level": "original_real_pilot_fusion",
            "num_rows": old_b_summary["num_rows"],
            "num_base_samples": old_b_summary["num_base_samples"],
            "label_scope": old_b_summary["label_scope"],
            "label_naturalness_level": old_b_summary["label_naturalness_level"],
            "mean_prediction_score": old_b_logistic["mean_prediction_score"],
            "num_predictions": old_b_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "B_larger",
            "route_name": "more_natural_supervision_proxy",
            "substrate_level": "larger_labeled_split",
            "num_rows": larger_b_summary["num_rows"],
            "num_base_samples": larger_b_summary["num_base_samples"],
            "label_scope": larger_b_summary["label_scope"],
            "label_naturalness_level": larger_b_summary["label_naturalness_level"],
            "mean_prediction_score": larger_b_logistic["mean_prediction_score"],
            "num_predictions": larger_b_logistic["num_predictions"],
            "comparison_role": "symmetric_larger_split_candidate",
        },
        {
            "route_code": "C_larger",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "substrate_level": "larger_labeled_split",
            "num_rows": larger_c_summary["num_rows"],
            "num_base_samples": larger_c_summary["num_base_samples"],
            "label_scope": larger_c_summary["label_scope"],
            "label_naturalness_level": larger_c_summary["label_naturalness_level"],
            "mean_prediction_score": larger_c_logistic["mean_prediction_score"],
            "num_predictions": larger_c_logistic["num_predictions"],
            "comparison_role": "symmetric_larger_split_candidate",
        },
        {
            "route_code": "C_expanded",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "substrate_level": "expanded_labeled_slice",
            "num_rows": expanded_c_summary["num_rows"],
            "num_base_samples": expanded_c_summary["num_base_samples"],
            "label_scope": expanded_c_summary["label_scope"],
            "label_naturalness_level": expanded_c_summary["label_naturalness_level"],
            "mean_prediction_score": expanded_c_logistic["mean_prediction_score"],
            "num_predictions": expanded_c_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
    ]

    progression_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "larger_split_context": {
            "split_name": larger_split_summary["split_name"],
            "num_rows": larger_split_summary["num_rows"],
            "num_base_samples": larger_split_summary["num_base_samples"],
        },
        "progression": {
            "route_b_old_rows": old_b_summary["num_rows"],
            "route_b_larger_rows": larger_b_summary["num_rows"],
            "route_c_expanded_rows": expanded_c_summary["num_rows"],
            "route_c_larger_rows": larger_c_summary["num_rows"],
            "route_b_old_base_samples": old_b_summary["num_base_samples"],
            "route_b_larger_base_samples": larger_b_summary["num_base_samples"],
            "route_c_expanded_base_samples": expanded_c_summary["num_base_samples"],
            "route_c_larger_base_samples": larger_c_summary["num_base_samples"],
        },
        "main_takeaway": "B and C now both exist on the same 20-row larger split, so the substrate asymmetry has been materially reduced and the next common ceiling is the substrate itself.",
    }

    tradeoff_rows = [
        {
            "route_code": "B_larger",
            "route_name": "more_natural_supervision_proxy",
            "truth_anchor_level": larger_b_summary["label_naturalness_level"],
            "substrate_level": "larger_labeled_split",
            "current_rows": larger_b_summary["num_rows"],
            "current_base_samples": larger_b_summary["num_base_samples"],
            "realism": "medium",
            "cost_to_expand_further": "medium",
            "next_ceiling": "shared_substrate_size",
            "why": "B is now symmetric in substrate size but still weaker in truth anchoring than route C.",
        },
        {
            "route_code": "C_larger",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "truth_anchor_level": larger_c_summary["label_naturalness_level"],
            "substrate_level": "larger_labeled_split",
            "current_rows": larger_c_summary["num_rows"],
            "current_base_samples": larger_c_summary["num_base_samples"],
            "realism": "medium_high",
            "cost_to_expand_further": "medium",
            "next_ceiling": "shared_substrate_size",
            "why": "C keeps the stronger truth-leaning semantics, but both B and C now hit the same substrate ceiling.",
        },
        {
            "route_code": "substrate_v2",
            "route_name": "larger_labeled_split_v2",
            "truth_anchor_level": "shared_substrate_enabler",
            "substrate_level": "next_bootstrap",
            "current_rows": larger_split_summary["num_rows"],
            "current_base_samples": larger_split_summary["num_base_samples"],
            "realism": "enabler",
            "cost_to_expand_further": "medium",
            "next_ceiling": "local_curated_split_growth",
            "why": "A larger shared substrate would unlock the next symmetric comparison step for both B and C.",
        },
    ]

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "symmetric_larger_split_ready": True,
        "main_question_answer": "After symmetric larger-split reruns are available, the next highest-value step is to prepare a larger labeled split v2, because both B and C now share the same substrate ceiling.",
        "why": [
            "Route B and route C now both run on the same 20-row larger split.",
            "Route C retains the stronger truth-leaning supervision semantics, while route B retains a cheaper more-natural proxy path.",
            "The dominant remaining bottleneck is no longer rerun asymmetry but the shared substrate size itself.",
        ],
        "historical_context": {
            "post_rerun_recommendation": post_rerun_recommendation.get("recommended_next_step"),
        },
    }
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "prepare_larger_labeled_split_v2",
        "why_recommended": [
            "B and C have now both been exercised on the same larger substrate.",
            "Further route-specific reruns on the same 20-row split would yield diminishing returns.",
            "A larger shared substrate is the cleanest next enabler for both supervision routes.",
        ],
        "why_not_expand_B_first": [
            "B already received the most recent larger-split rerun and no longer has the main asymmetry problem.",
        ],
        "why_not_expand_C_first": [
            "C now also exists on the larger split, so a route-specific C-first expansion would be less informative than increasing the shared substrate.",
        ],
        "minimum_success_standard": [
            "define larger split v2 contract",
            "materialize a larger shared labeled substrate beyond 20 rows",
            "prove route B / route C / fusion builders still attach cleanly",
        ],
    }

    write_json(output_dir / "symmetric_larger_split_comparison_summary.json", summary)
    write_csv(output_dir / "route_b_larger_vs_route_c_larger_comparison.csv", comparison_rows)
    write_json(output_dir / "supervision_progression_after_symmetric_rerun.json", progression_summary)
    write_csv(output_dir / "symmetric_rerun_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "symmetric_rerun_next_step_recommendation.json", recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM symmetric larger-split comparison",
                f"route_b_larger_rows={larger_b_summary['num_rows']}",
                f"route_c_larger_rows={larger_c_summary['num_rows']}",
                "recommended_next_step=prepare_larger_labeled_split_v2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "recommendation": recommendation,
        "output_paths": {
            "summary": str((output_dir / "symmetric_larger_split_comparison_summary.json").resolve()),
            "comparison_csv": str((output_dir / "route_b_larger_vs_route_c_larger_comparison.csv").resolve()),
            "progression": str((output_dir / "supervision_progression_after_symmetric_rerun.json").resolve()),
            "tradeoff_csv": str((output_dir / "symmetric_rerun_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "symmetric_rerun_next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
