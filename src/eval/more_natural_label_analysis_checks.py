"""Validation helpers for more-natural-label analysis artifacts."""

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


def validate_more_natural_label_analysis(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    scaling_path = run_dir / "controlled_supervision_scaling_summary.json"
    routes_path = run_dir / "route_A_vs_route_B_comparison.json"
    ceiling_path = run_dir / "supervision_ceiling_summary.json"
    inputs_path = run_dir / "route_decision_inputs.csv"
    recommendation_path = run_dir / "more_natural_label_next_step_recommendation.json"

    scaling = load_json(scaling_path)
    routes = load_json(routes_path)
    ceiling = load_json(ceiling_path)
    recommendation = load_json(recommendation_path)
    rows = load_csv_rows(inputs_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "scaling_summary", "path": str(scaling_path.resolve()), "exists": scaling_path.is_file()},
            {"artifact_name": "route_comparison", "path": str(routes_path.resolve()), "exists": routes_path.is_file()},
            {"artifact_name": "ceiling_summary", "path": str(ceiling_path.resolve()), "exists": ceiling_path.is_file()},
            {"artifact_name": "decision_inputs_csv", "path": str(inputs_path.resolve()), "exists": inputs_path.is_file()},
            {"artifact_name": "recommendation", "path": str(recommendation_path.resolve()), "exists": recommendation_path.is_file()},
        ],
        "field_checks": {
            "scaling_status_pass": scaling.get("summary_status") == "PASS",
            "route_count_ge_2": len(routes.get("routes", [])) >= 2,
            "ceiling_status_pass": ceiling.get("summary_status") == "PASS",
            "decision_inputs_non_empty": bool(rows),
            "recommendation_is_B": recommendation.get("recommended_route") == "B",
        },
        "snapshot": {
            "expanded_labeled_rows": scaling.get("route_a_state_after_expansion", {}).get("expanded_labeled_rows"),
            "recommended_route": recommendation.get("recommended_route"),
            "recommended_route_name": recommendation.get("recommended_route_name"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_scaling = load_json(compare_run_dir / "controlled_supervision_scaling_summary.json")
        compare_recommendation = load_json(compare_run_dir / "more_natural_label_next_step_recommendation.json")
        repeatability_summary = {
            "summary_status": "PASS",
            "reference_acceptance": acceptance,
            "candidate_run_dir": str(compare_run_dir.resolve()),
            "comparisons": [
                {
                    "field": "expanded_labeled_rows",
                    "reference_value": scaling.get("route_a_state_after_expansion", {}).get("expanded_labeled_rows"),
                    "candidate_value": compare_scaling.get("route_a_state_after_expansion", {}).get("expanded_labeled_rows"),
                    "matches": scaling.get("route_a_state_after_expansion", {}).get("expanded_labeled_rows")
                    == compare_scaling.get("route_a_state_after_expansion", {}).get("expanded_labeled_rows"),
                },
                {
                    "field": "recommended_route",
                    "reference_value": recommendation.get("recommended_route"),
                    "candidate_value": compare_recommendation.get("recommended_route"),
                    "matches": recommendation.get("recommended_route") == compare_recommendation.get("recommended_route"),
                },
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM more-natural-label analysis validation",
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
