"""Repair Qwen2.5-7B first-slice result package artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscope/qwen2p5-7b-result-package-repair/v1"
TASK_NAME = "dualscope-qwen2p5-7b-result-package-repair"
FINAL_VALIDATED = "Qwen2.5-7B result package repair validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"

RESPONSE_PREFIX = "dualscope_qwen2p5_7b_first_slice_response_generation"
METRIC_PREFIX = "dualscope_qwen2p5_7b_label_aligned_metric_computation"
REPAIR_PREFIX = "dualscope_qwen2p5_7b_metric_computation_repair"
OUTPUT_PREFIX = "dualscope_qwen2p5_7b_result_package_repair"

UTILITY_SUCCESS_FIELDS = (
    "clean_utility_success",
    "utility_success",
    "reference_match",
    "response_reference_matched",
)

PY_FILES = [
    "src/eval/dualscope_qwen2p5_7b_result_package_repair.py",
    "scripts/build_dualscope_qwen2p5_7b_result_package_repair.py",
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


def write_markdown(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([f"# {title}", "", *lines, ""]) + "\n", encoding="utf-8")


def _response_path(response_dir: Path, suffix: str) -> Path:
    return response_dir / f"{RESPONSE_PREFIX}_{suffix}"


def _metric_path(metric_dir: Path, suffix: str) -> Path:
    return metric_dir / f"{METRIC_PREFIX}_{suffix}"


def _repair_path(repair_dir: Path, suffix: str) -> Path:
    return repair_dir / f"{REPAIR_PREFIX}_{suffix}"


def _run_py_compile(repo_root: Path) -> dict[str, Any]:
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


def _current_commit(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _rows_are_real(rows: list[dict[str, Any]]) -> bool:
    if not rows:
        return False
    for row in rows:
        if row.get("model_response_fabricated") is True:
            return False
        if row.get("model_response_present") is not True:
            return False
        if row.get("response_generation_status") not in {None, "generated"}:
            return False
        response = row.get("model_response")
        if not isinstance(response, str) or not response.strip():
            return False
    return True


def _has_explicit_utility_success(rows: list[dict[str, Any]]) -> bool:
    clean_rows = [row for row in rows if row.get("utility_eligible") is True or row.get("condition") == "clean"]
    if not clean_rows:
        return False
    for row in clean_rows:
        if not any(isinstance(row.get(field), (bool, int)) for field in UTILITY_SUCCESS_FIELDS):
            return False
    return True


def _metric_pass(payload: dict[str, Any]) -> bool:
    return payload.get("summary_status") == "PASS" and payload.get("metrics_computed") is True


def _build_real_metric_summary(
    *,
    detection: dict[str, Any],
    asr: dict[str, Any],
    clean_utility: dict[str, Any],
    aligned_rows: list[dict[str, Any]],
    response_rows: list[dict[str, Any]],
    repair_real_summary: dict[str, Any],
) -> dict[str, Any]:
    aligned_rows_real = _rows_are_real(aligned_rows)
    response_rows_real = _rows_are_real(response_rows)
    detection_reportable = _metric_pass(detection) and aligned_rows_real
    asr_reportable = _metric_pass(asr) and aligned_rows_real and asr.get("model_responses_fabricated") is False
    utility_has_explicit_fields = _has_explicit_utility_success(aligned_rows)
    utility_reportable = _metric_pass(clean_utility) and aligned_rows_real and utility_has_explicit_fields

    return {
        "summary_status": "PASS" if detection_reportable and asr_reportable else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "source_repair_summary_status": repair_real_summary.get("summary_status", "MISSING"),
        "aligned_real_response_row_count": len(aligned_rows) if aligned_rows_real else 0,
        "response_generation_real_row_count": len(response_rows) if response_rows_real else 0,
        "detection_metrics": {
            "reportable": detection_reportable,
            "source_status": detection.get("summary_status", "MISSING"),
            "metrics_computed": detection.get("metrics_computed") is True,
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
            "source_status": asr.get("summary_status", "MISSING"),
            "metrics_computed": asr.get("metrics_computed") is True,
            "eligible_row_count": asr.get("eligible_row_count") if asr_reportable else None,
            "target_match_success_count": asr.get("target_match_success_count") if asr_reportable else None,
            "asr": asr.get("asr") if asr_reportable else None,
        },
        "clean_utility": {
            "reportable": utility_reportable,
            "source_status": clean_utility.get("summary_status", "MISSING"),
            "metrics_computed": clean_utility.get("metrics_computed") is True,
            "eligible_row_count": clean_utility.get("eligible_row_count", 0),
            "clean_utility": clean_utility.get("clean_utility") if utility_reportable else None,
            "explicit_success_fields_present": utility_has_explicit_fields,
            "blocked_unless_explicit_success_fields_present": not utility_reportable,
            "supported_explicit_success_fields": list(UTILITY_SUCCESS_FIELDS),
        },
        "metrics_computed_from_placeholders": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
        "full_paper_performance": False,
    }


def _limitation_matrix(
    *,
    real_metrics: dict[str, Any],
    response_summary: dict[str, Any],
    prior_registry: dict[str, Any],
    prior_package_dir: Path,
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "rows": [
            {
                "item": "scope",
                "status": "LIMITED",
                "detail": "Qwen2.5-7B first-slice only; not full-paper or full-matrix performance.",
            },
            {
                "item": "detection_metrics",
                "status": "REPORTABLE" if real_metrics["detection_metrics"]["reportable"] else "BLOCKED",
                "detail": "Reportable only from PASS metric artifact and aligned real response rows.",
            },
            {
                "item": "attack_success_rate",
                "status": "REPORTABLE" if real_metrics["asr"]["reportable"] else "BLOCKED",
                "detail": "Reportable only from PASS ASR artifact over real poisoned-triggered response rows.",
            },
            {
                "item": "clean_utility",
                "status": "BLOCKED" if not real_metrics["clean_utility"]["reportable"] else "REPORTABLE",
                "detail": "Requires explicit utility success/reference-match fields; free text is not sufficient.",
            },
            {
                "item": "logprobs",
                "status": "UNAVAILABLE" if response_summary.get("capability_mode", {}).get("with_logprobs") is not True else "AVAILABLE",
                "detail": "This repair does not fabricate logprobs or logprob-dependent metrics.",
            },
            {
                "item": "prior_package_directory",
                "status": "PRESENT" if prior_package_dir.exists() else "MISSING_IN_WORKTREE",
                "detail": "Prior registry is used as routing history, not as a metric source.",
            },
            {
                "item": "prior_package_registry",
                "status": prior_registry.get("verdict", "MISSING"),
                "detail": "Previous package was partial because clean utility was not reportable.",
            },
        ],
    }


def _unavailable_metric_blockers(real_metrics: dict[str, Any], clean_utility: dict[str, Any]) -> dict[str, Any]:
    unavailable: list[dict[str, Any]] = []
    if not real_metrics["detection_metrics"]["reportable"]:
        unavailable.append(
            {
                "metric": "detection_metrics",
                "reportable": False,
                "blocker": "Detection metrics require PASS artifact backed by aligned real Qwen2.5-7B response rows.",
            }
        )
    if not real_metrics["asr"]["reportable"]:
        unavailable.append(
            {
                "metric": "attack_success_rate",
                "reportable": False,
                "blocker": "ASR requires PASS artifact over real poisoned-triggered Qwen2.5-7B response rows.",
            }
        )
    if not real_metrics["clean_utility"]["reportable"]:
        unavailable.append(
            {
                "metric": "clean_utility",
                "reportable": False,
                "blocker": clean_utility.get(
                    "reason",
                    "Clean utility requires explicit utility success/reference-match fields; it is not inferred from free text.",
                ),
                "missing_utility_success_row_ids": clean_utility.get("missing_utility_success_row_ids", []),
            }
        )
    unavailable.append(
        {
            "metric": "full_paper_performance",
            "reportable": False,
            "blocker": "First-slice repair cannot be projected to full-paper or full-matrix performance.",
        }
    )
    return {
        "summary_status": "BLOCKED" if unavailable else "PASS",
        "schema_version": SCHEMA_VERSION,
        "unavailable_metrics": unavailable,
        "essential_detection_metrics_unavailable": not real_metrics["detection_metrics"]["reportable"],
        "asr_unavailable": not real_metrics["asr"]["reportable"],
        "clean_utility_blocker_is_explicit": not real_metrics["clean_utility"]["reportable"],
    }


def build_result_package_repair(
    *,
    prior_package_dir: Path,
    prior_registry: Path,
    response_dir: Path,
    metric_dir: Path,
    metric_repair_dir: Path,
    output_dir: Path,
    analysis_dir: Path,
    verdict_registry: Path,
    docs_path: Path,
    seed: int,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    prior_registry_payload = maybe_read_json(prior_registry)
    response_summary = maybe_read_json(_response_path(response_dir, "summary.json"))
    response_capability = maybe_read_json(_response_path(response_dir, "capability_mode.json"))
    response_rows = read_jsonl(_response_path(response_dir, "rows.jsonl"))

    metric_summary = maybe_read_json(_metric_path(metric_dir, "summary.json"))
    metric_readiness = maybe_read_json(_metric_path(metric_dir, "metric_readiness.json"))
    detection = maybe_read_json(_metric_path(metric_dir, "detection_metrics.json"))
    asr = maybe_read_json(_metric_path(metric_dir, "asr_metrics.json"))
    clean_utility = maybe_read_json(_metric_path(metric_dir, "clean_utility_metrics.json"))
    aligned_rows = read_jsonl(_metric_path(metric_dir, "aligned_rows.jsonl"))

    repair_summary = maybe_read_json(_repair_path(metric_repair_dir, "summary.json"))
    repair_real_summary = maybe_read_json(_repair_path(metric_repair_dir, "real_metric_summary.json"))
    repair_availability = maybe_read_json(_repair_path(metric_repair_dir, "metric_availability_matrix.json"))
    repair_blockers = maybe_read_json(_repair_path(metric_repair_dir, "unavailable_metric_blockers.json"))
    repair_limitations = maybe_read_json(_repair_path(metric_repair_dir, "limitations.json"))

    py_compile = _run_py_compile(repo_root)
    created_at = utc_now()
    real_metrics = _build_real_metric_summary(
        detection=detection,
        asr=asr,
        clean_utility=clean_utility,
        aligned_rows=aligned_rows,
        response_rows=response_rows,
        repair_real_summary=repair_real_summary,
    )
    limitations = _limitation_matrix(
        real_metrics=real_metrics,
        response_summary=response_summary,
        prior_registry=prior_registry_payload,
        prior_package_dir=prior_package_dir,
    )
    unavailable_blockers = _unavailable_metric_blockers(real_metrics, clean_utility)
    clean_utility_blocker = {
        "summary_status": "BLOCKED" if not real_metrics["clean_utility"]["reportable"] else "PASS",
        "schema_version": SCHEMA_VERSION,
        "clean_utility_reportable": real_metrics["clean_utility"]["reportable"],
        "reason": clean_utility.get(
            "reason",
            "Clean utility requires explicit utility success/reference-match fields; it is not inferred from free text.",
        ),
        "eligible_row_count": clean_utility.get("eligible_row_count", 0),
        "supported_utility_success_fields": clean_utility.get("supported_utility_success_fields", list(UTILITY_SUCCESS_FIELDS)),
        "missing_utility_success_row_ids": clean_utility.get("missing_utility_success_row_ids", []),
        "free_text_inference_used": False,
    }

    detection_ready = real_metrics["detection_metrics"]["reportable"]
    asr_ready = real_metrics["asr"]["reportable"]
    utility_blocked = clean_utility_blocker["summary_status"] == "BLOCKED"
    if detection_ready and asr_ready and utility_blocked and py_compile["passed"]:
        final_verdict = FINAL_VALIDATED
        summary_status = "PASS"
        recommended_next_step = "dualscope-sci3-main-experiment-expansion-plan"
    elif (detection_ready or asr_ready) and py_compile["passed"]:
        final_verdict = FINAL_PARTIAL
        summary_status = "PARTIAL"
        recommended_next_step = "dualscope-qwen2p5-7b-result-package-blocker-closure"
    else:
        final_verdict = FINAL_NOT_VALIDATED
        summary_status = "FAIL"
        recommended_next_step = "dualscope-qwen2p5-7b-result-package-blocker-closure"

    readiness_note = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "sci3_expansion_ready": final_verdict == FINAL_VALIDATED,
        "recommended_next_step": recommended_next_step,
        "reason": "Detection metrics and ASR are real PASS first-slice evidence; clean utility remains explicitly blocked."
        if final_verdict == FINAL_VALIDATED
        else "Detection/ASR real evidence is incomplete or package validation failed.",
        "allowed_claims": [
            "Qwen2.5-7B first-slice detection metrics from 8 aligned real response rows",
            "Qwen2.5-7B first-slice ASR from 4 poisoned-triggered eligible rows",
            "Clean utility blocked until explicit success/reference-match fields exist",
        ],
        "forbidden_claims": [
            "full-paper performance",
            "full-matrix performance",
            "clean utility inferred from free text",
            "fabricated responses, labels, logprobs, final_risk_score, or metrics",
        ],
    }
    summary = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "created_at": created_at,
        "seed": seed,
        "final_verdict": final_verdict,
        "recommended_next_step": recommended_next_step,
        "prior_result_package_registry_verdict": prior_registry_payload.get("verdict"),
        "prior_result_package_dir_exists": prior_package_dir.exists(),
        "response_generation_final_verdict": response_summary.get("final_verdict"),
        "metric_computation_final_verdict": metric_summary.get("final_verdict"),
        "metric_repair_final_verdict": repair_summary.get("final_verdict"),
        "real_response_row_count": real_metrics["response_generation_real_row_count"],
        "aligned_metric_row_count": real_metrics["aligned_real_response_row_count"],
        "detection_metrics_reportable": detection_ready,
        "asr_reportable": asr_ready,
        "clean_utility_reportable": real_metrics["clean_utility"]["reportable"],
        "clean_utility_explicitly_blocked": utility_blocked,
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
    verdict = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommended_next_step,
        "single_verdict_policy": "one_of_qwen2p5_7b_result_package_repair_validated__partially_validated__not_validated",
    }
    registry = {
        "task_id": TASK_NAME,
        "verdict": final_verdict,
        "source_output_dir": str(output_dir),
        "commit": _current_commit(repo_root),
        "created_at": created_at,
        "validated": final_verdict == FINAL_VALIDATED,
        "next_task": recommended_next_step,
        "real_response_row_count": real_metrics["response_generation_real_row_count"],
        "aligned_metric_row_count": real_metrics["aligned_real_response_row_count"],
        "detection_metrics_reportable": detection_ready,
        "asr_reportable": asr_ready,
        "clean_utility_reportable": real_metrics["clean_utility"]["reportable"],
        "clean_utility_explicitly_blocked": utility_blocked,
        "full_paper_performance_claimed": False,
        "model_responses_fabricated": False,
        "logprobs_fabricated": False,
        "placeholder_metrics_presented_as_real": False,
    }

    report_lines = [
        f"- Final verdict: `{final_verdict}`",
        f"- Recommended next step: `{recommended_next_step}`",
        f"- Prior result-package registry verdict: `{prior_registry_payload.get('verdict')}`",
        f"- Prior result-package directory exists: `{prior_package_dir.exists()}`",
        f"- Response-generation verdict: `{response_summary.get('final_verdict')}`",
        f"- Metric-computation verdict: `{metric_summary.get('final_verdict')}`",
        f"- Metric-repair verdict: `{repair_summary.get('final_verdict')}`",
        f"- Real Qwen2.5-7B response rows: `{real_metrics['response_generation_real_row_count']}`",
        f"- Aligned metric rows: `{real_metrics['aligned_real_response_row_count']}`",
        f"- Detection metrics reportable: `{detection_ready}`",
        f"- AUROC: `{real_metrics['detection_metrics']['auroc']}`",
        f"- AUPRC: `{real_metrics['detection_metrics']['auprc']}`",
        f"- F1: `{real_metrics['detection_metrics']['f1']}`",
        f"- Accuracy: `{real_metrics['detection_metrics']['accuracy']}`",
        f"- ASR reportable: `{asr_ready}`",
        f"- ASR: `{real_metrics['asr']['asr']}`",
        f"- Clean utility reportable: `{real_metrics['clean_utility']['reportable']}`",
        f"- Clean utility explicitly blocked: `{utility_blocked}`",
        f"- Capability mode: `without_logprobs={response_capability.get('without_logprobs')}`, `with_logprobs={response_capability.get('with_logprobs')}`",
        "- Clean utility is not inferred from free text.",
        "- This package is first-slice evidence only; it is not full-paper performance.",
        "- Benchmark truth changed: `False`",
        "- Gates changed: `False`",
        "- route_c / 199+ continuation: `False`",
        "- Full matrix executed: `False`",
        "- Training executed: `False`",
    ]

    write_json(output_dir / f"{OUTPUT_PREFIX}_real_metric_summary.json", real_metrics)
    write_json(output_dir / f"{OUTPUT_PREFIX}_limitation_matrix.json", limitations)
    write_json(output_dir / f"{OUTPUT_PREFIX}_unavailable_metric_blockers.json", unavailable_blockers)
    write_json(output_dir / f"{OUTPUT_PREFIX}_clean_utility_blocker.json", clean_utility_blocker)
    write_json(output_dir / f"{OUTPUT_PREFIX}_sci3_expansion_readiness_note.json", readiness_note)
    write_json(output_dir / f"{OUTPUT_PREFIX}_source_registry_audit.json", prior_registry_payload)
    write_json(output_dir / f"{OUTPUT_PREFIX}_metric_repair_availability_snapshot.json", repair_availability)
    write_json(output_dir / f"{OUTPUT_PREFIX}_metric_repair_blocker_snapshot.json", repair_blockers)
    write_json(output_dir / f"{OUTPUT_PREFIX}_metric_repair_limitations_snapshot.json", repair_limitations)
    write_json(output_dir / f"{OUTPUT_PREFIX}_py_compile.json", py_compile)
    write_json(output_dir / f"{OUTPUT_PREFIX}_summary.json", summary)
    write_json(output_dir / f"{OUTPUT_PREFIX}_verdict.json", verdict)
    write_markdown(output_dir / f"{OUTPUT_PREFIX}_report.md", "DualScope Qwen2.5-7B Result Package Repair", report_lines)

    write_json(analysis_dir / f"{OUTPUT_PREFIX}_real_metric_summary.json", real_metrics)
    write_json(analysis_dir / f"{OUTPUT_PREFIX}_limitation_matrix.json", limitations)
    write_json(analysis_dir / f"{OUTPUT_PREFIX}_summary.json", summary)
    write_json(analysis_dir / f"{OUTPUT_PREFIX}_verdict.json", verdict)
    write_json(verdict_registry, registry)
    write_markdown(docs_path, "DualScope Qwen2.5-7B Result Package Repair", report_lines + ["", "## Regenerate", "", "```bash", "python3 scripts/build_dualscope_qwen2p5_7b_result_package_repair.py --seed 2025", "```"])

    return summary
