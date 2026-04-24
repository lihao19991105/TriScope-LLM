"""Post-analysis for DualScope minimal real-run command entrypoint package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_real_run_entrypoint_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-minimal-real-run-command-entrypoint-package/v1"


def post_dualscope_minimal_real_run_command_entrypoint_package_analysis(package_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_real_run_entrypoint_scope.json",
        "dualscope_real_run_entrypoint_inventory.json",
        "dualscope_real_run_entrypoint_cli_contract.json",
        "dualscope_real_run_entrypoint_py_compile_check.json",
        "dualscope_real_run_entrypoint_dry_run_results.json",
        "dualscope_real_run_entrypoint_required_artifacts_check.json",
        "dualscope_real_run_entrypoint_chain_compatibility_check.json",
        "dualscope_real_run_entrypoint_readiness_delta.json",
        "dualscope_real_run_entrypoint_package_summary.json",
        "dualscope_real_run_entrypoint_package_details.jsonl",
        "dualscope_real_run_entrypoint_package_report.md",
        "dualscope_real_run_entrypoint_package_verdict.json",
        "dualscope_real_run_entrypoint_package_next_step_recommendation.json",
    ]
    missing = [name for name in required if not (package_dir / name).exists()]
    if missing:
        final_verdict = "Not validated"
        recommendation = "dualscope-real-run-entrypoint-blocker-closure"
        source_summary: dict[str, Any] = {}
    else:
        source_summary = json.loads((package_dir / "dualscope_real_run_entrypoint_package_summary.json").read_text(encoding="utf-8"))
        final_verdict = source_summary.get("final_verdict", "Not validated")
        recommendation = source_summary.get("recommended_next_step", "dualscope-real-run-entrypoint-blocker-closure")
    summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "source_summary": source_summary,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
    }
    rec = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    write_json(output_dir / "dualscope_real_run_entrypoint_package_analysis_summary.json", summary)
    write_json(output_dir / "dualscope_real_run_entrypoint_package_verdict.json", verdict)
    write_json(output_dir / "dualscope_real_run_entrypoint_package_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict, "recommendation": rec}

