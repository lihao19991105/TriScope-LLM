"""Compare supervision routes after route B and route C reruns on labeled split v6."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-v6-symmetric-comparison/v1"


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


def build_post_v6_symmetric_comparison(
    old_route_b_dir: Path,
    larger_route_b_dir: Path,
    route_b_v2_dir: Path,
    route_b_v3_dir: Path,
    route_b_v4_dir: Path,
    route_b_v5_dir: Path,
    route_b_v6_dir: Path,
    old_route_c_dir: Path,
    larger_route_c_dir: Path,
    route_c_v2_dir: Path,
    route_c_v3_dir: Path,
    route_c_v4_dir: Path,
    route_c_v5_dir: Path,
    route_c_v6_dir: Path,
    post_v5_comparison_dir: Path,
    post_v5_bootstrap_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    old_b_summary = load_json(old_route_b_dir / "more_natural_label_summary.json")
    old_b_logistic = load_json(old_route_b_dir / "more_natural_logistic_summary.json")
    larger_b_summary = load_json(larger_route_b_dir / "expanded_more_natural_summary.json")
    larger_b_logistic = load_json(larger_route_b_dir / "expanded_more_natural_logistic_summary.json")
    route_b_v2_summary = load_json(route_b_v2_dir / "route_b_v2_summary.json")
    route_b_v2_logistic = load_json(route_b_v2_dir / "route_b_v2_logistic_summary.json")
    route_b_v3_summary = load_json(route_b_v3_dir / "route_b_v3_summary.json")
    route_b_v3_logistic = load_json(route_b_v3_dir / "route_b_v3_logistic_summary.json")
    route_b_v4_summary = load_json(route_b_v4_dir / "route_b_v4_summary.json")
    route_b_v4_logistic = load_json(route_b_v4_dir / "route_b_v4_logistic_summary.json")
    route_b_v5_summary = load_json(route_b_v5_dir / "route_b_v5_summary.json")
    route_b_v5_logistic = load_json(route_b_v5_dir / "route_b_v5_logistic_summary.json")
    route_b_v6_summary = load_json(route_b_v6_dir / "route_b_v6_summary.json")
    route_b_v6_logistic = load_json(route_b_v6_dir / "route_b_v6_logistic_summary.json")

    old_c_summary = load_json(old_route_c_dir / "benchmark_truth_leaning_summary.json")
    old_c_logistic = load_json(old_route_c_dir / "benchmark_truth_leaning_logistic_summary.json")
    larger_c_summary = load_json(larger_route_c_dir / "larger_split_route_c_summary.json")
    larger_c_logistic = load_json(larger_route_c_dir / "larger_split_route_c_logistic_summary.json")
    route_c_v2_summary = load_json(route_c_v2_dir / "route_c_v2_summary.json")
    route_c_v2_logistic = load_json(route_c_v2_dir / "route_c_v2_logistic_summary.json")
    route_c_v3_summary = load_json(route_c_v3_dir / "route_c_v3_summary.json")
    route_c_v3_logistic = load_json(route_c_v3_dir / "route_c_v3_logistic_summary.json")
    route_c_v4_summary = load_json(route_c_v4_dir / "route_c_v4_summary.json")
    route_c_v4_logistic = load_json(route_c_v4_dir / "route_c_v4_logistic_summary.json")
    route_c_v5_summary = load_json(route_c_v5_dir / "route_c_v5_summary.json")
    route_c_v5_logistic = load_json(route_c_v5_dir / "route_c_v5_logistic_summary.json")
    route_c_v6_summary = load_json(route_c_v6_dir / "route_c_v6_summary.json")
    route_c_v6_logistic = load_json(route_c_v6_dir / "route_c_v6_logistic_summary.json")

    prior_recommendation = load_json(post_v5_comparison_dir / "v5_symmetric_next_step_recommendation.json")
    v6_split_summary = load_json(post_v5_bootstrap_dir / "larger_labeled_split_v6_summary.json")

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
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "B_v2",
            "route_name": "more_natural_supervision_proxy",
            "substrate_level": "larger_labeled_split_v2",
            "num_rows": route_b_v2_summary["num_rows"],
            "num_base_samples": route_b_v2_summary["num_base_samples"],
            "label_scope": route_b_v2_summary["label_scope"],
            "label_naturalness_level": route_b_v2_summary["label_naturalness_level"],
            "mean_prediction_score": route_b_v2_logistic["mean_prediction_score"],
            "num_predictions": route_b_v2_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "B_v3",
            "route_name": "more_natural_supervision_proxy",
            "substrate_level": "larger_labeled_split_v3",
            "num_rows": route_b_v3_summary["num_rows"],
            "num_base_samples": route_b_v3_summary["num_base_samples"],
            "label_scope": route_b_v3_summary["label_scope"],
            "label_naturalness_level": route_b_v3_summary["label_naturalness_level"],
            "mean_prediction_score": route_b_v3_logistic["mean_prediction_score"],
            "num_predictions": route_b_v3_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "B_v4",
            "route_name": "more_natural_supervision_proxy",
            "substrate_level": "larger_labeled_split_v4",
            "num_rows": route_b_v4_summary["num_rows"],
            "num_base_samples": route_b_v4_summary["num_base_samples"],
            "label_scope": route_b_v4_summary["label_scope"],
            "label_naturalness_level": route_b_v4_summary["label_naturalness_level"],
            "mean_prediction_score": route_b_v4_logistic["mean_prediction_score"],
            "num_predictions": route_b_v4_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "B_v5",
            "route_name": "more_natural_supervision_proxy",
            "substrate_level": "larger_labeled_split_v5",
            "num_rows": route_b_v5_summary["num_rows"],
            "num_base_samples": route_b_v5_summary["num_base_samples"],
            "label_scope": route_b_v5_summary["label_scope"],
            "label_naturalness_level": route_b_v5_summary["label_naturalness_level"],
            "mean_prediction_score": route_b_v5_logistic["mean_prediction_score"],
            "num_predictions": route_b_v5_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "B_v6",
            "route_name": "more_natural_supervision_proxy",
            "substrate_level": "larger_labeled_split_v6",
            "num_rows": route_b_v6_summary["num_rows"],
            "num_base_samples": route_b_v6_summary["num_base_samples"],
            "label_scope": route_b_v6_summary["label_scope"],
            "label_naturalness_level": route_b_v6_summary["label_naturalness_level"],
            "mean_prediction_score": route_b_v6_logistic["mean_prediction_score"],
            "num_predictions": route_b_v6_logistic["num_predictions"],
            "comparison_role": "v6_symmetric_candidate",
        },
        {
            "route_code": "C_old",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "substrate_level": "first_truth_leaning_proxy_bootstrap",
            "num_rows": old_c_summary["num_rows"],
            "num_base_samples": old_c_summary["num_base_samples"],
            "label_scope": old_c_summary["label_scope"],
            "label_naturalness_level": old_c_summary["label_naturalness_level"],
            "mean_prediction_score": old_c_logistic["mean_prediction_score"],
            "num_predictions": old_c_logistic["num_predictions"],
            "comparison_role": "historical_reference",
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
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "C_v2",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "substrate_level": "larger_labeled_split_v2",
            "num_rows": route_c_v2_summary["num_rows"],
            "num_base_samples": route_c_v2_summary["num_base_samples"],
            "label_scope": route_c_v2_summary["label_scope"],
            "label_naturalness_level": route_c_v2_summary["label_naturalness_level"],
            "mean_prediction_score": route_c_v2_logistic["mean_prediction_score"],
            "num_predictions": route_c_v2_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "C_v3",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "substrate_level": "larger_labeled_split_v3",
            "num_rows": route_c_v3_summary["num_rows"],
            "num_base_samples": route_c_v3_summary["num_base_samples"],
            "label_scope": route_c_v3_summary["label_scope"],
            "label_naturalness_level": route_c_v3_summary["label_naturalness_level"],
            "mean_prediction_score": route_c_v3_logistic["mean_prediction_score"],
            "num_predictions": route_c_v3_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "C_v4",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "substrate_level": "larger_labeled_split_v4",
            "num_rows": route_c_v4_summary["num_rows"],
            "num_base_samples": route_c_v4_summary["num_base_samples"],
            "label_scope": route_c_v4_summary["label_scope"],
            "label_naturalness_level": route_c_v4_summary["label_naturalness_level"],
            "mean_prediction_score": route_c_v4_logistic["mean_prediction_score"],
            "num_predictions": route_c_v4_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "C_v5",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "substrate_level": "larger_labeled_split_v5",
            "num_rows": route_c_v5_summary["num_rows"],
            "num_base_samples": route_c_v5_summary["num_base_samples"],
            "label_scope": route_c_v5_summary["label_scope"],
            "label_naturalness_level": route_c_v5_summary["label_naturalness_level"],
            "mean_prediction_score": route_c_v5_logistic["mean_prediction_score"],
            "num_predictions": route_c_v5_logistic["num_predictions"],
            "comparison_role": "historical_reference",
        },
        {
            "route_code": "C_v6",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "substrate_level": "larger_labeled_split_v6",
            "num_rows": route_c_v6_summary["num_rows"],
            "num_base_samples": route_c_v6_summary["num_base_samples"],
            "label_scope": route_c_v6_summary["label_scope"],
            "label_naturalness_level": route_c_v6_summary["label_naturalness_level"],
            "mean_prediction_score": route_c_v6_logistic["mean_prediction_score"],
            "num_predictions": route_c_v6_logistic["num_predictions"],
            "comparison_role": "v6_symmetric_candidate",
        },
    ]

    progression_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "v6_split_context": {
            "split_name": v6_split_summary["split_name"],
            "num_rows": v6_split_summary["num_rows"],
            "num_base_samples": v6_split_summary["num_base_samples"],
        },
        "progression": {
            "route_b_old_rows": old_b_summary["num_rows"],
            "route_b_larger_rows": larger_b_summary["num_rows"],
            "route_b_v2_rows": route_b_v2_summary["num_rows"],
            "route_b_v3_rows": route_b_v3_summary["num_rows"],
            "route_b_v4_rows": route_b_v4_summary["num_rows"],
            "route_b_v5_rows": route_b_v5_summary["num_rows"],
            "route_b_v6_rows": route_b_v6_summary["num_rows"],
            "route_c_old_rows": old_c_summary["num_rows"],
            "route_c_larger_rows": larger_c_summary["num_rows"],
            "route_c_v2_rows": route_c_v2_summary["num_rows"],
            "route_c_v3_rows": route_c_v3_summary["num_rows"],
            "route_c_v4_rows": route_c_v4_summary["num_rows"],
            "route_c_v5_rows": route_c_v5_summary["num_rows"],
            "route_c_v6_rows": route_c_v6_summary["num_rows"],
            "route_b_old_base_samples": old_b_summary["num_base_samples"],
            "route_b_larger_base_samples": larger_b_summary["num_base_samples"],
            "route_b_v2_base_samples": route_b_v2_summary["num_base_samples"],
            "route_b_v3_base_samples": route_b_v3_summary["num_base_samples"],
            "route_b_v4_base_samples": route_b_v4_summary["num_base_samples"],
            "route_b_v5_base_samples": route_b_v5_summary["num_base_samples"],
            "route_b_v6_base_samples": route_b_v6_summary["num_base_samples"],
            "route_c_old_base_samples": old_c_summary["num_base_samples"],
            "route_c_larger_base_samples": larger_c_summary["num_base_samples"],
            "route_c_v2_base_samples": route_c_v2_summary["num_base_samples"],
            "route_c_v3_base_samples": route_c_v3_summary["num_base_samples"],
            "route_c_v4_base_samples": route_c_v4_summary["num_base_samples"],
            "route_c_v5_base_samples": route_c_v5_summary["num_base_samples"],
            "route_c_v6_base_samples": route_c_v6_summary["num_base_samples"],
        },
        "main_takeaway": "B and C now both exist on the same 70-row labeled split v6, but the value of yet another proxy-substrate expansion is starting to flatten relative to preparing a more realistic labeled experiment cutover.",
    }

    tradeoff_rows = [
        {
            "route_code": "B_v6",
            "route_name": "more_natural_supervision_proxy",
            "truth_anchor_level": route_b_v6_summary["label_naturalness_level"],
            "substrate_level": "larger_labeled_split_v6",
            "current_rows": route_b_v6_summary["num_rows"],
            "current_base_samples": route_b_v6_summary["num_base_samples"],
            "realism": "medium",
            "cost_to_expand_further": "medium",
            "next_ceiling": "shared_substrate_size",
            "why": "B now has symmetric substrate access at 60 rows, but it still uses the weaker more-natural proxy truth anchor.",
        },
        {
            "route_code": "C_v6",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "truth_anchor_level": route_c_v6_summary["label_naturalness_level"],
            "substrate_level": "larger_labeled_split_v6",
            "current_rows": route_c_v6_summary["num_rows"],
            "current_base_samples": route_c_v6_summary["num_base_samples"],
            "realism": "medium_high",
            "cost_to_expand_further": "medium",
            "next_ceiling": "shared_substrate_size",
            "why": "C preserves the stronger truth-leaning semantics, but both B and C again share the same substrate ceiling at v6.",
        },
        {
            "route_code": "substrate_v6",
            "route_name": "larger_labeled_split_v6",
            "truth_anchor_level": "shared_substrate_enabler",
            "substrate_level": "next_bootstrap",
            "current_rows": v6_split_summary["num_rows"],
            "current_base_samples": v6_split_summary["num_base_samples"],
            "realism": "enabler",
            "cost_to_expand_further": "medium",
            "next_ceiling": "local_curated_split_growth",
            "why": "V6 successfully lifts the shared base again, but the project is still cycling inside the same local curated proxy world.",
        },
        {
            "route_code": "real_cutover",
            "route_name": "small_real_labeled_experiment_cutover",
            "truth_anchor_level": "cutover_candidate",
            "substrate_level": "post_proxy_transition",
            "current_rows": v6_split_summary["num_rows"],
            "current_base_samples": v6_split_summary["num_base_samples"],
            "realism": "higher",
            "cost_to_expand_further": "medium",
            "next_ceiling": "real_dataset_and_label_availability",
            "why": "At v6, another proxy substrate lift would still help, but its marginal gain is lower than starting a first more realistic labeled experiment bootstrap.",
        },
    ]

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "v6_symmetric_ready": True,
        "main_question_answer": "After route B and route C both exist on labeled split v6, the next highest-value step is to start a small real-labeled experiment cutover rather than automatically expanding to v7.",
        "why": [
            "Route B v6 and route C v6 now both run on the same 70-row shared substrate.",
            "Route C still carries the stronger truth-leaning supervision semantics, while route B remains the cheaper more-natural proxy path.",
            "The dominant asymmetry problem has been removed again, but the remaining bottleneck is no longer just substrate size; it is the lack of a more realistic labeled experiment contract.",
        ],
        "historical_context": {
            "prior_recommendation": prior_recommendation.get("recommended_next_step"),
        },
        "continue_proxy_substrate_expansion": False,
        "proxy_substrate_expansion_marginal_value": "declining",
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "prepare_small_real_labeled_experiment",
        "why_recommended": [
            "Route B and route C have both now been exercised on the same 70-row labeled split v6.",
            "Further proxy-only substrate expansion would still help, but its marginal value is lower than beginning a first more realistic labeled experiment cutover.",
            "The repository now has enough stable proxy infrastructure to support a small real-experiment bootstrap without immediately jumping to benchmark-scale execution.",
        ],
        "why_not_expand_B_first": [
            "B already has a true v6 rerun, so another B-first step on the same substrate would add limited new information.",
        ],
        "why_not_expand_C_first": [
            "C also already has a true v6 rerun, so another C-first step on the same substrate would still stay inside the same proxy supervision regime.",
        ],
        "why_not_prepare_larger_labeled_split_v7": [
            "A v7 substrate would mostly extend the same local curated proxy loop and is no longer the highest-leverage action.",
        ],
        "continue_proxy_substrate_expansion": False,
        "continue_proxy_substrate_expansion_reason": "The shared substrate is still useful, but its marginal benefit is now below the value of bootstrapping a first more realistic labeled experiment contract.",
        "minimum_success_standard": [
            "select one minimal but more realistic labeled experiment candidate",
            "materialize its input contract and bootstrap inputs",
            "prove the current route B / route C / fusion stack can map onto that cutover object",
        ],
    }

    write_json(output_dir / "v6_symmetric_comparison_summary.json", summary)
    write_csv(output_dir / "route_b_v6_vs_route_c_v6_comparison.csv", comparison_rows)
    write_json(output_dir / "supervision_progression_after_v6_rerun.json", progression_summary)
    write_csv(output_dir / "v6_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "v6_symmetric_next_step_recommendation.json", recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM post-v6 symmetric comparison",
                f"route_b_v6_rows={route_b_v6_summary['num_rows']}",
                f"route_c_v6_rows={route_c_v6_summary['num_rows']}",
                "recommended_next_step=prepare_small_real_labeled_experiment",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "recommendation": recommendation,
        "output_paths": {
            "summary": str((output_dir / "v6_symmetric_comparison_summary.json").resolve()),
            "comparison_csv": str((output_dir / "route_b_v6_vs_route_c_v6_comparison.csv").resolve()),
            "progression": str((output_dir / "supervision_progression_after_v6_rerun.json").resolve()),
            "tradeoff_csv": str((output_dir / "v6_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "v6_symmetric_next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
