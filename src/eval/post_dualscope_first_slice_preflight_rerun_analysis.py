"""Post-analysis wrapper for DualScope first-slice preflight rerun."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_preflight_common import write_json
from src.eval.post_dualscope_minimal_first_slice_real_run_preflight_analysis import (
    post_dualscope_minimal_first_slice_real_run_preflight_analysis,
)


POST_SCHEMA_VERSION = "dualscopellm/post-first-slice-preflight-rerun/v1"


def post_dualscope_first_slice_preflight_rerun_analysis(preflight_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Analyze rerun artifacts and normalize verdict names for this phase."""

    result = post_dualscope_minimal_first_slice_real_run_preflight_analysis(
        preflight_dir=preflight_dir,
        output_dir=output_dir,
    )
    source_verdict = result["verdict"]["final_verdict"]
    if source_verdict == "Minimal first slice real run preflight validated":
        final_verdict = "First slice preflight rerun validated"
        recommendation = "dualscope-minimal-first-slice-real-run-readiness-package"
    elif source_verdict == "Partially validated":
        final_verdict = "Partially validated"
        recommendation = "first-slice-preflight-rerun-repair"
    else:
        final_verdict = "Not validated"
        recommendation = "first-slice-real-run-blocker-closure"

    summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "source_preflight_verdict": source_verdict,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_first_slice_preflight_rerun_validated__partially_validated__not_validated",
    }
    rec = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_first_slice_preflight_rerun_analysis_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_preflight_rerun_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_preflight_rerun_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict, "recommendation": rec}

