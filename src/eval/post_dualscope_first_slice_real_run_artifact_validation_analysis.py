"""Post-analysis for first-slice real-run artifact validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import SCHEMA_VERSION, markdown, read_json, write_json


def build_post_real_run_artifact_validation_analysis(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = read_json(repo_root / "outputs/dualscope_first_slice_real_run_artifact_validation/default/dualscope_first_slice_real_run_artifact_validation_summary.json")
    verdict = summary.get("final_verdict", "Not validated")
    recommendation = summary.get("recommended_next_step", "dualscope-first-slice-real-run-artifact-validation-blocker-closure")
    analysis = {
        "summary_status": summary.get("summary_status", "FAIL"),
        "schema_version": SCHEMA_VERSION,
        "artifact_chain_passed": summary.get("artifact_chain_passed"),
        "stage_entrypoints_model_integrated": summary.get("stage_entrypoints_model_integrated"),
        "performance_metrics_ready": summary.get("performance_metrics_ready"),
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_analysis_summary.json", analysis)
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_verdict.json", {"summary_status": analysis["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_next_step_recommendation.json", {"summary_status": analysis["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    markdown(output_dir / "dualscope_first_slice_real_run_artifact_validation_analysis_report.md", "Artifact Validation Analysis", [
        f"- Final verdict: `{verdict}`",
        f"- Recommendation: {recommendation}",
    ])
    return analysis
