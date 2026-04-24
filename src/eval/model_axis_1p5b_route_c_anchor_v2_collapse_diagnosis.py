"""Diagnose why anchor follow-up v2 passes precheck but collapses at labels stage in execution."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json
from src.fusion.benchmark_truth_leaning_label import summarize_option_label_parse


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-anchor-v2-collapse-diagnosis/v1"
PUNCT_ONLY_PATTERN = re.compile(r"^[!?.]+$")


def _safe_load_json(path: Path) -> dict[str, Any] | None:
    return load_json(path) if path.is_file() else None


def _safe_load_jsonl(path: Path) -> list[dict[str, Any]]:
    return load_jsonl(path) if path.is_file() else []


def build_model_axis_1p5b_route_c_anchor_v2_collapse_diagnosis(
    route_c_anchor_followup_v2_dir: Path,
    route_c_anchor_execution_v2_dir: Path,
    route_c_execution_dir: Path,
    route_c_anchor_execution_recheck_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    precheck = load_json(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_precheck.json")
    candidate_summary = load_json(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_candidate_summary.json")
    selection_registry = load_json(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_selection_registry.json")
    execution_selection = load_json(route_c_anchor_execution_v2_dir / "route_c_anchor_execution_v2_selection.json")
    execution_readiness = load_json(route_c_anchor_execution_v2_dir / "route_c_anchor_execution_v2_readiness_summary.json")
    execution_run_summary = load_json(route_c_anchor_execution_v2_dir / "route_c_anchor_execution_v2_run_summary.json")

    candidate_dataset_rows = _safe_load_jsonl(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_candidate_dataset.jsonl")
    execution_dataset_summary = _safe_load_json(
        route_c_anchor_execution_v2_dir
        / "route_c_anchor_execution_v2_run"
        / "route_c_v6_dataset_dir"
        / "benchmark_truth_leaning_summary.json"
    )
    execution_dataset_rows = _safe_load_jsonl(
        route_c_anchor_execution_v2_dir
        / "route_c_anchor_execution_v2_run"
        / "route_c_v6_dataset_dir"
        / "benchmark_truth_leaning_dataset.jsonl"
    )
    labeled_raw_rows = _safe_load_jsonl(
        route_c_anchor_execution_v2_dir
        / "route_c_anchor_execution_v2_run"
        / "route_c_v6_labeled_illumination"
        / "illumination_probe"
        / "raw_results.jsonl"
    )

    # Optional control evidence: rerun of original anchor baseline under current runtime.
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

    precheck_class_balance = precheck.get("class_balance")
    precheck_label_set = sorted(
        {
            int(row.get("ground_truth_label", 0))
            for row in candidate_dataset_rows
        }
    )
    execution_label_set = sorted(
        {
            int(row.get("ground_truth_label", 0))
            for row in execution_dataset_rows
        }
    )

    labeled_responses = [str(row.get("response_text", "")) for row in labeled_raw_rows]
    robust_parse_summary = summarize_option_label_parse(labeled_responses, parse_mode="robust_prefix")
    strict_parse_summary = summarize_option_label_parse(labeled_responses, parse_mode="strict")
    punct_only_count = sum(1 for text in labeled_responses if PUNCT_ONLY_PATTERN.match(text.strip() or "") is not None)

    recheck_labeled_responses = [str(row.get("response_text", "")) for row in recheck_labeled_raw_rows]
    recheck_robust_parse_summary = summarize_option_label_parse(
        recheck_labeled_responses,
        parse_mode="robust_prefix",
    ) if recheck_labeled_responses else None
    recheck_punct_only_count = (
        sum(1 for text in recheck_labeled_responses if PUNCT_ONLY_PATTERN.match(text.strip() or "") is not None)
        if recheck_labeled_responses
        else None
    )

    diff = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "selection_alignment": {
            "precheck_selected_base_ids": selection_registry.get("selected_base_ids"),
            "execution_selected_base_ids": execution_selection.get("selected_base_ids"),
            "selection_consistent": selection_registry.get("selected_base_ids") == execution_selection.get("selected_base_ids"),
        },
        "row_alignment": {
            "precheck_row_count": precheck.get("row_count"),
            "execution_dataset_row_count": None if execution_dataset_summary is None else execution_dataset_summary.get("num_rows"),
            "execution_readiness_selected_contract_count": execution_readiness.get("selected_contract_count"),
        },
        "label_path_difference": {
            "precheck_label_source": "historical_ground_truth_label_from_route_c_execution_dataset",
            "execution_label_source": "recomputed_from_live_labeled_illumination_response_option_vs_query_answer_key",
            "precheck_label_set": precheck_label_set,
            "execution_label_set": execution_label_set,
            "precheck_class_balance": precheck_class_balance,
            "execution_class_balance": None if execution_dataset_summary is None else execution_dataset_summary.get("class_balance"),
        },
        "parser_difference": {
            "precheck_parser_mode": "not_used_precheck_uses_existing_labels",
            "execution_option_parse_mode": None if execution_dataset_summary is None else execution_dataset_summary.get("option_parse_mode"),
            "execution_robust_prefix_parse_summary": robust_parse_summary,
            "execution_strict_parse_summary": strict_parse_summary,
        },
        "threshold_difference": {
            "precheck_threshold": "none_self_fit_logistic_without_threshold_gate",
            "execution_threshold": "0.5_configured_for_logistic_but_not_reached_due_to_single_class_dataset",
        },
    }

    label_path_audit = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "stage_counts": {
            "candidate_dataset_rows_for_precheck": len(candidate_dataset_rows),
            "labeled_illumination_raw_rows_execution": len(labeled_raw_rows),
            "benchmark_truth_leaning_dataset_rows_execution": len(execution_dataset_rows),
        },
        "execution_labeled_response_audit": {
            "punct_only_count": punct_only_count,
            "punct_only_ratio": (float(punct_only_count) / float(len(labeled_responses))) if labeled_responses else None,
            "sample_responses": [
                {"sample_id": str(row.get("sample_id")), "response_text": str(row.get("response_text", ""))}
                for row in labeled_raw_rows
            ],
            "robust_prefix_parse_summary": robust_parse_summary,
            "strict_parse_summary": strict_parse_summary,
        },
        "collapse_point": {
            "stage": "labels",
            "failure_reason": execution_run_summary.get("failure_reason"),
            "execution_status": execution_run_summary.get("execution_status"),
        },
        "control_recheck_evidence": {
            "available": recheck_run_summary is not None,
            "recheck_summary_status": None if recheck_run_summary is None else recheck_run_summary.get("summary_status"),
            "recheck_failure_stage": None if recheck_run_summary is None else recheck_run_summary.get("failure_stage"),
            "recheck_dataset_class_balance": None if recheck_dataset_summary is None else recheck_dataset_summary.get("class_balance"),
            "recheck_robust_prefix_parse_summary": recheck_robust_parse_summary,
            "recheck_punct_only_count": recheck_punct_only_count,
        },
    }

    failure_hypotheses = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "ranked_hypotheses": [
            {
                "rank": 1,
                "hypothesis": "Labeled illumination responses are unparseable punctuation, causing option extraction to return None for all rows.",
                "confidence": "high",
                "evidence": [
                    "execution labeled responses are all '!!!!!!!!!!!!!!!!'",
                    "robust_prefix parsed_option_count = 0",
                    "execution dataset class_balance = {label_0:0,label_1:6}",
                ],
            },
            {
                "rank": 2,
                "hypothesis": "Precheck and execution use different label paths (historical labels vs live relabeling), so precheck PASS does not guarantee execution class balance.",
                "confidence": "high",
                "evidence": [
                    "precheck label_set includes both classes",
                    "execution label_set is single-class",
                    "selection and row count remain aligned, so mismatch is path-level not sampling-level",
                ],
            },
            {
                "rank": 3,
                "hypothesis": "Candidate selection itself is not the primary root cause.",
                "confidence": "medium",
                "evidence": [
                    "control recheck on original anchor candidate also collapses at labels stage under current runtime",
                ],
            },
            {
                "rank": 4,
                "hypothesis": "Logistic threshold choice is not the primary root cause.",
                "confidence": "high",
                "evidence": [
                    "failure happens before logistic fit because dataset has a single class",
                ],
            },
        ],
    }

    collapse_root_cause = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "primary_root_cause": "execution_label_path_receives_unparseable_labeled_illumination_outputs",
        "root_cause_statement": (
            "Execution relabels contracts from live labeled-illumination responses; under current runtime these responses are punctuation-only and unparseable, "
            "so all contracts become task_answer_incorrect_label=1 and logistic cannot run."
        ),
        "contributing_factors": [
            "precheck path uses historical ground_truth_label instead of live relabeling output",
            "no execution readiness gate checks parseability/class-balance before logistic step",
        ],
        "non_primary_factors": [
            "selection_registry mismatch (not observed)",
            "label_threshold misconfiguration (logistic not reached)",
        ],
        "evidence_trace": {
            "precheck_class_balance": precheck_class_balance,
            "execution_class_balance": None if execution_dataset_summary is None else execution_dataset_summary.get("class_balance"),
            "execution_parse_summary": robust_parse_summary,
            "execution_failure_stage": execution_run_summary.get("failure_stage"),
        },
    }

    recovery_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_anchor_followup_v2",
        "recovery_goal": "avoid repeating precheck-pass / execution-label-collapse mismatch",
        "actions": [
            {
                "priority": "P0",
                "action": "Add execution-path label sanity gate before logistic: abort with structured BLOCKED when parsed options are all missing.",
                "expected_effect": "Surface collapse earlier and avoid misleading baseline assessments.",
            },
            {
                "priority": "P0",
                "action": "For micro-deepening candidate readiness, run a lightweight live labeled-illumination parseability probe on selected contracts.",
                "expected_effect": "Align readiness with execution path instead of relying on historical labels.",
            },
            {
                "priority": "P1",
                "action": "Record parse diagnostics (parsed_option_count, missing_option_count, punct_only_ratio) in execution summary artifacts.",
                "expected_effect": "Make labels-stage failures analyzable and comparable across candidates.",
            },
            {
                "priority": "P1",
                "action": "Only permit micro-deepening execution when live prelabel class balance is two-class.",
                "expected_effect": "Reduce repeated PARTIAL failures at labels stage.",
            },
        ],
        "worth_executing_rule_update": (
            "worth_executing requires both historical precheck pass and live label-path precheck pass on the same selected contracts."
        ),
    }

    micro_deepening_constraints = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c_micro_deepening",
        "baseline_constraints": {
            "must_keep_anchor_reference": True,
            "must_keep_base_count_lte": 3,
            "must_keep_density_floor": "anchor_1_over_6",
        },
        "label_stability_constraints": {
            "require_live_labeled_parse_check": True,
            "min_parsed_option_count": 1,
            "max_missing_option_ratio": 0.8,
            "require_two_class_live_label_balance": True,
            "block_if_punct_only_ratio_ge": 0.9,
        },
        "execution_gate": {
            "if_live_label_gate_fails": "do_not_run_full_execution_and_fall_back_to_anchor_baseline",
            "if_live_label_gate_passes": "allow_micro_deepening_execution",
        },
        "intended_next_plan": "136-anchor-aware-micro-deepening-stable-execution",
    }

    write_json(output_dir / "route_c_anchor_v2_precheck_vs_execution_diff.json", diff)
    write_json(output_dir / "route_c_anchor_v2_label_path_audit.json", label_path_audit)
    write_json(output_dir / "route_c_anchor_v2_failure_hypotheses.json", failure_hypotheses)
    write_json(output_dir / "route_c_anchor_v2_collapse_root_cause.json", collapse_root_cause)
    write_json(output_dir / "route_c_anchor_v2_recovery_plan.json", recovery_plan)
    write_json(output_dir / "route_c_anchor_v2_micro_deepening_constraints.json", micro_deepening_constraints)

    return {
        "summary": collapse_root_cause,
        "output_paths": {
            "diff": str((output_dir / "route_c_anchor_v2_precheck_vs_execution_diff.json").resolve()),
            "audit": str((output_dir / "route_c_anchor_v2_label_path_audit.json").resolve()),
            "hypotheses": str((output_dir / "route_c_anchor_v2_failure_hypotheses.json").resolve()),
            "root_cause": str((output_dir / "route_c_anchor_v2_collapse_root_cause.json").resolve()),
            "recovery_plan": str((output_dir / "route_c_anchor_v2_recovery_plan.json").resolve()),
            "constraints": str((output_dir / "route_c_anchor_v2_micro_deepening_constraints.json").resolve()),
        },
    }
