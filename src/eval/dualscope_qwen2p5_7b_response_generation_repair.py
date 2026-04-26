"""Repair helpers for Qwen2.5-7B first-slice response generation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.eval.dualscope_qwen2p5_7b_first_slice_response_generation import (
    build_qwen2p5_7b_first_slice_response_generation,
)


SCHEMA_VERSION = "dualscope/qwen2p5-7b-response-generation-repair/v1"
FINAL_REPAIRED = "Qwen2.5-7B first-slice response generation repaired"
FINAL_PARTIAL = "Partially validated"
FINAL_NOT_VALIDATED = "Not validated"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _repair_next_step(summary: dict[str, Any]) -> tuple[str, str]:
    blockers = [str(item) for item in summary.get("blockers") or []]
    if summary.get("final_verdict") == "Qwen2.5-7B first-slice response generation validated":
        return "dualscope-qwen2p5-7b-label-aligned-metric-computation", ""
    blocker_text = " ".join(blockers).lower()
    if "oom" in blocker_text or "insufficient_selected_gpu_memory" in blocker_text:
        return "dualscope-qwen2p5-7b-quantized-response-generation-repair", "oom_or_gpu_memory"
    if "logprob" in blocker_text:
        return "dualscope-qwen2p5-7b-without-logprobs-response-generation-repair", "logprob_unavailable"
    if (
        "missing_labeled_pairs" in blocker_text
        or "missing_target_response_plan" in blocker_text
        or "missing_target_response_plan_rows" in blocker_text
        or "missing_model_path" in blocker_text
        or "missing_resource_materialization" in blocker_text
    ):
        return "dualscope-qwen2p5-7b-response-input-artifact-repair", "missing_input"
    return "dualscope-qwen2p5-7b-response-generation-repair", "missing_response_generation_artifacts"


def _write_repair_artifacts(output_dir: Path, summary: dict[str, Any], rows_text: str = "") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    next_task = str(summary.get("next_task") or "dualscope-qwen2p5-7b-response-generation-repair")
    blocker_type = str(summary.get("blocker_type") or "")
    final_verdict = str(summary.get("final_verdict") or FINAL_PARTIAL)
    write_json(output_dir / "response_generation_repair_summary.json", summary)
    write_json(output_dir / "response_generation_repair_blockers.json", {"blockers": summary.get("blockers") or []})
    (output_dir / "response_generation_repair_responses.jsonl").write_text(rows_text, encoding="utf-8")
    write_json(
        output_dir / "dualscope_qwen2p5_7b_response_generation_repair_verdict.json",
        {
            "summary_status": summary.get("summary_status"),
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": next_task,
            "blocker_type": blocker_type,
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
        },
    )
    write_json(
        output_dir / "dualscope_qwen2p5_7b_response_generation_repair_next_step_recommendation.json",
        {"next_task": next_task, "blocker_type": blocker_type},
    )
    (output_dir / "response_generation_repair_report.md").write_text(
        "\n".join(
            [
                "# Qwen2.5-7B Response Generation Repair",
                "",
                f"- Final verdict: `{final_verdict}`",
                f"- Generated rows: `{summary.get('generated_rows', 0)}`",
                f"- Next task: `{next_task}`",
                f"- Blocker type: `{blocker_type or 'none'}`",
                f"- Blockers: `{summary.get('blockers') or []}`",
                "- Model responses fabricated: `False`",
                "- Logprobs fabricated: `False`",
                "- Metrics computed: `False`",
                "- Benchmark truth changed: `False`",
                "- Gates changed: `False`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def build_qwen2p5_7b_response_generation_repair(
    *,
    output_dir: Path,
    first_slice_output_dir: Path,
    labeled_pairs: Path,
    target_response_plan_dir: Path,
    resource_materialization_dir: Path,
    model_dir: Path,
    seed: int,
    max_examples: int,
    batch_size: int,
    max_new_tokens: int,
    min_free_gpu_memory_mib: int,
    load_in_4bit: bool,
    allow_without_logprobs: bool,
    dry_run: bool,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    first_slice_output_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        summary = {
            "summary_status": "PARTIAL",
            "schema_version": SCHEMA_VERSION,
            "task_id": "dualscope-qwen2p5-7b-response-generation-repair",
            "created_at": utc_now(),
            "final_verdict": FINAL_PARTIAL,
            "repair_for": "dualscope-qwen2p5-7b-first-slice-response-generation",
            "blockers": ["dry_run_no_generation"],
            "next_task": "dualscope-qwen2p5-7b-response-generation-repair",
            "blocker_type": "dry_run",
            "model_response_fabricated": False,
            "logprobs_fabricated": False,
            "metrics_computed": False,
            "benchmark_truth_changed": False,
            "gate_changed": False,
            "route_c_199_plus_generated": False,
        }
        _write_repair_artifacts(output_dir, summary)
        return summary

    repair_input_blockers: list[str] = []
    resource_verdict_path = resource_materialization_dir / "dualscope_qwen2p5_7b_resource_materialization_verdict.json"
    if not resource_materialization_dir.exists():
        repair_input_blockers.append("missing_resource_materialization_dir")
    elif not resource_verdict_path.exists():
        repair_input_blockers.append("missing_resource_materialization_verdict")

    generation_summary = build_qwen2p5_7b_first_slice_response_generation(
        output_dir=first_slice_output_dir,
        labeled_pairs=labeled_pairs,
        target_response_plan_dir=target_response_plan_dir,
        model_path=model_dir,
        seed=seed,
        trigger_text="cftrigger",
        target_text="I have completed the requested instruction.",
        max_new_tokens=max_new_tokens,
        temperature=0.0,
        top_p=1.0,
        batch_size=batch_size,
        use_4bit=load_in_4bit,
        low_memory=True,
        min_free_gpu_memory_mib=min_free_gpu_memory_mib,
        allow_cpu_generation=False,
        no_full_matrix=True,
        max_rows=max_examples,
        prepare_only=False,
        prepare_only_reason="",
    )
    generated_rows = int(generation_summary.get("response_generation_mode", {}).get("row_count_generated") or 0)
    generation_blockers = list(generation_summary.get("blockers") or [])
    all_blockers = repair_input_blockers + generation_blockers
    generation_summary_for_routing = {**generation_summary, "blockers": all_blockers}
    if generation_summary.get("final_verdict") == "Qwen2.5-7B first-slice response generation validated" or generated_rows > 0:
        final_verdict = FINAL_REPAIRED
    elif generation_summary.get("final_verdict") == "Not validated":
        final_verdict = FINAL_NOT_VALIDATED
    else:
        final_verdict = FINAL_PARTIAL
    if repair_input_blockers and final_verdict == FINAL_REPAIRED:
        final_verdict = FINAL_PARTIAL
    next_task, blocker_type = _repair_next_step(generation_summary_for_routing)
    if generated_rows == 0 and blocker_type in {"missing_input", "oom_or_gpu_memory", "logprob_unavailable"}:
        final_verdict = FINAL_PARTIAL
    if final_verdict == FINAL_REPAIRED:
        next_task = "dualscope-qwen2p5-7b-label-aligned-metric-computation"
        blocker_type = ""
    summary = {
        "summary_status": "PASS" if final_verdict == FINAL_REPAIRED else "PARTIAL" if final_verdict == FINAL_PARTIAL else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_id": "dualscope-qwen2p5-7b-response-generation-repair",
        "created_at": utc_now(),
        "final_verdict": final_verdict,
        "repair_for": "dualscope-qwen2p5-7b-first-slice-response-generation",
        "first_slice_output_dir": str(first_slice_output_dir),
        "source_generation_verdict": generation_summary.get("final_verdict"),
        "generated_rows": generated_rows,
        "blockers": all_blockers,
        "blocker_type": blocker_type,
        "next_task": next_task,
        "required_inputs": {
            "labeled_pairs": str(labeled_pairs),
            "target_response_plan_dir": str(target_response_plan_dir),
            "resource_materialization_dir": str(resource_materialization_dir),
            "model_dir": str(model_dir),
        },
        "allow_without_logprobs": allow_without_logprobs,
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
    }
    rows_source = first_slice_output_dir / "dualscope_qwen2p5_7b_first_slice_response_generation_rows.jsonl"
    rows_text = ""
    if rows_source.exists():
        rows_text = rows_source.read_text(encoding="utf-8")
    _write_repair_artifacts(output_dir, summary, rows_text)
    return summary
