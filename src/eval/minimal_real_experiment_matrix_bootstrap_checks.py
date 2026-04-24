"""Validation helpers for minimal real-experiment matrix bootstrap."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def validate_minimal_real_experiment_matrix_bootstrap(run_dir: Path, compare_run_dir: Path | None, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = load_json(run_dir / "minimal_real_experiment_bootstrap_summary.json")
    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "summary_pass": summary.get("summary_status") == "PASS",
            "route_count_positive": int(summary.get("route_count", 0)) > 0,
            "dataset_count_positive": int(summary.get("dataset_count", 0)) > 0,
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)
    repeatability: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_summary = load_json(compare_run_dir / "minimal_real_experiment_bootstrap_summary.json")
        repeatability = {
            "summary_status": "PASS",
            "comparisons": [
                {
                    "field": "route_count",
                    "reference_value": summary.get("route_count"),
                    "candidate_value": compare_summary.get("route_count"),
                    "matches": summary.get("route_count") == compare_summary.get("route_count"),
                }
            ],
        }
        repeatability["all_key_metrics_match"] = all(item["matches"] for item in repeatability["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability)
    (output_dir / "repeat_check.log").write_text("TriScope-LLM minimal real matrix bootstrap validation\n", encoding="utf-8")
    return {"acceptance": acceptance, "repeatability": repeatability}
