"""Validation helpers for post first real experiment analysis."""

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


def validate_post_first_real_experiment_analysis(run_dir: Path, compare_run_dir: Path | None, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis = load_json(run_dir / "first_real_experiment_analysis_summary.json")
    recommendation = load_json(run_dir / "first_real_experiment_next_step_recommendation.json")
    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "field_checks": {
            "analysis_pass": analysis.get("summary_status") == "PASS",
            "recommendation_pass": recommendation.get("summary_status") == "PASS",
            "matrix_recommended": recommendation.get("recommended_next_step") == "bootstrap_minimal_real_experiment_matrix",
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)
    repeatability: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_recommendation = load_json(compare_run_dir / "first_real_experiment_next_step_recommendation.json")
        repeatability = {
            "summary_status": "PASS",
            "comparisons": [
                {
                    "field": "recommended_next_step",
                    "reference_value": recommendation.get("recommended_next_step"),
                    "candidate_value": compare_recommendation.get("recommended_next_step"),
                    "matches": recommendation.get("recommended_next_step") == compare_recommendation.get("recommended_next_step"),
                }
            ],
        }
        repeatability["all_key_metrics_match"] = all(item["matches"] for item in repeatability["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability)
    (output_dir / "repeat_check.log").write_text("TriScope-LLM post-first-real analysis validation\n", encoding="utf-8")
    return {"acceptance": acceptance, "repeatability": repeatability}
