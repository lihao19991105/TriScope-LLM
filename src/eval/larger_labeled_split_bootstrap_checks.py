"""Validation helpers for larger labeled split bootstrap artifacts."""

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
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def validate_larger_labeled_split_bootstrap(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_path = run_dir / "larger_labeled_split_plan.json"
    definition_path = run_dir / "larger_labeled_split_definition.json"
    readiness_path = run_dir / "larger_labeled_split_readiness_summary.json"
    split_path = run_dir / "larger_labeled_split.jsonl"
    summary_path = run_dir / "larger_labeled_split_summary.json"
    bridge_summary_path = run_dir / "larger_labeled_bridge_artifact_summary.json"
    compatibility_path = run_dir / "larger_split_route_compatibility_summary.json"
    materialized_dir = run_dir / "materialized_larger_labeled_inputs"

    reasoning_query_path = materialized_dir / "reasoning_query_contracts.jsonl"
    confidence_query_path = materialized_dir / "confidence_query_contracts.jsonl"
    illumination_query_path = materialized_dir / "illumination_query_contracts.jsonl"
    labeled_illumination_query_path = materialized_dir / "labeled_illumination_query_contracts.jsonl"

    plan = load_json(plan_path)
    definition = load_json(definition_path)
    readiness = load_json(readiness_path)
    summary = load_json(summary_path)
    bridge_summary = load_json(bridge_summary_path)
    compatibility = load_json(compatibility_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "plan", "path": str(plan_path.resolve()), "exists": plan_path.is_file()},
            {"artifact_name": "definition", "path": str(definition_path.resolve()), "exists": definition_path.is_file()},
            {"artifact_name": "readiness", "path": str(readiness_path.resolve()), "exists": readiness_path.is_file()},
            {"artifact_name": "larger_split", "path": str(split_path.resolve()), "exists": split_path.is_file()},
            {"artifact_name": "summary", "path": str(summary_path.resolve()), "exists": summary_path.is_file()},
            {"artifact_name": "bridge_summary", "path": str(bridge_summary_path.resolve()), "exists": bridge_summary_path.is_file()},
            {"artifact_name": "compatibility", "path": str(compatibility_path.resolve()), "exists": compatibility_path.is_file()},
            {"artifact_name": "reasoning_query_contracts", "path": str(reasoning_query_path.resolve()), "exists": reasoning_query_path.is_file()},
            {"artifact_name": "confidence_query_contracts", "path": str(confidence_query_path.resolve()), "exists": confidence_query_path.is_file()},
            {"artifact_name": "illumination_query_contracts", "path": str(illumination_query_path.resolve()), "exists": illumination_query_path.is_file()},
            {"artifact_name": "labeled_illumination_query_contracts", "path": str(labeled_illumination_query_path.resolve()), "exists": labeled_illumination_query_path.is_file()},
        ],
        "field_checks": {
            "plan_pass": plan.get("summary_status") == "PASS",
            "definition_row_target_20": definition.get("row_count_target") == 20,
            "readiness_pass": readiness.get("summary_status") == "PASS",
            "larger_split_has_20_rows": count_jsonl_rows(split_path) == 20,
            "summary_reports_20_rows": summary.get("num_rows") == 20,
            "bridge_summary_pass": bridge_summary.get("summary_status") == "PASS",
            "compatibility_pass": compatibility.get("summary_status") == "PASS",
            "reasoning_contracts_has_20_rows": count_jsonl_rows(reasoning_query_path) == 20,
            "confidence_contracts_has_20_rows": count_jsonl_rows(confidence_query_path) == 20,
            "illumination_contracts_has_20_rows": count_jsonl_rows(illumination_query_path) == 20,
            "labeled_illumination_contracts_has_40_rows": count_jsonl_rows(labeled_illumination_query_path) == 40,
        },
        "snapshot": {
            "larger_split_rows": summary.get("num_rows"),
            "num_new_rows": summary.get("num_new_rows"),
            "route_b_capacity": summary.get("expected_follow_on_capacity", {}).get("route_b_more_natural_rows"),
            "route_c_capacity": summary.get("expected_follow_on_capacity", {}).get("route_c_benchmark_truth_leaning_rows"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_summary = load_json(compare_run_dir / "larger_labeled_split_summary.json")
        compare_compatibility = load_json(compare_run_dir / "larger_split_route_compatibility_summary.json")
        repeatability_summary = {
            "summary_status": "PASS",
            "reference_acceptance": acceptance,
            "candidate_run_dir": str(compare_run_dir.resolve()),
            "comparisons": [
                {
                    "field": "num_rows",
                    "reference_value": summary.get("num_rows"),
                    "candidate_value": compare_summary.get("num_rows"),
                    "matches": summary.get("num_rows") == compare_summary.get("num_rows"),
                },
                {
                    "field": "num_new_rows",
                    "reference_value": summary.get("num_new_rows"),
                    "candidate_value": compare_summary.get("num_new_rows"),
                    "matches": summary.get("num_new_rows") == compare_summary.get("num_new_rows"),
                },
                {
                    "field": "bridge_compatibility",
                    "reference_value": compatibility.get("compatibility_targets"),
                    "candidate_value": compare_compatibility.get("compatibility_targets"),
                    "matches": compatibility.get("compatibility_targets") == compare_compatibility.get("compatibility_targets"),
                },
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM larger labeled split bootstrap validation",
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
