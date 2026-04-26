"""Package Qwen2.5-7B first-slice result artifacts without inflating claims."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscope/qwen2p5-7b-first-slice-result-package/v1"
TASK_NAME = "dualscope-qwen2p5-7b-first-slice-result-package"
FINAL_VALIDATED = "Qwen2.5-7B first-slice result package validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"

RESPONSE_PREFIX = "dualscope_qwen2p5_7b_first_slice_response_generation"
METRIC_PREFIX = "dualscope_qwen2p5_7b_label_aligned_metric_computation"
REPAIR_PREFIX = "dualscope_qwen2p5_7b_metric_computation_repair"

PY_FILES = [
    "src/eval/dualscope_qwen2p5_7b_first_slice_result_package.py",
    "scripts/build_dualscope_qwen2p5_7b_first_slice_result_package.py",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def maybe_read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"summary_status": "MISSING", "path": str(path)}
    return read_json(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_markdown(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([f"# {title}", "", *lines, ""]) + "\n", encoding="utf-8")


def run_py_compile(repo_root: Path) -> dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", *PY_FILES],
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
        "files": PY_FILES,
    }


def _response_path(response_dir: Path, suffix: str) -> Path:
    return response_dir / f"{RESPONSE_PREFIX}_{suffix}"


def _metric_path(metric_dir: Path, suffix: str) -> Path:
    return metric_dir / f"{METRIC_PREFIX}_{suffix}"


def _repair_path(repair_dir: Path, suffix: str) -> Path:
    return repair_dir / f"{REPAIR_PREFIX}_{suffix}"


def _real_response_summary(rows: list[dict[str, Any]], response_summary: dict[str, Any]) -> dict[str, Any]:
    generated_rows = [
        row
        for row in rows
        if row.get("model_response_present") is True
        and row.get("response_generation_status") == "generated"
        and row.get("model_response_fabricated") is not True
        and isinstance(row.get("model_response"), str)
        and row.get("model_response", "").strip()
    ]
    total_generated_tokens = sum(int(row.get("generated_token_count", 0) or 0) for row in generated_rows)
    return {
        "summary_status": "PASS" if len(generated_rows) == len(rows) and rows else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "source_final_verdict": response_summary.get("final_verdict"),
        "row_count": len(rows),
        "real_generated_row_count": len(generated_rows),
        "blocked_row_count": response_summary.get("response_generation_mode", {}).get("row_count_blocked", 0),
        "model_response_fabricated": any(row.get("model_response_fabricated") is True for row in rows),
        "response_backend": response_summary.get("capability_mode", {}).get("response_backend"),
        "model_family": response_summary.get("capability_mode", {}).get("model_family"),
        "model_path": response_summary.get("capability_mode", {}).get("model_path"),
        "without_logprobs": response_summary.get("capability_mode", {}).get("without_logprobs"),
        "with_logprobs": response_summary.get("capability_mode", {}).get("with_logprobs"),
        "total_generated_tokens": total_generated_tokens,
        "average_generated_tokens": round(total_generated_tokens / len(generated_rows), 6) if generated_rows else None,
        "first_slice_only": True,
    }


def _real_metric_package(
    detection: dict[str, Any],
    asr: dict[str, Any],
    clean_utility: dict[str, Any],
    metric_summary: dict[str, Any],
    repair_real_metrics: dict[str, Any],
) -> dict[str, Any]:
    detection_reportable = detection.get("summary_status") == "PASS" and detection.get("metrics_computed") is True
    asr_reportable = asr.get("summary_status") == "PASS" and asr.get("metrics_computed") is True
    utility_reportable = clean_utility.get("summary_status") == "PASS" and clean_utility.get("metrics_computed") is True
    return {
        "summary_status": "PARTIAL" if detection_reportable or asr_reportable else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "metric_scope": "qwen2p5_7b_first_slice_real_artifact_metrics_only",
        "source_metric_final_verdict": metric_summary.get("final_verdict"),
        "source_repair_status": repair_real_metrics.get("summary_status", "MISSING"),
        "aligned_metric_row_count": metric_summary.get("aligned_metric_row_count", 0),
        "detection_metrics": {
            "reportable": detection_reportable,
            "row_count": detection.get("row_count") if detection_reportable else None,
            "positive_label_count": detection.get("positive_label_count") if detection_reportable else None,
            "negative_label_count": detection.get("negative_label_count") if detection_reportable else None,
            "auroc": detection.get("auroc") if detection_reportable else None,
            "auprc": detection.get("auprc") if detection_reportable else None,
            "tpr_at_fpr_1pct": detection.get("tpr_at_fpr_1pct") if detection_reportable else None,
            "threshold": detection.get("threshold") if detection_reportable else None,
            "tp": detection.get("tp") if detection_reportable else None,
            "fp": detection.get("fp") if detection_reportable else None,
            "tn": detection.get("tn") if detection_reportable else None,
            "fn": detection.get("fn") if detection_reportable else None,
            "precision": detection.get("precision") if detection_reportable else None,
            "recall": detection.get("recall") if detection_reportable else None,
            "f1": detection.get("f1") if detection_reportable else None,
            "accuracy": detection.get("accuracy") if detection_reportable else None,
        },
        "asr": {
            "reportable": asr_reportable,
            "eligible_row_count": asr.get("eligible_row_count") if asr_reportable else None,
            "target_match_success_count": asr.get("target_match_success_count") if asr_reportable else None,
            "asr": asr.get("asr") if asr_reportable else None,
        },
        "clean_utility": {
            "reportable": utility_reportable,
            "eligible_row_count": clean_utility.get("eligible_row_count", 0),
            "clean_utility": clean_utility.get("clean_utility") if utility_reportable else None,
        },
        "metrics_computed_from_placeholders": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
        "full_paper_performance": False,
    }


def _cost_notes(rows: list[dict[str, Any]], runtime: dict[str, Any], response_summary: dict[str, Any]) -> dict[str, Any]:
    query_count = len(rows)
    elapsed = runtime.get("generation_elapsed_seconds")
    total_tokens = sum(int(row.get("generated_token_count", 0) or 0) for row in rows)
    return {
        "summary_status": "PASS" if query_count else "MISSING",
        "schema_version": SCHEMA_VERSION,
        "query_count_observed": query_count,
        "generated_token_count_observed": total_tokens,
        "generation_elapsed_seconds_observed": elapsed,
        "average_seconds_per_query_observed": round(float(elapsed) / query_count, 6)
        if isinstance(elapsed, (int, float)) and query_count
        else None,
        "batch_size": response_summary.get("capability_mode", {}).get("batch_size"),
        "low_memory": response_summary.get("capability_mode", {}).get("low_memory"),
        "used_4bit": response_summary.get("fallback_flags", {}).get("used_4bit"),
        "cuda_visible_devices": response_summary.get("capability_mode", {}).get("cuda_visible_devices"),
        "selected_device": runtime.get("selected_device"),
        "load_strategy": runtime.get("load_strategy"),
        "min_free_gpu_memory_mib": response_summary.get("capability_mode", {}).get("min_free_gpu_memory_mib"),
        "cost_is_first_slice_only": True,
        "not_projected_to_full_matrix": True,
    }


def build_qwen2p5_7b_first_slice_result_package(
    *,
    response_dir: Path,
    metric_dir: Path,
    repair_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)

    response_summary = maybe_read_json(_response_path(response_dir, "summary.json"))
    response_runtime = maybe_read_json(_response_path(response_dir, "runtime.json"))
    response_capability = maybe_read_json(_response_path(response_dir, "capability_mode.json"))
    response_rows = read_jsonl(_response_path(response_dir, "rows.jsonl"))

    metric_summary = maybe_read_json(_metric_path(metric_dir, "summary.json"))
    metric_readiness = maybe_read_json(_metric_path(metric_dir, "metric_readiness.json"))
    detection_metrics = maybe_read_json(_metric_path(metric_dir, "detection_metrics.json"))
    asr_metrics = maybe_read_json(_metric_path(metric_dir, "asr_metrics.json"))
    clean_utility_metrics = maybe_read_json(_metric_path(metric_dir, "clean_utility_metrics.json"))
    metric_blockers = maybe_read_json(_metric_path(metric_dir, "blockers.json"))

    repair_summary = maybe_read_json(_repair_path(repair_dir, "summary.json"))
    repair_real_metrics = maybe_read_json(_repair_path(repair_dir, "real_metric_summary.json"))
    repair_limitations = maybe_read_json(_repair_path(repair_dir, "limitations.json"))

    py_compile = run_py_compile(repo_root)
    response_evidence = _real_response_summary(response_rows, response_summary)
    real_metrics = _real_metric_package(
        detection=detection_metrics,
        asr=asr_metrics,
        clean_utility=clean_utility_metrics,
        metric_summary=metric_summary,
        repair_real_metrics=repair_real_metrics,
    )
    cost_notes = _cost_notes(response_rows, response_runtime, response_summary)

    projected_metrics = {
        "summary_status": "NOT_AVAILABLE",
        "schema_version": SCHEMA_VERSION,
        "projected_metrics_available": False,
        "projected_metrics": [],
        "reason": "No projected full-matrix or full-paper metrics are produced by this package.",
    }
    placeholders = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "placeholder_metrics_presented_as_real": False,
        "placeholder_metric_values": [],
        "notes": [
            "Full-paper performance placeholders are intentionally absent.",
            "Clean utility is blocked rather than filled with a placeholder.",
            "Logprob-dependent confidence metrics are unavailable in this response pass.",
        ],
    }
    blockers = {
        "summary_status": "BLOCKED" if metric_blockers.get("blockers") else "PASS",
        "schema_version": SCHEMA_VERSION,
        "blockers": metric_blockers.get("blockers", []),
        "clean_utility_blocker": clean_utility_metrics.get("reason") if clean_utility_metrics.get("summary_status") == "BLOCKED" else "",
        "response_blockers": response_summary.get("blockers", []),
        "limitations": repair_limitations.get("items", []),
    }
    asr_readiness = {
        "summary_status": "PASS" if real_metrics["asr"]["reportable"] else "BLOCKED",
        "schema_version": SCHEMA_VERSION,
        "ready": real_metrics["asr"]["reportable"],
        "eligible_row_count": real_metrics["asr"]["eligible_row_count"],
        "target_match_success_count": real_metrics["asr"]["target_match_success_count"],
        "asr": real_metrics["asr"]["asr"],
        "source": str(_metric_path(metric_dir, "asr_metrics.json")),
    }
    clean_utility_readiness = {
        "summary_status": "PASS" if real_metrics["clean_utility"]["reportable"] else "BLOCKED",
        "schema_version": SCHEMA_VERSION,
        "ready": real_metrics["clean_utility"]["reportable"],
        "eligible_row_count": clean_utility_metrics.get("eligible_row_count", 0),
        "reason": clean_utility_metrics.get("reason", "Clean utility is unavailable."),
        "supported_utility_success_fields": clean_utility_metrics.get("supported_utility_success_fields", []),
        "missing_utility_success_row_ids": clean_utility_metrics.get("missing_utility_success_row_ids", []),
    }

    source_artifacts_ready = (
        response_summary.get("final_verdict") == "Qwen2.5-7B first-slice response generation validated"
        and metric_summary.get("final_verdict") in {"Partially validated", "Qwen2.5-7B label-aligned metrics validated"}
        and response_evidence["summary_status"] == "PASS"
        and real_metrics["detection_metrics"]["reportable"] is True
        and real_metrics["asr"]["reportable"] is True
    )
    if source_artifacts_ready and py_compile["passed"]:
        final_verdict = FINAL_VALIDATED if clean_utility_readiness["ready"] else FINAL_PARTIAL
    elif py_compile["passed"]:
        final_verdict = FINAL_PARTIAL if response_evidence["summary_status"] == "PASS" else FINAL_NOT_VALIDATED
    else:
        final_verdict = FINAL_NOT_VALIDATED

    summary_status = "PASS" if final_verdict == FINAL_VALIDATED else "PARTIAL" if final_verdict == FINAL_PARTIAL else "FAIL"
    recommended_next_step = (
        "dualscope-qwen2p5-7b-clean-utility-scoring"
        if clean_utility_readiness["ready"] is False and final_verdict != FINAL_NOT_VALIDATED
        else "dualscope-qwen2p5-7b-next-experiment-readiness"
        if final_verdict == FINAL_VALIDATED
        else "dualscope-qwen2p5-7b-first-slice-result-package-repair"
    )
    summary = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "created_at": utc_now(),
        "seed": seed,
        "final_verdict": final_verdict,
        "recommended_next_step": recommended_next_step,
        "response_generation_final_verdict": response_summary.get("final_verdict"),
        "metric_computation_final_verdict": metric_summary.get("final_verdict"),
        "metric_repair_final_verdict": repair_summary.get("final_verdict"),
        "real_response_row_count": response_evidence["real_generated_row_count"],
        "aligned_metric_row_count": real_metrics["aligned_metric_row_count"],
        "detection_metrics_reportable": real_metrics["detection_metrics"]["reportable"],
        "asr_reportable": real_metrics["asr"]["reportable"],
        "clean_utility_reportable": real_metrics["clean_utility"]["reportable"],
        "projected_metrics_reportable": False,
        "placeholder_metrics_presented_as_real": False,
        "with_logprobs": response_capability.get("with_logprobs"),
        "without_logprobs": response_capability.get("without_logprobs"),
        "full_paper_performance_claimed": False,
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
    }

    report_lines = [
        f"- Final verdict: `{final_verdict}`",
        f"- Response-generation verdict: `{response_summary.get('final_verdict')}`",
        f"- Metric-computation verdict: `{metric_summary.get('final_verdict')}`",
        f"- Real Qwen2.5-7B response rows: `{response_evidence['real_generated_row_count']}`",
        f"- Detection metrics reportable: `{real_metrics['detection_metrics']['reportable']}`",
        f"- AUROC: `{real_metrics['detection_metrics']['auroc']}`",
        f"- F1: `{real_metrics['detection_metrics']['f1']}`",
        f"- ASR reportable: `{real_metrics['asr']['reportable']}`",
        f"- ASR: `{real_metrics['asr']['asr']}`",
        f"- Clean utility reportable: `{real_metrics['clean_utility']['reportable']}`",
        f"- Projected metrics reportable: `False`",
        f"- Placeholder metrics presented as real: `False`",
        f"- Capability mode: `without_logprobs={response_capability.get('without_logprobs')}`, `with_logprobs={response_capability.get('with_logprobs')}`",
        f"- Observed query count: `{cost_notes['query_count_observed']}`",
        f"- Observed generation elapsed seconds: `{cost_notes['generation_elapsed_seconds_observed']}`",
        "- This is a Qwen2.5-7B first-slice package only; it is not full-paper performance.",
    ]

    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_response_evidence.json", response_evidence)
    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_real_metrics.json", real_metrics)
    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_projected_metrics.json", projected_metrics)
    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_placeholders.json", placeholders)
    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_blockers.json", blockers)
    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_asr_readiness.json", asr_readiness)
    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_clean_utility_readiness.json", clean_utility_readiness)
    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_cost_notes.json", cost_notes)
    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_py_compile.json", py_compile)
    write_json(output_dir / f"{RESPONSE_PREFIX}_result_package_summary.json", summary)
    write_markdown(output_dir / f"{RESPONSE_PREFIX}_result_package_report.md", "DualScope Qwen2.5-7B First-Slice Result Package", report_lines)
    write_json(
        output_dir / f"{RESPONSE_PREFIX}_result_package_verdict.json",
        {
            "summary_status": summary_status,
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "single_verdict_policy": "one_of_qwen2p5_7b_first_slice_result_package_validated__partially_validated__not_validated",
        },
    )
    write_json(
        output_dir / f"{RESPONSE_PREFIX}_result_package_next_step_recommendation.json",
        {
            "summary_status": summary_status,
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": recommended_next_step,
        },
    )
    write_jsonl(
        output_dir / f"{RESPONSE_PREFIX}_result_package_sources.jsonl",
        [
            {"source_type": "response_generation", "path": str(response_dir), "final_verdict": response_summary.get("final_verdict")},
            {"source_type": "label_aligned_metric_computation", "path": str(metric_dir), "final_verdict": metric_summary.get("final_verdict")},
            {"source_type": "metric_computation_repair", "path": str(repair_dir), "final_verdict": repair_summary.get("final_verdict")},
        ],
    )
    return summary
