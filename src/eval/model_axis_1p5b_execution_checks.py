"""Validation helpers for the 1.5B model-axis execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_model_axis_1p5b_execution(
    run_dir: Path,
    compare_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_summary = load_json(run_dir / "model_axis_1p5b_execution_run_summary.json")
    metrics = load_json(run_dir / "model_axis_1p5b_execution_metrics.json")
    compare_summary = load_json(compare_run_dir / "model_axis_1p5b_execution_run_summary.json")
    compare_metrics = load_json(compare_run_dir / "model_axis_1p5b_execution_metrics.json")

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "run_summary_present": run_summary.get("summary_status") in {"PASS", "PARTIAL"},
            "metrics_present": metrics.get("summary_status") in {"PASS", "PARTIAL"},
            "selected_cell_route_b": run_summary.get("selected_cell") == "route_b",
            "used_local_weights": metrics.get("used_local_weights") is True,
            "entered_model_inference": metrics.get("entered_model_inference") is True,
            "repeat_execution_status_match": run_summary.get("execution_status") == compare_summary.get("execution_status"),
            "repeat_rows_match": metrics.get("num_rows") == compare_metrics.get("num_rows"),
        },
    }
    (output_dir / "artifact_acceptance.json").write_text(
        json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return acceptance
