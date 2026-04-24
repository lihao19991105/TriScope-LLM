"""Minimal real-execution validation for route_c frozen semantic boundary behavior."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json, write_jsonl
from src.eval.route_c_label_health_gating import build_route_c_label_health_gating
from src.fusion.benchmark_truth_leaning_label import (
    build_benchmark_truth_leaning_dataset,
    run_benchmark_truth_leaning_logistic,
)


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-minimal-real-execution-validation/v1"


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def _load_150_details(stage_150_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(stage_150_dir / "route_c_frozen_semantic_minimal_execution_path_regression_details.jsonl"))


def _load_real_raw_rows(real_run_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(real_run_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl"))


def _load_real_health_rows(real_run_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(
        _required_file(real_run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_health_rows.jsonl")
    )


def _load_real_fusion_rows(real_run_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(real_run_dir / "route_c_v6_real_pilot_fusion" / "fusion_dataset.jsonl"))


def _reference_by_case_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["case_id"]): row for row in rows}


def _real_row_by_sample_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["sample_id"]): row for row in rows}


def _fusion_by_base_sample_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["sample_id"]): row for row in rows}


def _query_answer_key(real_row: dict[str, Any]) -> str:
    metadata = real_row.get("metadata", {})
    contract = metadata.get("contract_metadata", {})
    value = str(contract.get("query_answer_key", "")).strip().upper()
    if value == "":
        return "A"
    return value


def _minimal_real_execution_suite(
    real_raw_rows: list[dict[str, Any]],
    reference_by_case: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    by_sample = _real_row_by_sample_id(real_raw_rows)

    required_samples = [
        "csqa-pilot-002__control",
        "csqa-pilot-021__control",
        "csqa-pilot-021__targeted",
    ]
    missing = [sample_id for sample_id in required_samples if sample_id not in by_sample]
    if missing:
        raise ValueError(f"Real execution run missing required anchor samples: {missing}")

    recoverable_anchor = by_sample["csqa-pilot-002__control"]
    nonrecoverable_anchor = by_sample["csqa-pilot-021__targeted"]
    recoverable_raw = str(recoverable_anchor["response_text"])
    nonrecoverable_raw = str(nonrecoverable_anchor["response_text"])

    suite: list[dict[str, Any]] = [
        {
            "case_id": "real_exec::controlled_recoverable::code_fence",
            "path_group": "recoverable_real_execution",
            "source_type": "controlled-format-variant-from-real",
            "is_real_execution_input": False,
            "real_execution_anchor_sample_id": "csqa-pilot-002__control",
            "raw_response": f"```{recoverable_raw}```",
            "query_answer_key": _query_answer_key(recoverable_anchor),
            "expected_handoff": "pass_formatted_to_parser",
            "expected_category": "recoverable_formatting_issue",
            "expected_recoverability": "recoverable",
            "frozen_reference_case_id": "focused::controlled_recoverable::code_fence",
            "frozen_reference_handoff": reference_by_case["focused::controlled_recoverable::code_fence"][
                "current_path_handoff"
            ],
            "frozen_reference_category": reference_by_case["focused::controlled_recoverable::code_fence"][
                "current_path_category"
            ],
            "code_fence_like": True,
            "case_note": "code-fence-like recoverable wrapper derived from a real execution parser-reachable response",
        },
        {
            "case_id": "real_exec::controlled_recoverable::code_fence_lang_tag",
            "path_group": "recoverable_real_execution",
            "source_type": "controlled-format-variant-from-real",
            "is_real_execution_input": False,
            "real_execution_anchor_sample_id": "csqa-pilot-002__control",
            "raw_response": f"```text\n{recoverable_raw}\n```",
            "query_answer_key": _query_answer_key(recoverable_anchor),
            "expected_handoff": "pass_formatted_to_parser",
            "expected_category": "recoverable_formatting_issue",
            "expected_recoverability": "recoverable",
            "frozen_reference_case_id": "focused::new_recoverable::code_fence_lang_tag",
            "frozen_reference_handoff": reference_by_case["focused::new_recoverable::code_fence_lang_tag"][
                "current_path_handoff"
            ],
            "frozen_reference_category": reference_by_case["focused::new_recoverable::code_fence_lang_tag"][
                "current_path_category"
            ],
            "code_fence_like": True,
            "case_note": "language-tagged code-fence recoverable wrapper derived from a real execution parser-reachable response",
        },
        {
            "case_id": "real_exec::real_normal::csqa-pilot-002__control",
            "path_group": "normal_real_execution_guardrail",
            "source_type": "real",
            "is_real_execution_input": True,
            "real_execution_anchor_sample_id": "csqa-pilot-002__control",
            "raw_response": str(by_sample["csqa-pilot-002__control"]["response_text"]),
            "query_answer_key": _query_answer_key(by_sample["csqa-pilot-002__control"]),
            "expected_handoff": "pass_raw_to_parser",
            "expected_category": "parser_reachable",
            "expected_recoverability": "not_needed",
            "frozen_reference_case_id": "focused::real_normal::csqa-pilot-002__control",
            "frozen_reference_handoff": reference_by_case["focused::real_normal::csqa-pilot-002__control"][
                "current_path_handoff"
            ],
            "frozen_reference_category": reference_by_case["focused::real_normal::csqa-pilot-002__control"][
                "current_path_category"
            ],
            "code_fence_like": False,
            "case_note": "real parser-reachable normal guardrail case from stable real execution run",
        },
        {
            "case_id": "real_exec::real_normal::csqa-pilot-021__control",
            "path_group": "normal_real_execution_guardrail",
            "source_type": "real",
            "is_real_execution_input": True,
            "real_execution_anchor_sample_id": "csqa-pilot-021__control",
            "raw_response": str(by_sample["csqa-pilot-021__control"]["response_text"]),
            "query_answer_key": _query_answer_key(by_sample["csqa-pilot-021__control"]),
            "expected_handoff": "pass_raw_to_parser",
            "expected_category": "parser_reachable",
            "expected_recoverability": "not_needed",
            "frozen_reference_case_id": "focused::real_normal::csqa-pilot-021__control",
            "frozen_reference_handoff": reference_by_case["focused::real_normal::csqa-pilot-021__control"][
                "current_path_handoff"
            ],
            "frozen_reference_category": reference_by_case["focused::real_normal::csqa-pilot-021__control"][
                "current_path_category"
            ],
            "code_fence_like": False,
            "case_note": "second real parser-reachable normal guardrail case from stable real execution run",
        },
        {
            "case_id": "real_exec::real_nonrecoverable::csqa-pilot-021__targeted",
            "path_group": "nonrecoverable_real_execution_guardrail",
            "source_type": "real",
            "is_real_execution_input": True,
            "real_execution_anchor_sample_id": "csqa-pilot-021__targeted",
            "raw_response": nonrecoverable_raw,
            "query_answer_key": _query_answer_key(nonrecoverable_anchor),
            "expected_handoff": "degeneration_blocked",
            "expected_category": "contract_broken_response",
            "expected_recoverability": "not_recoverable",
            "frozen_reference_case_id": None,
            "frozen_reference_handoff": None,
            "frozen_reference_category": None,
            "code_fence_like": False,
            "case_note": "real nonrecoverable blocked case from stable real execution run",
        },
        {
            "case_id": "real_exec::controlled_nonrecoverable::code_fence_contract_broken",
            "path_group": "nonrecoverable_real_execution_guardrail",
            "source_type": "controlled-format-variant-from-real",
            "is_real_execution_input": False,
            "real_execution_anchor_sample_id": "csqa-pilot-021__targeted",
            "raw_response": f"```text\n{nonrecoverable_raw}\n```",
            "query_answer_key": _query_answer_key(nonrecoverable_anchor),
            "expected_handoff": "degeneration_blocked",
            "expected_category": "contract_broken_response",
            "expected_recoverability": "not_recoverable",
            "frozen_reference_case_id": "focused::new_nonrecoverable::code_fence_contract_broken",
            "frozen_reference_handoff": reference_by_case["focused::new_nonrecoverable::code_fence_contract_broken"][
                "current_path_handoff"
            ],
            "frozen_reference_category": reference_by_case["focused::new_nonrecoverable::code_fence_contract_broken"][
                "current_path_category"
            ],
            "code_fence_like": True,
            "case_note": "near-boundary nonrecoverable code-fence wrapper derived from a real nonrecoverable response",
        },
    ]
    return suite


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
    if parse_failure_category == "unknown_token":
        return "contract_broken_response"
    return parse_failure_category


def _materialize_real_execution_inputs(
    cases: list[dict[str, Any]],
    real_raw_rows: list[dict[str, Any]],
    real_fusion_rows: list[dict[str, Any]],
    execution_root_dir: Path,
) -> dict[str, Any]:
    raw_by_sample_id = _real_row_by_sample_id(real_raw_rows)
    fusion_by_base_id = _fusion_by_base_sample_id(real_fusion_rows)

    labeled_rows: list[dict[str, Any]] = []
    used_base_ids: set[str] = set()

    for index, case in enumerate(cases):
        template = raw_by_sample_id[case["real_execution_anchor_sample_id"]]
        metadata = dict(template.get("metadata", {}))
        contract_metadata = dict(metadata.get("contract_metadata", {}))
        base_sample_id = str(contract_metadata["base_sample_id"])
        used_base_ids.add(base_sample_id)

        contract_metadata.update(
            {
                "base_sample_id": base_sample_id,
                "contract_variant": f"real_exec_validation_{index:02d}",
                "query_answer_key": str(case["query_answer_key"]),
                "label_source": "minimal_real_execution_validation",
                "label_scope": "benchmark_truth_leaning_supervision_proxy",
            }
        )
        metadata["contract_metadata"] = contract_metadata
        metadata["real_execution_validation_reference"] = {
            "case_id": case["case_id"],
            "path_group": case["path_group"],
            "source_type": case["source_type"],
            "is_real_execution_input": bool(case["is_real_execution_input"]),
            "real_execution_anchor_sample_id": case["real_execution_anchor_sample_id"],
        }

        labeled_rows.append(
            {
                **template,
                "sample_id": f"real_exec_validation_{index:02d}__{case['case_id'].split('::')[-1]}",
                "response_text": case["raw_response"],
                "metadata": metadata,
            }
        )

    fusion_rows = [fusion_by_base_id[base_id] for base_id in sorted(used_base_ids)]

    labeled_path = execution_root_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl"
    dataset_input_path = execution_root_dir / "execution_inputs" / "minimal_real_execution_labeled_raw_results.jsonl"
    fusion_path = execution_root_dir / "execution_inputs" / "minimal_real_execution_fusion_dataset.jsonl"
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
        "group_counts": dict(Counter(case["path_group"] for case in cases)),
        "source_type_counts": dict(Counter(case["source_type"] for case in cases)),
        "real_execution_input_count": sum(1 for case in cases if bool(case["is_real_execution_input"])),
        "controlled_variant_count": sum(1 for case in cases if not bool(case["is_real_execution_input"])),
        "execution_root_dir": str(execution_root_dir.resolve()),
        "labeled_results_path": str(labeled_path.resolve()),
        "fusion_dataset_path": str(fusion_path.resolve()),
    }
    write_json(execution_root_dir / "execution_inputs" / "real_execution_input_manifest.json", manifest)
    return manifest


def _evaluate_records(cases: list[dict[str, Any]], health_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    health_by_sample_id = {str(row["sample_id"]): row for row in health_rows}
    records: list[dict[str, Any]] = []

    for index, case in enumerate(cases):
        sample_id = f"real_exec_validation_{index:02d}__{case['case_id'].split('::')[-1]}"
        health_row = health_by_sample_id[sample_id]
        current_handoff = _path_handoff_from_health_row(health_row)
        current_category = _path_category_from_health_row(health_row)

        match_expected = current_handoff == case["expected_handoff"] and current_category == case["expected_category"]
        has_frozen_reference = bool(case["frozen_reference_case_id"])
        match_frozen_reference = (
            current_handoff == case["frozen_reference_handoff"] and current_category == case["frozen_reference_category"]
            if has_frozen_reference
            else None
        )

        if bool(case["code_fence_like"]) and case["path_group"] == "recoverable_real_execution" and current_handoff != "pass_formatted_to_parser":
            mismatch_type = "code_fence_handoff_regression"
        elif case["path_group"] == "recoverable_real_execution" and current_handoff != "pass_formatted_to_parser":
            mismatch_type = "recoverable_real_execution_regression"
        elif case["path_group"] == "normal_real_execution_guardrail" and current_handoff != "pass_raw_to_parser":
            mismatch_type = "normal_real_execution_damage"
        elif case["path_group"] == "nonrecoverable_real_execution_guardrail" and current_handoff != "degeneration_blocked":
            mismatch_type = "nonrecoverable_real_execution_leak"
        elif not match_expected:
            mismatch_type = "expected_behavior_drift"
        elif has_frozen_reference and match_frozen_reference is False:
            mismatch_type = "frozen_reference_drift"
        else:
            mismatch_type = "match"

        records.append(
            {
                "schema_version": SCHEMA_VERSION,
                **case,
                "synthetic_sample_id": sample_id,
                "current_handoff": current_handoff,
                "current_category": current_category,
                "current_selected_parser_source": health_row.get("selected_parser_source"),
                "current_response_option_missing": health_row.get("response_option_missing"),
                "current_parse_failure_category": health_row.get("parse_failure_category"),
                "current_ground_truth_label": health_row.get("ground_truth_label"),
                "current_response_option": health_row.get("response_option"),
                "match_expected": match_expected,
                "match_frozen_reference": match_frozen_reference,
                "mismatch_type": mismatch_type,
            }
        )
    return records


def _summary(
    records: list[dict[str, Any]],
    gate_result: dict[str, Any],
    logistic_status: str,
    reference_snapshots: dict[str, Any],
) -> dict[str, Any]:
    by_group_handoff: dict[str, Counter[str]] = defaultdict(Counter)
    by_parser_source: Counter[str] = Counter()
    mismatch_counts: Counter[str] = Counter()

    for record in records:
        by_group_handoff[record["path_group"]][record["current_handoff"]] += 1
        by_parser_source[str(record.get("current_selected_parser_source") or "raw")] += 1
        mismatch_counts[record["mismatch_type"]] += 1

    recoverable_records = [r for r in records if r["path_group"] == "recoverable_real_execution"]
    normal_records = [r for r in records if r["path_group"] == "normal_real_execution_guardrail"]
    nonrecoverable_records = [r for r in records if r["path_group"] == "nonrecoverable_real_execution_guardrail"]
    code_fence_records = [r for r in recoverable_records if bool(r["code_fence_like"])]
    anchored_records = [r for r in records if bool(r["frozen_reference_case_id"])]

    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_case_count": len(records),
        "group_vs_current_handoff": {group: dict(counter) for group, counter in by_group_handoff.items()},
        "selected_parser_source_counts": dict(by_parser_source),
        "mismatch_type_counts": dict(mismatch_counts),
        "recoverable_real_execution_regression_count": int(mismatch_counts.get("recoverable_real_execution_regression", 0)),
        "code_fence_handoff_regression_count": int(mismatch_counts.get("code_fence_handoff_regression", 0)),
        "normal_real_execution_damage_count": int(mismatch_counts.get("normal_real_execution_damage", 0)),
        "nonrecoverable_real_execution_leak_count": int(mismatch_counts.get("nonrecoverable_real_execution_leak", 0)),
        "expected_behavior_drift_count": int(mismatch_counts.get("expected_behavior_drift", 0)),
        "frozen_reference_drift_count": int(mismatch_counts.get("frozen_reference_drift", 0)),
        "recoverable_real_execution_pass_rate": (
            sum(1 for r in recoverable_records if r["current_handoff"] == "pass_formatted_to_parser") / len(recoverable_records)
            if recoverable_records
            else None
        ),
        "code_fence_recoverable_pass_rate": (
            sum(1 for r in code_fence_records if r["current_handoff"] == "pass_formatted_to_parser") / len(code_fence_records)
            if code_fence_records
            else None
        ),
        "normal_real_execution_pass_rate": (
            sum(1 for r in normal_records if r["current_handoff"] == "pass_raw_to_parser") / len(normal_records)
            if normal_records
            else None
        ),
        "nonrecoverable_real_execution_block_rate": (
            sum(1 for r in nonrecoverable_records if r["current_handoff"] == "degeneration_blocked")
            / len(nonrecoverable_records)
            if nonrecoverable_records
            else None
        ),
        "all_cases_match_expected": all(bool(r["match_expected"]) for r in records),
        "anchored_case_count": len(anchored_records),
        "anchored_cases_match_frozen_reference": all(bool(r["match_frozen_reference"]) for r in anchored_records),
        "gate_status": gate_result.get("gate_status"),
        "gate_blocked_reason": gate_result.get("blocked_reason"),
        "logistic_status": logistic_status,
        "minimal_collateral_analysis": {
            "new_false_block_count": int(mismatch_counts.get("normal_real_execution_damage", 0)),
            "new_leak_count": int(mismatch_counts.get("nonrecoverable_real_execution_leak", 0)),
            "suite_path_ok_but_real_execution_unstable": bool(
                int(mismatch_counts.get("expected_behavior_drift", 0)) > 0
                or int(mismatch_counts.get("frozen_reference_drift", 0)) > 0
            ),
        },
        "frozen_reference_snapshots": reference_snapshots,
    }


def _report(summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Route-C Frozen Semantic Minimal Real Execution Validation Report")
    lines.append("")
    lines.append("## Real-Execution Summary")
    lines.append(f"- recoverable_real_execution_pass_rate: {summary['recoverable_real_execution_pass_rate']}")
    lines.append(f"- code_fence_recoverable_pass_rate: {summary['code_fence_recoverable_pass_rate']}")
    lines.append(f"- normal_real_execution_pass_rate: {summary['normal_real_execution_pass_rate']}")
    lines.append(f"- nonrecoverable_real_execution_block_rate: {summary['nonrecoverable_real_execution_block_rate']}")
    lines.append(f"- gate_status: {summary['gate_status']}")
    lines.append(f"- logistic_status: {summary['logistic_status']}")
    lines.append(f"- all_cases_match_expected: {summary['all_cases_match_expected']}")
    lines.append(f"- anchored_cases_match_frozen_reference: {summary['anchored_cases_match_frozen_reference']}")
    lines.append("")
    lines.append("## Minimal Collateral Analysis")
    collateral = summary["minimal_collateral_analysis"]
    lines.append(f"- new_false_block_count: {collateral['new_false_block_count']}")
    lines.append(f"- new_leak_count: {collateral['new_leak_count']}")
    lines.append(f"- suite_path_ok_but_real_execution_unstable: {collateral['suite_path_ok_but_real_execution_unstable']}")
    lines.append("")
    lines.append("## Case-Level Evidence")
    for record in records:
        lines.append(
            "- "
            + f"{record['case_id']}: expected {record['expected_handoff']} / {record['expected_category']} -> "
            + f"current {record['current_handoff']} / {record['current_category']} ({record['mismatch_type']})"
        )
    lines.append("")
    lines.append("## Before/After Frozen Reference")
    snapshots = summary["frozen_reference_snapshots"]
    lines.append(f"- stage_148_recoverable_pass_rate_reference: {snapshots['stage_148'].get('recoverable_pass_rate')}")
    lines.append(f"- stage_149_recoverable_pass_rate_reference: {snapshots['stage_149'].get('recoverable_pass_rate')}")
    lines.append(f"- stage_150_recoverable_path_pass_rate_reference: {snapshots['stage_150'].get('recoverable_path_pass_rate')}")
    lines.append(f"- stage_150_normal_path_pass_rate_reference: {snapshots['stage_150'].get('normal_path_pass_rate')}")
    lines.append(f"- stage_150_nonrecoverable_path_block_rate_reference: {snapshots['stage_150'].get('nonrecoverable_path_block_rate')}")
    return "\n".join(lines) + "\n"


def _load_reference_snapshots(stage_148_dir: Path, stage_149_dir: Path, stage_150_dir: Path) -> dict[str, Any]:
    stage_148_summary = load_json(_required_file(stage_148_dir / "route_c_recoverable_boundary_control_summary.json"))
    stage_149_summary = load_json(_required_file(stage_149_dir / "route_c_frozen_semantic_small_regression_summary.json"))
    stage_150_summary = load_json(_required_file(stage_150_dir / "route_c_frozen_semantic_minimal_execution_path_regression_summary.json"))
    return {
        "stage_148": {
            "recoverable_pass_rate": stage_148_summary.get("recoverable_pass_rate"),
            "normal_pass_through_rate": stage_148_summary.get("normal_pass_through_rate"),
            "nonrecoverable_block_rate": stage_148_summary.get("nonrecoverable_block_rate"),
        },
        "stage_149": {
            "recoverable_pass_rate": stage_149_summary.get("recoverable_pass_rate"),
            "normal_pass_through_rate": stage_149_summary.get("normal_pass_through_rate"),
            "nonrecoverable_block_rate": stage_149_summary.get("nonrecoverable_block_rate"),
        },
        "stage_150": {
            "recoverable_path_pass_rate": stage_150_summary.get("recoverable_path_pass_rate"),
            "normal_path_pass_rate": stage_150_summary.get("normal_path_pass_rate"),
            "nonrecoverable_path_block_rate": stage_150_summary.get("nonrecoverable_path_block_rate"),
            "all_cases_match_frozen_reference": stage_150_summary.get("all_cases_match_frozen_reference"),
        },
    }


def build_route_c_frozen_semantic_minimal_real_execution_validation(
    real_run_dir: Path,
    stage_148_dir: Path,
    stage_149_dir: Path,
    stage_150_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    reference_150_details = _load_150_details(stage_150_dir)
    reference_by_case = _reference_by_case_id(reference_150_details)
    real_raw_rows = _load_real_raw_rows(real_run_dir)
    real_health_rows = _load_real_health_rows(real_run_dir)
    real_fusion_rows = _load_real_fusion_rows(real_run_dir)

    cases = _minimal_real_execution_suite(real_raw_rows=real_raw_rows, reference_by_case=reference_by_case)
    suite = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "suite_name": "route_c_frozen_semantic_minimal_real_execution_v1",
        "case_count": len(cases),
        "group_counts": dict(Counter(case["path_group"] for case in cases)),
        "source_type_counts": dict(Counter(case["source_type"] for case in cases)),
        "real_execution_input_count": sum(1 for case in cases if bool(case["is_real_execution_input"])),
        "controlled_variant_count": sum(1 for case in cases if not bool(case["is_real_execution_input"])),
        "cases": cases,
    }

    rules = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_real_execution_criteria": [
            "recoverable cases must keep pass_formatted_to_parser",
            "code-fence-like recoverable cases must not regress to degeneration_blocked",
            "semantic_guess_used must remain false",
        ],
        "normal_real_execution_criteria": [
            "normal cases must keep pass_raw_to_parser",
            "normal cases must not gain new collateral damage",
        ],
        "nonrecoverable_real_execution_criteria": [
            "nonrecoverable cases must keep degeneration_blocked",
            "recoverable-boundary repair must not leak nonrecoverable rows into parser",
        ],
        "real_execution_consistency_criteria": [
            "parser/gate/label-health/handoff semantics remain coherent",
            "impact scope stays local to recoverable boundary",
            "no contract drift introduced by this stage",
        ],
    }

    execution_root_dir = output_dir / "minimal_real_execution_root"
    input_manifest = _materialize_real_execution_inputs(
        cases=cases,
        real_raw_rows=real_raw_rows,
        real_fusion_rows=real_fusion_rows,
        execution_root_dir=execution_root_dir,
    )

    dataset_dir = execution_root_dir / "route_c_v6_dataset_dir"
    dataset_result = build_benchmark_truth_leaning_dataset(
        expanded_real_pilot_fusion_dataset_path=execution_root_dir / "execution_inputs" / "minimal_real_execution_fusion_dataset.jsonl",
        labeled_illumination_raw_results_path=execution_root_dir / "execution_inputs" / "minimal_real_execution_labeled_raw_results.jsonl",
        output_dir=dataset_dir,
        fusion_profile="route_c_frozen_semantic_minimal_real_execution",
        run_id="route_c_frozen_semantic_minimal_real_execution",
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
            fusion_profile="route_c_frozen_semantic_minimal_real_execution",
            run_id="route_c_frozen_semantic_minimal_real_execution",
            label_threshold=label_threshold,
            random_seed=seed,
        )
        logistic_status = "PASS"
        logistic_output_paths = logistic_result["output_paths"]
    else:
        logistic_status = "BLOCKED_BY_GATE"

    health_rows = load_jsonl(dataset_dir / "benchmark_truth_leaning_label_health_rows.jsonl")
    records = _evaluate_records(cases=cases, health_rows=health_rows)
    reference_snapshots = _load_reference_snapshots(
        stage_148_dir=stage_148_dir,
        stage_149_dir=stage_149_dir,
        stage_150_dir=stage_150_dir,
    )
    summary = _summary(
        records=records,
        gate_result=gate_result["summary"],
        logistic_status=logistic_status,
        reference_snapshots=reference_snapshots,
    )
    report = _report(summary=summary, records=records)

    write_json(output_dir / "route_c_frozen_semantic_minimal_real_execution_suite.json", suite)
    write_json(output_dir / "route_c_frozen_semantic_minimal_real_execution_rules.json", rules)
    write_json(output_dir / "route_c_frozen_semantic_minimal_real_execution_summary.json", summary)
    write_jsonl(output_dir / "route_c_frozen_semantic_minimal_real_execution_details.jsonl", records)
    (output_dir / "route_c_frozen_semantic_minimal_real_execution_report.md").write_text(report, encoding="utf-8")

    write_json(
        output_dir / "config_snapshot.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "real_run_dir": str(real_run_dir.resolve()),
            "stage_148_dir": str(stage_148_dir.resolve()),
            "stage_149_dir": str(stage_149_dir.resolve()),
            "stage_150_dir": str(stage_150_dir.resolve()),
            "seed": seed,
            "label_threshold": label_threshold,
            "input_manifest_path": str(
                (execution_root_dir / "execution_inputs" / "real_execution_input_manifest.json").resolve()
            ),
            "real_health_row_count_reference": len(real_health_rows),
        },
    )

    return {
        "suite": suite,
        "rules": rules,
        "summary": summary,
        "output_paths": {
            "suite": str((output_dir / "route_c_frozen_semantic_minimal_real_execution_suite.json").resolve()),
            "rules": str((output_dir / "route_c_frozen_semantic_minimal_real_execution_rules.json").resolve()),
            "summary": str((output_dir / "route_c_frozen_semantic_minimal_real_execution_summary.json").resolve()),
            "details": str((output_dir / "route_c_frozen_semantic_minimal_real_execution_details.jsonl").resolve()),
            "report": str((output_dir / "route_c_frozen_semantic_minimal_real_execution_report.md").resolve()),
            "execution_input_manifest": str(
                (execution_root_dir / "execution_inputs" / "real_execution_input_manifest.json").resolve()
            ),
            "dataset_summary": dataset_result["output_paths"]["summary"],
            "label_health_summary": dataset_result["output_paths"]["label_health_summary"],
            "gate_result": gate_result["output_paths"]["gate_result"],
            "logistic_summary": logistic_output_paths.get("summary"),
            "real_run_dir": str(real_run_dir.resolve()),
            "input_manifest_summary_status": input_manifest["summary_status"],
        },
    }
