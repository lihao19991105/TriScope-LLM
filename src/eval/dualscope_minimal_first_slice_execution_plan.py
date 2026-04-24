"""Build the DualScope minimal first-slice execution plan artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_common import (
    SCHEMA_VERSION,
    TASK_NAME,
    build_details,
    build_expected_artifacts,
    build_failure_fallback_plan,
    build_first_slice_definition,
    build_report,
    build_resource_contract,
    build_run_contract,
    build_summary,
    build_validation_criteria,
    write_json,
    write_jsonl,
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def build_dualscope_minimal_first_slice_execution_plan(matrix_freeze_dir: Path, output_dir: Path, seed: int) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix_first_slice = _load_json(matrix_freeze_dir / "dualscope_minimal_first_slice.json")

    first_slice = build_first_slice_definition(matrix_first_slice)
    run_contract = build_run_contract(first_slice)
    expected_artifacts = build_expected_artifacts(first_slice)
    validation = build_validation_criteria()
    resource = build_resource_contract(first_slice)
    fallback = build_failure_fallback_plan()
    details = build_details(first_slice, run_contract, expected_artifacts, validation, resource)
    summary = build_summary(first_slice, expected_artifacts, details)
    report = build_report(summary, first_slice)

    write_json(output_dir / "dualscope_first_slice_definition.json", first_slice)
    write_json(output_dir / "dualscope_first_slice_run_contract.json", run_contract)
    write_json(output_dir / "dualscope_first_slice_expected_artifacts.json", expected_artifacts)
    write_json(output_dir / "dualscope_first_slice_validation_criteria.json", validation)
    write_json(output_dir / "dualscope_first_slice_resource_contract.json", resource)
    write_json(output_dir / "dualscope_first_slice_failure_fallback_plan.json", fallback)
    write_json(output_dir / "dualscope_first_slice_summary.json", summary)
    write_jsonl(output_dir / "dualscope_first_slice_details.jsonl", details)
    (output_dir / "dualscope_first_slice_report.md").write_text(report, encoding="utf-8")
    write_json(
        output_dir / "dualscope_first_slice_execution_plan_manifest.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "task_name": TASK_NAME,
            "seed": seed,
            "matrix_freeze_dir": str(matrix_freeze_dir.resolve()),
        },
    )
    return {
        "summary": summary,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_summary.json").resolve()),
            "report": str((output_dir / "dualscope_first_slice_report.md").resolve()),
        },
    }
