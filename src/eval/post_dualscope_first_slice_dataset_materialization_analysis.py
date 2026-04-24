"""Post-analysis for DualScope first-slice dataset materialization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_dataset_materialization_common import SCHEMA_VERSION, write_json


POST_SCHEMA_VERSION = "dualscopellm/post-first-slice-dataset-materialization-analysis/v1"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def post_dualscope_first_slice_dataset_materialization_analysis(materialization_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_dataset_materialization_scope.json",
        "dualscope_first_slice_dataset_source_check.json",
        "dualscope_first_slice_dataset_materialization_manifest.json",
        "dualscope_first_slice_dataset_schema_check.json",
        "dualscope_first_slice_dataset_sliceability_check.json",
        "dualscope_first_slice_dataset_materialization_summary.json",
        "dualscope_first_slice_dataset_materialization_details.jsonl",
        "dualscope_first_slice_dataset_materialization_report.md",
        "dualscope_first_slice_dataset_materialization_verdict.json",
        "dualscope_first_slice_dataset_materialization_next_step_recommendation.json",
    ]
    missing = [name for name in required if not (materialization_dir / name).exists()]
    summary = _load(materialization_dir / "dualscope_first_slice_dataset_materialization_summary.json")
    final_verdict = summary.get("final_verdict", "Not validated") if not missing else "Not validated"
    recommendation = (
        "进入 dualscope-minimal-first-slice-real-run-preflight-rerun"
        if final_verdict == "Dataset materialization validated"
        else "进入 dualscope-first-slice-data-source-intake-package"
        if final_verdict == "Partially validated"
        else "进入 dataset-materialization-tooling-closure"
    )
    analysis = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "source_summary": summary,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_dataset_materialization_validated__partially_validated__not_validated",
    }
    rec = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_first_slice_dataset_materialization_analysis_summary.json", analysis)
    write_json(output_dir / "dualscope_first_slice_dataset_materialization_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_dataset_materialization_next_step_recommendation.json", rec)
    return {"analysis_summary": analysis, "verdict": verdict, "recommendation": rec}
