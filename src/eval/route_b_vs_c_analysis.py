"""Compare route B, route C, and labeled-slice expansion direction D."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/route-b-vs-c-analysis/v1"


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


def build_route_b_vs_c_analysis(
    more_natural_bootstrap_dir: Path,
    benchmark_truth_leaning_bootstrap_dir: Path,
    controlled_supervision_expansion_dir: Path,
    supervision_route_comparison_dir: Path,
    pilot_materialized_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    route_a_summary = load_json(controlled_supervision_expansion_dir / "expanded_labeled_summary.json")
    route_a_logistic = load_json(controlled_supervision_expansion_dir / "expanded_logistic_summary.json")
    route_b_summary = load_json(more_natural_bootstrap_dir / "more_natural_label_summary.json")
    route_b_logistic = load_json(more_natural_bootstrap_dir / "more_natural_logistic_summary.json")
    route_c_summary = load_json(benchmark_truth_leaning_bootstrap_dir / "benchmark_truth_leaning_summary.json")
    route_c_logistic = load_json(benchmark_truth_leaning_bootstrap_dir / "benchmark_truth_leaning_logistic_summary.json")
    prior_recommendation = load_json(supervision_route_comparison_dir / "supervision_next_step_recommendation.json")
    pilot_slice = load_jsonl(pilot_materialized_dir / "csqa_reasoning_pilot_slice.jsonl")

    current_slice_size = len(pilot_slice)
    expanded_slice_target = current_slice_size + 5
    route_d_candidate = {
        "route_code": "D",
        "route_name": "labeled_slice_expansion_bootstrap",
        "current_slice_size": current_slice_size,
        "target_slice_size": expanded_slice_target,
        "expected_route_b_rows_after_expansion": expanded_slice_target,
        "expected_route_c_rows_after_expansion": expanded_slice_target * 2,
        "expected_route_a_rows_after_expansion": expanded_slice_target * 2,
        "value_statement": (
            "Expand the shared labeled substrate first so that future route B and route C runs are no longer ceilinged by the same 5-sample slice."
        ),
        "main_limitations": [
            "This is not a new supervision signal by itself.",
            "It only enlarges the base substrate for later route-B/route-C execution.",
        ],
    }

    gain_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_routes": {
            "route_a": {
                "num_rows": int(route_a_summary["num_rows"]),
                "num_base_samples": int(route_a_summary["num_base_samples"]),
                "label_scope": str(route_a_summary["label_scope"]),
                "logistic_status": str(route_a_logistic["summary_status"]),
            },
            "route_b": {
                "num_rows": int(route_b_summary["num_rows"]),
                "num_base_samples": int(route_b_summary["num_base_samples"]),
                "label_name": str(route_b_summary["label_name"]),
                "label_scope": str(route_b_summary["label_scope"]),
                "label_naturalness_level": str(route_b_summary["label_naturalness_level"]),
                "logistic_status": str(route_b_logistic["summary_status"]),
            },
            "route_c": {
                "num_rows": int(route_c_summary["num_rows"]),
                "num_base_samples": int(route_c_summary["num_base_samples"]),
                "label_name": str(route_c_summary["label_name"]),
                "label_scope": str(route_c_summary["label_scope"]),
                "label_naturalness_level": str(route_c_summary["label_naturalness_level"]),
                "logistic_status": str(route_c_logistic["summary_status"]),
            },
            "route_d_candidate": route_d_candidate,
        },
        "main_question_answer": (
            "Route C is more truth-leaning than route B, but both are already constrained by the same 5-sample slice. "
            "The next highest-value step is therefore D: expand the shared labeled slice first."
        ),
        "key_findings": [
            "Route B already covers all 5 currently aligned base samples.",
            "Route C already doubles contract rows to 10, but it still depends on the same 5 base samples.",
            "Route D does not add a new label by itself, but it increases the substrate that both route B and route C can reuse next.",
        ],
        "historical_context": {
            "prior_supervision_route_recommendation": str(prior_recommendation["chosen_route"]),
            "prior_supervision_route_name": str(prior_recommendation["chosen_route_name"]),
        },
    }

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "routes": [
            {
                "route_code": "B",
                "route_name": "more_natural_supervision_proxy",
                "current_benefit": "Grounded in task correctness at the base-sample level.",
                "current_ceiling": "already spans all current 5 base samples",
                "realism_gain_over_A": "moderate",
                "realism_gain_over_previous": "more natural than controlled supervision",
                "next_bottleneck": "needs a larger slice to increase coverage",
                "recommendation_rank": 3,
            },
            {
                "route_code": "C",
                "route_name": "benchmark_truth_leaning_supervision_proxy",
                "current_benefit": "Grounded in contract-level answer correctness and already materialized on 10 rows.",
                "current_ceiling": "still anchored to the same 5 base samples",
                "realism_gain_over_B": "moderate",
                "realism_gain_over_previous": "closer to task truth than route B",
                "next_bottleneck": "needs a larger slice to keep adding new contracts",
                "recommendation_rank": 2,
            },
            {
                "route_code": "D",
                "route_name": "labeled_slice_expansion_bootstrap",
                "current_benefit": "Unlocks future headroom for both route B and route C at the same time.",
                "current_ceiling": "requires new local sample authoring, but no new external resource",
                "realism_gain_over_B": "indirect",
                "realism_gain_over_C": "indirect",
                "next_bottleneck": "expanded slice still remains local and pilot-level",
                "recommendation_rank": 1,
            },
        ],
    }

    gain_rows = [
        {
            "route_code": "B",
            "route_name": "more_natural_supervision_proxy",
            "executability_now": "pass",
            "truth_anchor_level": "task_truth_proxy",
            "num_rows": int(route_b_summary["num_rows"]),
            "num_base_samples": int(route_b_summary["num_base_samples"]),
            "current_cost": "low",
            "ceiling_pressure": "high",
            "future_headroom_if_unchanged": "low",
        },
        {
            "route_code": "C",
            "route_name": "benchmark_truth_leaning_supervision_proxy",
            "executability_now": "pass",
            "truth_anchor_level": "contract_level_task_truth_proxy",
            "num_rows": int(route_c_summary["num_rows"]),
            "num_base_samples": int(route_c_summary["num_base_samples"]),
            "current_cost": "low",
            "ceiling_pressure": "high",
            "future_headroom_if_unchanged": "low_medium",
        },
        {
            "route_code": "D",
            "route_name": "labeled_slice_expansion_bootstrap",
            "executability_now": "ready_to_materialize",
            "truth_anchor_level": "shared_substrate_expansion",
            "num_rows": route_d_candidate["target_slice_size"],
            "num_base_samples": route_d_candidate["target_slice_size"],
            "current_cost": "low_medium",
            "ceiling_pressure": "medium",
            "future_headroom_if_unchanged": "high",
        },
    ]

    realism_cost_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "definitions": {
            "route_b": "more-natural proxy supervision grounded in task correctness at sample level",
            "route_c": "benchmark-truth-leaning proxy supervision grounded in contract-level answer correctness",
            "route_d": "shared labeled-slice expansion that prepares larger future route-B/route-C runs",
        },
        "realism_vs_cost_ranking": [
            {
                "route_code": "D",
                "why": "Best next-step leverage because it increases future B/C headroom without requiring external resources.",
            },
            {
                "route_code": "C",
                "why": "Currently the strongest truth-leaning proxy among runnable routes, but already limited by the same slice.",
            },
            {
                "route_code": "B",
                "why": "Still useful for diversity of supervision semantics, but immediate marginal coverage gain is weakest right now.",
            },
        ],
        "ceiling_summary": {
            "route_b": "base-sample ceiling already reached on current slice",
            "route_c": "contract rows expanded, but still slice-limited",
            "route_d": "expansion remains pilot-level and local, not benchmark-scale",
        },
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "chosen_route": "D",
        "chosen_route_name": "labeled_slice_expansion_bootstrap",
        "why_chosen": [
            "Route B and route C are both now visibly constrained by the same 5-base-sample local slice.",
            "Route C is more truth-leaning than route B, but its next gain is also blocked by the slice ceiling.",
            "Route D is the lowest-cost move that increases future headroom for both route B and route C at once.",
        ],
        "why_not_B_first": [
            "Route B already covers all currently aligned base samples.",
            "Without a larger slice, the next B expansion would mostly reshuffle the same substrate.",
        ],
        "why_not_C_first": [
            "Route C already proves the stronger truth-leaning proxy path exists.",
            "Its next marginal benefit is also limited by the same current slice size.",
        ],
        "bootstrap_contract": {
            "chosen_route": "D",
            "goal": "Expand the current 5-row local labeled slice into a larger reusable pilot substrate that later route-B and route-C runs can both consume.",
            "input_resources": [
                "outputs/pilot_materialization/pilot_csqa_reasoning_local/csqa_reasoning_pilot_slice.jsonl",
                "src/eval/pilot_execution.py",
                "src/eval/pilot_extension.py",
                "src/eval/pilot_illumination.py",
                "src/eval/labeled_pilot_bootstrap.py",
            ],
            "label_source_or_expansion_mode": "local curated CSQA-style sample expansion with reusable reasoning/confidence/illumination/labeled-illumination query contracts",
            "success_criteria": [
                "materialize a 10-row expanded labeled slice",
                "emit reusable bridge contracts for route B and route C",
                "prove the expanded contracts are executable via dry-run probe paths",
            ],
            "known_risks": [
                "Expanded slice remains local and pilot-level.",
                "No new benchmark ground truth is introduced by this step alone.",
            ],
        },
    }

    write_json(output_dir / "route_b_vs_c_gain_summary.json", gain_summary)
    write_json(output_dir / "route_b_vs_c_vs_d_comparison.json", comparison)
    write_csv(output_dir / "supervision_route_gain_matrix.csv", gain_rows)
    write_json(output_dir / "supervision_realism_cost_summary.json", realism_cost_summary)
    write_json(output_dir / "route_b_vs_c_next_step_recommendation.json", recommendation)
    (output_dir / "build.log").write_text(
        "\n".join(
            [
                "TriScope-LLM route B vs C vs D supervision comparison",
                "Compared routes: B, C, D",
                "Chosen route: D",
                "Why: both B and C are slice-limited; D expands shared substrate",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "gain_summary": gain_summary,
        "comparison": comparison,
        "recommendation": recommendation,
        "output_paths": {
            "gain_summary": str((output_dir / "route_b_vs_c_gain_summary.json").resolve()),
            "comparison": str((output_dir / "route_b_vs_c_vs_d_comparison.json").resolve()),
            "gain_matrix": str((output_dir / "supervision_route_gain_matrix.csv").resolve()),
            "realism_cost_summary": str((output_dir / "supervision_realism_cost_summary.json").resolve()),
            "recommendation": str((output_dir / "route_b_vs_c_next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
