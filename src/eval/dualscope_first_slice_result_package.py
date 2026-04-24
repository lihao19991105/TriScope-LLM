"""Package DualScope first-slice rerun results."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import SCHEMA_VERSION, markdown, read_json, run_py_compile, write_json


PY_FILES = [
    "src/eval/dualscope_first_slice_result_package.py",
    "src/eval/post_dualscope_first_slice_result_package_analysis.py",
    "scripts/build_dualscope_first_slice_result_package.py",
    "scripts/build_post_dualscope_first_slice_result_package_analysis.py",
]


def _read(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {"summary_status": "MISSING", "path": str(path)}


def build_result_package(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    rerun = _read(repo_root / "outputs/dualscope_minimal_first_slice_real_run_rerun/default/dualscope_minimal_first_slice_real_run_rerun_summary.json")
    artifact_validation = _read(repo_root / "outputs/dualscope_first_slice_real_run_artifact_validation/default/dualscope_first_slice_real_run_artifact_validation_summary.json")
    stage1 = _read(repo_root / "outputs/dualscope_minimal_first_slice_real_run_rerun/default/pipeline/stage1_illumination/stage1_illumination_summary.json")
    stage2 = _read(repo_root / "outputs/dualscope_minimal_first_slice_real_run_rerun/default/pipeline/stage2_confidence/stage2_confidence_summary.json")
    stage3 = _read(repo_root / "outputs/dualscope_minimal_first_slice_real_run_rerun/default/pipeline/stage3_fusion/stage3_fusion_summary.json")
    evaluation = _read(repo_root / "outputs/dualscope_minimal_first_slice_real_run_rerun/default/pipeline/evaluation/first_slice_evaluation_summary.json")
    cost = _read(repo_root / "outputs/dualscope_minimal_first_slice_real_run_rerun/default/pipeline/evaluation/first_slice_cost_summary.json")
    capability = _read(repo_root / "outputs/dualscope_minimal_first_slice_real_run_rerun/default/dualscope_minimal_first_slice_real_run_rerun_capability_mode.json")
    py_compile = run_py_compile(repo_root, PY_FILES)
    can_report = [
        "data_slice_artifact_chain",
        "stage1_stage2_stage3_schema_compatibility",
        "local_model_minimal_generation_probe",
        "local_logits_softmax_probability_probe",
        "cost_summary_shape",
        "decision_distribution_shape",
    ]
    cannot_report = [
        "paper_level_detection_performance",
        "AUROC",
        "F1",
        "ASR",
        "clean_utility",
        "fully_model_integrated_stage1_stage2_results",
    ]
    limitations = [
        "Stage 1 and Stage 2 entrypoints still report protocol-compatible deterministic no-model execution.",
        "Performance labels are unavailable, so metric placeholders remain required.",
        "Local logits-derived probabilities are available but not yet wired into Stage 2 per-sample feature extraction.",
    ]
    if artifact_validation.get("artifact_chain_passed") and py_compile["passed"]:
        verdict = "First-slice result package validated"
        recommendation = "dualscope-next-experiment-readiness-package"
    elif py_compile["passed"]:
        verdict = "Partially validated"
        recommendation = "dualscope-next-experiment-readiness-package"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-first-slice-result-package-blocker-closure"
    final_setting = {
        "dataset": "stanford_alpaca_first_slice",
        "model": "Qwen2.5-1.5B-Instruct local path",
        "trigger": "lexical",
        "target": "fixed_response",
        "capability_mode": capability.get("selected_mode"),
        "full_matrix_executed": False,
        "training_executed": False,
    }
    summary = {
        "summary_status": "PASS" if py_compile["passed"] else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "final_setting": final_setting,
        "stage1_result_summary": stage1,
        "stage2_result_summary": stage2,
        "stage3_fusion_summary": stage3,
        "evaluation_summary": evaluation,
        "cost_summary": cost,
        "can_report": can_report,
        "cannot_report": cannot_report,
        "limitations": limitations,
        "py_compile_passed": py_compile["passed"],
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_first_slice_result_package_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_final_setting.json", final_setting)
    write_json(output_dir / "dualscope_first_slice_reportable_items.json", {"summary_status": "PASS", "can_report": can_report, "cannot_report": cannot_report})
    write_json(output_dir / "dualscope_first_slice_result_limitations.json", {"summary_status": "PASS", "limitations": limitations})
    write_json(output_dir / "dualscope_first_slice_result_package_py_compile.json", py_compile)
    markdown(output_dir / "dualscope_first_slice_result_package_report.md", "First-Slice Result Package", [
        f"- Capability mode: `{capability.get('selected_mode')}`",
        f"- Artifact validation verdict: `{artifact_validation.get('final_verdict')}`",
        "- Reportable: artifact chain, schema compatibility, model/logits probes, cost and decision shapes.",
        "- Not reportable: AUROC/F1/ASR/clean utility or final paper-level performance.",
        f"- Verdict: `{verdict}`",
    ])
    write_json(output_dir / "dualscope_first_slice_result_package_verdict.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_first_slice_result_package_next_step_recommendation.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    return summary
