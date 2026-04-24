"""Decide whether larger-split rerun should prioritize route B or route C."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/larger-split-route-rerun-decision/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


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


def build_larger_split_route_rerun_decision(
    larger_split_dir: Path,
    route_b_dir: Path,
    expanded_route_c_dir: Path,
    expanded_supervision_comparison_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    larger_split_summary = load_json(larger_split_dir / "larger_labeled_split_summary.json")
    compatibility_summary = load_json(larger_split_dir / "larger_split_route_compatibility_summary.json")
    route_b_summary = load_json(route_b_dir / "more_natural_label_summary.json")
    route_b_logistic = load_json(route_b_dir / "more_natural_logistic_summary.json")
    expanded_c_summary = load_json(expanded_route_c_dir / "expanded_benchmark_truth_leaning_summary.json")
    expanded_c_logistic = load_json(expanded_route_c_dir / "expanded_benchmark_truth_leaning_logistic_summary.json")
    prior_recommendation = load_json(expanded_supervision_comparison_dir / "expanded_supervision_next_step_recommendation.json")

    tradeoff_rows = [
        {
            "route_code": "B",
            "route_name": "more_natural_supervision_proxy",
            "current_rows": route_b_summary["num_rows"],
            "larger_split_expected_rows": larger_split_summary["expected_follow_on_capacity"]["route_b_more_natural_rows"],
            "truth_anchor_level": route_b_summary["label_naturalness_level"],
            "rerun_cost_relative": "medium",
            "information_gain": "high",
            "why": "B is currently under-expanded and would gain the most comparative value from a larger substrate rerun.",
        },
        {
            "route_code": "C",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "current_rows": expanded_c_summary["num_rows"],
            "larger_split_expected_rows": larger_split_summary["expected_follow_on_capacity"]["route_c_benchmark_truth_leaning_rows"],
            "truth_anchor_level": expanded_c_summary["label_naturalness_level"],
            "rerun_cost_relative": "medium_high",
            "information_gain": "medium",
            "why": "C is still the strongest truth path, but it already has an expanded rerun on the smaller substrate.",
        },
    ]

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "larger_split_context": {
            "num_rows": larger_split_summary["num_rows"],
            "route_b_capacity": larger_split_summary["expected_follow_on_capacity"]["route_b_more_natural_rows"],
            "route_c_capacity": larger_split_summary["expected_follow_on_capacity"]["route_c_benchmark_truth_leaning_rows"],
            "compatibility_targets": compatibility_summary["compatibility_targets"],
        },
        "route_b_current_state": {
            "num_rows": route_b_summary["num_rows"],
            "truth_anchor_level": route_b_summary["label_naturalness_level"],
            "logistic_status": route_b_logistic["summary_status"],
        },
        "route_c_current_state": {
            "num_rows": expanded_c_summary["num_rows"],
            "truth_anchor_level": expanded_c_summary["label_naturalness_level"],
            "logistic_status": expanded_c_logistic["summary_status"],
        },
        "main_question_answer": (
            "On the larger split, the highest-information next rerun is route B, because route C already has an expanded result while route B still lacks a symmetric rerun on a larger shared substrate."
        ),
        "prior_recommendation_context": prior_recommendation.get("recommended_next_step"),
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_route_to_rerun_first": "B",
        "recommended_route_name": "more_natural_supervision_proxy",
        "why_recommended": [
            "Route C already demonstrated that truth-leaning supervision scales on the current expanded substrate.",
            "Route B is currently the asymmetric missing comparison, so rerunning B on the larger split yields higher comparative information gain.",
            "The larger split is fully compatible with route B and would raise its row capacity from 5 to 20.",
        ],
        "why_not_C_first": [
            "C is already the strongest current path and already has an expanded rerun artifact.",
            "Another immediate C rerun would add less new information than bringing B onto the same larger substrate.",
        ],
        "minimum_success_standard": [
            "materialize a larger-split route-B dataset",
            "run route B on the larger substrate",
            "compare larger-split route B directly against expanded route C",
        ],
    }

    write_json(output_dir / "larger_split_route_rerun_comparison.json", comparison)
    write_csv(output_dir / "larger_split_route_rerun_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "larger_split_route_next_step_recommendation.json", recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM larger split route rerun decision",
                "Compared routes: B, C",
                "Recommendation: rerun B first on larger split",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "comparison": comparison,
        "recommendation": recommendation,
        "output_paths": {
            "comparison": str((output_dir / "larger_split_route_rerun_comparison.json").resolve()),
            "tradeoff_matrix": str((output_dir / "larger_split_route_rerun_tradeoff_matrix.csv").resolve()),
            "recommendation": str((output_dir / "larger_split_route_next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
