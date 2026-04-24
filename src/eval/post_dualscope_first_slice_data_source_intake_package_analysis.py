"""Post-analysis for DualScope data-source intake package."""

from __future__ import annotations

import json
from pathlib import Path

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/post-first-slice-data-source-intake-package/v1"


def post_dualscope_first_slice_data_source_intake_package_analysis(intake_dir: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_data_source_requirements.json",
        "dualscope_first_slice_accepted_source_formats.json",
        "dualscope_first_slice_import_command_examples.json",
        "dualscope_first_slice_schema_expectation.json",
        "dualscope_first_slice_user_action_items.md",
        "dualscope_first_slice_data_source_intake_summary.json",
        "dualscope_first_slice_data_source_intake_report.md",
    ]
    missing = [name for name in required if not (intake_dir / name).exists()]
    final = "Data source intake package validated" if not missing else "Not validated"
    summary = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "missing_artifacts": missing, "final_verdict": final}
    verdict = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final}
    rec = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final, "recommended_next_step": "进入 dualscope-first-slice-dry-run-config-and-contract-validator" if not missing else "进入 data-source-intake-package-closure"}
    write_json(output_dir / "dualscope_first_slice_data_source_intake_analysis_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_data_source_intake_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_data_source_intake_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict}
