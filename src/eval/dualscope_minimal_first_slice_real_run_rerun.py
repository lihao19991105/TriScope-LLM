"""Rerun the DualScope minimal first-slice with model/logprob capability evidence attached."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import (
    SCHEMA_VERSION,
    markdown,
    read_json,
    run_py_compile,
    write_json,
    write_jsonl,
)


PY_FILES = [
    "src/eval/dualscope_minimal_first_slice_real_run_rerun.py",
    "src/eval/post_dualscope_minimal_first_slice_real_run_rerun_analysis.py",
    "scripts/build_dualscope_minimal_first_slice_real_run_rerun.py",
    "scripts/build_post_dualscope_minimal_first_slice_real_run_rerun_analysis.py",
]


def _safe_read(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {"summary_status": "MISSING", "path": str(path)}


def _normalize_self_referential_artifact_check(pipeline_dir: Path, artifacts: dict[str, Any]) -> dict[str, Any]:
    """The upstream minimal-run checker can list its own output before it is written."""

    missing = list(artifacts.get("missing_artifacts", []))
    self_path = pipeline_dir / "dualscope_minimal_first_slice_real_run_required_artifacts_check.json"
    if missing and all(Path(item) == self_path for item in missing) and self_path.exists():
        fixed = dict(artifacts)
        fixed["passed"] = True
        fixed["missing_artifacts"] = []
        fixed["normalized_self_referential_check"] = True
        fixed["normalization_note"] = "Only the required-artifacts-check file itself was listed missing before it was written."
        group_checks = dict(fixed.get("group_checks", {}))
        root = dict(group_checks.get("root", {}))
        root["passed"] = True
        root["missing"] = []
        group_checks["root"] = root
        fixed["group_checks"] = group_checks
        return fixed
    return artifacts


def build_real_run_rerun(output_dir: Path, mode: str, no_full_matrix: bool) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    if not no_full_matrix:
        raise ValueError("--no-full-matrix is required.")
    model_summary = _safe_read(repo_root / "outputs/dualscope_first_slice_model_execution_enablement/default/dualscope_first_slice_model_execution_enablement_summary.json")
    logprob_summary = _safe_read(repo_root / "outputs/dualscope_first_slice_logprob_capability_enablement/default/dualscope_first_slice_logprob_capability_summary.json")
    label_summary = _safe_read(repo_root / "outputs/dualscope_first_slice_label_materialization/default/dualscope_first_slice_label_materialization_summary.json")
    model_ready = bool(model_summary.get("model_execution_ready"))
    logprobs_ready = bool(logprob_summary.get("logprobs_available"))
    labels_ready = bool(label_summary.get("performance_labels_available"))
    if mode == "auto":
        selected_mode = "model_with_logprobs" if model_ready and logprobs_ready else "model_without_logprobs_fallback" if model_ready else "protocol_fallback_only"
    else:
        selected_mode = mode
    capability_mode_arg = "with_logprobs" if selected_mode == "model_with_logprobs" else "auto"
    pipeline_dir = output_dir / "pipeline"
    cmd = [
        sys.executable,
        "scripts/build_dualscope_minimal_first_slice_real_run.py",
        "--output-dir",
        str(pipeline_dir),
        "--capability-mode",
        capability_mode_arg,
        "--allow-fallback-without-logprobs",
        "--no-full-matrix",
    ]
    proc = subprocess.run(cmd, cwd=repo_root, text=True, capture_output=True, check=False)
    pipeline_summary = _safe_read(pipeline_dir / "dualscope_minimal_first_slice_real_run_summary.json")
    compatibility = _safe_read(pipeline_dir / "dualscope_minimal_first_slice_real_run_contract_compatibility_check.json")
    artifacts = _normalize_self_referential_artifact_check(
        pipeline_dir,
        _safe_read(pipeline_dir / "dualscope_minimal_first_slice_real_run_required_artifacts_check.json"),
    )
    py_compile = run_py_compile(repo_root, PY_FILES)
    stage_entrypoints_model_integrated = not bool(pipeline_summary.get("protocol_compatible_deterministic_mode"))
    performance_metrics_ready = labels_ready and not bool(pipeline_summary.get("labels_unavailable_for_performance"))
    if proc.returncode == 0 and artifacts.get("passed") and compatibility.get("passed") and py_compile["passed"] and stage_entrypoints_model_integrated and performance_metrics_ready:
        verdict = "Minimal first-slice real run rerun validated"
        recommendation = "dualscope-first-slice-real-run-artifact-validation"
    elif proc.returncode == 0 and artifacts.get("passed") and compatibility.get("passed") and py_compile["passed"]:
        verdict = "Partially validated"
        recommendation = "dualscope-first-slice-real-run-artifact-validation"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-minimal-first-slice-real-run-rerun-blocker-closure"
    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-minimal-first-slice-real-run-rerun-with-model-or-fallback",
        "requested_mode": mode,
        "selected_mode": selected_mode,
        "no_full_matrix": no_full_matrix,
        "training_executed": False,
        "full_matrix_executed": False,
    }
    capability_after = {
        "summary_status": "PASS",
        "model_execution_ready": model_ready,
        "logprobs_available": logprobs_ready,
        "logprob_source": logprob_summary.get("logprob_source"),
        "selected_mode": selected_mode,
        "stage_entrypoints_model_integrated": stage_entrypoints_model_integrated,
        "stage2_capability_mode_after_rerun": pipeline_summary.get("stage2_capability_mode"),
    }
    metric_readiness = {
        "summary_status": "PARTIAL" if not performance_metrics_ready else "PASS",
        "performance_metrics_ready": performance_metrics_ready,
        "labels_available": labels_ready,
        "metric_placeholders_required": not performance_metrics_ready,
    }
    summary = {
        "summary_status": "PASS" if py_compile["passed"] else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "model_execution_ready": model_ready,
        "logprobs_available": logprobs_ready,
        "labels_available": labels_ready,
        "pipeline_returncode": proc.returncode,
        "pipeline_verdict": pipeline_summary.get("final_verdict"),
        "stage_entrypoints_model_integrated": stage_entrypoints_model_integrated,
        "performance_metrics_ready": performance_metrics_ready,
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_scope.json", scope)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_command_plan.json", {"summary_status": "PASS", "command": cmd, "stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()[-4000:]})
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_stage_status.json", pipeline_summary)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_capability_mode.json", capability_after)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_metric_readiness.json", metric_readiness)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_artifact_check.json", artifacts)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_compatibility_check.json", compatibility)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_summary.json", summary)
    write_jsonl(output_dir / "dualscope_minimal_first_slice_real_run_rerun_details.jsonl", [
        {"detail_type": "model_enablement", "payload": model_summary},
        {"detail_type": "logprob_enablement", "payload": logprob_summary},
        {"detail_type": "label_materialization", "payload": label_summary},
        {"detail_type": "pipeline_summary", "payload": pipeline_summary},
    ])
    markdown(output_dir / "dualscope_minimal_first_slice_real_run_rerun_report.md", "Minimal First-Slice Real Run Rerun", [
        f"- Selected mode: `{selected_mode}`",
        f"- Model execution ready: `{model_ready}`",
        f"- Logprobs available: `{logprobs_ready}`",
        f"- Stage entrypoints model-integrated: `{stage_entrypoints_model_integrated}`",
        f"- Performance labels ready: `{performance_metrics_ready}`",
        f"- Verdict: `{verdict}`",
        "- Capability probes are attached honestly; no full matrix or training was executed.",
    ])
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_verdict.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_rerun_next_step_recommendation.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    return summary
