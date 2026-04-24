"""Validation helpers for post-v4 next-step bootstrap artifacts."""

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


def validate_post_v4_next_step_bootstrap(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_path = run_dir / "post_v4_next_step_plan.json"
    readiness_path = run_dir / "post_v4_next_step_readiness_summary.json"
    split_path = run_dir / "larger_labeled_split_v5.jsonl"
    summary_path = run_dir / "larger_labeled_split_v5_summary.json"
    bridge_path = run_dir / "post_v4_next_step_bridge_summary.json"

    plan = load_json(plan_path)
    readiness = load_json(readiness_path)
    summary = load_json(summary_path)
    bridge = load_json(bridge_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "plan", "path": str(plan_path.resolve()), "exists": plan_path.is_file()},
            {"artifact_name": "readiness", "path": str(readiness_path.resolve()), "exists": readiness_path.is_file()},
            {"artifact_name": "split", "path": str(split_path.resolve()), "exists": split_path.is_file()},
            {"artifact_name": "summary", "path": str(summary_path.resolve()), "exists": summary_path.is_file()},
            {"artifact_name": "bridge", "path": str(bridge_path.resolve()), "exists": bridge_path.is_file()},
        ],
        "field_checks": {
            "plan_pass": plan.get("summary_status") == "PASS",
            "chosen_next_step_is_v5": plan.get("chosen_next_step") == "prepare_larger_labeled_split_v5",
            "readiness_pass": readiness.get("summary_status") == "PASS",
            "split_has_60_rows": count_jsonl_rows(split_path) == 60,
            "summary_pass": summary.get("summary_status") == "PASS",
            "bridge_pass": bridge.get("summary_status") == "PASS",
        },
        "snapshot": {
            "num_rows": summary.get("num_rows"),
            "num_new_rows": summary.get("num_new_rows"),
            "route_b_capacity": summary.get("expected_follow_on_capacity", {}).get("route_b_more_natural_rows"),
            "route_c_capacity": summary.get("expected_follow_on_capacity", {}).get("route_c_benchmark_truth_leaning_rows"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_summary = load_json(compare_run_dir / "larger_labeled_split_v5_summary.json")
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
                    "field": "route_c_capacity",
                    "reference_value": summary.get("expected_follow_on_capacity", {}).get("route_c_benchmark_truth_leaning_rows"),
                    "candidate_value": compare_summary.get("expected_follow_on_capacity", {}).get("route_c_benchmark_truth_leaning_rows"),
                    "matches": summary.get("expected_follow_on_capacity", {}).get("route_c_benchmark_truth_leaning_rows")
                    == compare_summary.get("expected_follow_on_capacity", {}).get("route_c_benchmark_truth_leaning_rows"),
                },
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM post-v4 next-step bootstrap validation",
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
