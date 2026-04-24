"""Post-analysis for DualScope artifact validator hardening."""

from __future__ import annotations

import json
from pathlib import Path

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/post-first-slice-artifact-validator/v1"


def post_dualscope_first_slice_artifact_validator_analysis(validator_dir: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_required_artifact_schema.json",
        "dualscope_first_slice_artifact_validator_rules.json",
        "dualscope_first_slice_artifact_validator_summary.json",
        "dualscope_first_slice_artifact_validator_report.md",
        "dualscope_first_slice_artifact_validator_verdict.json",
        "dualscope_first_slice_artifact_validator_next_step_recommendation.json",
    ]
    missing = [name for name in required if not (validator_dir / name).exists()]
    summary = json.loads((validator_dir / "dualscope_first_slice_artifact_validator_summary.json").read_text())
    final = summary.get("final_verdict", "Not validated") if not missing else "Not validated"
    payload = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "missing_artifacts": missing, "final_verdict": final}
    verdict = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final}
    rec = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final, "recommended_next_step": "进入 dualscope-first-slice-readiness-report-package"}
    write_json(output_dir / "dualscope_first_slice_artifact_validator_analysis_summary.json", payload)
    write_json(output_dir / "dualscope_first_slice_artifact_validator_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_artifact_validator_next_step_recommendation.json", rec)
    return {"summary": payload, "verdict": verdict}
