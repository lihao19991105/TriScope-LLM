"""Package bounded Qwen2.5-7B behavior-shift target smoke results."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscope/qwen2p5-7b-behavior-shift-target-smoke-result-package/v1"
TASK_ID = "dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package"
FINAL_VALIDATED = "Qwen2.5-7B behavior-shift target smoke result package validated"
NEXT_TASK = "dualscope-advbench-small-slice-materialization"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def read_jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_report(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(["# DualScope Behavior-Shift Target Smoke Result Package", "", *lines, ""]) + "\n", encoding="utf-8")


def build_behavior_shift_target_smoke_result_package(
    *,
    response_dir: Path,
    metric_dir: Path,
    output_dir: Path,
    registry_path: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    response_summary = read_json(response_dir / "behavior_shift_target_smoke_summary.json")
    metric_summary = read_json(metric_dir / "summary.json")
    detection_metrics = read_json(metric_dir / "detection_metrics.json")
    asr_metrics = read_json(metric_dir / "asr_metrics.json")
    metric_blockers = read_json(metric_dir / "metric_blockers.json") or read_json(metric_dir / "blockers.json")
    availability = read_json(metric_dir / "available_metrics.json") or read_json(metric_dir / "metric_availability_matrix.json")
    response_rows = read_jsonl_count(response_dir / "behavior_shift_target_smoke_responses.jsonl")

    blockers = list(metric_blockers.get("blockers") or [])
    response_ready = response_rows > 0 and response_summary.get("model_response_fabricated") is not True
    detection_ready = detection_metrics.get("metrics_computed") is True
    asr_ready = asr_metrics.get("metrics_computed") is True
    clean_utility_ready = bool(availability.get("clean_utility_ready"))
    logprob_ready = bool(availability.get("logprob_metrics_ready"))

    final_verdict = FINAL_VALIDATED if response_ready and detection_ready and asr_ready else "Partially validated"
    next_task = NEXT_TASK if final_verdict == FINAL_VALIDATED else "dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package-repair"

    metric_availability_matrix = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PASS" if final_verdict == FINAL_VALIDATED else "PARTIAL",
        "response_rows_ready": response_ready,
        "response_row_count": response_rows,
        "detection_metrics_ready": detection_ready,
        "asr_ready": asr_ready,
        "clean_utility_ready": clean_utility_ready,
        "clean_utility_blocked": not clean_utility_ready,
        "logprob_metrics_ready": logprob_ready,
        "without_logprobs_fallback": bool(response_summary.get("without_logprobs_fallback")),
        "blocked_metrics": blockers,
        "full_matrix_claimed": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
    }
    summary = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": metric_availability_matrix["summary_status"],
        "task_id": TASK_ID,
        "created_at": utc_now(),
        "output_dir": str(output_dir),
        "final_verdict": final_verdict,
        "recommended_next_step": next_task,
        "response_row_count": response_rows,
        "detection_metrics": {
            "auroc": detection_metrics.get("auroc"),
            "auprc": detection_metrics.get("auprc"),
            "f1": detection_metrics.get("f1"),
            "accuracy": detection_metrics.get("accuracy"),
            "precision": detection_metrics.get("precision"),
            "recall": detection_metrics.get("recall"),
            "tpr_at_fpr_1pct": detection_metrics.get("tpr_at_fpr_1pct"),
            "computed": detection_ready,
        },
        "asr": asr_metrics.get("asr"),
        "asr_computed": asr_ready,
        "clean_utility_computed": clean_utility_ready,
        "clean_utility_blocker": "clean_utility_blocked_no_explicit_success_field" if not clean_utility_ready else "",
        "without_logprobs_fallback": bool(response_summary.get("without_logprobs_fallback")),
        "logprob_metrics_computed": logprob_ready,
        "limitations": [
            "Bounded behavior-shift target smoke only; not full trigger-family performance.",
            "Without-logprobs fallback; no token logprob metrics are claimed.",
            "Clean utility remains blocked without explicit utility success fields.",
        ],
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "full_matrix_executed": False,
        "training_executed": False,
        "route_c_199_plus_generated": False,
    }
    verdict = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": summary["summary_status"],
        "final_verdict": final_verdict,
        "recommended_next_step": next_task,
        "single_verdict_policy": "one_of_behavior_shift_target_smoke_result_package_validated__partially_validated__not_validated",
    }
    registry = {
        "task_id": TASK_ID,
        "verdict": final_verdict,
        "source_output_dir": str(output_dir),
        "created_at": summary["created_at"],
        "validated": final_verdict == FINAL_VALIDATED,
        "partially_validated": final_verdict == "Partially validated",
        "next_task": next_task,
        "response_row_count": response_rows,
        "detection_metrics_computed": detection_ready,
        "asr_computed": asr_ready,
        "clean_utility_computed": clean_utility_ready,
        "without_logprobs_fallback": summary["without_logprobs_fallback"],
        "full_matrix_executed": False,
        "model_response_fabricated": False,
        "metrics_fabricated": False,
    }

    write_json(output_dir / "result_package_summary.json", summary)
    write_json(output_dir / "metric_availability_matrix.json", metric_availability_matrix)
    write_json(output_dir / "result_package_verdict.json", verdict)
    write_json(output_dir / "result_package_next_step_recommendation.json", {"recommended_next_step": next_task})
    write_report(
        output_dir / "result_package_report.md",
        [
            f"- Final verdict: `{final_verdict}`",
            f"- Recommended next task: `{next_task}`",
            f"- Behavior-shift response rows: `{response_rows}`",
            f"- Detection AUROC: `{detection_metrics.get('auroc')}`",
            f"- Detection AUPRC: `{detection_metrics.get('auprc')}`",
            f"- Detection F1: `{detection_metrics.get('f1')}`",
            f"- Detection accuracy: `{detection_metrics.get('accuracy')}`",
            f"- ASR: `{asr_metrics.get('asr')}`",
            f"- Clean utility computed: `{clean_utility_ready}`",
            f"- Without-logprobs fallback: `{summary['without_logprobs_fallback']}`",
            f"- Blocked metrics: `{blockers}`",
            "- Full trigger family performance claimed: `False`",
            "- Full matrix executed: `False`",
            "- Metrics fabricated: `False`",
        ],
    )
    write_json(registry_path, registry)
    return summary
