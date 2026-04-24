"""Post-analysis for the DualScope experimental matrix freeze."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_experiment_matrix_common import write_json


POST_SCHEMA_VERSION = "dualscopellm/post-experimental-matrix-freeze-analysis/v1"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def _count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def post_dualscope_experimental_matrix_freeze_analysis(freeze_dir: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    required_names = [
        "dualscope_experimental_matrix_problem_definition.json",
        "dualscope_dataset_matrix.json",
        "dualscope_model_matrix.json",
        "dualscope_attack_trigger_matrix.json",
        "dualscope_target_behavior_matrix.json",
        "dualscope_capability_mode_matrix.json",
        "dualscope_baseline_matrix.json",
        "dualscope_ablation_matrix.json",
        "dualscope_robustness_matrix.json",
        "dualscope_metrics_contract.json",
        "dualscope_table_plan.json",
        "dualscope_resource_execution_plan.json",
        "dualscope_artifact_contract.json",
        "dualscope_experimental_matrix_freeze_summary.json",
        "dualscope_experimental_matrix_freeze_details.jsonl",
        "dualscope_experimental_matrix_freeze_report.md",
    ]
    missing = [name for name in required_names if not (freeze_dir / name).exists()]

    datasets = _load_json(freeze_dir / "dualscope_dataset_matrix.json")
    models = _load_json(freeze_dir / "dualscope_model_matrix.json")
    triggers = _load_json(freeze_dir / "dualscope_attack_trigger_matrix.json")
    targets = _load_json(freeze_dir / "dualscope_target_behavior_matrix.json")
    capabilities = _load_json(freeze_dir / "dualscope_capability_mode_matrix.json")
    baselines = _load_json(freeze_dir / "dualscope_baseline_matrix.json")
    ablations = _load_json(freeze_dir / "dualscope_ablation_matrix.json")
    robustness = _load_json(freeze_dir / "dualscope_robustness_matrix.json")
    metrics = _load_json(freeze_dir / "dualscope_metrics_contract.json")
    tables = _load_json(freeze_dir / "dualscope_table_plan.json")
    resources = _load_json(freeze_dir / "dualscope_resource_execution_plan.json")
    summary = _load_json(freeze_dir / "dualscope_experimental_matrix_freeze_summary.json")
    detail_count = _count_jsonl(freeze_dir / "dualscope_experimental_matrix_freeze_details.jsonl")

    dataset_ready = datasets["dataset_count"] >= 4 and sum(row["used_in_main_table"] for row in datasets["datasets"]) >= 3
    model_ready = models["model_count"] >= 3 and sum(row["whether_main_experiment"] for row in models["models"]) >= 2
    trigger_ready = triggers["trigger_count"] >= 4 and sum(row["whether_main_matrix"] for row in triggers["triggers"]) >= 3
    target_ready = targets["target_count"] >= 3 and sum(row["used_in_main"] for row in targets["targets"]) >= 2
    capability_ready = {row["capability_mode"] for row in capabilities["capability_modes"]} == {
        "with_logprobs",
        "without_logprobs",
    }
    baseline_ready = baselines["baseline_count"] >= 5
    ablation_ready = ablations["ablation_count"] >= 15
    robustness_ready = robustness["robustness_count"] >= 7
    metrics_ready = metrics["metric_count"] >= 18
    table_ready = tables["table_count"] >= 5
    resource_ready = resources["resource_boundary"] == "2 x RTX 3090" and bool(resources["recommended_first_execution_slice"])
    details_ready = detail_count == summary["details_row_count"] and detail_count >= 30
    no_forbidden_expansion = not summary["full_matrix_executed"] and not summary["route_c_chain_continued"] and not summary["reasoning_branch_included"]

    checks = {
        "missing_artifacts": missing,
        "dataset_ready": dataset_ready,
        "model_ready": model_ready,
        "trigger_ready": trigger_ready,
        "target_ready": target_ready,
        "capability_ready": capability_ready,
        "baseline_ready": baseline_ready,
        "ablation_ready": ablation_ready,
        "robustness_ready": robustness_ready,
        "metrics_ready": metrics_ready,
        "table_ready": table_ready,
        "resource_ready": resource_ready,
        "details_ready": details_ready,
        "no_forbidden_expansion": no_forbidden_expansion,
    }

    if not missing and all(value for key, value in checks.items() if key != "missing_artifacts"):
        final_verdict = "Experimental matrix freeze validated"
        recommendation = "进入 dualscope-minimal-first-slice-execution-plan"
        basis = [
            "Dataset/model/trigger/target/capability matrices are frozen with future-only entries separated from the minimum matrix.",
            "Baseline, ablation, robustness, metrics, table, cost, resource, and artifact contracts are machine-readable.",
            "No full matrix execution, route_c continuation, reasoning branch expansion, or benchmark truth change occurred.",
        ]
    elif not missing and dataset_ready and model_ready and baseline_ready:
        final_verdict = "Partially validated"
        recommendation = "进入 experimental-matrix-freeze-compression"
        basis = ["The matrix shape exists, but at least one validation readiness criterion remains incomplete."]
    else:
        final_verdict = "Not validated"
        recommendation = "进入 dataset-model-trigger-matrix-closure"
        basis = ["Required artifacts or core matrix contracts are missing or incomplete."]

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "task_name": "dualscope-experimental-matrix-freeze",
        **checks,
        "detail_count": detail_count,
        "final_verdict": final_verdict,
    }
    verdict = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_experimental_matrix_freeze_validated__partially_validated__not_validated",
        "primary_basis": basis,
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": POST_SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": basis,
        "do_not_do_yet": [
            "run_full_experimental_matrix",
            "expand_model_axis",
            "expand_budget",
            "continue_route_c_199_plus",
            "revive_reasoning_branch",
        ],
    }

    write_json(output_dir / "dualscope_experimental_matrix_freeze_analysis_summary.json", analysis_summary)
    write_json(output_dir / "dualscope_experimental_matrix_freeze_verdict.json", verdict)
    write_json(output_dir / "dualscope_experimental_matrix_freeze_next_step_recommendation.json", recommendation_payload)
    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / "dualscope_experimental_matrix_freeze_analysis_summary.json").resolve()),
            "verdict": str((output_dir / "dualscope_experimental_matrix_freeze_verdict.json").resolve()),
            "recommendation": str(
                (output_dir / "dualscope_experimental_matrix_freeze_next_step_recommendation.json").resolve()
            ),
        },
    }
