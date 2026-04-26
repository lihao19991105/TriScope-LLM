"""Post-analysis for Qwen2.5-7B response-generation repair."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscope/qwen2p5-7b-response-generation-repair-analysis/v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def current_git_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
    except Exception:
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


def build_post_qwen2p5_7b_response_generation_repair_analysis(
    *,
    repair_output_dir: Path,
    output_dir: Path,
    registry_path: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = repair_output_dir / "response_generation_repair_summary.json"
    if summary_path.exists():
        summary = read_json(summary_path)
        final_verdict = str(summary.get("final_verdict") or "Partially validated")
        next_task = str(summary.get("next_task") or "dualscope-qwen2p5-7b-response-generation-repair")
        blocker_type = str(summary.get("blocker_type") or "")
        source_output_dir = str(repair_output_dir)
        validated = final_verdict == "Qwen2.5-7B first-slice response generation repaired"
    else:
        summary = {}
        final_verdict = "Partially validated"
        next_task = "dualscope-qwen2p5-7b-response-generation-repair"
        blocker_type = "missing_response_generation_artifacts"
        source_output_dir = str(repair_output_dir)
        validated = False
    verdict = {
        "summary_status": "PASS" if validated else "PARTIAL" if final_verdict == "Partially validated" else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "created_at": utc_now(),
        "task_id": "dualscope-qwen2p5-7b-response-generation-repair",
        "final_verdict": final_verdict,
        "verdict": final_verdict,
        "validated": validated,
        "repair_for": "dualscope-qwen2p5-7b-first-slice-response-generation",
        "source_output_dir": source_output_dir,
        "next_task": next_task,
        "blocker_type": blocker_type,
        "model_response_fabricated": False,
        "logprobs_fabricated": False,
        "metrics_computed": False,
    }
    write_json(output_dir / "dualscope_qwen2p5_7b_response_generation_repair_verdict.json", verdict)
    write_json(output_dir / "dualscope_qwen2p5_7b_response_generation_repair_next_step_recommendation.json", {"next_task": next_task})
    registry_payload = {
        "task_id": "dualscope-qwen2p5-7b-response-generation-repair",
        "verdict": final_verdict,
        "source_output_dir": source_output_dir,
        "commit": current_git_commit(),
        "created_at": utc_now(),
        "validated": validated,
        "repair_for": "dualscope-qwen2p5-7b-first-slice-response-generation",
        "next_task": next_task,
    }
    if blocker_type:
        registry_payload["blocker_type"] = blocker_type
    write_json(registry_path, registry_payload)
    (output_dir / "dualscope_qwen2p5_7b_response_generation_repair_analysis_report.md").write_text(
        "\n".join(
            [
                "# Qwen2.5-7B Response Generation Repair Analysis",
                "",
                f"- Verdict: `{final_verdict}`",
                f"- Validated: `{validated}`",
                f"- Next task: `{next_task}`",
                f"- Blocker type: `{blocker_type or 'none'}`",
                "- Fabricated responses/logprobs/metrics: `False`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return verdict
