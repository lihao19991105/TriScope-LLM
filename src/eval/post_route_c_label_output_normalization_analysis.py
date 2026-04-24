"""Post-recheck analysis for route_c label output normalization minimal repair."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-label-output-normalization-analysis/v1"


def _distribution_delta(raw_dist: dict[str, Any], normalized_dist: dict[str, Any]) -> dict[str, int]:
    keys = sorted(set(raw_dist) | set(normalized_dist))
    return {
        key: int(raw_dist.get(key, 0) or 0) - int(normalized_dist.get(key, 0) or 0)
        for key in keys
    }


def build_post_route_c_label_output_normalization_analysis(
    prior_label_repair_analysis_dir: Path,
    normalization_dir: Path,
    normalization_recheck_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    prior_summary = load_json(prior_label_repair_analysis_dir / "route_c_label_repair_analysis_summary.json")
    prior_recommendation = load_json(
        prior_label_repair_analysis_dir / "route_c_label_repair_next_step_recommendation.json"
    )

    normalization_summary = load_json(
        normalization_dir / "route_c_label_output_normalization_summary.json"
    )
    normalization_compare = load_json(
        normalization_dir / "route_c_label_output_normalization_compare.json"
    )
    recheck_summary = load_json(
        normalization_recheck_dir / "route_c_label_output_normalization_recheck_summary.json"
    )

    raw_dist = normalization_compare.get("raw_parser_outcome", {}).get("failure_category_distribution", {})
    normalized_dist = normalization_compare.get("normalized_parser_outcome", {}).get(
        "failure_category_distribution", {}
    )
    fixed_delta = _distribution_delta(raw_dist, normalized_dist)
    improved_failure_categories = [key for key, delta in fixed_delta.items() if delta > 0]
    remaining_failure_categories = [
        key for key, count in normalized_dist.items() if int(count or 0) > 0
    ]

    consistency_restored = bool(recheck_summary.get("consistency_restored"))
    execution_label_set = recheck_summary.get("execution_label_set")

    summary = {
        "summary_status": "PASS" if consistency_restored else "PASS_WITH_LIMITATIONS",
        "schema_version": SCHEMA_VERSION,
        "working_baseline": prior_summary.get("working_baseline"),
        "prior_strategy_still_valid": True,
        "minimal_normalization_repair_applied": True,
        "consistency_restored": consistency_restored,
        "execution_label_set": execution_label_set,
        "precheck_label_set": recheck_summary.get("precheck_label_set"),
        "gate_status": recheck_summary.get("gate_status"),
        "normalized_parseability": recheck_summary.get("parseability"),
        "improved_failure_categories": improved_failure_categories,
        "remaining_failure_categories": remaining_failure_categories,
        "label_path_still_primary_blocker": not consistency_restored,
        "key_answer": {
            "did_minimal_normalization_fix_primary_blocker": consistency_restored,
            "should_keep_parser_first_strategy": True,
        },
        "source_artifacts": {
            "prior_repair_summary": str(
                (prior_label_repair_analysis_dir / "route_c_label_repair_analysis_summary.json").resolve()
            ),
            "normalization_summary": str(
                (normalization_dir / "route_c_label_output_normalization_summary.json").resolve()
            ),
            "recheck_summary": str(
                (normalization_recheck_dir / "route_c_label_output_normalization_recheck_summary.json").resolve()
            ),
        },
    }

    if consistency_restored:
        next_step = "resume_guarded_anchor_execution_then_retry_micro"
        why = [
            "Execution label set is restored under unchanged gate definitions.",
            "Parser-first minimal repair objective is satisfied for this branch.",
        ]
    else:
        next_step = "keep_label_path_instrumentation_and_target_punct_only_generation_format_control"
        why = [
            "Execution label set is not restored to [0,1] after conservative normalization.",
            "Remaining blocker is still primarily parser drift/output formatting behavior (including punct_only where present).",
            "Further action should stay parser/output-path-first before any expansion attempts.",
        ]

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "working_baseline": prior_summary.get("working_baseline"),
        "recommended_next_step": next_step,
        "why": why,
        "strategy_confirmation": {
            "prior_recommendation": prior_recommendation.get("recommended_next_step"),
            "still_keep_parser_before_expansion": True,
        },
        "not_recommended_yet": [
            "blind_budget_expansion",
            "3b_or_7b_expansion",
            "dataset_axis_expansion",
            "prompt_family_expansion",
        ],
    }

    write_json(output_dir / "route_c_label_output_normalization_analysis_summary.json", summary)
    write_json(output_dir / "route_c_label_output_normalization_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "summary": str((output_dir / "route_c_label_output_normalization_analysis_summary.json").resolve()),
            "recommendation": str(
                (output_dir / "route_c_label_output_normalization_next_step_recommendation.json").resolve()
            ),
        },
    }
