"""Repair/compression package for AdvBench small-slice response generation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "dualscope-advbench-small-slice-response-generation-repair"
SOURCE_TASK_ID = "dualscope-advbench-small-slice-response-generation"
SCHEMA_VERSION = "dualscope/advbench-small-slice-response-generation-repair/v1"
VALIDATED = "AdvBench small-slice response generation repair validated"
PARTIAL = "Partially validated"
NOT_VALIDATED = "Not validated"

DEFAULT_RESPONSE_DIR = Path("outputs/dualscope_advbench_small_slice_response_generation/default")
DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_advbench_small_slice_response_generation_repair/default")
DEFAULT_REGISTRY_PATH = Path(".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _has_real_response(row: dict[str, Any]) -> bool:
    return (
        row.get("response_generation_status") == "generated"
        and bool(str(row.get("model_response") or "").strip())
        and not bool(row.get("model_output_fabricated"))
    )


def _blocker_route(blocker_type: str, blockers: list[str]) -> tuple[str, str]:
    text = " ".join([blocker_type, *blockers]).lower()
    if "missing" in text:
        return "dualscope-advbench-small-slice-response-input-artifact-repair", "missing_input_or_dependency"
    if "oom" in text or "memory" in text:
        return "dualscope-advbench-small-slice-response-generation-blocker-closure", "gpu_memory_blocker"
    if "cuda" in text or "nvidia" in text or "driver" in text:
        return "dualscope-advbench-small-slice-response-generation-blocker-closure", "cuda_visibility_blocker"
    if "safety_filter" in text:
        return "dualscope-advbench-small-slice-response-generation-blocker-closure", "output_safety_filter_blocker"
    if "logprob" in text:
        return "dualscope-advbench-small-slice-metric-computation", "without_logprobs_fallback_ready"
    return "dualscope-advbench-small-slice-response-generation-blocker-closure", "runtime_blocker"


def _row_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    required = {
        "sample_id",
        "dataset_id",
        "instruction",
        "model_response",
        "generation_mode",
        "capability_flags",
        "safety_mode",
        "without_logprobs_fallback",
        "model_output_fabricated",
    }
    missing_required = 0
    fabricated_rows = 0
    real_rows = 0
    blocked_rows = 0
    safety_suppressed_rows = 0
    for row in rows:
        if any(key not in row for key in required):
            missing_required += 1
        if bool(row.get("model_output_fabricated")):
            fabricated_rows += 1
        if _has_real_response(row):
            real_rows += 1
        if row.get("response_generation_status") != "generated":
            blocked_rows += 1
        if bool(row.get("output_safety_filter_suppressed")):
            safety_suppressed_rows += 1
    return {
        "row_count": len(rows),
        "real_response_rows": real_rows,
        "blocked_rows": blocked_rows,
        "missing_required_field_rows": missing_required,
        "fabricated_response_rows": fabricated_rows,
        "safety_filter_suppressed_rows": safety_suppressed_rows,
    }


def _availability_matrix(summary: dict[str, Any], row_audit: dict[str, Any]) -> dict[str, Any]:
    real_rows = int(row_audit["real_response_rows"])
    blocker_type = str(summary.get("blocker_type") or "")
    return {
        "response_rows_jsonl": {
            "status": "available" if row_audit["row_count"] else "missing",
            "row_count": row_audit["row_count"],
        },
        "real_model_responses": {
            "status": "available" if real_rows else "blocked",
            "row_count": real_rows,
            "blocker_type": blocker_type if not real_rows else "",
        },
        "explicit_blocker": {
            "status": "available" if blocker_type else "missing",
            "blocker_type": blocker_type,
        },
        "with_logprobs_metrics": {
            "status": "blocked",
            "reason": "source response-generation task records without_logprobs_fallback=true",
        },
        "metric_computation": {
            "status": "blocked" if real_rows == 0 else "ready_for_bounded_metric_task",
            "reason": "metric computation is out of scope for this repair package",
        },
        "full_matrix": {
            "status": "not_run",
            "reason": "bounded AdvBench small-slice only",
        },
    }


def _report(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# DualScope AdvBench Small-Slice Response Generation Repair",
            "",
            "This repair/compression package does not print harmful prompts or model completions.",
            "",
            f"- Final verdict: `{summary['final_verdict']}`",
            f"- Repair for: `{summary['repair_for']}`",
            f"- Source verdict: `{summary['source_final_verdict']}`",
            f"- Source blocker type: `{summary['source_blocker_type'] or 'none'}`",
            f"- Real response rows: `{summary['real_response_rows']}`",
            f"- Blocked rows: `{summary['blocked_rows']}`",
            f"- Recommended next step: `{summary['recommended_next_step']}`",
            f"- Routing reason: `{summary['routing_reason']}`",
            "- Model responses fabricated: `False`",
            "- Logprobs fabricated: `False`",
            "- Metrics computed: `False`",
            "- Benchmark truth changed: `False`",
            "- Gates changed: `False`",
            "- Full matrix executed: `False`",
            "- Training executed: `False`",
            "- route_c continued: `False`",
            "- 199+ generated: `False`",
            "",
        ]
    )


def build_advbench_small_slice_response_generation_repair(
    *,
    response_dir: Path = DEFAULT_RESPONSE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    seed: int = 20260427,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = response_dir / "advbench_small_slice_response_generation_summary.json"
    blockers_path = response_dir / "advbench_small_slice_response_generation_blockers.json"
    verdict_path = response_dir / "advbench_small_slice_response_generation_verdict.json"
    rows_path = response_dir / "advbench_small_slice_responses.jsonl"

    missing_inputs = [
        str(path)
        for path in (summary_path, blockers_path, verdict_path, rows_path)
        if not path.exists()
    ]
    if missing_inputs:
        source_summary: dict[str, Any] = {}
        source_blockers: dict[str, Any] = {"blockers": missing_inputs, "blocker_type": "missing_input"}
        source_verdict: dict[str, Any] = {}
        rows: list[dict[str, Any]] = []
    else:
        source_summary = read_json(summary_path)
        source_blockers = read_json(blockers_path)
        source_verdict = read_json(verdict_path)
        rows = read_jsonl(rows_path)

    row_audit = _row_audit(rows)
    blockers = [str(item) for item in source_summary.get("blockers") or source_blockers.get("blockers") or []]
    source_blocker_type = str(source_summary.get("blocker_type") or source_blockers.get("blocker_type") or "")
    next_step, routing_reason = _blocker_route(source_blocker_type, blockers)

    source_final = str(source_summary.get("final_verdict") or source_verdict.get("verdict") or "")
    explicit_blocker = bool(source_blocker_type and blockers)
    clean_nonfabricated_contract = (
        not bool(source_summary.get("model_response_fabricated"))
        and not bool(source_summary.get("logprobs_fabricated"))
        and not bool(source_summary.get("metrics_computed"))
        and not bool(source_summary.get("benchmark_truth_changed"))
        and not bool(source_summary.get("gate_changed"))
    )

    if missing_inputs:
        final_verdict = NOT_VALIDATED
        next_step = "dualscope-advbench-small-slice-response-generation-blocker-closure"
        routing_reason = "missing_repair_inputs"
    elif row_audit["real_response_rows"] > 0 and row_audit["fabricated_response_rows"] == 0:
        final_verdict = VALIDATED
        next_step = "dualscope-advbench-small-slice-metric-computation"
        routing_reason = "real_response_rows_available"
    elif explicit_blocker and clean_nonfabricated_contract and row_audit["fabricated_response_rows"] == 0:
        final_verdict = VALIDATED
    else:
        final_verdict = PARTIAL

    availability = _availability_matrix(source_summary, row_audit)
    blocker_compression = {
        "summary_status": "PASS" if final_verdict == VALIDATED else "FAIL" if final_verdict == NOT_VALIDATED else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "repair_for": SOURCE_TASK_ID,
        "source_blocker_type": source_blocker_type,
        "source_blockers": blockers,
        "routing_reason": routing_reason,
        "recommended_next_step": next_step,
        "cuda_blocker_preserved": source_blocker_type in {"torch_cuda_unavailable", "cuda_unavailable"},
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
    }
    summary = {
        "summary_status": "PASS" if final_verdict == VALIDATED else "FAIL" if final_verdict == NOT_VALIDATED else "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "created_at": utc_now(),
        "seed": seed,
        "final_verdict": final_verdict,
        "repair_for": SOURCE_TASK_ID,
        "source_output_dir": str(response_dir),
        "source_final_verdict": source_final,
        "source_blocker_type": source_blocker_type,
        "source_blockers": blockers,
        "real_response_rows": row_audit["real_response_rows"],
        "blocked_rows": row_audit["blocked_rows"],
        "row_audit": row_audit,
        "availability_matrix": availability,
        "blocker_compression": blocker_compression,
        "recommended_next_step": next_step,
        "routing_reason": routing_reason,
        "missing_inputs": missing_inputs,
        "without_logprobs_fallback": bool(source_summary.get("without_logprobs_fallback", True)),
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
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
        "validated": final_verdict == VALIDATED,
        "partially_validated": final_verdict == PARTIAL,
        "not_validated": final_verdict == NOT_VALIDATED,
        "created_at": summary["created_at"],
        "source_output_dir": str(output_dir),
        "repair_for": SOURCE_TASK_ID,
        "next_task": next_step,
        "generated_rows": row_audit["real_response_rows"],
        "blocked_rows": row_audit["blocked_rows"],
        "blocker_type": source_blocker_type,
        "routing_reason": routing_reason,
        "without_logprobs_fallback": summary["without_logprobs_fallback"],
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "full_matrix_executed": False,
        "training_executed": False,
        "route_c_continued": False,
        "generated_199_plus": False,
    }

    compact_rows = [
        {
            "sample_id": row.get("sample_id"),
            "dataset_id": row.get("dataset_id"),
            "response_generation_status": row.get("response_generation_status"),
            "model_response_present": bool(str(row.get("model_response") or "").strip()),
            "model_response_sha256": row.get("model_response_sha256", ""),
            "model_output_fabricated": bool(row.get("model_output_fabricated")),
            "without_logprobs_fallback": bool(row.get("without_logprobs_fallback", True)),
            "blocker": row.get("blocker", ""),
        }
        for row in rows
    ]
    write_json(output_dir / "advbench_small_slice_response_generation_repair_summary.json", summary)
    write_json(output_dir / "advbench_small_slice_response_generation_repair_availability_matrix.json", availability)
    write_json(output_dir / "advbench_small_slice_response_generation_repair_blocker_compression.json", blocker_compression)
    write_json(output_dir / "advbench_small_slice_response_generation_repair_row_audit.json", row_audit)
    write_jsonl(output_dir / "advbench_small_slice_response_generation_repair_compact_rows.jsonl", compact_rows)
    write_json(output_dir / "advbench_small_slice_response_generation_repair_verdict.json", verdict)
    write_text(output_dir / "advbench_small_slice_response_generation_repair_report.md", _report(summary))
    write_json(registry_path, verdict)
    return summary
