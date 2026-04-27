"""External GPU runner for bounded Qwen2.5-7B generation.

This module intentionally runs outside ``codex exec``.  It reuses the bounded
Alpaca main-slice generation implementation, then writes a small external-runner
artifact set and a tracked verdict registry.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.eval.dualscope_qwen2p5_7b_alpaca_main_slice_response_generation import (
    build_qwen2p5_7b_alpaca_main_slice_response_generation,
)
from src.eval.dualscope_qwen2p5_7b_first_slice_response_generation import (
    line_count,
    nvidia_smi_snapshot,
    write_json,
    write_jsonl,
)


TASK_ID = "dualscope-external-gpu-runner-for-qwen2p5-7b-generation"
SCHEMA_VERSION = "dualscope/qwen2p5-7b-external-gpu-generation/v1"
VALIDATED = "Qwen2.5-7B external GPU generation validated"
PARTIAL = "Partially validated"
NOT_VALIDATED = "Not validated"
DEFAULT_MAIN_OUTPUT_DIR = Path("outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default")
DEFAULT_REGISTRY_PATH = Path(
    ".reports/dualscope_task_verdicts/dualscope-external-gpu-runner-for-qwen2p5-7b-generation.json"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _torch_cuda_snapshot() -> dict[str, Any]:
    try:
        import torch

        cuda_available = bool(torch.cuda.is_available())
        devices = []
        if cuda_available:
            for index in range(torch.cuda.device_count()):
                devices.append({"visible_index": index, "name": torch.cuda.get_device_name(index)})
        return {
            "summary_status": "PASS" if cuda_available else "FAIL",
            "torch_version": str(torch.__version__),
            "torch_cuda_version": str(torch.version.cuda),
            "cuda_available": cuda_available,
            "device_count": len(devices),
            "devices": devices,
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
            "cuda_device_order": os.environ.get("CUDA_DEVICE_ORDER", ""),
        }
    except Exception as exc:  # noqa: BLE001 - readiness artifact must record real failure.
        return {
            "summary_status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
            "cuda_device_order": os.environ.get("CUDA_DEVICE_ORDER", ""),
        }


def _filter_generated_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row.get("response_generation_status") == "generated"
        and bool(row.get("model_response_present"))
        and str(row.get("model_response") or "").strip()
        and not bool(row.get("model_response_fabricated"))
    ]


def _blocker_type(summary: dict[str, Any], torch_snapshot: dict[str, Any]) -> str:
    if summary.get("blocker_type"):
        return str(summary["blocker_type"])
    if not torch_snapshot.get("cuda_available"):
        return "torch_cuda_unavailable"
    blockers = " ".join(str(item) for item in summary.get("blockers") or []).lower()
    if "out of memory" in blockers or "oom" in blockers:
        return "oom"
    if "model_load" in blockers:
        return "model_load_failure"
    if "missing" in blockers:
        return "missing_input"
    if blockers:
        return "runtime_error"
    return ""


def build_external_gpu_generation(
    *,
    model_dir: Path,
    labeled_pairs: Path,
    target_response_plan_dir: Path,
    output_dir: Path,
    main_output_dir: Path,
    registry_path: Path,
    seed: int,
    max_examples: int,
    batch_size: int,
    max_new_tokens: int,
    device_map: str,
    allow_without_logprobs: bool,
    dry_run: bool,
) -> dict[str, Any]:
    if device_map != "auto":
        raise ValueError("Only --device-map auto is supported for this bounded runner.")
    if batch_size != 1:
        raise ValueError("External GPU generation requires --batch-size 1.")
    if max_examples <= 0:
        raise ValueError("--max-examples must be positive.")
    if not allow_without_logprobs:
        raise ValueError("--allow-without-logprobs is required; logprobs are not claimed.")

    output_dir.mkdir(parents=True, exist_ok=True)
    main_output_dir.mkdir(parents=True, exist_ok=True)
    torch_snapshot = _torch_cuda_snapshot()
    smi_snapshot = nvidia_smi_snapshot()
    target_plan_ready = target_response_plan_dir.exists()

    if dry_run:
        summary = {
            "summary_status": "DRY_RUN",
            "schema_version": SCHEMA_VERSION,
            "task_id": TASK_ID,
            "created_at": utc_now(),
            "final_verdict": PARTIAL,
            "recommended_next_step": TASK_ID,
            "dry_run": True,
            "model_dir": str(model_dir),
            "labeled_pairs": str(labeled_pairs),
            "target_response_plan_dir": str(target_response_plan_dir),
            "target_response_plan_ready": target_plan_ready,
            "torch_cuda_snapshot": torch_snapshot,
            "nvidia_smi_snapshot": smi_snapshot,
            "response_row_count": 0,
            "blocker_type": "dry_run_no_generation",
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
        }
        write_json(output_dir / "external_gpu_generation_summary.json", summary)
        write_json(output_dir / "external_gpu_generation_blockers.json", {"blocker_type": "dry_run_no_generation"})
        write_json(output_dir / "external_gpu_generation_verdict.json", summary)
        (output_dir / "external_gpu_generation_report.md").write_text(
            "# DualScope External GPU Generation\n\n"
            "- Dry run: `true`\n"
            f"- CUDA available: `{torch_snapshot.get('cuda_available')}`\n"
            "- Model responses fabricated: `False`\n",
            encoding="utf-8",
        )
        write_jsonl(output_dir / "external_gpu_generation_responses.jsonl", [])
        return summary

    inner_summary = build_qwen2p5_7b_alpaca_main_slice_response_generation(
        output_dir=main_output_dir,
        input_jsonl=labeled_pairs,
        model_dir=model_dir,
        plan_verdict=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json"),
        registry_path=Path(".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.json"),
        seed=seed,
        max_source_examples=max_examples,
        expected_response_rows=max_examples * 2,
        batch_size=batch_size,
        max_new_tokens=max_new_tokens,
        max_generation_attempts=max_examples * 2,
        min_free_gpu_memory_mib=18432,
        load_in_4bit=False,
        low_memory=True,
        allow_without_logprobs=allow_without_logprobs,
        trigger_text="cftrigger",
        target_text="I have completed the requested instruction.",
        dry_run=False,
    )

    all_rows = read_jsonl(main_output_dir / "qwen2p5_7b_alpaca_main_slice_responses.jsonl")
    generated_rows = _filter_generated_rows(all_rows)
    response_count = len(generated_rows)
    blocker_type = _blocker_type(inner_summary, torch_snapshot)
    if response_count > 0:
        final_verdict = VALIDATED
        next_task = "dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation"
    elif blocker_type == "oom":
        final_verdict = PARTIAL
        next_task = "dualscope-qwen2p5-7b-external-gpu-oom-repair"
    elif blocker_type == "model_load_failure":
        final_verdict = PARTIAL
        next_task = "dualscope-qwen2p5-7b-model-load-blocker-closure"
    else:
        final_verdict = PARTIAL if blocker_type else NOT_VALIDATED
        next_task = "dualscope-qwen2p5-7b-external-gpu-runner-repair"

    summary = {
        "summary_status": "PASS" if response_count > 0 else "PARTIAL" if blocker_type else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "created_at": utc_now(),
        "final_verdict": final_verdict,
        "recommended_next_step": next_task,
        "dry_run": False,
        "model_dir": str(model_dir),
        "labeled_pairs": str(labeled_pairs),
        "target_response_plan_dir": str(target_response_plan_dir),
        "target_response_plan_ready": target_plan_ready,
        "main_output_dir": str(main_output_dir),
        "torch_cuda_snapshot": torch_snapshot,
        "nvidia_smi_snapshot": smi_snapshot,
        "inner_summary": inner_summary,
        "response_row_count": response_count,
        "all_output_row_count": len(all_rows),
        "blocker_type": blocker_type,
        "without_logprobs_fallback": True,
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
    }
    write_json(output_dir / "external_gpu_generation_summary.json", summary)
    write_jsonl(output_dir / "external_gpu_generation_responses.jsonl", generated_rows)
    write_json(
        output_dir / "external_gpu_generation_blockers.json",
        {
            "summary_status": "PASS" if response_count > 0 else "BLOCKED",
            "blocker_type": "" if response_count > 0 else blocker_type,
            "blockers": inner_summary.get("blockers") or ([] if response_count > 0 else [blocker_type]),
        },
    )
    write_json(
        output_dir / "external_gpu_generation_verdict.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": next_task,
            "response_row_count": response_count,
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
        },
    )
    report = [
        "# DualScope External GPU Runner for Qwen2.5-7B",
        "",
        f"- Final verdict: `{final_verdict}`",
        f"- Response rows generated: `{response_count}`",
        f"- CUDA available in runner: `{torch_snapshot.get('cuda_available')}`",
        f"- CUDA_VISIBLE_DEVICES: `{os.environ.get('CUDA_VISIBLE_DEVICES', '')}`",
        f"- Model dir: `{model_dir}`",
        f"- Main output dir: `{main_output_dir}`",
        f"- Blocker type: `{blocker_type}`",
        "- Without-logprobs fallback: `True`",
        "- Model responses fabricated: `False`",
        "- Logprobs fabricated: `False`",
        "- Metrics computed: `False`",
        "- Full matrix executed: `False`",
    ]
    (output_dir / "external_gpu_generation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    write_json(
        registry_path,
        {
            "task_id": TASK_ID,
            "verdict": final_verdict,
            "source_output_dir": str(output_dir),
            "response_output_dir": str(main_output_dir),
            "created_at": summary["created_at"],
            "validated": final_verdict == VALIDATED,
            "next_task": next_task,
            "response_row_count": response_count,
            "blocker_type": blocker_type if response_count == 0 else "",
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
        },
    )

    # Preserve explicit external artifacts even though the canonical main-slice
    # directory is the downstream contract.
    for source_name, dest_name in (
        ("qwen2p5_7b_alpaca_main_slice_response_generation_summary.json", "main_slice_sync_summary.json"),
        ("qwen2p5_7b_alpaca_main_slice_response_generation_verdict.json", "main_slice_sync_verdict.json"),
    ):
        source = main_output_dir / source_name
        if source.exists():
            shutil.copy2(source, output_dir / dest_name)
    return summary
