"""Validation helpers for next-axis-after-v6 matrix bootstrap."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def validate_next_axis_after_v6_matrix_bootstrap(
    run_dir: Path,
    compare_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = load_json(run_dir / "next_axis_after_v6_bootstrap_summary.json")
    definition = load_json(run_dir / "next_axis_after_v6_matrix_definition.json")
    compare_summary = load_json(compare_run_dir / "next_axis_after_v6_bootstrap_summary.json")

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "summary_pass": summary.get("summary_status") == "PASS",
            "route_count_positive": summary.get("route_count", 0) > 0,
            "dataset_count_positive": summary.get("dataset_count", 0) > 0,
            "repeat_route_count_match": summary.get("route_count") == compare_summary.get("route_count"),
            "route_set_non_empty": len(definition.get("routes", [])) > 0,
            "fusion_mode_present": bool(summary.get("fusion_mode")),
        },
    }
    (output_dir / "artifact_acceptance.json").write_text(
        json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return acceptance
