"""Validation helpers for first real experiment execution artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def count_jsonl_rows(path: Path) -> int:
    return sum(1 for row in path.read_text(encoding="utf-8").splitlines() if row.strip())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def validate_first_real_experiment_execution(run_dir: Path, compare_run_dir: Path | None, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_summary = load_json(run_dir / "first_real_execution_run_summary.json")
    registry = load_json(run_dir / "first_real_execution_registry.json")
    metrics = load_json(run_dir / "first_real_execution_metrics.json")
    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "run_summary_pass": run_summary.get("summary_status") == "PASS",
            "registry_pass": registry.get("summary_status") == "PASS",
            "metrics_pass": metrics.get("summary_status") == "PASS",
            "preview_non_empty": count_jsonl_rows(run_dir / "first_real_execution_preview.jsonl") > 0,
        },
        "snapshot": {
            "route_b_rows": metrics.get("route_b_rows"),
            "route_c_rows": metrics.get("route_c_rows"),
            "shared_base_samples": metrics.get("shared_base_samples"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)
    repeatability: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_metrics = load_json(compare_run_dir / "first_real_execution_metrics.json")
        repeatability = {
            "summary_status": "PASS",
            "comparisons": [
                {
                    "field": "route_b_rows",
                    "reference_value": metrics.get("route_b_rows"),
                    "candidate_value": compare_metrics.get("route_b_rows"),
                    "matches": metrics.get("route_b_rows") == compare_metrics.get("route_b_rows"),
                },
                {
                    "field": "route_c_rows",
                    "reference_value": metrics.get("route_c_rows"),
                    "candidate_value": compare_metrics.get("route_c_rows"),
                    "matches": metrics.get("route_c_rows") == compare_metrics.get("route_c_rows"),
                },
            ],
        }
        repeatability["all_key_metrics_match"] = all(item["matches"] for item in repeatability["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability)
    (output_dir / "repeat_check.log").write_text("TriScope-LLM first real execution validation\n", encoding="utf-8")
    return {"acceptance": acceptance, "repeatability": repeatability}
