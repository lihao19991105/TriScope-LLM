"""Compare supervision routes after the larger-split rerun."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-rerun-comparison/v1"


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


def build_post_rerun_comparison(
    route_b_dir: Path,
    expanded_route_c_dir: Path,
    chosen_route_rerun_dir: Path,
    larger_split_dir: Path,
    expanded_supervision_comparison_dir: Path,
    larger_split_decision_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    route_b_summary = load_json(route_b_dir / "more_natural_label_summary.json")
    route_b_logistic = load_json(route_b_dir / "more_natural_logistic_summary.json")
    expanded_route_c_summary = load_json(expanded_route_c_dir / "expanded_benchmark_truth_leaning_summary.json")
    expanded_route_c_logistic = load_json(expanded_route_c_dir / "expanded_benchmark_truth_leaning_logistic_summary.json")
    chosen_rerun_summary = load_json(chosen_route_rerun_dir / "expanded_more_natural_summary.json")
    chosen_rerun_logistic = load_json(chosen_route_rerun_dir / "expanded_more_natural_logistic_summary.json")
    chosen_rerun_run_summary = load_json(chosen_route_rerun_dir / "chosen_route_rerun_run_summary.json")
    larger_split_summary = load_json(larger_split_dir / "larger_labeled_split_summary.json")
    prior_expanded_recommendation = load_json(
        expanded_supervision_comparison_dir / "expanded_supervision_next_step_recommendation.json"
    )
    larger_split_recommendation = load_json(
        larger_split_decision_dir / "larger_split_route_next_step_recommendation.json"
    )

    progression_rows = [
        {
            "route_code": "B_old",
            "route_name": "more_natural_supervision_proxy",
            "substrate_level": "original_real_pilot_fusion",
            "num_rows": route_b_summary["num_rows"],
            "num_base_samples": route_b_summary["num_base_samples"],
            "label_scope": route_b_summary["label_scope"],
            "label_naturalness_level": route_b_summary["label_naturalness_level"],
            "mean_prediction_score": route_b_logistic["mean_prediction_score"],
            "num_predictions": route_b_logistic["num_predictions"],
            "main_takeaway": "original route-B bootstrap",
        },
        {
            "route_code": "B_larger",
            "route_name": "more_natural_supervision_proxy",
            "substrate_level": "larger_labeled_split",
            "num_rows": chosen_rerun_summary["num_rows"],
            "num_base_samples": chosen_rerun_summary["num_base_samples"],
            "label_scope": chosen_rerun_summary["label_scope"],
            "label_naturalness_level": chosen_rerun_summary["label_naturalness_level"],
            "mean_prediction_score": chosen_rerun_logistic["mean_prediction_score"],
            "num_predictions": chosen_rerun_logistic["num_predictions"],
            "main_takeaway": "chosen rerun route-B bootstrap on larger split",
        },
        {
            "route_code": "C_expanded",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "substrate_level": "expanded_labeled_slice",
            "num_rows": expanded_route_c_summary["num_rows"],
            "num_base_samples": expanded_route_c_summary["num_base_samples"],
            "label_scope": expanded_route_c_summary["label_scope"],
            "label_naturalness_level": expanded_route_c_summary["label_naturalness_level"],
            "mean_prediction_score": expanded_route_c_logistic["mean_prediction_score"],
            "num_predictions": expanded_route_c_logistic["num_predictions"],
            "main_takeaway": "current strongest truth-leaning path, but not yet rerun on larger split",
        },
    ]

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "larger_split_context": {
            "split_name": larger_split_summary["split_name"],
            "num_rows": larger_split_summary["num_rows"],
            "num_base_samples": larger_split_summary["num_base_samples"],
        },
        "route_progression": {
            "route_b_old_rows": route_b_summary["num_rows"],
            "route_b_larger_rows": chosen_rerun_summary["num_rows"],
            "route_b_old_base_samples": route_b_summary["num_base_samples"],
            "route_b_larger_base_samples": chosen_rerun_summary["num_base_samples"],
            "route_c_expanded_rows": expanded_route_c_summary["num_rows"],
            "route_c_expanded_base_samples": expanded_route_c_summary["num_base_samples"],
        },
        "main_question_answer": "After route B is rerun on the larger split, the next highest-value step is to rerun route C on the same larger split so B and C can be compared symmetrically on a shared substrate.",
        "why": [
            "033 removed route B's tiny-slice bottleneck by increasing it from 5 rows / 5 base samples to 20 rows / 20 base samples.",
            "Route C still carries the stronger truth-leaning supervision semantics, but it remains anchored to the earlier 10-base-sample expanded substrate.",
            "The main remaining asymmetry is now substrate-level, not mere route existence.",
        ],
        "prior_context": {
            "030_recommendation": prior_expanded_recommendation.get("recommended_next_step"),
            "032_recommendation": larger_split_recommendation.get("recommended_route_to_rerun_first"),
        },
        "chosen_route_run_summary": chosen_rerun_run_summary,
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "rerun_route_C_on_larger_split",
        "why_recommended": [
            "Route B now exists on the larger split and no longer blocks comparison.",
            "Route C remains the strongest truth-leaning proxy, but it has not yet been rerun on the same 20-row shared substrate.",
            "Rerunning route C next creates the first genuinely symmetric B-vs-C comparison on a larger shared labeled split.",
        ],
        "why_not_expand_substrate_first": [
            "The current larger split already unlocked a meaningful rerun and still has unused comparison value.",
            "Expanding substrate again before rerunning C would postpone the first symmetric larger-split comparison.",
        ],
        "why_not_stop_here": [
            "Current post-rerun evidence is still asymmetric across routes.",
            "Stopping here would leave the key B-vs-C question partially answered.",
        ],
        "minimum_success_standard": [
            "materialize route-C inputs on the larger split",
            "rerun route C on the 20-row larger substrate",
            "compare route B larger vs route C larger under the same substrate size",
        ],
    }

    write_json(output_dir / "post_rerun_comparison_summary.json", summary)
    write_csv(output_dir / "route_progression_after_rerun.csv", progression_rows)
    write_json(output_dir / "post_rerun_next_step_recommendation.json", recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM post-rerun comparison",
                f"route_b_old_rows={route_b_summary['num_rows']}",
                f"route_b_larger_rows={chosen_rerun_summary['num_rows']}",
                f"route_c_expanded_rows={expanded_route_c_summary['num_rows']}",
                "recommended_next_step=rerun_route_C_on_larger_split",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "recommendation": recommendation,
        "output_paths": {
            "summary": str((output_dir / "post_rerun_comparison_summary.json").resolve()),
            "progression_csv": str((output_dir / "route_progression_after_rerun.csv").resolve()),
            "recommendation": str((output_dir / "post_rerun_next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
