"""Package bounded AdvBench small-slice status without fabricating metrics."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscope/advbench-small-slice-result-package/v1"
TASK_ID = "dualscope-advbench-small-slice-result-package"
FINAL_VALIDATED = "AdvBench small-slice result package validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"
NEXT_WHEN_BLOCKED = "dualscope-advbench-small-slice-response-generation-blocker-closure"
NEXT_WHEN_VALIDATED = "dualscope-jbb-small-slice-materialization"


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


def write_markdown(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _blocked_metric_rows(available_metrics: dict[str, Any], metric_blockers: dict[str, Any]) -> list[dict[str, Any]]:
    refusal = available_metrics.get("refusal_rate_and_safety_behavior_proxy", {})
    target = available_metrics.get("target_behavior_status", {})
    detection = available_metrics.get("label_score_aligned_detection_metrics", {})
    unsupported = available_metrics.get("unsupported_or_blocked_performance_metrics", {})

    return [
        {
            "metric": "refusal_rate",
            "status": "not_applicable" if refusal.get("summary_status") != "PASS" else "available",
            "reportable": refusal.get("summary_status") == "PASS",
            "value": refusal.get("refusal_rate"),
            "blocker": refusal.get("reason", ""),
        },
        {
            "metric": "safety_behavior_proxy",
            "status": "not_applicable"
            if refusal.get("summary_status") != "PASS"
            else refusal.get("safety_behavior_proxy", {}).get("status", "available"),
            "reportable": refusal.get("summary_status") == "PASS",
            "value": refusal.get("safety_behavior_proxy", {}).get("safe_refusal_proxy_rate"),
            "blocker": refusal.get("reason", ""),
        },
        {
            "metric": "target_behavior_status",
            "status": "not_applicable" if target.get("summary_status") != "PASS" else "available",
            "reportable": target.get("summary_status") == "PASS",
            "value": target.get("target_match_rate"),
            "blocker": target.get("reason", ""),
        },
        {
            "metric": "label_score_aligned_detection_metrics",
            "status": "not_applicable" if detection.get("summary_status") != "PASS" else "available",
            "reportable": detection.get("summary_status") == "PASS" and detection.get("metrics_computed") is True,
            "value": {
                "auroc": detection.get("auroc"),
                "f1": detection.get("f1"),
                "precision": detection.get("precision"),
                "recall": detection.get("recall"),
                "tpr_at_fpr_1pct": detection.get("tpr_at_fpr_1pct"),
            },
            "blocker": detection.get("reason", ""),
        },
        {
            "metric": "asr",
            "status": unsupported.get("asr", metric_blockers.get("asr", {})).get("status", "not_applicable"),
            "reportable": False,
            "value": None,
            "blocker": unsupported.get("asr", metric_blockers.get("asr", {})).get("reason", ""),
        },
        {
            "metric": "clean_utility",
            "status": unsupported.get("clean_utility", metric_blockers.get("clean_utility", {})).get(
                "status", "not_applicable"
            ),
            "reportable": False,
            "value": None,
            "blocker": unsupported.get("clean_utility", metric_blockers.get("clean_utility", {})).get("reason", ""),
        },
        {
            "metric": "with_logprobs_metrics",
            "status": unsupported.get("with_logprobs_metrics", metric_blockers.get("with_logprobs_metrics", {})).get(
                "status", "not_applicable"
            ),
            "reportable": False,
            "value": None,
            "blocker": unsupported.get("with_logprobs_metrics", metric_blockers.get("with_logprobs_metrics", {})).get(
                "reason", "No token logprobs are present in bounded artifacts."
            ),
        },
        {
            "metric": "full_paper_performance",
            "status": unsupported.get("full_paper_performance", {}).get("status", "not_applicable"),
            "reportable": False,
            "value": None,
            "blocker": unsupported.get("full_paper_performance", {}).get(
                "reason", "This is a bounded small-slice package, not full-matrix evidence."
            ),
        },
    ]


def build_advbench_small_slice_result_package(
    *,
    metric_dir: Path,
    response_dir: Path,
    materialization_registry: Path,
    response_generation_registry: Path,
    response_generation_repair_registry: Path,
    metric_registry: Path,
    output_dir: Path,
    registry_path: Path,
    docs_path: Path,
    seed: int,
) -> dict[str, Any]:
    created_at = utc_now()
    output_dir.mkdir(parents=True, exist_ok=True)

    materialization = read_json(materialization_registry)
    response_registry = read_json(response_generation_registry)
    response_repair_registry = read_json(response_generation_repair_registry)
    metric_registry_payload = read_json(metric_registry)
    response_summary = read_json(response_dir / "advbench_small_slice_response_generation_summary.json")
    metric_summary = read_json(metric_dir / "metric_summary.json")
    available_metrics = read_json(metric_dir / "available_metrics.json")
    metric_blockers = read_json(metric_dir / "metric_blockers.json")
    readiness_matrix = read_json(metric_dir / "readiness_matrix.json")
    response_row_count = read_jsonl_count(response_dir / "advbench_small_slice_responses.jsonl")

    real_response_count = int(metric_summary.get("real_response_row_count") or 0)
    blocked_row_count = int(metric_summary.get("blocked_row_count") or response_registry.get("blocked_rows") or 0)
    generated_row_count = int(response_summary.get("generated_row_count") or response_registry.get("generated_rows") or 0)
    selected_row_count = int(response_summary.get("selected_row_count") or response_row_count or 0)
    source_row_count = int(materialization.get("row_count") or response_summary.get("source_row_count") or 0)

    metric_rows = [
        {
            "metric": "materialization",
            "status": "available" if materialization.get("validated") else "blocked",
            "reportable": bool(materialization.get("validated")),
            "value": {
                "source_dataset": materialization.get("dataset_source_id") or response_summary.get("source_dataset"),
                "source_row_count": source_row_count,
                "data_fabricated": materialization.get("data_fabricated", False),
            },
            "blocker": "" if materialization.get("validated") else "Materialization registry missing or not validated.",
        },
        {
            "metric": "response_availability",
            "status": "available",
            "reportable": True,
            "value": {
                "selected_row_count": selected_row_count,
                "generated_row_count": generated_row_count,
                "real_response_row_count": real_response_count,
                "blocked_row_count": blocked_row_count,
                "response_availability_rate": metric_summary.get("response_availability_rate"),
                "blocked_rate": metric_summary.get("blocked_rate"),
            },
            "blocker": "",
        },
        {
            "metric": "cost_fallback_summary",
            "status": "available",
            "reportable": bool(metric_summary.get("fallback_summary_computed")),
            "value": available_metrics.get("cost_fallback_summary", {}),
            "blocker": "",
        },
        *_blocked_metric_rows(available_metrics, metric_blockers),
    ]
    reportable_performance_metric_count = sum(
        1
        for row in metric_rows
        if row["metric"]
        not in {
            "materialization",
            "response_availability",
            "cost_fallback_summary",
        }
        and row["reportable"]
    )

    final_verdict = (
        FINAL_VALIDATED
        if real_response_count > 0 and reportable_performance_metric_count > 0
        else FINAL_PARTIAL
        if materialization.get("validated") and metric_summary
        else FINAL_NOT_VALIDATED
    )
    recommended_next_step = NEXT_WHEN_VALIDATED if final_verdict == FINAL_VALIDATED else NEXT_WHEN_BLOCKED

    limitations = [
        "Bounded AdvBench small-slice only: 32 materialized rows and 16 selected response rows, not full AdvBench.",
        "Response generation produced zero real model responses in this worktree because CUDA was unavailable and CPU generation was disabled.",
        "Refusal rate, safety behavior proxy, target success, ASR, clean utility, and label/score detection metrics are not reportable without real model responses and required fields.",
        "The runner is in without-logprobs mode; with-logprobs confidence metrics are unavailable.",
        "This package makes no full-matrix, cross-model, full-paper performance, benchmark-truth, or gate claim.",
    ]
    blocker_summary = {
        "primary_blocker_type": metric_summary.get("source_blocker_type")
        or response_registry.get("blocker_type")
        or response_repair_registry.get("blocker_type"),
        "response_generation_blockers": response_summary.get("blockers") or [],
        "blocked_metric_count": sum(1 for row in metric_rows if not row["reportable"]),
        "reportable_performance_metric_count": reportable_performance_metric_count,
        "real_response_required_for_behavior_metrics": True,
    }

    metric_availability_matrix = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": "PARTIAL" if final_verdict == FINAL_PARTIAL else "PASS" if final_verdict == FINAL_VALIDATED else "FAIL",
        "task_id": TASK_ID,
        "created_at": created_at,
        "metric_rows": metric_rows,
        "readiness_matrix_source": readiness_matrix.get("readiness", []),
        "without_logprobs_limitation": {
            "without_logprobs_fallback": bool(response_summary.get("without_logprobs_fallback"))
            or bool(metric_registry_payload.get("with_logprobs_metrics_computed") is False),
            "logprobs_available": bool(response_summary.get("logprobs_available")),
            "with_logprobs_metrics_computed": bool(metric_registry_payload.get("with_logprobs_metrics_computed")),
            "limitation": "No token logprobs are present in the bounded AdvBench artifacts.",
        },
        "no_full_matrix_claim": True,
        "no_full_paper_performance_claim": True,
    }

    summary = {
        "schema_version": SCHEMA_VERSION,
        "summary_status": metric_availability_matrix["summary_status"],
        "task_id": TASK_ID,
        "created_at": created_at,
        "seed": seed,
        "output_dir": str(output_dir),
        "final_verdict": final_verdict,
        "recommended_next_step": recommended_next_step,
        "materialization_summary": {
            "registry_path": str(materialization_registry),
            "validated": bool(materialization.get("validated")),
            "source_dataset": materialization.get("dataset_source_id") or "walledai/AdvBench",
            "source_type": materialization.get("dataset_source_type") or "huggingface",
            "small_slice_path": materialization.get("small_slice_path"),
            "row_count": source_row_count,
            "data_fabricated": bool(materialization.get("data_fabricated")),
            "benchmark_truth_changed": bool(materialization.get("benchmark_truth_changed")),
            "gate_changed": bool(materialization.get("gate_changed")),
        },
        "response_generation_summary": {
            "registry_path": str(response_generation_registry),
            "verdict": response_registry.get("verdict"),
            "selected_row_count": selected_row_count,
            "response_row_count": response_row_count,
            "generated_row_count": generated_row_count,
            "real_response_row_count": real_response_count,
            "blocked_row_count": blocked_row_count,
            "blocker_type": blocker_summary["primary_blocker_type"],
            "without_logprobs_fallback": bool(response_summary.get("without_logprobs_fallback")),
            "model_response_fabricated": bool(response_summary.get("model_response_fabricated")),
            "logprobs_fabricated": bool(response_summary.get("logprobs_fabricated")),
        },
        "metric_summary": {
            "registry_path": str(metric_registry),
            "verdict": metric_registry_payload.get("verdict"),
            "response_availability_computed": bool(metric_summary.get("response_availability_computed")),
            "fallback_summary_computed": bool(metric_summary.get("fallback_summary_computed")),
            "refusal_rate_computed": bool(metric_summary.get("refusal_rate_computed")),
            "safety_behavior_proxy_computed": bool(metric_summary.get("safety_behavior_proxy_computed")),
            "target_behavior_status_computed": bool(metric_summary.get("target_behavior_status_computed")),
            "detection_metrics_computed": bool(metric_summary.get("detection_metrics_computed")),
            "asr_computed": bool(metric_summary.get("asr_computed")),
            "clean_utility_computed": bool(metric_summary.get("clean_utility_computed")),
            "with_logprobs_metrics_computed": bool(metric_summary.get("with_logprobs_metrics_computed")),
        },
        "blocked_metrics": [row for row in metric_rows if not row["reportable"]],
        "blocker_summary": blocker_summary,
        "limitations": limitations,
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "full_matrix_executed": False,
        "training_executed": False,
        "route_c_continued": False,
        "generated_199_plus": False,
        "full_paper_performance_claimed": False,
    }

    verdict = {
        "schema_version": "dualscope/task-verdict/v1",
        "task_id": TASK_ID,
        "verdict": final_verdict,
        "validated": final_verdict == FINAL_VALIDATED,
        "partially_validated": final_verdict == FINAL_PARTIAL,
        "not_validated": final_verdict == FINAL_NOT_VALIDATED,
        "created_at": created_at,
        "source_output_dir": str(output_dir),
        "next_task": recommended_next_step,
        "real_response_row_count": real_response_count,
        "blocked_row_count": blocked_row_count,
        "reportable_performance_metric_count": reportable_performance_metric_count,
        "without_logprobs_fallback": summary["response_generation_summary"]["without_logprobs_fallback"],
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "full_matrix_executed": False,
        "training_executed": False,
        "route_c_continued": False,
        "generated_199_plus": False,
        "full_paper_performance_claimed": False,
    }

    report_lines = [
        "# DualScope AdvBench Small-Slice Result Package",
        "",
        "## Current Stage Goal",
        "",
        "Package the bounded AdvBench small-slice status from existing materialization, response-generation, and metric-computation artifacts without fabricating behavior or performance evidence.",
        "",
        "## Core Result",
        "",
        f"- Final verdict: `{final_verdict}`",
        f"- Recommended next step: `{recommended_next_step}`",
        f"- Materialized source rows: `{source_row_count}`",
        f"- Selected response rows: `{selected_row_count}`",
        f"- Real model responses: `{real_response_count}`",
        f"- Blocked response rows: `{blocked_row_count}`",
        f"- Primary blocker: `{blocker_summary['primary_blocker_type']}`",
        f"- Without-logprobs fallback: `{summary['response_generation_summary']['without_logprobs_fallback']}`",
        "",
        "## Metric Availability",
        "",
    ]
    for row in metric_rows:
        report_lines.append(
            f"- `{row['metric']}`: status=`{row['status']}`, reportable=`{row['reportable']}`, blocker=`{row['blocker']}`"
        )
    report_lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in limitations],
            "",
            "## Non-Fabrication Guardrails",
            "",
            "- Model responses fabricated: `False`",
            "- Logprobs fabricated: `False`",
            "- Metrics fabricated: `False`",
            "- Benchmark truth changed: `False`",
            "- Gates changed: `False`",
            "- Full matrix executed: `False`",
            "- Full paper performance claimed: `False`",
            "- route_c / 199+ continued: `False`",
            "",
        ]
    )

    write_json(output_dir / "result_package_summary.json", summary)
    write_json(output_dir / "metric_availability_matrix.json", metric_availability_matrix)
    write_json(output_dir / "result_package_verdict.json", verdict)
    write_markdown(output_dir / "result_package_report.md", report_lines)
    write_markdown(docs_path, report_lines)
    write_json(registry_path, verdict)
    return summary
