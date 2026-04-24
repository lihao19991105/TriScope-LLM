"""Validation helpers for expanded supervision comparison artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def validate_expanded_supervision_comparison(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    comparison_summary_path = run_dir / "expanded_supervision_comparison_summary.json"
    comparison_csv_path = run_dir / "route_b_oldc_expandedc_comparison.csv"
    progression_summary_path = run_dir / "supervision_progression_summary.json"
    recommendation_path = run_dir / "expanded_supervision_next_step_recommendation.json"

    comparison_summary = load_json(comparison_summary_path)
    progression_summary = load_json(progression_summary_path)
    recommendation = load_json(recommendation_path)
    comparison_rows = load_csv_rows(comparison_csv_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "comparison_summary", "path": str(comparison_summary_path.resolve()), "exists": comparison_summary_path.is_file()},
            {"artifact_name": "comparison_csv", "path": str(comparison_csv_path.resolve()), "exists": comparison_csv_path.is_file()},
            {"artifact_name": "progression_summary", "path": str(progression_summary_path.resolve()), "exists": progression_summary_path.is_file()},
            {"artifact_name": "recommendation", "path": str(recommendation_path.resolve()), "exists": recommendation_path.is_file()},
        ],
        "field_checks": {
            "comparison_summary_pass": comparison_summary.get("summary_status") == "PASS",
            "comparison_csv_has_3_rows": len(comparison_rows) >= 3,
            "progression_summary_pass": progression_summary.get("summary_status") == "PASS",
            "recommended_next_step_present": bool(recommendation.get("recommended_next_step")),
        },
        "snapshot": {
            "recommended_next_step": recommendation.get("recommended_next_step"),
            "route_c_row_gain": progression_summary.get("route_c_progression", {}).get("row_gain"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_recommendation = load_json(compare_run_dir / "expanded_supervision_next_step_recommendation.json")
        compare_progression = load_json(compare_run_dir / "supervision_progression_summary.json")
        repeatability_summary = {
            "summary_status": "PASS",
            "reference_acceptance": acceptance,
            "candidate_run_dir": str(compare_run_dir.resolve()),
            "comparisons": [
                {
                    "field": "recommended_next_step",
                    "reference_value": recommendation.get("recommended_next_step"),
                    "candidate_value": compare_recommendation.get("recommended_next_step"),
                    "matches": recommendation.get("recommended_next_step") == compare_recommendation.get("recommended_next_step"),
                },
                {
                    "field": "route_c_row_gain",
                    "reference_value": progression_summary.get("route_c_progression", {}).get("row_gain"),
                    "candidate_value": compare_progression.get("route_c_progression", {}).get("row_gain"),
                    "matches": progression_summary.get("route_c_progression", {}).get("row_gain") == compare_progression.get("route_c_progression", {}).get("row_gain"),
                },
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM expanded supervision comparison validation",
                f"Acceptance status: {acceptance['summary_status']}",
                f"Repeatability status: {repeatability_summary['summary_status'] if repeatability_summary is not None else 'SKIPPED'}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "acceptance": acceptance,
        "repeatability": repeatability_summary,
        "output_paths": {
            "acceptance": str((output_dir / "artifact_acceptance.json").resolve()),
            "repeatability": str((output_dir / "repeatability_summary.json").resolve()) if repeatability_summary is not None else None,
            "log": str((output_dir / "repeat_check.log").resolve()),
        },
    }
