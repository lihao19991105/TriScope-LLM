"""Repair/compress the labeled rerun blocker into condition-level rerun inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import (
    SCHEMA_VERSION,
    markdown,
    read_json,
    read_jsonl,
    run_py_compile,
    write_json,
    write_jsonl,
)


PY_FILES = [
    "src/eval/dualscope_first_slice_label_common.py",
    "src/eval/dualscope_first_slice_clean_poisoned_labeled_slice.py",
    "src/eval/post_dualscope_first_slice_clean_poisoned_labeled_slice_analysis.py",
    "src/eval/dualscope_minimal_first_slice_real_run_rerun_with_labels.py",
    "src/eval/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair.py",
    "scripts/build_dualscope_first_slice_clean_poisoned_labeled_slice.py",
    "scripts/build_post_dualscope_first_slice_clean_poisoned_labeled_slice_analysis.py",
    "scripts/build_dualscope_minimal_first_slice_real_run_rerun_with_labels.py",
    "scripts/build_dualscope_minimal_first_slice_real_run_rerun_with_labels_repair.py",
]


def _read_optional_json(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {"summary_status": "MISSING", "path": str(path)}


def _first_sources(rows: list[dict[str, Any]], max_sources: int) -> set[str]:
    selected: list[str] = []
    for row in rows:
        source_id = str(row.get("source_example_id") or "")
        if source_id and source_id not in selected:
            selected.append(source_id)
        if len(selected) >= max_sources:
            break
    return set(selected)


def _condition_input_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "example_id": row["row_id"],
        "row_id": row["row_id"],
        "pair_id": row["pair_id"],
        "source_example_id": row["source_example_id"],
        "dataset_id": row["dataset_id"],
        "condition": row["condition"],
        "prompt": row["prompt"],
        "response": row.get("response_reference", ""),
        "response_reference": row.get("response_reference", ""),
        "trigger_present": row["trigger_present"],
        "detection_label": row["detection_label"],
        "asr_eligible": row["asr_eligible"],
        "utility_eligible": row["utility_eligible"],
        "target_text": row["target_text"],
        "target_match_rule": row["target_match_rule"],
        "metadata": {
            "source_example_id": row["source_example_id"],
            "condition_level_rerun_input": True,
            "label_source": row.get("label_source"),
            "model_output_fabricated": False,
        },
    }


def build_labeled_rerun_repair(
    output_dir: Path,
    labeled_rerun_dir: Path,
    label_file: Path,
    max_sources: int,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    labeled_summary = _read_optional_json(
        labeled_rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_summary.json"
    )
    metric_readiness = _read_optional_json(
        labeled_rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_metric_readiness.json"
    )
    joined_rows_path = labeled_rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_joined_rows.jsonl"
    joined_rows = read_jsonl(joined_rows_path) if joined_rows_path.exists() else []
    label_rows = read_jsonl(label_file) if label_file.exists() else []
    selected_sources = _first_sources(joined_rows or label_rows, max_sources)
    condition_rows = [
        _condition_input_row(row)
        for row in label_rows
        if row.get("source_example_id") in selected_sources and row.get("condition") in {"clean", "poisoned_triggered"}
    ]
    condition_rows.sort(key=lambda row: (str(row["source_example_id"]), str(row["condition"])))
    clean_count = sum(1 for row in condition_rows if row["condition"] == "clean")
    poisoned_count = sum(1 for row in condition_rows if row["condition"] == "poisoned_triggered")
    source_count = len({row["source_example_id"] for row in condition_rows})
    condition_slice_ready = bool(condition_rows) and clean_count == poisoned_count == source_count
    py_compile = run_py_compile(repo_root, PY_FILES)

    source_level_compression = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "joined_row_count": len(joined_rows),
        "source_level_repeated_predictions_detected": bool(
            joined_rows and len(joined_rows) > len({row.get("source_example_id") for row in joined_rows})
        ),
        "condition_level_prediction_scope_present": metric_readiness.get("condition_level_predictions_ready") is True,
        "use_for_performance_metrics": False,
    }
    blocker_compression = {
        "summary_status": "PASS" if condition_slice_ready else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "labels_ready": metric_readiness.get("labels_ready") is True,
        "source_level_repeated_predictions_detected": source_level_compression["source_level_repeated_predictions_detected"],
        "condition_level_predictions_ready": False,
        "condition_level_query_slice_ready": condition_slice_ready,
        "model_responses_ready": False,
        "performance_metrics_ready": False,
        "auroc_ready": False,
        "f1_ready": False,
        "asr_ready": False,
        "clean_utility_ready": False,
        "blocker": "Need row_id-keyed condition-level Stage 1/2/3 outputs and model responses before reporting performance metrics.",
    }
    manifest = {
        "summary_status": "PASS" if condition_slice_ready else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "file": "condition_level_rerun_input_slice.jsonl",
        "row_count": len(condition_rows),
        "source_count": source_count,
        "clean_row_count": clean_count,
        "poisoned_triggered_row_count": poisoned_count,
        "example_id_key": "row_id",
        "source_example_id_preserved": all(row.get("source_example_id") for row in condition_rows),
        "ready_for_stage_entrypoints": condition_slice_ready,
    }
    if condition_slice_ready and py_compile["passed"]:
        verdict = "Repair/compression package validated"
        recommendation = "dualscope-minimal-first-slice-condition-level-rerun"
    elif py_compile["passed"]:
        verdict = "Partially validated"
        recommendation = "dualscope-minimal-first-slice-real-run-rerun-with-labels-repair"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-minimal-first-slice-real-run-rerun-with-labels-blocker-closure"
    summary = {
        "summary_status": "PASS" if verdict != "Not validated" else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-minimal-first-slice-real-run-rerun-with-labels-repair",
        "input_labeled_rerun_verdict": labeled_summary.get("final_verdict"),
        "previous_performance_metrics_ready": metric_readiness.get("performance_metrics_ready") is True,
        "label_row_count": len(label_rows),
        "joined_source_level_row_count": len(joined_rows),
        "condition_level_query_row_count": len(condition_rows),
        "condition_level_source_count": source_count,
        "condition_clean_row_count": clean_count,
        "condition_poisoned_row_count": poisoned_count,
        "condition_level_query_slice_ready": condition_slice_ready,
        "performance_metrics_ready": False,
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "labeled_rerun_dir": str(labeled_rerun_dir),
        "label_file": str(label_file),
        "max_sources": max_sources,
        "training_executed": False,
        "full_matrix_executed": False,
    }
    write_jsonl(output_dir / "condition_level_rerun_input_slice.jsonl", condition_rows)
    write_json(output_dir / "source_level_prediction_compression.json", source_level_compression)
    write_json(output_dir / "metric_blocker_compression.json", blocker_compression)
    write_json(output_dir / "condition_level_rerun_input_manifest.json", manifest)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_repair_scope.json", scope)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_repair_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_repair_summary.json", summary)
    write_json(
        output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_repair_verdict.json",
        {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict},
    )
    write_json(
        output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_repair_next_step_recommendation.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": verdict,
            "recommended_next_step": recommendation,
        },
    )
    markdown(
        output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_repair_report.md",
        "Minimal First-Slice Labeled Rerun Repair",
        [
            f"- Input labeled rerun verdict: `{labeled_summary.get('final_verdict')}`",
            f"- Condition-level input rows: `{len(condition_rows)}`",
            f"- Condition-level sources: `{source_count}`",
            f"- Performance metrics ready: `False`",
            f"- Final verdict: `{verdict}`",
            f"- Recommended next step: `{recommendation}`",
            "- No training, full matrix, benchmark truth change, gate change, or route_c continuation was performed.",
        ],
    )
    return summary
