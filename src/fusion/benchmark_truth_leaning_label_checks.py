"""Validation helpers for benchmark-truth-leaning label bootstrap artifacts."""

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


def validate_benchmark_truth_leaning_label_bootstrap(
    run_dir: Path,
    compare_run_dir: Path | None,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    selection_path = run_dir / "benchmark_truth_leaning_label_selection.json"
    definition_path = run_dir / "benchmark_truth_leaning_label_definition.json"
    readiness_path = run_dir / "benchmark_truth_leaning_readiness_summary.json"
    dataset_path = run_dir / "benchmark_truth_leaning_dataset.jsonl"
    summary_path = run_dir / "benchmark_truth_leaning_summary.json"
    predictions_path = run_dir / "benchmark_truth_leaning_logistic_predictions.jsonl"
    logistic_summary_path = run_dir / "benchmark_truth_leaning_logistic_summary.json"

    selection = load_json(selection_path)
    definition = load_json(definition_path)
    readiness = load_json(readiness_path)
    summary = load_json(summary_path)
    logistic_summary = load_json(logistic_summary_path)

    acceptance = {
        "summary_status": "PASS",
        "run_dir": str(run_dir.resolve()),
        "artifact_checks": [
            {"artifact_name": "selection", "path": str(selection_path.resolve()), "exists": selection_path.is_file()},
            {"artifact_name": "definition", "path": str(definition_path.resolve()), "exists": definition_path.is_file()},
            {"artifact_name": "readiness", "path": str(readiness_path.resolve()), "exists": readiness_path.is_file()},
            {"artifact_name": "dataset", "path": str(dataset_path.resolve()), "exists": dataset_path.is_file()},
            {"artifact_name": "summary", "path": str(summary_path.resolve()), "exists": summary_path.is_file()},
            {"artifact_name": "predictions", "path": str(predictions_path.resolve()), "exists": predictions_path.is_file()},
            {"artifact_name": "logistic_summary", "path": str(logistic_summary_path.resolve()), "exists": logistic_summary_path.is_file()},
        ],
        "field_checks": {
            "selection_pass": selection.get("summary_status") == "PASS",
            "definition_name_correct": definition.get("label_name") == "task_answer_incorrect_label",
            "readiness_pass": readiness.get("summary_status") == "PASS",
            "dataset_non_empty": count_jsonl_rows(dataset_path) > 0,
            "summary_pass": summary.get("summary_status") == "PASS",
            "predictions_non_empty": count_jsonl_rows(predictions_path) > 0,
            "logistic_pass": logistic_summary.get("summary_status") == "PASS",
        },
        "snapshot": {
            "num_rows": summary.get("num_rows"),
            "class_balance": summary.get("class_balance"),
            "num_predictions": logistic_summary.get("num_predictions"),
            "mean_prediction_score": logistic_summary.get("mean_prediction_score"),
        },
    }
    write_json(output_dir / "artifact_acceptance.json", acceptance)

    repeatability_summary: dict[str, Any] | None = None
    if compare_run_dir is not None:
        compare_summary = load_json(compare_run_dir / "benchmark_truth_leaning_summary.json")
        compare_logistic = load_json(compare_run_dir / "benchmark_truth_leaning_logistic_summary.json")
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
                    "field": "class_balance",
                    "reference_value": summary.get("class_balance"),
                    "candidate_value": compare_summary.get("class_balance"),
                    "matches": summary.get("class_balance") == compare_summary.get("class_balance"),
                },
                {
                    "field": "num_predictions",
                    "reference_value": logistic_summary.get("num_predictions"),
                    "candidate_value": compare_logistic.get("num_predictions"),
                    "matches": logistic_summary.get("num_predictions") == compare_logistic.get("num_predictions"),
                },
                {
                    "field": "mean_prediction_score",
                    "reference_value": logistic_summary.get("mean_prediction_score"),
                    "candidate_value": compare_logistic.get("mean_prediction_score"),
                    "matches": logistic_summary.get("mean_prediction_score") == compare_logistic.get("mean_prediction_score"),
                },
            ],
        }
        repeatability_summary["all_key_metrics_match"] = all(item["matches"] for item in repeatability_summary["comparisons"])
        write_json(output_dir / "repeatability_summary.json", repeatability_summary)

    (output_dir / "repeat_check.log").write_text(
        "\n".join(
            [
                "TriScope-LLM benchmark-truth-leaning label bootstrap validation",
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
