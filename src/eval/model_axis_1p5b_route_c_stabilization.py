"""Stabilize 1.5B route_c label balance under small-budget portability prechecks."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.fusion.benchmark_truth_leaning_label import (
    extract_option_label,
    summarize_option_label_parse,
)
from src.probes.illumination_probe import run_illumination_probe


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-c-stabilization/v1"


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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def summarize_class_balance(rows: list[dict[str, Any]], label_key: str) -> dict[str, int]:
    return {
        "label_0": sum(1 for row in rows if int(row.get(label_key, 0)) == 0),
        "label_1": sum(1 for row in rows if int(row.get(label_key, 0)) == 1),
    }


def collect_reference_base_profiles(reference_rows: list[dict[str, Any]]) -> dict[str, str]:
    label_sets: dict[str, set[int]] = defaultdict(set)
    for row in reference_rows:
        label_sets[str(row["base_sample_id"])].add(int(row.get("ground_truth_label", 0)))

    profiles: dict[str, str] = {}
    for base_id, labels in label_sets.items():
        if labels == {0}:
            profiles[base_id] = "all_label_0"
        elif labels == {1}:
            profiles[base_id] = "all_label_1"
        else:
            profiles[base_id] = "mixed"
    return profiles


def build_candidate_row(row: dict[str, Any]) -> dict[str, Any]:
    metadata = row.get("metadata", {})
    contract_metadata = metadata.get("contract_metadata", {})
    response_text = str(row.get("response_text", ""))
    answer_key = str(contract_metadata.get("query_answer_key", ""))
    strict_option = extract_option_label(response_text, parse_mode="strict")
    robust_option = extract_option_label(response_text, parse_mode="robust_prefix")

    strict_correct = bool(strict_option is not None and strict_option == answer_key)
    robust_correct = bool(robust_option is not None and robust_option == answer_key)

    return {
        "schema_version": SCHEMA_VERSION,
        "sample_id": str(row["sample_id"]),
        "base_sample_id": str(contract_metadata["base_sample_id"]),
        "contract_variant": str(contract_metadata["contract_variant"]),
        "query_answer_key": answer_key,
        "trigger_type": str(row.get("trigger_type", "")),
        "target_type": str(row.get("target_type", "")),
        "response_text": response_text,
        "strict_response_option": strict_option,
        "robust_response_option": robust_option,
        "strict_ground_truth_label": 0 if strict_correct else 1,
        "robust_ground_truth_label": 0 if robust_correct else 1,
        "strict_task_answer_correct": strict_correct,
        "robust_task_answer_correct": robust_correct,
    }


def select_balanced_base_ids(
    candidate_rows: list[dict[str, Any]],
    reasoning_rows: list[dict[str, Any]],
    target_base_budget: int,
) -> tuple[list[str], dict[str, Any]]:
    per_base_labels: dict[str, set[int]] = defaultdict(set)
    for row in candidate_rows:
        per_base_labels[str(row["base_sample_id"])].add(int(row["robust_ground_truth_label"]))

    mixed_bases = sorted(base_id for base_id, labels in per_base_labels.items() if labels == {0, 1})
    positive_only_bases = sorted(base_id for base_id, labels in per_base_labels.items() if labels == {1})
    negative_only_bases = sorted(base_id for base_id, labels in per_base_labels.items() if labels == {0})

    reasoning_order = [str(row["sample_id"]) for row in reasoning_rows]
    selected: list[str] = []

    for base_id in mixed_bases[:1]:
        selected.append(base_id)

    positive_target = 2 if len(positive_only_bases) >= 2 else len(positive_only_bases)
    for base_id in positive_only_bases[:positive_target]:
        if base_id not in selected:
            selected.append(base_id)

    for base_id in reasoning_order:
        if len(selected) >= max(1, target_base_budget):
            break
        if base_id in selected:
            continue
        if base_id not in per_base_labels:
            continue
        selected.append(base_id)

    selected_set = set(selected)
    selected_rows = [row for row in candidate_rows if str(row["base_sample_id"]) in selected_set]
    diagnostics = {
        "strategy": "prefer_mixed_then_positive_only_then_fill_reasoning_order",
        "target_base_budget": target_base_budget,
        "available_mixed_base_count": len(mixed_bases),
        "available_positive_only_base_count": len(positive_only_bases),
        "available_negative_only_base_count": len(negative_only_bases),
        "selected_base_count": len(selected),
        "selected_class_balance": summarize_class_balance(selected_rows, "robust_ground_truth_label"),
    }
    return selected, diagnostics


def diagnose_route_c_label_collapse(
    portability_selection: dict[str, Any],
    precheck_labeled_raw_rows: list[dict[str, Any]],
    reference_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    selected_base_ids = {
        str(row.get("metadata", {}).get("contract_metadata", {}).get("base_sample_id", ""))
        for row in precheck_labeled_raw_rows
        if row.get("metadata", {}).get("contract_metadata", {}).get("base_sample_id")
    }
    selected_reference_rows = [row for row in reference_rows if str(row.get("base_sample_id", "")) in selected_base_ids]

    selected_candidate_rows = [build_candidate_row(row) for row in precheck_labeled_raw_rows]
    strict_parse_summary = summarize_option_label_parse(
        [str(row.get("response_text", "")) for row in precheck_labeled_raw_rows],
        parse_mode="strict",
    )
    robust_parse_summary = summarize_option_label_parse(
        [str(row.get("response_text", "")) for row in precheck_labeled_raw_rows],
        parse_mode="robust_prefix",
    )

    strict_balance = summarize_class_balance(selected_candidate_rows, "strict_ground_truth_label")
    robust_balance = summarize_class_balance(selected_candidate_rows, "robust_ground_truth_label")
    reference_balance = summarize_class_balance(selected_reference_rows, "ground_truth_label")
    reference_profiles = collect_reference_base_profiles(selected_reference_rows)
    reference_profile_counts = Counter(reference_profiles.values())

    diagnosis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "current_precheck_budget": int(portability_selection.get("selected_base_sample_count", 0)),
        "selected_labeled_contract_count": len(selected_candidate_rows),
        "strict_parser_class_balance": strict_balance,
        "robust_parser_class_balance": robust_balance,
        "reference_selected_contract_class_balance": reference_balance,
        "reference_base_profile_counts": dict(reference_profile_counts),
        "direct_causes": [
            {
                "factor": "truth_leaning_label_parser",
                "evidence": {
                    "strict_parse_summary": strict_parse_summary,
                    "robust_parse_summary": robust_parse_summary,
                    "strict_parser_class_balance": strict_balance,
                    "robust_parser_class_balance": robust_balance,
                },
                "conclusion": "Primary bug. The strict parser misses prefix-form answers like 'AHuman:' and forces the full 24-contract precheck subset into label_1.",
            },
            {
                "factor": "sample_selection_under_1p5b",
                "evidence": {
                    "reference_selected_contract_class_balance": reference_balance,
                    "reference_base_profile_counts": dict(reference_profile_counts),
                    "robust_parser_class_balance": robust_balance,
                },
                "conclusion": "After parser repair, the current 12-base subset still collapses to all label_0 under the actual 1.5B outputs. Selection/budget must therefore adapt to real 1.5B behavior instead of the lightweight reference expectation.",
            },
        ],
        "route_b_reuse": {
            "reusable": [
                "robust prefix-aware option parsing for local answers",
                "explicit diagnosis artifacts that separate parser failure from selection failure",
            ],
            "not_directly_reusable": [
                "route_b sample-level balancing rules cannot be copied verbatim because route_c supervision is contract-level and its 1.5B answer pattern diverges from the lightweight reference subset.",
            ],
        },
        "current_failure_stage": "labels",
        "current_failure_reason": "Benchmark-truth-leaning dataset must contain at least two classes.",
    }

    recovery_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_recovery_path": "robust_prefix_label_parse_plus_full_labeled_scan_then_balanced_base_selection",
        "why_this_is_minimal": [
            "It keeps the current 1.5B model axis and route_c contract unchanged.",
            "It only repairs parser semantics and selection logic, without opening a new dataset or model axis.",
            "It uses a labeled-illumination-only scan before any full route_c rerun.",
        ],
        "must_change": [
            "Use robust prefix-aware option parsing for benchmark-truth-leaning label construction.",
            "Search route_c labeled contracts under the real 1.5B outputs instead of relying on lightweight reference balance.",
        ],
        "should_not_change": [
            "Do not expand to 3B/7B.",
            "Do not reopen fusion-axis work.",
            "Do not expand dataset scope.",
        ],
        "success_criterion": [
            "Produce a candidate labeled subset with both label_0 and label_1 under 1.5B outputs.",
            "Materialize enough balanced base ids to rerun route_c portability precheck without the old single-class failure.",
        ],
    }

    knobs_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_knobs": {
            "precheck_budget": int(portability_selection.get("selected_base_sample_count", 0)),
            "selected_labeled_contract_count": len(selected_candidate_rows),
            "label_parse_mode": "strict_in_113",
            "selection_strategy": portability_selection.get("selection_diagnostics", {}).get("strategy"),
        },
        "recovery_knobs": {
            "scan_scope": "all_labeled_illumination_contracts_from_model_axis_1p5b_dry_run",
            "label_parse_mode": "robust_prefix",
            "target_base_budget": int(portability_selection.get("selected_base_sample_count", 0)),
            "selection_priority": [
                "mixed-label bases under real 1.5B outputs",
                "positive-only bases under real 1.5B outputs",
                "reasoning-order fill",
            ],
        },
    }
    return diagnosis, recovery_plan, knobs_summary


def build_model_axis_1p5b_route_c_stabilization(
    route_c_portability_dir: Path,
    dry_run_materialized_inputs_dir: Path,
    reference_route_c_dataset_path: Path,
    models_config_path: Path,
    illumination_config_path: Path,
    illumination_prompt_dir: Path,
    output_dir: Path,
    seed: int,
    target_base_budget: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    portability_selection = load_json(route_c_portability_dir / "route_c_portability_selection.json")
    portability_readiness = load_json(route_c_portability_dir / "route_c_portability_readiness_summary.json")
    portability_run_summary = load_json(route_c_portability_dir / "route_c_portability_run_summary.json")
    reference_rows = load_jsonl(reference_route_c_dataset_path)
    precheck_labeled_raw_rows = load_jsonl(
        route_c_portability_dir
        / "route_c_portability_precheck_run"
        / "route_c_v6_labeled_illumination"
        / "illumination_probe"
        / "raw_results.jsonl"
    )
    full_reasoning_rows = load_jsonl(dry_run_materialized_inputs_dir / "reasoning_query_contracts.jsonl")
    full_labeled_rows = load_jsonl(dry_run_materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl")

    diagnosis, recovery_plan, knobs_summary = diagnose_route_c_label_collapse(
        portability_selection=portability_selection,
        precheck_labeled_raw_rows=precheck_labeled_raw_rows,
        reference_rows=reference_rows,
    )
    write_json(output_dir / "route_c_label_collapse_diagnosis.json", diagnosis)
    write_json(output_dir / "route_c_label_balance_recovery_plan.json", recovery_plan)
    write_json(output_dir / "route_c_selection_knobs_summary.json", knobs_summary)

    scan_dir = output_dir / "route_c_full_labeled_scan"
    scan_budget = len(full_labeled_rows)
    labeled_probe = run_illumination_probe(
        model_config_path=models_config_path,
        model_profile_name="pilot_small_hf",
        illumination_config_path=illumination_config_path,
        illumination_profile_name="labeled_bootstrap",
        prompt_dir=illumination_prompt_dir,
        output_dir=scan_dir / "illumination_probe",
        dataset_manifest=None,
        query_file=dry_run_materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl",
        alpha_override=None,
        query_budget_override=scan_budget,
        trigger_type_override="targeted_icl_demo",
        target_type_override="forced_option_label",
        seed=seed,
        dry_run=False,
        smoke_mode=False,
    )

    full_labeled_raw_rows = load_jsonl(scan_dir / "illumination_probe" / "raw_results.jsonl")
    candidate_rows = [build_candidate_row(row) for row in full_labeled_raw_rows]
    selected_base_ids, selection_diagnostics = select_balanced_base_ids(
        candidate_rows=candidate_rows,
        reasoning_rows=full_reasoning_rows,
        target_base_budget=target_base_budget,
    )
    selected_base_id_set = set(selected_base_ids)
    balanced_candidate_rows = [row for row in candidate_rows if str(row["base_sample_id"]) in selected_base_id_set]
    class_balance = summarize_class_balance(balanced_candidate_rows, "robust_ground_truth_label")

    balanced_candidate_summary = {
        "summary_status": "PASS" if class_balance["label_0"] > 0 and class_balance["label_1"] > 0 else "BLOCKED",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "source_portability_status": portability_run_summary.get("execution_status"),
        "source_ready_run": portability_readiness.get("ready_run"),
        "scan_probe_summary_status": labeled_probe["summary"]["summary_status"],
        "full_scan_contract_count": len(candidate_rows),
        "full_scan_base_count": len({row["base_sample_id"] for row in candidate_rows}),
        "full_scan_class_balance": summarize_class_balance(candidate_rows, "robust_ground_truth_label"),
        "selected_base_ids": selected_base_ids,
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": len(balanced_candidate_rows),
        "class_balance": class_balance,
        "selection_diagnostics": selection_diagnostics,
        "notes": [
            "This artifact stabilizes route_c label balance under real 1.5B outputs before rerunning route_c portability.",
            "Class balance is computed with robust prefix-aware option parsing.",
        ],
    }
    write_jsonl(output_dir / "route_c_balanced_candidate_dataset.jsonl", balanced_candidate_rows)
    write_json(output_dir / "route_c_balanced_candidate_summary.json", balanced_candidate_summary)

    precheck = {
        "summary_status": "PASS" if class_balance["label_0"] > 0 and class_balance["label_1"] > 0 else "BLOCKED",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "class_balance": class_balance,
        "selected_base_ids": selected_base_ids,
        "selected_base_count": len(selected_base_ids),
        "selected_contract_count": len(balanced_candidate_rows),
        "ready_for_stable_portability_rerun": class_balance["label_0"] > 0 and class_balance["label_1"] > 0,
        "recommended_label_parse_mode": "robust_prefix",
        "blocking_reason": (
            None
            if class_balance["label_0"] > 0 and class_balance["label_1"] > 0
            else "No bi-class candidate subset could be constructed from the scanned 1.5B labeled contracts."
        ),
    }
    write_json(output_dir / "route_c_label_balance_precheck.json", precheck)

    return {
        "diagnosis": diagnosis,
        "recovery_plan": recovery_plan,
        "knobs_summary": knobs_summary,
        "balanced_candidate_summary": balanced_candidate_summary,
        "precheck": precheck,
        "output_paths": {
            "diagnosis": str((output_dir / "route_c_label_collapse_diagnosis.json").resolve()),
            "recovery_plan": str((output_dir / "route_c_label_balance_recovery_plan.json").resolve()),
            "knobs_summary": str((output_dir / "route_c_selection_knobs_summary.json").resolve()),
            "balanced_candidate_dataset": str((output_dir / "route_c_balanced_candidate_dataset.jsonl").resolve()),
            "balanced_candidate_summary": str((output_dir / "route_c_balanced_candidate_summary.json").resolve()),
            "precheck": str((output_dir / "route_c_label_balance_precheck.json").resolve()),
        },
    }
