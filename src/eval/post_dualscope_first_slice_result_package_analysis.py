"""Post-analysis for DualScope first-slice result package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import SCHEMA_VERSION, markdown, read_json, write_json


def build_post_result_package_analysis(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = read_json(repo_root / "outputs/dualscope_first_slice_result_package/default/dualscope_first_slice_result_package_summary.json")
    verdict = summary.get("final_verdict", "Not validated")
    recommendation = summary.get("recommended_next_step", "dualscope-first-slice-result-package-blocker-closure")
    analysis = {
        "summary_status": summary.get("summary_status", "FAIL"),
        "schema_version": SCHEMA_VERSION,
        "can_report_count": len(summary.get("can_report", [])),
        "cannot_report_count": len(summary.get("cannot_report", [])),
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_first_slice_result_package_analysis_summary.json", analysis)
    write_json(output_dir / "dualscope_first_slice_result_package_verdict.json", {"summary_status": analysis["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_first_slice_result_package_next_step_recommendation.json", {"summary_status": analysis["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    markdown(output_dir / "dualscope_first_slice_result_package_analysis_report.md", "Result Package Analysis", [
        f"- Final verdict: `{verdict}`",
        f"- Recommendation: {recommendation}",
    ])
    return analysis
