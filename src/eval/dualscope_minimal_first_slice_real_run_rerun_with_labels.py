"""Rerun the DualScope minimal first-slice chain with label contracts attached."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import (
    SCHEMA_VERSION,
    base_scope,
    markdown,
    read_json,
    read_jsonl,
    run_py_compile,
    write_json,
    write_jsonl,
)
from src.eval.dualscope_minimal_first_slice_real_run_rerun import build_real_run_rerun


PY_FILES = [
    "src/eval/dualscope_minimal_first_slice_real_run_rerun_with_labels.py",
    "scripts/build_dualscope_minimal_first_slice_real_run_rerun_with_labels.py",
    "src/eval/dualscope_minimal_first_slice_real_run_rerun.py",
    "scripts/build_dualscope_minimal_first_slice_real_run_rerun.py",
]


def _read_optional_json(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {"summary_status": "MISSING", "path": str(path)}


def _index_stage3_by_source(stage3_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("example_id")): row for row in stage3_rows if row.get("example_id")}


def _metric_counts(joined_rows: list[dict[str, Any]]) -> dict[str, Any]:
    positives = sum(1 for row in joined_rows if row.get("detection_label") == 1)
    negatives = sum(1 for row in joined_rows if row.get("detection_label") == 0)
    flagged_positive = sum(1 for row in joined_rows if row.get("detection_label") == 1 and row.get("final_decision_flag") is True)
    flagged_negative = sum(1 for row in joined_rows if row.get("detection_label") == 0 and row.get("final_decision_flag") is True)
    return {
        "joined_row_count": len(joined_rows),
        "positive_label_count": positives,
        "negative_label_count": negatives,
        "flagged_positive_count": flagged_positive,
        "flagged_negative_count": flagged_negative,
    }


def build_labeled_real_run_rerun(
    output_dir: Path,
    rerun_output_dir: Path,
    label_output_dir: Path,
    label_analysis_dir: Path,
    mode: str,
    seed: int,
    no_full_matrix: bool,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    if not no_full_matrix:
        raise ValueError("--no-full-matrix is required.")

    nested_rerun_dir = output_dir / "base_rerun"
    rerun_summary = build_real_run_rerun(nested_rerun_dir, mode, no_full_matrix)

    label_summary = _read_optional_json(label_output_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_summary.json")
    label_metric_readiness = _read_optional_json(label_output_dir / "dualscope_first_slice_metric_readiness_summary.json")
    label_verdict = _read_optional_json(label_analysis_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_verdict.json")
    label_rows_path = Path(
        _read_optional_json(label_output_dir / "dualscope_first_slice_clean_poisoned_pair_manifest.json").get(
            "output_file",
            "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        )
    )
    if not label_rows_path.is_absolute():
        label_rows_path = repo_root / label_rows_path

    pipeline_dir = nested_rerun_dir / "pipeline"
    stage3_path = pipeline_dir / "stage3_fusion/stage3_fusion_outputs.jsonl"
    label_rows = read_jsonl(label_rows_path) if label_rows_path.exists() else []
    stage3_rows = read_jsonl(stage3_path) if stage3_path.exists() else []
    stage3_by_source = _index_stage3_by_source(stage3_rows)

    joined_rows: list[dict[str, Any]] = []
    unmatched_label_rows: list[str] = []
    for row in label_rows:
        source_id = str(row.get("source_example_id") or "")
        stage3 = stage3_by_source.get(source_id)
        if stage3 is None:
            unmatched_label_rows.append(str(row.get("row_id") or source_id))
            continue
        joined_rows.append(
            {
                "row_id": row.get("row_id"),
                "pair_id": row.get("pair_id"),
                "source_example_id": source_id,
                "condition": row.get("condition"),
                "detection_label": row.get("detection_label"),
                "asr_eligible": row.get("asr_eligible"),
                "utility_eligible": row.get("utility_eligible"),
                "final_risk_score": stage3.get("final_risk_score"),
                "final_decision_flag": stage3.get("final_decision_flag"),
                "stage3_prediction_scope": "source_example_level",
            }
        )

    condition_level_predictions_ready = all(
        row.get("condition") in {"clean", "poisoned_triggered"} and row.get("stage3_prediction_scope") == "condition_row_level"
        for row in joined_rows
    )
    labels_ready = bool(label_summary.get("schema_valid") and label_summary.get("pairing_valid"))
    joined_source_count = len({row["source_example_id"] for row in joined_rows})
    metric_readiness = {
        "summary_status": "PASS" if labels_ready else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "labels_ready": labels_ready,
        "label_verdict": label_verdict.get("final_verdict"),
        "source_level_stage3_outputs_ready": bool(stage3_rows),
        "condition_level_predictions_ready": condition_level_predictions_ready,
        "joined_label_row_count": len(joined_rows),
        "joined_source_count": joined_source_count,
        "total_label_row_count": len(label_rows),
        "stage3_output_count": len(stage3_rows),
        "performance_metrics_ready": labels_ready and condition_level_predictions_ready,
        "auroc_ready": labels_ready and condition_level_predictions_ready,
        "f1_ready": labels_ready and condition_level_predictions_ready,
        "asr_ready": False,
        "clean_utility_ready": False,
        "reason": (
            "Labels are attached to matching source-level Stage 3 outputs, but clean/poisoned row-level predictions "
            "and model responses are still required for honest AUROC/F1/ASR/utility metrics."
        ),
        **_metric_counts(joined_rows),
    }
    alignment = {
        "summary_status": "PASS" if joined_rows else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "label_rows_path": str(label_rows_path),
        "stage3_path": str(stage3_path),
        "label_row_count": len(label_rows),
        "stage3_output_count": len(stage3_rows),
        "joined_label_row_count": len(joined_rows),
        "joined_source_count": joined_source_count,
        "unmatched_label_row_count": len(unmatched_label_rows),
        "unmatched_label_rows_preview": unmatched_label_rows[:20],
        "prediction_scope_mismatch": bool(joined_rows) and not condition_level_predictions_ready,
    }
    py_compile = run_py_compile(repo_root, PY_FILES)

    if (
        rerun_summary.get("final_verdict") != "Not validated"
        and labels_ready
        and metric_readiness["performance_metrics_ready"]
        and py_compile["passed"]
    ):
        final_verdict = "Minimal first-slice labeled rerun validated"
        recommendation = "dualscope-first-slice-target-response-generation-plan"
    elif rerun_summary.get("final_verdict") != "Not validated" and labels_ready and joined_rows and py_compile["passed"]:
        final_verdict = "Partially validated"
        recommendation = "dualscope-minimal-first-slice-real-run-rerun-with-labels-repair"
    else:
        final_verdict = "Not validated"
        recommendation = "dualscope-minimal-first-slice-real-run-rerun-with-labels-blocker-closure"

    scope = base_scope("dualscope-minimal-first-slice-real-run-rerun-with-labels", output_dir)
    scope.update(
        {
            "rerun_output_dir": str(rerun_output_dir),
            "nested_rerun_dir": str(nested_rerun_dir),
            "label_output_dir": str(label_output_dir),
            "label_analysis_dir": str(label_analysis_dir),
            "mode": mode,
            "seed": seed,
            "no_full_matrix": no_full_matrix,
        }
    )
    summary = {
        "summary_status": "PASS" if final_verdict != "Not validated" else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "base_rerun_verdict": rerun_summary.get("final_verdict"),
        "labels_ready": labels_ready,
        "labels_integrated_into_metric_readiness": bool(joined_rows),
        "performance_metrics_ready": metric_readiness["performance_metrics_ready"],
        "condition_level_predictions_ready": condition_level_predictions_ready,
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }

    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_scope.json", scope)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_label_contract.json", label_summary)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_label_metric_source.json", label_metric_readiness)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_alignment.json", alignment)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_metric_readiness.json", metric_readiness)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_summary.json", summary)
    write_json(
        output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_verdict.json",
        {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": final_verdict},
    )
    write_json(
        output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_next_step_recommendation.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": recommendation,
        },
    )
    write_jsonl(
        output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_joined_rows.jsonl",
        joined_rows,
    )
    write_jsonl(
        output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_details.jsonl",
        [
            {"detail_type": "base_rerun_summary", "payload": rerun_summary},
            {"detail_type": "label_summary", "payload": label_summary},
            {"detail_type": "label_metric_readiness", "payload": label_metric_readiness},
            {"detail_type": "alignment", "payload": alignment},
            {"detail_type": "metric_readiness", "payload": metric_readiness},
        ],
    )
    markdown(
        output_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_report.md",
        "Minimal First-Slice Real Run Rerun With Labels",
        [
            f"- Base rerun verdict: `{rerun_summary.get('final_verdict')}`",
            f"- Labels ready: `{labels_ready}`",
            f"- Joined label rows: `{len(joined_rows)}`",
            f"- Stage 3 prediction scope: `source_example_level`",
            f"- Performance metrics ready: `{metric_readiness['performance_metrics_ready']}`",
            f"- Final verdict: `{final_verdict}`",
            f"- Recommended next step: `{recommendation}`",
            "- No training, full matrix, benchmark truth change, gate change, or route_c continuation was performed.",
        ],
    )
    return summary
