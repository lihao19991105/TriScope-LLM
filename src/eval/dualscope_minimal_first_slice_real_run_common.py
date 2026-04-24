"""Common helpers for the DualScope minimal first-slice real run."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_real_run_entrypoint_common import read_json, read_jsonl, run_py_compile, write_json, write_jsonl


SCHEMA_VERSION = "dualscopellm/minimal-first-slice-real-run/v1"

PY_COMPILE_FILES = [
    "src/eval/dualscope_minimal_first_slice_real_run_common.py",
    "src/eval/dualscope_minimal_first_slice_real_run.py",
    "src/eval/post_dualscope_minimal_first_slice_real_run_analysis.py",
    "scripts/build_dualscope_minimal_first_slice_real_run.py",
    "scripts/build_post_dualscope_minimal_first_slice_real_run_analysis.py",
    "scripts/build_dualscope_first_slice_data_slice.py",
    "scripts/run_dualscope_stage1_illumination.py",
    "scripts/run_dualscope_stage2_confidence.py",
    "scripts/run_dualscope_stage3_fusion.py",
    "scripts/evaluate_dualscope_first_slice.py",
    "scripts/build_dualscope_first_slice_real_run_report.py",
]


def run_command(repo_root: Path, cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=False)
    return {
        "command": cmd,
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def py_compile(repo_root: Path) -> dict[str, Any]:
    return run_py_compile(repo_root, PY_COMPILE_FILES)


def required_artifacts(output_dir: Path) -> dict[str, list[Path]]:
    return {
        "root": [
            output_dir / "dualscope_minimal_first_slice_real_run_scope.json",
            output_dir / "dualscope_minimal_first_slice_real_run_command_plan.json",
            output_dir / "dualscope_minimal_first_slice_real_run_stage_status.json",
            output_dir / "dualscope_minimal_first_slice_real_run_required_artifacts_check.json",
            output_dir / "dualscope_minimal_first_slice_real_run_contract_compatibility_check.json",
            output_dir / "dualscope_minimal_first_slice_real_run_summary.json",
            output_dir / "dualscope_minimal_first_slice_real_run_details.jsonl",
            output_dir / "dualscope_minimal_first_slice_real_run_report.md",
            output_dir / "dualscope_minimal_first_slice_real_run_verdict.json",
            output_dir / "dualscope_minimal_first_slice_real_run_next_step_recommendation.json",
        ],
        "data_slice": [
            output_dir / "data_slice/first_slice_data_slice_summary.json",
            output_dir / "data_slice/first_slice_data_slice_details.jsonl",
            output_dir / "data_slice/first_slice_clean_subset.jsonl",
            output_dir / "data_slice/first_slice_candidate_queries.jsonl",
            output_dir / "data_slice/first_slice_manifest.json",
        ],
        "stage1": [
            output_dir / "stage1_illumination/stage1_illumination_outputs.jsonl",
            output_dir / "stage1_illumination/stage1_illumination_summary.json",
            output_dir / "stage1_illumination/stage1_illumination_budget_usage.json",
            output_dir / "stage1_illumination/stage1_illumination_report.md",
        ],
        "stage2": [
            output_dir / "stage2_confidence/stage2_confidence_outputs.jsonl",
            output_dir / "stage2_confidence/stage2_confidence_summary.json",
            output_dir / "stage2_confidence/stage2_capability_mode_report.json",
            output_dir / "stage2_confidence/stage2_confidence_report.md",
        ],
        "stage3": [
            output_dir / "stage3_fusion/stage3_fusion_outputs.jsonl",
            output_dir / "stage3_fusion/stage3_fusion_summary.json",
            output_dir / "stage3_fusion/stage3_budget_summary.json",
            output_dir / "stage3_fusion/stage3_fusion_report.md",
        ],
        "evaluation": [
            output_dir / "evaluation/first_slice_evaluation_summary.json",
            output_dir / "evaluation/first_slice_metric_placeholders.json",
            output_dir / "evaluation/first_slice_cost_summary.json",
            output_dir / "evaluation/first_slice_evaluation_report.md",
        ],
        "report": [
            output_dir / "report/dualscope_first_slice_real_run_report.md",
            output_dir / "report/dualscope_first_slice_real_run_report_summary.json",
            output_dir / "report/dualscope_first_slice_real_run_table_skeleton.json",
            output_dir / "report/dualscope_first_slice_real_run_figure_placeholders.json",
        ],
    }


def check_required_artifacts(output_dir: Path, *, include_root: bool = True) -> dict[str, Any]:
    groups = required_artifacts(output_dir)
    if not include_root:
        groups = {key: value for key, value in groups.items() if key != "root"}
    group_checks = {}
    missing = []
    for group, paths in groups.items():
        group_missing = [str(path) for path in paths if not path.exists()]
        group_checks[group] = {"passed": not group_missing, "missing": group_missing}
        missing.extend(group_missing)
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "passed": not missing, "group_checks": group_checks, "missing_artifacts": missing}


def check_contract_compatibility(output_dir: Path) -> dict[str, Any]:
    try:
        stage1 = read_jsonl(output_dir / "stage1_illumination/stage1_illumination_outputs.jsonl")
        stage2 = read_jsonl(output_dir / "stage2_confidence/stage2_confidence_outputs.jsonl")
        stage3 = read_jsonl(output_dir / "stage3_fusion/stage3_fusion_outputs.jsonl")
        evaluation = read_json(output_dir / "evaluation/first_slice_evaluation_summary.json")
        stage1_summary = read_json(output_dir / "stage1_illumination/stage1_illumination_summary.json")
        stage2_summary = read_json(output_dir / "stage2_confidence/stage2_confidence_summary.json")
    except Exception as exc:
        return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "passed": False, "error": str(exc)}
    ids1 = {row.get("example_id") for row in stage1}
    ids2 = {row.get("example_id") for row in stage2}
    ids3 = {row.get("example_id") for row in stage3}
    required_stage1 = {"screening_risk_score", "screening_risk_bucket", "confidence_verification_candidate_flag", "template_results", "query_aggregate_features", "budget_usage_summary"}
    required_stage2 = {"capability_mode", "verification_risk_score", "verification_risk_bucket", "confidence_lock_evidence_present", "fallback_degradation_flag", "budget_usage_summary", "fusion_readable_fields"}
    required_stage3 = {"final_risk_score", "final_risk_bucket", "final_decision_flag", "verification_triggered", "capability_mode", "evidence_summary", "budget_usage_summary"}
    missing_fields = []
    for stage_name, rows, required in [("stage1", stage1, required_stage1), ("stage2", stage2, required_stage2), ("stage3", stage3, required_stage3)]:
        for index, row in enumerate(rows):
            missing = sorted(required - set(row))
            if missing:
                missing_fields.append({"stage": stage_name, "index": index, "missing": missing})
    passed = bool(stage1) and ids1 == ids2 == ids3 and not missing_fields and evaluation.get("field_check_passed") is True
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "passed": passed,
        "id_sets_match": ids1 == ids2 == ids3,
        "stage1_count": len(stage1),
        "stage2_count": len(stage2),
        "stage3_count": len(stage3),
        "missing_fields": missing_fields,
        "evaluation_field_check_passed": evaluation.get("field_check_passed"),
        "stage1_execution_mode": stage1_summary.get("execution_mode"),
        "stage2_execution_mode": stage2_summary.get("execution_mode"),
        "stage2_capability_mode": stage2_summary.get("capability_mode"),
        "stage2_logprob_extraction_executed": stage2_summary.get("logprob_extraction_executed"),
        "labels_unavailable_for_performance": evaluation.get("labels_unavailable_for_performance"),
    }


def write_markdown(path: Path, title: str, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join([f"# {title}", "", *lines, ""]) + "\n", encoding="utf-8")
