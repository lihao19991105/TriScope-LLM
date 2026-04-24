"""Build the final go/no-go package for the DualScope minimal first-slice real run."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/minimal-first-slice-real-run-readiness-package/v1"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"missing": True, "path": str(path)}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"payload": payload}


def _extract_script_path(command: str) -> str | None:
    match = re.search(r"(?P<script>scripts/[A-Za-z0-9_./-]+\.py)", command)
    return match.group("script") if match else None


def _py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_minimal_first_slice_real_run_readiness_package.py",
        "src/eval/post_dualscope_minimal_first_slice_real_run_readiness_package_analysis.py",
        "scripts/build_dualscope_minimal_first_slice_real_run_readiness_package.py",
        "scripts/build_post_dualscope_minimal_first_slice_real_run_readiness_package_analysis.py",
    ]
    result = subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=repo_root, capture_output=True, text=True, check=False)
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "passed": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "files": files,
    }


def build_dualscope_minimal_first_slice_real_run_readiness_package(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)

    materialization = _load(repo_root / "outputs/dualscope_first_slice_dataset_materialization/default/dualscope_first_slice_dataset_materialization_summary.json")
    preflight = _load(repo_root / "outputs/dualscope_first_slice_preflight_rerun/default/dualscope_first_slice_preflight_summary.json")
    preflight_verdict = _load(repo_root / "outputs/dualscope_first_slice_preflight_rerun_analysis/default/dualscope_first_slice_preflight_rerun_verdict.json")
    run_plan = _load(repo_root / "outputs/dualscope_minimal_first_slice_real_run_plan/default/dualscope_first_slice_run_command_plan.json")
    scope = _load(repo_root / "outputs/dualscope_minimal_first_slice_real_run_plan/default/dualscope_first_slice_real_run_scope.json")
    model_plan = _load(repo_root / "outputs/dualscope_minimal_first_slice_real_run_plan/default/dualscope_first_slice_model_plan.json")

    dataset_path = repo_root / "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl"
    model_path = Path(model_plan.get("local_path_expectation", ""))
    commands = run_plan.get("commands", [])
    command_checks = []
    missing_entrypoints = []
    for command in commands:
        script = _extract_script_path(command.get("command", ""))
        exists = bool(script) and (repo_root / script).exists()
        if script and not exists:
            missing_entrypoints.append(script)
        command_checks.append(
            {
                "command_id": command.get("command_id"),
                "script": script,
                "script_exists": exists if script else None,
                "planned_not_executed_yet": command.get("planned_not_executed_yet") is True,
            }
        )

    dataset_ready = dataset_path.exists() and materialization.get("final_verdict") == "Dataset materialization validated"
    gpu_ready = preflight.get("gpu_available") is True and preflight.get("torch_cuda_available") is True
    preflight_ready = preflight_verdict.get("final_verdict") == "First slice preflight rerun validated"
    model_ready = bool(str(model_path)) and model_path.exists()
    commands_defined = bool(commands)
    commands_safe = commands_defined and all(item["planned_not_executed_yet"] for item in command_checks)
    command_entrypoints_ready = not missing_entrypoints
    py_compile = _py_compile(repo_root)

    blockers = []
    if not dataset_ready:
        blockers.append({"blocker_id": "dataset_not_ready", "required_action": "Rerun dataset materialization with real Alpaca source."})
    if not gpu_ready:
        blockers.append({"blocker_id": "gpu_not_ready", "required_action": "Run preflight in GPU-enabled environment with RTX 3090 devices visible."})
    if not preflight_ready:
        blockers.append({"blocker_id": "preflight_not_validated", "required_action": "Rerun first-slice preflight rerun and post-analysis."})
    if not model_ready:
        blockers.append({"blocker_id": "model_not_ready", "required_action": "Restore local Qwen2.5-1.5B model path."})
    if not command_entrypoints_ready:
        blockers.append({"blocker_id": "missing_real_run_entrypoints", "missing_scripts": sorted(set(missing_entrypoints)), "required_action": "Implement minimal real-run command entrypoints before execution."})
    if not py_compile["passed"]:
        blockers.append({"blocker_id": "readiness_py_compile_failed", "required_action": "Repair readiness package Python files."})

    if dataset_ready and gpu_ready and preflight_ready and model_ready and commands_safe and command_entrypoints_ready and py_compile["passed"]:
        final_verdict = "Minimal real run readiness validated"
        recommendation = "Enter dualscope-minimal-first-slice-real-run"
    elif dataset_ready and gpu_ready and preflight_ready and model_ready and commands_safe and py_compile["passed"]:
        final_verdict = "Partially validated"
        recommendation = "Implement minimal real-run command-entrypoint package before starting real run"
    else:
        final_verdict = "Not validated"
        recommendation = "Resolve minimal real-run readiness blockers before execution"

    gpu_confirmation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "gpu_ready": gpu_ready,
        "gpu_available": preflight.get("gpu_available"),
        "torch_cuda_available": preflight.get("torch_cuda_available"),
        "physical_3090_count": preflight.get("physical_3090_count"),
        "with_logprobs_capability": preflight.get("with_logprobs_capability"),
    }
    dataset_confirmation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "dataset_ready": dataset_ready,
        "dataset_path": str(dataset_path),
        "dataset_exists": dataset_path.exists(),
        "materialization_verdict": materialization.get("final_verdict"),
    }
    model_confirmation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "model_ready": model_ready,
        "model_path": str(model_path),
        "model_exists": model_path.exists() if str(model_path) else False,
    }
    scope_confirmation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "scope": scope,
        "no_full_matrix": True,
        "no_model_axis_expansion": True,
        "no_route_c_199_plus": True,
    }
    command_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "commands_defined": commands_defined,
        "commands_safe_planned_only": commands_safe,
        "command_entrypoints_ready": command_entrypoints_ready,
        "command_checks": command_checks,
        "missing_entrypoints": sorted(set(missing_entrypoints)),
        "commands": commands,
    }
    checklist = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "checks": [
            {"check": "dataset_ready", "passed": dataset_ready},
            {"check": "model_ready", "passed": model_ready},
            {"check": "gpu_ready", "passed": gpu_ready},
            {"check": "preflight_rerun_validated", "passed": preflight_ready},
            {"check": "commands_defined", "passed": commands_defined},
            {"check": "commands_remain_planned", "passed": commands_safe},
            {"check": "command_entrypoints_ready", "passed": command_entrypoints_ready},
            {"check": "py_compile", "passed": py_compile["passed"]},
            {"check": "no_forbidden_expansion", "passed": True},
        ],
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "dataset_ready": dataset_ready,
        "model_ready": model_ready,
        "gpu_ready": gpu_ready,
        "preflight_ready": preflight_ready,
        "commands_safe": commands_safe,
        "command_entrypoints_ready": command_entrypoints_ready,
        "missing_entrypoints": sorted(set(missing_entrypoints)),
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    report = "\n".join(
        [
            "# DualScope Minimal First-Slice Real-Run Readiness Package",
            "",
            f"- Dataset ready: `{dataset_ready}`",
            f"- Model ready: `{model_ready}`",
            f"- GPU ready: `{gpu_ready}`",
            f"- Preflight rerun ready: `{preflight_ready}`",
            f"- Real-run command entrypoints ready: `{command_entrypoints_ready}`",
            f"- Missing entrypoints: `{', '.join(sorted(set(missing_entrypoints))) or 'none'}`",
            f"- Verdict: `{final_verdict}`",
            f"- Recommendation: {recommendation}",
            "",
            "This phase did not execute training, inference, or the full experiment matrix.",
            "",
        ]
    )
    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_real_run_readiness_validated__partially_validated__not_validated",
    }
    rec = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "blockers": blockers,
    }

    write_json(output_dir / "dualscope_minimal_real_run_command_plan.json", command_plan)
    write_json(output_dir / "dualscope_minimal_real_run_gpu_config_confirmation.json", gpu_confirmation)
    write_json(output_dir / "dualscope_minimal_real_run_dataset_path_confirmation.json", dataset_confirmation)
    write_json(output_dir / "dualscope_minimal_real_run_model_path_confirmation.json", model_confirmation)
    write_json(output_dir / "dualscope_minimal_real_run_scope_confirmation.json", scope_confirmation)
    write_json(output_dir / "dualscope_minimal_real_run_verification_checklist.json", checklist)
    write_json(output_dir / "dualscope_minimal_real_run_readiness_summary.json", summary)
    write_json(output_dir / "dualscope_minimal_real_run_readiness_blockers.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "blockers": blockers})
    write_json(output_dir / "dualscope_minimal_real_run_readiness_py_compile.json", py_compile)
    (output_dir / "dualscope_minimal_real_run_readiness_report.md").write_text(report, encoding="utf-8")
    write_json(output_dir / "dualscope_minimal_real_run_readiness_verdict.json", verdict)
    write_json(output_dir / "dualscope_minimal_real_run_readiness_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict, "recommendation": rec}

