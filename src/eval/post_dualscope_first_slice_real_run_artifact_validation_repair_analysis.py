"""Post-analysis for DualScope artifact-validation repair artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_artifact_validation_repair import (
    NOT_VALIDATED_VERDICT,
    PARTIAL_VERDICT,
    VALIDATED_VERDICT,
)
from src.eval.dualscope_first_slice_real_run_compression_common import SCHEMA_VERSION, markdown, read_json, write_json


POST_SCHEMA_VERSION = "dualscopellm/post-first-slice-real-run-artifact-validation-repair-analysis/v1"

REQUIRED_REPAIR_FILES = [
    "dualscope_first_slice_real_run_artifact_validation_repair_scope.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_partial_verdict_audit.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_gap_taxonomy.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_schema_granularity.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_metric_guardrail.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_capability_fallback.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_report_status.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_manifest.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_py_compile.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_summary.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_verdict.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_next_step_recommendation.json",
    "dualscope_first_slice_real_run_artifact_validation_repair_report.md",
]


def _read_optional_json(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {"summary_status": "MISSING", "path": str(path)}


def build_post_real_run_artifact_validation_repair_analysis(
    repair_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    missing = [name for name in REQUIRED_REPAIR_FILES if not (repair_dir / name).exists()]
    summary = _read_optional_json(
        repair_dir / "dualscope_first_slice_real_run_artifact_validation_repair_summary.json"
    )
    gap_taxonomy = _read_optional_json(
        repair_dir / "dualscope_first_slice_real_run_artifact_validation_repair_gap_taxonomy.json"
    )
    metric_guardrail = _read_optional_json(
        repair_dir / "dualscope_first_slice_real_run_artifact_validation_repair_metric_guardrail.json"
    )
    capability = _read_optional_json(
        repair_dir / "dualscope_first_slice_real_run_artifact_validation_repair_capability_fallback.json"
    )
    py_compile = _read_optional_json(
        repair_dir / "dualscope_first_slice_real_run_artifact_validation_repair_py_compile.json"
    )

    no_fake_performance = (
        metric_guardrail.get("allowed_to_report_as_full_model_performance") is False
        and metric_guardrail.get("model_responses_ready") is False
        and metric_guardrail.get("paper_performance_metrics_ready") is False
    )
    capability_flags_ready = capability.get("current_capability_flags_sufficient_for_repair") is True
    repair_summary_validated = summary.get("final_verdict") == VALIDATED_VERDICT
    if not missing and py_compile.get("passed") is True and repair_summary_validated and no_fake_performance and capability_flags_ready:
        final_verdict = VALIDATED_VERDICT
        recommendation = "dualscope-first-slice-model-response-metrics"
    elif py_compile.get("passed") is True:
        final_verdict = PARTIAL_VERDICT
        recommendation = "dualscope-first-slice-real-run-artifact-validation-repair"
    else:
        final_verdict = NOT_VALIDATED_VERDICT
        recommendation = "dualscope-first-slice-real-run-artifact-validation-blocker-closure"

    analysis = {
        "summary_status": "PASS" if final_verdict != NOT_VALIDATED_VERDICT else "FAIL",
        "schema_version": POST_SCHEMA_VERSION,
        "source_schema_version": SCHEMA_VERSION,
        "seed": seed,
        "repair_dir": str(repair_dir),
        "missing_repair_artifacts": missing,
        "repair_summary_verdict": summary.get("final_verdict"),
        "gap_taxonomy_status": gap_taxonomy.get("summary_status"),
        "no_fake_performance": no_fake_performance,
        "capability_flags_ready": capability_flags_ready,
        "py_compile_passed": py_compile.get("passed"),
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    verdict_payload = {
        "summary_status": analysis["summary_status"],
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_first_slice_real_run_artifact_validation_repair_validated__partially_validated__not_validated",
    }
    recommendation_payload = {
        "summary_status": analysis["summary_status"],
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }

    write_json(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_analysis_summary.json",
        analysis,
    )
    write_json(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_verdict.json",
        verdict_payload,
    )
    write_json(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_next_step_recommendation.json",
        recommendation_payload,
    )
    markdown(
        output_dir / "dualscope_first_slice_real_run_artifact_validation_repair_analysis_report.md",
        "Artifact Validation Repair Analysis",
        [
            f"- Missing repair artifacts: `{len(missing)}`",
            f"- Repair summary verdict: `{summary.get('final_verdict')}`",
            f"- No fake performance: `{no_fake_performance}`",
            f"- Capability flags ready: `{capability_flags_ready}`",
            f"- Final verdict: `{final_verdict}`",
            f"- Recommended next step: `{recommendation}`",
        ],
    )
    return analysis
