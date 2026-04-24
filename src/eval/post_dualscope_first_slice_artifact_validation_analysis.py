"""Post-analysis for DualScope first-slice artifact validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-first-slice-artifact-validation-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def post_dualscope_first_slice_artifact_validation_analysis(validation_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_artifact_validation_summary.json",
        "dualscope_first_slice_artifact_checklist.json",
        "dualscope_first_slice_contract_compatibility_report.json",
        "dualscope_first_slice_artifact_validation_report.md",
    ]
    missing = [name for name in required if not (validation_dir / name).exists()]
    summary = _load_json(validation_dir / "dualscope_first_slice_artifact_validation_summary.json")
    compatibility = _load_json(validation_dir / "dualscope_first_slice_contract_compatibility_report.json")

    artifacts_ready = summary["all_artifacts_exist"]
    contract_ready = summary["contract_compatibility_ok"]
    stage_rows_ready = summary["stage1_row_count"] == 3 and summary["stage2_row_count"] >= 2 and summary["stage3_row_count"] == 3
    capability_ready = compatibility["capability_markers_ok"]
    budget_ready = compatibility["budget_fields_ok"]
    metrics_ready = compatibility["metrics_placeholder_ok"]

    if not missing and all([artifacts_ready, contract_ready, stage_rows_ready, capability_ready, budget_ready, metrics_ready]):
        final_verdict = "First slice artifact validation validated"
        recommendation = "进入 dualscope-first-slice-report-skeleton"
        basis = [
            "All expected first-slice artifacts exist.",
            "Stage 1 / Stage 2 / Stage 3 public fields, capability markers, budget fields, and metrics placeholders are compatible.",
            "The smoke artifacts are ready to be referenced by a first-slice report skeleton.",
        ]
    elif not missing and artifacts_ready:
        final_verdict = "Partially validated"
        recommendation = "进入 first-slice-artifact-repair"
        basis = ["Artifacts exist, but one or more compatibility checks failed."]
    else:
        final_verdict = "Not validated"
        recommendation = "进入 first-slice-contract-debug"
        basis = ["Expected artifacts are missing or unreadable."]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "artifacts_ready": artifacts_ready,
        "contract_ready": contract_ready,
        "stage_rows_ready": stage_rows_ready,
        "capability_ready": capability_ready,
        "budget_ready": budget_ready,
        "metrics_ready": metrics_ready,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_first_slice_artifact_validation_validated__partially_validated__not_validated",
        "primary_basis": basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": basis,
    }
    write_json(output_dir / "dualscope_first_slice_artifact_validation_analysis_summary.json", analysis_summary)
    write_json(output_dir / "dualscope_first_slice_artifact_validation_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_artifact_validation_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_artifact_validation_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "dualscope_first_slice_artifact_validation_verdict.json").resolve()),
            "recommendation": str(
                (output_dir / "dualscope_first_slice_artifact_validation_next_step_recommendation.json").resolve()
            ),
        },
    }
