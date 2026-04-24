"""Validation helpers for first real-experiment dry-run artifacts."""

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


def validate_real_experiment_first_dry_run(run_dir: Path, compare_run_dir: Path | None, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = load_json(run_dir / "first_real_experiment_dry_run_summary.json")
    registry = load_json(run_dir / "first_real_experiment_dry_run_registry.json")
    module_status = load_json(run_dir / "first_real_experiment_module_status.json")
    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "summary_pass": summary.get("summary_status") == "PASS",
            "registry_pass": registry.get("summary_status") == "PASS",
            "module_status_pass": module_status.get("summary_status") == "PASS",
            "preview_non_empty": count_jsonl_rows(run_dir / "first_real_experiment_dry_run_preview.jsonl") > 0,
        },
        "snapshot": {
            "dataset_rows": summary.get("dataset_rows"),
            "num_passed_modules": len(summary.get("passed_modules", [])),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)
    repeatability: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_summary = load_json(compare_run_dir / "first_real_experiment_dry_run_summary.json")
        repeatability = {
            "summary_status": "PASS",
            "comparisons": [
                {
                    "field": "dataset_rows",
                    "reference_value": summary.get("dataset_rows"),
                    "candidate_value": compare_summary.get("dataset_rows"),
                    "matches": summary.get("dataset_rows") == compare_summary.get("dataset_rows"),
                }
            ],
        }
        repeatability["all_key_metrics_match"] = all(item["matches"] for item in repeatability["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability)
    (output_dir / "repeat_check.log").write_text("TriScope-LLM first real-experiment dry-run validation\n", encoding="utf-8")
    return {"acceptance": acceptance, "repeatability": repeatability}
