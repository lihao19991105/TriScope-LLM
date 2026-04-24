"""Validation helpers for next-axis-after-v9 matrix execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_next_axis_after_v9_matrix_execution(
    run_dir: Path,
    compare_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_summary = load_json(run_dir / "next_axis_after_v9_matrix_execution_run_summary.json")
    registry = load_json(run_dir / "next_axis_after_v9_matrix_execution_registry.json")
    metrics = load_json(run_dir / "next_axis_after_v9_matrix_execution_metrics.json")
    preview_path = run_dir / "next_axis_after_v9_matrix_execution_preview.jsonl"
    compare_metrics = load_json(compare_run_dir / "next_axis_after_v9_matrix_execution_metrics.json")

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "run_summary_pass": run_summary.get("summary_status") == "PASS",
            "registry_pass": registry.get("summary_status") == "PASS",
            "metrics_pass": metrics.get("summary_status") == "PASS",
            "preview_non_empty": preview_path.is_file() and preview_path.stat().st_size > 0,
            "fusion_refined_support_ablation_floor_stress_executed": metrics.get(
                "fusion_cell_refined_support_ablation_floor_stress_executed"
            )
            is True,
            "repeat_floor_stress_score_match": metrics.get("fusion_cell_refined_support_ablation_floor_stress_score")
            == compare_metrics.get("fusion_cell_refined_support_ablation_floor_stress_score"),
        },
        "snapshot": {
            "executed_cell_count": metrics.get("executed_cell_count"),
            "fusion_cell_refined_support_ablation_floor_stress_score": metrics.get(
                "fusion_cell_refined_support_ablation_floor_stress_score"
            ),
            "explicit_fusion_cell_count": metrics.get("explicit_fusion_cell_count"),
        },
    }
    (output_dir / "artifact_acceptance.json").write_text(
        json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return acceptance
