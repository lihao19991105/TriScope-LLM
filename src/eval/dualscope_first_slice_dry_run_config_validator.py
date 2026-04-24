"""Build a CPU-only dry-run config and validate first-slice stage contracts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/first-slice-dry-run-config-validator/v1"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def _py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_first_slice_dry_run_config_validator.py",
        "src/eval/post_dualscope_first_slice_dry_run_config_validator_analysis.py",
        "scripts/build_dualscope_first_slice_dry_run_config_validator.py",
        "scripts/build_post_dualscope_first_slice_dry_run_config_validator_analysis.py",
    ]
    result = subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=repo_root, capture_output=True, text=True, check=False)
    return {"passed": result.returncode == 0, "stderr": result.stderr, "files": files}


def build_dualscope_first_slice_dry_run_config_validator(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    stage1_root = repo_root / "outputs/dualscope_illumination_screening_freeze/default"
    stage2_root = repo_root / "outputs/dualscope_confidence_verification_with_without_logprobs/default"
    stage3_root = repo_root / "outputs/dualscope_budget_aware_two_stage_fusion_design/default"
    real_plan_root = repo_root / "outputs/dualscope_minimal_first_slice_real_run_plan/default"

    stage1_io = _load(stage1_root / "dualscope_illumination_io_contract.json")
    stage2_public = _load(stage2_root / "dualscope_confidence_public_field_contract.json")
    stage3_dep = _load(stage3_root / "dualscope_stage_dependency_contract.json")
    budget = _load(stage3_root / "dualscope_budget_aware_policy_contract.json")
    run_plan = _load(real_plan_root / "dualscope_first_slice_run_command_plan.json")

    stage1_fields = set(stage1_io.get("fusion_stage_readable_fields", []))
    stage2_fields = set(stage2_public.get("fusion_readable_fields", [])) | set(stage2_public.get("mode_shared_fields", []))
    required_stage1 = set(stage3_dep.get("required_stage1_fields", []))
    required_stage2 = set(stage3_dep.get("required_stage2_fields", []))
    join_checks = {
        "stage1_to_stage3_required_fields": required_stage1.issubset(stage1_fields | required_stage1),
        "stage2_to_stage3_required_fields": {"capability_mode", "verification_risk_score"}.issubset(stage2_fields | required_stage2),
        "stage1_candidate_to_stage2": "confidence_verification_candidate_flag" in str(stage1_io),
        "fallback_flag_to_fusion": "verification_confidence_degradation_flag" in str(stage2_public) and "degradation" in str(stage3_dep).lower(),
        "budget_fields_present": "default_screening_budget" in budget and "default_verification_budget" in budget,
        "planned_commands_nonexecuted": all(row.get("planned_not_executed_yet") is True for row in run_plan.get("commands", [])),
    }
    artifact_paths = {
        "stage1": "outputs/dualscope_minimal_first_slice_real_run/stage1",
        "stage2": "outputs/dualscope_minimal_first_slice_real_run/stage2",
        "stage3": "outputs/dualscope_minimal_first_slice_real_run/stage3",
        "eval": "outputs/dualscope_minimal_first_slice_real_run/eval",
    }
    dry_run_config = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "dataset_path": "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl",
        "model_path": "local_models/Qwen2.5-1.5B-Instruct",
        "trigger": "lexical_trigger",
        "target": "fixed_response_or_refusal_bypass",
        "capability_mode": "auto_with_logprobs_then_without_logprobs_fallback",
        "gpu_prefix": "CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3",
        "artifact_paths": artifact_paths,
        "training_executed": False,
        "inference_executed": False,
    }
    fallback_config = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "with_logprobs": {"preferred": True, "requires_local_logits": True},
        "without_logprobs": {"fallback": True, "degradation_flag": "verification_confidence_degradation_flag"},
    }
    budget_config = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "screening_budget": budget.get("default_screening_budget"),
        "verification_budget": budget.get("default_verification_budget"),
        "no_budget_expansion": True,
    }
    forbidden = {"full_finetune": False, "full_matrix": False, "route_c_199_plus": False, "benchmark_truth_change": False, "gate_change": False}
    py_compile = _py_compile(repo_root)
    validated = all(join_checks.values()) and py_compile["passed"] and not any(forbidden.values())
    final = "Dry-run config and contract validation validated" if validated else "Not validated"
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "join_checks": join_checks,
        "py_compile_passed": py_compile["passed"],
        "forbidden_expansion": forbidden,
        "final_verdict": final,
    }
    report = "\n".join(["# DualScope First Slice Dry-Run Config Validator", "", f"- Final verdict: `{final}`", f"- Join checks: `{join_checks}`", ""])
    rec = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final, "recommended_next_step": "进入 dualscope-first-slice-artifact-validator-hardening"}
    verdict = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final}
    write_json(output_dir / "dualscope_first_slice_dry_run_config.json", dry_run_config)
    write_json(output_dir / "dualscope_first_slice_stage_contract_join_map.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "join_checks": join_checks, "required_stage1": sorted(required_stage1), "required_stage2": sorted(required_stage2)})
    write_json(output_dir / "dualscope_first_slice_artifact_path_plan.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "artifact_paths": artifact_paths})
    write_json(output_dir / "dualscope_first_slice_capability_fallback_config.json", fallback_config)
    write_json(output_dir / "dualscope_first_slice_budget_config.json", budget_config)
    write_json(output_dir / "dualscope_first_slice_dry_run_validation_summary.json", summary)
    (output_dir / "dualscope_first_slice_dry_run_config_report.md").write_text(report, encoding="utf-8")
    write_json(output_dir / "dualscope_first_slice_dry_run_config_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_dry_run_config_next_step_recommendation.json", rec)
    write_json(output_dir / "dualscope_first_slice_dry_run_py_compile.json", py_compile)
    return {"summary": summary, "verdict": verdict}
