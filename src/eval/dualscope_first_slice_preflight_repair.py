"""Build repair artifacts for DualScope first-slice real-run preflight."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_preflight_repair_common import (
    RECOMMENDED_GPU_PREFIX,
    RECOMMENDED_PYTHON,
    SCHEMA_VERSION,
    TARGET_DATASET_PATH,
    TASK_NAME,
    status_payload,
    utc_now,
    write_json,
    write_jsonl,
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def _environment_snapshot(repo_root: Path) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "python_executable": sys.executable,
        "recommended_python": RECOMMENDED_PYTHON,
        "recommended_gpu_prefix": RECOMMENDED_GPU_PREFIX,
        "repo_root": str(repo_root),
    }
    try:
        import torch

        snapshot.update(
            {
                "torch_imported": True,
                "torch_version": getattr(torch, "__version__", "unknown"),
                "cuda_available": bool(torch.cuda.is_available()),
                "torch_visible_gpu_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
                "torch_visible_gpus": [
                    torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())
                ]
                if torch.cuda.is_available()
                else [],
            }
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        snapshot.update({"torch_imported": False, "torch_error": str(exc)})
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
        snapshot.update(
            {
                "nvidia_smi_returncode": smi.returncode,
                "nvidia_smi_stdout": smi.stdout,
                "nvidia_smi_stderr": smi.stderr,
            }
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        snapshot.update({"nvidia_smi_error": str(exc)})
    try:
        usage = shutil.disk_usage(repo_root)
        snapshot["disk_available_gb"] = round(usage.free / (1024**3), 2)
    except Exception as exc:  # pragma: no cover - environment dependent
        snapshot["disk_available_error"] = str(exc)
    return snapshot


def _py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_first_slice_preflight_repair_common.py",
        "src/eval/dualscope_first_slice_preflight_repair.py",
        "src/eval/post_dualscope_first_slice_preflight_repair_analysis.py",
        "scripts/build_dualscope_first_slice_preflight_repair.py",
        "scripts/build_post_dualscope_first_slice_preflight_repair_analysis.py",
        "scripts/build_dualscope_first_slice_alpaca_jsonl.py",
        "scripts/check_dualscope_first_slice_dataset_schema.py",
    ]
    result = subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=repo_root, capture_output=True, text=True, check=False)
    return status_payload(
        "py_compile",
        "passed" if result.returncode == 0 else "failed",
        result.returncode == 0,
        "py_compile passed." if result.returncode == 0 else "py_compile failed.",
        command=" ".join([sys.executable, "-m", "py_compile", *files]),
        files=files,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
    )


def build_dualscope_first_slice_preflight_repair(
    preflight_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)

    preflight_summary = _load_json(preflight_dir / "dualscope_first_slice_preflight_summary.json")
    dataset_target = repo_root / TARGET_DATASET_PATH
    dataset_exists = dataset_target.exists()

    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "seed": seed,
        "repair_only": True,
        "training_executed": False,
        "real_run_executed": False,
        "full_matrix_executed": False,
        "preflight_dir": str(preflight_dir.resolve()),
        "target_dataset_path": str(dataset_target),
        "source_preflight_verdict": "Partially validated",
        "does_not_claim_preflight_validated": True,
    }
    blockers = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "blockers": [
            {
                "blocker_id": "missing_stanford_alpaca_first_slice_jsonl",
                "status": "open" if not dataset_exists else "resolved",
                "path": str(dataset_target),
                "repair_path": "materialize from a real user-provided Alpaca JSON/JSONL source",
                "do_not_do": "do_not_fabricate_or_download_data_in_repair_stage",
            },
            {
                "blocker_id": "dataset_schema_and_sliceability_blocked",
                "status": "open" if not dataset_exists else "needs_rerun_preflight",
                "blocked_by": "missing_stanford_alpaca_first_slice_jsonl" if not dataset_exists else "requires_schema_rerun",
            },
        ],
        "gpu_note": {
            "status": "repair_guidance_recorded",
            "recommended_prefix": RECOMMENDED_GPU_PREFIX,
            "latest_preflight_gpu_available": preflight_summary.get("gpu_available"),
            "latest_preflight_3090_count": preflight_summary.get("physical_3090_count"),
        },
    }
    dataset_import_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "requires_real_source_file": True,
        "synthetic_data_allowed": False,
        "supported_source_formats": ["json_array", "json_object_with_data_examples_or_rows", "jsonl"],
        "supported_field_families": [
            ["instruction", "input", "output"],
            ["prompt", "response"],
            ["query", "target"],
        ],
        "target_output_file": TARGET_DATASET_PATH,
        "target_schema": ["example_id", "dataset_id", "instruction", "input", "prompt", "response", "split", "source", "metadata"],
        "example_id_policy": "use source example_id/id if present, else derive deterministic sha1 id",
        "prompt_construction_rule": "prompt field if available, else instruction plus optional input block",
        "empty_input_allowed": True,
        "empty_prompt_allowed": False,
        "empty_response_allowed": False,
    }
    dataset_schema_contract = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "required_fields": ["example_id", "dataset_id", "prompt", "response", "split"],
        "checks": [
            "row_count",
            "missing_required_field_count",
            "empty_prompt_count",
            "empty_response_count",
            "duplicate_example_id_count",
            "split_distribution",
        ],
        "verdicts": ["pass", "blocked_by_missing_file", "failed_schema_validation"],
        "no_implicit_repair": True,
    }
    import_command_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "planned_not_executed_yet": True,
        "command": (
            f"{RECOMMENDED_PYTHON} scripts/build_dualscope_first_slice_alpaca_jsonl.py "
            "--source-file <REAL_ALPACA_SOURCE_JSON_OR_JSONL> "
            f"--output-file {TARGET_DATASET_PATH} "
            "--max-examples 72 --seed 2025 --split-name first_slice --dataset-id stanford_alpaca"
        ),
        "placeholder_source_path_must_be_replaced": True,
    }
    schema_command_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "planned_not_executed_yet": True,
        "command": (
            f"{RECOMMENDED_PYTHON} scripts/check_dualscope_first_slice_dataset_schema.py "
            f"--dataset-file {TARGET_DATASET_PATH} "
            "--output-dir outputs/dualscope_first_slice_dataset_schema_check/default"
        ),
    }
    gpu_requirements = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "real_run_requires_gpu": True,
        "repair_stage_gpu_required": False,
        "required_python": RECOMMENDED_PYTHON,
        "required_gpu_prefix": RECOMMENDED_GPU_PREFIX,
        "minimum_visible_gpu_count_for_real_run": 1,
        "recommended_visible_gpu_count": 2,
        "recommended_gpu_type": "RTX 3090",
        "can_continue_without_gpu_now": [
            "dataset_repair",
            "schema_validation",
            "command_plan",
            "cpu_only_dry_run_config",
            "artifact_contract_checks",
        ],
        "do_not_do_without_gpu": ["lora_training", "gpu_inference_real_run", "full_first_slice_execution"],
    }
    environment_snapshot = _environment_snapshot(repo_root)
    rerun_preflight_checklist = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "required_before_rerun": [
            {"item": "real Alpaca JSONL exists", "path": TARGET_DATASET_PATH, "currently_satisfied": dataset_exists},
            {"item": "dataset schema checker passes", "currently_satisfied": False, "blocked_until_dataset_exists": not dataset_exists},
            {"item": "model path exists", "currently_satisfied": bool(preflight_summary.get("model_path_exists"))},
            {"item": "tokenizer loads", "currently_satisfied": bool(preflight_summary.get("tokenizer_load_passed"))},
            {"item": "CUDA visible or fallback explicitly marked", "currently_satisfied": bool(preflight_summary.get("gpu_available"))},
            {"item": "output dir writable", "currently_satisfied": bool(preflight_summary.get("output_dir_writable"))},
        ],
        "rerun_preflight_command": (
            f"{RECOMMENDED_GPU_PREFIX} {RECOMMENDED_PYTHON} "
            "scripts/build_dualscope_minimal_first_slice_real_run_preflight.py "
            "--output-dir outputs/dualscope_minimal_first_slice_real_run_preflight/default"
        ),
        "rerun_post_analysis_command": (
            f"{RECOMMENDED_PYTHON} scripts/build_post_dualscope_minimal_first_slice_real_run_preflight_analysis.py "
            "--preflight-dir outputs/dualscope_minimal_first_slice_real_run_preflight/default "
            "--output-dir outputs/dualscope_minimal_first_slice_real_run_preflight_analysis/default"
        ),
    }
    py_compile = _py_compile(repo_root)
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "repair_package_complete": True,
        "dataset_exists_now": dataset_exists,
        "dataset_import_tool_ready": True,
        "dataset_schema_check_tool_ready": True,
        "gpu_environment_requirements_recorded": True,
        "rerun_preflight_checklist_ready": True,
        "py_compile_passed": py_compile["passed"],
        "synthetic_data_generated": False,
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_semantics_changed": False,
        "preflight_validated_by_this_stage": False,
        "details_row_count": 10,
    }
    details = [
        {"schema_version": SCHEMA_VERSION, "detail_type": "scope", "payload": scope},
        {"schema_version": SCHEMA_VERSION, "detail_type": "blockers", "payload": blockers},
        {"schema_version": SCHEMA_VERSION, "detail_type": "dataset_import_contract", "payload": dataset_import_contract},
        {"schema_version": SCHEMA_VERSION, "detail_type": "dataset_schema_contract", "payload": dataset_schema_contract},
        {"schema_version": SCHEMA_VERSION, "detail_type": "import_command_plan", "payload": import_command_plan},
        {"schema_version": SCHEMA_VERSION, "detail_type": "schema_command_plan", "payload": schema_command_plan},
        {"schema_version": SCHEMA_VERSION, "detail_type": "gpu_requirements", "payload": gpu_requirements},
        {"schema_version": SCHEMA_VERSION, "detail_type": "environment_snapshot", "payload": environment_snapshot},
        {"schema_version": SCHEMA_VERSION, "detail_type": "rerun_preflight_checklist", "payload": rerun_preflight_checklist},
        {"schema_version": SCHEMA_VERSION, "detail_type": "py_compile", "payload": py_compile},
    ]
    report = "\n".join(
        [
            "# DualScope First Slice Preflight Repair Report",
            "",
            "- Repair package validates import/schema/environment tooling only.",
            f"- Target dataset exists now: `{dataset_exists}`",
            "- Synthetic data generated: `False`",
            f"- Dataset import tool ready: `{summary['dataset_import_tool_ready']}`",
            f"- Dataset schema check tool ready: `{summary['dataset_schema_check_tool_ready']}`",
            f"- GPU requirement prefix: `{RECOMMENDED_GPU_PREFIX}`",
            f"- py_compile passed: `{py_compile['passed']}`",
            "- Next step after validated repair is dataset materialization, not real run.",
            "",
        ]
    )

    outputs = {
        "dualscope_first_slice_preflight_repair_scope.json": scope,
        "dualscope_first_slice_preflight_blockers.json": blockers,
        "dualscope_first_slice_dataset_import_contract.json": dataset_import_contract,
        "dualscope_first_slice_dataset_schema_contract.json": dataset_schema_contract,
        "dualscope_first_slice_dataset_import_command_plan.json": import_command_plan,
        "dualscope_first_slice_dataset_schema_check_command_plan.json": schema_command_plan,
        "dualscope_first_slice_gpu_environment_requirements.json": gpu_requirements,
        "dualscope_first_slice_environment_snapshot.json": environment_snapshot,
        "dualscope_first_slice_rerun_preflight_checklist.json": rerun_preflight_checklist,
        "dualscope_first_slice_repair_summary.json": summary,
        "dualscope_first_slice_py_compile_check.json": py_compile,
        "dualscope_first_slice_missing_requirements.json": {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "missing_requirements": [
                {"requirement": "real_alpaca_source_file", "status": "external_required", "target_output": TARGET_DATASET_PATH},
            ],
        },
        "dualscope_first_slice_repair_readiness_matrix.json": {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "rows": [
                {"item": "repair_tools", "ready": True},
                {"item": "real_dataset_materialized", "ready": dataset_exists},
                {"item": "preflight_rerun", "ready": False},
                {"item": "real_run", "ready": False},
            ],
        },
    }
    for name, payload in outputs.items():
        write_json(output_dir / name, payload)
    write_jsonl(output_dir / "dualscope_first_slice_repair_details.jsonl", details)
    (output_dir / "dualscope_first_slice_repair_report.md").write_text(report, encoding="utf-8")
    (output_dir / "dualscope_first_slice_user_action_items.md").write_text(
        "\n".join(
            [
                "# DualScope First Slice User Action Items",
                "",
                "1. Provide a real Alpaca-style JSON or JSONL source file.",
                "2. Run the dataset import command with that real source path.",
                "3. Run the schema checker.",
                "4. Rerun preflight with `.venv/bin/python` and the 3090 GPU prefix.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "summary": summary,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_repair_summary.json").resolve()),
            "report": str((output_dir / "dualscope_first_slice_repair_report.md").resolve()),
        },
    }
