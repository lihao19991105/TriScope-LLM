"""Validate artifacts from the DualScope first-slice real-run rerun."""

from __future__ import annotations

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
    "src/eval/dualscope_first_slice_real_run_artifact_validation.py",
    "src/eval/post_dualscope_first_slice_real_run_artifact_validation_analysis.py",
    "scripts/build_dualscope_first_slice_real_run_artifact_validation.py",
    "scripts/build_post_dualscope_first_slice_real_run_artifact_validation_analysis.py",
]


REQUIRED_PIPELINE_ARTIFACTS = [
    "pipeline/data_slice/first_slice_data_slice_summary.json",
    "pipeline/data_slice/first_slice_candidate_queries.jsonl",
    "pipeline/stage1_illumination/stage1_illumination_outputs.jsonl",
    "pipeline/stage1_illumination/stage1_illumination_summary.json",
    "pipeline/stage2_confidence/stage2_confidence_outputs.jsonl",
    "pipeline/stage2_confidence/stage2_confidence_summary.json",
    "pipeline/stage2_confidence/stage2_capability_mode_report.json",
    "pipeline/stage3_fusion/stage3_fusion_outputs.jsonl",
    "pipeline/stage3_fusion/stage3_fusion_summary.json",
    "pipeline/evaluation/first_slice_evaluation_summary.json",
    "pipeline/report/dualscope_first_slice_real_run_report.md",
]


def _read(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {"summary_status": "MISSING", "path": str(path)}


def build_real_run_artifact_validation(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    rerun_dir = repo_root / "outputs/dualscope_minimal_first_slice_real_run_rerun/default"
    missing = [str(rerun_dir / item) for item in REQUIRED_PIPELINE_ARTIFACTS if not (rerun_dir / item).exists()]
    rerun_summary = _read(rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_summary.json")
    capability = _read(rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_capability_mode.json")
    metric_readiness = _read(rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_metric_readiness.json")
    compatibility = _read(rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_compatibility_check.json")
    py_compile = run_py_compile(repo_root, PY_FILES)
    artifact_chain_passed = not missing
    no_forbidden = not bool(rerun_summary.get("training_executed")) and not bool(rerun_summary.get("full_matrix_executed"))
    complete_model_integrated = bool(capability.get("stage_entrypoints_model_integrated"))
    performance_ready = bool(metric_readiness.get("performance_metrics_ready"))
    if artifact_chain_passed and no_forbidden and py_compile["passed"] and complete_model_integrated and performance_ready:
        verdict = "Real-run artifact validation validated"
        recommendation = "dualscope-first-slice-result-package"
    elif artifact_chain_passed and no_forbidden and py_compile["passed"]:
        verdict = "Partially validated"
        recommendation = "dualscope-first-slice-result-package"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-first-slice-real-run-artifact-validation-blocker-closure"
    summary = {
        "summary_status": "PASS" if artifact_chain_passed and py_compile["passed"] else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "artifact_chain_passed": artifact_chain_passed,
        "missing_artifacts": missing,
        "capability_mode": capability.get("selected_mode"),
        "stage_entrypoints_model_integrated": complete_model_integrated,
        "performance_metrics_ready": performance_ready,
        "no_forbidden_expansion": no_forbidden,
        "py_compile_passed": py_compile["passed"],
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_scope.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "validated_source": str(rerun_dir)})
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_checklist.json", {"summary_status": "PASS" if artifact_chain_passed else "FAIL", "required": REQUIRED_PIPELINE_ARTIFACTS, "missing": missing})
    write_json(output_dir / "dualscope_first_slice_real_run_contract_compatibility_report.json", compatibility)
    write_json(output_dir / "dualscope_first_slice_real_run_capability_validation.json", capability)
    write_json(output_dir / "dualscope_first_slice_real_run_metric_label_validation.json", metric_readiness)
    write_json(output_dir / "dualscope_first_slice_real_run_forbidden_expansion_check.json", {"summary_status": "PASS" if no_forbidden else "FAIL", "training_executed": rerun_summary.get("training_executed"), "full_matrix_executed": rerun_summary.get("full_matrix_executed")})
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_summary.json", summary)
    write_jsonl(output_dir / "dualscope_first_slice_real_run_artifact_validation_details.jsonl", [
        {"detail_type": "rerun_summary", "payload": rerun_summary},
        {"detail_type": "capability", "payload": capability},
        {"detail_type": "metric_readiness", "payload": metric_readiness},
    ])
    markdown(output_dir / "dualscope_first_slice_real_run_artifact_validation_report.md", "Real-Run Artifact Validation", [
        f"- Artifact chain passed: `{artifact_chain_passed}`",
        f"- Stage entrypoints model-integrated: `{complete_model_integrated}`",
        f"- Performance metrics ready: `{performance_ready}`",
        f"- No forbidden expansion: `{no_forbidden}`",
        f"- Verdict: `{verdict}`",
    ])
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_verdict.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_first_slice_real_run_artifact_validation_next_step_recommendation.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    return summary
