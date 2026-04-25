"""Post-analysis for DualScope Qwen2.5-7B resource materialization."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.eval.dualscope_qwen2p5_7b_resource_common import (
    DEFAULT_ANALYSIS_OUTPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    read_json,
    utc_now,
    write_json,
)


def build_post_analysis(input_dir: Path = DEFAULT_OUTPUT_DIR, output_dir: Path = DEFAULT_ANALYSIS_OUTPUT_DIR) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = input_dir / "dualscope_qwen2p5_7b_resource_materialization_summary.json"
    verdict_path = input_dir / "dualscope_qwen2p5_7b_resource_materialization_verdict.json"
    blockers_path = input_dir / "dualscope_qwen2p5_7b_resource_blockers.json"
    summary = read_json(summary_path) if summary_path.exists() else {}
    verdict = read_json(verdict_path) if verdict_path.exists() else {}
    blockers = read_json(blockers_path).get("blockers", []) if blockers_path.exists() else []
    final_verdict = verdict.get("final_verdict") or "Not validated"
    analysis = {
        "summary_status": "PASS" if final_verdict != "Not validated" else "FAIL",
        "schema_version": "dualscope/qwen2p5-7b-resource-materialization-analysis/v1",
        "generated_at": utc_now(),
        "input_dir": str(input_dir),
        "final_verdict": final_verdict,
        "blocker_count": len(blockers),
        "model_ready": bool(summary.get("resolved_model_path"))
        and summary.get("tokenizer_check") == "PASS"
        and summary.get("config_check") == "PASS",
        "data_ready": bool(summary.get("labeled_pairs_ready")) and bool(summary.get("target_response_plan_ready")),
        "recommended_next_step": (
            "dualscope-qwen2p5-7b-first-slice-response-generation-plan"
            if final_verdict == "Qwen2.5-7B resource materialization validated"
            else "dualscope-qwen2p5-7b-resource-materialization-repair"
        ),
        "blockers": blockers,
    }
    write_json(output_dir / "dualscope_qwen2p5_7b_resource_materialization_analysis_summary.json", analysis)
    write_json(output_dir / "dualscope_qwen2p5_7b_resource_materialization_verdict.json", verdict or analysis)
    report = [
        "# Qwen2.5-7B Resource Materialization Analysis",
        "",
        "- Final verdict: `%s`" % analysis["final_verdict"],
        "- Model ready: `%s`" % analysis["model_ready"],
        "- Data ready: `%s`" % analysis["data_ready"],
        "- Recommended next step: `%s`" % analysis["recommended_next_step"],
        "",
        "## Blockers",
    ]
    if blockers:
        for blocker in blockers:
            report.append("- `%s`: %s" % (blocker.get("kind"), blocker.get("message")))
    else:
        report.append("- None.")
    (output_dir / "dualscope_qwen2p5_7b_resource_materialization_analysis_report.md").write_text(
        "\n".join(report) + "\n",
        encoding="utf-8",
    )
    return analysis

