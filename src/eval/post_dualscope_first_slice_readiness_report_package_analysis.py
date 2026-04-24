"""Post-analysis for DualScope first-slice readiness package."""

from __future__ import annotations

import json
from pathlib import Path

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/post-first-slice-readiness-report-package/v1"


def post_dualscope_first_slice_readiness_report_package_analysis(readiness_dir: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_readiness_summary.json",
        "dualscope_first_slice_completed_components.json",
        "dualscope_first_slice_blockers.json",
        "dualscope_first_slice_user_action_items.md",
        "dualscope_first_slice_next_command_plan.json",
        "dualscope_first_slice_readiness_report.md",
        "dualscope_first_slice_readiness_verdict.json",
        "dualscope_first_slice_readiness_next_step_recommendation.json",
    ]
    missing = [name for name in required if not (readiness_dir / name).exists()]
    source_summary = json.loads((readiness_dir / "dualscope_first_slice_readiness_summary.json").read_text())
    final = source_summary.get("final_verdict", "Not validated") if not missing else "Not validated"
    source_rec = json.loads((readiness_dir / "dualscope_first_slice_readiness_next_step_recommendation.json").read_text())
    summary = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "missing_artifacts": missing, "final_verdict": final}
    verdict = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final}
    rec = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final, "recommended_next_step": source_rec.get("recommended_next_step")}
    write_json(output_dir / "dualscope_first_slice_readiness_analysis_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_readiness_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_readiness_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict, "recommendation": rec}
