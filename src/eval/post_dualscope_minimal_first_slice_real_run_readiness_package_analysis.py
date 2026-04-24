"""Post-analysis for the DualScope minimal first-slice real-run readiness package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-minimal-first-slice-real-run-readiness-package/v1"


def post_dualscope_minimal_first_slice_real_run_readiness_package_analysis(readiness_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_minimal_real_run_command_plan.json",
        "dualscope_minimal_real_run_gpu_config_confirmation.json",
        "dualscope_minimal_real_run_dataset_path_confirmation.json",
        "dualscope_minimal_real_run_model_path_confirmation.json",
        "dualscope_minimal_real_run_scope_confirmation.json",
        "dualscope_minimal_real_run_verification_checklist.json",
        "dualscope_minimal_real_run_readiness_summary.json",
        "dualscope_minimal_real_run_readiness_report.md",
        "dualscope_minimal_real_run_readiness_verdict.json",
        "dualscope_minimal_real_run_readiness_next_step_recommendation.json",
    ]
    missing = [name for name in required if not (readiness_dir / name).exists()]
    if missing:
        final_verdict = "Not validated"
        recommendation = "Resolve minimal real-run readiness artifact gaps"
        source_summary: dict[str, Any] = {}
    else:
        source_summary = json.loads((readiness_dir / "dualscope_minimal_real_run_readiness_summary.json").read_text(encoding="utf-8"))
        final_verdict = source_summary.get("final_verdict", "Not validated")
        recommendation = source_summary.get("recommended_next_step", "Resolve minimal real-run readiness blockers before execution")
    summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "source_summary": source_summary,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
    }
    rec = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_minimal_real_run_readiness_analysis_summary.json", summary)
    write_json(output_dir / "dualscope_minimal_real_run_readiness_verdict.json", verdict)
    write_json(output_dir / "dualscope_minimal_real_run_readiness_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict, "recommendation": rec}

