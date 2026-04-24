"""Compact analysis and next-step recommendation for real-pilot artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


REAL_PILOT_ANALYSIS_SCHEMA_VERSION = "triscopellm/real-pilot-analysis/v1"


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


def _pilot_row(
    module_name: str,
    run_summary: dict[str, Any],
    feature_summary: dict[str, Any],
) -> dict[str, Any]:
    common = {
        "module_name": module_name,
        "run_id": feature_summary.get("run_id"),
        "experiment_profile": run_summary.get("experiment_profile"),
        "dataset_profile": run_summary.get("dataset_profile"),
        "model_profile": run_summary.get("model_profile"),
        "feature_extraction_completed": run_summary.get("feature_extraction_completed"),
        "summary_status": run_summary.get("summary_status"),
        "seed": run_summary.get("seed"),
        "smoke_mode": run_summary.get("smoke_mode"),
    }
    if module_name == "reasoning":
        common.update(
            {
                "num_samples": feature_summary.get("num_samples"),
                "answer_changed_rate": feature_summary.get("answer_changed_rate"),
                "target_behavior_flip_rate": feature_summary.get("target_behavior_flip_rate"),
                "primary_signal": "answer_changed_after_reasoning",
            }
        )
    elif module_name == "confidence":
        common.update(
            {
                "num_samples": feature_summary.get("num_samples"),
                "target_behavior_rate": feature_summary.get("target_behavior_rate"),
                "high_confidence_fraction_mean": feature_summary.get("high_confidence_fraction_mean"),
                "entropy_collapse_score_mean": feature_summary.get("entropy_collapse_score_mean"),
                "primary_signal": "confidence_collapse",
            }
        )
    else:
        common.update(
            {
                "num_samples": feature_summary.get("num_prompts"),
                "target_behavior_rate": feature_summary.get("target_behavior_rate"),
                "realized_budget_ratio": feature_summary.get("realized_budget_ratio"),
                "variance_across_prompts": feature_summary.get("variance_across_prompts"),
                "primary_signal": "targeted_icl_susceptibility",
            }
        )
    return common


def build_real_pilot_analysis(
    real_pilot_readiness_summary_path: Path,
    real_pilot_alignment_summary_path: Path,
    real_pilot_rule_summary_path: Path,
    real_pilot_logistic_summary_path: Path,
    reasoning_run_summary_path: Path,
    reasoning_feature_summary_path: Path,
    confidence_run_summary_path: Path,
    confidence_feature_summary_path: Path,
    illumination_run_summary_path: Path,
    illumination_feature_summary_path: Path,
    smoke_report_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    readiness_summary = load_json(real_pilot_readiness_summary_path)
    alignment_summary = load_json(real_pilot_alignment_summary_path)
    rule_summary = load_json(real_pilot_rule_summary_path)
    logistic_summary = load_json(real_pilot_logistic_summary_path)
    smoke_report_summary = load_json(smoke_report_summary_path)

    reasoning_run_summary = load_json(reasoning_run_summary_path)
    reasoning_feature_summary = load_json(reasoning_feature_summary_path)
    confidence_run_summary = load_json(confidence_run_summary_path)
    confidence_feature_summary = load_json(confidence_feature_summary_path)
    illumination_run_summary = load_json(illumination_run_summary_path)
    illumination_feature_summary = load_json(illumination_feature_summary_path)

    comparison_rows = [
        _pilot_row("reasoning", reasoning_run_summary, reasoning_feature_summary),
        _pilot_row("confidence", confidence_run_summary, confidence_feature_summary),
        _pilot_row("illumination", illumination_run_summary, illumination_feature_summary),
    ]

    blocker_summary = {
        "summary_status": "PASS",
        "schema_version": REAL_PILOT_ANALYSIS_SCHEMA_VERSION,
        "primary_blocker": "missing_ground_truth_labels",
        "blocking_stage": "supervised_real_pilot_fusion_baseline",
        "root_cause": logistic_summary.get("reason"),
        "full_intersection_available": readiness_summary.get("full_intersection_available"),
        "current_real_pilot_modules": readiness_summary.get("real_pilot_modules"),
        "resolved_blockers": [
            "multi_pilot_coverage",
            "cross_modal_alignment",
            "real_pilot_rule_baseline_existence",
        ],
        "remaining_blockers": [
            {
                "blocker_name": "missing_ground_truth_labels",
                "scope": "real_pilot_logistic_baseline",
                "why_it_matters": (
                    "The aligned real-pilot fusion dataset now exists, but there is still no "
                    "auditable supervision field to support a supervised baseline."
                ),
                "evidence": logistic_summary.get("notes", []),
            },
            {
                "blocker_name": "pilot_level_semantic_narrowness",
                "scope": "research_grade_experiments",
                "why_it_matters": (
                    "All current real pilots share the same local slice and small model, which is "
                    "enough for execution-path validation but not for research-scale claims."
                ),
            },
        ],
    }

    real_pilot_vs_smoke_summary = {
        "summary_status": "PASS",
        "schema_version": REAL_PILOT_ANALYSIS_SCHEMA_VERSION,
        "real_pilot_modules": readiness_summary.get("real_pilot_modules"),
        "real_pilot_full_intersection_available": readiness_summary.get("full_intersection_available"),
        "real_pilot_num_aligned_rows": readiness_summary.get("num_aligned_rows"),
        "smoke_module_status": smoke_report_summary.get("module_status"),
        "smoke_fusion_num_rows": smoke_report_summary.get("fusion_snapshot", {}).get("num_rows"),
        "smoke_rule_baseline_available": smoke_report_summary.get("baseline_snapshot", {}).get("rule_num_predictions", 0) > 0,
        "smoke_logistic_baseline_available": smoke_report_summary.get("baseline_snapshot", {}).get("logistic_num_predictions", 0) > 0,
        "real_pilot_rule_baseline_available": rule_summary.get("summary_status") == "PASS",
        "real_pilot_logistic_baseline_available": logistic_summary.get("summary_status") == "PASS",
        "real_pilot_limitations": [
            "local_csqa_style_slice_only",
            "pilot_distilgpt2_hf_only",
            "pilot_level_evidence_not_research_grade",
        ],
    }

    real_pilot_analysis_summary = {
        "summary_status": "PASS",
        "schema_version": REAL_PILOT_ANALYSIS_SCHEMA_VERSION,
        "real_pilot_modules": readiness_summary.get("real_pilot_modules"),
        "num_real_pilot_modules": len(readiness_summary.get("real_pilot_modules", [])),
        "full_intersection_available": readiness_summary.get("full_intersection_available"),
        "num_aligned_rows": readiness_summary.get("num_aligned_rows"),
        "rule_baseline_status": rule_summary.get("summary_status"),
        "rule_baseline_num_predictions": rule_summary.get("num_predictions"),
        "rule_baseline_mean_prediction_score": rule_summary.get("mean_prediction_score"),
        "logistic_baseline_status": logistic_summary.get("summary_status"),
        "logistic_skip_reason": logistic_summary.get("reason"),
        "shared_dataset_profile": readiness_summary.get("shared_dataset_profile"),
        "shared_model_profile": readiness_summary.get("shared_model_profile"),
        "pilot_vs_smoke_scope": "compact_readiness_and_blocker_analysis",
        "notes": [
            "The real-pilot stack now covers illumination, reasoning, and confidence on a shared local slice.",
            "The current fusion bottleneck is no longer coverage or missingness; it is label availability.",
            "This analysis is intended to select the next engineering step, not to claim benchmark-level performance.",
        ],
        "artifacts": {
            "real_pilot_vs_smoke_summary": str((output_dir / "real_pilot_vs_smoke_summary.json").resolve()),
            "real_pilot_vs_pilot_comparison": str((output_dir / "real_pilot_vs_pilot_comparison.csv").resolve()),
            "real_pilot_blocker_summary": str((output_dir / "real_pilot_blocker_summary.json").resolve()),
            "next_step_recommendation": str((output_dir / "next_step_recommendation.json").resolve()),
        },
    }

    next_step_recommendation = {
        "summary_status": "PASS",
        "schema_version": REAL_PILOT_ANALYSIS_SCHEMA_VERSION,
        "decision_scope": "post_real_pilot_fusion_next_step",
        "route_options": [
            {
                "route_name": "expand_more_unlabeled_pilots",
                "route_code": "A",
                "recommended": False,
                "priority_score": 0.38,
                "pros": [
                    "Could broaden execution coverage.",
                    "Could expose more module-level behaviors on additional pilot slices.",
                ],
                "cons": [
                    "Does not remove the supervised logistic blocker.",
                    "Adds more pilot breadth before the first labeled supervised path exists.",
                ],
            },
            {
                "route_name": "first_labeled_pilot_bootstrap",
                "route_code": "B",
                "recommended": True,
                "priority_score": 0.92,
                "pros": [
                    "Directly addresses the missing_ground_truth_labels blocker.",
                    "Lets the repository materialize its first honest supervised pilot path.",
                    "Provides the highest marginal value relative to adding another unlabeled pilot.",
                ],
                "cons": [
                    "The first label source will still be pilot-level controlled supervision, not benchmark truth.",
                ],
            },
        ],
        "recommended_route": "first_labeled_pilot_bootstrap",
        "recommended_route_code": "B",
        "recommendation_rationale": [
            "Coverage is no longer the first bottleneck because real-pilot full intersection already exists.",
            "Rule-based fusion already runs, so the main missing capability is supervised label availability.",
            "A first labeled pilot is the minimal-cost path that unlocks a supervised preprocessing / baseline path.",
        ],
        "recommended_bootstrap_target": {
            "module_name": "illumination",
            "label_strategy": "controlled_targeted_icl_label",
            "why_this_target": (
                "The illumination query contract already carries explicit target_text and contract metadata, "
                "so it is the cleanest place to introduce a first auditable pilot-level supervision field."
            ),
        },
    }

    write_csv(output_dir / "real_pilot_vs_pilot_comparison.csv", comparison_rows)
    write_json(output_dir / "real_pilot_analysis_summary.json", real_pilot_analysis_summary)
    write_json(output_dir / "real_pilot_vs_smoke_summary.json", real_pilot_vs_smoke_summary)
    write_json(output_dir / "real_pilot_blocker_summary.json", blocker_summary)
    write_json(output_dir / "next_step_recommendation.json", next_step_recommendation)

    log_lines = [
        "TriScope-LLM real-pilot compact analysis",
        f"Readiness summary: {real_pilot_readiness_summary_path.resolve()}",
        f"Alignment summary: {real_pilot_alignment_summary_path.resolve()}",
        f"Rule baseline summary: {real_pilot_rule_summary_path.resolve()}",
        f"Logistic baseline summary: {real_pilot_logistic_summary_path.resolve()}",
        f"Smoke report summary: {smoke_report_summary_path.resolve()}",
    ]
    (output_dir / "build.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    return {
        "real_pilot_analysis_summary": real_pilot_analysis_summary,
        "real_pilot_vs_smoke_summary": real_pilot_vs_smoke_summary,
        "real_pilot_blocker_summary": blocker_summary,
        "next_step_recommendation": next_step_recommendation,
        "output_paths": {
            "real_pilot_analysis_summary": str((output_dir / "real_pilot_analysis_summary.json").resolve()),
            "real_pilot_vs_smoke_summary": str((output_dir / "real_pilot_vs_smoke_summary.json").resolve()),
            "real_pilot_vs_pilot_comparison": str((output_dir / "real_pilot_vs_pilot_comparison.csv").resolve()),
            "real_pilot_blocker_summary": str((output_dir / "real_pilot_blocker_summary.json").resolve()),
            "next_step_recommendation": str((output_dir / "next_step_recommendation.json").resolve()),
            "log": str((output_dir / "build.log").resolve()),
        },
    }
