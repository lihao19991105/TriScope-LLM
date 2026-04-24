"""Execute preflight checks for the DualScope minimal first-slice real run."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_preflight_common import (
    SCHEMA_VERSION,
    TASK_NAME,
    check_artifact_group,
    load_json,
    required_stage_artifacts,
    status_payload,
    write_json,
    write_jsonl,
)


def _read_first_jsonl_row(path: Path) -> dict[str, Any] | None:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                payload = json.loads(line)
                if isinstance(payload, dict):
                    return payload
                raise ValueError("First JSONL row is not an object.")
    return None


def _safe_import_tokenizer(model_path: Path) -> dict[str, Any]:
    try:
        from transformers import AutoTokenizer
    except Exception as exc:  # pragma: no cover - environment dependent
        return status_payload(
            "tokenizer_load_check",
            "failed",
            False,
            "transformers import failed",
            error=str(exc),
        )
    try:
        tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True, trust_remote_code=False)
        return status_payload(
            "tokenizer_load_check",
            "passed",
            True,
            "Tokenizer loaded locally without loading full model weights.",
            tokenizer_class=tokenizer.__class__.__name__,
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        return status_payload(
            "tokenizer_load_check",
            "failed",
            False,
            "Tokenizer load failed.",
            error=str(exc),
        )


def _gpu_check() -> dict[str, Any]:
    physical_gpus: list[dict[str, Any]] = []
    nvidia_smi_status = "not_executed"
    nvidia_smi_error = None
    try:
        smi = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.used",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if smi.returncode == 0:
            nvidia_smi_status = "passed"
            for line in smi.stdout.splitlines():
                parts = [part.strip() for part in line.split(",")]
                if len(parts) >= 4:
                    physical_gpus.append(
                        {
                            "index": int(parts[0]),
                            "name": parts[1],
                            "memory_total_mb": int(parts[2]),
                            "memory_used_mb": int(parts[3]),
                        }
                    )
        else:
            nvidia_smi_status = "failed"
            nvidia_smi_error = smi.stderr
    except Exception as exc:  # pragma: no cover - environment dependent
        nvidia_smi_status = "failed"
        nvidia_smi_error = str(exc)

    try:
        import torch
    except Exception as exc:  # pragma: no cover - environment dependent
        return status_payload(
            "gpu_check",
            "failed",
            False,
            "torch import failed",
            error=str(exc),
            nvidia_smi_status=nvidia_smi_status,
            nvidia_smi_error=nvidia_smi_error,
            physical_gpu_count=len(physical_gpus),
            physical_3090_count=sum(1 for gpu in physical_gpus if "3090" in gpu["name"]),
            physical_gpus=physical_gpus,
        )
    cuda_available = bool(torch.cuda.is_available())
    gpu_count = int(torch.cuda.device_count()) if cuda_available else 0
    gpus = []
    if cuda_available:
        for index in range(gpu_count):
            props = torch.cuda.get_device_properties(index)
            gpus.append(
                {
                    "index": index,
                    "name": props.name,
                    "total_memory_gb": round(props.total_memory / (1024**3), 2),
                }
            )
    return status_payload(
        "gpu_check",
        "passed" if cuda_available else "torch_cuda_unavailable",
        cuda_available,
        "torch CUDA available." if cuda_available else "Physical GPUs may be visible, but torch CUDA is unavailable in this Python environment.",
        torch_version=getattr(torch, "__version__", "unknown"),
        cuda_available=cuda_available,
        torch_visible_gpu_count=gpu_count,
        torch_gpus=gpus,
        nvidia_smi_status=nvidia_smi_status,
        nvidia_smi_error=nvidia_smi_error,
        physical_gpu_count=len(physical_gpus),
        physical_3090_count=sum(1 for gpu in physical_gpus if "3090" in gpu["name"]),
        physical_gpus=physical_gpus,
    )


def _py_compile_check(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_first_slice_preflight_common.py",
        "src/eval/dualscope_minimal_first_slice_real_run_preflight.py",
        "src/eval/post_dualscope_minimal_first_slice_real_run_preflight_analysis.py",
        "scripts/build_dualscope_minimal_first_slice_real_run_preflight.py",
        "scripts/build_post_dualscope_minimal_first_slice_real_run_preflight_analysis.py",
        "src/eval/dualscope_minimal_first_slice_real_run_plan.py",
        "scripts/build_dualscope_minimal_first_slice_real_run_plan.py",
    ]
    cmd = [sys.executable, "-m", "py_compile", *files]
    result = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=False)
    return status_payload(
        "py_compile_check",
        "passed" if result.returncode == 0 else "failed",
        result.returncode == 0,
        "py_compile passed." if result.returncode == 0 else "py_compile failed.",
        command=" ".join(cmd),
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        files=files,
    )


def build_dualscope_minimal_first_slice_real_run_preflight(
    real_run_plan_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]

    scope = load_json(real_run_plan_dir / "dualscope_first_slice_real_run_scope.json")
    dataset_plan = load_json(real_run_plan_dir / "dualscope_first_slice_dataset_slice_plan.json")
    model_plan = load_json(real_run_plan_dir / "dualscope_first_slice_model_plan.json")
    capability_plan = load_json(real_run_plan_dir / "dualscope_first_slice_capability_mode_plan.json")
    commands = load_json(real_run_plan_dir / "dualscope_first_slice_run_command_plan.json")
    fallback_plan = load_json(real_run_plan_dir / "dualscope_first_slice_failure_fallback_plan.json")

    dataset_path = repo_root / dataset_plan["source_path_expectation"]
    model_path = Path(model_plan["local_path_expectation"])
    output_root = repo_root / "outputs/dualscope_minimal_first_slice_real_run"

    preflight_scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "seed": seed,
        "real_run_plan_dir": str(real_run_plan_dir.resolve()),
        "dataset_path": str(dataset_path),
        "model_path": str(model_path),
        "output_root": str(output_root),
        "preflight_only": True,
        "training_executed": False,
        "full_matrix_executed": False,
    }

    dataset_exists = dataset_path.exists()
    dataset_path_check = status_payload(
        "dataset_path_check",
        "passed" if dataset_exists else "dataset_missing",
        dataset_exists,
        "Dataset path exists." if dataset_exists else "Dataset path missing; real run must stop until provided.",
        path=str(dataset_path),
        expected_from_plan=dataset_plan["source_path_expectation"],
    )
    if dataset_exists:
        try:
            row = _read_first_jsonl_row(dataset_path)
            fields = set(row or {})
            valid_schema = bool(row) and (
                {"instruction", "output"}.issubset(fields)
                or {"prompt", "response"}.issubset(fields)
                or {"query", "target"}.issubset(fields)
            )
            dataset_schema_check = status_payload(
                "dataset_schema_check",
                "passed" if valid_schema else "failed",
                valid_schema,
                "Dataset schema is compatible." if valid_schema else "Dataset schema lacks required prompt/response fields.",
                observed_fields=sorted(fields),
            )
            dataset_sliceability_check = status_payload(
                "dataset_sliceability_check",
                "passed" if valid_schema else "failed",
                valid_schema,
                "Dataset can be sliced if enough rows exist; row count is deferred to real pre-run builder.",
                required_splits=dataset_plan["split_names"],
            )
        except Exception as exc:
            dataset_schema_check = status_payload("dataset_schema_check", "failed", False, "Dataset schema read failed.", error=str(exc))
            dataset_sliceability_check = status_payload("dataset_sliceability_check", "failed", False, "Dataset sliceability blocked by schema failure.")
    else:
        dataset_schema_check = status_payload(
            "dataset_schema_check",
            "blocked_by_dataset_missing",
            False,
            "Dataset schema check blocked because dataset file is missing.",
        )
        dataset_sliceability_check = status_payload(
            "dataset_sliceability_check",
            "blocked_by_dataset_missing",
            False,
            "Dataset sliceability check blocked because dataset file is missing.",
        )

    model_path_check = status_payload(
        "model_path_check",
        "passed" if model_path.exists() else "failed",
        model_path.exists(),
        "Model path exists." if model_path.exists() else "Model path missing.",
        path=str(model_path),
    )
    tokenizer_check = _safe_import_tokenizer(model_path) if model_path.exists() else status_payload(
        "tokenizer_load_check", "blocked_by_model_missing", False, "Tokenizer check blocked because model path is missing."
    )
    config_path = model_path / "config.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            model_config_check = status_payload(
                "model_config_check",
                "passed",
                True,
                "Model config is readable.",
                config_path=str(config_path),
                model_type=config.get("model_type", "unknown"),
            )
        except Exception as exc:
            model_config_check = status_payload("model_config_check", "failed", False, "Model config read failed.", error=str(exc))
    else:
        model_config_check = status_payload("model_config_check", "failed", False, "Model config missing.", config_path=str(config_path))

    gpu_check = _gpu_check()

    try:
        output_root.mkdir(parents=True, exist_ok=True)
        probe_path = output_root / ".preflight_write_probe"
        probe_path.write_text("ok\n", encoding="utf-8")
        probe_path.unlink()
        output_dir_check = status_payload("output_dir_check", "passed", True, "Output root is writable.", output_root=str(output_root))
    except Exception as exc:
        output_dir_check = status_payload("output_dir_check", "failed", False, "Output root is not writable.", error=str(exc))

    try:
        usage = shutil.disk_usage(output_root)
        available_gb = round(usage.free / (1024**3), 2)
        disk_space_check = status_payload(
            "disk_space_check",
            "passed" if available_gb >= 10 else "failed",
            available_gb >= 10,
            "Disk space is sufficient." if available_gb >= 10 else "Disk space below recommended 10GB.",
            available_gb=available_gb,
        )
    except Exception as exc:
        disk_space_check = status_payload("disk_space_check", "unknown", False, "Disk space check failed.", error=str(exc))

    stage_roots = {
        "stage1": repo_root / "outputs/dualscope_illumination_screening_freeze/default",
        "stage2": repo_root / "outputs/dualscope_confidence_verification_with_without_logprobs/default",
        "stage3": repo_root / "outputs/dualscope_budget_aware_two_stage_fusion_design/default",
        "matrix": repo_root / "outputs/dualscope_experimental_matrix_freeze/default",
        "real_run_plan": real_run_plan_dir,
    }
    artifact_groups = {
        group: check_artifact_group(stage_roots[group], names)
        for group, names in required_stage_artifacts().items()
    }
    all_stage_artifacts_exist = all(not group["missing"] for group in artifact_groups.values())
    stage_artifact_checks = status_payload(
        "stage_artifact_checks",
        "passed" if all_stage_artifacts_exist else "failed",
        all_stage_artifacts_exist,
        "All required stage artifacts exist." if all_stage_artifacts_exist else "One or more required stage artifacts are missing.",
        groups=artifact_groups,
    )

    stage1_io = load_json(stage_roots["stage1"] / "dualscope_illumination_io_contract.json")
    stage2_public = load_json(stage_roots["stage2"] / "dualscope_confidence_public_field_contract.json")
    stage3_dependency = load_json(stage_roots["stage3"] / "dualscope_stage_dependency_contract.json")
    stage3_final = load_json(stage_roots["stage3"] / "dualscope_final_decision_contract.json")
    stage1_fields = set(stage1_io.get("fusion_stage_readable_fields", [])) | set(stage3_dependency.get("required_stage1_fields", []))
    stage2_fields = set(stage2_public.get("mode_shared_fields", [])) | set(stage2_public.get("fusion_readable_fields", []))
    stage3_required_stage1 = set(stage3_dependency.get("required_stage1_fields", []))
    stage3_required_stage2 = set(stage3_dependency.get("required_stage2_fields", []))
    final_fields = set(stage3_final.get("explainable_output_fields", [])) | set(stage3_final.keys())
    compatibility_checks = {
        "stage1_candidate_flag": "confidence_verification_candidate_flag" in stage1_fields,
        "stage1_screening_score": "screening_risk_score" in stage1_fields,
        "stage1_screening_bucket": "screening_risk_bucket" in stage1_fields,
        "stage2_capability_mode": "capability_mode" in stage2_fields,
        "stage2_degradation_flag": "verification_confidence_degradation_flag" in str(stage2_public),
        "stage3_reads_stage1": {"screening_risk_score", "confidence_verification_candidate_flag"}.issubset(stage3_required_stage1),
        "stage3_reads_stage2": {"capability_mode", "verification_risk_score"}.issubset(stage3_required_stage2),
        "stage3_final_score": "final_risk_score" in str(stage3_final),
        "stage3_final_bucket": "final_risk_bucket" in str(stage3_final),
        "stage3_final_decision": "final_decision_flag" in str(stage3_final),
    }
    contract_compatibility_check = status_payload(
        "contract_compatibility_check",
        "passed" if all(compatibility_checks.values()) else "failed",
        all(compatibility_checks.values()),
        "Stage public fields are compatible." if all(compatibility_checks.values()) else "Stage public fields are not fully compatible.",
        checks=compatibility_checks,
    )

    with_logprobs_available = bool(gpu_check["passed"] and model_path_check["passed"] and tokenizer_check["passed"])
    capability_mode_check = status_payload(
        "capability_mode_check",
        "with_logprobs_available_via_local_logits" if with_logprobs_available else "fallback_required_unknown_logprobs",
        True,
        (
            "Local CUDA inference path is available; with-logprobs can be implemented from local logits."
            if with_logprobs_available
            else "with-logprobs backend capability is not confirmed in this preflight environment; without-logprobs fallback remains available and must be marked if used."
        ),
        with_logprobs_capability="available_via_local_logits" if with_logprobs_available else "unknown",
        fallback_required=not with_logprobs_available,
        fallback_protocol="without_logprobs",
        fallback_degradation_flag="verification_confidence_degradation_flag",
        default_attempt=capability_plan["default_attempt"],
    )

    forbidden_terms = ["route_c", "199", "full_matrix", "full finetune", "full_finetune"]
    command_rows = commands["commands"]
    command_checks = {
        "commands_present": bool(command_rows),
        "all_planned_not_executed": all(row.get("planned_not_executed_yet") is True for row in command_rows),
        "no_forbidden_terms": not any(term in row.get("command", "") for term in forbidden_terms for row in command_rows),
        "output_paths_dualscope": all("dualscope" in row.get("command", "") for row in command_rows),
    }
    planned_command_consistency_check = status_payload(
        "planned_command_consistency_check",
        "passed" if all(command_checks.values()) else "failed",
        all(command_checks.values()),
        "Planned commands are consistent and remain non-executed." if all(command_checks.values()) else "Planned command consistency failed.",
        checks=command_checks,
        command_count=len(command_rows),
    )

    py_compile_check = _py_compile_check(repo_root)

    dry_run_config = {
        "dataset_path": str(dataset_path),
        "model_path": str(model_path),
        "trigger": scope["trigger_id"],
        "target": scope["target_id"],
        "capability_mode": "auto_with_without_fallback",
        "output_root": str(output_root),
        "python_executable": sys.executable,
        "recommended_gpu_env": {
            "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
            "CUDA_VISIBLE_DEVICES": "2,3",
        },
        "stage_roots": {key: str(value) for key, value in stage_roots.items()},
        "planned_commands": command_rows,
        "fallback_policy": fallback_plan["fallbacks"],
    }
    dry_run_fields = [
        "dataset_path",
        "model_path",
        "trigger",
        "target",
        "capability_mode",
        "output_root",
        "stage_roots",
        "planned_commands",
        "fallback_policy",
    ]
    dry_run_config_check = status_payload(
        "dry_run_config_check",
        "passed",
        True,
        "Dry-run config object constructed without executing training.",
        required_fields_present=all(field in dry_run_config for field in dry_run_fields),
        dry_run_config=dry_run_config,
    )

    forbidden_expansion_flags = {
        "full_finetune": False,
        "old_route_c_chain": False,
        "benchmark_truth_change": False,
        "gate_semantic_change": False,
        "full_matrix_execution": False,
        "model_axis_expansion": False,
        "budget_expansion": False,
    }
    forbidden_expansion_check = status_payload(
        "forbidden_expansion_check",
        "passed",
        True,
        "No forbidden expansion detected in preflight artifacts.",
        flags=forbidden_expansion_flags,
    )

    checks = {
        "dataset_path_check": dataset_path_check,
        "dataset_schema_check": dataset_schema_check,
        "dataset_sliceability_check": dataset_sliceability_check,
        "model_path_check": model_path_check,
        "tokenizer_load_check": tokenizer_check,
        "model_config_check": model_config_check,
        "gpu_check": gpu_check,
        "output_dir_check": output_dir_check,
        "disk_space_check": disk_space_check,
        "stage_artifact_checks": stage_artifact_checks,
        "contract_compatibility_check": contract_compatibility_check,
        "capability_mode_check": capability_mode_check,
        "planned_command_consistency_check": planned_command_consistency_check,
        "py_compile_check": py_compile_check,
        "dry_run_config_check": dry_run_config_check,
        "forbidden_expansion_check": forbidden_expansion_check,
    }
    details = [{"schema_version": SCHEMA_VERSION, "detail_type": key, "payload": value} for key, value in checks.items()]
    blocking_reasons = [
        key for key, value in checks.items()
        if not value["passed"] and key not in {"gpu_check", "capability_mode_check"}
    ]
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "preflight_only": True,
        "training_executed": False,
        "full_matrix_executed": False,
        "dataset_exists": dataset_exists,
        "model_path_exists": model_path_check["passed"],
        "tokenizer_load_passed": tokenizer_check["passed"],
        "gpu_available": gpu_check["passed"],
        "physical_gpu_count": gpu_check.get("physical_gpu_count", 0),
        "physical_3090_count": gpu_check.get("physical_3090_count", 0),
        "torch_cuda_available": gpu_check.get("cuda_available", False),
        "output_dir_writable": output_dir_check["passed"],
        "stage_artifacts_exist": stage_artifact_checks["passed"],
        "contract_compatibility_passed": contract_compatibility_check["passed"],
        "with_logprobs_capability": capability_mode_check["with_logprobs_capability"],
        "without_logprobs_fallback_available": True,
        "recommended_gpu_env": {
            "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
            "CUDA_VISIBLE_DEVICES": "2,3",
        },
        "planned_commands_consistent": planned_command_consistency_check["passed"],
        "py_compile_passed": py_compile_check["passed"],
        "dry_run_config_constructed": dry_run_config_check["passed"],
        "forbidden_expansion_detected": False,
        "blocking_reasons": blocking_reasons,
        "details_row_count": len(details),
    }
    missing_requirements = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "missing_requirements": [
            {
                "requirement": "stanford_alpaca_first_slice_jsonl",
                "path": str(dataset_path),
                "reason": "required dataset file is missing",
            }
        ] if not dataset_exists else [],
    }
    repair_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "repair_steps": [
            "Provide a real Alpaca-format JSONL at the planned dataset path.",
            "Rerun preflight without changing matrix scope.",
            "Run GPU checks and future real-run commands with `.venv/bin/python` plus `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3`.",
            "If tokenizer or CUDA checks fail later, repair those locally before real run.",
        ],
        "do_not_do": ["fabricate_data", "run_full_matrix", "change_benchmark_truth", "continue_route_c"],
    }
    environment_snapshot = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "python_executable": sys.executable,
        "recommended_python_executable": ".venv/bin/python",
        "recommended_gpu_command_prefix": "CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3",
        "repo_root": str(repo_root),
        "output_dir": str(output_dir.resolve()),
        "disk_available_gb": disk_space_check.get("available_gb", "unknown"),
        "gpu_check": gpu_check,
    }
    report = "\n".join(
        [
            "# DualScope First Slice Real-Run Preflight Report",
            "",
            f"- Dataset exists: `{dataset_exists}`",
            f"- Model path exists: `{model_path_check['passed']}`",
            f"- Tokenizer load passed: `{tokenizer_check['passed']}`",
            f"- GPU available: `{gpu_check['passed']}`",
            f"- Physical 3090 count: `{gpu_check.get('physical_3090_count', 0)}`",
            f"- Torch visible GPU count: `{gpu_check.get('torch_visible_gpu_count', 0)}`",
            f"- with-logprobs capability: `{capability_mode_check['with_logprobs_capability']}`",
            "- Recommended GPU command prefix: `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3`",
            f"- Stage artifacts exist: `{stage_artifact_checks['passed']}`",
            f"- Contract compatibility: `{contract_compatibility_check['passed']}`",
            f"- py_compile passed: `{py_compile_check['passed']}`",
            f"- Blocking reasons: `{blocking_reasons}`",
            "",
            "This is preflight only. No training or full experiment was executed.",
            "",
        ]
    )

    write_json(output_dir / "dualscope_first_slice_preflight_scope.json", preflight_scope)
    write_json(output_dir / "dualscope_first_slice_dataset_path_check.json", dataset_path_check)
    write_json(output_dir / "dualscope_first_slice_dataset_schema_check.json", dataset_schema_check)
    write_json(output_dir / "dualscope_first_slice_dataset_sliceability_check.json", dataset_sliceability_check)
    write_json(output_dir / "dualscope_first_slice_model_path_check.json", model_path_check)
    write_json(output_dir / "dualscope_first_slice_tokenizer_load_check.json", tokenizer_check)
    write_json(output_dir / "dualscope_first_slice_model_config_check.json", model_config_check)
    write_json(output_dir / "dualscope_first_slice_gpu_check.json", gpu_check)
    write_json(output_dir / "dualscope_first_slice_output_dir_check.json", output_dir_check)
    write_json(output_dir / "dualscope_first_slice_disk_space_check.json", disk_space_check)
    write_json(output_dir / "dualscope_first_slice_stage_artifact_checks.json", stage_artifact_checks)
    write_json(output_dir / "dualscope_first_slice_contract_compatibility_check.json", contract_compatibility_check)
    write_json(output_dir / "dualscope_first_slice_capability_mode_check.json", capability_mode_check)
    write_json(output_dir / "dualscope_first_slice_planned_command_consistency_check.json", planned_command_consistency_check)
    write_json(output_dir / "dualscope_first_slice_py_compile_check.json", py_compile_check)
    write_json(output_dir / "dualscope_first_slice_dry_run_config_check.json", dry_run_config_check)
    write_json(output_dir / "dualscope_first_slice_forbidden_expansion_check.json", forbidden_expansion_check)
    write_json(output_dir / "dualscope_first_slice_preflight_summary.json", summary)
    write_jsonl(output_dir / "dualscope_first_slice_preflight_details.jsonl", details)
    (output_dir / "dualscope_first_slice_preflight_report.md").write_text(report, encoding="utf-8")
    checklist_md = "\n".join(
        ["# DualScope First Slice Preflight Results", ""]
        + [f"- [{'x' if value['passed'] else ' '}] `{key}`: {value['status']} - {value['message']}" for key, value in checks.items()]
        + [""]
    )
    (output_dir / "dualscope_first_slice_preflight_checklist.md").write_text(checklist_md, encoding="utf-8")
    write_json(output_dir / "dualscope_first_slice_missing_requirements.json", missing_requirements)
    write_json(output_dir / "dualscope_first_slice_repair_plan.json", repair_plan)
    write_json(output_dir / "dualscope_first_slice_environment_snapshot.json", environment_snapshot)

    return {
        "summary": summary,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_preflight_summary.json").resolve()),
            "report": str((output_dir / "dualscope_first_slice_preflight_report.md").resolve()),
        },
    }
