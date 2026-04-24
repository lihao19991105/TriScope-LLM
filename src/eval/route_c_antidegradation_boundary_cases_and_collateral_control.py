"""Boundary-case and collateral-control validation for route_c anti-degradation."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_jsonl, write_json, write_jsonl
from src.fusion.benchmark_truth_leaning_label import build_output_antidegradation_record


SCHEMA_VERSION = "triscopellm/route-c-antidegradation-boundary-cases-and-collateral-control/v1"


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def _shorten(text: str, max_chars: int = 120) -> str:
    compact = " ".join(str(text).split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3] + "..."


def _load_health_rows(run_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_health_rows.jsonl"))


def _find_real_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    parser_reachable = [row for row in rows if row.get("raw_parser_outcome", {}).get("parsed_label") is not None]
    contract_broken = next(
        (
            row
            for row in rows
            if row.get("raw_parser_outcome", {}).get("parsed_label") is None
            and str(row.get("parse_failure_category")) in {"unknown_token", "other"}
        ),
        None,
    )
    if contract_broken is None:
        raise ValueError("Could not find a representative contract-broken row in the provided stage-143 rows.")
    return parser_reachable, contract_broken


def _build_suite_cases(stage_143_rows: list[dict[str, Any]], stage_144_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    parser_reachable_rows, contract_broken_row = _find_real_rows(stage_143_rows)
    if not parser_reachable_rows:
        raise ValueError("Could not find parser-reachable stage-143 rows.")
    normal_template = parser_reachable_rows[0]
    punct_template = stage_144_rows[0]

    cases: list[dict[str, Any]] = []

    for row in stage_144_rows:
        cases.append(
            {
                "case_id": f"real_unrecoverable::{row['sample_id']}",
                "source_type": "real",
                "source_stage": "144",
                "base_origin": str(row["sample_id"]),
                "suite_group": "clearly_unrecoverable_degeneration",
                "expected_category": "punctuation_collapse",
                "expected_handoff": "degeneration_blocked",
                "expected_recoverability": "not_recoverable",
                "format_mutation_only": False,
                "semantic_guess_allowed": False,
                "raw_response": str(row.get("raw_response", "")),
                "query_answer_key": str(row.get("query_answer_key", "")),
                "case_note": "real time-separated regression punctuation collapse",
            }
        )

    for row in parser_reachable_rows:
        cases.append(
            {
                "case_id": f"real_normal::{row['sample_id']}",
                "source_type": "real",
                "source_stage": "143",
                "base_origin": str(row["sample_id"]),
                "suite_group": "clearly_normal_parser_reachable_responses",
                "expected_category": "parser_reachable",
                "expected_handoff": "pass_raw_to_parser",
                "expected_recoverability": "not_needed",
                "format_mutation_only": False,
                "semantic_guess_allowed": False,
                "raw_response": str(row.get("raw_response", "")),
                "query_answer_key": str(row.get("query_answer_key", "")),
                "case_note": "real stage-143 parser-reachable baseline row",
            }
        )

    cases.append(
        {
            "case_id": f"real_ambiguous_nonrecoverable::{contract_broken_row['sample_id']}",
            "source_type": "real",
            "source_stage": "143",
            "base_origin": str(contract_broken_row["sample_id"]),
            "suite_group": "ambiguous_but_still_nonrecoverable_cases",
            "expected_category": "contract_broken_response",
            "expected_handoff": "degeneration_blocked",
            "expected_recoverability": "not_recoverable",
            "format_mutation_only": False,
            "semantic_guess_allowed": False,
            "raw_response": str(contract_broken_row.get("raw_response", "")),
            "query_answer_key": str(contract_broken_row.get("query_answer_key", "")),
            "case_note": "real stage-143 non-parse row retained for ambiguity boundary",
        }
    )

    normal_text = str(normal_template.get("raw_response", ""))
    normal_key = str(normal_template.get("query_answer_key", ""))
    recoverable_variants = [
        ("controlled_recoverable::quote_wrap", f"\"{normal_text}\"", "quote wrapper only"),
        ("controlled_recoverable::bracket_wrap", f"[{normal_text}]", "single bracket wrapper only"),
        ("controlled_recoverable::prefix_noise", f"Answer: {normal_text}", "prefix noise only"),
        ("controlled_recoverable::bullet_prefix", f"- {normal_text}", "bullet prefix only"),
        ("controlled_recoverable::code_fence", f"```{normal_text}```", "single markdown code fence wrapper"),
    ]
    for case_id, raw_response, case_note in recoverable_variants:
        cases.append(
            {
                "case_id": case_id,
                "source_type": "controlled-format-variant",
                "source_stage": "143",
                "base_origin": str(normal_template["sample_id"]),
                "suite_group": "recoverable_formatting_boundary_cases",
                "expected_category": "recoverable_formatting_issue",
                "expected_handoff": "pass_formatted_to_parser",
                "expected_recoverability": "recoverable",
                "format_mutation_only": True,
                "semantic_guess_allowed": False,
                "raw_response": raw_response,
                "query_answer_key": normal_key,
                "case_note": case_note,
            }
        )

    broken_text = str(contract_broken_row.get("raw_response", ""))
    broken_key = str(contract_broken_row.get("query_answer_key", ""))
    ambiguous_variants = [
        ("controlled_ambiguous::quote_wrap", f"\"{broken_text}\"", "quote wrapper around real contract-broken row"),
        ("controlled_ambiguous::prefix_noise", f"Answer: {broken_text}", "prefix noise around real contract-broken row"),
        ("controlled_ambiguous::bracket_wrap", f"[{broken_text}]", "bracket wrapper around real contract-broken row"),
        ("controlled_ambiguous::prefixed_punct", "Answer: ???", "structured but still no label token"),
    ]
    for case_id, raw_response, case_note in ambiguous_variants:
        cases.append(
            {
                "case_id": case_id,
                "source_type": "controlled-format-variant",
                "source_stage": "143_or_144_boundary",
                "base_origin": str(contract_broken_row["sample_id"]),
                "suite_group": "ambiguous_but_still_nonrecoverable_cases",
                "expected_category": "contract_broken_response",
                "expected_handoff": "degeneration_blocked",
                "expected_recoverability": "not_recoverable",
                "format_mutation_only": True,
                "semantic_guess_allowed": False,
                "raw_response": raw_response,
                "query_answer_key": broken_key,
                "case_note": case_note,
            }
        )

    punct_key = str(punct_template.get("query_answer_key", ""))
    unrecoverable_variants = [
        ("controlled_unrecoverable::mixed_punct", "?!?!!!", "format-only punct-only variant"),
        ("controlled_unrecoverable::whitespace_like", "   \t  ", "whitespace-like degenerate variant"),
        ("controlled_unrecoverable::quoted_punct", "\"???!!!\"", "punctuation wrapped with quotes"),
    ]
    for case_id, raw_response, case_note in unrecoverable_variants:
        expected_category = "empty_whitespace_like" if raw_response.strip() == "" else "punctuation_collapse"
        cases.append(
            {
                "case_id": case_id,
                "source_type": "controlled-format-variant",
                "source_stage": "144",
                "base_origin": str(punct_template["sample_id"]),
                "suite_group": "clearly_unrecoverable_degeneration",
                "expected_category": expected_category,
                "expected_handoff": "degeneration_blocked",
                "expected_recoverability": "not_recoverable",
                "format_mutation_only": True,
                "semantic_guess_allowed": False,
                "raw_response": raw_response,
                "query_answer_key": punct_key,
                "case_note": case_note,
            }
        )
    return cases


def _evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    anti = build_output_antidegradation_record(
        response_text=case["raw_response"],
        parse_mode="robust_prefix",
        allowed_labels={case["query_answer_key"]} if case["query_answer_key"] else {"A", "B", "C", "D"},
        normalization_mode="conservative",
    )
    observed_handoff = anti["parser_handoff"]
    observed_category = anti["degeneration_category"]
    observed_recoverability = anti["recoverability"]

    match_handoff = observed_handoff == case["expected_handoff"]
    match_category = observed_category == case["expected_category"]
    match_recoverability = observed_recoverability == case["expected_recoverability"]

    if case["suite_group"] == "recoverable_formatting_boundary_cases" and observed_handoff != "pass_formatted_to_parser":
        mismatch_type = "recoverable_boundary_overblocked"
    elif case["suite_group"] == "clearly_normal_parser_reachable_responses" and observed_handoff != "pass_raw_to_parser":
        mismatch_type = "normal_collateral_damage"
    elif case["expected_handoff"] != "degeneration_blocked" and observed_handoff == "degeneration_blocked":
        mismatch_type = "false_positive_degeneration"
    elif case["expected_handoff"] == "degeneration_blocked" and observed_handoff != "degeneration_blocked":
        mismatch_type = "false_negative_degeneration"
    elif match_handoff and match_category and match_recoverability:
        mismatch_type = "match"
    else:
        mismatch_type = "other_boundary_mismatch"

    return {
        "schema_version": SCHEMA_VERSION,
        **case,
        "observed_category": observed_category,
        "observed_handoff": observed_handoff,
        "observed_recoverability": observed_recoverability,
        "observed_formatter_applied": anti["formatter_applied"],
        "observed_formatter_steps": anti["formatter_steps"],
        "observed_parser_input_source": anti["parser_input_source"],
        "observed_parser_input_text": anti["parser_input_text"],
        "observed_raw_parser_outcome": anti["raw_parser_outcome"],
        "observed_normalized_response": anti["normalized_response"],
        "observed_normalized_parser_outcome": anti["normalized_parser_outcome"],
        "match_handoff": match_handoff,
        "match_category": match_category,
        "match_recoverability": match_recoverability,
        "all_expectations_met": match_handoff and match_category and match_recoverability,
        "mismatch_type": mismatch_type,
    }


def _suite_manifest(cases: list[dict[str, Any]]) -> dict[str, Any]:
    group_counts = Counter(case["suite_group"] for case in cases)
    source_counts = Counter(case["source_type"] for case in cases)
    category_counts = Counter(case["expected_category"] for case in cases)
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "suite_name": "route_c_antidegradation_boundary_control_minimal_v1",
        "case_count": len(cases),
        "group_counts": dict(group_counts),
        "source_type_counts": dict(source_counts),
        "expected_category_counts": dict(category_counts),
        "cases": cases,
    }


def _rules() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "false_positive_definition": {
            "normal_parser_reachable_blocked": True,
            "recoverable_boundary_blocked": True,
        },
        "false_negative_definition": {
            "clearly_unrecoverable_not_blocked": True,
            "ambiguous_nonrecoverable_marked_recoverable": True,
        },
        "acceptable_boundary": {
            "clearly_unrecoverable_degeneration": "must_be_blocked",
            "clearly_normal_parser_reachable_responses": "must_remain_pass_raw_to_parser",
            "ambiguous_but_still_nonrecoverable_cases": "conservative_blocking_is_acceptable",
            "recoverable_formatting_boundary_cases": "should_pass_formatted_to_parser_without_semantic_guess",
        },
        "highest_risk_boundary_types_pre_validation": [
            "recoverable_formatting_boundary_cases",
            "contract_broken_response_vs_recoverable_formatting_issue",
            "markdown_code_fence_wrapped_label_like_outputs",
        ],
    }


def _build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_group_handoff: dict[str, Counter[str]] = defaultdict(Counter)
    mismatches: Counter[str] = Counter()
    for record in records:
        by_group_handoff[record["suite_group"]][record["observed_handoff"]] += 1
        mismatches[record["mismatch_type"]] += 1

    recoverable_records = [r for r in records if r["suite_group"] == "recoverable_formatting_boundary_cases"]
    normal_records = [r for r in records if r["suite_group"] == "clearly_normal_parser_reachable_responses"]
    unrecoverable_records = [r for r in records if r["suite_group"] == "clearly_unrecoverable_degeneration"]
    ambiguous_records = [r for r in records if r["suite_group"] == "ambiguous_but_still_nonrecoverable_cases"]

    risky_groups = sorted(
        (
            {
                "suite_group": group,
                "mismatch_count": sum(1 for r in records if r["suite_group"] == group and not r["all_expectations_met"]),
                "case_count": sum(1 for r in records if r["suite_group"] == group),
            }
            for group in sorted({r["suite_group"] for r in records})
        ),
        key=lambda item: (-item["mismatch_count"], -item["case_count"], item["suite_group"]),
    )

    false_positive_degeneration_count = sum(
        1
        for r in records
        if (
            r["suite_group"] == "recoverable_formatting_boundary_cases"
            and r["observed_handoff"] == "degeneration_blocked"
        )
        or (
            r["suite_group"] == "clearly_normal_parser_reachable_responses"
            and r["observed_handoff"] == "degeneration_blocked"
        )
    )
    false_negative_degeneration_count = sum(
        1
        for r in records
        if (
            r["suite_group"] == "clearly_unrecoverable_degeneration"
            and r["observed_handoff"] != "degeneration_blocked"
        )
        or (
            r["suite_group"] == "ambiguous_but_still_nonrecoverable_cases"
            and r["observed_handoff"] != "degeneration_blocked"
        )
    )
    normal_collateral_damage_count = sum(
        1
        for r in records
        if r["suite_group"] == "clearly_normal_parser_reachable_responses"
        and r["observed_handoff"] != "pass_raw_to_parser"
    )
    recoverable_boundary_overblocked_count = sum(
        1
        for r in records
        if r["suite_group"] == "recoverable_formatting_boundary_cases"
        and r["observed_handoff"] != "pass_formatted_to_parser"
    )

    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_case_count": len(records),
        "all_cases_expected_behavior_met": all(r["all_expectations_met"] for r in records),
        "expected_group_vs_observed_handoff": {
            group: dict(counter) for group, counter in by_group_handoff.items()
        },
        "mismatch_type_counts": dict(mismatches),
        "false_positive_degeneration_count": false_positive_degeneration_count,
        "false_negative_degeneration_count": false_negative_degeneration_count,
        "normal_collateral_damage_count": normal_collateral_damage_count,
        "recoverable_boundary_overblocked_count": recoverable_boundary_overblocked_count,
        "recoverable_boundary_pass_rate": (
            sum(1 for r in recoverable_records if r["observed_handoff"] == "pass_formatted_to_parser") / len(recoverable_records)
            if recoverable_records
            else None
        ),
        "normal_pass_through_rate": (
            sum(1 for r in normal_records if r["observed_handoff"] == "pass_raw_to_parser") / len(normal_records)
            if normal_records
            else None
        ),
        "unrecoverable_block_rate": (
            sum(1 for r in unrecoverable_records if r["observed_handoff"] == "degeneration_blocked") / len(unrecoverable_records)
            if unrecoverable_records
            else None
        ),
        "ambiguous_nonrecoverable_block_rate": (
            sum(1 for r in ambiguous_records if r["observed_handoff"] == "degeneration_blocked") / len(ambiguous_records)
            if ambiguous_records
            else None
        ),
        "top_boundary_risk_types": risky_groups[:3],
        "controlled_validation_executed": False,
        "controlled_validation_note": "Boundary-case suite uses helper-level controlled-format variants only; no replay/model rerun was executed.",
    }


def _build_markdown_report(suite: dict[str, Any], rules: dict[str, Any], summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Route-C Antidegradation Boundary Control Report")
    lines.append("")
    lines.append("## Suite Coverage")
    lines.append(f"- total_case_count: {suite['case_count']}")
    for key, value in suite["group_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## False-Positive / False-Negative Criteria")
    lines.append("- false_positive_degeneration: normal parser-reachable or recoverable boundary is blocked")
    lines.append("- false_negative_degeneration: clearly unrecoverable or ambiguous-nonrecoverable case is allowed into parser")
    lines.append("")
    lines.append("## Validation Summary")
    lines.append(f"- normal_pass_through_rate: {summary['normal_pass_through_rate']}")
    lines.append(f"- unrecoverable_block_rate: {summary['unrecoverable_block_rate']}")
    lines.append(f"- ambiguous_nonrecoverable_block_rate: {summary['ambiguous_nonrecoverable_block_rate']}")
    lines.append(f"- recoverable_boundary_pass_rate: {summary['recoverable_boundary_pass_rate']}")
    lines.append(f"- false_positive_degeneration_count: {summary['false_positive_degeneration_count']}")
    lines.append(f"- false_negative_degeneration_count: {summary['false_negative_degeneration_count']}")
    lines.append(f"- recoverable_boundary_overblocked_count: {summary['recoverable_boundary_overblocked_count']}")
    lines.append("")
    lines.append("## Most Sensitive Boundary Cases")
    for record in [r for r in records if not r["all_expectations_met"]][:5]:
        lines.append(
            "- "
            + f"{record['case_id']} => expected {record['expected_handoff']} / {record['expected_category']}, "
            + f"observed {record['observed_handoff']} / {record['observed_category']} ({record['mismatch_type']})"
        )
    if not any(not r["all_expectations_met"] for r in records):
        lines.append("- no mismatches observed")
    lines.append("")
    lines.append("## Notes")
    lines.append("- Controlled-format variants are explicitly synthetic and are not presented as real recovered regressions.")
    lines.append("- No benchmark truth or gate semantics were changed in this stage.")
    return "\n".join(lines) + "\n"


def build_route_c_antidegradation_boundary_cases_and_collateral_control(
    stage_143_run_dir: Path,
    stage_144_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    stage_143_rows = _load_health_rows(stage_143_run_dir)
    stage_144_rows = _load_health_rows(stage_144_run_dir)
    cases = _build_suite_cases(stage_143_rows=stage_143_rows, stage_144_rows=stage_144_rows)
    records = [_evaluate_case(case) for case in cases]

    suite = _suite_manifest(cases)
    rules = _rules()
    summary = _build_summary(records)
    report = _build_markdown_report(suite=suite, rules=rules, summary=summary, records=records)

    write_json(output_dir / "route_c_antidegradation_boundary_control_suite.json", suite)
    write_json(output_dir / "route_c_antidegradation_boundary_control_rules.json", rules)
    write_json(output_dir / "route_c_antidegradation_boundary_control_summary.json", summary)
    write_jsonl(output_dir / "route_c_antidegradation_boundary_control_details.jsonl", records)
    (output_dir / "route_c_antidegradation_boundary_control_report.md").write_text(report, encoding="utf-8")

    return {
        "suite": suite,
        "rules": rules,
        "summary": summary,
        "output_paths": {
            "suite": str((output_dir / "route_c_antidegradation_boundary_control_suite.json").resolve()),
            "rules": str((output_dir / "route_c_antidegradation_boundary_control_rules.json").resolve()),
            "summary": str((output_dir / "route_c_antidegradation_boundary_control_summary.json").resolve()),
            "details": str((output_dir / "route_c_antidegradation_boundary_control_details.jsonl").resolve()),
            "report": str((output_dir / "route_c_antidegradation_boundary_control_report.md").resolve()),
        },
    }
