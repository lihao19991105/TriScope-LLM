"""Repair/compression package for AdvBench small-slice metric computation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


TASK_ID = "dualscope-advbench-small-slice-metric-computation-repair"
SOURCE_TASK_ID = "dualscope-advbench-small-slice-metric-computation"
SCHEMA_VERSION = "dualscope/advbench-small-slice-metric-computation-repair/v1"
FINAL_VALIDATED = "AdvBench small-slice metric computation repair validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"

DEFAULT_METRIC_DIR = Path("outputs/dualscope_advbench_small_slice_metric_computation/default")
DEFAULT_RESPONSE_DIR = Path("outputs/dualscope_advbench_small_slice_response_generation/default")
DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_advbench_small_slice_metric_computation_repair/default")
DEFAULT_REGISTRY_PATH = Path(
    ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation-repair.json"
)


@dataclass(frozen=True)
class RepairInputs:
    metric_dir: Path
    response_dir: Path
    metric_registry: Path
    response_generation_registry: Path
    response_generation_repair_registry: Path
    output_dir: Path
    registry_path: Path
    docs_path: Path
    seed: int


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def maybe_read_json(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {}


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


def write_markdown(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _real_response_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    real_rows: list[dict[str, Any]] = []
    for row in rows:
        response = row.get("model_response")
        if row.get("model_response_present") is not True:
            continue
        if row.get("response_generation_status") not in (None, "generated"):
            continue
        if row.get("model_output_fabricated") is True or row.get("model_response_fabricated") is True:
            continue
        if isinstance(response, str) and response.strip():
            real_rows.append(row)
    return real_rows


def _source_audit(
    *,
    metric_summary: dict[str, Any],
    metric_verdict: dict[str, Any],
    available_metrics: dict[str, Any],
    metric_blockers: dict[str, Any],
    response_rows: list[dict[str, Any]],
    response_generation_registry: dict[str, Any],
    response_generation_repair_registry: dict[str, Any],
) -> dict[str, Any]:
    real_rows = _real_response_rows(response_rows)
    fabricated_rows = [
        row
        for row in response_rows
        if row.get("model_output_fabricated") is True
        or row.get("model_response_fabricated") is True
        or row.get("logprobs_fabricated") is True
    ]
    blocked_rows = [row for row in response_rows if row.get("response_generation_status") == "blocked"]
    blocker_counts: dict[str, int] = {}
    for row in blocked_rows:
        blocker = str(row.get("blocker") or "unknown_blocker")
        blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    required_metric_files_present = all(
        bool(payload)
        for payload in (
            metric_summary,
            metric_verdict,
            available_metrics,
            metric_blockers,
        )
    )
    nonfabrication_flags_clear = (
        not bool(metric_summary.get("model_response_fabricated"))
        and not bool(metric_summary.get("logprobs_fabricated"))
        and not bool(metric_summary.get("benchmark_truth_changed"))
        and not bool(metric_summary.get("gate_changed"))
        and not bool(metric_summary.get("full_matrix_executed"))
        and not bool(metric_summary.get("training_executed"))
        and not bool(metric_summary.get("route_c_continued"))
        and not bool(metric_summary.get("generated_199_plus"))
        and not fabricated_rows
    )
    return {
        "summary_status": "PASS" if required_metric_files_present and nonfabrication_flags_clear else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "source_metric_verdict": metric_summary.get("final_verdict") or metric_verdict.get("verdict"),
        "source_metric_summary_status": metric_summary.get("summary_status"),
        "response_generation_verdict": response_generation_registry.get("verdict"),
        "response_generation_repair_verdict": response_generation_repair_registry.get("verdict"),
        "response_generation_repair_next_task": response_generation_repair_registry.get("next_task"),
        "response_row_count": len(response_rows),
        "real_response_row_count": len(real_rows),
        "blocked_row_count": len(blocked_rows),
        "fabricated_row_count": len(fabricated_rows),
        "blocker_counts": blocker_counts,
        "source_blocker_type": metric_summary.get("source_blocker_type")
        or response_generation_registry.get("blocker_type")
        or response_generation_repair_registry.get("blocker_type"),
        "required_metric_files_present": required_metric_files_present,
        "nonfabrication_flags_clear": nonfabrication_flags_clear,
        "response_availability_computed": bool(metric_summary.get("response_availability_computed")),
        "fallback_summary_computed": bool(metric_summary.get("fallback_summary_computed")),
        "performance_metrics_computed": any(
            bool(metric_summary.get(key))
            for key in (
                "refusal_rate_computed",
                "safety_behavior_proxy_computed",
                "target_behavior_status_computed",
                "detection_metrics_computed",
                "asr_computed",
                "clean_utility_computed",
                "with_logprobs_metrics_computed",
            )
        ),
    }


def _availability_matrix(
    *,
    metric_summary: dict[str, Any],
    available_metrics: dict[str, Any],
    source_audit: dict[str, Any],
) -> dict[str, Any]:
    metric_rows = [
        {
            "metric": "response_availability",
            "source_status": available_metrics.get("response_availability", {}).get("summary_status", "MISSING"),
            "reportable": bool(metric_summary.get("response_availability_computed")),
            "value": metric_summary.get("response_availability_rate"),
            "blocker": "",
        },
        {
            "metric": "cost_fallback_summary",
            "source_status": available_metrics.get("cost_fallback_summary", {}).get("summary_status", "MISSING"),
            "reportable": bool(metric_summary.get("fallback_summary_computed")),
            "value": available_metrics.get("cost_fallback_summary", {}).get("without_logprobs_fallback_rate"),
            "blocker": "",
        },
        {
            "metric": "refusal_rate",
            "source_status": available_metrics.get("refusal_rate_and_safety_behavior_proxy", {}).get(
                "summary_status", "MISSING"
            ),
            "reportable": bool(metric_summary.get("refusal_rate_computed")),
            "value": available_metrics.get("refusal_rate_and_safety_behavior_proxy", {}).get("refusal_rate"),
            "blocker": available_metrics.get("refusal_rate_and_safety_behavior_proxy", {}).get(
                "reason", "No PASS refusal metric artifact."
            ),
        },
        {
            "metric": "target_behavior_status",
            "source_status": available_metrics.get("target_behavior_status", {}).get("summary_status", "MISSING"),
            "reportable": bool(metric_summary.get("target_behavior_status_computed")),
            "value": available_metrics.get("target_behavior_status", {}).get("target_match_rate"),
            "blocker": available_metrics.get("target_behavior_status", {}).get(
                "reason", "No PASS target behavior artifact."
            ),
        },
        {
            "metric": "label_score_aligned_detection_metrics",
            "source_status": available_metrics.get("label_score_aligned_detection_metrics", {}).get(
                "summary_status", "MISSING"
            ),
            "reportable": bool(metric_summary.get("detection_metrics_computed")),
            "value": None,
            "blocker": available_metrics.get("label_score_aligned_detection_metrics", {}).get(
                "reason", "No PASS detection metric artifact."
            ),
        },
        {
            "metric": "attack_success_rate",
            "source_status": "NOT_APPLICABLE",
            "reportable": bool(metric_summary.get("asr_computed")),
            "value": None,
            "blocker": "No real target_matched response rows are available.",
        },
        {
            "metric": "clean_utility",
            "source_status": "NOT_APPLICABLE",
            "reportable": bool(metric_summary.get("clean_utility_computed")),
            "value": None,
            "blocker": "AdvBench harmful-prompt slice has no clean utility contract in this task.",
        },
        {
            "metric": "with_logprobs_metrics",
            "source_status": "NOT_APPLICABLE",
            "reportable": bool(metric_summary.get("with_logprobs_metrics_computed")),
            "value": None,
            "blocker": "No token logprobs are present in bounded AdvBench artifacts.",
        },
    ]
    reportable_performance = [
        row
        for row in metric_rows
        if row["metric"] not in {"response_availability", "cost_fallback_summary"} and row["reportable"]
    ]
    return {
        "summary_status": "PASS" if source_audit["summary_status"] == "PASS" else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "real_response_row_count": source_audit["real_response_row_count"],
        "blocked_row_count": source_audit["blocked_row_count"],
        "reportable_performance_metric_count": len(reportable_performance),
        "rows": metric_rows,
    }


def _blocked_metric_compression(
    *,
    metric_blockers: dict[str, Any],
    availability: dict[str, Any],
    source_audit: dict[str, Any],
) -> dict[str, Any]:
    unavailable = [
        row
        for row in availability["rows"]
        if row["metric"] not in {"response_availability", "cost_fallback_summary"} and row["reportable"] is not True
    ]
    return {
        "summary_status": "BLOCKED" if unavailable else "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "source_blocker_type": source_audit.get("source_blocker_type"),
        "source_blocker_counts": source_audit.get("blocker_counts", {}),
        "unavailable_metrics": unavailable,
        "source_metric_blockers": metric_blockers,
        "metric_gap_root_cause": "no_real_model_responses"
        if source_audit["real_response_row_count"] == 0
        else "metric_fields_unavailable",
        "recommended_blocker_owner": "response_generation"
        if source_audit["real_response_row_count"] == 0
        else "metric_computation",
    }


def _select_verdict_and_next_step(
    *,
    source_audit: dict[str, Any],
    availability: dict[str, Any],
    response_generation_repair_registry: dict[str, Any],
) -> tuple[str, str, str]:
    if source_audit["summary_status"] != "PASS":
        return FINAL_NOT_VALIDATED, "dualscope-advbench-small-slice-metric-computation-blocker-closure", "source_audit_failed"
    if source_audit["fabricated_row_count"]:
        return FINAL_NOT_VALIDATED, "dualscope-advbench-small-slice-metric-computation-blocker-closure", "fabricated_rows_detected"
    if source_audit["real_response_row_count"] == 0:
        upstream_next = str(response_generation_repair_registry.get("next_task") or "")
        next_step = upstream_next or "dualscope-advbench-small-slice-response-generation-blocker-closure"
        return FINAL_VALIDATED, next_step, "zero_real_responses_upstream_generation_blocker_preserved"
    if availability["reportable_performance_metric_count"] > 0:
        return FINAL_VALIDATED, "dualscope-advbench-small-slice-result-package", "reportable_metrics_available"
    return FINAL_PARTIAL, "dualscope-advbench-small-slice-metric-computation-blocker-closure", "real_responses_without_reportable_metrics"


def _limitations(source_audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "items": [
            "This repair reports only artifact-supported response availability and fallback evidence.",
            "No refusal, target behavior, detection, ASR, clean utility, or logprob metric is made reportable without real response rows.",
            "The package does not infer benchmark truth, labels, target success, or utility from free text.",
            "The package does not retry model generation inside the CUDA-invisible Codex sandbox.",
            "No benchmark truth, gates, labels, responses, logprobs, final_risk_score, route_c artifacts, or 199+ plans were modified.",
        ],
        "source_blocker_type": source_audit.get("source_blocker_type"),
    }


def _write_report(
    *,
    output_dir: Path,
    docs_path: Path,
    summary: dict[str, Any],
    availability: dict[str, Any],
    blockers: dict[str, Any],
) -> None:
    lines = [
        "# DualScope AdvBench Small-Slice Metric Computation Repair",
        "",
        "## Current Stage Goal",
        "",
        "Compress the partially validated AdvBench metric-computation state into explicit metric availability, blockers, and next-step routing.",
        "",
        "## Core Result",
        "",
        f"- Final verdict: `{summary['final_verdict']}`",
        f"- Source metric verdict: `{summary['source_metric_verdict']}`",
        f"- Real response rows: `{summary['real_response_row_count']}`",
        f"- Blocked response rows: `{summary['blocked_row_count']}`",
        f"- Source blocker type: `{summary['source_blocker_type']}`",
        f"- Recommended next step: `{summary['recommended_next_step']}`",
        f"- Routing reason: `{summary['routing_reason']}`",
        "",
        "## Availability",
        "",
    ]
    for row in availability["rows"]:
        lines.append(
            f"- `{row['metric']}`: reportable=`{row['reportable']}`, source_status=`{row['source_status']}`"
        )
    lines.extend(
        [
            "",
            "## Blocked Metrics",
            "",
        ]
    )
    for row in blockers["unavailable_metrics"]:
        lines.append(f"- `{row['metric']}`: {row['blocker']}")
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Model responses fabricated: `False`",
            "- Logprobs fabricated: `False`",
            "- Benchmark truth changed: `False`",
            "- Gates changed: `False`",
            "- Full matrix executed: `False`",
            "- Training executed: `False`",
            "- route_c continued: `False`",
            "- 199+ generated: `False`",
            "",
        ]
    )
    write_markdown(output_dir / "advbench_small_slice_metric_computation_repair_report.md", lines)
    write_markdown(docs_path, lines)


def build_advbench_small_slice_metric_computation_repair(
    *,
    metric_dir: Path,
    response_dir: Path,
    metric_registry: Path,
    response_generation_registry: Path,
    response_generation_repair_registry: Path,
    output_dir: Path,
    registry_path: Path,
    docs_path: Path,
    seed: int,
) -> dict[str, Any]:
    inputs = RepairInputs(
        metric_dir=metric_dir,
        response_dir=response_dir,
        metric_registry=metric_registry,
        response_generation_registry=response_generation_registry,
        response_generation_repair_registry=response_generation_repair_registry,
        output_dir=output_dir,
        registry_path=registry_path,
        docs_path=docs_path,
        seed=seed,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()

    metric_summary = maybe_read_json(inputs.metric_dir / "metric_summary.json")
    available_metrics = maybe_read_json(inputs.metric_dir / "available_metrics.json")
    metric_blockers = maybe_read_json(inputs.metric_dir / "metric_blockers.json")
    readiness_matrix = maybe_read_json(inputs.metric_dir / "readiness_matrix.json")
    metric_verdict = maybe_read_json(inputs.metric_dir / "metric_verdict.json")
    metric_registry_payload = maybe_read_json(inputs.metric_registry)
    response_generation_registry_payload = maybe_read_json(inputs.response_generation_registry)
    response_generation_repair_registry_payload = maybe_read_json(inputs.response_generation_repair_registry)
    response_rows = read_jsonl(inputs.response_dir / "advbench_small_slice_responses.jsonl")

    source_audit = _source_audit(
        metric_summary=metric_summary,
        metric_verdict=metric_verdict,
        available_metrics=available_metrics,
        metric_blockers=metric_blockers,
        response_rows=response_rows,
        response_generation_registry=response_generation_registry_payload,
        response_generation_repair_registry=response_generation_repair_registry_payload,
    )
    availability = _availability_matrix(
        metric_summary=metric_summary,
        available_metrics=available_metrics,
        source_audit=source_audit,
    )
    blockers = _blocked_metric_compression(
        metric_blockers=metric_blockers,
        availability=availability,
        source_audit=source_audit,
    )
    final_verdict, next_step, routing_reason = _select_verdict_and_next_step(
        source_audit=source_audit,
        availability=availability,
        response_generation_repair_registry=response_generation_repair_registry_payload,
    )
    summary_status = "PASS" if final_verdict == FINAL_VALIDATED else "PARTIAL" if final_verdict == FINAL_PARTIAL else "FAIL"
    limitations = _limitations(source_audit)

    summary = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "created_at": created_at,
        "seed": seed,
        "final_verdict": final_verdict,
        "recommended_next_step": next_step,
        "routing_reason": routing_reason,
        "repair_for": SOURCE_TASK_ID,
        "metric_dir": str(metric_dir),
        "response_dir": str(response_dir),
        "source_metric_verdict": metric_summary.get("final_verdict") or metric_registry_payload.get("verdict"),
        "source_registry_verdict": metric_registry_payload.get("verdict"),
        "source_response_generation_verdict": response_generation_registry_payload.get("verdict"),
        "source_response_generation_repair_verdict": response_generation_repair_registry_payload.get("verdict"),
        "source_blocker_type": source_audit.get("source_blocker_type"),
        "response_row_count": source_audit["response_row_count"],
        "real_response_row_count": source_audit["real_response_row_count"],
        "blocked_row_count": source_audit["blocked_row_count"],
        "reportable_performance_metric_count": availability["reportable_performance_metric_count"],
        "response_availability_computed": bool(metric_summary.get("response_availability_computed")),
        "fallback_summary_computed": bool(metric_summary.get("fallback_summary_computed")),
        "performance_metrics_computed": bool(source_audit["performance_metrics_computed"]),
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "full_matrix_executed": False,
        "training_executed": False,
        "route_c_continued": False,
        "generated_199_plus": False,
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
        "repair_for": SOURCE_TASK_ID,
        "next_task": next_step,
        "routing_reason": routing_reason,
        "real_response_row_count": source_audit["real_response_row_count"],
        "blocked_row_count": source_audit["blocked_row_count"],
        "reportable_performance_metric_count": availability["reportable_performance_metric_count"],
        "blocker_type": source_audit.get("source_blocker_type"),
        "response_availability_computed": bool(metric_summary.get("response_availability_computed")),
        "fallback_summary_computed": bool(metric_summary.get("fallback_summary_computed")),
        "performance_metrics_computed": bool(source_audit["performance_metrics_computed"]),
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "full_matrix_executed": False,
        "training_executed": False,
        "route_c_continued": False,
        "generated_199_plus": False,
    }
    recommendation = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": next_step,
        "reason": routing_reason,
    }

    write_json(output_dir / "advbench_small_slice_metric_computation_repair_summary.json", summary)
    write_json(output_dir / "advbench_small_slice_metric_computation_repair_metric_availability_matrix.json", availability)
    write_json(output_dir / "advbench_small_slice_metric_computation_repair_blocked_metric_compression.json", blockers)
    write_json(output_dir / "advbench_small_slice_metric_computation_repair_source_audit.json", source_audit)
    write_json(output_dir / "advbench_small_slice_metric_computation_repair_limitations.json", limitations)
    write_json(output_dir / "advbench_small_slice_metric_computation_repair_readiness_snapshot.json", readiness_matrix)
    write_json(output_dir / "advbench_small_slice_metric_computation_repair_verdict.json", verdict)
    write_json(output_dir / "advbench_small_slice_metric_computation_repair_next_step_recommendation.json", recommendation)
    write_json(registry_path, verdict)
    _write_report(output_dir=output_dir, docs_path=docs_path, summary=summary, availability=availability, blockers=blockers)
    return summary
