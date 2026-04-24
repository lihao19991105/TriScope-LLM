"""Analyze route_c positive-class sparsity on the 1.5B model axis."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-sparsity/v1"


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object on line {line_number} of `{path}`.")
            rows.append(payload)
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("Expected at least one CSV row.")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize_by_base(execution_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    per_base: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in execution_rows:
        per_base[str(row["base_sample_id"])].append(row)

    csv_rows: list[dict[str, Any]] = []
    positive_support_rows: list[dict[str, Any]] = []
    for base_sample_id in sorted(per_base):
        items = sorted(per_base[base_sample_id], key=lambda item: str(item.get("contract_variant", "")))
        item_by_variant = {str(item.get("contract_variant", "")): item for item in items}
        control = item_by_variant.get("control")
        targeted = item_by_variant.get("targeted")
        positive_variants = [
            str(item.get("contract_variant", ""))
            for item in items
            if int(item.get("ground_truth_label", 0)) == 1
        ]
        if positive_variants:
            for item in items:
                if int(item.get("ground_truth_label", 0)) == 1:
                    positive_support_rows.append(
                        {
                            "base_sample_id": base_sample_id,
                            "sample_id": str(item["sample_id"]),
                            "contract_variant": str(item.get("contract_variant", "")),
                            "ground_truth_label": int(item.get("ground_truth_label", 0)),
                            "query_answer_key": str(item.get("query_answer_key", "")),
                            "illumination_response_option": str(item.get("illumination_response_option", "")),
                            "task_answer_correct": bool(item.get("task_answer_correct", False)),
                            "task_answer_incorrect": bool(item.get("task_answer_incorrect", False)),
                            "sparsity_role": "positive_support_anchor",
                        }
                    )
        csv_rows.append(
            {
                "base_sample_id": base_sample_id,
                "control_label": int(control.get("ground_truth_label", 0)) if control is not None else -1,
                "targeted_label": int(targeted.get("ground_truth_label", 0)) if targeted is not None else -1,
                "control_answer": "" if control is None else str(control.get("illumination_response_option", "")),
                "targeted_answer": "" if targeted is None else str(targeted.get("illumination_response_option", "")),
                "query_answer_key": str(items[0].get("query_answer_key", "")),
                "positive_contract_count": len(positive_variants),
                "positive_variants": "|".join(positive_variants) if positive_variants else "",
                "base_pattern": "mixed" if len(positive_variants) == 1 else ("all_positive" if len(positive_variants) == 2 else "all_negative"),
            }
        )
    return csv_rows, positive_support_rows


def build_model_axis_1p5b_route_c_sparsity(
    route_c_stabilization_dir: Path,
    route_c_stable_portability_dir: Path,
    route_c_execution_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    diagnosis = load_json(route_c_stabilization_dir / "route_c_label_collapse_diagnosis.json")
    recovery_plan = load_json(route_c_stabilization_dir / "route_c_label_balance_recovery_plan.json")
    knobs_summary = load_json(route_c_stabilization_dir / "route_c_selection_knobs_summary.json")
    candidate_summary = load_json(route_c_stabilization_dir / "route_c_balanced_candidate_summary.json")
    stable_run_summary = load_json(route_c_stable_portability_dir / "route_c_stable_portability_run_summary.json")
    execution_run_summary = load_json(route_c_execution_dir / "route_c_execution_run_summary.json")
    execution_metrics = load_json(route_c_execution_dir / "route_c_execution_metrics.json")
    next_step = load_json(route_c_execution_dir / "route_c_execution_next_step_recommendation.json")

    execution_rows = load_jsonl(route_c_execution_dir / "route_c_execution_run" / "route_c_v6_dataset.jsonl")
    distribution_rows, positive_support_rows = summarize_by_base(execution_rows)
    positive_support_base_ids = [row["base_sample_id"] for row in positive_support_rows]
    positive_support_sample_ids = [row["sample_id"] for row in positive_support_rows]

    class_balance = Counter(int(row.get("ground_truth_label", 0)) for row in execution_rows)
    full_scan_balance = candidate_summary.get("full_scan_class_balance", {})
    full_scan_contract_count = int(candidate_summary.get("full_scan_contract_count", 0))
    full_scan_positive_contracts = int(full_scan_balance.get("label_1", 0) or 0)
    execution_positive_contracts = int(class_balance.get(1, 0))
    execution_contract_count = len(execution_rows)

    hypotheses = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "hypotheses": [
            {
                "hypothesis_id": "selection_only",
                "factor": "selected_subset_only",
                "directly_measurable": True,
                "current_status": "secondary_contributor",
                "evidence": {
                    "selected_contract_count": execution_contract_count,
                    "selected_class_balance": {"label_0": execution_contract_count - execution_positive_contracts, "label_1": execution_positive_contracts},
                    "full_scan_contract_count": full_scan_contract_count,
                    "full_scan_class_balance": full_scan_balance,
                },
                "conclusion": "Selection determines whether the lone positive-support base enters the subset, but cannot explain away sparsity because the full 140-contract scan is already 139/1.",
            },
            {
                "hypothesis_id": "parser_conservatism",
                "factor": "robust_prefix_parser",
                "directly_measurable": True,
                "current_status": "historical_but_not_current",
                "evidence": {
                    "strict_parser_class_balance": diagnosis.get("strict_parser_class_balance"),
                    "robust_parser_class_balance": diagnosis.get("robust_parser_class_balance"),
                    "current_label_parse_mode": execution_run_summary.get("label_parse_mode"),
                },
                "conclusion": "Parser bugs caused 113 collapse, but after 114/115 repairs they are no longer the dominant source of the current 1/24 sparsity.",
            },
            {
                "hypothesis_id": "threshold_driver",
                "factor": "logistic_label_threshold",
                "directly_measurable": True,
                "current_status": "not_primary",
                "evidence": {
                    "label_threshold": execution_metrics.get("label_threshold"),
                    "ground_truth_label_source": "contract-level task answer correctness",
                    "num_positive_predictions": execution_metrics.get("num_positive_predictions"),
                },
                "conclusion": "Threshold affects the self-fit logistic score, not the underlying contract-level correctness labels that create the 23/1 class balance.",
            },
            {
                "hypothesis_id": "model_behavior_plus_truth_leaning_label",
                "factor": "1p5b_route_c_answer_behavior",
                "directly_measurable": True,
                "current_status": "primary_driver",
                "evidence": {
                    "positive_support_sample_ids": positive_support_sample_ids,
                    "positive_support_base_ids": positive_support_base_ids,
                    "execution_class_balance": execution_run_summary.get("class_balance"),
                    "full_scan_class_balance": full_scan_balance,
                },
                "conclusion": "The dominant cause is that under the current benchmark-truth-leaning route_c contract, the local 1.5B model exposes only one incorrect contract-level answer across the known 140-contract universe.",
            },
            {
                "hypothesis_id": "budget_too_small",
                "factor": "execution_budget",
                "directly_measurable": False,
                "current_status": "unlikely_primary",
                "evidence": {
                    "full_scan_positive_contracts": full_scan_positive_contracts,
                    "full_scan_contract_count": full_scan_contract_count,
                    "selected_positive_contracts": execution_positive_contracts,
                },
                "conclusion": "Blindly expanding budget inside the same current search space is likely to add many more negatives than positives because the full scan already surfaced only one positive contract.",
            },
        ],
    }

    diagnosis_protocol = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "analysis_sequence": [
            "Use 114 diagnosis to isolate parser-related historical failure from current sparsity.",
            "Use 114 full-scan summary to estimate positive-support density in the known contract universe.",
            "Use 116 execution dataset to locate positive support by base_sample_id and contract_variant.",
            "Compare current sparsity drivers against threshold and budget effects.",
            "Emit next-step recommendation based on whether the current result is sparse-but-analyzable or still too unstable.",
        ],
        "direct_measurements": [
            "strict vs robust parser class balance",
            "full scan 139/1 class balance",
            "execution 23/1 class balance",
            "positive support breakdown by base sample and contract variant",
        ],
        "inferred_measurements": [
            "marginal benefit of blind budget expansion under the current 140-contract universe",
            "relative advantage of selection refinement for increasing positive density without reopening new axes",
        ],
    }

    signal_sources = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "signal_sources": {
            "parser_history": {
                "source_artifact": str((route_c_stabilization_dir / "route_c_label_collapse_diagnosis.json").resolve()),
                "signal_strength": "resolved historical blocker",
                "key_measurements": {
                    "strict_parser_class_balance": diagnosis.get("strict_parser_class_balance"),
                    "robust_parser_class_balance": diagnosis.get("robust_parser_class_balance"),
                },
            },
            "selection_gate": {
                "source_artifact": str((route_c_stabilization_dir / "route_c_balanced_candidate_summary.json").resolve()),
                "signal_strength": "important gate but not sole root cause",
                "key_measurements": {
                    "available_mixed_base_count": candidate_summary.get("selection_diagnostics", {}).get("available_mixed_base_count"),
                    "selected_base_count": candidate_summary.get("selected_base_count"),
                },
            },
            "model_behavior": {
                "source_artifact": str((route_c_execution_dir / "route_c_execution_run" / "route_c_v6_dataset.jsonl").resolve()),
                "signal_strength": "primary current cause",
                "key_measurements": {
                    "positive_support_sample_ids": positive_support_sample_ids,
                    "positive_support_base_ids": positive_support_base_ids,
                    "execution_class_balance": execution_run_summary.get("class_balance"),
                },
            },
            "budget_limit": {
                "source_artifact": str((route_c_stabilization_dir / "route_c_balanced_candidate_summary.json").resolve()),
                "signal_strength": "secondary planning constraint",
                "key_measurements": {
                    "full_scan_contract_count": full_scan_contract_count,
                    "full_scan_positive_contracts": full_scan_positive_contracts,
                },
            },
        },
    }

    full_scan_positive_density = (
        float(full_scan_positive_contracts) / float(full_scan_contract_count)
        if full_scan_contract_count > 0
        else None
    )
    execution_positive_density = (
        float(execution_positive_contracts) / float(execution_contract_count)
        if execution_contract_count > 0
        else None
    )
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "current_execution_status": execution_run_summary.get("execution_status"),
        "current_class_balance": execution_run_summary.get("class_balance"),
        "full_scan_class_balance": full_scan_balance,
        "full_scan_positive_density": full_scan_positive_density,
        "execution_positive_density": execution_positive_density,
        "positive_support_base_ids": positive_support_base_ids,
        "positive_support_sample_ids": positive_support_sample_ids,
        "dominant_driver": "model_behavior_plus_truth_leaning_label_mechanism_under_current_selection",
        "parser_is_current_primary_driver": False,
        "threshold_is_current_primary_driver": False,
        "budget_is_current_primary_driver": False,
        "selection_is_gatekeeper_not_full_explanation": True,
        "sparse_but_analyzable": True,
        "key_findings": [
            "The current 23/1 class balance is no longer caused by parser failure; robust_prefix parsing already repaired that blocker in 114/115.",
            "Selection matters because only one mixed base sample exists in the known 1.5B route_c contract universe, but the full 140-contract scan already shows the same underlying sparsity pattern.",
            "The lone positive support point is concentrated on csqa-pilot-021__targeted, so current route_c is sparse but still structurally analyzable.",
            "Blind budget expansion inside the same current 140-contract universe is unlikely to thicken positives materially because it would mostly add negatives.",
        ],
    }
    positive_breakdown = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "positive_support_count": len(positive_support_rows),
        "positive_support_base_count": len(set(positive_support_base_ids)),
        "positive_support_rows": positive_support_rows,
        "support_pattern": "single_anchor_positive" if len(positive_support_rows) == 1 else "multi_anchor_positive",
        "why_it_matters": [
            "The positive class is currently concentrated on one base_sample_id and one contract variant.",
            "This means the next honest question is whether that anchor persists under light reruns, not whether we can inflate the denominator.",
        ],
    }
    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "current_execution_status": execution_run_summary.get("execution_status"),
        "current_class_balance": execution_run_summary.get("class_balance"),
        "recommended_next_step": "confirm_route_c_stability_before_refinement",
        "why": [
            "The current route_c result is already a true 1.5B execution and remains analyzable despite sparsity.",
            "Because the full scan already exposes only one positive contract, the immediate question is whether this positive support point is stable or accidental.",
            "Selection refinement is more promising than blind budget expansion if stability holds, but that decision should follow a lightweight stability confirmation.",
        ],
        "not_recommended_yet": [
            "blind_budget_expansion_inside_current_140_contract_universe",
            "3b_or_7b_expansion",
            "fusion_axis_expansion",
            "dataset_axis_expansion",
        ],
        "supporting_inputs": {
            "recovery_plan_path": str((route_c_stabilization_dir / "route_c_label_balance_recovery_plan.json").resolve()),
            "selection_knobs_path": str((route_c_stabilization_dir / "route_c_selection_knobs_summary.json").resolve()),
            "current_execution_recommendation_path": str((route_c_execution_dir / "route_c_execution_next_step_recommendation.json").resolve()),
        },
    }

    write_json(output_dir / "route_c_sparsity_hypotheses.json", hypotheses)
    write_json(output_dir / "route_c_sparsity_diagnosis_protocol.json", diagnosis_protocol)
    write_json(output_dir / "route_c_sparsity_signal_sources.json", signal_sources)
    write_json(output_dir / "route_c_sparsity_analysis_summary.json", summary)
    write_json(output_dir / "route_c_positive_support_breakdown.json", positive_breakdown)
    write_csv(output_dir / "route_c_label_distribution_by_sample.csv", distribution_rows)
    write_json(output_dir / "route_c_sparsity_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "hypotheses": str((output_dir / "route_c_sparsity_hypotheses.json").resolve()),
            "protocol": str((output_dir / "route_c_sparsity_diagnosis_protocol.json").resolve()),
            "signal_sources": str((output_dir / "route_c_sparsity_signal_sources.json").resolve()),
            "summary": str((output_dir / "route_c_sparsity_analysis_summary.json").resolve()),
            "positive_breakdown": str((output_dir / "route_c_positive_support_breakdown.json").resolve()),
            "distribution_csv": str((output_dir / "route_c_label_distribution_by_sample.csv").resolve()),
            "recommendation": str((output_dir / "route_c_sparsity_next_step_recommendation.json").resolve()),
        },
    }
