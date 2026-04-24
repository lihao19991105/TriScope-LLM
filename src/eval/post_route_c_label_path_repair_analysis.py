"""Compare collapse-era and repair-era label-path evidence for route_c."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-label-path-repair-analysis/v1"


def build_post_route_c_label_path_repair_analysis(
    collapse_diagnosis_dir: Path,
    micro_analysis_dir: Path,
    label_health_dir: Path,
    label_recheck_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    collapse_root = load_json(collapse_diagnosis_dir / "route_c_anchor_v2_collapse_root_cause.json")
    micro_summary = load_json(micro_analysis_dir / "route_c_micro_analysis_summary.json")
    micro_recommendation = load_json(micro_analysis_dir / "route_c_micro_next_step_recommendation.json")
    label_health_gate = load_json(label_health_dir / "route_c_label_health_gate_result.json")
    label_recheck_summary = load_json(label_recheck_dir / "route_c_label_recheck_summary.json")
    label_recheck_comparison = load_json(label_recheck_dir / "route_c_precheck_vs_execution_recheck_comparison.json")

    consistency_restored = bool(label_recheck_summary.get("consistency_restored"))
    gate_status = str(label_health_gate.get("gate_status"))
    prior_working_baseline = str(micro_summary.get("working_baseline"))

    if consistency_restored and gate_status == "PASS":
        working_baseline = prior_working_baseline
        repair_phase = "consistency_restored"
    else:
        working_baseline = prior_working_baseline
        repair_phase = "gate_first_not_fully_restored"

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "collapse_era": {
            "primary_root_cause": collapse_root.get("primary_root_cause"),
            "root_cause_statement": collapse_root.get("root_cause_statement"),
            "micro_recommendation": micro_recommendation.get("recommended_next_step"),
        },
        "repair_era": {
            "label_health_gate_status": gate_status,
            "label_health_blocked_reason": label_health_gate.get("blocked_reason"),
            "consistency_restored": consistency_restored,
            "precheck_vs_execution": label_recheck_comparison,
        },
        "working_baseline": working_baseline,
        "repair_phase": repair_phase,
    }

    summary = {
        "summary_status": "PASS_WITH_LIMITATIONS" if repair_phase != "consistency_restored" else "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "working_baseline": working_baseline,
        "label_path_still_primary_blocker": bool(repair_phase != "consistency_restored"),
        "label_health_gate_status": gate_status,
        "consistency_restored": consistency_restored,
        "precheck_label_set": label_recheck_summary.get("precheck_label_set"),
        "execution_label_set": label_recheck_summary.get("execution_label_set"),
    }

    if repair_phase == "consistency_restored":
        recommended_next_step = "resume_guarded_anchor_execution_then_retry_micro"
        why = [
            "Label-path consistency is restored under current gate definitions.",
            "It is now safe to resume guarded execution attempts.",
        ]
    else:
        recommended_next_step = "continue_label_path_instrumentation_and_parser_repair_before_next_execution_attempt"
        why = [
            "Gate diagnostics are now explicit, but consistency is not yet restored.",
            "Execution still does not produce two-class labels under current runtime.",
            "Next effort should target parser/output-normalization robustness before candidate expansion.",
        ]

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "working_baseline": working_baseline,
        "recommended_next_step": recommended_next_step,
        "why": why,
        "not_recommended_yet": [
            "blind_budget_expansion",
            "3b_or_7b_expansion",
            "dataset_axis_expansion",
            "fusion_axis_expansion",
        ],
    }

    write_json(output_dir / "route_c_label_repair_vs_collapse_comparison.json", comparison)
    write_json(output_dir / "route_c_label_repair_analysis_summary.json", summary)
    write_json(output_dir / "route_c_label_repair_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "comparison": str((output_dir / "route_c_label_repair_vs_collapse_comparison.json").resolve()),
            "summary": str((output_dir / "route_c_label_repair_analysis_summary.json").resolve()),
            "recommendation": str((output_dir / "route_c_label_repair_next_step_recommendation.json").resolve()),
        },
    }
