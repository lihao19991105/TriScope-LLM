"""Post-analysis for DualScope first-slice real-run compression."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import SCHEMA_VERSION, read_json, write_json


def post_dualscope_minimal_first_slice_real_run_compression_analysis(compression_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_real_run_compression_scope.json",
        "dualscope_first_slice_previous_real_run_status.json",
        "dualscope_first_slice_model_execution_gap.json",
        "dualscope_first_slice_logprob_capability_probe.json",
        "dualscope_first_slice_label_metric_readiness.json",
        "dualscope_minimal_first_slice_real_run_compression_summary.json",
        "dualscope_minimal_first_slice_real_run_compression_report.md",
    ]
    missing = [name for name in required if not (compression_dir / name).exists()]
    summary = read_json(compression_dir / "dualscope_minimal_first_slice_real_run_compression_summary.json") if not missing else {}
    verdict = summary.get("final_verdict", "Not validated") if not missing else "Not validated"
    rec = summary.get("recommended_next_step", "dualscope-minimal-first-slice-real-run-blocker-closure")
    payload = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "missing_artifacts": missing, "final_verdict": verdict, "recommended_next_step": rec}
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_compression_analysis_summary.json", payload)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_compression_verdict.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_compression_next_step_recommendation.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": rec})
    return {"summary": payload, "verdict": verdict, "recommendation": rec}

