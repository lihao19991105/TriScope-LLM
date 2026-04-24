"""Validate DualScope minimal real-run command entrypoints via dry-run chain."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_real_run_entrypoint_common import read_json, read_jsonl, run_py_compile, write_json, write_jsonl, write_report


SCHEMA_VERSION = "dualscopellm/minimal-real-run-command-entrypoint-package/v1"

ENTRYPOINTS = [
    "scripts/build_dualscope_first_slice_data_slice.py",
    "scripts/run_dualscope_stage1_illumination.py",
    "scripts/run_dualscope_stage2_confidence.py",
    "scripts/run_dualscope_stage3_fusion.py",
    "scripts/evaluate_dualscope_first_slice.py",
    "scripts/build_dualscope_first_slice_real_run_report.py",
]

PY_FILES = [
    "src/eval/dualscope_real_run_entrypoint_common.py",
    "src/eval/dualscope_minimal_real_run_command_entrypoint_package.py",
    "src/eval/post_dualscope_minimal_real_run_command_entrypoint_package_analysis.py",
    "scripts/build_dualscope_minimal_real_run_command_entrypoint_package.py",
    "scripts/build_post_dualscope_minimal_real_run_command_entrypoint_package_analysis.py",
    *ENTRYPOINTS,
]


def _run(repo_root: Path, cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=False)
    return {
        "command": cmd,
        "returncode": result.returncode,
        "passed": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _required_artifacts(dry_root: Path) -> dict[str, list[Path]]:
    return {
        "data_slice": [
            dry_root / "data/first_slice_data_slice_summary.json",
            dry_root / "data/first_slice_data_slice_details.jsonl",
            dry_root / "data/first_slice_clean_subset.jsonl",
            dry_root / "data/first_slice_candidate_queries.jsonl",
            dry_root / "data/first_slice_manifest.json",
        ],
        "stage1": [
            dry_root / "stage1/stage1_illumination_outputs.jsonl",
            dry_root / "stage1/stage1_illumination_summary.json",
            dry_root / "stage1/stage1_illumination_budget_usage.json",
            dry_root / "stage1/stage1_illumination_report.md",
        ],
        "stage2": [
            dry_root / "stage2/stage2_confidence_outputs.jsonl",
            dry_root / "stage2/stage2_confidence_summary.json",
            dry_root / "stage2/stage2_capability_mode_report.json",
            dry_root / "stage2/stage2_confidence_report.md",
        ],
        "stage3": [
            dry_root / "stage3/stage3_fusion_outputs.jsonl",
            dry_root / "stage3/stage3_fusion_summary.json",
            dry_root / "stage3/stage3_budget_summary.json",
            dry_root / "stage3/stage3_fusion_report.md",
        ],
        "evaluation": [
            dry_root / "eval/first_slice_evaluation_summary.json",
            dry_root / "eval/first_slice_metric_placeholders.json",
            dry_root / "eval/first_slice_cost_summary.json",
            dry_root / "eval/first_slice_evaluation_report.md",
        ],
        "report": [
            dry_root / "report/dualscope_first_slice_real_run_report.md",
            dry_root / "report/dualscope_first_slice_real_run_report_summary.json",
            dry_root / "report/dualscope_first_slice_real_run_table_skeleton.json",
            dry_root / "report/dualscope_first_slice_real_run_figure_placeholders.json",
        ],
    }


def _check_required_artifacts(dry_root: Path) -> dict[str, Any]:
    groups = _required_artifacts(dry_root)
    group_checks = {}
    missing = []
    for group, paths in groups.items():
        group_missing = [str(path) for path in paths if not path.exists()]
        group_checks[group] = {"passed": not group_missing, "missing": group_missing, "required_count": len(paths)}
        missing.extend(group_missing)
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "passed": not missing,
        "group_checks": group_checks,
        "missing_artifacts": missing,
    }


def _check_chain(dry_root: Path) -> dict[str, Any]:
    try:
        stage1 = read_jsonl(dry_root / "stage1/stage1_illumination_outputs.jsonl")
        stage2 = read_jsonl(dry_root / "stage2/stage2_confidence_outputs.jsonl")
        stage3 = read_jsonl(dry_root / "stage3/stage3_fusion_outputs.jsonl")
        eval_summary = read_json(dry_root / "eval/first_slice_evaluation_summary.json")
    except Exception as exc:
        return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "passed": False, "error": str(exc)}
    ids1 = {row.get("example_id") for row in stage1}
    ids2 = {row.get("example_id") for row in stage2}
    ids3 = {row.get("example_id") for row in stage3}
    required_stage1 = {"screening_risk_score", "screening_risk_bucket", "confidence_verification_candidate_flag", "budget_usage_summary"}
    required_stage2 = {"capability_mode", "verification_risk_score", "verification_risk_bucket", "fallback_degradation_flag", "budget_usage_summary"}
    required_stage3 = {"final_risk_score", "final_risk_bucket", "final_decision_flag", "budget_usage_summary", "evidence_summary"}
    missing_fields = []
    for name, rows, required in [("stage1", stage1, required_stage1), ("stage2", stage2, required_stage2), ("stage3", stage3, required_stage3)]:
        for idx, row in enumerate(rows):
            missing = sorted(required - set(row))
            if missing:
                missing_fields.append({"stage": name, "index": idx, "missing": missing})
    passed = bool(stage1) and ids1 == ids2 == ids3 and not missing_fields and eval_summary.get("field_check_passed") is True
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "passed": passed,
        "stage1_count": len(stage1),
        "stage2_count": len(stage2),
        "stage3_count": len(stage3),
        "id_sets_match": ids1 == ids2 == ids3,
        "missing_fields": missing_fields,
        "evaluation_field_check_passed": eval_summary.get("field_check_passed"),
    }


def build_dualscope_minimal_real_run_command_entrypoint_package(output_dir: Path, seed: int = 42) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    dry_root = output_dir / "dry_run"

    inventory_items = []
    for script in ENTRYPOINTS:
        inventory_items.append({"script": script, "exists": (repo_root / script).exists()})
    inventory = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "entrypoint_count": len(ENTRYPOINTS),
        "all_exist": all(item["exists"] for item in inventory_items),
        "entrypoints": inventory_items,
    }

    cli_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "required_common_args": ["--output-dir", "--dry-run", "--contract-check", "--seed"],
        "entrypoint_specific_args": {
            "build_dualscope_first_slice_data_slice": ["--dataset-file", "--max-examples"],
            "run_dualscope_stage1_illumination": ["--input-file/--input", "--template-spec", "--budget-contract"],
            "run_dualscope_stage2_confidence": ["--stage1-file/--stage1-dir", "--capability-mode", "--fallback-policy"],
            "run_dualscope_stage3_fusion": ["--stage1-file/--stage1-dir", "--stage2-file/--stage2-dir", "--fusion-policy"],
            "evaluate_dualscope_first_slice": ["--fusion-file/--fusion-dir", "--metrics-contract"],
            "build_dualscope_first_slice_real_run_report": ["--stage*-summary", "--run-dir"],
        },
    }

    py_compile = run_py_compile(repo_root, PY_FILES)

    commands = [
        [sys.executable, "scripts/build_dualscope_first_slice_data_slice.py", "--dataset-file", "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl", "--output-dir", str(dry_root / "data"), "--max-examples", "8", "--seed", str(seed), "--dry-run", "--contract-check"],
        [sys.executable, "scripts/run_dualscope_stage1_illumination.py", "--input-file", str(dry_root / "data/first_slice_candidate_queries.jsonl"), "--output-dir", str(dry_root / "stage1"), "--seed", str(seed), "--dry-run", "--contract-check"],
        [sys.executable, "scripts/run_dualscope_stage2_confidence.py", "--stage1-file", str(dry_root / "stage1/stage1_illumination_outputs.jsonl"), "--output-dir", str(dry_root / "stage2"), "--capability-mode", "auto", "--seed", str(seed), "--dry-run", "--contract-check"],
        [sys.executable, "scripts/run_dualscope_stage3_fusion.py", "--stage1-file", str(dry_root / "stage1/stage1_illumination_outputs.jsonl"), "--stage2-file", str(dry_root / "stage2/stage2_confidence_outputs.jsonl"), "--output-dir", str(dry_root / "stage3"), "--seed", str(seed), "--dry-run", "--contract-check"],
        [sys.executable, "scripts/evaluate_dualscope_first_slice.py", "--fusion-file", str(dry_root / "stage3/stage3_fusion_outputs.jsonl"), "--output-dir", str(dry_root / "eval"), "--seed", str(seed), "--dry-run", "--contract-check"],
        [sys.executable, "scripts/build_dualscope_first_slice_real_run_report.py", "--stage1-summary", str(dry_root / "stage1/stage1_illumination_summary.json"), "--stage2-summary", str(dry_root / "stage2/stage2_confidence_summary.json"), "--stage3-summary", str(dry_root / "stage3/stage3_fusion_summary.json"), "--evaluation-summary", str(dry_root / "eval/first_slice_evaluation_summary.json"), "--output-dir", str(dry_root / "report"), "--seed", str(seed), "--dry-run", "--contract-check"],
    ]
    dry_results = [_run(repo_root, command) for command in commands]
    dry_run_results = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "passed": all(result["passed"] for result in dry_results),
        "results": dry_results,
    }
    required_artifacts = _check_required_artifacts(dry_root)
    chain = _check_chain(dry_root)

    before_readiness = {}
    before_path = repo_root / "outputs/dualscope_minimal_first_slice_real_run_readiness_package_analysis/default/dualscope_minimal_real_run_readiness_verdict.json"
    if before_path.exists():
        before_readiness = read_json(before_path)

    readiness_build = _run(repo_root, [sys.executable, "scripts/build_dualscope_minimal_first_slice_real_run_readiness_package.py", "--output-dir", "outputs/dualscope_minimal_first_slice_real_run_readiness_package/default"])
    readiness_post = _run(repo_root, [sys.executable, "scripts/build_post_dualscope_minimal_first_slice_real_run_readiness_package_analysis.py", "--output-dir", "outputs/dualscope_minimal_first_slice_real_run_readiness_package_analysis/default"])
    after_path = repo_root / "outputs/dualscope_minimal_first_slice_real_run_readiness_package_analysis/default/dualscope_minimal_real_run_readiness_verdict.json"
    after_readiness = read_json(after_path) if after_path.exists() else {}
    readiness_delta = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "before_verdict": before_readiness.get("final_verdict"),
        "after_verdict": after_readiness.get("final_verdict"),
        "readiness_build_passed": readiness_build["passed"],
        "readiness_post_passed": readiness_post["passed"],
        "missing_entrypoint_blocker_resolved": after_readiness.get("final_verdict") == "Minimal real run readiness validated",
    }

    all_passed = (
        inventory["all_exist"]
        and py_compile["passed"]
        and dry_run_results["passed"]
        and required_artifacts["passed"]
        and chain["passed"]
        and readiness_delta["missing_entrypoint_blocker_resolved"]
    )
    if all_passed:
        final_verdict = "Real-run command entrypoint package validated"
        recommendation = "dualscope-minimal-first-slice-real-run"
    elif inventory["all_exist"] and py_compile["passed"] and dry_run_results["passed"] and required_artifacts["passed"] and chain["passed"]:
        final_verdict = "Partially validated"
        recommendation = "dualscope-real-run-entrypoint-package-compression"
    else:
        final_verdict = "Not validated"
        recommendation = "dualscope-real-run-entrypoint-blocker-closure"

    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-minimal-real-run-command-entrypoint-package",
        "dry_run_only": True,
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "entrypoints_all_exist": inventory["all_exist"],
        "py_compile_passed": py_compile["passed"],
        "dry_run_passed": dry_run_results["passed"],
        "required_artifacts_passed": required_artifacts["passed"],
        "chain_compatibility_passed": chain["passed"],
        "readiness_after_verdict": after_readiness.get("final_verdict"),
        "training_executed": False,
        "full_matrix_executed": False,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    details = [
        {"detail_type": "inventory", "payload": inventory},
        {"detail_type": "py_compile", "payload": py_compile},
        {"detail_type": "dry_run_results", "payload": dry_run_results},
        {"detail_type": "required_artifacts", "payload": required_artifacts},
        {"detail_type": "chain_compatibility", "payload": chain},
        {"detail_type": "readiness_delta", "payload": readiness_delta},
    ]
    report_lines = [
        f"- Entrypoints all exist: `{inventory['all_exist']}`",
        f"- Py compile passed: `{py_compile['passed']}`",
        f"- Dry-run chain passed: `{dry_run_results['passed']}`",
        f"- Required artifacts passed: `{required_artifacts['passed']}`",
        f"- Chain compatibility passed: `{chain['passed']}`",
        f"- Readiness after rerun: `{after_readiness.get('final_verdict')}`",
        f"- Final verdict: `{final_verdict}`",
        f"- Recommendation: {recommendation}",
        "",
        "This package did not train, run full inference, expand the matrix, change benchmark truth, or change gate semantics.",
    ]
    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_real_run_command_entrypoint_package_validated__partially_validated__not_validated",
    }
    rec = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }

    write_json(output_dir / "dualscope_real_run_entrypoint_scope.json", scope)
    write_json(output_dir / "dualscope_real_run_entrypoint_inventory.json", inventory)
    write_json(output_dir / "dualscope_real_run_entrypoint_cli_contract.json", cli_contract)
    write_json(output_dir / "dualscope_real_run_entrypoint_py_compile_check.json", py_compile)
    write_json(output_dir / "dualscope_real_run_entrypoint_dry_run_results.json", dry_run_results)
    write_json(output_dir / "dualscope_real_run_entrypoint_required_artifacts_check.json", required_artifacts)
    write_json(output_dir / "dualscope_real_run_entrypoint_chain_compatibility_check.json", chain)
    write_json(output_dir / "dualscope_real_run_entrypoint_readiness_delta.json", readiness_delta)
    write_json(output_dir / "dualscope_real_run_entrypoint_package_summary.json", summary)
    write_jsonl(output_dir / "dualscope_real_run_entrypoint_package_details.jsonl", details)
    write_report(output_dir / "dualscope_real_run_entrypoint_package_report.md", "DualScope Minimal Real-Run Command Entrypoint Package", report_lines)
    write_json(output_dir / "dualscope_real_run_entrypoint_package_verdict.json", verdict)
    write_json(output_dir / "dualscope_real_run_entrypoint_package_next_step_recommendation.json", rec)
    write_json(output_dir / "dualscope_real_run_entrypoint_command_manifest.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "commands": commands})
    write_json(output_dir / "dualscope_real_run_entrypoint_dry_run_artifact_map.json", {group: [str(path) for path in paths] for group, paths in _required_artifacts(dry_root).items()})
    (output_dir / "dualscope_real_run_entrypoint_user_command_reference.md").write_text(
        "\n".join(["# DualScope Real-Run Entrypoint Command Reference", "", "Use the dry-run commands in `dualscope_real_run_entrypoint_command_manifest.json` before real execution."]) + "\n",
        encoding="utf-8",
    )
    return {"summary": summary, "verdict": verdict, "recommendation": rec}

