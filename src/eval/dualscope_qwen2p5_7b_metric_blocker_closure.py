"""Close Qwen2.5-7B metric blockers with explicit artifact diagnostics."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscope/qwen2p5-7b-metric-blocker-closure/v1"
TASK_NAME = "dualscope-qwen2p5-7b-metric-blocker-closure"
FINAL_VALIDATED = "Qwen2.5-7B metric blocker closure validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"

LABEL_METRIC_TASK = "dualscope-qwen2p5-7b-label-aligned-metric-computation"
LABEL_METRIC_SUMMARY = "dualscope_qwen2p5_7b_label_aligned_metric_computation_summary.json"
LABEL_METRIC_READINESS = "dualscope_qwen2p5_7b_label_aligned_metric_computation_metric_readiness.json"
LABEL_METRIC_SOURCE_AUDIT = "dualscope_qwen2p5_7b_label_aligned_metric_computation_source_audit.json"
LABEL_METRIC_AVAILABILITY = "dualscope_qwen2p5_7b_label_aligned_metric_computation_availability_matrix.json"
LABEL_METRIC_DETECTION = "dualscope_qwen2p5_7b_label_aligned_metric_computation_detection_metrics.json"
LABEL_METRIC_ASR = "dualscope_qwen2p5_7b_label_aligned_metric_computation_asr_metrics.json"
LABEL_METRIC_UTILITY = "dualscope_qwen2p5_7b_label_aligned_metric_computation_clean_utility_metrics.json"
LABEL_METRIC_BLOCKERS = "dualscope_qwen2p5_7b_label_aligned_metric_computation_blockers.json"

RESPONSE_ROW_CANDIDATES = (
    "dualscope_qwen2p5_7b_first_slice_response_generation_rows.jsonl",
    "qwen2p5_7b_response_rows.jsonl",
    "response_generation_repair_responses.jsonl",
)
SCORE_ROW_CANDIDATES = (
    "dualscope_minimal_first_slice_condition_level_rerun_joined_predictions.jsonl",
    "stage3_fusion/stage3_fusion_outputs.jsonl",
)


@dataclass(frozen=True)
class ClosureInputs:
    labeled_pairs: Path
    response_dir: Path
    score_dir: Path
    metric_dir: Path
    prior_registry: Path
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


def _first_existing(base_dir: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        candidate = base_dir / name
        if candidate.exists():
            return candidate
    return None


def _count_jsonl(path: Path | None) -> int:
    if path is None or not path.exists():
        return 0
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def _run_py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_qwen2p5_7b_metric_blocker_closure.py",
        "scripts/build_dualscope_qwen2p5_7b_metric_blocker_closure.py",
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


def _classify_blockers(
    *,
    inputs: ClosureInputs,
    source_audit: dict[str, Any],
    readiness: dict[str, Any],
    availability: dict[str, Any],
    detection: dict[str, Any],
    asr: dict[str, Any],
    utility: dict[str, Any],
    runtime_audit: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    response_rows_path = _first_existing(inputs.response_dir, RESPONSE_ROW_CANDIDATES)
    score_rows_path = _first_existing(inputs.score_dir, SCORE_ROW_CANDIDATES)
    availability_rows = availability.get("label_score_response_availability_rows")
    if not isinstance(availability_rows, list):
        availability_rows = []

    missing_detection_label_rows = [
        row.get("row_id")
        for row in availability_rows
        if row.get("label_available") is True and row.get("detection_label_available") is not True
    ]
    missing_final_risk_score_rows = [
        row.get("row_id")
        for row in availability_rows
        if row.get("score_available") is True and row.get("final_risk_score_available") is not True
    ]
    missing_response_rows = [
        row.get("row_id")
        for row in availability_rows
        if row.get("label_available") is True and row.get("response_available") is not True
    ]

    categories = {
        "missing_final_risk_score": {
            "blocked": not inputs.score_dir.exists()
            or score_rows_path is None
            or bool(missing_final_risk_score_rows)
            or readiness.get("scores_ready") is not True,
            "score_dir_exists": inputs.score_dir.exists(),
            "score_rows_path": str(score_rows_path) if score_rows_path else "",
            "score_row_count": source_audit.get("score_row_count", 0),
            "missing_final_risk_score_row_ids": missing_final_risk_score_rows[:50],
            "reason": "No condition-level score rows with final_risk_score are available."
            if score_rows_path is None
            else "At least one score row lacks final_risk_score.",
        },
        "missing_detection_label_alignment": {
            "blocked": not inputs.labeled_pairs.exists()
            or readiness.get("label_score_real_response_alignment_ready") is not True
            or detection.get("summary_status") != "PASS"
            or bool(missing_detection_label_rows),
            "labeled_pairs_exists": inputs.labeled_pairs.exists(),
            "labeled_row_count": source_audit.get("labeled_row_count", 0),
            "aligned_metric_row_count": availability.get("aligned_metric_row_count", 0),
            "detection_metrics_status": detection.get("summary_status", "MISSING"),
            "missing_detection_label_row_ids": missing_detection_label_rows[:50],
            "reason": detection.get(
                "reason",
                "Detection labels and final_risk_score are not aligned on real-response rows.",
            ),
        },
        "missing_asr_inputs": {
            "blocked": asr.get("summary_status") != "PASS",
            "asr_status": asr.get("summary_status", "MISSING"),
            "eligible_row_count": asr.get("eligible_row_count", 0),
            "reason": asr.get("reason", "ASR requires real poisoned-triggered rows with target_text/target matching evidence."),
        },
        "missing_utility_inputs": {
            "blocked": utility.get("summary_status") != "PASS",
            "utility_status": utility.get("summary_status", "MISSING"),
            "eligible_row_count": utility.get("eligible_row_count", 0),
            "reason": utility.get(
                "reason",
                "Clean utility requires real clean rows with reference_response and explicit utility success evidence.",
            ),
        },
        "missing_response_artifacts": {
            "blocked": not inputs.response_dir.exists()
            or response_rows_path is None
            or readiness.get("real_responses_ready") is not True
            or bool(missing_response_rows),
            "response_dir_exists": inputs.response_dir.exists(),
            "response_rows_path": str(response_rows_path) if response_rows_path else "",
            "response_row_count": source_audit.get("response_row_count", 0),
            "real_responses_ready": readiness.get("real_responses_ready", False),
            "missing_response_row_ids": missing_response_rows[:50],
            "reason": "No Qwen2.5-7B response row artifact is present at the expected response directory."
            if response_rows_path is None
            else "Response rows exist but do not align to labels/scores as real model responses.",
        },
        "logprob_unavailable_fallback": {
            "blocked": response_rows_path is None,
            "confirmed_without_logprobs_fallback": False,
            "logprobs_available": None,
            "reason": "Logprob/capability flags cannot be evaluated because response artifacts are missing."
            if response_rows_path is None
            else "Response artifacts should be inspected for logprobs_available before logprob-dependent metrics are claimed.",
        },
        "schema_mismatch": {
            "blocked": False,
            "reason": "No schema mismatch was observed; required artifacts are missing before row schema can be validated."
            if not availability_rows
            else "Metric artifact schema was readable.",
        },
        "runtime_errors": {
            "blocked": runtime_audit.get("venv_python_available") is not True,
            "venv_python_available": runtime_audit.get("venv_python_available", False),
            "python3_metric_cli_returncode": runtime_audit.get("python3_metric_cli_returncode"),
            "reason": "Requested .venv/bin/python is absent; python3 metric CLI ran and returned the task's Not validated exit code."
            if runtime_audit.get("venv_python_available") is not True
            else "No runtime error blocker recorded.",
        },
    }

    rows = [
        {
            "blocker_category": name,
            "blocked": bool(payload["blocked"]),
            "reason": payload.get("reason", ""),
        }
        for name, payload in categories.items()
    ]
    return categories, rows


def build_metric_blocker_closure(
    *,
    labeled_pairs: Path,
    response_dir: Path,
    score_dir: Path,
    metric_dir: Path,
    prior_registry: Path,
    output_dir: Path,
    analysis_dir: Path,
    verdict_registry: Path,
    python3_metric_cli_returncode: int | None = None,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    inputs = ClosureInputs(
        labeled_pairs=labeled_pairs,
        response_dir=response_dir,
        score_dir=score_dir,
        metric_dir=metric_dir,
        prior_registry=prior_registry,
        output_dir=output_dir,
        analysis_dir=analysis_dir,
        verdict_registry=verdict_registry,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    prior = maybe_read_json(prior_registry)
    source_audit = maybe_read_json(metric_dir / LABEL_METRIC_SOURCE_AUDIT)
    readiness = maybe_read_json(metric_dir / LABEL_METRIC_READINESS)
    availability = maybe_read_json(metric_dir / LABEL_METRIC_AVAILABILITY)
    detection = maybe_read_json(metric_dir / LABEL_METRIC_DETECTION)
    asr = maybe_read_json(metric_dir / LABEL_METRIC_ASR)
    utility = maybe_read_json(metric_dir / LABEL_METRIC_UTILITY)
    metric_summary = maybe_read_json(metric_dir / LABEL_METRIC_SUMMARY)
    metric_blockers = maybe_read_json(metric_dir / LABEL_METRIC_BLOCKERS)

    response_rows_path = _first_existing(response_dir, RESPONSE_ROW_CANDIDATES)
    score_rows_path = _first_existing(score_dir, SCORE_ROW_CANDIDATES)
    source_inventory = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "labeled_pairs_path": str(labeled_pairs),
        "labeled_pairs_exists": labeled_pairs.exists(),
        "labeled_pair_row_count": _count_jsonl(labeled_pairs) if labeled_pairs.exists() else 0,
        "response_dir": str(response_dir),
        "response_dir_exists": response_dir.exists(),
        "response_rows_path": str(response_rows_path) if response_rows_path else "",
        "response_row_count": _count_jsonl(response_rows_path),
        "score_dir": str(score_dir),
        "score_dir_exists": score_dir.exists(),
        "score_rows_path": str(score_rows_path) if score_rows_path else "",
        "score_row_count": _count_jsonl(score_rows_path),
        "metric_dir": str(metric_dir),
        "metric_dir_exists": metric_dir.exists(),
        "prior_registry_path": str(prior_registry),
        "prior_registry_exists": prior_registry.exists(),
        "prior_registry_verdict": prior.get("verdict"),
    }
    source_inventory["summary_status"] = (
        "PASS"
        if source_inventory["labeled_pairs_exists"]
        and source_inventory["response_rows_path"]
        and source_inventory["score_rows_path"]
        else "FAIL"
    )

    runtime_audit = {
        "summary_status": "PARTIAL",
        "schema_version": SCHEMA_VERSION,
        "requested_venv_python": ".venv/bin/python",
        "venv_python_available": (repo_root / ".venv/bin/python").exists(),
        "python3_metric_cli_returncode": python3_metric_cli_returncode,
        "metric_cli_output_dir": str(metric_dir),
    }
    categories, blocker_rows = _classify_blockers(
        inputs=inputs,
        source_audit=source_audit,
        readiness=readiness,
        availability=availability,
        detection=detection,
        asr=asr,
        utility=utility,
        runtime_audit=runtime_audit,
    )
    blocked_categories = [name for name, payload in categories.items() if payload.get("blocked")]
    detection_computed = detection.get("summary_status") == "PASS"
    asr_computed = asr.get("summary_status") == "PASS"
    clean_utility_computed = utility.get("summary_status") == "PASS"
    metrics_available = (
        detection_computed
        and asr_computed
        and clean_utility_computed
    )
    partial_metric_progress = detection_computed or asr_computed
    repair_only = bool(blocked_categories) and set(blocked_categories).issubset(
        {
            "missing_final_risk_score",
            "missing_detection_label_alignment",
            "missing_asr_inputs",
            "missing_utility_inputs",
            "missing_response_artifacts",
            "logprob_unavailable_fallback",
            "runtime_errors",
        }
    )

    if metrics_available:
        final_verdict = FINAL_VALIDATED
        next_task = "dualscope-qwen2p5-7b-first-slice-result-package"
        summary_status = "PASS"
    elif repair_only and partial_metric_progress:
        final_verdict = FINAL_PARTIAL
        next_task = "dualscope-qwen2p5-7b-metric-computation-repair"
        summary_status = "PARTIAL"
    else:
        final_verdict = FINAL_NOT_VALIDATED
        next_task = "dualscope-qwen2p5-7b-metric-blocker-closure"
        summary_status = "FAIL"

    py_compile = _run_py_compile(repo_root)
    summary = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "created_at": utc_now(),
        "final_verdict": final_verdict,
        "recommended_next_step": next_task,
        "prior_metric_task_verdict": prior.get("verdict"),
        "metric_cli_final_verdict": metric_summary.get("final_verdict"),
        "metric_cli_aligned_row_count": metric_summary.get("aligned_metric_row_count", 0),
        "detection_metrics_computed": detection_computed,
        "asr_computed": asr_computed,
        "clean_utility_computed": clean_utility_computed,
        "partial_metric_progress": partial_metric_progress,
        "blocked_categories": blocked_categories,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "training_executed": False,
        "full_matrix_executed": False,
        "route_c_199_plus_generated": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
    }
    verdict = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": next_task,
        "single_verdict_policy": "one_of_metric_blocker_closure_validated__partially_validated__not_validated",
    }
    registry = {
        "task_id": TASK_NAME,
        "verdict": final_verdict,
        "source_output_dir": str(output_dir),
        "commit": _current_commit(repo_root),
        "created_at": summary["created_at"],
        "validated": final_verdict == FINAL_VALIDATED,
        "next_task": next_task,
    }

    write_json(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_source_inventory.json", source_inventory)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_runtime_audit.json", runtime_audit)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_prior_metric_registry.json", prior)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_metric_cli_summary.json", metric_summary)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_metric_cli_blockers.json", metric_blockers)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_blocker_categories.json", categories)
    write_jsonl(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_blocker_rows.jsonl", blocker_rows)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_summary.json", summary)
    write_json(output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_verdict.json", verdict)
    write_json(
        output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_next_step_recommendation.json",
        {
            "summary_status": summary_status,
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": next_task,
        },
    )
    write_json(analysis_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_summary.json", summary)
    write_json(analysis_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_verdict.json", verdict)
    write_json(analysis_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_blocker_categories.json", categories)
    write_json(verdict_registry, registry)

    write_markdown(
        output_dir / "dualscope_qwen2p5_7b_metric_blocker_closure_report.md",
        "DualScope Qwen2.5-7B Metric Blocker Closure",
        [
            f"- Final verdict: `{final_verdict}`",
            f"- Prior metric task verdict: `{prior.get('verdict')}`",
            f"- Metric CLI final verdict: `{metric_summary.get('final_verdict')}`",
            f"- Labeled pairs present: `{source_inventory['labeled_pairs_exists']}`",
            f"- Response rows present: `{bool(source_inventory['response_rows_path'])}`",
            f"- Score rows present: `{bool(source_inventory['score_rows_path'])}`",
            f"- Aligned metric rows: `{metric_summary.get('aligned_metric_row_count', 0)}`",
            f"- Detection metrics computed: `{detection.get('summary_status') == 'PASS'}`",
            f"- ASR computed: `{asr.get('summary_status') == 'PASS'}`",
            f"- Clean utility computed: `{utility.get('summary_status') == 'PASS'}`",
            f"- Blocked categories: `{blocked_categories}`",
            f"- Recommended next step: `{next_task}`",
            "- Benchmark truth changed: `False`",
            "- Gates changed: `False`",
            "- route_c / 199+ continuation: `False`",
        ],
    )
    return summary
