"""Post-analysis for the DualScope minimal first-slice smoke run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-minimal-first-slice-smoke-run-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def post_dualscope_minimal_first_slice_smoke_run_analysis(smoke_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    expected = [
        "stage1_illumination_outputs.jsonl",
        "stage1_illumination_summary.json",
        "stage2_confidence_outputs.jsonl",
        "stage2_confidence_summary.json",
        "stage3_fusion_outputs.jsonl",
        "stage3_fusion_summary.json",
        "baseline_scores.json",
        "metrics_placeholder.json",
        "budget_usage_summary.json",
        "first_slice_run_manifest.json",
        "dualscope_first_slice_smoke_run_summary.json",
        "dualscope_first_slice_smoke_run_details.jsonl",
        "dualscope_first_slice_smoke_run_report.md",
    ]
    missing = [name for name in expected if not (smoke_dir / name).exists()]
    summary = _load_json(smoke_dir / "dualscope_first_slice_smoke_run_summary.json")
    budget = _load_json(smoke_dir / "budget_usage_summary.json")
    metrics = _load_json(smoke_dir / "metrics_placeholder.json")

    stage_counts_ready = summary["stage1_row_count"] == 3 and summary["stage3_row_count"] == 3
    stage2_ready = summary["stage2_row_count"] >= 2
    capability_ready = {"with_logprobs", "without_logprobs"}.issubset(set(summary["capability_modes_observed"]))
    budget_ready = budget["total_query_count"] > 0 and not budget["full_matrix_executed"]
    metrics_ready = metrics["metrics_not_computed"] and bool(metrics["placeholder_metrics"])
    no_expansion = summary["controlled_smoke_only"] and not summary["full_matrix_executed"]

    if not missing and all([stage_counts_ready, stage2_ready, capability_ready, budget_ready, metrics_ready, no_expansion]):
        final_verdict = "Minimal first slice smoke run validated"
        recommendation = "进入 dualscope-first-slice-artifact-validation"
        basis = [
            "The smoke emitted Stage 1, Stage 2, Stage 3, baseline, metric-placeholder, and budget artifacts.",
            "Both with-logprobs and without-logprobs capability paths are represented.",
            "The run is explicitly controlled smoke only and not a full matrix execution.",
        ]
    elif not missing:
        final_verdict = "Partially validated"
        recommendation = "进入 first-slice-smoke-run-compression"
        basis = ["Smoke artifacts exist but one or more coverage checks failed."]
    else:
        final_verdict = "Not validated"
        recommendation = "进入 first-slice-execution-debug"
        basis = ["Required smoke artifacts are missing."]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "stage_counts_ready": stage_counts_ready,
        "stage2_ready": stage2_ready,
        "capability_ready": capability_ready,
        "budget_ready": budget_ready,
        "metrics_ready": metrics_ready,
        "no_expansion": no_expansion,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_first_slice_smoke_run_validated__partially_validated__not_validated",
        "primary_basis": basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": basis,
    }
    write_json(output_dir / "dualscope_first_slice_smoke_run_analysis_summary.json", analysis_summary)
    write_json(output_dir / "dualscope_first_slice_smoke_run_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_smoke_run_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_smoke_run_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "dualscope_first_slice_smoke_run_verdict.json").resolve()),
            "recommendation": str((output_dir / "dualscope_first_slice_smoke_run_next_step_recommendation.json").resolve()),
        },
    }
