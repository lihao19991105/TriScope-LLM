"""Minimal execution-path regression validation for route_c frozen semantic boundary behavior."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json, write_jsonl
from src.eval.route_c_label_health_gating import build_route_c_label_health_gating
from src.fusion.benchmark_truth_leaning_label import (
    build_benchmark_truth_leaning_dataset,
    run_benchmark_truth_leaning_logistic,
)


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-minimal-execution-path-regression/v1"


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(path))


def _load_149_details(regression_dir: Path) -> list[dict[str, Any]]:
    return _load_jsonl(regression_dir / "route_c_frozen_semantic_small_regression_details.jsonl")


def _load_143_raw_results(stage_143_run_dir: Path) -> list[dict[str, Any]]:
    return _load_jsonl(stage_143_run_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl")


def _load_144_raw_results(stage_144_run_dir: Path) -> list[dict[str, Any]]:
    return _load_jsonl(stage_144_run_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl")


def _load_143_dataset(stage_143_run_dir: Path) -> list[dict[str, Any]]:
    return _load_jsonl(stage_143_run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_dataset.jsonl")


def _select_regression_cases(details: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_case_id = {str(row["case_id"]): row for row in details}
    selected_case_ids = [
        "focused::controlled_recoverable::code_fence",
        "focused::new_recoverable::code_fence_lang_tag",
        "focused::controlled_recoverable::quote_wrap",
        "focused::real_normal::csqa-pilot-002__control",
        "focused::real_normal::csqa-pilot-021__control",
        "focused::real_unrecoverable::csqa-pilot-021__targeted",
        "focused::new_nonrecoverable::code_fence_punct_only",
        "focused::new_nonrecoverable::code_fence_contract_broken",
    ]
    return [by_case_id[case_id] for case_id in selected_case_ids]


def _raw_result_templates(stage_143_rows: list[dict[str, Any]], stage_144_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    templates: dict[str, dict[str, Any]] = {}
    for row in stage_143_rows + stage_144_rows:
        templates[str(row["sample_id"])] = row
    return templates


def _fusion_templates(stage_143_dataset_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    templates: dict[str, dict[str, Any]] = {}
    for row in stage_143_dataset_rows:
        base_sample_id = str(row["base_sample_id"])
        if base_sample_id in templates:
            continue
        templates[base_sample_id] = {
            "sample_id": base_sample_id,
            "model_profile": row["model_profile"],
            "reasoning_present": bool(row["reasoning_present"]),
            "confidence_present": bool(row["confidence_present"]),
            "reasoning__sample_id": row["reasoning__sample_id"],
            "reasoning__answer_changed_after_reasoning": float(row["reasoning__answer_changed_after_reasoning"]),
            "reasoning__target_behavior_flip_flag": float(row["reasoning__target_behavior_flip_flag"]),
            "reasoning__reasoning_length": float(row["reasoning__reasoning_length"]),
            "reasoning__reasoning_step_count": float(row["reasoning__reasoning_step_count"]),
            "reasoning__reasoning_to_answer_length_ratio": float(row["reasoning__reasoning_to_answer_length_ratio"]),
            "confidence__sample_id": row["confidence__sample_id"],
            "confidence__mean_chosen_token_prob": float(row["confidence__mean_chosen_token_prob"]),
            "confidence__mean_entropy": float(row["confidence__mean_entropy"]),
            "confidence__high_confidence_fraction": float(row["confidence__high_confidence_fraction"]),
            "confidence__max_consecutive_high_confidence_steps": float(row["confidence__max_consecutive_high_confidence_steps"]),
            "confidence__entropy_collapse_score": float(row["confidence__entropy_collapse_score"]),
        }
    return templates


def _regression_group_from_case(case_id: str) -> str:
    if "real_normal" in case_id:
        return "normal_execution_guardrail"
    if "real_unrecoverable" in case_id or "new_nonrecoverable" in case_id:
        return "nonrecoverable_execution_guardrail"
    return "recoverable_execution_path"


def _materialize_execution_inputs(
    cases: list[dict[str, Any]],
    raw_templates: dict[str, dict[str, Any]],
    fusion_templates: dict[str, dict[str, Any]],
    execution_root_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    labeled_rows: list[dict[str, Any]] = []
    used_base_ids: set[str] = set()

    for index, case in enumerate(cases):
        base_source_case_id = str(case["case_id"])
        if "real_normal::" in base_source_case_id:
            template_sample_id = base_source_case_id.replace("focused::", "").replace("real_normal::", "")
        elif "real_unrecoverable::" in base_source_case_id:
            template_sample_id = base_source_case_id.replace("focused::", "").replace("real_unrecoverable::", "")
        elif "new_nonrecoverable::code_fence_contract_broken" in base_source_case_id:
            template_sample_id = "csqa-pilot-021__targeted"
        else:
            template_sample_id = "csqa-pilot-002__control"

        template = raw_templates[template_sample_id]
        contract_metadata = dict(template.get("metadata", {}).get("contract_metadata", {}))
        base_sample_id = str(contract_metadata["base_sample_id"])
        used_base_ids.add(base_sample_id)

        synthetic_sample_id = f"regression_exec_{index:02d}__{base_source_case_id.split('::')[-1]}"
        contract_variant = f"regression_{index:02d}"
        contract_metadata.update(
            {
                "base_sample_id": base_sample_id,
                "contract_variant": contract_variant,
                "query_answer_key": str(case["query_answer_key"]),
                "label_source": "minimal_execution_path_regression",
                "label_scope": "benchmark_truth_leaning_supervision_proxy",
            }
        )

        metadata = dict(template.get("metadata", {}))
        metadata["contract_metadata"] = contract_metadata
        metadata["regression_reference"] = {
            "frozen_case_id": case["case_id"],
            "regression_group": _regression_group_from_case(base_source_case_id),
            "frozen_reference_handoff": case["frozen_reference_handoff"],
            "frozen_reference_category": case["frozen_reference_category"],
        }

        labeled_row = {
            **template,
            "sample_id": synthetic_sample_id,
            "response_text": case["raw_response"],
            "metadata": metadata,
        }
        labeled_rows.append(labeled_row)

    fusion_rows = [fusion_templates[base_id] for base_id in sorted(used_base_ids)]

    labeled_path = execution_root_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl"
    dataset_input_path = execution_root_dir / "execution_inputs" / "minimal_labeled_illumination_raw_results.jsonl"
    fusion_path = execution_root_dir / "execution_inputs" / "minimal_expanded_real_pilot_fusion_dataset.jsonl"
    labeled_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_input_path.parent.mkdir(parents=True, exist_ok=True)

    write_jsonl(labeled_path, labeled_rows)
    write_jsonl(dataset_input_path, labeled_rows)
    write_jsonl(fusion_path, fusion_rows)

    manifest = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "case_count": len(cases),
        "base_sample_count": len(fusion_rows),
        "regression_group_counts": dict(Counter(_regression_group_from_case(case["case_id"]) for case in cases)),
        "execution_root_dir": str(execution_root_dir.resolve()),
        "labeled_results_path": str(labeled_path.resolve()),
        "fusion_dataset_path": str(fusion_path.resolve()),
    }
    write_json(execution_root_dir / "execution_inputs" / "execution_input_manifest.json", manifest)
    return labeled_rows, fusion_rows, manifest


def _path_handoff_from_health_row(row: dict[str, Any]) -> str:
    if bool(row.get("response_option_missing")):
        return "degeneration_blocked"
    source = str(row.get("selected_parser_source") or "raw")
    if source == "normalized":
        return "pass_formatted_to_parser"
    return "pass_raw_to_parser"


def _path_category_from_health_row(row: dict[str, Any]) -> str:
    if not bool(row.get("response_option_missing")):
        source = str(row.get("selected_parser_source") or "raw")
        return "recoverable_formatting_issue" if source == "normalized" else "parser_reachable"
    if bool(row.get("response_punct_only")):
        return "punctuation_collapse"
    parse_failure_category = str(row.get("parse_failure_category") or "contract_broken_response")
    # At path level we collapse parser-internal "unknown_token" failures into the
    # higher-level blocked taxonomy used by the anti-degradation boundary suite.
    if parse_failure_category == "unknown_token":
        return "contract_broken_response"
    return parse_failure_category


def _evaluate_rows(
    cases: list[dict[str, Any]],
    health_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    health_by_sample_id = {str(row["sample_id"]): row for row in health_rows}
    records: list[dict[str, Any]] = []

    for index, case in enumerate(cases):
        synthetic_sample_id = f"regression_exec_{index:02d}__{case['case_id'].split('::')[-1]}"
        health_row = health_by_sample_id[synthetic_sample_id]
        current_handoff = _path_handoff_from_health_row(health_row)
        current_category = _path_category_from_health_row(health_row)
        frozen_handoff = str(case["frozen_reference_handoff"])
        frozen_category = str(case["frozen_reference_category"])
        regression_group = _regression_group_from_case(case["case_id"])
        match = current_handoff == frozen_handoff and current_category == frozen_category

        if regression_group == "recoverable_execution_path" and current_handoff != "pass_formatted_to_parser":
            mismatch_type = "recoverable_path_regression"
        elif regression_group == "normal_execution_guardrail" and current_handoff != "pass_raw_to_parser":
            mismatch_type = "normal_path_damage"
        elif regression_group == "nonrecoverable_execution_guardrail" and current_handoff != "degeneration_blocked":
            mismatch_type = "nonrecoverable_path_leak"
        elif not match:
            mismatch_type = "path_reference_drift"
        else:
            mismatch_type = "match"

        records.append(
            {
                "schema_version": SCHEMA_VERSION,
                "case_id": case["case_id"],
                "regression_group": regression_group,
                "source_type": case["source_type"],
                "raw_response": case["raw_response"],
                "query_answer_key": case["query_answer_key"],
                "frozen_reference_handoff": frozen_handoff,
                "frozen_reference_category": frozen_category,
                "current_path_handoff": current_handoff,
                "current_path_category": current_category,
                "current_selected_parser_source": health_row.get("selected_parser_source"),
                "current_response_option_missing": health_row.get("response_option_missing"),
                "current_parse_failure_category": health_row.get("parse_failure_category"),
                "current_ground_truth_label": health_row.get("ground_truth_label"),
                "current_response_option": health_row.get("response_option"),
                "match_frozen_reference": match,
                "mismatch_type": mismatch_type,
            }
        )
    return records


def _summary(records: list[dict[str, Any]], gate_result: dict[str, Any], logistic_status: str) -> dict[str, Any]:
    by_group_handoff: dict[str, Counter[str]] = defaultdict(Counter)
    mismatch_counts: Counter[str] = Counter()
    for record in records:
        by_group_handoff[record["regression_group"]][record["current_path_handoff"]] += 1
        mismatch_counts[record["mismatch_type"]] += 1

    recoverable_records = [r for r in records if r["regression_group"] == "recoverable_execution_path"]
    normal_records = [r for r in records if r["regression_group"] == "normal_execution_guardrail"]
    nonrecoverable_records = [r for r in records if r["regression_group"] == "nonrecoverable_execution_guardrail"]

    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_case_count": len(records),
        "group_vs_current_path_handoff": {group: dict(counter) for group, counter in by_group_handoff.items()},
        "mismatch_type_counts": dict(mismatch_counts),
        "recoverable_path_regression_count": int(mismatch_counts.get("recoverable_path_regression", 0)),
        "normal_path_damage_count": int(mismatch_counts.get("normal_path_damage", 0)),
        "nonrecoverable_path_leak_count": int(mismatch_counts.get("nonrecoverable_path_leak", 0)),
        "path_reference_drift_count": int(mismatch_counts.get("path_reference_drift", 0)),
        "recoverable_path_pass_rate": (
            sum(1 for r in recoverable_records if r["current_path_handoff"] == "pass_formatted_to_parser") / len(recoverable_records)
            if recoverable_records
            else None
        ),
        "normal_path_pass_rate": (
            sum(1 for r in normal_records if r["current_path_handoff"] == "pass_raw_to_parser") / len(normal_records)
            if normal_records
            else None
        ),
        "nonrecoverable_path_block_rate": (
            sum(1 for r in nonrecoverable_records if r["current_path_handoff"] == "degeneration_blocked") / len(nonrecoverable_records)
            if nonrecoverable_records
            else None
        ),
        "all_cases_match_frozen_reference": all(record["match_frozen_reference"] for record in records),
        "gate_status": gate_result.get("gate_status"),
        "gate_blocked_reason": gate_result.get("blocked_reason"),
        "logistic_status": logistic_status,
    }


def _report(summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Route-C Frozen Semantic Minimal Execution-Path Regression Report")
    lines.append("")
    lines.append("## Path Summary")
    lines.append(f"- recoverable_path_pass_rate: {summary['recoverable_path_pass_rate']}")
    lines.append(f"- normal_path_pass_rate: {summary['normal_path_pass_rate']}")
    lines.append(f"- nonrecoverable_path_block_rate: {summary['nonrecoverable_path_block_rate']}")
    lines.append(f"- gate_status: {summary['gate_status']}")
    lines.append(f"- logistic_status: {summary['logistic_status']}")
    lines.append(f"- all_cases_match_frozen_reference: {summary['all_cases_match_frozen_reference']}")
    lines.append("")
    lines.append("## Case-Level Comparison")
    for record in records:
        lines.append(
            "- "
            + f"{record['case_id']}: ref {record['frozen_reference_handoff']} / {record['frozen_reference_category']} -> "
            + f"path {record['current_path_handoff']} / {record['current_path_category']} ({record['mismatch_type']})"
        )
    return "\n".join(lines) + "\n"


def build_route_c_frozen_semantic_minimal_execution_path_regression(
    regression_dir: Path,
    stage_143_run_dir: Path,
    stage_144_run_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    regression_details = _load_149_details(regression_dir)
    cases = _select_regression_cases(regression_details)
    raw_templates = _raw_result_templates(
        stage_143_rows=_load_143_raw_results(stage_143_run_dir),
        stage_144_rows=_load_144_raw_results(stage_144_run_dir),
    )
    fusion_templates = _fusion_templates(_load_143_dataset(stage_143_run_dir))

    execution_root_dir = output_dir / "minimal_execution_root"
    labeled_rows, fusion_rows, manifest = _materialize_execution_inputs(
        cases=cases,
        raw_templates=raw_templates,
        fusion_templates=fusion_templates,
        execution_root_dir=execution_root_dir,
    )

    dataset_dir = execution_root_dir / "route_c_v6_dataset_dir"
    dataset_result = build_benchmark_truth_leaning_dataset(
        expanded_real_pilot_fusion_dataset_path=execution_root_dir / "execution_inputs" / "minimal_expanded_real_pilot_fusion_dataset.jsonl",
        labeled_illumination_raw_results_path=execution_root_dir / "execution_inputs" / "minimal_labeled_illumination_raw_results.jsonl",
        output_dir=dataset_dir,
        fusion_profile="route_c_frozen_semantic_minimal_execution_path_regression",
        run_id="route_c_frozen_semantic_minimal_execution_path_regression",
        option_parse_mode="robust_prefix",
        option_normalization_mode="conservative",
        emit_parser_instrumentation=True,
    )
    gate_dir = output_dir / "route_c_label_health_gate"
    gate_result = build_route_c_label_health_gating(
        execution_root_dir=execution_root_dir,
        route_c_run_subdir=".",
        output_dir=gate_dir,
    )

    logistic_status = "SKIPPED"
    logistic_output_paths: dict[str, str] = {}
    if gate_result["summary"].get("gate_status") == "PASS":
        logistic_dir = output_dir / "route_c_logistic_continuation"
        logistic_result = run_benchmark_truth_leaning_logistic(
            dataset_path=dataset_dir / "benchmark_truth_leaning_dataset.jsonl",
            output_dir=logistic_dir,
            fusion_profile="route_c_frozen_semantic_minimal_execution_path_regression",
            run_id="route_c_frozen_semantic_minimal_execution_path_regression",
            label_threshold=label_threshold,
            random_seed=seed,
        )
        logistic_status = "PASS"
        logistic_output_paths = logistic_result["output_paths"]
    else:
        logistic_status = "BLOCKED_BY_GATE"

    health_rows = load_jsonl(dataset_dir / "benchmark_truth_leaning_label_health_rows.jsonl")
    records = _evaluate_rows(cases=cases, health_rows=health_rows)
    summary = _summary(records=records, gate_result=gate_result["summary"], logistic_status=logistic_status)

    suite = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "suite_name": "route_c_frozen_semantic_minimal_execution_path_regression_v1",
        "case_count": len(cases),
        "group_counts": dict(Counter(_regression_group_from_case(case["case_id"]) for case in cases)),
        "source_type_counts": dict(Counter(case["source_type"] for case in cases)),
        "cases": cases,
    }
    rules = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_path_criteria": [
            "selected_parser_source == normalized",
            "response_option_missing == false",
            "no semantic guessing",
        ],
        "normal_path_criteria": [
            "selected_parser_source == raw",
            "response_option_missing == false",
        ],
        "nonrecoverable_path_criteria": [
            "response_option_missing == true",
            "gate must not be relaxed for bad rows",
        ],
        "path_level_consistency_criteria": [
            "path-level handoff matches stage-149 frozen reference",
            "gate semantics unchanged",
            "logistic continuation only after PASS gate",
        ],
    }
    report = _report(summary=summary, records=records)

    write_json(output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_suite.json", suite)
    write_json(output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_rules.json", rules)
    write_json(output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_summary.json", summary)
    write_jsonl(output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_details.jsonl", records)
    (output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_report.md").write_text(report, encoding="utf-8")
    write_json(
        output_dir / "config_snapshot.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "regression_dir": str(regression_dir.resolve()),
            "stage_143_run_dir": str(stage_143_run_dir.resolve()),
            "stage_144_run_dir": str(stage_144_run_dir.resolve()),
            "seed": seed,
            "label_threshold": label_threshold,
        },
    )

    return {
        "suite": suite,
        "rules": rules,
        "summary": summary,
        "output_paths": {
            "suite": str((output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_suite.json").resolve()),
            "rules": str((output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_rules.json").resolve()),
            "summary": str((output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_summary.json").resolve()),
            "details": str((output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_details.jsonl").resolve()),
            "report": str((output_dir / "route_c_frozen_semantic_minimal_execution_path_regression_report.md").resolve()),
            "execution_input_manifest": str((execution_root_dir / "execution_inputs" / "execution_input_manifest.json").resolve()),
            "dataset_summary": dataset_result["output_paths"]["summary"],
            "label_health_summary": dataset_result["output_paths"]["label_health_summary"],
            "gate_result": gate_result["output_paths"]["gate_result"],
            "logistic_summary": logistic_output_paths.get("summary"),
        },
    }
