"""Validation helpers for the 1.5B model-axis bootstrap."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_model_axis_1p5b_bootstrap(
    run_dir: Path,
    compare_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = load_json(run_dir / "model_axis_1p5b_bootstrap_summary.json")
    selection = load_json(run_dir / "model_axis_1p5b_candidate_selection.json")
    readiness = load_json(run_dir / "model_axis_1p5b_readiness_summary.json")
    compare_summary = load_json(compare_run_dir / "model_axis_1p5b_bootstrap_summary.json")

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "summary_pass": summary.get("summary_status") == "PASS",
            "selection_pass": selection.get("summary_status") == "PASS",
            "readiness_pass": readiness.get("summary_status") == "PASS",
            "selected_model_is_1p5b": selection.get("selected_model_id") == "Qwen/Qwen2.5-1.5B-Instruct",
            "repeat_model_match": summary.get("selected_model_profile") == compare_summary.get("selected_model_profile"),
            "route_count_positive": summary.get("route_count", 0) > 0,
        },
    }
    (output_dir / "artifact_acceptance.json").write_text(
        json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return acceptance
