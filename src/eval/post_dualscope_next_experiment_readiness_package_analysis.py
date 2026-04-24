"""Post-analysis for DualScope next experiment readiness package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import SCHEMA_VERSION, markdown, read_json, write_json


def build_post_next_experiment_readiness_analysis(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = read_json(repo_root / "outputs/dualscope_next_experiment_readiness_package/default/dualscope_next_experiment_readiness_summary.json")
    verdict = summary.get("final_verdict", "Not validated")
    recommendation = summary.get("recommended_next_step", "dualscope-next-experiment-readiness-blocker-closure")
    analysis = {
        "summary_status": summary.get("summary_status", "FAIL"),
        "schema_version": SCHEMA_VERSION,
        "selected_next_action": summary.get("selected_next_action"),
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_next_experiment_readiness_analysis_summary.json", analysis)
    write_json(output_dir / "dualscope_next_experiment_readiness_verdict.json", {"summary_status": analysis["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_next_experiment_readiness_next_step_recommendation.json", {"summary_status": analysis["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    markdown(output_dir / "dualscope_next_experiment_readiness_analysis_report.md", "Next Experiment Readiness Analysis", [
        f"- Final verdict: `{verdict}`",
        f"- Recommendation: {recommendation}",
    ])
    return analysis
