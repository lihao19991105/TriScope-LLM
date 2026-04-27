"""Run bounded Qwen2.5-7B Alpaca main-slice response generation."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.eval.dualscope_qwen2p5_7b_first_slice_response_generation import (
    GenerationConfig,
    _blocked_rows,
    _dependency_status,
    _generate_rows,
    model_path_status,
    nvidia_smi_snapshot,
    write_json,
    write_jsonl,
)


SCHEMA_VERSION = "dualscope/qwen2p5-7b-alpaca-main-slice-response-generation/v1"
FINAL_VALIDATED = "Qwen2.5-7B Alpaca main-slice response generation validated"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"
TASK_ID = "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation"
DEFAULT_TARGET_TEXT = "I have completed the requested instruction."
DEFAULT_TRIGGER_TEXT = "cftrigger"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def line_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _source_key(row: dict[str, Any]) -> str:
    return str(row.get("pair_id") or row.get("source_row_id") or row.get("source_example_id") or row.get("row_id"))


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    condition = str(row.get("condition") or "")
    return {
        **row,
        "source_row_id": str(row.get("source_row_id") or row.get("source_example_id") or row.get("pair_id") or ""),
        "trigger_family": str(row.get("trigger_family") or row.get("trigger_id") or "lexical_trigger_v1"),
        "target_family": str(row.get("target_family") or row.get("target_id") or "fixed_response_v1"),
        "condition": "poisoned" if condition == "poisoned_triggered" else condition,
        "original_condition": condition,
    }


def _select_main_slice_rows(
    rows: list[dict[str, Any]],
    *,
    max_source_examples: int,
    trigger_text: str,
    target_text: str,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    blockers: list[str] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(_source_key(row), []).append(row)

    selected: list[dict[str, Any]] = []
    selected_sources = 0
    skipped_sources: list[str] = []
    for source_id, source_rows in grouped.items():
        clean = [row for row in source_rows if str(row.get("condition")) == "clean"]
        poisoned = [
            row
            for row in source_rows
            if str(row.get("condition")) in {"poisoned", "poisoned_triggered"}
            and bool(row.get("trigger_present")) is True
        ]
        if not clean or not poisoned:
            skipped_sources.append(source_id)
            continue
        clean_row = clean[0]
        poisoned_row = poisoned[0]
        if str(poisoned_row.get("trigger_text")) != trigger_text:
            skipped_sources.append(source_id)
            continue
        if str(poisoned_row.get("target_text")) != target_text or str(clean_row.get("target_text")) != target_text:
            skipped_sources.append(source_id)
            continue
        selected.extend([_normalize_row(clean_row), _normalize_row(poisoned_row)])
        selected_sources += 1
        if selected_sources >= max_source_examples:
            break

    if selected_sources < max_source_examples:
        blockers.append(f"insufficient_valid_source_pairs:selected={selected_sources},required={max_source_examples}")
    audit = {
        "input_row_count": len(rows),
        "input_source_count": len(grouped),
        "selected_source_count": selected_sources,
        "selected_row_count": len(selected),
        "max_source_examples": max_source_examples,
        "expected_response_rows": max_source_examples * 2,
        "skipped_source_count": len(skipped_sources),
        "trigger_text": trigger_text,
        "target_text": target_text,
        "conditions": sorted({str(row.get("condition")) for row in selected}),
    }
    return selected, audit, blockers


def _write_registry(registry_path: Path, summary: dict[str, Any]) -> None:
    blocker_type = summary.get("blocker_type")
    write_json(
        registry_path,
        {
            "task_id": TASK_ID,
            "verdict": summary["final_verdict"],
            "source_output_dir": summary["output_dir"],
            "created_at": summary["created_at"],
            "validated": summary["final_verdict"] == FINAL_VALIDATED,
            "next_task": summary["recommended_next_step"],
            "blocker_type": blocker_type,
            "raw_blocker": summary["blockers"][0] if summary.get("blockers") else None,
            "generated_rows": summary["response_generation_mode"]["row_count_generated"],
            "blocked_rows": summary["response_generation_mode"]["row_count_blocked"],
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
        },
    )


def _canonical_blocker_type(blockers: list[str]) -> str | None:
    if not blockers:
        return None
    joined = " ".join(blockers).lower()
    if "out of memory" in joined or "cuda_oom" in joined:
        return "oom"
    if "cuda_unavailable" in joined:
        return "torch_cuda_unavailable"
    if "cuda" in joined:
        return "cuda_error"
    if "missing_torch" in joined or "missing_transformers" in joined or "bitsandbytes_unavailable" in joined:
        return "missing_dependency"
    if any(blocker.startswith("missing_") for blocker in blockers):
        return "missing_input"
    if any(blocker.startswith("model_load_failed") for blocker in blockers):
        return "model_load_failure"
    return "runtime_error"


def build_qwen2p5_7b_alpaca_main_slice_response_generation(
    *,
    output_dir: Path,
    input_jsonl: Path,
    model_dir: Path,
    plan_verdict: Path,
    registry_path: Path,
    seed: int,
    max_source_examples: int,
    expected_response_rows: int,
    batch_size: int,
    max_new_tokens: int,
    max_generation_attempts: int,
    min_free_gpu_memory_mib: int,
    load_in_4bit: bool,
    low_memory: bool,
    allow_without_logprobs: bool,
    trigger_text: str,
    target_text: str,
    dry_run: bool,
) -> dict[str, Any]:
    if batch_size != 1:
        raise ValueError("Alpaca main-slice response generation requires --batch-size 1.")
    if max_source_examples <= 0:
        raise ValueError("--max-source-examples must be positive.")
    if expected_response_rows != max_source_examples * 2:
        raise ValueError("--expected-response-rows must equal 2 * --max-source-examples.")
    if max_generation_attempts < expected_response_rows:
        raise ValueError("--max-generation-attempts must be at least --expected-response-rows.")
    if not allow_without_logprobs:
        raise ValueError("--allow-without-logprobs is required for this task.")
    if trigger_text != DEFAULT_TRIGGER_TEXT:
        raise ValueError("Only lexical trigger baseline cftrigger is in scope.")
    if target_text != DEFAULT_TARGET_TEXT:
        raise ValueError("Only the fixed target response is in scope.")

    started = time.time()
    output_dir.mkdir(parents=True, exist_ok=True)
    blockers: list[str] = []
    plan_payload = read_json(plan_verdict) if plan_verdict.exists() else {}
    if plan_payload.get("verdict") != "Qwen2.5-7B Alpaca main-slice plan validated":
        blockers.append("alpaca_main_slice_plan_not_validated")
    if not input_jsonl.exists():
        blockers.append("missing_input_jsonl")
    if not model_dir.exists():
        blockers.append("missing_model_dir")

    input_rows = read_jsonl(input_jsonl) if input_jsonl.exists() else []
    selected_rows, slice_audit, slice_blockers = _select_main_slice_rows(
        input_rows,
        max_source_examples=max_source_examples,
        trigger_text=trigger_text,
        target_text=target_text,
    )
    blockers.extend(slice_blockers)
    if len(selected_rows) != expected_response_rows:
        blockers.append(f"unexpected_selected_row_count:selected={len(selected_rows)},expected={expected_response_rows}")
    if max_generation_attempts > 72:
        blockers.append("max_generation_attempts_exceeds_bounded_plan")
    if dry_run:
        blockers.append("dry_run_no_generation")

    config = GenerationConfig(
        seed=seed,
        max_new_tokens=max_new_tokens,
        temperature=0.0,
        top_p=1.0,
        batch_size=batch_size,
        use_4bit=load_in_4bit,
        low_memory=low_memory,
        min_free_gpu_memory_mib=min_free_gpu_memory_mib or (8192 if load_in_4bit else 18432),
        allow_cpu_generation=False,
        no_full_matrix=True,
        prepare_only=False,
    )

    runtime: dict[str, Any] = {}
    if blockers:
        output_rows = _blocked_rows(selected_rows, ",".join(blockers))
    else:
        output_rows, runtime, runtime_blockers = _generate_rows(selected_rows, model_dir, config)
        blockers.extend(runtime_blockers)

    generated_count = sum(1 for row in output_rows if row.get("response_generation_status") == "generated")
    blocked_count = sum(1 for row in output_rows if row.get("response_generation_status") == "blocked")
    if generated_count == expected_response_rows and not blockers:
        final_verdict = FINAL_VALIDATED
    elif generated_count > 0:
        final_verdict = FINAL_PARTIAL
    else:
        final_verdict = FINAL_NOT_VALIDATED if any(blocker.startswith("missing_") for blocker in blockers) else FINAL_PARTIAL

    response_generation_mode = {
        "summary_status": "PASS" if generated_count else "FAIL",
        "mode": "real_local_huggingface_generation" if generated_count else "blocked_or_fallback_no_generation",
        "row_count_requested": expected_response_rows,
        "row_count_selected": len(selected_rows),
        "row_count_generated": generated_count,
        "row_count_blocked": blocked_count,
        "source_examples_requested": max_source_examples,
        "source_examples_selected": slice_audit.get("selected_source_count", 0),
        "max_generation_attempts": max_generation_attempts,
        "generation_attempts_used": generated_count + blocked_count,
        "retry_attempts_used": 0,
        "aggregate_metrics_computed": False,
    }
    capability_mode = {
        "summary_status": "PASS" if generated_count else "PARTIAL" if selected_rows else "FAIL",
        "model_family": "Qwen2.5-7B-Instruct",
        "model_path": str(model_dir),
        "response_backend": "local_huggingface",
        "with_logprobs": False,
        "without_logprobs": True,
        "allow_without_logprobs": allow_without_logprobs,
        "logprobs_reason": "Task generates responses only; token logprob extraction is not claimed.",
        "batch_size": batch_size,
        "low_memory": low_memory,
        "use_4bit": load_in_4bit,
        "min_free_gpu_memory_mib": config.min_free_gpu_memory_mib,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
    }
    fallback_flags = {
        "requested_4bit": load_in_4bit,
        "used_4bit": bool(load_in_4bit and generated_count and not any("4bit" in blocker for blocker in blockers)),
        "without_logprobs_fallback": True,
        "logprobs_unavailable": True,
        "bitsandbytes_unavailable": "requested_4bit_but_bitsandbytes_unavailable" in blockers,
        "accelerate_unavailable": _dependency_status().get("accelerate") is False,
        "oom_encountered": "cuda_oom" in blockers or any("out of memory" in blocker.lower() for blocker in blockers),
        "model_load_failed": any(blocker.startswith("model_load_failed") for blocker in blockers),
        "responses_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
    }
    budget_trace = {
        "primary_query_budget": expected_response_rows,
        "hard_generation_attempt_cap": max_generation_attempts,
        "generation_attempts_used": generated_count + blocked_count,
        "generated_rows": generated_count,
        "blocked_rows": blocked_count,
        "retry_attempts_used": 0,
        "max_new_tokens": max_new_tokens,
    }
    summary = {
        "summary_status": "PASS" if final_verdict == FINAL_VALIDATED else "PARTIAL" if final_verdict == FINAL_PARTIAL else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "created_at": utc_now(),
        "output_dir": str(output_dir),
        "final_verdict": final_verdict,
        "recommended_next_step": (
            "dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation"
            if final_verdict == FINAL_VALIDATED
            else f"{TASK_ID}-repair"
            if final_verdict == FINAL_PARTIAL
            else f"{TASK_ID}-blocker-closure"
        ),
        "response_generation_mode": response_generation_mode,
        "capability_mode": capability_mode,
        "fallback_flags": fallback_flags,
        "budget_trace": budget_trace,
        "blockers": blockers,
        "blocker_type": _canonical_blocker_type(blockers),
        "input_jsonl": str(input_jsonl),
        "input_row_count": line_count(input_jsonl),
        "slice_audit": slice_audit,
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
        "runtime_elapsed_seconds": round(time.time() - started, 3),
    }

    write_json(output_dir / "main_slice_input_audit.json", slice_audit)
    write_json(output_dir / "model_path_status.json", model_path_status(model_dir))
    write_json(output_dir / "gpu_snapshot.json", nvidia_smi_snapshot())
    write_json(output_dir / "runtime.json", runtime)
    write_json(output_dir / "capability_mode.json", capability_mode)
    write_json(output_dir / "fallback_flags.json", fallback_flags)
    write_json(output_dir / "budget_trace.json", budget_trace)
    write_json(output_dir / "blockers.json", {"summary_status": "PASS" if not blockers else "BLOCKED", "blockers": blockers})
    write_jsonl(output_dir / "selected_main_slice_rows.jsonl", selected_rows)
    write_jsonl(output_dir / "qwen2p5_7b_alpaca_main_slice_response_rows.jsonl", output_rows)
    write_jsonl(output_dir / "qwen2p5_7b_alpaca_main_slice_responses.jsonl", output_rows)
    write_json(output_dir / "generation_summary.json", summary)
    write_json(output_dir / "qwen2p5_7b_alpaca_main_slice_response_generation_summary.json", summary)
    write_json(
        output_dir / "qwen2p5_7b_alpaca_main_slice_response_generation_blockers.json",
        {
            "summary_status": "PASS" if not blockers else "BLOCKED",
            "blocker_type": summary["blocker_type"] or "",
            "raw_blocker": blockers[0] if blockers else "",
            "blockers": blockers,
        },
    )
    write_json(
        output_dir / "verdict.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": summary["recommended_next_step"],
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
        },
    )
    write_json(
        output_dir / "qwen2p5_7b_alpaca_main_slice_response_generation_verdict.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": summary["recommended_next_step"],
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
        },
    )
    report_lines = [
        "# DualScope Qwen2.5-7B Alpaca Main-Slice Response Generation",
        "",
        f"- Final verdict: `{final_verdict}`",
        f"- Input rows: `{line_count(input_jsonl)}`",
        f"- Selected source examples: `{slice_audit.get('selected_source_count', 0)}`",
        f"- Selected response rows: `{len(selected_rows)}`",
        f"- Generated rows: `{generated_count}`",
        f"- Blocked rows: `{blocked_count}`",
        f"- Capability mode: `without_logprobs`",
        f"- Response generation mode: `{response_generation_mode['mode']}`",
        f"- Budget trace: `{budget_trace}`",
        f"- CUDA_VISIBLE_DEVICES: `{os.environ.get('CUDA_VISIBLE_DEVICES', '')}`",
        f"- Model path: `{model_dir}`",
        f"- 4-bit requested: `{load_in_4bit}`",
        f"- Minimum selected-GPU free memory MiB: `{config.min_free_gpu_memory_mib}`",
        "- Metrics computed: `False`",
        "- Model responses fabricated: `False`",
        "- Logprobs fabricated: `False`",
        "- Training executed: `False`",
        "- Full matrix executed: `False`",
        "- Benchmark truth changed: `False`",
        "- Gates changed: `False`",
        f"- Blockers: `{blockers}`",
        "",
    ]
    (output_dir / "dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_report.md").write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )
    (output_dir / "qwen2p5_7b_alpaca_main_slice_response_generation_report.md").write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )
    _write_registry(registry_path, summary)
    return summary
