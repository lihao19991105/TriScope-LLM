"""Build a controlled micro-deepening candidate with live label-gate checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json
from src.fusion.benchmark_truth_leaning_label import summarize_option_label_parse


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-micro-deepening/v1"


def _safe_load_json(path: Path) -> dict[str, Any] | None:
    return load_json(path) if path.is_file() else None


def _safe_load_jsonl(path: Path) -> list[dict[str, Any]]:
    return load_jsonl(path) if path.is_file() else []


def build_model_axis_1p5b_route_c_micro_deepening(
    route_c_anchor_followup_dir: Path,
    route_c_anchor_execution_dir: Path,
    route_c_anchor_execution_recheck_dir: Path,
    route_c_refined_execution_dir: Path,
    collapse_diagnosis_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    anchor_registry = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_selection_registry.json")
    anchor_summary = load_json(route_c_anchor_followup_dir / "route_c_anchor_followup_candidate_summary.json")
    anchor_run_summary = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_run_summary.json")
    anchor_metrics = load_json(route_c_anchor_execution_dir / "route_c_anchor_execution_metrics.json")
    refined_metrics = load_json(route_c_refined_execution_dir / "route_c_refined_execution_metrics.json")
    collapse_constraints = load_json(collapse_diagnosis_dir / "route_c_anchor_v2_micro_deepening_constraints.json")

    recheck_run_summary = _safe_load_json(route_c_anchor_execution_recheck_dir / "route_c_anchor_execution_run_summary.json")
    recheck_dataset_summary = _safe_load_json(
        route_c_anchor_execution_recheck_dir
        / "route_c_anchor_execution_run"
        / "route_c_v6_dataset_dir"
        / "benchmark_truth_leaning_summary.json"
    )
    recheck_labeled_raw_rows = _safe_load_jsonl(
        route_c_anchor_execution_recheck_dir
        / "route_c_anchor_execution_run"
        / "route_c_v6_labeled_illumination"
        / "illumination_probe"
        / "raw_results.jsonl"
    )

    labeled_responses = [str(row.get("response_text", "")) for row in recheck_labeled_raw_rows]
    parse_summary = summarize_option_label_parse(labeled_responses, parse_mode="robust_prefix") if labeled_responses else None

    selected_base_ids = [str(item) for item in anchor_registry.get("selected_base_ids", [])]
    class_balance = anchor_summary.get("class_balance")
    anchor_density = float(anchor_metrics.get("anchor_density", 0.0) or 0.0)
    refined_density = float(refined_metrics.get("refined_density", 0.0) or 0.0)

    label_constraints = collapse_constraints.get("label_stability_constraints", {})
    min_parsed_option_count = int(label_constraints.get("min_parsed_option_count", 1))
    max_missing_option_ratio = float(label_constraints.get("max_missing_option_ratio", 0.8))
    require_two_class_live = bool(label_constraints.get("require_two_class_live_label_balance", True))

    recheck_class_balance = None if recheck_dataset_summary is None else recheck_dataset_summary.get("class_balance")
    recheck_two_class = bool(
        recheck_class_balance is not None
        and int(recheck_class_balance.get("label_0", 0) or 0) > 0
        and int(recheck_class_balance.get("label_1", 0) or 0) > 0
    )
    parsed_option_count = 0 if parse_summary is None else int(parse_summary.get("parsed_option_count", 0) or 0)
    missing_option_ratio = (
        None
        if parse_summary is None or int(parse_summary.get("row_count", 0) or 0) == 0
        else float(parse_summary.get("missing_option_count", 0) or 0) / float(parse_summary.get("row_count", 0) or 1)
    )

    live_label_gate_pass = bool(
        parse_summary is not None
        and parsed_option_count >= min_parsed_option_count
        and (missing_option_ratio is not None and missing_option_ratio <= max_missing_option_ratio)
        and ((not require_two_class_live) or recheck_two_class)
    )

    strategy = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_micro_deepening",
        "strategy_name": "anchor_baseline_with_live_label_gate",
        "difference_vs_132_133": {
            "selection_change": "no_additional_neighbor_swap; revert to anchor baseline candidate",
            "new_guard": "live_labeled_parse_and_class_balance_gate_before_full_execution",
            "why": "135 shows labels-stage collapse is path-level under current runtime, so stability gate is prioritized over expansion.",
        },
        "fallback_rule": "if live_label_gate fails, keep anchor-aware baseline and block micro execution",
        "success_criteria": [
            "live label parse gate passes",
            "live label class balance has two classes",
            "density floor remains at anchor 1/6",
        ],
    }
    selection_registry = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_micro_deepening",
        "selection_source": str((route_c_anchor_followup_dir / "route_c_anchor_followup_selection_registry.json").resolve()),
        "selected_base_ids": selected_base_ids,
        "selection_strategy": "anchor_baseline_with_live_label_gate",
    }
    candidate_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_micro_deepening",
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": anchor_summary.get("selected_contract_count"),
        "class_balance": class_balance,
        "anchor_density": anchor_density,
        "refined_density": refined_density,
        "candidate_density": anchor_summary.get("anchor_followup_density"),
        "density_vs_anchor": 1.0,
        "density_vs_refined": (anchor_density / refined_density) if refined_density > 0 else None,
    }

    readiness_summary = {
        "summary_status": "PASS" if live_label_gate_pass else "PASS_WITH_LIMITATIONS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_micro_deepening",
        "ready_for_execution": live_label_gate_pass,
        "selected_base_ids": selected_base_ids,
        "live_label_gate": {
            "parsed_option_count": parsed_option_count,
            "missing_option_ratio": missing_option_ratio,
            "recheck_class_balance": recheck_class_balance,
            "recheck_two_class": recheck_two_class,
            "gate_pass": live_label_gate_pass,
        },
        "recheck_reference": str(route_c_anchor_execution_recheck_dir.resolve()),
        "block_reason": (
            "live label gate failed; execution likely to collapse at labels stage" if not live_label_gate_pass else None
        ),
    }

    if live_label_gate_pass:
        summary_status = "PASS_WITH_LIMITATIONS"
        execution_status = "PASS_WITH_LIMITATIONS"
        failure_stage = "not_run_in_this_step"
        failure_reason = "Gate passed but full rerun is deferred; use dedicated execution command if needed."
        micro_assessment = "baseline_preserved_but_no_gain"
        labels_collapse_avoided = True
    else:
        summary_status = "BLOCKED"
        execution_status = "BLOCKED"
        failure_stage = "labels_precheck_gate"
        failure_reason = "Live labeled parse/class-balance gate failed under current runtime evidence."
        micro_assessment = "still_label_fragile"
        labels_collapse_avoided = False

    run_summary = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_micro_deepening",
        "execution_status": execution_status,
        "used_local_weights": None,
        "entered_model_inference": None,
        "class_balance": recheck_class_balance,
        "num_rows": None if recheck_dataset_summary is None else recheck_dataset_summary.get("num_rows"),
        "num_predictions": None,
        "failure_stage": failure_stage,
        "failure_reason": failure_reason,
        "density_vs_anchor": None,
        "density_vs_refined": None,
        "reference_anchor_preserved": None if recheck_run_summary is None else recheck_run_summary.get("reference_anchor_preserved"),
        "labels_collapse_avoided": labels_collapse_avoided,
        "micro_deepening_assessment": micro_assessment,
    }
    metrics = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "class_balance": recheck_class_balance,
        "num_rows": None if recheck_dataset_summary is None else recheck_dataset_summary.get("num_rows"),
        "num_predictions": None,
        "anchor_density": anchor_density,
        "refined_density": refined_density,
        "micro_density": None,
        "labels_collapse_avoided": labels_collapse_avoided,
    }
    model_summary_placeholder = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "message": "No full micro-deepening execution summary available because live gate blocked execution.",
    }
    model_logistic_placeholder = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "message": "No logistic summary available because live gate blocked execution.",
    }
    density_comparison = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "anchor_density": anchor_density,
        "refined_density": refined_density,
        "micro_density": None,
        "density_vs_anchor": None,
        "density_vs_refined": None,
    }
    positive_support_breakdown = {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "positive_support_count": None,
        "anchor_positive_support_count": len(anchor_run_summary.get("positive_support_sample_ids", []) or []),
        "incremental_positive_support_vs_anchor": None,
    }

    write_json(output_dir / "route_c_micro_deepening_strategy.json", strategy)
    write_json(output_dir / "route_c_micro_deepening_selection_registry.json", selection_registry)
    write_json(output_dir / "route_c_micro_deepening_candidate_summary.json", candidate_summary)
    write_json(output_dir / "route_c_micro_deepening_readiness_summary.json", readiness_summary)
    write_json(output_dir / "route_c_micro_deepening_run_summary.json", run_summary)
    write_json(output_dir / "route_c_micro_deepening_metrics.json", metrics)
    write_json(output_dir / "model_axis_1p5b_route_c_micro_summary.json", model_summary_placeholder)
    write_json(output_dir / "model_axis_1p5b_route_c_micro_logistic_summary.json", model_logistic_placeholder)
    write_json(output_dir / "route_c_micro_deepening_density_comparison.json", density_comparison)
    write_json(output_dir / "route_c_micro_positive_support_breakdown.json", positive_support_breakdown)

    return {
        "summary": run_summary,
        "output_paths": {
            "strategy": str((output_dir / "route_c_micro_deepening_strategy.json").resolve()),
            "selection": str((output_dir / "route_c_micro_deepening_selection_registry.json").resolve()),
            "candidate_summary": str((output_dir / "route_c_micro_deepening_candidate_summary.json").resolve()),
            "readiness": str((output_dir / "route_c_micro_deepening_readiness_summary.json").resolve()),
            "run_summary": str((output_dir / "route_c_micro_deepening_run_summary.json").resolve()),
            "metrics": str((output_dir / "route_c_micro_deepening_metrics.json").resolve()),
        },
    }
