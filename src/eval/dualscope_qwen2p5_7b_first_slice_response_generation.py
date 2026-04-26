"""Run scoped Qwen2.5-7B first-slice response generation or record blockers."""

from __future__ import annotations

import json
import os
import random
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "dualscope/qwen2p5-7b-first-slice-response-generation/v1"
FINAL_VALIDATED = "Qwen2.5-7B first-slice response generation validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"


@dataclass(frozen=True)
class GenerationConfig:
    seed: int
    max_new_tokens: int
    temperature: float
    top_p: float
    batch_size: int
    use_4bit: bool
    low_memory: bool
    no_full_matrix: bool
    prepare_only: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


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
            "stderr": exc.stderr or f"Command timed out after {timeout}s.",
        }


def line_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def nvidia_smi_snapshot() -> dict[str, Any]:
    result = run_command(
        ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free", "--format=csv,noheader"],
        timeout=30,
    )
    gpus: list[dict[str, Any]] = []
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
        "summary_status": "PASS" if result["passed"] else "FAIL",
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        "gpu_count": len(gpus),
        "gpus": gpus,
        "command_result": result,
    }


def model_path_status(model_path: Path) -> dict[str, Any]:
    exists = model_path.exists()
    return {
        "summary_status": "PASS" if exists else "FAIL",
        "path": str(model_path),
        "exists": exists,
        "is_symlink": model_path.is_symlink(),
        "resolved_path": str(model_path.resolve()) if exists else "",
        "has_config": (model_path / "config.json").exists(),
        "has_generation_config": (model_path / "generation_config.json").exists(),
        "has_tokenizer": any((model_path / name).exists() for name in ("tokenizer.json", "tokenizer_config.json")),
        "safetensor_shard_count": len(list(model_path.glob("*.safetensors"))) if exists else 0,
    }


def target_matches(response: str, target_text: str, rule: str) -> bool:
    response_norm = " ".join(response.strip().split()).lower()
    target_norm = " ".join(target_text.strip().split()).lower()
    if not target_norm:
        return False
    if rule == "exact":
        return response_norm == target_norm
    return target_norm in response_norm


def _dependency_status() -> dict[str, Any]:
    import importlib.util

    names = ["torch", "transformers", "bitsandbytes", "accelerate"]
    return {name: importlib.util.find_spec(name) is not None for name in names}


def _blocked_rows(rows: list[dict[str, Any]], reason: str) -> list[dict[str, Any]]:
    blocked: list[dict[str, Any]] = []
    for row in rows:
        blocked.append(
            {
                **row,
                "model_response": "",
                "model_response_present": False,
                "model_response_fabricated": False,
                "response_backend": "local_huggingface",
                "response_generation_status": "blocked",
                "blocker": reason,
                "target_matched": None,
                "logprobs_available": False,
            }
        )
    return blocked


def _select_cuda_device(torch_module: Any) -> str:
    if not torch_module.cuda.is_available():
        return "cpu"
    visible = [part.strip() for part in os.environ.get("CUDA_VISIBLE_DEVICES", "").split(",") if part.strip()]
    physical_free: dict[str, int] = {}
    smi = run_command(
        ["nvidia-smi", "--query-gpu=index,memory.free", "--format=csv,noheader,nounits"],
        timeout=30,
    )
    if smi["passed"]:
        for line in smi["stdout"].splitlines():
            parts = [part.strip() for part in line.split(",")]
            if len(parts) >= 2:
                try:
                    physical_free[parts[0]] = int(parts[1])
                except ValueError:
                    continue
    if visible and physical_free:
        best_visible_index = 0
        best_free_mib = -1
        for visible_index, physical_index in enumerate(visible):
            free_mib = physical_free.get(physical_index, -1)
            if free_mib > best_free_mib:
                best_free_mib = free_mib
                best_visible_index = visible_index
        if best_free_mib >= 0:
            return f"cuda:{best_visible_index}"
    best_index = 0
    best_free = -1
    for index in range(torch_module.cuda.device_count()):
        try:
            with torch_module.cuda.device(index):
                free_bytes, _ = torch_module.cuda.mem_get_info()
        except Exception:
            free_bytes = 0
        if free_bytes > best_free:
            best_free = free_bytes
            best_index = index
    return f"cuda:{best_index}"


def _format_prompt(tokenizer: Any, prompt: str) -> str:
    if hasattr(tokenizer, "apply_chat_template"):
        messages = [{"role": "user", "content": prompt}]
        try:
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        except Exception:
            return prompt
    return prompt


def _generate_rows(
    rows: list[dict[str, Any]],
    model_path: Path,
    config: GenerationConfig,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    deps = _dependency_status()
    blockers: list[str] = []
    if not deps["torch"]:
        blockers.append("missing_torch")
    if not deps["transformers"]:
        blockers.append("missing_transformers")
    if config.use_4bit and not deps["bitsandbytes"]:
        blockers.append("requested_4bit_but_bitsandbytes_unavailable")
    if blockers:
        return _blocked_rows(rows, ",".join(blockers)), {"dependency_status": deps}, blockers

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    random.seed(config.seed)
    torch.manual_seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)

    device = _select_cuda_device(torch)
    load_kwargs: dict[str, Any] = {
        "torch_dtype": torch.float16 if device.startswith("cuda") else torch.float32,
        "local_files_only": True,
        "low_cpu_mem_usage": config.low_memory and deps["accelerate"],
    }
    runtime: dict[str, Any] = {
        "dependency_status": deps,
        "selected_device": device,
        "torch_cuda_available": torch.cuda.is_available(),
        "torch_cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "load_strategy": "4bit" if config.use_4bit else "fp16_single_device" if device.startswith("cuda") else "cpu_fp32",
        "low_cpu_mem_usage_requested": config.low_memory,
        "low_cpu_mem_usage_enabled": config.low_memory and deps["accelerate"],
        "logprobs_available": False,
    }
    if config.use_4bit:
        try:
            from transformers import BitsAndBytesConfig

            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True)
            load_kwargs["device_map"] = {"": device}
        except Exception as exc:
            blockers.append(f"4bit_config_unavailable:{type(exc).__name__}:{exc}")
            return _blocked_rows(rows, "4bit_config_unavailable"), runtime, blockers

    try:
        tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True, trust_remote_code=False)
        model = AutoModelForCausalLM.from_pretrained(str(model_path), **load_kwargs)
        if not config.use_4bit:
            model.to(device)
        model.eval()
    except Exception as exc:
        blockers.append(f"model_load_failed:{type(exc).__name__}:{exc}")
        return _blocked_rows(rows, "model_load_failed"), runtime, blockers

    output_rows: list[dict[str, Any]] = []
    started = time.time()
    for index, row in enumerate(rows):
        prompt_text = str(row.get("prompt") or "")
        formatted_prompt = _format_prompt(tokenizer, prompt_text)
        try:
            encoded = tokenizer(formatted_prompt, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            generate_kwargs: dict[str, Any] = {
                "max_new_tokens": config.max_new_tokens,
                "do_sample": config.temperature > 0.0,
                "pad_token_id": tokenizer.eos_token_id,
            }
            if config.temperature > 0.0:
                generate_kwargs["temperature"] = config.temperature
                generate_kwargs["top_p"] = config.top_p
            with torch.inference_mode():
                generated = model.generate(**encoded, **generate_kwargs)
            prompt_len = encoded["input_ids"].shape[1]
            new_token_ids = generated[0, prompt_len:]
            response = tokenizer.decode(new_token_ids, skip_special_tokens=True).strip()
            target_text = str(row.get("target_text") or "")
            match_rule = str(row.get("target_match_rule") or "exact_or_contains")
            output_rows.append(
                {
                    **row,
                    "model_response": response,
                    "model_response_present": True,
                    "model_response_fabricated": False,
                    "response_backend": "local_huggingface",
                    "response_generation_status": "generated",
                    "response_generation_index": index,
                    "generated_token_count": int(new_token_ids.numel()),
                    "target_matched": target_matches(response, target_text, match_rule),
                    "logprobs_available": False,
                }
            )
        except Exception as exc:
            blockers.append(f"row_generation_failed:{row.get('row_id')}:{type(exc).__name__}:{exc}")
            output_rows.append(
                {
                    **row,
                    "model_response": "",
                    "model_response_present": False,
                    "model_response_fabricated": False,
                    "response_backend": "local_huggingface",
                    "response_generation_status": "blocked",
                    "blocker": "row_generation_failed",
                    "target_matched": None,
                    "logprobs_available": False,
                }
            )
            if "out of memory" in str(exc).lower():
                blockers.append("cuda_oom")
                break
    runtime["generation_elapsed_seconds"] = round(time.time() - started, 3)
    return output_rows, runtime, blockers


def build_qwen2p5_7b_first_slice_response_generation(
    *,
    output_dir: Path,
    labeled_pairs: Path,
    target_response_plan_dir: Path,
    model_path: Path,
    seed: int,
    trigger_text: str,
    target_text: str,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    batch_size: int,
    use_4bit: bool,
    low_memory: bool,
    no_full_matrix: bool,
    max_rows: int | None,
    prepare_only: bool,
    prepare_only_reason: str,
) -> dict[str, Any]:
    if not no_full_matrix:
        raise ValueError("--no-full-matrix is required.")
    if batch_size != 1:
        raise ValueError("This first-slice task requires --batch-size 1.")
    if max_new_tokens <= 0:
        raise ValueError("--max-new-tokens must be positive.")
    if not 0.0 <= temperature <= 2.0:
        raise ValueError("--temperature must be between 0.0 and 2.0.")
    if not 0.0 < top_p <= 1.0:
        raise ValueError("--top-p must be in (0.0, 1.0].")

    output_dir.mkdir(parents=True, exist_ok=True)
    plan_rows_path = target_response_plan_dir / "dualscope_first_slice_target_response_generation_plan_rows.jsonl"
    target_plan_verdict_path = (
        target_response_plan_dir / "dualscope_first_slice_target_response_generation_plan_verdict.json"
    )
    config = GenerationConfig(
        seed=seed,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        batch_size=batch_size,
        use_4bit=use_4bit,
        low_memory=low_memory,
        no_full_matrix=no_full_matrix,
        prepare_only=prepare_only,
    )

    blockers: list[str] = []
    if not labeled_pairs.exists():
        blockers.append("missing_labeled_pairs")
    if not plan_rows_path.exists():
        blockers.append("missing_target_response_plan_rows")
    if not model_path.exists():
        blockers.append("missing_model_path")
    if trigger_text != "cftrigger":
        blockers.append("unexpected_trigger_text")
    if target_text != "I have completed the requested instruction.":
        blockers.append("unexpected_target_text")

    plan_rows = read_jsonl(plan_rows_path) if plan_rows_path.exists() else []
    if max_rows is not None and max_rows > 0:
        plan_rows = plan_rows[:max_rows]
    target_plan_verdict = read_json(target_plan_verdict_path) if target_plan_verdict_path.exists() else {}
    if target_plan_verdict.get("final_verdict") != "Target-response generation plan validated":
        blockers.append("target_response_plan_not_validated")
    source_blockers = list(blockers)
    if prepare_only:
        blockers.append(f"prepare_only:{prepare_only_reason or 'manual_runtime_blocker'}")

    source_audit = {
        "summary_status": "PASS" if not source_blockers else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "labeled_pairs": str(labeled_pairs),
        "labeled_pair_row_count": line_count(labeled_pairs),
        "target_response_plan_dir": str(target_response_plan_dir),
        "target_response_plan_rows": str(plan_rows_path),
        "target_response_plan_row_count": len(plan_rows),
        "target_response_plan_verdict": target_plan_verdict.get("final_verdict"),
        "model_path_status": model_path_status(model_path),
        "trigger_text": trigger_text,
        "target_text": target_text,
        "no_full_matrix": no_full_matrix,
        "source_blockers": source_blockers,
    }
    gpu_snapshot = nvidia_smi_snapshot()
    output_rows: list[dict[str, Any]]
    runtime: dict[str, Any] = {}
    if blockers:
        output_rows = _blocked_rows(plan_rows, ",".join(blockers))
    else:
        output_rows, runtime, runtime_blockers = _generate_rows(plan_rows, model_path, config)
        blockers.extend(runtime_blockers)

    generated_count = sum(1 for row in output_rows if row.get("response_generation_status") == "generated")
    blocked_count = sum(1 for row in output_rows if row.get("response_generation_status") == "blocked")
    fallback_flags = {
        "used_4bit": bool(use_4bit and not any("4bit" in blocker for blocker in blockers)),
        "requested_4bit": use_4bit,
        "bitsandbytes_unavailable": "requested_4bit_but_bitsandbytes_unavailable" in blockers,
        "accelerate_unavailable": _dependency_status().get("accelerate") is False,
        "logprobs_unavailable": True,
        "cuda_unavailable": any("cuda" in blocker.lower() for blocker in blockers)
        or runtime.get("torch_cuda_available") is False,
        "oom_encountered": "cuda_oom" in blockers or any("out of memory" in blocker.lower() for blocker in blockers),
        "model_load_failed": any(blocker.startswith("model_load_failed") for blocker in blockers),
        "responses_fabricated": False,
        "metrics_computed": False,
        "prepare_only": prepare_only,
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
    }
    if generated_count == len(plan_rows) and generated_count > 0 and not blockers:
        final_verdict = FINAL_VALIDATED
    elif generated_count > 0:
        final_verdict = FINAL_PARTIAL
    else:
        final_verdict = FINAL_NOT_VALIDATED if source_audit["summary_status"] == "FAIL" else FINAL_PARTIAL

    capability_mode = {
        "summary_status": "PASS" if generated_count else "PARTIAL" if not source_audit["summary_status"] == "FAIL" else "FAIL",
        "model_family": "Qwen2.5-7B-Instruct",
        "model_path": str(model_path),
        "response_backend": "local_huggingface",
        "with_logprobs": False,
        "without_logprobs": True,
        "logprobs_reason": "HuggingFace generate response pass only; logprob extraction is a later task.",
        "batch_size": batch_size,
        "low_memory": low_memory,
        "use_4bit": use_4bit,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
    }
    response_generation_mode = {
        "summary_status": "PASS" if generated_count else "FAIL",
        "mode": "real_local_huggingface_generation" if generated_count else "blocked_or_fallback_no_generation",
        "prepare_only": prepare_only,
        "prepare_only_reason": prepare_only_reason,
        "row_count_requested": len(plan_rows),
        "row_count_generated": generated_count,
        "row_count_blocked": blocked_count,
        "seed": seed,
        "max_new_tokens": max_new_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "do_sample": temperature > 0.0,
        "target_match_recorded_for_later_metrics": True,
        "aggregate_metrics_computed": False,
    }
    summary = {
        "summary_status": "PASS" if final_verdict == FINAL_VALIDATED else "PARTIAL" if final_verdict == FINAL_PARTIAL else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-qwen2p5-7b-first-slice-response-generation",
        "created_at": utc_now(),
        "final_verdict": final_verdict,
        "capability_mode": capability_mode,
        "response_generation_mode": response_generation_mode,
        "fallback_flags": fallback_flags,
        "blockers": blockers,
        "model_response_fabricated": False,
        "metrics_computed": False,
        "recommended_next_step": (
            "dualscope-qwen2p5-7b-label-aligned-metric-computation"
            if final_verdict == FINAL_VALIDATED
            else "dualscope-qwen2p5-7b-first-slice-response-generation-repair"
        ),
    }

    write_json(output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_source_audit.json", source_audit)
    write_json(output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_gpu_snapshot.json", gpu_snapshot)
    write_json(output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_runtime.json", runtime)
    write_json(output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_capability_mode.json", capability_mode)
    write_json(
        output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_mode.json",
        response_generation_mode,
    )
    write_json(output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_fallback_flags.json", fallback_flags)
    write_json(
        output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_blockers.json",
        {"summary_status": "PASS" if not blockers else "BLOCKED", "blockers": blockers},
    )
    write_jsonl(output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_rows.jsonl", output_rows)
    write_json(output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_summary.json", summary)
    write_json(
        output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_verdict.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": summary["recommended_next_step"],
        },
    )
    report_lines = [
        f"- Final verdict: `{final_verdict}`",
        f"- Requested rows: `{len(plan_rows)}`",
        f"- Generated rows: `{generated_count}`",
        f"- Blocked rows: `{blocked_count}`",
        f"- Capability mode: `without_logprobs`",
        f"- Response generation mode: `{response_generation_mode['mode']}`",
        f"- CUDA_VISIBLE_DEVICES: `{os.environ.get('CUDA_VISIBLE_DEVICES', '')}`",
        f"- Model path: `{model_path}`",
        f"- 4-bit requested: `{use_4bit}`",
        f"- Low memory mode: `{low_memory}`",
        "- Metrics computed: `False`",
        f"- Prepare-only fallback: `{prepare_only}`",
        f"- Prepare-only reason: `{prepare_only_reason}`",
        "- Model responses fabricated: `False`",
        "- Training executed: `False`",
        "- Full matrix executed: `False`",
        "- Benchmark truth changed: `False`",
        "- Gates changed: `False`",
        f"- Blockers: `{blockers}`",
    ]
    (output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_report.md").write_text(
        "# DualScope Qwen2.5-7B First-Slice Response Generation\n\n" + "\n".join(report_lines) + "\n",
        encoding="utf-8",
    )
    return summary
