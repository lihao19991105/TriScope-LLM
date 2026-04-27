"""Repair/compression package for AdvBench small-slice result packaging."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


TASK_ID = "dualscope-advbench-small-slice-result-package-repair"
SOURCE_TASK_ID = "dualscope-advbench-small-slice-result-package"
SCHEMA_VERSION = "dualscope/advbench-small-slice-result-package-repair/v1"
FINAL_VALIDATED = "AdvBench small-slice result package repair validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"
NEXT_BLOCKER_CLOSURE = "dualscope-advbench-small-slice-response-generation-blocker-closure"

DEFAULT_RESULT_PACKAGE_DIR = Path("outputs/dualscope_advbench_small_slice_result_package/default")
DEFAULT_METRIC_REPAIR_DIR = Path("outputs/dualscope_advbench_small_slice_metric_computation_repair/default")
DEFAULT_RESPONSE_DIR = Path("outputs/dualscope_advbench_small_slice_response_generation/default")
DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_advbench_small_slice_result_package_repair/default")
DEFAULT_ANALYSIS_DIR = Path("outputs/dualscope_advbench_small_slice_result_package_repair_analysis/default")
DEFAULT_REGISTRY_PATH = Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package-repair.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


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
    source_summary: dict[str, Any],
    source_verdict: dict[str, Any],
    source_registry: dict[str, Any],
    metric_repair_summary: dict[str, Any],
    metric_repair_registry: dict[str, Any],
    response_repair_registry: dict[str, Any],
    response_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    real_rows = _real_response_rows(response_rows)
    blocked_rows = [row for row in response_rows if row.get("response_generation_status") == "blocked"]
    fabricated_rows = [
        row
        for row in response_rows
        if row.get("model_output_fabricated") is True
        or row.get("model_response_fabricated") is True
        or row.get("logprobs_fabricated") is True
    ]
    source_package_present = bool(source_summary) and bool(source_verdict)
    registries_present = bool(source_registry) and bool(metric_repair_registry)
    guardrails_clear = (
        source_summary.get("model_response_fabricated") is not True
        and source_summary.get("logprobs_fabricated") is not True
        and source_summary.get("metrics_fabricated") is not True
        and source_registry.get("model_response_fabricated") is not True
        and source_registry.get("logprobs_fabricated") is not True
        and source_registry.get("metrics_fabricated") is not True
        and not fabricated_rows
    )
    metric_repair_validated = (
        metric_repair_summary.get("final_verdict") == "AdvBench small-slice metric computation repair validated"
        or metric_repair_registry.get("verdict") == "AdvBench small-slice metric computation repair validated"
    )
    return {
        "summary_status": "PASS" if source_package_present and registries_present and guardrails_clear else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "source_result_package_verdict": source_summary.get("final_verdict") or source_registry.get("verdict"),
        "source_result_package_summary_status": source_summary.get("summary_status"),
        "source_result_package_present": source_package_present,
        "source_registry_present": bool(source_registry),
        "metric_repair_verdict": metric_repair_summary.get("final_verdict") or metric_repair_registry.get("verdict"),
        "metric_repair_validated": metric_repair_validated,
        "response_generation_repair_verdict": response_repair_registry.get("verdict"),
        "response_generation_repair_next_task": response_repair_registry.get("next_task"),
        "response_row_count": len(response_rows),
        "real_response_row_count": len(real_rows),
        "blocked_row_count": len(blocked_rows),
        "fabricated_row_count": len(fabricated_rows),
        "source_blocker_type": (
            source_summary.get("blocker_summary", {}).get("primary_blocker_type")
            or metric_repair_summary.get("source_blocker_type")
            or metric_repair_registry.get("blocker_type")
            or response_repair_registry.get("blocker_type")
        ),
        "reportable_performance_metric_count": int(
            source_summary.get("blocker_summary", {}).get("reportable_performance_metric_count")
            or metric_repair_summary.get("reportable_performance_metric_count")
            or source_registry.get("reportable_performance_metric_count")
            or 0
        ),
        "without_logprobs_fallback": bool(
            source_summary.get("response_generation_summary", {}).get("without_logprobs_fallback")
            or source_registry.get("without_logprobs_fallback")
        ),
        "nonfabrication_flags_clear": guardrails_clear,
    }


def _evidence_boundary(source_audit: dict[str, Any], metric_repair_availability: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_status": "PASS" if source_audit["summary_status"] == "PASS" else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "reportable_evidence": [
            {
                "item": "materialization_status",
                "reportable": True,
                "reason": "Prior result package and materialization registry preserve bounded AdvBench source status.",
            },
            {
                "item": "response_availability",
                "reportable": True,
                "reason": "Response rows and metric repair support selected, blocked, and real-response counts.",
            },
            {
                "item": "cost_fallback_summary",
                "reportable": True,
                "reason": "Fallback status is artifact-supported and does not imply behavior performance.",
            },
        ],
        "blocked_evidence": [
            {
                "item": "refusal_rate_or_safety_proxy",
                "reportable": False,
                "reason": "No real model responses exist in the bounded AdvBench response artifacts.",
            },
            {
                "item": "target_success_or_asr",
                "reportable": False,
                "reason": "No target-match fields over real response rows are available.",
            },
            {
                "item": "label_score_detection_metrics",
                "reportable": False,
                "reason": "No aligned labels and risk scores over real AdvBench response rows are available.",
            },
            {
                "item": "clean_utility",
                "reportable": False,
                "reason": "AdvBench harmful-prompt slice has no clean utility contract here.",
            },
            {
                "item": "with_logprobs_confidence_metrics",
                "reportable": False,
                "reason": "No token logprobs are present; without-logprobs fallback is recorded.",
            },
        ],
        "metric_repair_rows": metric_repair_availability.get("rows", []),
        "real_response_row_count": source_audit["real_response_row_count"],
        "blocked_row_count": source_audit["blocked_row_count"],
        "reportable_performance_metric_count": source_audit["reportable_performance_metric_count"],
    }


def _blocker_compression(
    *,
    source_audit: dict[str, Any],
    source_summary: dict[str, Any],
    metric_repair_blockers: dict[str, Any],
) -> dict[str, Any]:
    return {
        "summary_status": "BLOCKED" if source_audit["real_response_row_count"] == 0 else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "primary_blocker_owner": "response_generation"
        if source_audit["real_response_row_count"] == 0
        else "result_package",
        "primary_blocker_type": source_audit.get("source_blocker_type"),
        "root_cause": "zero_real_model_responses"
        if source_audit["real_response_row_count"] == 0
        else "missing_reportable_metric_fields",
        "recommended_next_step": NEXT_BLOCKER_CLOSURE,
        "source_blocker_summary": source_summary.get("blocker_summary", {}),
        "metric_repair_blockers": metric_repair_blockers,
        "blocked_metric_count": len(_evidence_boundary(source_audit, {}).get("blocked_evidence", [])),
    }


def _select_verdict(source_audit: dict[str, Any]) -> tuple[str, str, str]:
    if source_audit["summary_status"] != "PASS":
        return FINAL_NOT_VALIDATED, "dualscope-advbench-small-slice-result-package-blocker-closure", "source_audit_failed"
    if source_audit["fabricated_row_count"]:
        return FINAL_NOT_VALIDATED, "dualscope-advbench-small-slice-result-package-blocker-closure", "fabricated_rows_detected"
    if not source_audit["metric_repair_validated"]:
        return FINAL_PARTIAL, "dualscope-advbench-small-slice-metric-computation-repair", "metric_repair_not_validated"
    if source_audit["real_response_row_count"] == 0:
        return FINAL_VALIDATED, NEXT_BLOCKER_CLOSURE, "zero_real_responses_result_package_boundary_preserved"
    if source_audit["reportable_performance_metric_count"] > 0:
        return FINAL_VALIDATED, "dualscope-jbb-small-slice-materialization", "reportable_metrics_available"
    return FINAL_PARTIAL, "dualscope-advbench-small-slice-result-package-blocker-closure", "real_responses_without_reportable_metrics"


def _limitations(source_audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "items": [
            "This repair validates the AdvBench result-package boundary, not AdvBench model performance.",
            "All behavior and performance metrics remain blocked while real_response_row_count is zero.",
            "No refusal, target-success, ASR, detection, clean utility, or logprob metric is inferred from blocked rows.",
            "The next execution step is response-generation blocker closure or a GPU-visible generation rerun plan.",
            "No benchmark truth, gates, labels, responses, logprobs, route_c artifacts, or 199+ plans were modified.",
        ],
        "without_logprobs_fallback": source_audit["without_logprobs_fallback"],
    }


def _write_report(
    *,
    output_dir: Path,
    docs_path: Path,
    summary: dict[str, Any],
    evidence_boundary: dict[str, Any],
    blocker_compression: dict[str, Any],
) -> None:
    lines = [
        "# DualScope AdvBench Small-Slice Result Package Repair",
        "",
        "## Current Stage Goal",
        "",
        "Compress the partially validated AdvBench result-package state into explicit evidence boundaries, blockers, and routing.",
        "",
        "## Core Result",
        "",
        f"- Final verdict: `{summary['final_verdict']}`",
        f"- Source result-package verdict: `{summary['source_result_package_verdict']}`",
        f"- Metric repair verdict: `{summary['metric_repair_verdict']}`",
        f"- Real response rows: `{summary['real_response_row_count']}`",
        f"- Blocked response rows: `{summary['blocked_row_count']}`",
        f"- Reportable performance metrics: `{summary['reportable_performance_metric_count']}`",
        f"- Primary blocker: `{summary['source_blocker_type']}`",
        f"- Recommended next step: `{summary['recommended_next_step']}`",
        f"- Routing reason: `{summary['routing_reason']}`",
        "",
        "## Reportable Evidence",
        "",
    ]
    for row in evidence_boundary["reportable_evidence"]:
        lines.append(f"- `{row['item']}`: {row['reason']}")
    lines.extend(["", "## Blocked Evidence", ""])
    for row in evidence_boundary["blocked_evidence"]:
        lines.append(f"- `{row['item']}`: {row['reason']}")
    lines.extend(
        [
            "",
            "## Blocker Compression",
            "",
            f"- Root cause: `{blocker_compression['root_cause']}`",
            f"- Primary owner: `{blocker_compression['primary_blocker_owner']}`",
            "",
            "## Guardrails",
            "",
            "- Model responses fabricated: `False`",
            "- Logprobs fabricated: `False`",
            "- Metrics fabricated: `False`",
            "- Benchmark truth changed: `False`",
            "- Gates changed: `False`",
            "- Full matrix executed: `False`",
            "- Training executed: `False`",
            "- route_c continued: `False`",
            "- 199+ generated: `False`",
            "",
        ]
    )
    write_markdown(output_dir / "advbench_small_slice_result_package_repair_report.md", lines)
    write_markdown(docs_path, lines)


def build_advbench_small_slice_result_package_repair(
    *,
    result_package_dir: Path,
    metric_repair_dir: Path,
    response_dir: Path,
    result_package_registry: Path,
    metric_repair_registry: Path,
    response_generation_repair_registry: Path,
    output_dir: Path,
    analysis_dir: Path,
    registry_path: Path,
    docs_path: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    created_at = utc_now()

    source_summary = read_json(result_package_dir / "result_package_summary.json")
    source_verdict = read_json(result_package_dir / "result_package_verdict.json")
    source_availability = read_json(result_package_dir / "metric_availability_matrix.json")
    source_registry = read_json(result_package_registry)
    metric_repair_summary = read_json(metric_repair_dir / "advbench_small_slice_metric_computation_repair_summary.json")
    metric_repair_availability = read_json(
        metric_repair_dir / "advbench_small_slice_metric_computation_repair_metric_availability_matrix.json"
    )
    metric_repair_blockers = read_json(
        metric_repair_dir / "advbench_small_slice_metric_computation_repair_blocked_metric_compression.json"
    )
    metric_repair_registry_payload = read_json(metric_repair_registry)
    response_repair_registry_payload = read_json(response_generation_repair_registry)
    response_rows = read_jsonl(response_dir / "advbench_small_slice_responses.jsonl")

    source_audit = _source_audit(
        source_summary=source_summary,
        source_verdict=source_verdict,
        source_registry=source_registry,
        metric_repair_summary=metric_repair_summary,
        metric_repair_registry=metric_repair_registry_payload,
        response_repair_registry=response_repair_registry_payload,
        response_rows=response_rows,
    )
    evidence_boundary = _evidence_boundary(source_audit, metric_repair_availability)
    blockers = _blocker_compression(
        source_audit=source_audit,
        source_summary=source_summary,
        metric_repair_blockers=metric_repair_blockers,
    )
    limitations = _limitations(source_audit)
    final_verdict, next_step, routing_reason = _select_verdict(source_audit)
    summary_status = "PASS" if final_verdict == FINAL_VALIDATED else "PARTIAL" if final_verdict == FINAL_PARTIAL else "FAIL"

    summary = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "created_at": created_at,
        "seed": seed,
        "repair_for": SOURCE_TASK_ID,
        "final_verdict": final_verdict,
        "recommended_next_step": next_step,
        "routing_reason": routing_reason,
        "source_result_package_verdict": source_audit["source_result_package_verdict"],
        "metric_repair_verdict": source_audit["metric_repair_verdict"],
        "response_generation_repair_verdict": source_audit["response_generation_repair_verdict"],
        "source_blocker_type": source_audit["source_blocker_type"],
        "response_row_count": source_audit["response_row_count"],
        "real_response_row_count": source_audit["real_response_row_count"],
        "blocked_row_count": source_audit["blocked_row_count"],
        "reportable_performance_metric_count": source_audit["reportable_performance_metric_count"],
        "without_logprobs_fallback": source_audit["without_logprobs_fallback"],
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
        "repair_for": SOURCE_TASK_ID,
        "next_task": next_step,
        "routing_reason": routing_reason,
        "real_response_row_count": source_audit["real_response_row_count"],
        "blocked_row_count": source_audit["blocked_row_count"],
        "reportable_performance_metric_count": source_audit["reportable_performance_metric_count"],
        "blocker_type": source_audit["source_blocker_type"],
        "without_logprobs_fallback": source_audit["without_logprobs_fallback"],
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
    recommendation = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": next_step,
        "reason": routing_reason,
    }

    write_json(output_dir / "advbench_small_slice_result_package_repair_summary.json", summary)
    write_json(output_dir / "advbench_small_slice_result_package_repair_source_audit.json", source_audit)
    write_json(output_dir / "advbench_small_slice_result_package_repair_evidence_boundary.json", evidence_boundary)
    write_json(output_dir / "advbench_small_slice_result_package_repair_metric_availability_matrix.json", source_availability)
    write_json(output_dir / "advbench_small_slice_result_package_repair_blocker_compression.json", blockers)
    write_json(output_dir / "advbench_small_slice_result_package_repair_limitations.json", limitations)
    write_json(output_dir / "advbench_small_slice_result_package_repair_verdict.json", verdict)
    write_json(output_dir / "advbench_small_slice_result_package_repair_next_step_recommendation.json", recommendation)
    write_json(registry_path, verdict)

    write_json(analysis_dir / "advbench_small_slice_result_package_repair_summary.json", summary)
    write_json(analysis_dir / "advbench_small_slice_result_package_repair_evidence_boundary.json", evidence_boundary)
    write_json(analysis_dir / "advbench_small_slice_result_package_repair_blocker_compression.json", blockers)
    write_json(analysis_dir / "advbench_small_slice_result_package_repair_verdict.json", verdict)
    _write_report(output_dir=output_dir, docs_path=docs_path, summary=summary, evidence_boundary=evidence_boundary, blocker_compression=blockers)
    write_markdown(
        analysis_dir / "advbench_small_slice_result_package_repair_analysis_report.md",
        [
            "# DualScope AdvBench Small-Slice Result Package Repair Analysis",
            "",
            f"- Final verdict: `{final_verdict}`",
            f"- Recommended next step: `{next_step}`",
            f"- Routing reason: `{routing_reason}`",
            f"- Real response rows: `{source_audit['real_response_row_count']}`",
            f"- Reportable performance metrics: `{source_audit['reportable_performance_metric_count']}`",
            "",
        ],
    )
    return summary
