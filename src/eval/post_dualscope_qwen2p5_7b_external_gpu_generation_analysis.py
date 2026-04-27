"""Post-analysis for external Qwen2.5-7B GPU generation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_qwen2p5_7b_first_slice_response_generation import write_json
from src.eval.dualscope_qwen2p5_7b_external_gpu_generation import (
    DEFAULT_REGISTRY_PATH,
    PARTIAL,
    TASK_ID,
    VALIDATED,
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def line_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def build_post_analysis(*, input_dir: Path, output_dir: Path, registry_path: Path = DEFAULT_REGISTRY_PATH) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = input_dir / "external_gpu_generation_summary.json"
    blockers_path = input_dir / "external_gpu_generation_blockers.json"
    responses_path = input_dir / "external_gpu_generation_responses.jsonl"
    summary = read_json(summary_path) if summary_path.exists() else {}
    blockers = read_json(blockers_path) if blockers_path.exists() else {}
    response_rows = line_count(responses_path)
    final_verdict = str(summary.get("final_verdict") or (VALIDATED if response_rows > 0 else PARTIAL))
    next_step = str(summary.get("recommended_next_step") or "dualscope-qwen2p5-7b-external-gpu-runner-repair")
    analysis = {
        "summary_status": "PASS" if final_verdict == VALIDATED else "PARTIAL",
        "task_id": TASK_ID,
        "input_dir": str(input_dir),
        "final_verdict": final_verdict,
        "recommended_next_step": next_step,
        "response_row_count": response_rows,
        "blocker_type": blockers.get("blocker_type") or summary.get("blocker_type") or "",
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
    }
    write_json(output_dir / "external_gpu_generation_analysis_summary.json", analysis)
    write_json(output_dir / "external_gpu_generation_verdict.json", analysis)
    write_json(output_dir / "external_gpu_generation_next_step_recommendation.json", {"next_task": next_step})
    if final_verdict == VALIDATED and response_rows > 0:
        write_json(
            registry_path,
            {
                "task_id": TASK_ID,
                "verdict": final_verdict,
                "source_output_dir": str(input_dir),
                "validated": True,
                "next_task": next_step,
                "response_row_count": response_rows,
                "model_response_fabricated": False,
                "logprobs_fabricated": False,
                "metrics_computed": False,
            },
        )
    (output_dir / "external_gpu_generation_analysis_report.md").write_text(
        "# DualScope External GPU Generation Analysis\n\n"
        f"- Final verdict: `{final_verdict}`\n"
        f"- Response rows: `{response_rows}`\n"
        f"- Blocker type: `{analysis['blocker_type']}`\n"
        "- Model responses fabricated: `False`\n"
        "- Logprobs fabricated: `False`\n"
        "- Metrics computed: `False`\n",
        encoding="utf-8",
    )
    return analysis
