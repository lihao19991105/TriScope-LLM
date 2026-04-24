"""Post-analysis for DualScope first-slice preflight repair."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_preflight_repair_common import SCHEMA_VERSION, write_json


POST_SCHEMA_VERSION = "dualscopellm/post-first-slice-preflight-repair-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def post_dualscope_first_slice_preflight_repair_analysis(repair_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_preflight_repair_scope.json",
        "dualscope_first_slice_preflight_blockers.json",
        "dualscope_first_slice_dataset_import_contract.json",
        "dualscope_first_slice_dataset_schema_contract.json",
        "dualscope_first_slice_dataset_import_command_plan.json",
        "dualscope_first_slice_dataset_schema_check_command_plan.json",
        "dualscope_first_slice_gpu_environment_requirements.json",
        "dualscope_first_slice_environment_snapshot.json",
        "dualscope_first_slice_rerun_preflight_checklist.json",
        "dualscope_first_slice_repair_summary.json",
        "dualscope_first_slice_repair_details.jsonl",
        "dualscope_first_slice_repair_report.md",
    ]
    missing = [name for name in required if not (repair_dir / name).exists()]
    summary = _load_json(repair_dir / "dualscope_first_slice_repair_summary.json")
    py_compile_path = repair_dir / "dualscope_first_slice_py_compile_check.json"
    py_compile = _load_json(py_compile_path) if py_compile_path.exists() else {"passed": False}

    validated = (
        not missing
        and summary.get("dataset_import_tool_ready") is True
        and summary.get("dataset_schema_check_tool_ready") is True
        and summary.get("gpu_environment_requirements_recorded") is True
        and summary.get("rerun_preflight_checklist_ready") is True
        and summary.get("synthetic_data_generated") is False
        and summary.get("training_executed") is False
        and summary.get("full_matrix_executed") is False
        and summary.get("benchmark_truth_changed") is False
        and summary.get("gate_semantics_changed") is False
        and py_compile.get("passed") is True
    )
    if validated:
        final_verdict = "Preflight repair validated"
        recommendation = "进入 dualscope-first-slice-dataset-materialization"
        basis = [
            "Dataset import and schema validation tools are implemented.",
            "Repair artifacts, GPU/environment requirements, and rerun checklist are complete.",
            "py_compile passed and no synthetic data, training, full matrix, benchmark truth, or gate changes occurred.",
            "This validates the repair package only; real preflight still needs dataset materialization.",
        ]
    else:
        final_verdict = "Partially validated" if not missing else "Not validated"
        recommendation = (
            "进入 dualscope-first-slice-preflight-repair-compression"
            if final_verdict == "Partially validated"
            else "进入 dualscope-first-slice-preflight-blocker-closure"
        )
        basis = [
            "Repair package is incomplete or py_compile failed.",
            f"Missing artifacts: {missing}",
        ]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "source_summary": summary,
        "py_compile_passed": py_compile.get("passed"),
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_preflight_repair_validated__partially_validated__not_validated",
        "primary_basis": basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": basis,
        "do_not_do_yet": [
            "start_real_run_before_dataset_materialization",
            "fabricate_dataset",
            "run_lora_training",
            "run_full_matrix",
            "continue_route_c_199_plus",
        ],
    }
    write_json(output_dir / "dualscope_first_slice_preflight_repair_analysis_summary.json", analysis_summary)
    write_json(output_dir / "dualscope_first_slice_preflight_repair_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_preflight_repair_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_preflight_repair_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "dualscope_first_slice_preflight_repair_verdict.json").resolve()),
            "recommendation": str((output_dir / "dualscope_first_slice_preflight_repair_next_step_recommendation.json").resolve()),
        },
    }
