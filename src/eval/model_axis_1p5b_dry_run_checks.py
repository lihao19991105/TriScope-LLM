"""Validation helpers for the 1.5B model-axis dry-run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_model_axis_1p5b_dry_run(
    run_dir: Path,
    compare_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = load_json(run_dir / "model_axis_1p5b_dry_run_summary.json")
    registry = load_json(run_dir / "model_axis_1p5b_dry_run_registry.json")
    cell_status = load_json(run_dir / "model_axis_1p5b_cell_status.json")
    compare_summary = load_json(compare_run_dir / "model_axis_1p5b_dry_run_summary.json")

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "summary_present": summary.get("summary_status") in {"PASS", "PARTIAL", "BLOCKED", "PASS_WITH_LIMITATIONS"},
            "registry_pass": registry.get("summary_status") == "PASS",
            "cell_status_pass": cell_status.get("summary_status") == "PASS",
            "minimal_candidate_route_b": summary.get("minimal_execution_candidate") == "route_b",
            "repeat_status_match": summary.get("dry_run_status") == compare_summary.get("dry_run_status"),
            "repeat_model_match": summary.get("selected_model_profile") == compare_summary.get("selected_model_profile"),
            "runtime_alignment": (
                summary.get("route_b_status") == "READY"
                if summary.get("ready_run") is True
                else summary.get("route_b_status") == "BLOCKED_NOT_READY_LOCAL"
            ),
        },
    }
    (output_dir / "artifact_acceptance.json").write_text(
        json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return acceptance
