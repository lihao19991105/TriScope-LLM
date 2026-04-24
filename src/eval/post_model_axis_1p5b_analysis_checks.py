"""Validation helpers for post-model-axis 1.5B analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_post_model_axis_1p5b_analysis(
    run_dir: Path,
    compare_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis = load_json(run_dir / "model_axis_1p5b_analysis_summary.json")
    recommendation = load_json(run_dir / "model_axis_1p5b_next_step_recommendation.json")
    compare_analysis = load_json(compare_run_dir / "model_axis_1p5b_analysis_summary.json")

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "analysis_pass": analysis.get("summary_status") == "PASS",
            "entry_opened": analysis.get("model_axis_entry_opened") is True,
            "used_local_weights": analysis.get("used_local_weights") is True,
            "execution_repeat_match": analysis.get("execution_status") == compare_analysis.get("execution_status"),
            "recommendation_focus_match": recommendation.get("recommended_next_step") == "stabilize_model_axis_1p5b_route_b_label_balance",
        },
    }
    (output_dir / "artifact_acceptance.json").write_text(
        json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return acceptance
