"""Repair audit for DualScope first-slice real-run artifact validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import (
    SCHEMA_VERSION,
    markdown,
    read_json,
    read_jsonl,
    run_py_compile,
    write_json,
    write_jsonl,
)


TASK_NAME = "dualscope-first-slice-real-run-artifact-validation-repair"
VALIDATED_VERDICT = "First-slice real-run artifact validation repair validated"
PARTIAL_VERDICT = "Partially validated"
NOT_VALIDATED_VERDICT = "Not validated"

PY_FILES = [
    "src/eval/dualscope_first_slice_real_run_artifact_validation_repair.py",
    "src/eval/post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py",
    "scripts/build_dualscope_first_slice_real_run_artifact_validation_repair.py",
    "scripts/build_post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py",
]

PREVIOUS_VALIDATION_FILES = [
    "dualscope_first_slice_real_run_artifact_validation_summary.json",
    "dualscope_first_slice_real_run_artifact_validation_verdict.json",
    "dualscope_first_slice_real_run_artifact_validation_report.md",
    "dualscope_first_slice_real_run_artifact_validation_next_step_recommendation.json",
    "dualscope_first_slice_real_run_artifact_checklist.json",
    "dualscope_first_slice_real_run_capability_validation.json",
    "dualscope_first_slice_real_run_metric_label_validation.json",
]

POST_ANALYSIS_FILES = [
    "dualscope_first_slice_real_run_artifact_validation_analysis_summary.json",
    "dualscope_first_slice_real_run_artifact_validation_verdict.json",
    "dualscope_first_slice_real_run_artifact_validation_analysis_report.md",
    "dualscope_first_slice_real_run_artifact_validation_next_step_recommendation.json",
]

TARGET_RESPONSE_FILES = [
    "dualscope_first_slice_target_response_generation_plan_summary.json",
    "dualscope_first_slice_target_response_generation_plan_rows.jsonl",
    "dualscope_first_slice_target_response_generation_plan_verdict.json",
    "dualscope_first_slice_target_response_generation_plan_report.md",
    "dualscope_first_slice_target_response_generation_plan_metric_dependency.json",
]

CONDITION_RERUN_FILES = [
    "dualscope_minimal_first_slice_condition_level_rerun_summary.json",
    "dualscope_minimal_first_slice_condition_level_rerun_alignment.json",
    "dualscope_minimal_first_slice_condition_level_rerun_metric_readiness.json",
    "dualscope_minimal_first_slice_condition_level_rerun_detection_metrics.json",
    "dualscope_minimal_first_slice_condition_level_rerun_joined_predictions.jsonl",
    "dualscope_minimal_first_slice_condition_level_rerun_verdict.json",
    "stage2_confidence/stage2_capability_mode_report.json",
]

FROZEN_CONTRACT_FILES = {
    "illumination": "dualscope_illumination_io_contract.json",
    "confidence": "dualscope_confidence_capability_contract.json",
    "fusion": "dualscope_final_decision_contract.json",
}


def _read_optional_json(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {"summary_status": "MISSING", "path": str(path)}


def _safe_jsonl_count(path: Path) -> int:
    return len(read_jsonl(path)) if path.exists() else 0


def _missing_files(root: Path, names: list[str]) -> list[str]:
    return [name for name in names if not (root / name).exists()]


def _status_from_missing(missing: list[str]) -> str:
    return "PASS" if not missing else "PARTIAL"


def build_real_run_artifact_validation_repair(
    output_dir: Path,
    validation_dir: Path,
    validation_analysis_dir: Path,
    labeled_rerun_dir: Path,
    condition_rerun_dir: Path,
    row_level_fusion_alignment_dir: Path,
    target_response_dir: Path,
    illumination_freeze_dir: Path,
    confidence_freeze_dir: Path,
    fusion_freeze_dir: Path,
    seed: int,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)

    prior_summary = _read_optional_json(validation_dir / "dualscope_first_slice_real_run_artifact_validation_summary.json")
    prior_capability = _read_optional_json(validation_dir / "dualscope_first_slice_real_run_capability_validation.json")
    prior_metric = _read_optional_json(validation_dir / "dualscope_first_slice_real_run_metric_label_validation.json")
    prior_verdict = _read_optional_json(validation_dir / "dualscope_first_slice_real_run_artifact_validation_verdict.json")
    post_summary = _read_optional_json(
        validation_analysis_dir / "dualscope_first_slice_real_run_artifact_validation_analysis_summary.json"
    )
    labeled_summary = _read_optional_json(
        labeled_rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_summary.json"
    )
    labeled_metric = _read_optional_json(
        labeled_rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_metric_readiness.json"
    )
    condition_summary = _read_optional_json(
        condition_rerun_dir / "dualscope_minimal_first_slice_condition_level_rerun_summary.json"
    )
    condition_alignment = _read_optional_json(
        condition_rerun_dir / "dualscope_minimal_first_slice_condition_level_rerun_alignment.json"
    )
    condition_metric = _read_optional_json(
        condition_rerun_dir / "dualscope_minimal_first_slice_condition_level_rerun_metric_readiness.json"
    )
    detection_preview = _read_optional_json(
        condition_rerun_dir / "dualscope_minimal_first_slice_condition_level_rerun_detection_metrics.json"
    )
    condition_capability = _read_optional_json(condition_rerun_dir / "stage2_confidence/stage2_capability_mode_report.json")
    target_summary = _read_optional_json(
        target_response_dir / "dualscope_first_slice_target_response_generation_plan_summary.json"
    )
    target_metric = _read_optional_json(
        target_response_dir / "dualscope_first_slice_target_response_generation_plan_metric_dependency.json"
    )

    prior_missing = _missing_files(validation_dir, PREVIOUS_VALIDATION_FILES)
    post_missing = _missing_files(validation_analysis_dir, POST_ANALYSIS_FILES)
    target_missing = _missing_files(target_response_dir, TARGET_RESPONSE_FILES)
    condition_missing = _missing_files(condition_rerun_dir, CONDITION_RERUN_FILES)
    frozen_missing = [
        str(illumination_freeze_dir / FROZEN_CONTRACT_FILES["illumination"])
        for _ in [0]
        if not (illumination_freeze_dir / FROZEN_CONTRACT_FILES["illumination"]).exists()
    ] + [
        str(confidence_freeze_dir / FROZEN_CONTRACT_FILES["confidence"])
        for _ in [0]
        if not (confidence_freeze_dir / FROZEN_CONTRACT_FILES["confidence"]).exists()
    ] + [
        str(fusion_freeze_dir / FROZEN_CONTRACT_FILES["fusion"])
        for _ in [0]
        if not (fusion_freeze_dir / FROZEN_CONTRACT_FILES["fusion"]).exists()
    ]

    row_level_alignment_missing = not row_level_fusion_alignment_dir.exists()
    equivalent_condition_alignment_present = condition_alignment.get("summary_status") == "PASS"
    missing_artifact_audit = {
        "summary_status": "PASS" if not condition_missing and not target_missing and not prior_missing else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "previous_validation_missing": prior_missing,
        "previous_post_analysis_missing": post_missing,
        "target_response_generation_missing": target_missing,
        "condition_level_rerun_missing": condition_missing,
        "frozen_contract_missing": frozen_missing,
        "row_level_fusion_alignment_dir_missing": row_level_alignment_missing,
        "condition_rerun_alignment_available_as_current_row_level_evidence": equivalent_condition_alignment_present,
        "notes": [
            "The standalone row-level fusion-alignment directory is absent.",
            "The condition-level rerun alignment artifact is present and row_id keyed.",
        ],
    }

    schema_granularity = {
        "summary_status": "PASS" if equivalent_condition_alignment_present else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "previous_validation_source": prior_summary.get("recommended_next_step"),
        "previous_labels_available": prior_metric.get("labels_available"),
        "labeled_rerun_labels_ready": labeled_metric.get("labels_ready"),
        "previous_condition_level_predictions_ready": prior_summary.get("condition_level_predictions_ready"),
        "condition_level_predictions_ready": condition_summary.get("condition_level_predictions_ready"),
        "condition_prediction_scope": condition_alignment.get("prediction_scope"),
        "joined_condition_row_count": condition_alignment.get("joined_row_count"),
        "clean_row_count": condition_alignment.get("clean_row_count"),
        "poisoned_triggered_row_count": condition_alignment.get("poisoned_triggered_row_count"),
        "granularity_mismatch": prior_metric.get("labels_available") is False and labeled_metric.get("labels_ready") is True,
        "repair_interpretation": (
            "Prior validation summarized older source-level readiness; current condition-level rerun provides row_id-keyed "
            "clean/poisoned predictions suitable for detection preview analysis."
        ),
    }

    metric_guardrail = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "detection_preview_metric_scope": detection_preview.get("metric_scope"),
        "detection_preview_real_performance_claimed": detection_preview.get("real_performance_claimed"),
        "condition_detection_preview_ready": condition_metric.get("condition_level_detection_preview_ready"),
        "auroc_preview_ready": condition_metric.get("auroc_preview_ready"),
        "f1_preview_ready": condition_metric.get("f1_preview_ready"),
        "asr_ready": condition_metric.get("asr_ready"),
        "clean_utility_ready": condition_metric.get("clean_utility_ready"),
        "model_responses_ready": condition_metric.get("model_responses_ready"),
        "paper_performance_metrics_ready": condition_metric.get("paper_performance_metrics_ready"),
        "target_plan_performance_metrics_reported": target_summary.get("performance_metrics_reported"),
        "target_plan_model_responses_generated": target_summary.get("model_responses_generated"),
        "allowed_to_report_as_full_model_performance": False,
        "projected_metric_vs_full_metric_confusion_repaired": True,
        "reason": "AUROC/F1 are condition-level detection previews only; ASR and clean utility require real generated model responses.",
    }

    capability_fallback = {
        "summary_status": "PASS" if condition_capability.get("fallback_degradation_flag") is True else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "previous_selected_mode": prior_capability.get("selected_mode"),
        "previous_stage2_mode": prior_capability.get("stage2_capability_mode_after_rerun"),
        "condition_stage2_capability_mode": condition_capability.get("capability_mode"),
        "condition_fallback_degradation_flag": condition_capability.get("fallback_degradation_flag"),
        "condition_no_logprobs_reason": condition_capability.get("no_logprobs_reason"),
        "capability_mode_or_fallback_flags_missing_in_previous_summary": "fallback_degradation_flag" not in prior_capability,
        "current_capability_flags_sufficient_for_repair": condition_capability.get("fallback_degradation_flag") is True
        and bool(condition_capability.get("no_logprobs_reason")),
    }

    report_verdict_recommendation = {
        "summary_status": _status_from_missing(prior_missing + post_missing + target_missing),
        "schema_version": SCHEMA_VERSION,
        "previous_validation_report_present": (validation_dir / "dualscope_first_slice_real_run_artifact_validation_report.md").exists(),
        "previous_validation_verdict_present": (validation_dir / "dualscope_first_slice_real_run_artifact_validation_verdict.json").exists(),
        "previous_validation_recommendation_present": (
            validation_dir / "dualscope_first_slice_real_run_artifact_validation_next_step_recommendation.json"
        ).exists(),
        "post_analysis_report_present": (
            validation_analysis_dir / "dualscope_first_slice_real_run_artifact_validation_analysis_report.md"
        ).exists(),
        "target_response_report_present": (
            target_response_dir / "dualscope_first_slice_target_response_generation_plan_report.md"
        ).exists(),
        "missing_report_verdict_or_recommendation": prior_missing + post_missing + target_missing,
    }

    forbidden_check = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "labels_fabricated": False,
        "model_outputs_fabricated": False,
        "route_c_199_plus_generated": False,
        "performance_metrics_fabricated": False,
    }

    joined_predictions_count = _safe_jsonl_count(
        condition_rerun_dir / "dualscope_minimal_first_slice_condition_level_rerun_joined_predictions.jsonl"
    )
    target_generation_count = _safe_jsonl_count(
        target_response_dir / "dualscope_first_slice_target_response_generation_plan_rows.jsonl"
    )
    repair_manifest = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "repair_only": True,
        "seed": seed,
        "input_counts": {
            "condition_joined_prediction_rows": joined_predictions_count,
            "target_generation_request_rows": target_generation_count,
        },
        "generated_artifacts": [
            "dualscope_first_slice_real_run_artifact_validation_repair_scope.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_partial_verdict_audit.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_gap_taxonomy.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_schema_granularity.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_metric_guardrail.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_capability_fallback.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_report_status.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_summary.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_verdict.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_next_step_recommendation.json",
            "dualscope_first_slice_real_run_artifact_validation_repair_report.md",
        ],
    }

    py_compile = run_py_compile(repo_root, PY_FILES)
    repair_validated = (
        py_compile["passed"]
        and prior_summary.get("final_verdict") == PARTIAL_VERDICT
        and condition_summary.get("condition_level_predictions_ready") is True
        and condition_metric.get("real_performance_claimed") is False
        and condition_metric.get("model_responses_ready") is False
        and detection_preview.get("real_performance_claimed") is False
        and capability_fallback["summary_status"] == "PASS"
        and not condition_missing
        and not target_missing
        and not frozen_missing
    )
    if repair_validated:
        final_verdict = VALIDATED_VERDICT
        recommendation = "dualscope-first-slice-model-response-metrics"
    elif py_compile["passed"]:
        final_verdict = PARTIAL_VERDICT
        recommendation = "dualscope-first-slice-real-run-artifact-validation-repair"
    else:
        final_verdict = NOT_VALIDATED_VERDICT
        recommendation = "dualscope-first-slice-real-run-artifact-validation-blocker-closure"

    partial_verdict_audit = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "previous_final_verdict": prior_verdict.get("final_verdict") or prior_summary.get("final_verdict"),
        "previous_artifact_chain_passed": prior_summary.get("artifact_chain_passed"),
        "previous_performance_metrics_ready": prior_summary.get("performance_metrics_ready"),
        "previous_stage_entrypoints_model_integrated": prior_summary.get("stage_entrypoints_model_integrated"),
        "previous_recommendation": prior_summary.get("recommended_next_step"),
        "post_analysis_final_verdict": post_summary.get("final_verdict"),
        "repair_final_verdict": final_verdict,
        "why_partial": [
            "Previous validation did not consume the newer condition-row rerun artifacts.",
            "Previous metric validation recorded labels unavailable, while labeled rerun artifacts now have labels ready.",
            "Full ASR and clean utility remain blocked because model responses are not generated.",
            "Preview AUROC/F1 must remain scoped as condition-level detection preview metrics.",
        ],
    }
    gap_taxonomy = {
        "summary_status": "PASS" if final_verdict != NOT_VALIDATED_VERDICT else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "missing_artifacts": missing_artifact_audit,
        "schema_mismatch": {
            "summary_status": "PASS",
            "old_label_field_conflict": {
                "previous_labels_available": prior_metric.get("labels_available"),
                "current_labels_ready": labeled_metric.get("labels_ready"),
            },
            "old_capability_summary_conflict": {
                "previous_selected_mode": prior_capability.get("selected_mode"),
                "current_condition_stage2_mode": condition_capability.get("capability_mode"),
            },
        },
        "granularity_mismatch": schema_granularity,
        "projected_metric_versus_full_metric_confusion": metric_guardrail,
        "missing_capability_mode_or_fallback_flags": capability_fallback,
        "missing_report_verdict_or_recommendation_artifacts": report_verdict_recommendation,
    }
    summary = {
        "summary_status": "PASS" if final_verdict != NOT_VALIDATED_VERDICT else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "previous_validation_verdict": prior_summary.get("final_verdict"),
        "condition_level_predictions_ready": condition_summary.get("condition_level_predictions_ready"),
        "condition_detection_preview_ready": condition_metric.get("condition_level_detection_preview_ready"),
        "model_responses_ready": condition_metric.get("model_responses_ready"),
        "paper_performance_metrics_ready": condition_metric.get("paper_performance_metrics_ready"),
        "asr_ready": condition_metric.get("asr_ready"),
        "clean_utility_ready": condition_metric.get("clean_utility_ready"),
        "row_level_alignment_dir_missing": row_level_alignment_missing,
        "condition_alignment_available": equivalent_condition_alignment_present,
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "labels_fabricated": False,
        "model_outputs_fabricated": False,
        "route_c_199_plus_generated": False,
        "real_performance_claimed": False,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "output_dir": str(output_dir),
        "validation_dir": str(validation_dir),
        "validation_analysis_dir": str(validation_analysis_dir),
        "labeled_rerun_dir": str(labeled_rerun_dir),
        "condition_rerun_dir": str(condition_rerun_dir),
        "row_level_fusion_alignment_dir": str(row_level_fusion_alignment_dir),
        "target_response_dir": str(target_response_dir),
        "illumination_freeze_dir": str(illumination_freeze_dir),
        "confidence_freeze_dir": str(confidence_freeze_dir),
        "fusion_freeze_dir": str(fusion_freeze_dir),
        "repair_only": True,
        "seed": seed,
    }

    details = [
        {"detail_type": "previous_partial_verdict", "payload": partial_verdict_audit},
        {"detail_type": "missing_artifacts", "payload": missing_artifact_audit},
        {"detail_type": "schema_granularity", "payload": schema_granularity},
        {"detail_type": "metric_guardrail", "payload": metric_guardrail},
        {"detail_type": "capability_fallback", "payload": capability_fallback},
        {"detail_type": "report_verdict_recommendation", "payload": report_verdict_recommendation},
    ]

    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_scope.json", scope)
    write_json(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_partial_verdict_audit.json",
        partial_verdict_audit,
    )
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_gap_taxonomy.json", gap_taxonomy)
    write_json(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_schema_granularity.json",
        schema_granularity,
    )
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_metric_guardrail.json", metric_guardrail)
    write_json(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_capability_fallback.json",
        capability_fallback,
    )
    write_json(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_report_status.json",
        report_verdict_recommendation,
    )
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_forbidden_check.json", forbidden_check)
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_manifest.json", repair_manifest)
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_summary.json", summary)
    write_json(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_verdict.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "single_verdict_policy": "one_of_first_slice_real_run_artifact_validation_repair_validated__partially_validated__not_validated",
        },
    )
    write_json(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_next_step_recommendation.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": recommendation,
        },
    )
    write_jsonl(output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_details.jsonl", details)
    markdown(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_report.md",
        "First-Slice Real-Run Artifact Validation Repair",
        [
            f"- Previous verdict: `{prior_summary.get('final_verdict')}`",
            f"- Condition-level predictions ready: `{condition_summary.get('condition_level_predictions_ready')}`",
            f"- Condition detection preview ready: `{condition_metric.get('condition_level_detection_preview_ready')}`",
            f"- Model responses ready: `{condition_metric.get('model_responses_ready')}`",
            f"- Full paper performance ready: `{condition_metric.get('paper_performance_metrics_ready')}`",
            f"- Standalone row-level fusion alignment dir missing: `{row_level_alignment_missing}`",
            f"- Condition alignment artifact available: `{equivalent_condition_alignment_present}`",
            f"- Final verdict: `{final_verdict}`",
            f"- Recommended next step: `{recommendation}`",
            "- This repair does not claim preview metrics as full model performance.",
        ],
    )
    return summary
