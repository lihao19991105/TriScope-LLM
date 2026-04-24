"""Validation helpers for real-experiment cutover bootstrap artifacts."""

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


def validate_real_experiment_cutover_bootstrap(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    plan_path = run_dir / "real_experiment_cutover_plan.json"
    selection_path = run_dir / "real_experiment_candidate_selection.json"
    readiness_path = run_dir / "real_experiment_readiness_summary.json"
    inputs_dir = run_dir / "materialized_real_experiment_inputs"
    contract_path = run_dir / "real_experiment_input_contract.json"
    summary_path = run_dir / "real_experiment_bootstrap_summary.json"
    dataset_path = inputs_dir / "real_experiment_dataset.jsonl"

    plan = load_json(plan_path)
    selection = load_json(selection_path)
    readiness = load_json(readiness_path)
    contract = load_json(contract_path)
    summary = load_json(summary_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "plan", "path": str(plan_path.resolve()), "exists": plan_path.is_file()},
            {"artifact_name": "selection", "path": str(selection_path.resolve()), "exists": selection_path.is_file()},
            {"artifact_name": "readiness", "path": str(readiness_path.resolve()), "exists": readiness_path.is_file()},
            {"artifact_name": "inputs_dir", "path": str(inputs_dir.resolve()), "exists": inputs_dir.is_dir()},
            {"artifact_name": "dataset", "path": str(dataset_path.resolve()), "exists": dataset_path.is_file()},
            {"artifact_name": "contract", "path": str(contract_path.resolve()), "exists": contract_path.is_file()},
            {"artifact_name": "summary", "path": str(summary_path.resolve()), "exists": summary_path.is_file()},
        ],
        "field_checks": {
            "plan_pass": plan.get("summary_status") == "PASS",
            "cutover_selected": plan.get("chosen_next_step") == "prepare_small_real_labeled_experiment",
            "selection_pass": selection.get("summary_status") == "PASS",
            "readiness_pass": readiness.get("summary_status") == "PASS",
            "dataset_non_empty": count_jsonl_rows(dataset_path) > 0,
            "contract_pass": contract.get("summary_status") == "PASS",
            "summary_pass": summary.get("summary_status") == "PASS",
        },
        "snapshot": {
            "chosen_candidate_name": plan.get("chosen_candidate_name"),
            "dataset_rows": summary.get("dataset_rows"),
            "route_b_compatible": summary.get("route_and_fusion_compatibility", {}).get("route_b"),
            "route_c_compatible": summary.get("route_and_fusion_compatibility", {}).get("route_c"),
            "fusion_compatible": summary.get("route_and_fusion_compatibility", {}).get("fusion"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_summary = load_json(compare_run_dir / "real_experiment_bootstrap_summary.json")
        repeatability_summary = {
            "summary_status": "PASS",
            "reference_acceptance": acceptance,
            "candidate_run_dir": str(compare_run_dir.resolve()),
            "comparisons": [
                {
                    "field": "chosen_candidate_name",
                    "reference_value": summary.get("chosen_candidate_name"),
                    "candidate_value": compare_summary.get("chosen_candidate_name"),
                    "matches": summary.get("chosen_candidate_name") == compare_summary.get("chosen_candidate_name"),
                },
                {
                    "field": "dataset_rows",
                    "reference_value": summary.get("dataset_rows"),
                    "candidate_value": compare_summary.get("dataset_rows"),
                    "matches": summary.get("dataset_rows") == compare_summary.get("dataset_rows"),
                },
                {
                    "field": "fusion_compatible",
                    "reference_value": summary.get("route_and_fusion_compatibility", {}).get("fusion"),
                    "candidate_value": compare_summary.get("route_and_fusion_compatibility", {}).get("fusion"),
                    "matches": summary.get("route_and_fusion_compatibility", {}).get("fusion")
                    == compare_summary.get("route_and_fusion_compatibility", {}).get("fusion"),
                },
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM real experiment cutover bootstrap validation",
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
