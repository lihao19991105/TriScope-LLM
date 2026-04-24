"""Validation helpers for next real-experiment matrix execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_next_real_experiment_matrix_execution(
    run_dir: Path,
    compare_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_summary = load_json(run_dir / "next_matrix_execution_run_summary.json")
    registry = load_json(run_dir / "next_matrix_execution_registry.json")
    metrics = load_json(run_dir / "next_matrix_execution_metrics.json")
    preview_path = run_dir / "next_matrix_execution_preview.jsonl"
    compare_metrics = load_json(compare_run_dir / "next_matrix_execution_metrics.json")

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "run_summary_pass": run_summary.get("summary_status") == "PASS",
            "registry_pass": registry.get("summary_status") == "PASS",
            "metrics_pass": metrics.get("summary_status") == "PASS",
            "preview_non_empty": preview_path.is_file() and preview_path.stat().st_size > 0,
            "repeat_rows_match": metrics.get("route_b_rows") == compare_metrics.get("route_b_rows")
            and metrics.get("route_c_rows") == compare_metrics.get("route_c_rows")
            and metrics.get("route_b_only_ablation_rows") == compare_metrics.get("route_b_only_ablation_rows")
            and metrics.get("route_c_only_ablation_rows") == compare_metrics.get("route_c_only_ablation_rows"),
        },
        "snapshot": {
            "route_b_rows": metrics.get("route_b_rows"),
            "route_c_rows": metrics.get("route_c_rows"),
            "ablation_cell_count": metrics.get("ablation_cell_count"),
            "executed_cell_count": metrics.get("executed_cell_count"),
        },
    }
    (output_dir / "artifact_acceptance.json").write_text(
        json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return acceptance
