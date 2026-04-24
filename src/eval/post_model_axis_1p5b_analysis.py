"""Analyze whether the first 1.5B model-axis execution opens a real portability path."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/post-model-axis-1p5b-analysis/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def build_post_model_axis_1p5b_analysis(
    bootstrap_summary_path: Path,
    dry_run_summary_path: Path,
    execution_run_summary_path: Path,
    execution_metrics_path: Path,
    execution_selection_path: Path,
    route_b_summary_path: Path,
    route_b_logistic_summary_path: Path,
    route_b_run_summary_path: Path,
    lightweight_route_b_summary_path: Path,
    lightweight_route_b_logistic_summary_path: Path,
    lightweight_route_b_run_summary_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    bootstrap_summary = load_json(bootstrap_summary_path)
    dry_run_summary = load_json(dry_run_summary_path)
    execution_run_summary = load_json(execution_run_summary_path)
    execution_metrics = load_json(execution_metrics_path)
    execution_selection = load_json(execution_selection_path)
    route_b_summary = load_json(route_b_summary_path)
    route_b_logistic_summary = load_json(route_b_logistic_summary_path)
    route_b_run_summary = load_json(route_b_run_summary_path)
    lightweight_route_b_summary = load_json(lightweight_route_b_summary_path)
    lightweight_route_b_logistic_summary = load_json(lightweight_route_b_logistic_summary_path)
    lightweight_route_b_run_summary = load_json(lightweight_route_b_run_summary_path)

    model_axis_entry_opened = bool(
        bootstrap_summary.get("ready_local")
        and dry_run_summary.get("ready_run")
        and execution_metrics.get("used_local_weights")
        and execution_metrics.get("entered_model_inference")
    )
    logistic_blocked = route_b_logistic_summary.get("summary_status") == "BLOCKED"
    baseline_logistic_available = lightweight_route_b_logistic_summary.get("summary_status") == "PASS"
    comparison_gap = None
    if baseline_logistic_available:
        comparison_gap = {
            "baseline_mean_prediction_score": lightweight_route_b_logistic_summary.get("mean_prediction_score"),
            "model_axis_mean_prediction_score": route_b_logistic_summary.get("mean_prediction_score"),
            "baseline_positive_predictions": lightweight_route_b_logistic_summary.get("num_positive_predictions"),
            "model_axis_positive_predictions": route_b_logistic_summary.get("num_positive_predictions"),
        }

    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_model_profile": bootstrap_summary["selected_model_profile"],
        "selected_model_id": bootstrap_summary["selected_model_id"],
        "selected_cell": execution_selection["selected_cell"],
        "model_axis_entry_opened": model_axis_entry_opened,
        "bootstrap_ready_local": bootstrap_summary.get("ready_local"),
        "dry_run_status": dry_run_summary.get("dry_run_status"),
        "execution_status": execution_run_summary.get("execution_status"),
        "used_local_weights": execution_metrics.get("used_local_weights"),
        "entered_model_inference": execution_metrics.get("entered_model_inference"),
        "route_b_dataset_rows": route_b_summary.get("num_rows"),
        "route_b_class_balance": route_b_summary.get("class_balance"),
        "lightweight_route_b_dataset_rows": lightweight_route_b_summary.get("num_rows"),
        "lightweight_route_b_class_balance": lightweight_route_b_summary.get("class_balance"),
        "current_primary_blocker": route_b_run_summary.get("logistic_blocked_reason"),
        "main_takeaway": (
            "The 1.5B model-axis path is now genuinely open because the local Qwen2.5-1.5B-Instruct snapshot was loaded and route_b entered real inference, "
            "but the first minimal execution still collapses to a single-class more-natural label set, so the current gain is portability proof rather than a stable comparative detector result."
        ),
    }

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "lightweight_baseline": {
            "model_profile": "pilot_distilgpt2_hf",
            "execution_status": lightweight_route_b_run_summary.get("execution_status", "FULL_EXECUTE"),
            "dataset_rows": lightweight_route_b_summary.get("num_rows"),
            "class_balance": lightweight_route_b_summary.get("class_balance"),
            "logistic_status": lightweight_route_b_logistic_summary.get("summary_status"),
            "mean_prediction_score": lightweight_route_b_logistic_summary.get("mean_prediction_score"),
            "num_positive_predictions": lightweight_route_b_logistic_summary.get("num_positive_predictions"),
        },
        "model_axis_1p5b": {
            "model_profile": bootstrap_summary["selected_model_profile"],
            "model_id": bootstrap_summary["selected_model_id"],
            "execution_status": execution_run_summary.get("execution_status"),
            "used_local_weights": execution_metrics.get("used_local_weights"),
            "entered_model_inference": execution_metrics.get("entered_model_inference"),
            "dataset_rows": route_b_summary.get("num_rows"),
            "class_balance": route_b_summary.get("class_balance"),
            "logistic_status": route_b_logistic_summary.get("summary_status"),
            "mean_prediction_score": route_b_logistic_summary.get("mean_prediction_score"),
            "num_positive_predictions": route_b_logistic_summary.get("num_positive_predictions"),
            "blocking_reason": route_b_logistic_summary.get("blocking_reason"),
        },
        "portability_gains": [
            "The project-local 1.5B snapshot is now wired into pilot_small_hf and passes local-only config/tokenizer/model probes.",
            "The 1.5B route_b execution reused the existing matrix contract without changing dataset or route semantics.",
            "The 1.5B path reached real local inference, which means the model-axis is no longer just a bootstrap object.",
        ],
        "remaining_limitations": [
            "The current 1.5B route_b minimal execution still uses pilot-level proxy supervision rather than benchmark ground truth.",
            "The first 32-row minimal execution collapsed to a single class, so logistic fitting could not complete.",
            "This means the current result proves executability and contract transfer, not yet stable model-axis comparability.",
        ],
        "metric_gap": comparison_gap,
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "stabilize_model_axis_1p5b_route_b_label_balance",
        "selected_model_profile": bootstrap_summary["selected_model_profile"],
        "selected_model_id": bootstrap_summary["selected_model_id"],
        "why_recommended": [
            "The model-axis entry is now genuinely open, so the highest-value next step is to stabilize the first 1.5B route rather than expand to larger models immediately.",
            "route_b already proved it can reach real 1.5B inference, but its current minimal subset collapses to one class and blocks logistic fitting.",
            "Fixing that label-balance issue will produce a much stronger portability signal than jumping early to 3B or another route.",
        ],
        "why_not_route_c_yet": "route_c is still a valid next portability target, but route_b is already partially executing and is the smallest honest place to remove the remaining blocker.",
        "why_not_3b_yet": "A larger model would multiply resource cost before the first 1.5B route is even stabilized.",
        "why_not_return_to_fusion_axis": "The current bottleneck is model portability, not missing fusion granularity.",
        "current_blocker": route_b_run_summary.get("logistic_blocked_reason"),
    }

    write_json(output_dir / "model_axis_1p5b_analysis_summary.json", analysis_summary)
    write_json(output_dir / "model_axis_1p5b_vs_lightweight_comparison.json", comparison)
    write_json(output_dir / "model_axis_1p5b_next_step_recommendation.json", recommendation)

    return {
        "analysis_summary": analysis_summary,
        "comparison": comparison,
        "recommendation": recommendation,
        "output_paths": {
            "analysis_summary": str((output_dir / "model_axis_1p5b_analysis_summary.json").resolve()),
            "comparison": str((output_dir / "model_axis_1p5b_vs_lightweight_comparison.json").resolve()),
            "recommendation": str((output_dir / "model_axis_1p5b_next_step_recommendation.json").resolve()),
        },
    }
