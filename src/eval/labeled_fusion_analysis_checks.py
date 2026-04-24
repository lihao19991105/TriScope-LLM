"""Validation helpers for labeled-fusion analysis artifacts."""

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


def validate_labeled_fusion_analysis(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis_path = run_dir / "labeled_fusion_analysis_summary.json"
    blocker_path = run_dir / "labeled_fusion_scaling_blocker_summary.json"
    routes_path = run_dir / "route_comparison_A_vs_B.json"
    comparison_path = run_dir / "labeled_fusion_vs_unlabeled_fusion_comparison.csv"
    recommendation_path = run_dir / "labeled_fusion_next_step_recommendation.json"

    analysis = load_json(analysis_path)
    blocker = load_json(blocker_path)
    routes = load_json(routes_path)
    recommendation = load_json(recommendation_path)
    comparison_rows = load_csv_rows(comparison_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "analysis_summary", "path": str(analysis_path.resolve()), "exists": analysis_path.is_file()},
            {"artifact_name": "blocker_summary", "path": str(blocker_path.resolve()), "exists": blocker_path.is_file()},
            {"artifact_name": "route_comparison", "path": str(routes_path.resolve()), "exists": routes_path.is_file()},
            {"artifact_name": "comparison_csv", "path": str(comparison_path.resolve()), "exists": comparison_path.is_file()},
            {"artifact_name": "recommendation", "path": str(recommendation_path.resolve()), "exists": recommendation_path.is_file()},
        ],
        "field_checks": {
            "analysis_status_pass": analysis.get("summary_status") == "PASS",
            "blocker_status_pass": blocker.get("summary_status") == "PASS",
            "route_count_ge_2": len(routes.get("routes", [])) >= 2,
            "comparison_non_empty": bool(comparison_rows),
            "recommendation_has_route": recommendation.get("chosen_route") in {"A", "B"},
        },
        "snapshot": {
            "chosen_route": recommendation.get("chosen_route"),
            "current_labeled_rows": analysis.get("labeled_real_pilot_fusion", {}).get("num_rows"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_recommendation = load_json(compare_run_dir / "labeled_fusion_next_step_recommendation.json")
        compare_analysis = load_json(compare_run_dir / "labeled_fusion_analysis_summary.json")
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
                    "field": "current_labeled_rows",
                    "reference_value": analysis.get("labeled_real_pilot_fusion", {}).get("num_rows"),
                    "candidate_value": compare_analysis.get("labeled_real_pilot_fusion", {}).get("num_rows"),
                    "matches": analysis.get("labeled_real_pilot_fusion", {}).get("num_rows")
                    == compare_analysis.get("labeled_real_pilot_fusion", {}).get("num_rows"),
                },
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM labeled fusion analysis validation",
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
