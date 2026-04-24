"""Post-analysis for the DualScope first-slice report skeleton."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-first-slice-report-skeleton-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def post_dualscope_first_slice_report_skeleton_analysis(skeleton_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_report_skeleton_summary.json",
        "dualscope_first_slice_table_skeleton.json",
        "dualscope_first_slice_figure_placeholder.json",
        "dualscope_first_slice_report_artifact_links.json",
        "dualscope_first_slice_report_skeleton.md",
    ]
    missing = [name for name in required if not (skeleton_dir / name).exists()]
    summary = _load_json(skeleton_dir / "dualscope_first_slice_report_skeleton_summary.json")
    table = _load_json(skeleton_dir / "dualscope_first_slice_table_skeleton.json")
    figure = _load_json(skeleton_dir / "dualscope_first_slice_figure_placeholder.json")
    links = _load_json(skeleton_dir / "dualscope_first_slice_report_artifact_links.json")

    report_ready = summary["report_skeleton_ready"] and (skeleton_dir / "dualscope_first_slice_report_skeleton.md").stat().st_size > 0
    table_ready = summary["table_skeleton_ready"] and len(table["tables"]) >= 3
    figure_ready = summary["figure_placeholder_ready"] and len(figure["figures"]) >= 2
    links_ready = summary["artifact_links_ready"] and all(Path(value).exists() for value in links.values())
    no_performance_claims = not summary["performance_claims_made"]

    if not missing and all([report_ready, table_ready, figure_ready, links_ready, no_performance_claims]):
        final_verdict = "First slice report skeleton validated"
        recommendation = "进入 dualscope-minimal-first-slice-real-run-plan"
        basis = [
            "The report skeleton, table skeleton, figure placeholders, and artifact links are present.",
            "The skeleton references validated first-slice smoke artifacts without making performance claims.",
            "The next natural step is a real first-slice run plan, still within DualScope boundaries.",
        ]
    elif not missing:
        final_verdict = "Partially validated"
        recommendation = "进入 first-slice-report-skeleton-repair"
        basis = ["The report skeleton exists, but one or more completeness checks failed."]
    else:
        final_verdict = "Not validated"
        recommendation = "进入 first-slice-report-skeleton-debug"
        basis = ["Required report skeleton artifacts are missing."]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "report_ready": report_ready,
        "table_ready": table_ready,
        "figure_ready": figure_ready,
        "links_ready": links_ready,
        "no_performance_claims": no_performance_claims,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_first_slice_report_skeleton_validated__partially_validated__not_validated",
        "primary_basis": basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": basis,
    }
    write_json(output_dir / "dualscope_first_slice_report_skeleton_analysis_summary.json", analysis_summary)
    write_json(output_dir / "dualscope_first_slice_report_skeleton_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_report_skeleton_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_report_skeleton_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "dualscope_first_slice_report_skeleton_verdict.json").resolve()),
            "recommendation": str((output_dir / "dualscope_first_slice_report_skeleton_next_step_recommendation.json").resolve()),
        },
    }
