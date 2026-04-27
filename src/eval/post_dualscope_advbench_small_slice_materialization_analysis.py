"""Post-analysis for AdvBench small-slice materialization."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscope/advbench-small-slice-materialization-analysis/v1"
TASK_ID = "dualscope-advbench-small-slice-materialization"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_post_advbench_small_slice_materialization_analysis(
    *,
    materialization_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = _read_json(materialization_dir / "advbench_small_slice_materialization_summary.json")
    if not summary:
        summary = _read_json(materialization_dir / "advbench_small_slice_summary.json")
    verdict = _read_json(materialization_dir / "advbench_small_slice_verdict.json")
    blockers = _read_json(materialization_dir / "advbench_small_slice_blockers.json")
    schema_check = _read_json(materialization_dir / "advbench_small_slice_schema_check.json")

    final_verdict = str(verdict.get("final_verdict") or summary.get("final_verdict") or "Not validated")
    recommended_next_step = str(
        verdict.get("recommended_next_step")
        or summary.get("recommended_next_step")
        or "dualscope-advbench-small-slice-data-blocker-closure"
    )
    row_count = int(summary.get("row_count") or verdict.get("row_count") or 0)
    analysis = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "created_at": _utc_now(),
        "final_verdict": final_verdict,
        "recommended_next_step": recommended_next_step,
        "row_count": row_count,
        "schema_valid": bool(schema_check.get("schema_valid")),
        "blocker_type": blockers.get("blocker_type", ""),
        "blockers": blockers.get("blockers", []),
        "data_fabricated": bool(summary.get("data_fabricated", False)),
        "benchmark_truth_changed": bool(summary.get("benchmark_truth_changed", False)),
        "gate_changed": bool(summary.get("gate_changed", False)),
    }
    recommendation = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "next_task": recommended_next_step,
        "row_count": row_count,
        "final_verdict": final_verdict,
    }

    _write_json(output_dir / "advbench_small_slice_materialization_analysis_summary.json", analysis)
    _write_json(output_dir / "advbench_small_slice_materialization_verdict.json", verdict or analysis)
    _write_json(output_dir / "advbench_small_slice_materialization_next_step_recommendation.json", recommendation)
    (output_dir / "advbench_small_slice_materialization_analysis_report.md").write_text(
        "\n".join(
            [
                "# AdvBench Small-Slice Materialization Analysis",
                "",
                f"- Final verdict: `{final_verdict}`",
                f"- Row count: `{row_count}`",
                f"- Schema valid: `{analysis['schema_valid']}`",
                f"- Next task: `{recommended_next_step}`",
                f"- Blockers: `{analysis['blockers']}`",
                "- Data fabricated: `False`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return analysis
