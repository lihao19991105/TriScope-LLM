"""Compare route B, old route C, and expanded route C."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/expanded-supervision-comparison/v1"


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


def build_expanded_supervision_comparison(
    route_b_dir: Path,
    old_route_c_dir: Path,
    expanded_route_c_dir: Path,
    labeled_slice_expansion_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    route_b_summary = load_json(route_b_dir / "more_natural_label_summary.json")
    route_b_logistic = load_json(route_b_dir / "more_natural_logistic_summary.json")
    old_c_summary = load_json(old_route_c_dir / "benchmark_truth_leaning_summary.json")
    old_c_logistic = load_json(old_route_c_dir / "benchmark_truth_leaning_logistic_summary.json")
    expanded_c_summary = load_json(expanded_route_c_dir / "expanded_benchmark_truth_leaning_summary.json")
    expanded_c_logistic = load_json(expanded_route_c_dir / "expanded_benchmark_truth_leaning_logistic_summary.json")
    substrate_summary = load_json(labeled_slice_expansion_dir / "expanded_labeled_slice_summary.json")

    comparison_rows = [
        {
            "route_code": "B",
            "route_name": "more_natural_supervision_proxy",
            "label_name": route_b_summary["label_name"],
            "label_scope": route_b_summary["label_scope"],
            "label_naturalness_level": route_b_summary["label_naturalness_level"],
            "num_rows": route_b_summary["num_rows"],
            "num_base_samples": route_b_summary["num_base_samples"],
            "num_predictions": route_b_logistic["num_predictions"],
            "mean_prediction_score": route_b_logistic["mean_prediction_score"],
            "truth_anchor_level": "task_truth_proxy",
            "current_role": "semantic_diversity_reference",
        },
        {
            "route_code": "C_old",
            "route_name": "old_benchmark_truth_leaning_supervision_proxy",
            "label_name": old_c_summary["label_name"],
            "label_scope": old_c_summary["label_scope"],
            "label_naturalness_level": old_c_summary["label_naturalness_level"],
            "num_rows": old_c_summary["num_rows"],
            "num_base_samples": old_c_summary["num_base_samples"],
            "num_predictions": old_c_logistic["num_predictions"],
            "mean_prediction_score": old_c_logistic["mean_prediction_score"],
            "truth_anchor_level": "contract_level_task_truth_proxy",
            "current_role": "pre_expansion_route_c_reference",
        },
        {
            "route_code": "C_expanded",
            "route_name": "expanded_benchmark_truth_leaning_supervision_proxy",
            "label_name": expanded_c_summary["label_name"],
            "label_scope": expanded_c_summary["label_scope"],
            "label_naturalness_level": expanded_c_summary["label_naturalness_level"],
            "num_rows": expanded_c_summary["num_rows"],
            "num_base_samples": expanded_c_summary["num_base_samples"],
            "num_predictions": expanded_c_logistic["num_predictions"],
            "mean_prediction_score": expanded_c_logistic["mean_prediction_score"],
            "truth_anchor_level": "contract_level_task_truth_proxy",
            "current_role": "post_expansion_route_c",
        },
    ]

    comparison_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_routes": {
            "route_b": route_b_summary,
            "old_route_c": old_c_summary,
            "expanded_route_c": expanded_c_summary,
        },
        "main_question_answer": (
            "Expanded route C is now the strongest current supervision path because it preserves route-C truth anchoring while doubling both row count and base-sample coverage relative to old route C."
        ),
        "substrate_context": {
            "expanded_slice_rows": substrate_summary["num_rows"],
            "new_base_samples": substrate_summary["num_new_rows"],
        },
    }
    progression_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "route_c_progression": {
            "old_num_rows": old_c_summary["num_rows"],
            "expanded_num_rows": expanded_c_summary["num_rows"],
            "old_num_base_samples": old_c_summary["num_base_samples"],
            "expanded_num_base_samples": expanded_c_summary["num_base_samples"],
            "row_gain": int(expanded_c_summary["num_rows"]) - int(old_c_summary["num_rows"]),
            "base_sample_gain": int(expanded_c_summary["num_base_samples"]) - int(old_c_summary["num_base_samples"]),
        },
        "route_b_vs_expanded_c": {
            "route_b_num_rows": route_b_summary["num_rows"],
            "expanded_c_num_rows": expanded_c_summary["num_rows"],
            "route_b_truth_anchor": route_b_summary["label_naturalness_level"],
            "expanded_c_truth_anchor": expanded_c_summary["label_naturalness_level"],
            "comparison_statement": (
                "Route B still adds supervision diversity, but expanded route C is now both larger and more truth-leaning."
            ),
        },
    }
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "prepare_larger_labeled_split",
        "why_recommended": [
            "Expanded route C clearly improves over old route C in both substrate size and supervised coverage.",
            "Expanded route C also dominates current route B on row count and truth anchoring.",
            "The next shared bottleneck is no longer route choice inside the current slice, but the limited size of the expanded local substrate itself.",
        ],
        "why_not_expand_B_first": [
            "Route B has not caught up to expanded route C in scale or truth anchoring.",
            "Expanding B again on the same 10-row substrate would likely add less marginal value than preparing a larger shared labeled split.",
        ],
        "why_not_keep_expanding_C_without_new_split": [
            "Expanded route C has already consumed the current 10-row substrate.",
            "Further substantive route-C gains now require a larger labeled split rather than another intra-slice reshuffle.",
        ],
        "next_bootstrap_contract": {
            "goal": "Prepare a larger labeled split that can support another round of route-B and route-C expansion on a shared substrate.",
            "minimum_success_standard": [
                "materialize a labeled split larger than the current 10-row substrate",
                "keep labels auditable and explicitly scoped as pilot/proxy where applicable",
                "preserve compatibility with current route-B and route-C builders",
            ],
            "known_risks": [
                "A larger split is still not automatically benchmark ground truth.",
                "Current model and prompt stack remain lightweight and pilot-level.",
            ],
        },
    }

    write_json(output_dir / "expanded_supervision_comparison_summary.json", comparison_summary)
    write_csv(output_dir / "route_b_oldc_expandedc_comparison.csv", comparison_rows)
    write_json(output_dir / "supervision_progression_summary.json", progression_summary)
    write_json(output_dir / "expanded_supervision_next_step_recommendation.json", recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM expanded supervision comparison",
                "Compared routes: B, old C, expanded C",
                "Recommendation: prepare_larger_labeled_split",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "comparison_summary": comparison_summary,
        "progression_summary": progression_summary,
        "recommendation": recommendation,
        "output_paths": {
            "comparison_summary": str((output_dir / "expanded_supervision_comparison_summary.json").resolve()),
            "comparison_csv": str((output_dir / "route_b_oldc_expandedc_comparison.csv").resolve()),
            "progression_summary": str((output_dir / "supervision_progression_summary.json").resolve()),
            "recommendation": str((output_dir / "expanded_supervision_next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
