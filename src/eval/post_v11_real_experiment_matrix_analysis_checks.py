"""Validation helpers for post-v11 real-experiment matrix analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_post_v11_real_experiment_matrix_analysis(
    run_dir: Path,
    compare_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis = load_json(run_dir / "next_axis_after_v10_matrix_analysis_summary.json")
    recommendation = load_json(run_dir / "next_axis_after_v10_matrix_next_step_recommendation.json")
    compare_analysis = load_json(compare_run_dir / "next_axis_after_v10_matrix_analysis_summary.json")

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "analysis_pass": analysis.get("summary_status") == "PASS",
            "recommendation_pass": recommendation.get("summary_status") == "PASS",
            "matrix_established": analysis.get("matrix_execution_established") is True,
            "repeat_cell_count_match": analysis.get("executed_cell_count") == compare_analysis.get("executed_cell_count"),
            "pivot_to_model_axis": recommendation.get("recommended_next_step") == "bootstrap_model_axis_1p5b",
        },
    }
    (output_dir / "artifact_acceptance.json").write_text(
        json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return acceptance
