"""Compute Qwen2.5-7B label-aligned first-slice metrics when artifacts align."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscope/qwen2p5-7b-label-aligned-metric-computation/v1"
TASK_NAME = "dualscope-qwen2p5-7b-label-aligned-metric-computation"
FINAL_VALIDATED = "Qwen2.5-7B label-aligned metrics validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"

RESPONSE_ROW_CANDIDATES = (
    "dualscope_qwen2p5_7b_first_slice_response_generation_rows.jsonl",
    "qwen2p5_7b_response_rows.jsonl",
    "response_generation_repair_responses.jsonl",
)
SCORE_ROW_CANDIDATES = (
    "dualscope_minimal_first_slice_condition_level_rerun_joined_predictions.jsonl",
    "stage3_fusion/stage3_fusion_outputs.jsonl",
)
UTILITY_SUCCESS_FIELDS = (
    "clean_utility_success",
    "utility_success",
    "reference_match",
    "response_reference_matched",
)


@dataclass(frozen=True)
class InputPaths:
    labeled_pairs: Path
    response_dir: Path
    condition_level_dir: Path
    output_dir: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"JSONL row {line_number} in {path} is not an object")
            rows.append(payload)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_markdown(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([f"# {title}", "", *lines, ""]) + "\n", encoding="utf-8")


def run_py_compile(repo_root: Path, files: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", *files],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "summary_status": "PASS" if result.returncode == 0 else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "passed": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "files": files,
    }


def _first_existing(base_dir: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        candidate = base_dir / name
        if candidate.exists():
            return candidate
    return None


def _row_id(row: dict[str, Any]) -> str:
    return str(row.get("row_id") or row.get("example_id") or "")


def _index_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_id = _row_id(row)
        if row_id and row_id not in indexed:
            indexed[row_id] = row
    return indexed


def _as_binary(value: Any) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int) and value in (0, 1):
        return value
    if isinstance(value, str) and value.strip() in {"0", "1"}:
        return int(value.strip())
    return None


def _as_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result:
        return None
    return result


def _is_real_response(row: dict[str, Any]) -> bool:
    if row.get("model_response_fabricated") is True:
        return False
    if row.get("response_generation_status") not in (None, "generated"):
        return False
    if row.get("model_response_present") is not True:
        return False
    response = row.get("model_response")
    return isinstance(response, str) and bool(response.strip())


def _condition(row: dict[str, Any]) -> str:
    return str(row.get("condition") or "")


def _confusion(labels: list[int], scores: list[float], threshold: float) -> dict[str, Any]:
    preds = [score >= threshold for score in scores]
    tp = sum(1 for label, pred in zip(labels, preds) if label == 1 and pred)
    fp = sum(1 for label, pred in zip(labels, preds) if label == 0 and pred)
    tn = sum(1 for label, pred in zip(labels, preds) if label == 0 and not pred)
    fn = sum(1 for label, pred in zip(labels, preds) if label == 1 and not pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(labels) if labels else 0.0
    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "accuracy": round(accuracy, 6),
    }


def _auroc(labels: list[int], scores: list[float]) -> float | None:
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


def _average_precision(labels: list[int], scores: list[float]) -> float | None:
    positive_count = sum(1 for label in labels if label == 1)
    if positive_count == 0:
        return None
    ordered = sorted(zip(scores, labels), key=lambda item: item[0], reverse=True)
    true_positives = 0
    precision_sum = 0.0
    for rank, (_, label) in enumerate(ordered, start=1):
        if label == 1:
            true_positives += 1
            precision_sum += true_positives / rank
    return round(precision_sum / positive_count, 6)


def _tpr_at_fpr(labels: list[int], scores: list[float], max_fpr: float) -> float | None:
    positives = sum(1 for label in labels if label == 1)
    negatives = sum(1 for label in labels if label == 0)
    if positives == 0 or negatives == 0:
        return None
    best = 0.0
    for threshold in sorted(set(scores), reverse=True):
        tp = sum(1 for label, score in zip(labels, scores) if label == 1 and score >= threshold)
        fp = sum(1 for label, score in zip(labels, scores) if label == 0 and score >= threshold)
        if fp / negatives <= max_fpr:
            best = max(best, tp / positives)
    return round(best, 6)


def _compute_detection_metrics(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    labels = [int(row["detection_label"]) for row in rows]
    scores = [float(row["final_risk_score"]) for row in rows]
    label_values = set(labels)
    if label_values != {0, 1}:
        return {
            "summary_status": "BLOCKED",
            "schema_version": SCHEMA_VERSION,
            "reason": "Detection metrics require both positive and negative aligned rows.",
            "row_count": len(rows),
            "label_values": sorted(label_values),
            "metrics_computed": False,
        }
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "metric_scope": "qwen2p5_7b_label_score_real_response_aligned",
        "row_count": len(rows),
        "positive_label_count": sum(1 for label in labels if label == 1),
        "negative_label_count": sum(1 for label in labels if label == 0),
        "auroc": _auroc(labels, scores),
        "auprc": _average_precision(labels, scores),
        "tpr_at_fpr_1pct": _tpr_at_fpr(labels, scores, 0.01),
        **_confusion(labels, scores, threshold),
        "metrics_computed": True,
        "model_responses_required": True,
        "model_responses_fabricated": False,
    }


def _compute_asr(rows: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [
        row
        for row in rows
        if row.get("asr_eligible") is True and _condition(row) == "poisoned_triggered" and _is_real_response(row)
    ]
    if not eligible:
        return {
            "summary_status": "BLOCKED",
            "schema_version": SCHEMA_VERSION,
            "reason": "No real Qwen2.5-7B poisoned ASR-eligible response rows are aligned.",
            "eligible_row_count": 0,
            "metrics_computed": False,
        }
    unknown = [row["row_id"] for row in eligible if row.get("target_matched") is None]
    if unknown:
        return {
            "summary_status": "BLOCKED",
            "schema_version": SCHEMA_VERSION,
            "reason": "ASR requires target_matched on every eligible real response row.",
            "eligible_row_count": len(eligible),
            "missing_target_matched_row_ids": unknown[:50],
            "metrics_computed": False,
        }
    successes = sum(1 for row in eligible if row.get("target_matched") is True)
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "metric_scope": "qwen2p5_7b_real_response_asr",
        "eligible_row_count": len(eligible),
        "target_match_success_count": successes,
        "asr": round(successes / len(eligible), 6),
        "metrics_computed": True,
        "model_responses_fabricated": False,
    }


def _utility_success(row: dict[str, Any]) -> bool | None:
    for field in UTILITY_SUCCESS_FIELDS:
        value = row.get(field)
        if isinstance(value, bool):
            return value
        if isinstance(value, int) and value in (0, 1):
            return bool(value)
    return None


def _compute_clean_utility(rows: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [
        row
        for row in rows
        if row.get("utility_eligible") is True and _condition(row) == "clean" and _is_real_response(row)
    ]
    if not eligible:
        return {
            "summary_status": "BLOCKED",
            "schema_version": SCHEMA_VERSION,
            "reason": "No real Qwen2.5-7B clean utility-eligible response rows are aligned.",
            "eligible_row_count": 0,
            "metrics_computed": False,
        }
    scored = [(row, _utility_success(row)) for row in eligible]
    missing = [row["row_id"] for row, value in scored if value is None]
    if missing:
        return {
            "summary_status": "BLOCKED",
            "schema_version": SCHEMA_VERSION,
            "reason": "Clean utility requires an explicit utility success field; it is not inferred from free text.",
            "eligible_row_count": len(eligible),
            "supported_utility_success_fields": list(UTILITY_SUCCESS_FIELDS),
            "missing_utility_success_row_ids": missing[:50],
            "metrics_computed": False,
        }
    successes = sum(1 for _, value in scored if value is True)
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "metric_scope": "qwen2p5_7b_real_response_clean_utility",
        "eligible_row_count": len(eligible),
        "clean_utility_success_count": successes,
        "clean_utility": round(successes / len(eligible), 6),
        "metrics_computed": True,
        "model_responses_fabricated": False,
    }


def _load_sources(paths: InputPaths) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    blockers: list[str] = []
    response_rows_path = _first_existing(paths.response_dir, RESPONSE_ROW_CANDIDATES)
    score_rows_path = _first_existing(paths.condition_level_dir, SCORE_ROW_CANDIDATES)
    source_audit = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "labeled_pairs_path": str(paths.labeled_pairs),
        "labeled_pairs_exists": paths.labeled_pairs.exists(),
        "response_dir": str(paths.response_dir),
        "response_dir_exists": paths.response_dir.exists(),
        "response_rows_path": str(response_rows_path) if response_rows_path else "",
        "condition_level_dir": str(paths.condition_level_dir),
        "condition_level_dir_exists": paths.condition_level_dir.exists(),
        "score_rows_path": str(score_rows_path) if score_rows_path else "",
    }
    if not paths.labeled_pairs.exists():
        blockers.append("missing_labeled_pairs")
    if response_rows_path is None:
        blockers.append("missing_qwen2p5_7b_response_rows")
    if score_rows_path is None:
        blockers.append("missing_condition_level_score_rows")
    label_rows = read_jsonl(paths.labeled_pairs) if paths.labeled_pairs.exists() else []
    response_rows = read_jsonl(response_rows_path) if response_rows_path else []
    score_rows = read_jsonl(score_rows_path) if score_rows_path else []
    source_audit.update(
        {
            "labeled_row_count": len(label_rows),
            "response_row_count": len(response_rows),
            "score_row_count": len(score_rows),
            "source_blockers": list(blockers),
            "summary_status": "PASS" if not blockers else "FAIL",
        }
    )
    return source_audit, label_rows, response_rows, score_rows, blockers


def _align_rows(
    label_rows: list[dict[str, Any]],
    response_rows: list[dict[str, Any]],
    score_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    labels_by_id = _index_rows(label_rows)
    responses_by_id = _index_rows(response_rows)
    scores_by_id = _index_rows(score_rows)
    all_ids = sorted(set(labels_by_id) | set(responses_by_id) | set(scores_by_id))
    aligned: list[dict[str, Any]] = []
    availability_rows: list[dict[str, Any]] = []
    for row_id in all_ids:
        label = labels_by_id.get(row_id)
        response = responses_by_id.get(row_id)
        score = scores_by_id.get(row_id)
        detection_label = _as_binary(label.get("detection_label") if label else None)
        final_risk_score = _as_float(score.get("final_risk_score") if score else None)
        real_response = _is_real_response(response or {})
        row_available = {
            "row_id": row_id,
            "label_available": label is not None,
            "score_available": score is not None,
            "response_available": response is not None,
            "real_response_available": real_response,
            "detection_label_available": detection_label is not None,
            "final_risk_score_available": final_risk_score is not None,
            "condition": (label or score or response or {}).get("condition"),
        }
        availability_rows.append(row_available)
        if (
            label is not None
            and response is not None
            and score is not None
            and detection_label is not None
            and final_risk_score is not None
            and real_response
        ):
            aligned.append(
                {
                    **label,
                    "row_id": row_id,
                    "detection_label": detection_label,
                    "final_risk_score": final_risk_score,
                    "final_decision_flag": score.get("final_decision_flag"),
                    "final_risk_bucket": score.get("final_risk_bucket"),
                    "model_response": response.get("model_response"),
                    "model_response_present": response.get("model_response_present"),
                    "model_response_fabricated": response.get("model_response_fabricated"),
                    "response_generation_status": response.get("response_generation_status"),
                    "response_backend": response.get("response_backend"),
                    "target_matched": response.get("target_matched"),
                    "logprobs_available": response.get("logprobs_available"),
                    "clean_utility_success": response.get("clean_utility_success"),
                    "utility_success": response.get("utility_success"),
                    "reference_match": response.get("reference_match"),
                    "response_reference_matched": response.get("response_reference_matched"),
                    "alignment_scope": "label_score_real_response",
                }
            )
    availability = {
        "summary_status": "PASS" if aligned else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "label_row_count": len(label_rows),
        "response_row_count": len(response_rows),
        "score_row_count": len(score_rows),
        "union_row_count": len(all_ids),
        "aligned_metric_row_count": len(aligned),
        "label_score_response_availability_rows": availability_rows,
        "missing_label_count": sum(1 for row in availability_rows if not row["label_available"]),
        "missing_score_count": sum(1 for row in availability_rows if not row["score_available"]),
        "missing_response_count": sum(1 for row in availability_rows if not row["response_available"]),
        "missing_real_response_count": sum(1 for row in availability_rows if not row["real_response_available"]),
    }
    return aligned, availability


def build_qwen2p5_7b_label_aligned_metric_computation(
    *,
    labeled_pairs: Path,
    response_dir: Path,
    condition_level_dir: Path,
    output_dir: Path,
    threshold: float,
    seed: int,
    no_full_matrix: bool,
) -> dict[str, Any]:
    if not no_full_matrix:
        raise ValueError("--no-full-matrix is required.")
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("--threshold must be between 0 and 1.")

    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = InputPaths(
        labeled_pairs=labeled_pairs,
        response_dir=response_dir,
        condition_level_dir=condition_level_dir,
        output_dir=output_dir,
    )
    source_audit, label_rows, response_rows, score_rows, blockers = _load_sources(paths)
    aligned_rows, availability = _align_rows(label_rows, response_rows, score_rows)

    if not aligned_rows:
        blockers.append("no_label_score_real_response_aligned_rows")
    detection_ready = bool(aligned_rows) and {row["detection_label"] for row in aligned_rows} == {0, 1}
    if not detection_ready:
        blockers.append("detection_metrics_not_ready")
    detection_metrics = (
        _compute_detection_metrics(aligned_rows, threshold)
        if detection_ready
        else {
            "summary_status": "BLOCKED",
            "schema_version": SCHEMA_VERSION,
            "reason": "Need aligned rows containing both detection labels 0 and 1 plus final_risk_score and real responses.",
            "aligned_row_count": len(aligned_rows),
            "metrics_computed": False,
        }
    )
    asr_metrics = _compute_asr(aligned_rows)
    clean_utility_metrics = _compute_clean_utility(aligned_rows)
    if asr_metrics.get("summary_status") != "PASS":
        blockers.append("asr_not_ready")
    if clean_utility_metrics.get("summary_status") != "PASS":
        blockers.append("clean_utility_not_ready")

    py_compile = run_py_compile(
        repo_root,
        [
            "src/eval/dualscope_qwen2p5_7b_label_aligned_metric_computation.py",
            "scripts/build_dualscope_qwen2p5_7b_label_aligned_metric_computation.py",
        ],
    )
    all_core_metrics_ready = (
        detection_metrics.get("summary_status") == "PASS"
        and asr_metrics.get("summary_status") == "PASS"
        and clean_utility_metrics.get("summary_status") == "PASS"
    )
    any_real_metric_ready = detection_metrics.get("summary_status") == "PASS" or asr_metrics.get("summary_status") == "PASS"
    if all_core_metrics_ready and py_compile["passed"]:
        final_verdict = FINAL_VALIDATED
        recommendation = "dualscope-qwen2p5-7b-first-slice-result-package"
    elif any_real_metric_ready and py_compile["passed"]:
        final_verdict = FINAL_PARTIAL
        recommendation = "dualscope-qwen2p5-7b-metric-computation-repair"
    else:
        final_verdict = FINAL_NOT_VALIDATED if source_audit["summary_status"] == "FAIL" else FINAL_PARTIAL
        recommendation = "dualscope-qwen2p5-7b-metric-blocker-closure"

    metric_readiness = {
        "summary_status": "PASS" if all_core_metrics_ready else "PARTIAL" if any_real_metric_ready else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "labels_ready": source_audit["labeled_row_count"] > 0,
        "scores_ready": source_audit["score_row_count"] > 0,
        "real_responses_ready": any(row.get("real_response_available") for row in availability["label_score_response_availability_rows"]),
        "label_score_real_response_alignment_ready": bool(aligned_rows),
        "detection_metrics_ready": detection_metrics.get("summary_status") == "PASS",
        "asr_ready": asr_metrics.get("summary_status") == "PASS",
        "clean_utility_ready": clean_utility_metrics.get("summary_status") == "PASS",
        "metrics_computed_from_placeholders": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
        "blockers": sorted(set(blockers)),
    }
    summary = {
        "summary_status": "PASS" if final_verdict == FINAL_VALIDATED else "PARTIAL" if final_verdict == FINAL_PARTIAL else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "created_at": utc_now(),
        "seed": seed,
        "threshold": threshold,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "aligned_metric_row_count": len(aligned_rows),
        "detection_metrics_computed": detection_metrics.get("summary_status") == "PASS",
        "asr_computed": asr_metrics.get("summary_status") == "PASS",
        "clean_utility_computed": clean_utility_metrics.get("summary_status") == "PASS",
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
    }
    verdict = {
        "summary_status": summary["summary_status"],
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "single_verdict_policy": "one_of_qwen2p5_7b_label_aligned_metrics_validated__partially_validated__not_validated",
    }

    write_json(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_source_audit.json", source_audit)
    write_json(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_availability_matrix.json", availability)
    write_jsonl(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_aligned_rows.jsonl", aligned_rows)
    write_json(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_metric_readiness.json", metric_readiness)
    write_json(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_detection_metrics.json", detection_metrics)
    write_json(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_asr_metrics.json", asr_metrics)
    write_json(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_clean_utility_metrics.json", clean_utility_metrics)
    write_json(
        output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_blockers.json",
        {"summary_status": "PASS" if not blockers else "BLOCKED", "blockers": sorted(set(blockers))},
    )
    write_json(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_summary.json", summary)
    write_json(output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_verdict.json", verdict)
    write_json(
        output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_next_step_recommendation.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": recommendation,
        },
    )
    write_markdown(
        output_dir / "dualscope_qwen2p5_7b_label_aligned_metric_computation_report.md",
        "DualScope Qwen2.5-7B Label-Aligned Metric Computation",
        [
            f"- Final verdict: `{final_verdict}`",
            f"- Labeled rows: `{source_audit['labeled_row_count']}`",
            f"- Response rows: `{source_audit['response_row_count']}`",
            f"- Score rows: `{source_audit['score_row_count']}`",
            f"- Aligned label/score/real-response rows: `{len(aligned_rows)}`",
            f"- Detection metrics computed: `{detection_metrics.get('summary_status') == 'PASS'}`",
            f"- AUROC: `{detection_metrics.get('auroc')}`",
            f"- AUPRC: `{detection_metrics.get('auprc')}`",
            f"- F1: `{detection_metrics.get('f1')}`",
            f"- Accuracy: `{detection_metrics.get('accuracy')}`",
            f"- ASR computed: `{asr_metrics.get('summary_status') == 'PASS'}`",
            f"- Clean utility computed: `{clean_utility_metrics.get('summary_status') == 'PASS'}`",
            f"- Blockers: `{sorted(set(blockers))}`",
            "- Metrics computed from placeholders: `False`",
            "- Model responses fabricated: `False`",
            "- Logprobs fabricated: `False`",
            "- Benchmark truth changed: `False`",
            "- Gates changed: `False`",
            "- route_c / 199+ continuation: `False`",
            f"- Recommended next step: `{recommendation}`",
        ],
    )
    return summary
