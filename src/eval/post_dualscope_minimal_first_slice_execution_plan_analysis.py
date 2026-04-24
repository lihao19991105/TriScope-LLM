"""Post-analysis for the DualScope minimal first-slice execution plan."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-minimal-first-slice-execution-plan-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def _count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def post_dualscope_minimal_first_slice_execution_plan_analysis(plan_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    required = [
        "dualscope_first_slice_definition.json",
        "dualscope_first_slice_run_contract.json",
        "dualscope_first_slice_expected_artifacts.json",
        "dualscope_first_slice_validation_criteria.json",
        "dualscope_first_slice_resource_contract.json",
        "dualscope_first_slice_failure_fallback_plan.json",
        "dualscope_first_slice_summary.json",
        "dualscope_first_slice_details.jsonl",
        "dualscope_first_slice_report.md",
    ]
    missing = [name for name in required if not (plan_dir / name).exists()]
    definition = _load_json(plan_dir / "dualscope_first_slice_definition.json")
    run_contract = _load_json(plan_dir / "dualscope_first_slice_run_contract.json")
    expected = _load_json(plan_dir / "dualscope_first_slice_expected_artifacts.json")
    validation = _load_json(plan_dir / "dualscope_first_slice_validation_criteria.json")
    resource = _load_json(plan_dir / "dualscope_first_slice_resource_contract.json")
    summary = _load_json(plan_dir / "dualscope_first_slice_summary.json")
    detail_count = _count_jsonl(plan_dir / "dualscope_first_slice_details.jsonl")

    slice_ready = all(definition[field] for field in ["dataset_id", "model_id", "trigger_id", "target_id"])
    run_ready = len(run_contract["stage_order"]) == 3 and "full_matrix_sweep" in run_contract["disallowed_now"]
    artifact_ready = len(expected["expected_artifacts"]) >= 10
    validation_ready = "all expected artifacts exist" in validation["success_criteria"]
    resource_ready = resource["resource_boundary"] == "2 x RTX 3090" and resource["no_training_required_for_smoke"]
    details_ready = detail_count == summary["details_row_count"]
    no_expansion = summary["full_matrix_disallowed"] and summary["controlled_plan_only"]

    if not missing and all([slice_ready, run_ready, artifact_ready, validation_ready, resource_ready, details_ready, no_expansion]):
        final_verdict = "Minimal first slice execution plan validated"
        recommendation = "进入 dualscope-minimal-first-slice-smoke-run"
        basis = [
            "The first slice is inside the frozen matrix and has dataset/model/trigger/target/capability/baseline scope fixed.",
            "Run, artifact, validation, resource, and fallback contracts are machine-readable.",
            "The plan remains a minimal smoke contract and does not start the full matrix.",
        ]
    elif not missing and slice_ready:
        final_verdict = "Partially validated"
        recommendation = "进入 first-slice-plan-compression"
        basis = ["The first-slice shape exists, but at least one contract readiness check failed."]
    else:
        final_verdict = "Not validated"
        recommendation = "进入 first-slice-scope-closure"
        basis = ["Required first-slice scope or artifacts are missing."]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "missing_artifacts": missing,
        "slice_ready": slice_ready,
        "run_ready": run_ready,
        "artifact_ready": artifact_ready,
        "validation_ready": validation_ready,
        "resource_ready": resource_ready,
        "details_ready": details_ready,
        "no_expansion": no_expansion,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_first_slice_execution_plan_validated__partially_validated__not_validated",
        "primary_basis": basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": basis,
    }
    write_json(output_dir / "dualscope_first_slice_analysis_summary.json", analysis_summary)
    write_json(output_dir / "dualscope_first_slice_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "dualscope_first_slice_verdict.json").resolve()),
            "recommendation": str((output_dir / "dualscope_first_slice_next_step_recommendation.json").resolve()),
        },
    }
