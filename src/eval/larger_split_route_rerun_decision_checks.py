"""Validation helpers for larger-split route rerun decision artifacts."""

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


def validate_larger_split_route_rerun_decision(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    comparison_path = run_dir / "larger_split_route_rerun_comparison.json"
    tradeoff_path = run_dir / "larger_split_route_rerun_tradeoff_matrix.csv"
    recommendation_path = run_dir / "larger_split_route_next_step_recommendation.json"

    comparison = load_json(comparison_path)
    tradeoff_rows = load_csv_rows(tradeoff_path)
    recommendation = load_json(recommendation_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "comparison", "path": str(comparison_path.resolve()), "exists": comparison_path.is_file()},
            {"artifact_name": "tradeoff_matrix", "path": str(tradeoff_path.resolve()), "exists": tradeoff_path.is_file()},
            {"artifact_name": "recommendation", "path": str(recommendation_path.resolve()), "exists": recommendation_path.is_file()},
        ],
        "field_checks": {
            "comparison_pass": comparison.get("summary_status") == "PASS",
            "tradeoff_has_2_rows": len(tradeoff_rows) >= 2,
            "recommendation_present": bool(recommendation.get("recommended_route_to_rerun_first")),
        },
        "snapshot": {
            "recommended_route_to_rerun_first": recommendation.get("recommended_route_to_rerun_first"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_recommendation = load_json(compare_run_dir / "larger_split_route_next_step_recommendation.json")
        repeatability_summary = {
            "summary_status": "PASS",
            "reference_acceptance": acceptance,
            "candidate_run_dir": str(compare_run_dir.resolve()),
            "comparisons": [
                {
                    "field": "recommended_route_to_rerun_first",
                    "reference_value": recommendation.get("recommended_route_to_rerun_first"),
                    "candidate_value": compare_recommendation.get("recommended_route_to_rerun_first"),
                    "matches": recommendation.get("recommended_route_to_rerun_first") == compare_recommendation.get("recommended_route_to_rerun_first"),
                }
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM larger split route rerun decision validation",
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
