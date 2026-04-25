"""Run the DualScope minimal first-slice chain on condition-level rows."""

from __future__ import annotations

import subprocess
import sys
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


TASK_NAME = "dualscope-minimal-first-slice-condition-level-rerun"
PY_FILES = [
    "src/eval/dualscope_minimal_first_slice_condition_level_rerun.py",
    "scripts/build_dualscope_minimal_first_slice_condition_level_rerun.py",
    "scripts/run_dualscope_stage1_illumination.py",
    "scripts/run_dualscope_stage2_confidence.py",
    "scripts/run_dualscope_stage3_fusion.py",
]


def _run_command(repo_root: Path, command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=repo_root, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "stdout": result.stdout.strip()[-4000:],
        "stderr": result.stderr.strip()[-4000:],
    }


def _auc(labels: list[int], scores: list[float]) -> float | None:
    positives = [score for label, score in zip(labels, scores) if label == 1]
    negatives = [score for label, score in zip(labels, scores) if label == 0]
    if not positives or not negatives:
        return None
    wins = 0.0
    for pos in positives:
        for neg in negatives:
            if pos > neg:
                wins += 1.0
            elif pos == neg:
                wins += 0.5
    return round(wins / (len(positives) * len(negatives)), 6)


def _tpr_at_fpr(labels: list[int], scores: list[float], max_fpr: float) -> float | None:
    positives = sum(1 for label in labels if label == 1)
    negatives = sum(1 for label in labels if label == 0)
    if positives == 0 or negatives == 0:
        return None
    best = 0.0
    for threshold in sorted(set(scores), reverse=True):
        tp = sum(1 for label, score in zip(labels, scores) if label == 1 and score >= threshold)
        fp = sum(1 for label, score in zip(labels, scores) if label == 0 and score >= threshold)
        fpr = fp / negatives
        if fpr <= max_fpr:
            best = max(best, tp / positives)
    return round(best, 6)


def _classification_metrics(joined_rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = [int(row["detection_label"]) for row in joined_rows]
    scores = [float(row["final_risk_score"]) for row in joined_rows]
    predictions = [bool(row["final_decision_flag"]) for row in joined_rows]
    tp = sum(1 for label, pred in zip(labels, predictions) if label == 1 and pred)
    fp = sum(1 for label, pred in zip(labels, predictions) if label == 0 and pred)
    tn = sum(1 for label, pred in zip(labels, predictions) if label == 0 and not pred)
    fn = sum(1 for label, pred in zip(labels, predictions) if label == 1 and not pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "metric_scope": "condition_level_detection_preview",
        "real_performance_claimed": False,
        "row_count": len(joined_rows),
        "positive_label_count": sum(1 for label in labels if label == 1),
        "negative_label_count": sum(1 for label in labels if label == 0),
        "threshold": 0.55,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "roc_auc": _auc(labels, scores),
        "tpr_at_fpr_1pct": _tpr_at_fpr(labels, scores, 0.01),
    }


def _join_predictions(input_rows: list[dict[str, Any]], stage3_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    stage3_by_id = {str(row.get("example_id")): row for row in stage3_rows}
    joined: list[dict[str, Any]] = []
    missing: list[str] = []
    for input_row in input_rows:
        row_id = str(input_row.get("row_id") or input_row.get("example_id") or "")
        stage3 = stage3_by_id.get(row_id)
        if stage3 is None:
            missing.append(row_id)
            continue
        budget = stage3.get("budget_usage_summary", {})
        joined.append(
            {
                "row_id": row_id,
                "example_id": stage3.get("example_id"),
                "pair_id": input_row.get("pair_id"),
                "source_example_id": input_row.get("source_example_id"),
                "dataset_id": input_row.get("dataset_id"),
                "condition": input_row.get("condition"),
                "trigger_present": input_row.get("trigger_present"),
                "detection_label": input_row.get("detection_label"),
                "asr_eligible": input_row.get("asr_eligible"),
                "utility_eligible": input_row.get("utility_eligible"),
                "target_text": input_row.get("target_text"),
                "target_match_rule": input_row.get("target_match_rule"),
                "final_risk_score": stage3.get("final_risk_score"),
                "final_risk_bucket": stage3.get("final_risk_bucket"),
                "final_decision_flag": stage3.get("final_decision_flag"),
                "verification_triggered": stage3.get("verification_triggered"),
                "capability_mode": stage3.get("capability_mode"),
                "stage1_query_count": budget.get("stage1_query_count", 0),
                "stage2_query_count": budget.get("stage2_query_count", 0),
                "prediction_scope": "condition_row_level",
                "model_response_available": False,
            }
        )
    return joined, missing


def build_condition_level_rerun(
    output_dir: Path,
    input_slice: Path,
    input_manifest: Path,
    capability_mode: str,
    seed: int,
    no_full_matrix: bool,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    if not no_full_matrix:
        raise ValueError("--no-full-matrix is required.")
    manifest = read_json(input_manifest)
    input_rows = read_jsonl(input_slice)
    if manifest.get("ready_for_stage_entrypoints") is not True:
        raise ValueError("Condition-level input manifest is not ready for stage entrypoints.")
    if len(input_rows) != int(manifest.get("row_count", -1)):
        raise ValueError("Condition-level input row count does not match manifest.")

    dirs = {
        "stage1": output_dir / "stage1_illumination",
        "stage2": output_dir / "stage2_confidence",
        "stage3": output_dir / "stage3_fusion",
    }
    command_plan = [
        [
            sys.executable,
            "scripts/run_dualscope_stage1_illumination.py",
            "--input-file",
            str(input_slice),
            "--output-dir",
            str(dirs["stage1"]),
            "--seed",
            str(seed),
        ],
        [
            sys.executable,
            "scripts/run_dualscope_stage2_confidence.py",
            "--stage1-file",
            str(dirs["stage1"] / "stage1_illumination_outputs.jsonl"),
            "--output-dir",
            str(dirs["stage2"]),
            "--capability-mode",
            capability_mode,
            "--seed",
            str(seed),
        ],
        [
            sys.executable,
            "scripts/run_dualscope_stage3_fusion.py",
            "--stage1-file",
            str(dirs["stage1"] / "stage1_illumination_outputs.jsonl"),
            "--stage2-file",
            str(dirs["stage2"] / "stage2_confidence_outputs.jsonl"),
            "--output-dir",
            str(dirs["stage3"]),
            "--seed",
            str(seed),
        ],
    ]
    stage_results: list[dict[str, Any]] = []
    for command in command_plan:
        result = _run_command(repo_root, command)
        stage_results.append(result)
        if not result["passed"]:
            break

    stage3_path = dirs["stage3"] / "stage3_fusion_outputs.jsonl"
    stage3_rows = read_jsonl(stage3_path) if stage3_path.exists() else []
    joined_rows, missing_row_ids = _join_predictions(input_rows, stage3_rows)
    clean_count = sum(1 for row in joined_rows if row.get("condition") == "clean")
    poisoned_count = sum(1 for row in joined_rows if row.get("condition") == "poisoned_triggered")
    condition_predictions_ready = (
        len(joined_rows) == len(input_rows)
        and not missing_row_ids
        and clean_count == poisoned_count
        and all(row.get("prediction_scope") == "condition_row_level" for row in joined_rows)
    )
    detection_metrics = _classification_metrics(joined_rows) if condition_predictions_ready else {
        "summary_status": "FAIL",
        "schema_version": SCHEMA_VERSION,
        "metric_scope": "condition_level_detection_preview",
        "real_performance_claimed": False,
        "reason": "Condition-level predictions are incomplete.",
    }
    total_queries = sum(row.get("stage1_query_count", 0) + row.get("stage2_query_count", 0) for row in joined_rows)
    metric_readiness = {
        "summary_status": "PASS" if condition_predictions_ready else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "labels_ready": True,
        "condition_level_predictions_ready": condition_predictions_ready,
        "condition_level_detection_preview_ready": condition_predictions_ready,
        "model_responses_ready": False,
        "paper_performance_metrics_ready": False,
        "auroc_preview_ready": condition_predictions_ready,
        "f1_preview_ready": condition_predictions_ready,
        "asr_ready": False,
        "clean_utility_ready": False,
        "real_performance_claimed": False,
        "reason": "Condition-level detection scores are aligned to labels; ASR and clean utility still require real generated model responses.",
    }
    py_compile = run_py_compile(repo_root, PY_FILES)
    all_stage_commands_passed = all(result["passed"] for result in stage_results) and len(stage_results) == len(command_plan)
    if all_stage_commands_passed and condition_predictions_ready and py_compile["passed"]:
        final_verdict = "Condition-level rerun validated"
        recommendation = "dualscope-first-slice-model-response-metrics"
    elif py_compile["passed"]:
        final_verdict = "Partially validated"
        recommendation = "dualscope-minimal-first-slice-condition-level-rerun-repair"
    else:
        final_verdict = "Not validated"
        recommendation = "dualscope-minimal-first-slice-condition-level-rerun-blocker-closure"

    scope = base_scope(TASK_NAME, output_dir)
    scope.update(
        {
            "input_slice": str(input_slice),
            "input_manifest": str(input_manifest),
            "capability_mode": capability_mode,
            "seed": seed,
            "no_full_matrix": no_full_matrix,
            "preserve_dataset_model_trigger_target_budget_scope": True,
        }
    )
    stage_status = {
        "summary_status": "PASS" if all_stage_commands_passed else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "stage_results": stage_results,
        "all_stage_commands_passed": all_stage_commands_passed,
        "stage3_output_count": len(stage3_rows),
    }
    alignment = {
        "summary_status": "PASS" if condition_predictions_ready else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "input_row_count": len(input_rows),
        "manifest_row_count": manifest.get("row_count"),
        "joined_row_count": len(joined_rows),
        "missing_row_id_count": len(missing_row_ids),
        "missing_row_ids_preview": missing_row_ids[:20],
        "clean_row_count": clean_count,
        "poisoned_triggered_row_count": poisoned_count,
        "prediction_scope": "condition_row_level" if condition_predictions_ready else "incomplete",
    }
    summary = {
        "summary_status": "PASS" if final_verdict != "Not validated" else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "input_row_count": len(input_rows),
        "joined_row_count": len(joined_rows),
        "condition_level_predictions_ready": condition_predictions_ready,
        "condition_level_detection_preview_ready": metric_readiness["condition_level_detection_preview_ready"],
        "model_responses_ready": False,
        "paper_performance_metrics_ready": False,
        "total_query_count": total_queries,
        "average_query_count": round(total_queries / len(joined_rows), 6) if joined_rows else 0,
        "stage_commands_passed": all_stage_commands_passed,
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
        "real_performance_claimed": False,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    verdict = {
        "summary_status": summary["summary_status"],
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_condition_level_rerun_validated__partially_validated__not_validated",
    }

    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_scope.json", scope)
    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_input_manifest.json", manifest)
    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_command_plan.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "commands": command_plan})
    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_stage_status.json", stage_status)
    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_alignment.json", alignment)
    write_jsonl(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_joined_predictions.jsonl", joined_rows)
    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_metric_readiness.json", metric_readiness)
    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_detection_metrics.json", detection_metrics)
    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_summary.json", summary)
    write_json(output_dir / "dualscope_minimal_first_slice_condition_level_rerun_verdict.json", verdict)
    write_json(
        output_dir / "dualscope_minimal_first_slice_condition_level_rerun_next_step_recommendation.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": recommendation,
        },
    )
    write_jsonl(
        output_dir / "dualscope_minimal_first_slice_condition_level_rerun_details.jsonl",
        [
            {"detail_type": "scope", "payload": scope},
            {"detail_type": "stage_status", "payload": stage_status},
            {"detail_type": "alignment", "payload": alignment},
            {"detail_type": "metric_readiness", "payload": metric_readiness},
            {"detail_type": "detection_metrics", "payload": detection_metrics},
            {"detail_type": "py_compile", "payload": py_compile},
        ],
    )
    markdown(
        output_dir / "dualscope_minimal_first_slice_condition_level_rerun_report.md",
        "DualScope Minimal First-Slice Condition-Level Rerun",
        [
            f"- Input rows: `{len(input_rows)}`",
            f"- Joined condition-level predictions: `{len(joined_rows)}`",
            f"- Stage commands passed: `{all_stage_commands_passed}`",
            f"- Condition-level predictions ready: `{condition_predictions_ready}`",
            f"- Detection preview AUROC: `{detection_metrics.get('roc_auc')}`",
            f"- Detection preview F1: `{detection_metrics.get('f1')}`",
            f"- Model responses ready for ASR / clean utility: `False`",
            f"- Paper performance claimed: `False`",
            f"- Training executed: `False`",
            f"- Full matrix executed: `False`",
            f"- Benchmark truth changed: `False`",
            f"- Gate changed: `False`",
            f"- route_c continuation: `False`",
            f"- Final verdict: `{final_verdict}`",
            f"- Recommended next step: `{recommendation}`",
        ],
    )
    return summary
