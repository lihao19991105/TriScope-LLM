"""Compress partial blockers from the DualScope minimal first-slice real run."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import (
    SCHEMA_VERSION,
    base_scope,
    markdown,
    read_json,
    run_py_compile,
    write_json,
    write_jsonl,
)


PY_FILES = [
    "src/eval/dualscope_first_slice_real_run_compression_common.py",
    "src/eval/dualscope_minimal_first_slice_real_run_compression.py",
    "src/eval/post_dualscope_minimal_first_slice_real_run_compression_analysis.py",
    "scripts/build_dualscope_minimal_first_slice_real_run_compression.py",
    "scripts/build_post_dualscope_minimal_first_slice_real_run_compression_analysis.py",
    "scripts/probe_dualscope_first_slice_model_execution_capability.py",
    "scripts/probe_dualscope_first_slice_logprob_capability.py",
]


def _load_optional(path: Path) -> dict[str, Any]:
    if path.exists():
        payload = read_json(path)
        payload.setdefault("source_path", str(path))
        return payload
    return {"missing": True, "path": str(path)}


def _load_first_existing(paths: list[Path]) -> dict[str, Any]:
    for path in paths:
        if path.exists():
            payload = read_json(path)
            payload.setdefault("source_path", str(path))
            return payload
    return {"missing": True, "candidate_paths": [str(path) for path in paths]}


def build_dualscope_minimal_first_slice_real_run_compression(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    real_run_summary = read_json(repo_root / "outputs/dualscope_minimal_first_slice_real_run/default/dualscope_minimal_first_slice_real_run_summary.json")
    compatibility = read_json(repo_root / "outputs/dualscope_minimal_first_slice_real_run/default/dualscope_minimal_first_slice_real_run_contract_compatibility_check.json")
    readiness = read_json(repo_root / "outputs/dualscope_minimal_first_slice_real_run_readiness_package_analysis/default/dualscope_minimal_real_run_readiness_verdict.json")
    preflight_capability = read_json(repo_root / "outputs/dualscope_first_slice_preflight_rerun/default/dualscope_first_slice_capability_mode_check.json")
    model_probe = _load_first_existing(
        [
            output_dir / "model_probe/dualscope_first_slice_model_execution_probe.json",
            repo_root / "outputs/dualscope_first_slice_model_execution_enablement/default/dualscope_first_slice_generation_probe.json",
            repo_root / "outputs/dualscope_first_slice_model_execution_enablement/default/dualscope_first_slice_model_execution_enablement_summary.json",
        ]
    )
    logprob_probe = _load_first_existing(
        [
            output_dir / "logprob_probe/dualscope_first_slice_logprob_capability_probe.json",
            repo_root / "outputs/dualscope_first_slice_logprob_capability_enablement/default/dualscope_first_slice_logprob_capability_probe.json",
            repo_root / "outputs/dualscope_first_slice_logprob_capability_enablement/default/dualscope_first_slice_logprob_capability_summary.json",
        ]
    )
    label_materialization = _load_optional(
        repo_root / "outputs/dualscope_first_slice_label_materialization/default/dualscope_first_slice_label_materialization_summary.json"
    )

    model_execution_ready = bool(model_probe.get("model_execution_ready"))
    logprobs_available = bool(logprob_probe.get("logprobs_available"))
    labels_available = bool(label_materialization.get("performance_labels_available")) or not bool(
        real_run_summary.get("labels_unavailable_for_performance")
    )
    py_compile = run_py_compile(repo_root, PY_FILES)

    model_gap = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "previous_stage1_execution_mode": compatibility.get("stage1_execution_mode"),
        "previous_stage2_execution_mode": compatibility.get("stage2_execution_mode"),
        "model_execution_ready": model_execution_ready,
        "gap": "minimal generation probe not yet validated" if not model_execution_ready else "closed",
        "next_action": "dualscope-first-slice-model-execution-enablement" if not model_execution_ready else "proceed_to_logprob_capability",
    }
    logprob_gap = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "previous_stage2_capability_mode": compatibility.get("stage2_capability_mode"),
        "preflight_with_logprobs_capability": preflight_capability.get("with_logprobs_capability"),
        "logprobs_available": logprobs_available,
        "gap": "local logits/logprob probe not yet validated" if not logprobs_available else "closed",
    }
    label_gap = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "labels_unavailable_for_performance": real_run_summary.get("labels_unavailable_for_performance"),
        "label_materialization_source": label_materialization.get("source_path"),
        "label_materialization_verdict": label_materialization.get("final_verdict"),
        "label_materialization_recommendation": label_materialization.get("recommended_next_step"),
        "artifact_validation_labels_available": label_materialization.get("artifact_validation_labels_available"),
        "trigger_annotations_available": label_materialization.get("trigger_annotations_available"),
        "target_annotations_available": label_materialization.get("target_annotations_available"),
        "performance_labels_available": labels_available,
        "gap": "performance label contract missing" if not labels_available else "closed",
        "do_not_fabricate_labels": True,
    }
    capability_after = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "model_execution_ready": model_execution_ready,
        "logprobs_available": logprobs_available,
        "fallback_valid": compatibility.get("stage2_capability_mode") == "without_logprobs",
        "labels_available": labels_available,
    }
    if py_compile["passed"]:
        verdict = "Real-run compression validated"
        if not model_execution_ready:
            recommendation = "dualscope-first-slice-model-execution-enablement"
        elif not logprobs_available:
            recommendation = "dualscope-first-slice-logprob-capability-enablement"
        elif not labels_available:
            recommendation = (
                "dualscope-first-slice-clean-poisoned-labeled-slice-plan"
                if not label_materialization.get("missing")
                else "dualscope-first-slice-label-materialization"
            )
        else:
            recommendation = "dualscope-minimal-first-slice-real-run-rerun-with-model-or-fallback"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-minimal-first-slice-real-run-blocker-closure"

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "previous_verdict": real_run_summary.get("final_verdict"),
        "model_execution_ready": model_execution_ready,
        "logprobs_available": logprobs_available,
        "labels_available": labels_available,
        "py_compile_passed": py_compile["passed"],
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    details = [
        {"detail_type": "previous_real_run", "payload": real_run_summary},
        {"detail_type": "model_gap", "payload": model_gap},
        {"detail_type": "logprob_gap", "payload": logprob_gap},
        {"detail_type": "label_gap", "payload": label_gap},
    ]
    write_json(output_dir / "dualscope_first_slice_real_run_compression_scope.json", base_scope("dualscope-minimal-first-slice-real-run-compression", output_dir))
    write_json(output_dir / "dualscope_first_slice_previous_real_run_status.json", real_run_summary)
    write_json(output_dir / "dualscope_first_slice_model_execution_gap.json", model_gap)
    write_json(output_dir / "dualscope_first_slice_model_execution_probe.json", model_probe)
    markdown(output_dir / "dualscope_first_slice_model_execution_probe_report.md", "Model Execution Gap", [f"- Model execution ready: `{model_execution_ready}`", f"- Gap: {model_gap['gap']}"])
    write_json(output_dir / "dualscope_first_slice_logprob_capability_probe.json", logprob_probe)
    markdown(output_dir / "dualscope_first_slice_logprob_capability_report.md", "Logprob Capability Gap", [f"- Logprobs available: `{logprobs_available}`", f"- Gap: {logprob_gap['gap']}"])
    write_json(output_dir / "dualscope_first_slice_capability_mode_after_compression.json", capability_after)
    write_json(output_dir / "dualscope_first_slice_label_metric_readiness.json", {"summary_status": "PASS", "labels_available": labels_available, "metric_placeholders_required": not labels_available})
    write_json(output_dir / "dualscope_first_slice_label_contract_gap.json", label_gap)
    markdown(output_dir / "dualscope_first_slice_metric_readiness_report.md", "Metric Readiness", [f"- Performance labels available: `{labels_available}`", "- No labels were fabricated."])
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_compression_summary.json", summary)
    write_jsonl(output_dir / "dualscope_minimal_first_slice_real_run_compression_details.jsonl", details)
    markdown(output_dir / "dualscope_minimal_first_slice_real_run_compression_report.md", "Minimal First-Slice Real Run Compression", [
        f"- Previous verdict: `{real_run_summary.get('final_verdict')}`",
        f"- Model execution ready: `{model_execution_ready}`",
        f"- Logprobs available: `{logprobs_available}`",
        f"- Labels available: `{labels_available}`",
        f"- Verdict: `{verdict}`",
        f"- Recommendation: {recommendation}",
    ])
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_compression_verdict.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_compression_next_step_recommendation.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_compression_py_compile.json", py_compile)
    return {"summary": summary, "verdict": verdict, "recommendation": recommendation}
