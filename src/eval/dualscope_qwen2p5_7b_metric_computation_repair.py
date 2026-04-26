"""Audit and package Qwen2.5-7B metric computation repair artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscope/qwen2p5-7b-metric-computation-repair/v1"
TASK_NAME = "dualscope-qwen2p5-7b-metric-computation-repair"
FINAL_VALIDATED = "Qwen2.5-7B metric computation repair validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"

METRIC_PREFIX = "dualscope_qwen2p5_7b_label_aligned_metric_computation"
BLOCKER_PREFIX = "dualscope_qwen2p5_7b_metric_blocker_closure"

UTILITY_SUCCESS_FIELDS = (
    "clean_utility_success",
    "utility_success",
    "reference_match",
    "response_reference_matched",
)


@dataclass(frozen=True)
class RepairInputs:
    metric_dir: Path
    blocker_dir: Path
    response_dir: Path
    label_metric_registry: Path
    blocker_registry: Path
    output_dir: Path
    analysis_dir: Path
    verdict_registry: Path


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


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_markdown(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([f"# {title}", "", *lines, ""]) + "\n", encoding="utf-8")


def _run_py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_qwen2p5_7b_metric_computation_repair.py",
        "scripts/build_dualscope_qwen2p5_7b_metric_computation_repair.py",
    ]
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


def _current_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _metric_path(metric_dir: Path, suffix: str) -> Path:
    return metric_dir / f"{METRIC_PREFIX}_{suffix}"


def _blocker_path(blocker_dir: Path, suffix: str) -> Path:
    return blocker_dir / f"{BLOCKER_PREFIX}_{suffix}"


def _utility_success(row: dict[str, Any]) -> bool | None:
    for field in UTILITY_SUCCESS_FIELDS:
        value = row.get(field)
        if isinstance(value, bool):
            return value
        if isinstance(value, int) and value in (0, 1):
            return bool(value)
    return None


def _is_metric_pass(payload: dict[str, Any]) -> bool:
    return payload.get("summary_status") == "PASS" and payload.get("metrics_computed") is True


def _aligned_rows_are_real(rows: list[dict[str, Any]]) -> bool:
    if not rows:
        return False
    for row in rows:
        if row.get("model_response_fabricated") is True:
            return False
        if row.get("model_response_present") is not True:
            return False
        response = row.get("model_response")
        if not isinstance(response, str) or not response.strip():
            return False
    return True


def _real_metric_summary(
    *,
    detection: dict[str, Any],
    asr: dict[str, Any],
    utility: dict[str, Any],
    aligned_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    real_rows_ready = _aligned_rows_are_real(aligned_rows)
    detection_reportable = _is_metric_pass(detection) and real_rows_ready
    asr_reportable = _is_metric_pass(asr) and real_rows_ready and asr.get("model_responses_fabricated") is False
    utility_reportable = _is_metric_pass(utility) and real_rows_ready

    return {
        "summary_status": "PASS" if detection_reportable and asr_reportable and utility_reportable else "PARTIAL"
        if detection_reportable or asr_reportable
        else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "aligned_real_response_row_count": len(aligned_rows) if real_rows_ready else 0,
        "detection_metrics": {
            "reportable": detection_reportable,
            "source_status": detection.get("summary_status", "MISSING"),
            "row_count": detection.get("row_count", 0),
            "auroc": detection.get("auroc") if detection_reportable else None,
            "auprc": detection.get("auprc") if detection_reportable else None,
            "tpr_at_fpr_1pct": detection.get("tpr_at_fpr_1pct") if detection_reportable else None,
            "precision": detection.get("precision") if detection_reportable else None,
            "recall": detection.get("recall") if detection_reportable else None,
            "f1": detection.get("f1") if detection_reportable else None,
            "accuracy": detection.get("accuracy") if detection_reportable else None,
            "threshold": detection.get("threshold") if detection_reportable else None,
        },
        "asr": {
            "reportable": asr_reportable,
            "source_status": asr.get("summary_status", "MISSING"),
            "eligible_row_count": asr.get("eligible_row_count", 0),
            "target_match_success_count": asr.get("target_match_success_count") if asr_reportable else None,
            "asr": asr.get("asr") if asr_reportable else None,
        },
        "clean_utility": {
            "reportable": utility_reportable,
            "source_status": utility.get("summary_status", "MISSING"),
            "eligible_row_count": utility.get("eligible_row_count", 0),
            "clean_utility": utility.get("clean_utility") if utility_reportable else None,
            "blocked_unless_explicit_success_fields_present": not utility_reportable,
            "supported_explicit_success_fields": list(UTILITY_SUCCESS_FIELDS),
        },
        "metrics_computed_from_placeholders": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
    }


def _availability_matrix(
    *,
    metric_summary: dict[str, Any],
    source_audit: dict[str, Any],
    readiness: dict[str, Any],
    detection: dict[str, Any],
    asr: dict[str, Any],
    utility: dict[str, Any],
    real_summary: dict[str, Any],
) -> dict[str, Any]:
    rows = [
        {
            "metric": "detection_metrics",
            "artifact_status": detection.get("summary_status", "MISSING"),
            "reportable": real_summary["detection_metrics"]["reportable"],
            "required_evidence": "aligned detection_label, final_risk_score, and real Qwen2.5-7B response rows",
            "blocker": "" if real_summary["detection_metrics"]["reportable"] else detection.get("reason", "Detection metric artifact is not PASS."),
        },
        {
            "metric": "attack_success_rate",
            "artifact_status": asr.get("summary_status", "MISSING"),
            "reportable": real_summary["asr"]["reportable"],
            "required_evidence": "real poisoned-triggered Qwen2.5-7B response rows with target_matched",
            "blocker": "" if real_summary["asr"]["reportable"] else asr.get("reason", "ASR artifact is not PASS."),
        },
        {
            "metric": "clean_utility",
            "artifact_status": utility.get("summary_status", "MISSING"),
            "reportable": real_summary["clean_utility"]["reportable"],
            "required_evidence": "real clean response rows plus explicit utility success/reference-match fields",
            "blocker": "" if real_summary["clean_utility"]["reportable"] else utility.get("reason", "Clean utility lacks explicit success fields."),
        },
    ]
    return {
        "summary_status": real_summary["summary_status"],
        "schema_version": SCHEMA_VERSION,
        "metric_cli_final_verdict": metric_summary.get("final_verdict"),
        "metric_cli_aligned_row_count": metric_summary.get("aligned_metric_row_count", 0),
        "labels_ready": readiness.get("labels_ready", False),
        "scores_ready": readiness.get("scores_ready", False),
        "real_responses_ready": readiness.get("real_responses_ready", False),
        "source_audit_status": source_audit.get("summary_status", "MISSING"),
        "rows": rows,
    }


def _blockers(
    *,
    metric_blockers: dict[str, Any],
    blocker_categories: dict[str, Any],
    availability: dict[str, Any],
    real_summary: dict[str, Any],
) -> dict[str, Any]:
    unavailable = [row for row in availability["rows"] if row["reportable"] is not True]
    return {
        "summary_status": "BLOCKED" if unavailable else "PASS",
        "schema_version": SCHEMA_VERSION,
        "metric_cli_blockers": metric_blockers.get("blockers", []),
        "blocker_closure_categories": blocker_categories,
        "unavailable_metrics": unavailable,
        "essential_detection_metrics_unavailable": not real_summary["detection_metrics"]["reportable"],
        "clean_utility_blocker_is_explicit": not real_summary["clean_utility"]["reportable"],
    }


def build_metric_computation_repair(
    *,
    metric_dir: Path,
    blocker_dir: Path,
    response_dir: Path,
    label_metric_registry: Path,
    blocker_registry: Path,
    output_dir: Path,
    analysis_dir: Path,
    verdict_registry: Path,
    seed: int,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    inputs = RepairInputs(
        metric_dir=metric_dir,
        blocker_dir=blocker_dir,
        response_dir=response_dir,
        label_metric_registry=label_metric_registry,
        blocker_registry=blocker_registry,
        output_dir=output_dir,
        analysis_dir=analysis_dir,
        verdict_registry=verdict_registry,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    metric_summary = maybe_read_json(_metric_path(inputs.metric_dir, "summary.json"))
    source_audit = maybe_read_json(_metric_path(inputs.metric_dir, "source_audit.json"))
    readiness = maybe_read_json(_metric_path(inputs.metric_dir, "metric_readiness.json"))
    detection = maybe_read_json(_metric_path(inputs.metric_dir, "detection_metrics.json"))
    asr = maybe_read_json(_metric_path(inputs.metric_dir, "asr_metrics.json"))
    utility = maybe_read_json(_metric_path(inputs.metric_dir, "clean_utility_metrics.json"))
    metric_blockers = maybe_read_json(_metric_path(inputs.metric_dir, "blockers.json"))
    aligned_rows = read_jsonl(_metric_path(inputs.metric_dir, "aligned_rows.jsonl"))

    blocker_summary = maybe_read_json(_blocker_path(inputs.blocker_dir, "summary.json"))
    blocker_categories = maybe_read_json(_blocker_path(inputs.blocker_dir, "blocker_categories.json"))
    label_registry = maybe_read_json(inputs.label_metric_registry)
    blocker_registry_payload = maybe_read_json(inputs.blocker_registry)

    real_summary = _real_metric_summary(
        detection=detection,
        asr=asr,
        utility=utility,
        aligned_rows=aligned_rows,
    )
    availability = _availability_matrix(
        metric_summary=metric_summary,
        source_audit=source_audit,
        readiness=readiness,
        detection=detection,
        asr=asr,
        utility=utility,
        real_summary=real_summary,
    )
    blockers = _blockers(
        metric_blockers=metric_blockers,
        blocker_categories=blocker_categories,
        availability=availability,
        real_summary=real_summary,
    )

    detection_ready = real_summary["detection_metrics"]["reportable"]
    asr_ready = real_summary["asr"]["reportable"]
    utility_ready = real_summary["clean_utility"]["reportable"]
    clean_utility_explicit_blocker = not utility_ready and availability["rows"][2]["artifact_status"] in {"BLOCKED", "MISSING"}

    if detection_ready and asr_ready and clean_utility_explicit_blocker:
        final_verdict = FINAL_VALIDATED
        recommended_next_step = "dualscope-qwen2p5-7b-first-slice-result-package"
        summary_status = "PASS"
    elif detection_ready or asr_ready:
        final_verdict = FINAL_PARTIAL
        recommended_next_step = "dualscope-qwen2p5-7b-first-slice-result-package" if detection_ready else "dualscope-qwen2p5-7b-metric-blocker-closure"
        summary_status = "PARTIAL"
    else:
        final_verdict = FINAL_NOT_VALIDATED
        recommended_next_step = "dualscope-qwen2p5-7b-metric-blocker-closure"
        summary_status = "FAIL"

    py_compile = _run_py_compile(repo_root)
    created_at = utc_now()
    limitations = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "items": [
            "This repair package reports metrics only from local metric artifacts with PASS status.",
            "Prior registries are used as routing history, not as metric value sources.",
            "Clean utility remains blocked unless explicit utility success/reference-match fields are present.",
            "The package does not infer utility from free-text responses.",
            "No benchmark truth, gates, labels, responses, logprobs, final_risk_score, or route_c artifacts were modified.",
        ],
    }
    if label_registry.get("detection_metrics_computed") and not detection_ready:
        limitations["items"].append(
            "The prior label metric registry claims detection metrics were computed, but the required PASS metric artifact is unavailable or non-PASS in this worktree."
        )
    if label_registry.get("asr_computed") and not asr_ready:
        limitations["items"].append(
            "The prior label metric registry claims ASR was computed, but the required PASS ASR artifact is unavailable or non-PASS in this worktree."
        )

    summary = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "created_at": created_at,
        "seed": seed,
        "final_verdict": final_verdict,
        "recommended_next_step": recommended_next_step,
        "metric_dir": str(metric_dir),
        "blocker_dir": str(blocker_dir),
        "response_dir": str(response_dir),
        "metric_cli_final_verdict": metric_summary.get("final_verdict"),
        "blocker_closure_final_verdict": blocker_summary.get("final_verdict") or blocker_registry_payload.get("verdict"),
        "prior_label_metric_registry_verdict": label_registry.get("verdict"),
        "prior_blocker_registry_verdict": blocker_registry_payload.get("verdict"),
        "aligned_real_response_row_count": real_summary["aligned_real_response_row_count"],
        "detection_metrics_reportable": detection_ready,
        "asr_reportable": asr_ready,
        "clean_utility_reportable": utility_ready,
        "clean_utility_explicitly_blocked": clean_utility_explicit_blocker,
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
    }
    verdict = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommended_next_step,
        "single_verdict_policy": "one_of_metric_computation_repair_validated__partially_validated__not_validated",
    }
    recommendation = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": recommended_next_step,
        "reason": "Detection metrics are unavailable from PASS artifacts in this worktree."
        if not detection_ready
        else "Detection metrics are available; package may proceed with limitations.",
    }
    registry = {
        "task_id": TASK_NAME,
        "verdict": final_verdict,
        "source_output_dir": str(output_dir),
        "commit": _current_commit(repo_root),
        "created_at": created_at,
        "validated": final_verdict == FINAL_VALIDATED,
        "next_task": recommended_next_step,
        "detection_metrics_reportable": detection_ready,
        "asr_reportable": asr_ready,
        "clean_utility_reportable": utility_ready,
    }

    write_json(output_dir / "dualscope_qwen2p5_7b_metric_computation_repair_metric_availability_matrix.json", availability)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_computation_repair_real_metric_summary.json", real_summary)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_computation_repair_unavailable_metric_blockers.json", blockers)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_computation_repair_limitations.json", limitations)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_computation_repair_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_computation_repair_summary.json", summary)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_computation_repair_verdict.json", verdict)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_computation_repair_next_step_recommendation.json", recommendation)
    write_json(analysis_dir / "dualscope_qwen2p5_7b_metric_computation_repair_metric_availability_matrix.json", availability)
    write_json(analysis_dir / "dualscope_qwen2p5_7b_metric_computation_repair_summary.json", summary)
    write_json(analysis_dir / "dualscope_qwen2p5_7b_metric_computation_repair_verdict.json", verdict)
    write_json(verdict_registry, registry)

    write_markdown(
        output_dir / "dualscope_qwen2p5_7b_metric_computation_repair_report.md",
        "DualScope Qwen2.5-7B Metric Computation Repair",
        [
            f"- Final verdict: `{final_verdict}`",
            f"- Metric CLI final verdict: `{metric_summary.get('final_verdict')}`",
            f"- Prior label metric registry verdict: `{label_registry.get('verdict')}`",
            f"- Detection metrics reportable: `{detection_ready}`",
            f"- ASR reportable: `{asr_ready}`",
            f"- Clean utility reportable: `{utility_ready}`",
            f"- Clean utility explicitly blocked: `{clean_utility_explicit_blocker}`",
            f"- Aligned real-response rows used for reportable metrics: `{real_summary['aligned_real_response_row_count']}`",
            f"- Recommended next step: `{recommended_next_step}`",
            "- Clean utility was not inferred from free text.",
            "- Benchmark truth changed: `False`",
            "- Gates changed: `False`",
            "- route_c / 199+ continuation: `False`",
            "- Full matrix executed: `False`",
            "- Training executed: `False`",
        ],
    )
    return summary
