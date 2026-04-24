"""Post-analysis for readiness after materialization."""

from __future__ import annotations

import json
from pathlib import Path

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/post-first-slice-readiness-after-materialization/v1"


def post_dualscope_first_slice_readiness_after_materialization_analysis(readiness_dir: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_readiness_after_materialization_summary.json",
        "dualscope_first_slice_completed_requirements.json",
        "dualscope_first_slice_remaining_blockers.json",
        "dualscope_first_slice_next_command_plan.json",
        "dualscope_first_slice_readiness_after_materialization_report.md",
        "dualscope_first_slice_readiness_after_materialization_verdict.json",
        "dualscope_first_slice_readiness_after_materialization_next_step_recommendation.json",
    ]
    missing = [name for name in required if not (readiness_dir / name).exists()]
    source_verdict = json.loads((readiness_dir / "dualscope_first_slice_readiness_after_materialization_verdict.json").read_text())
    source_rec = json.loads((readiness_dir / "dualscope_first_slice_readiness_after_materialization_next_step_recommendation.json").read_text())
    final = source_verdict.get("final_verdict", "Not ready") if not missing else "Not ready"
    summary = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "missing_artifacts": missing, "final_verdict": final}
    verdict = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final}
    rec = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final, "recommended_next_step": source_rec.get("recommended_next_step")}
    write_json(output_dir / "dualscope_first_slice_readiness_after_materialization_analysis_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_readiness_after_materialization_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_readiness_after_materialization_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict, "recommendation": rec}
