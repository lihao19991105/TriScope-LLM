"""Post-analysis for DualScope minimal first-slice real run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_real_run_entrypoint_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-minimal-first-slice-real-run/v1"


def post_dualscope_minimal_first_slice_real_run_analysis(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_minimal_first_slice_real_run_scope.json",
        "dualscope_minimal_first_slice_real_run_command_plan.json",
        "dualscope_minimal_first_slice_real_run_stage_status.json",
        "dualscope_minimal_first_slice_real_run_required_artifacts_check.json",
        "dualscope_minimal_first_slice_real_run_contract_compatibility_check.json",
        "dualscope_minimal_first_slice_real_run_summary.json",
        "dualscope_minimal_first_slice_real_run_details.jsonl",
        "dualscope_minimal_first_slice_real_run_report.md",
        "dualscope_minimal_first_slice_real_run_verdict.json",
        "dualscope_minimal_first_slice_real_run_next_step_recommendation.json",
    ]
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        final_verdict = "Not validated"
        recommendation = "dualscope-minimal-first-slice-real-run-blocker-closure"
        source_summary: dict[str, Any] = {}
    else:
        source_summary = json.loads((run_dir / "dualscope_minimal_first_slice_real_run_summary.json").read_text(encoding="utf-8"))
        final_verdict = source_summary.get("final_verdict", "Not validated")
        recommendation = source_summary.get("recommended_next_step", "dualscope-minimal-first-slice-real-run-blocker-closure")
    summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "source_summary": source_summary,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    verdict = {"summary_status": "PASS", "schema_version": POST_SCHEMA_VERSION, "final_verdict": final_verdict}
    rec = {"summary_status": "PASS", "schema_version": POST_SCHEMA_VERSION, "final_verdict": final_verdict, "recommended_next_step": recommendation}
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_analysis_summary.json", summary)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_verdict.json", verdict)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict, "recommendation": rec}

