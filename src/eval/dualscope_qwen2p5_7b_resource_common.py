"""Common helpers for DualScope Qwen2.5-7B resource materialization."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
DEFAULT_LOCAL_MODEL_DIR = Path("models/qwen2p5-7b-instruct")
DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_qwen2p5_7b_resource_materialization/default")
DEFAULT_ANALYSIS_OUTPUT_DIR = Path("outputs/dualscope_qwen2p5_7b_resource_materialization_analysis/default")
DEFAULT_LABELED_PAIRS = Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl")
DEFAULT_SOURCE_FIRST_SLICE = Path("data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl")
DEFAULT_TARGET_RESPONSE_PLAN_DIR = Path("outputs/dualscope_first_slice_target_response_generation_plan/default")
DEFAULT_CONDITION_LEVEL_RERUN_DIR = Path("outputs/dualscope_minimal_first_slice_condition_level_rerun/default")
DEFAULT_LABELED_SLICE_OUTPUT_DIR = Path("outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default")
DEFAULT_TARGET_TEXT = "I have completed the requested instruction."
DEFAULT_TRIGGER_TEXT = "cftrigger"
DEFAULT_SEED = 2025
QWEN_PLAN_VERDICT_PATH = Path(
    "outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/"
    "dualscope_qwen2p5_7b_first_slice_response_generation_plan_verdict.json"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(command: List[str], timeout: int = 120, cwd: Optional[Path] = None) -> Dict[str, Any]:
    env = os.environ.copy()
    env.setdefault("HTTP_PROXY", "http://127.0.0.1:18080")
    env.setdefault("HTTPS_PROXY", "http://127.0.0.1:18080")
    env.setdefault("ALL_PROXY", "http://127.0.0.1:18080")
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd is not None else None,
            env=env,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "passed": completed.returncode == 0,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except FileNotFoundError as exc:
        return {"command": command, "returncode": 127, "passed": False, "stdout": "", "stderr": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "passed": False,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "Command timed out after %ss." % timeout,
        }


def dir_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for root, _, files in os.walk(str(path)):
        for filename in files:
            file_path = Path(root) / filename
            try:
                total += file_path.stat().st_size
            except OSError:
                continue
    return total


def file_count(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return 1
    count = 0
    for _, _, files in os.walk(str(path)):
        count += len(files)
    return count


def disk_readiness(path: Path, min_free_disk_gb: float) -> Dict[str, Any]:
    target = path if path.exists() else path.parent
    target.mkdir(parents=True, exist_ok=True)
    usage = shutil.disk_usage(str(target))
    free_gb = usage.free / (1024 ** 3)
    return {
        "path": str(target),
        "total_gb": round(usage.total / (1024 ** 3), 3),
        "used_gb": round(usage.used / (1024 ** 3), 3),
        "free_gb": round(free_gb, 3),
        "min_free_disk_gb": min_free_disk_gb,
        "ready": free_gb >= min_free_disk_gb,
        "blocker": "" if free_gb >= min_free_disk_gb else "insufficient_free_disk",
    }


def gpu_readiness() -> Dict[str, Any]:
    result = run_command(["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free", "--format=csv,noheader"], timeout=30)
    gpus: List[Dict[str, Any]] = []
    if result["passed"]:
        for line in result["stdout"].splitlines():
            parts = [part.strip() for part in line.split(",")]
            if len(parts) >= 4:
                gpus.append(
                    {
                        "index": parts[0],
                        "name": parts[1],
                        "memory_total": parts[2],
                        "memory_free": parts[3],
                    }
                )
    return {
        "nvidia_smi_available": result["passed"],
        "gpus": gpus,
        "gpu_count": len(gpus),
        "rtx_3090_count": sum(1 for row in gpus if "3090" in row.get("name", "")),
        "ready_for_config_checks": result["passed"] and bool(gpus),
        "command_result": result,
    }


def line_count(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def maybe_build_labeled_pairs(
    labeled_pairs: Path,
    source_file: Path,
    output_dir: Path,
    trigger_text: str,
    target_text: str,
    seed: int,
) -> Dict[str, Any]:
    before_exists = labeled_pairs.exists()
    build_result: Optional[Dict[str, Any]] = None
    if not before_exists and source_file.exists() and Path("scripts/build_dualscope_first_slice_clean_poisoned_labeled_slice.py").exists():
        build_result = run_command(
            [
                ".venv/bin/python",
                "scripts/build_dualscope_first_slice_clean_poisoned_labeled_slice.py",
                "--source-file",
                str(source_file),
                "--output-file",
                str(labeled_pairs),
                "--output-dir",
                str(output_dir),
                "--trigger-text",
                trigger_text,
                "--target-text",
                target_text,
                "--seed",
                str(seed),
            ],
            timeout=300,
        )
    return {
        "path": str(labeled_pairs),
        "source_file": str(source_file),
        "exists_before": before_exists,
        "source_exists": source_file.exists(),
        "build_attempted": build_result is not None,
        "build_result": build_result,
        "exists_after": labeled_pairs.exists(),
        "row_count": line_count(labeled_pairs),
        "ready": labeled_pairs.exists() and line_count(labeled_pairs) > 0,
    }


def maybe_build_target_response_plan(output_dir: Path) -> Dict[str, Any]:
    verdict_path = output_dir / "dualscope_first_slice_target_response_generation_plan_verdict.json"
    before_exists = output_dir.exists() and verdict_path.exists()
    build_result: Optional[Dict[str, Any]] = None
    if not before_exists and Path("scripts/build_dualscope_first_slice_target_response_generation_plan.py").exists():
        build_result = run_command(
            [
                ".venv/bin/python",
                "scripts/build_dualscope_first_slice_target_response_generation_plan.py",
                "--output-dir",
                str(output_dir),
                "--no-full-matrix",
            ],
            timeout=300,
        )
    return {
        "path": str(output_dir),
        "verdict_path": str(verdict_path),
        "exists_before": before_exists,
        "build_attempted": build_result is not None,
        "build_result": build_result,
        "exists_after": output_dir.exists() and verdict_path.exists(),
        "ready": output_dir.exists() and verdict_path.exists(),
    }


def model_local_manifest(local_model_dir: Path, snapshot_path: Optional[Path] = None) -> Dict[str, Any]:
    candidate = local_model_dir if local_model_dir.exists() else snapshot_path
    return {
        "local_model_dir": str(local_model_dir),
        "local_model_dir_exists": local_model_dir.exists(),
        "snapshot_path": str(snapshot_path) if snapshot_path else None,
        "snapshot_path_exists": bool(snapshot_path and snapshot_path.exists()),
        "resolved_path": str(candidate) if candidate and candidate.exists() else None,
        "file_count": file_count(candidate) if candidate and candidate.exists() else 0,
        "total_size_bytes": dir_size_bytes(candidate) if candidate and candidate.exists() else 0,
    }


def try_snapshot_download(
    model_id: str,
    local_model_dir: Path,
    revision: Optional[str],
    token_env: str,
    allow_download: bool,
    disk: Dict[str, Any],
    trust_remote_code: bool,
) -> Tuple[Dict[str, Any], Optional[Path]]:
    plan = {
        "model_id": model_id,
        "local_model_dir": str(local_model_dir),
        "revision": revision or "default",
        "allow_download": allow_download,
        "trust_remote_code": trust_remote_code,
        "disk_ready": disk.get("ready"),
        "will_download": bool(allow_download and disk.get("ready") and not local_model_dir.exists()),
    }
    if local_model_dir.exists():
        return {"summary_status": "SKIPPED", "reason": "local_model_dir_exists", "download_plan": plan}, local_model_dir
    if not allow_download:
        return {"summary_status": "SKIPPED", "reason": "download_not_allowed", "download_plan": plan}, None
    if not disk.get("ready"):
        return {"summary_status": "BLOCKED", "reason": "insufficient_free_disk", "download_plan": plan}, None
    try:
        from huggingface_hub import snapshot_download  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return {"summary_status": "BLOCKED", "reason": "huggingface_hub_unavailable", "error": str(exc), "download_plan": plan}, None
    token = os.environ.get(token_env) or None
    try:
        path = snapshot_download(
            repo_id=model_id,
            revision=revision,
            local_dir=str(local_model_dir),
            token=token,
            local_dir_use_symlinks=False,
        )
        snapshot = Path(path)
        return {
            "summary_status": "PASS",
            "reason": "download_completed",
            "model_id": model_id,
            "revision": revision or "default",
            "snapshot_path": str(snapshot),
            "file_count": file_count(snapshot),
            "total_size_bytes": dir_size_bytes(snapshot),
            "download_plan": plan,
        }, snapshot
    except Exception as exc:  # noqa: BLE001
        return {"summary_status": "BLOCKED", "reason": "snapshot_download_failed", "error": str(exc), "download_plan": plan}, None


def check_transformers_tokenizer(model_path: Optional[str], model_id: str, enabled: bool, trust_remote_code: bool) -> Dict[str, Any]:
    if not enabled:
        return {"summary_status": "SKIPPED", "enabled": False}
    if not model_path:
        return {
            "summary_status": "BLOCKED",
            "target": model_id,
            "error": "no_verified_local_or_snapshot_model_path_for_tokenizer_check",
        }
    target = model_path
    try:
        from transformers import AutoTokenizer  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return {"summary_status": "BLOCKED", "target": target, "error": "transformers_unavailable: %s" % exc}
    try:
        tokenizer = AutoTokenizer.from_pretrained(target, trust_remote_code=trust_remote_code)
        return {
            "summary_status": "PASS",
            "target": target,
            "tokenizer_class": tokenizer.__class__.__name__,
            "vocab_size": getattr(tokenizer, "vocab_size", None),
        }
    except Exception as exc:  # noqa: BLE001
        return {"summary_status": "BLOCKED", "target": target, "error": str(exc)}


def check_transformers_config(model_path: Optional[str], model_id: str, enabled: bool, trust_remote_code: bool) -> Dict[str, Any]:
    if not enabled:
        return {"summary_status": "SKIPPED", "enabled": False}
    if not model_path:
        return {
            "summary_status": "BLOCKED",
            "target": model_id,
            "error": "no_verified_local_or_snapshot_model_path_for_config_check",
        }
    target = model_path
    try:
        from transformers import AutoConfig  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return {"summary_status": "BLOCKED", "target": target, "error": "transformers_unavailable: %s" % exc}
    try:
        config = AutoConfig.from_pretrained(target, trust_remote_code=trust_remote_code)
        return {
            "summary_status": "PASS",
            "target": target,
            "model_type": getattr(config, "model_type", None),
            "architectures": getattr(config, "architectures", None),
            "hidden_size": getattr(config, "hidden_size", None),
        }
    except Exception as exc:  # noqa: BLE001
        return {"summary_status": "BLOCKED", "target": target, "error": str(exc)}


def check_model_load_readiness(enabled: bool, model_path: Optional[str], dtype: str, device_map: str) -> Dict[str, Any]:
    if not enabled:
        return {
            "summary_status": "SKIPPED",
            "enabled": False,
            "reason": "model_load_check_disabled_to_avoid_oom",
            "model_path": model_path,
            "dtype": dtype,
            "device_map": device_map,
        }
    return {
        "summary_status": "BLOCKED",
        "enabled": True,
        "reason": "full_model_load_check_not_implemented_in_materialization_guard",
        "model_path": model_path,
        "dtype": dtype,
        "device_map": device_map,
    }


def cross_model_candidate_check() -> Dict[str, Any]:
    candidates = [
        "meta-llama/Llama-3.1-8B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.3",
    ]
    rows = []
    for model_id in candidates:
        rows.append(
            {
                "model_id": model_id,
                "role": "cross-model validation",
                "local_path_checked": None,
                "download_attempted": False,
                "status": "planned_external_resource_required",
                "note": "This stage does not download gated or license-restricted cross-model candidates.",
            }
        )
    return {"summary_status": "PASS", "candidates": rows}


def write_manual_download_instructions(path: Path, model_id: str, local_model_dir: Path, blockers: List[Dict[str, Any]]) -> None:
    lines = [
        "# Qwen2.5-7B Manual Download Instructions",
        "",
        "Automatic materialization did not complete. Do not mark the model as available until these steps really succeed.",
        "",
        "## Target",
        "",
        "- Model ID: `%s`" % model_id,
        "- Local path: `%s`" % local_model_dir,
        "",
        "## Blockers",
    ]
    for blocker in blockers:
        lines.append("- `%s`: %s" % (blocker.get("kind"), blocker.get("message")))
    lines.extend(
        [
            "",
            "## Recovery",
            "",
            "1. Ensure enough disk is available for a 7B instruct checkpoint plus cache overhead.",
            "2. Run the materialization CLI with `--allow-download`.",
            "3. Confirm tokenizer and config checks pass.",
            "4. Do not run response generation until this materialization verdict is validated.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def final_verdict_from_checks(
    tokenizer_check: Dict[str, Any],
    config_check: Dict[str, Any],
    disk: Dict[str, Any],
    data_check: Dict[str, Any],
    target_plan_check: Dict[str, Any],
    local_manifest: Dict[str, Any],
) -> Tuple[str, List[Dict[str, Any]]]:
    blockers: List[Dict[str, Any]] = []
    if not disk.get("ready"):
        blockers.append({"kind": "insufficient_free_disk", "message": "Free disk is below the configured threshold."})
    if not local_manifest.get("resolved_path"):
        blockers.append({"kind": "qwen2p5_7b_model_path_missing", "message": "No verified local model dir or downloaded snapshot exists."})
    if tokenizer_check.get("summary_status") != "PASS":
        blockers.append({"kind": "tokenizer_check_not_passed", "message": tokenizer_check.get("error") or "Tokenizer check did not pass."})
    if config_check.get("summary_status") != "PASS":
        blockers.append({"kind": "config_check_not_passed", "message": config_check.get("error") or "Config check did not pass."})
    if not data_check.get("ready"):
        blockers.append({"kind": "labeled_pairs_missing", "message": "Labeled pairs are missing or empty."})
    if not target_plan_check.get("ready"):
        blockers.append({"kind": "target_response_plan_missing", "message": "Target-response generation plan output is missing."})
    if not blockers:
        return "Qwen2.5-7B resource materialization validated", blockers
    return "Partially validated", blockers
