"""Small frozen-semantic regression validation for route_c recoverable-boundary behavior."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_jsonl, write_json, write_jsonl
from src.fusion.benchmark_truth_leaning_label import build_output_antidegradation_record


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-small-regression-validation/v1"


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def _load_148_records(boundary_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(boundary_dir / "route_c_recoverable_boundary_control_details.jsonl"))


def _by_case_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record["case_id"]): record for record in records}


def _regression_suite(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_case_id = _by_case_id(records)
    selected_case_ids = [
        "focused::controlled_recoverable::code_fence",
        "focused::new_recoverable::code_fence_lang_tag",
        "focused::controlled_recoverable::quote_wrap",
        "focused::controlled_recoverable::prefix_noise",
        "focused::real_normal::csqa-pilot-002__control",
        "focused::real_normal::csqa-pilot-021__control",
        "focused::real_unrecoverable::csqa-pilot-021__targeted",
        "focused::real_unrecoverable::csqa-pilot-002__control",
        "focused::new_nonrecoverable::code_fence_punct_only",
        "focused::new_nonrecoverable::code_fence_contract_broken",
    ]

    suite: list[dict[str, Any]] = []
    for case_id in selected_case_ids:
        record = by_case_id[case_id]
        suite_group = str(record["suite_group"])
        if suite_group == "recoverable_boundary_focus":
            regression_group = "recoverable_boundary_positive"
        elif suite_group == "normal_parser_reachable_guardrail":
            regression_group = "normal_guardrail"
        else:
            regression_group = "nonrecoverable_guardrail"

        suite.append(
            {
                "case_id": case_id,
                "regression_group": regression_group,
                "source_type": record["source_type"],
                "base_source_case_id": record["base_source_case_id"],
                "case_note": record["case_note"],
                "raw_response": record["raw_response"],
                "query_answer_key": record["query_answer_key"],
                "frozen_reference_handoff": record["current_handoff"],
                "frozen_reference_category": record["current_category"],
                "frozen_reference_recoverability": record["current_recoverability"],
                "frozen_reference_parser_input_text": record["current_parser_input_text"],
                "semantic_guess_allowed": False,
            }
        )
    return suite


def _suite_manifest(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "suite_name": "route_c_frozen_semantic_small_regression_v1",
        "case_count": len(cases),
        "group_counts": dict(Counter(case["regression_group"] for case in cases)),
        "source_type_counts": dict(Counter(case["source_type"] for case in cases)),
        "cases": cases,
    }


def _rules() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_path_regression_criteria": [
            "recoverable cases must keep pass_formatted_to_parser",
            "recoverable cases must not regress to degeneration_blocked",
            "semantic_guess_allowed must remain false",
        ],
        "normal_guardrail_criteria": [
            "normal cases must keep pass_raw_to_parser",
            "normal cases must not gain new collateral damage",
        ],
        "nonrecoverable_guardrail_criteria": [
            "nonrecoverable cases must keep degeneration_blocked",
            "nonrecoverable cases must not leak into parser",
        ],
        "change_scope_criteria": [
            "frozen reference uses stage-148 current outcomes",
            "benchmark truth semantics unchanged",
            "gate semantics unchanged",
            "no new formatter scope beyond recoverable boundary",
        ],
    }


def _evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    allowed_labels = {case["query_answer_key"]} if case["query_answer_key"] else {"A", "B", "C", "D"}
    current = build_output_antidegradation_record(
        response_text=case["raw_response"],
        parse_mode="robust_prefix",
        allowed_labels=allowed_labels,
        normalization_mode="conservative",
    )

    current_handoff = current["parser_handoff"]
    current_category = current["degeneration_category"]
    current_recoverability = current["recoverability"]
    all_reference_match = (
        current_handoff == case["frozen_reference_handoff"]
        and current_category == case["frozen_reference_category"]
        and current_recoverability == case["frozen_reference_recoverability"]
    )

    if case["regression_group"] == "recoverable_boundary_positive" and current_handoff != "pass_formatted_to_parser":
        mismatch_type = "recoverable_regression_failure"
    elif case["regression_group"] == "normal_guardrail" and current_handoff != "pass_raw_to_parser":
        mismatch_type = "normal_guardrail_damage"
    elif case["regression_group"] == "nonrecoverable_guardrail" and current_handoff != "degeneration_blocked":
        mismatch_type = "nonrecoverable_guardrail_leak"
    elif not all_reference_match:
        mismatch_type = "reference_drift"
    else:
        mismatch_type = "match"

    return {
        "schema_version": SCHEMA_VERSION,
        **case,
        "current_handoff": current_handoff,
        "current_category": current_category,
        "current_recoverability": current_recoverability,
        "current_parser_input_text": current["parser_input_text"],
        "current_formatter_steps": current["formatter_steps"],
        "all_reference_match": all_reference_match,
        "mismatch_type": mismatch_type,
    }


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_group_handoff: dict[str, Counter[str]] = defaultdict(Counter)
    mismatches = Counter(record["mismatch_type"] for record in records)
    for record in records:
        by_group_handoff[record["regression_group"]][record["current_handoff"]] += 1

    recoverable_records = [r for r in records if r["regression_group"] == "recoverable_boundary_positive"]
    normal_records = [r for r in records if r["regression_group"] == "normal_guardrail"]
    nonrecoverable_records = [r for r in records if r["regression_group"] == "nonrecoverable_guardrail"]

    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_case_count": len(records),
        "group_vs_current_handoff": {group: dict(counter) for group, counter in by_group_handoff.items()},
        "mismatch_type_counts": dict(mismatches),
        "recoverable_regression_failure_count": int(mismatches.get("recoverable_regression_failure", 0)),
        "normal_guardrail_damage_count": int(mismatches.get("normal_guardrail_damage", 0)),
        "nonrecoverable_guardrail_leak_count": int(mismatches.get("nonrecoverable_guardrail_leak", 0)),
        "reference_drift_count": int(mismatches.get("reference_drift", 0)),
        "recoverable_pass_rate": (
            sum(1 for r in recoverable_records if r["current_handoff"] == "pass_formatted_to_parser") / len(recoverable_records)
            if recoverable_records
            else None
        ),
        "normal_pass_through_rate": (
            sum(1 for r in normal_records if r["current_handoff"] == "pass_raw_to_parser") / len(normal_records)
            if normal_records
            else None
        ),
        "nonrecoverable_block_rate": (
            sum(1 for r in nonrecoverable_records if r["current_handoff"] == "degeneration_blocked") / len(nonrecoverable_records)
            if nonrecoverable_records
            else None
        ),
        "all_cases_match_frozen_reference": all(record["all_reference_match"] for record in records),
        "controlled_validation_executed": False,
        "controlled_validation_note": "Regression validation reuses frozen stage-148 evidence and reruns only the current helper path.",
    }


def _report(suite: dict[str, Any], rules: dict[str, Any], summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Route-C Frozen Semantic Small Regression Report")
    lines.append("")
    lines.append("## Frozen Scope")
    lines.append("- benchmark truth semantics unchanged")
    lines.append("- gate semantics unchanged")
    lines.append("- recoverable boundary scope frozen to stage-148 rule set")
    lines.append("")
    lines.append("## Suite Coverage")
    lines.append(f"- total_case_count: {suite['case_count']}")
    for key, value in suite["group_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Regression Summary")
    lines.append(f"- recoverable_pass_rate: {summary['recoverable_pass_rate']}")
    lines.append(f"- normal_pass_through_rate: {summary['normal_pass_through_rate']}")
    lines.append(f"- nonrecoverable_block_rate: {summary['nonrecoverable_block_rate']}")
    lines.append(f"- all_cases_match_frozen_reference: {summary['all_cases_match_frozen_reference']}")
    lines.append(f"- mismatch_type_counts: {summary['mismatch_type_counts']}")
    lines.append("")
    lines.append("## Key Cases")
    for record in records[:10]:
        lines.append(
            "- "
            + f"{record['case_id']}: ref {record['frozen_reference_handoff']} / {record['frozen_reference_category']} -> "
            + f"current {record['current_handoff']} / {record['current_category']} ({record['mismatch_type']})"
        )
    return "\n".join(lines) + "\n"


def build_route_c_frozen_semantic_small_regression_validation(
    recoverable_boundary_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    prior_records = _load_148_records(recoverable_boundary_dir)
    cases = _regression_suite(prior_records)
    records = [_evaluate_case(case) for case in cases]
    suite = _suite_manifest(cases)
    rules = _rules()
    summary = _summary(records)
    report = _report(suite=suite, rules=rules, summary=summary, records=records)

    write_json(output_dir / "route_c_frozen_semantic_small_regression_suite.json", suite)
    write_json(output_dir / "route_c_frozen_semantic_small_regression_rules.json", rules)
    write_json(output_dir / "route_c_frozen_semantic_small_regression_summary.json", summary)
    write_jsonl(output_dir / "route_c_frozen_semantic_small_regression_details.jsonl", records)
    (output_dir / "route_c_frozen_semantic_small_regression_report.md").write_text(report, encoding="utf-8")

    return {
        "suite": suite,
        "rules": rules,
        "summary": summary,
        "output_paths": {
            "suite": str((output_dir / "route_c_frozen_semantic_small_regression_suite.json").resolve()),
            "rules": str((output_dir / "route_c_frozen_semantic_small_regression_rules.json").resolve()),
            "summary": str((output_dir / "route_c_frozen_semantic_small_regression_summary.json").resolve()),
            "details": str((output_dir / "route_c_frozen_semantic_small_regression_details.jsonl").resolve()),
            "report": str((output_dir / "route_c_frozen_semantic_small_regression_report.md").resolve()),
        },
    }
