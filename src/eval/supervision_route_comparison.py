"""Unified comparison across controlled supervision, more-natural proxy, and benchmark-truth-leaning candidates."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/supervision-route-comparison/v1"


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


def build_supervision_route_comparison(
    first_labeled_fusion_dir: Path,
    first_labeled_fusion_run_dir: Path,
    labeled_fusion_analysis_dir: Path,
    controlled_supervision_expansion_dir: Path,
    more_natural_analysis_dir: Path,
    more_natural_bootstrap_dir: Path,
    real_pilot_fusion_readiness_dir: Path,
    real_pilot_fusion_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    first_labeled_summary = load_json(first_labeled_fusion_dir / "labeled_real_pilot_fusion_summary.json")
    first_labeled_logistic = load_json(first_labeled_fusion_run_dir / "labeled_real_pilot_logistic_summary.json")
    route_a_summary = load_json(controlled_supervision_expansion_dir / "expanded_labeled_summary.json")
    route_a_logistic = load_json(controlled_supervision_expansion_dir / "expanded_logistic_summary.json")
    route_b_summary = load_json(more_natural_bootstrap_dir / "more_natural_label_summary.json")
    route_b_logistic = load_json(more_natural_bootstrap_dir / "more_natural_logistic_summary.json")
    route_b_decision = load_json(more_natural_analysis_dir / "more_natural_label_next_step_recommendation.json")
    unlabeled_readiness = load_json(real_pilot_fusion_readiness_dir / "real_pilot_fusion_readiness_summary.json")
    unlabeled_rule = load_json(real_pilot_fusion_run_dir / "real_pilot_rule_summary.json")
    unlabeled_logistic = load_json(real_pilot_fusion_run_dir / "real_pilot_logistic_summary.json")

    route_c_candidate = {
        "route_code": "C",
        "route_name": "benchmark_truth_leaning_label_bootstrap",
        "label_name": "task_answer_incorrect_label",
        "label_source": "labeled_illumination_query_answer_correctness",
        "label_scope": "benchmark_truth_leaning_supervision_proxy",
        "label_naturalness_level": "contract_level_task_truth",
        "current_row_capacity": 10,
        "current_base_sample_capacity": 5,
        "estimated_class_balance": {"label_0": 6, "label_1": 4},
        "executable_now": True,
        "main_limitations": [
            "Still not benchmark ground truth.",
            "Reasoning/confidence remain projected from base-sample rows onto contract-level variants.",
        ],
    }

    tradeoff_rows = [
        {
            "route_code": "A",
            "route_name": "controlled_supervision_coverage_expansion",
            "label_scope": route_a_summary["label_scope"],
            "label_naturalness_level": "contract_variant_controlled",
            "num_rows": int(route_a_summary["num_rows"]),
            "num_base_samples": int(route_a_summary["num_base_samples"]),
            "supervised_logistic_status": route_a_logistic["summary_status"],
            "marginal_cost_now": "medium",
            "marginal_ceiling_now": "high_current_slice_ceiling",
            "interpretability": "high",
            "truth_proximity": "low",
        },
        {
            "route_code": "B",
            "route_name": "more_natural_proxy_supervision",
            "label_scope": route_b_summary["label_scope"],
            "label_naturalness_level": route_b_summary["label_naturalness_level"],
            "num_rows": int(route_b_summary["num_rows"]),
            "num_base_samples": int(route_b_summary["num_base_samples"]),
            "supervised_logistic_status": route_b_logistic["summary_status"],
            "marginal_cost_now": "medium",
            "marginal_ceiling_now": "base_sample_slice_ceiling",
            "interpretability": "medium_high",
            "truth_proximity": "medium",
        },
        {
            "route_code": "C",
            "route_name": route_c_candidate["route_name"],
            "label_scope": route_c_candidate["label_scope"],
            "label_naturalness_level": route_c_candidate["label_naturalness_level"],
            "num_rows": route_c_candidate["current_row_capacity"],
            "num_base_samples": route_c_candidate["current_base_sample_capacity"],
            "supervised_logistic_status": "READY_TO_BOOTSTRAP",
            "marginal_cost_now": "low",
            "marginal_ceiling_now": "same_slice_contract_level_capacity",
            "interpretability": "high",
            "truth_proximity": "medium_high",
        },
    ]

    comparison_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_unlabeled_context": {
            "num_aligned_rows": int(unlabeled_readiness["num_aligned_rows"]),
            "rule_baseline_status": str(unlabeled_rule["summary_status"]),
            "logistic_status": str(unlabeled_logistic["summary_status"]),
        },
        "current_supervised_routes": {
            "route_a": {
                "num_rows": int(route_a_summary["num_rows"]),
                "num_base_samples": int(route_a_summary["num_base_samples"]),
                "label_scope": str(route_a_summary["label_scope"]),
            },
            "route_b": {
                "num_rows": int(route_b_summary["num_rows"]),
                "num_base_samples": int(route_b_summary["num_base_samples"]),
                "label_scope": str(route_b_summary["label_scope"]),
            },
            "route_c_candidate": route_c_candidate,
        },
        "main_question_answer": (
            "Under current local-slice and lightweight-model constraints, direction C is the best next step because it offers "
            "a more truth-leaning label than A or B without requiring new resources."
        ),
        "historical_context": {
            "first_supervised_fusion_rows": int(first_labeled_summary["num_rows"]),
            "first_supervised_logistic_status": str(first_labeled_logistic["summary_status"]),
            "022_recommendation_was": "A",
            "023_recommendation_was": str(route_b_decision["recommended_route"]),
        },
    }

    route_comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "routes": [
            {
                "route_code": "A",
                "route_name": "controlled_supervision_coverage_expansion",
                "value_statement": "Largest currently materialized supervised dataset on the same slice.",
                "current_benefit": "10 rows / 5 aligned base samples already achieved.",
                "current_bottleneck": "Further gains require a larger slice while keeping the same controlled semantics.",
                "next_if_chosen": "second controlled expansion on a larger slice",
                "recommendation_rank": 3,
            },
            {
                "route_code": "B",
                "route_name": "more_natural_proxy_supervision",
                "value_statement": "More natural than A because the label is grounded in task correctness at the base-sample level.",
                "current_benefit": "More natural supervision exists and is executable now.",
                "current_bottleneck": "Current B already spans all 5 base samples, so the next gain would either require a larger slice or contract-level re-expansion.",
                "next_if_chosen": "more-natural proxy coverage expansion",
                "recommendation_rank": 2,
            },
            {
                "route_code": "C",
                "route_name": "benchmark_truth_leaning_label_bootstrap",
                "value_statement": "Closer to task truth because the label can be defined directly from contract-level answer correctness.",
                "current_benefit": "Low-cost 10-row candidate already exists in labeled illumination raw results.",
                "current_bottleneck": "Still only a truth-leaning proxy, not benchmark ground truth.",
                "next_if_chosen": "bootstrap contract-level task-answer correctness supervision",
                "recommendation_rank": 1,
            },
        ],
    }

    ceiling_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "controlled_supervision": {
            "ceiling": "current_5_row_slice_exhausted",
            "why": "Route A already materialized the full current contract coverage.",
        },
        "more_natural_proxy_supervision": {
            "ceiling": "current_5_base_sample_slice_exhausted",
            "why": "Route B already spans all currently aligned base samples.",
        },
        "benchmark_truth_leaning_supervision": {
            "ceiling": "still_small_and_contract_anchored_but_not_yet_exhausted",
            "why": "A direct contract-level correctness label can still be materialized on 10 rows without new resources.",
        },
        "high_cost_non_recommended_candidates": [
            "larger benchmark-scale labeled slice",
            "external dataset-backed supervision",
            "new model-backed relabeling",
        ],
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "C",
        "chosen_route_name": "benchmark_truth_leaning_label_bootstrap",
        "why_chosen": [
            "A is already near the current slice ceiling and would stay controlled in semantics.",
            "B is more natural than A, but it already covers all 5 base samples on the current slice.",
            "C offers a more truth-leaning label on 10 contract-level rows using existing raw artifacts and no new resources.",
        ],
        "why_not_A": [
            "The next A gain would require enlarging the slice before it adds new supervised coverage.",
            "Its semantics would still remain contract-controlled.",
        ],
        "why_not_B_first": [
            "B already proves a more-natural path exists at the base-sample level.",
            "The next marginal gain beyond current B is naturally contract-level answer correctness, which is effectively C.",
        ],
        "bootstrap_contract": {
            "chosen_route": "C",
            "goal": "Materialize a 10-row benchmark-truth-leaning supervised fusion dataset using contract-level answer correctness on existing labeled illumination runs.",
            "input_resources": [
                "outputs/labeled_pilot_runs/default/illumination_probe/raw_results.jsonl",
                "outputs/controlled_supervision_expansion/default/expanded_real_pilot_fusion/fusion_dataset.jsonl",
                "outputs/pilot_materialization/pilot_csqa_reasoning_local/csqa_reasoning_pilot_slice.jsonl",
            ],
            "label_source": "query_answer_key correctness on each labeled illumination contract row",
            "success_criteria": [
                "materialize a 10-row contract-level labeled fusion dataset",
                "preserve auditable answer-correctness label definitions",
                "run a minimal supervised logistic bootstrap on that dataset",
            ],
            "known_risks": route_c_candidate["main_limitations"],
        },
    }

    write_json(output_dir / "supervision_route_comparison_summary.json", comparison_summary)
    write_json(output_dir / "route_A_vs_B_vs_C_comparison.json", route_comparison)
    write_csv(output_dir / "supervision_tradeoff_matrix.csv", tradeoff_rows)
    write_json(output_dir / "supervision_ceiling_and_cost_summary.json", ceiling_summary)
    write_json(output_dir / "supervision_next_step_recommendation.json", recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM supervision route comparison",
                "Chosen route: C / benchmark_truth_leaning_label_bootstrap",
                f"Route A rows: {route_a_summary['num_rows']}",
                f"Route B rows: {route_b_summary['num_rows']}",
                "Route C candidate rows: 10",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "comparison_summary": comparison_summary,
        "recommendation": recommendation,
        "output_paths": {
            "summary": str((output_dir / "supervision_route_comparison_summary.json").resolve()),
            "routes": str((output_dir / "route_A_vs_B_vs_C_comparison.json").resolve()),
            "tradeoff_csv": str((output_dir / "supervision_tradeoff_matrix.csv").resolve()),
            "ceiling_summary": str((output_dir / "supervision_ceiling_and_cost_summary.json").resolve()),
            "recommendation": str((output_dir / "supervision_next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
