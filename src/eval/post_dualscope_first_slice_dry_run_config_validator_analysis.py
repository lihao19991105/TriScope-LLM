"""Post-analysis for DualScope dry-run config validator."""

from __future__ import annotations

import json
from pathlib import Path

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/post-first-slice-dry-run-config-validator/v1"


def post_dualscope_first_slice_dry_run_config_validator_analysis(validator_dir: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_dry_run_config.json",
        "dualscope_first_slice_stage_contract_join_map.json",
        "dualscope_first_slice_artifact_path_plan.json",
        "dualscope_first_slice_capability_fallback_config.json",
        "dualscope_first_slice_budget_config.json",
        "dualscope_first_slice_dry_run_validation_summary.json",
        "dualscope_first_slice_dry_run_config_report.md",
        "dualscope_first_slice_dry_run_config_verdict.json",
        "dualscope_first_slice_dry_run_config_next_step_recommendation.json",
    ]
    missing = [name for name in required if not (validator_dir / name).exists()]
    source_summary = json.loads((validator_dir / "dualscope_first_slice_dry_run_validation_summary.json").read_text())
    final = source_summary.get("final_verdict", "Not validated") if not missing else "Not validated"
    summary = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "missing_artifacts": missing, "final_verdict": final}
    verdict = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final}
    rec = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final, "recommended_next_step": "进入 dualscope-first-slice-artifact-validator-hardening"}
    write_json(output_dir / "dualscope_first_slice_dry_run_config_analysis_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_dry_run_config_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_dry_run_config_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict}
