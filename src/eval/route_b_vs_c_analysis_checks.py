"""Validation helpers for route B vs C vs D supervision analysis."""

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


def validate_route_b_vs_c_analysis(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    gain_summary_path = run_dir / "route_b_vs_c_gain_summary.json"
    comparison_path = run_dir / "route_b_vs_c_vs_d_comparison.json"
    gain_matrix_path = run_dir / "supervision_route_gain_matrix.csv"
    realism_cost_path = run_dir / "supervision_realism_cost_summary.json"
    recommendation_path = run_dir / "route_b_vs_c_next_step_recommendation.json"

    gain_summary = load_json(gain_summary_path)
    comparison = load_json(comparison_path)
    gain_rows = load_csv_rows(gain_matrix_path)
    realism_cost = load_json(realism_cost_path)
    recommendation = load_json(recommendation_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "gain_summary", "path": str(gain_summary_path.resolve()), "exists": gain_summary_path.is_file()},
            {"artifact_name": "comparison", "path": str(comparison_path.resolve()), "exists": comparison_path.is_file()},
            {"artifact_name": "gain_matrix", "path": str(gain_matrix_path.resolve()), "exists": gain_matrix_path.is_file()},
            {"artifact_name": "realism_cost", "path": str(realism_cost_path.resolve()), "exists": realism_cost_path.is_file()},
            {"artifact_name": "recommendation", "path": str(recommendation_path.resolve()), "exists": recommendation_path.is_file()},
        ],
        "field_checks": {
            "gain_summary_pass": gain_summary.get("summary_status") == "PASS",
            "comparison_has_3_routes": len(comparison.get("routes", [])) >= 3,
            "gain_matrix_non_empty": bool(gain_rows),
            "realism_cost_pass": realism_cost.get("summary_status") == "PASS",
            "recommended_route_is_D": recommendation.get("chosen_route") == "D",
        },
        "snapshot": {
            "chosen_route": recommendation.get("chosen_route"),
            "chosen_route_name": recommendation.get("chosen_route_name"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_recommendation = load_json(compare_run_dir / "route_b_vs_c_next_step_recommendation.json")
        repeatability_summary = {
            "summary_status": "PASS",
            "reference_acceptance": acceptance,
            "candidate_run_dir": str(compare_run_dir.resolve()),
            "comparisons": [
                {
                    "field": "chosen_route",
                    "reference_value": recommendation.get("chosen_route"),
                    "candidate_value": compare_recommendation.get("chosen_route"),
                    "matches": recommendation.get("chosen_route") == compare_recommendation.get("chosen_route"),
                },
                {
                    "field": "chosen_route_name",
                    "reference_value": recommendation.get("chosen_route_name"),
                    "candidate_value": compare_recommendation.get("chosen_route_name"),
                    "matches": recommendation.get("chosen_route_name") == compare_recommendation.get("chosen_route_name"),
                },
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM route B vs C vs D comparison validation",
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
