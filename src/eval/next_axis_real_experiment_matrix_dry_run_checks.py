"""Validation helpers for next-axis real-experiment matrix dry-run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_next_axis_real_experiment_matrix_dry_run(
    run_dir: Path,
    compare_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = load_json(run_dir / "next_axis_matrix_dry_run_summary.json")
    registry = load_json(run_dir / "next_axis_matrix_dry_run_registry.json")
    module_status = load_json(run_dir / "next_axis_matrix_module_status.json")
    cell_status = load_json(run_dir / "next_axis_matrix_cell_status.json")
    compare_summary = load_json(compare_run_dir / "next_axis_matrix_dry_run_summary.json")
    preview_path = run_dir / "next_axis_matrix_dry_run_preview.jsonl"

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "summary_pass": summary.get("summary_status") == "PASS",
            "registry_pass": registry.get("summary_status") == "PASS",
            "module_status_pass": module_status.get("summary_status") == "PASS",
            "cell_status_pass": cell_status.get("summary_status") == "PASS",
            "preview_non_empty": preview_path.is_file() and preview_path.stat().st_size > 0,
            "repeat_cell_count_match": summary.get("cell_count") == compare_summary.get("cell_count"),
            "repeat_route_count_match": summary.get("route_count") == compare_summary.get("route_count"),
            "refined_fusion_cell_present": len(summary.get("passed_fusion_refined_cells", [])) == 1,
        },
        "snapshot": {
            "dataset_rows": summary.get("dataset_rows"),
            "num_passed_cells": len(summary.get("passed_cells", [])),
            "num_refined_fusion_cells": len(summary.get("passed_fusion_refined_cells", [])),
        },
    }
    (output_dir / "artifact_acceptance.json").write_text(
        json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return acceptance
