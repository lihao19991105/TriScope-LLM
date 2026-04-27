"""Runtime readiness checks for DualScope isolated worktrees."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


READY_VERDICT = "Worktree GPU/BnB/input readiness validated"
PARTIAL_VERDICT = "Partially validated"
NOT_VALIDATED = "Not validated"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def run_command(command: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "passed": completed.returncode == 0,
        }
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"command": command, "returncode": 127, "stdout": "", "stderr": str(exc), "passed": False}


def dependency_check() -> dict[str, Any]:
    names = ("torch", "transformers", "accelerate", "bitsandbytes", "safetensors")
    return {name: importlib.util.find_spec(name) is not None for name in names}


def torch_cuda_check() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        "cuda_device_order": os.environ.get("CUDA_DEVICE_ORDER", ""),
    }
    try:
        import torch

        payload.update(
            {
                "torch_imported": True,
                "torch_version": torch.__version__,
                "torch_cuda_version": torch.version.cuda,
                "cuda_available": torch.cuda.is_available(),
                "cuda_device_count": torch.cuda.device_count(),
                "device_names": [
                    torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())
                ]
                if torch.cuda.is_available()
                else [],
            }
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        payload.update(
            {
                "torch_imported": False,
                "cuda_available": False,
                "cuda_device_count": 0,
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
    return payload


def path_status(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "is_symlink": path.is_symlink(),
        "writable": os.access(path, os.W_OK) if path.exists() else False,
        "resolved": str(path.resolve()) if path.exists() or path.is_symlink() else "",
    }


def check_worktree_runtime_readiness(
    *,
    output_dir: Path,
    labeled_pairs: Path,
    source_jsonl: Path,
    target_response_plan_dir: Path,
    alpaca_main_slice_plan_dir: Path,
    model_dir: Path,
    repo_model_symlink: Path,
    hf_home: Path,
    hf_hub_cache: Path,
    transformers_cache: Path,
    tmpdir: Path,
    registry_path: Path,
    attempt_pip_install: bool,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    blockers: list[str] = []
    warnings: list[str] = []

    deps = dependency_check()
    torch_check = torch_cuda_check()
    nvidia_smi = run_command(
        ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free", "--format=csv,noheader,nounits"],
        timeout=30,
    )
    gpu_blocker = (not bool(torch_check.get("cuda_available"))) or nvidia_smi.get("returncode") != 0

    pip_install_result: dict[str, Any] | None = None
    if not deps.get("bitsandbytes") and attempt_pip_install:
        pip_install_result = run_command(
            [sys.executable, "-m", "pip", "install", "bitsandbytes>=0.43,<0.47"],
            timeout=600,
        )
        deps = dependency_check()
        if not deps.get("bitsandbytes"):
            warnings.append("bitsandbytes_unavailable_after_install_attempt")
    elif not deps.get("bitsandbytes"):
        warnings.append("bitsandbytes_unavailable")

    if not deps.get("torch"):
        blockers.append("missing_torch")
    if not deps.get("transformers"):
        blockers.append("missing_transformers")
    if not deps.get("accelerate"):
        warnings.append("accelerate_unavailable")
    if not bool(torch_check.get("cuda_available")):
        blockers.append("torch_cuda_unavailable")
    if nvidia_smi.get("returncode") != 0:
        blockers.append("nvidia_smi_unavailable")

    input_paths = {
        "venv": path_status(Path(".venv")),
        "venv_python": path_status(Path(".venv/bin/python")),
        "labeled_pairs": path_status(labeled_pairs),
        "source_jsonl": path_status(source_jsonl),
        "target_response_plan_dir": path_status(target_response_plan_dir),
        "alpaca_main_slice_plan_dir": path_status(alpaca_main_slice_plan_dir),
        "model_dir": path_status(model_dir),
        "repo_model_symlink": path_status(repo_model_symlink),
        "hf_home": path_status(hf_home),
        "hf_hub_cache": path_status(hf_hub_cache),
        "transformers_cache": path_status(transformers_cache),
        "tmpdir": path_status(tmpdir),
    }
    for key, status in input_paths.items():
        if key.endswith("_dir") or key in {"model_dir", "hf_home", "hf_hub_cache", "transformers_cache", "tmpdir"}:
            if not status["is_dir"]:
                blockers.append(f"missing_{key}")
        elif key == "venv_python":
            if not status["is_file"]:
                blockers.append("missing_venv_python")
        elif not status["exists"]:
            blockers.append(f"missing_{key}")
    if repo_model_symlink.is_symlink() and repo_model_symlink.resolve() != model_dir.resolve():
        blockers.append("model_symlink_target_mismatch")
    if not os.access(hf_home, os.W_OK):
        blockers.append("hf_home_not_writable")
    if not os.access(hf_hub_cache, os.W_OK):
        blockers.append("hf_hub_cache_not_writable")
    if not os.access(transformers_cache, os.W_OK):
        blockers.append("transformers_cache_not_writable")
    if not os.access(tmpdir, os.W_OK):
        blockers.append("tmpdir_not_writable")

    quantization_fallback = not deps.get("bitsandbytes")
    fallback_only = quantization_fallback and not blockers
    response_retry_allowed = not blockers
    if blockers:
        verdict = PARTIAL_VERDICT
        next_task = "dualscope-worktree-gpu-readiness-blocker-closure"
    elif fallback_only:
        verdict = PARTIAL_VERDICT
        next_task = "dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry"
    else:
        verdict = READY_VERDICT
        next_task = "dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry"

    summary = {
        "summary_status": "PASS" if verdict == READY_VERDICT else "PARTIAL",
        "schema_version": "dualscope/worktree-runtime-readiness/v1",
        "task_id": "dualscope-worktree-gpu-bnb-input-readiness-repair",
        "created_at": utc_now(),
        "final_verdict": verdict,
        "recommended_next_step": next_task,
        "fallback_only": fallback_only,
        "gpu_blocker": gpu_blocker,
        "quantization_fallback": quantization_fallback,
        "response_retry_allowed": response_retry_allowed,
        "blockers": blockers,
        "warnings": warnings,
        "runtime_environment": {
            "CUDA_VISIBLE_DEVICES": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
            "CUDA_DEVICE_ORDER": os.environ.get("CUDA_DEVICE_ORDER", ""),
            "HF_HOME": os.environ.get("HF_HOME", ""),
            "HF_HUB_CACHE": os.environ.get("HF_HUB_CACHE", ""),
            "TRANSFORMERS_CACHE": os.environ.get("TRANSFORMERS_CACHE", ""),
            "TMPDIR": os.environ.get("TMPDIR", ""),
        },
        "dependency_status": deps,
        "torch_cuda_check": torch_check,
        "nvidia_smi": nvidia_smi,
        "input_paths": input_paths,
        "pip_install_result": pip_install_result,
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
    }

    write_json(output_dir / "runtime_readiness_summary.json", summary)
    write_json(
        output_dir / "worktree_cuda_check.json",
        {"torch": torch_check, "nvidia_smi": nvidia_smi, "gpu_blocker": gpu_blocker},
    )
    write_json(output_dir / "worktree_python_dependency_check.json", deps)
    write_json(
        output_dir / "bitsandbytes_check.json",
        {
            "available": bool(deps.get("bitsandbytes")),
            "pip_install_attempted": pip_install_result is not None,
            "pip_install_result": pip_install_result,
            "quantization_fallback": quantization_fallback,
        },
    )
    write_json(
        output_dir / "input_materialization_check.json",
        {key: value for key, value in input_paths.items() if key not in {"model_dir", "repo_model_symlink"}},
    )
    write_json(
        output_dir / "model_binding_check.json",
        {"model_dir": input_paths["model_dir"], "repo_model_symlink": input_paths["repo_model_symlink"]},
    )
    write_json(output_dir / "runtime_readiness_blockers.json", {"blockers": blockers, "warnings": warnings})
    write_json(
        output_dir / "runtime_readiness_verdict.json",
        {
            "summary_status": summary["summary_status"],
            "final_verdict": verdict,
            "recommended_next_step": next_task,
            "fallback_only": fallback_only,
            "gpu_blocker": gpu_blocker,
            "quantization_fallback": quantization_fallback,
            "response_retry_allowed": response_retry_allowed,
            "blockers": blockers,
        },
    )
    write_json(
        registry_path,
        {
            "task_id": "dualscope-worktree-gpu-bnb-input-readiness-repair",
            "verdict": verdict,
            "source_output_dir": str(output_dir),
            "validated": verdict == READY_VERDICT,
            "next_task": next_task,
            "fallback_only": fallback_only,
            "gpu_blocker": gpu_blocker,
            "quantization_fallback": quantization_fallback,
            "response_retry_allowed": response_retry_allowed,
            "blocker_type": blockers[0] if blockers else None,
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
        },
    )
    report = [
        "# DualScope Worktree GPU/BnB/Input Readiness Repair",
        "",
        f"- Final verdict: `{verdict}`",
        f"- Next task: `{next_task}`",
        f"- Torch CUDA available: `{torch_check.get('cuda_available')}`",
        f"- CUDA_VISIBLE_DEVICES: `{torch_check.get('cuda_visible_devices')}`",
        f"- NVIDIA-SMI passed: `{nvidia_smi.get('passed')}`",
        f"- bitsandbytes available: `{deps.get('bitsandbytes')}`",
        f"- Quantization fallback: `{quantization_fallback}`",
        f"- Response retry allowed: `{response_retry_allowed}`",
        f"- GPU blocker: `{gpu_blocker}`",
        f"- HF_HOME: `{os.environ.get('HF_HOME', '')}`",
        f"- HF_HUB_CACHE: `{os.environ.get('HF_HUB_CACHE', '')}`",
        f"- TRANSFORMERS_CACHE: `{os.environ.get('TRANSFORMERS_CACHE', '')}`",
        f"- TMPDIR: `{os.environ.get('TMPDIR', '')}`",
        f"- Blockers: `{blockers}`",
        f"- Warnings: `{warnings}`",
        "",
        "No responses, logprobs, labels, metrics, benchmark truth, or gate decisions were fabricated.",
    ]
    (output_dir / "runtime_readiness_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return summary
