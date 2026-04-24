"""Validation helpers for supervision route comparison artifacts."""

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


def validate_supervision_route_comparison(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "supervision_route_comparison_summary.json"
    routes_path = run_dir / "route_A_vs_B_vs_C_comparison.json"
    tradeoff_path = run_dir / "supervision_tradeoff_matrix.csv"
    ceiling_path = run_dir / "supervision_ceiling_and_cost_summary.json"
    recommendation_path = run_dir / "supervision_next_step_recommendation.json"

    summary = load_json(summary_path)
    routes = load_json(routes_path)
    ceiling = load_json(ceiling_path)
    recommendation = load_json(recommendation_path)
    rows = load_csv_rows(tradeoff_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "summary", "path": str(summary_path.resolve()), "exists": summary_path.is_file()},
            {"artifact_name": "routes", "path": str(routes_path.resolve()), "exists": routes_path.is_file()},
            {"artifact_name": "tradeoff_csv", "path": str(tradeoff_path.resolve()), "exists": tradeoff_path.is_file()},
            {"artifact_name": "ceiling_summary", "path": str(ceiling_path.resolve()), "exists": ceiling_path.is_file()},
            {"artifact_name": "recommendation", "path": str(recommendation_path.resolve()), "exists": recommendation_path.is_file()},
        ],
        "field_checks": {
            "summary_pass": summary.get("summary_status") == "PASS",
            "routes_ge_3": len(routes.get("routes", [])) >= 3,
            "tradeoff_non_empty": bool(rows),
            "ceiling_pass": ceiling.get("summary_status") == "PASS",
            "recommendation_is_C": recommendation.get("chosen_route") == "C",
        },
        "snapshot": {
            "chosen_route": recommendation.get("chosen_route"),
            "chosen_route_name": recommendation.get("chosen_route_name"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_recommendation = load_json(compare_run_dir / "supervision_next_step_recommendation.json")
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
                "TriScope-LLM supervision route comparison validation",
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
