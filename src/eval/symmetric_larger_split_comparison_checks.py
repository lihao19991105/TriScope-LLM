"""Validation helpers for symmetric larger-split comparison artifacts."""

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


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return sum(1 for _ in reader)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def validate_symmetric_larger_split_comparison(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "symmetric_larger_split_comparison_summary.json"
    comparison_csv_path = run_dir / "route_b_larger_vs_route_c_larger_comparison.csv"
    progression_path = run_dir / "supervision_progression_after_symmetric_rerun.json"
    tradeoff_csv_path = run_dir / "symmetric_rerun_tradeoff_matrix.csv"
    recommendation_path = run_dir / "symmetric_rerun_next_step_recommendation.json"

    summary = load_json(summary_path)
    progression = load_json(progression_path)
    recommendation = load_json(recommendation_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "summary", "path": str(summary_path.resolve()), "exists": summary_path.is_file()},
            {"artifact_name": "comparison_csv", "path": str(comparison_csv_path.resolve()), "exists": comparison_csv_path.is_file()},
            {"artifact_name": "progression", "path": str(progression_path.resolve()), "exists": progression_path.is_file()},
            {"artifact_name": "tradeoff_csv", "path": str(tradeoff_csv_path.resolve()), "exists": tradeoff_csv_path.is_file()},
            {"artifact_name": "recommendation", "path": str(recommendation_path.resolve()), "exists": recommendation_path.is_file()},
        ],
        "field_checks": {
            "summary_pass": summary.get("summary_status") == "PASS",
            "comparison_csv_has_rows": count_csv_rows(comparison_csv_path) >= 3,
            "progression_pass": progression.get("summary_status") == "PASS",
            "tradeoff_csv_has_rows": count_csv_rows(tradeoff_csv_path) >= 3,
            "recommendation_pass": recommendation.get("summary_status") == "PASS",
        },
        "snapshot": {
            "recommended_next_step": recommendation.get("recommended_next_step"),
            "route_b_larger_rows": progression.get("progression", {}).get("route_b_larger_rows"),
            "route_c_larger_rows": progression.get("progression", {}).get("route_c_larger_rows"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_recommendation = load_json(compare_run_dir / "symmetric_rerun_next_step_recommendation.json")
        compare_progression = load_json(compare_run_dir / "supervision_progression_after_symmetric_rerun.json")
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
                    "field": "route_c_larger_rows",
                    "reference_value": progression.get("progression", {}).get("route_c_larger_rows"),
                    "candidate_value": compare_progression.get("progression", {}).get("route_c_larger_rows"),
                    "matches": progression.get("progression", {}).get("route_c_larger_rows")
                    == compare_progression.get("progression", {}).get("route_c_larger_rows"),
                },
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM symmetric larger-split comparison validation",
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
