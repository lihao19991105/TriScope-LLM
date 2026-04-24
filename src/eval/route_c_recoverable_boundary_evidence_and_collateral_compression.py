"""Focused recoverable-boundary evidence and collateral-compression for route_c anti-degradation."""

from __future__ import annotations

from collections import Counter, defaultdict
import re
import unicodedata
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_jsonl, write_json, write_jsonl
from src.fusion.benchmark_truth_leaning_label import (
    ALNUM_TOKEN_PATTERN,
    ANTI_DEGRADATION_ALLOWED_FORMAT_STEPS,
    BRACKET_WRAPPERS,
    BULLET_PREFIX_PATTERN,
    LEADING_TRAILING_PUNCT_PATTERN,
    POTENTIAL_JSON_PATTERN,
    PREFIX_NOISE_PATTERN,
    PUNCT_ONLY_PATTERN,
    PUNCT_TRANSLATION_TABLE,
    QUOTE_WRAPPERS,
    _parse_outcome,
    build_output_antidegradation_record,
)


SCHEMA_VERSION = "triscopellm/route-c-recoverable-boundary-evidence-and-collateral-compression/v1"
LEGACY_MARKDOWN_CODE_FENCE_PATTERN = re.compile(r"^```[A-Za-z0-9_-]*\s*(.*?)\s*```$", flags=re.DOTALL)


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def _load_147_records(boundary_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(boundary_dir / "route_c_antidegradation_boundary_control_details.jsonl"))


def _legacy_normalize_response_format(response_text: str) -> tuple[str, list[str]]:
    trace: list[str] = []
    normalized = response_text

    nfkc = unicodedata.normalize("NFKC", normalized)
    if nfkc != normalized:
        trace.append("unicode_nfkc")
    normalized = nfkc

    translated = normalized.translate(PUNCT_TRANSLATION_TABLE)
    if translated != normalized:
        trace.append("punctuation_normalized")
    normalized = translated

    stripped = normalized.strip()
    code_fence_match = LEGACY_MARKDOWN_CODE_FENCE_PATTERN.match(stripped)
    if code_fence_match is not None:
        normalized = code_fence_match.group(1).strip()
        trace.append("markdown_code_fence_removed")

    bullet_cleaned = BULLET_PREFIX_PATTERN.sub("", normalized, count=1)
    if bullet_cleaned != normalized:
        normalized = bullet_cleaned
        trace.append("bullet_prefix_removed")

    prefix_removed = normalized
    while True:
        candidate = PREFIX_NOISE_PATTERN.sub("", prefix_removed, count=1)
        if candidate == prefix_removed:
            break
        prefix_removed = candidate
        trace.append("prefix_noise_removed")
    normalized = prefix_removed

    for _ in range(3):
        candidate = normalized.strip()
        removed = False
        for left, right in QUOTE_WRAPPERS:
            if len(candidate) >= 2 and candidate.startswith(left) and candidate.endswith(right):
                inner = candidate[len(left) : len(candidate) - len(right)].strip()
                if inner:
                    normalized = inner
                    trace.append("quote_wrapper_removed")
                    removed = True
                    break
        if removed:
            continue
        for left, right in BRACKET_WRAPPERS:
            if len(candidate) >= 2 and candidate.startswith(left) and candidate.endswith(right):
                inner = candidate[len(left) : len(candidate) - len(right)].strip()
                if inner:
                    normalized = inner
                    trace.append("bracket_wrapper_removed")
                    removed = True
                    break
        if not removed:
            break

    punct_trimmed = LEADING_TRAILING_PUNCT_PATTERN.sub("", normalized)
    if punct_trimmed != normalized:
        normalized = punct_trimmed
        trace.append("edge_punctuation_trimmed")

    return normalized.strip(), trace


def _build_legacy_output_antidegradation_record(
    response_text: str,
    parse_mode: str,
    allowed_labels: set[str],
) -> dict[str, Any]:
    raw_outcome = _parse_outcome(text=response_text, parse_mode=parse_mode, allowed_labels=allowed_labels)
    normalized_response, normalization_trace = _legacy_normalize_response_format(response_text)
    normalized_outcome = _parse_outcome(text=normalized_response, parse_mode=parse_mode, allowed_labels=allowed_labels)

    stripped = response_text.strip()
    normalized_stripped = normalized_response.strip()
    alnum_tokens = ALNUM_TOKEN_PATTERN.findall(stripped.upper())
    unknown_tokens = [token for token in alnum_tokens if token not in allowed_labels]
    formatter_only_recoverable = bool(
        raw_outcome.get("parsed_label") is None
        and normalized_outcome.get("parsed_label") is not None
        and normalization_trace
        and set(normalization_trace).issubset(ANTI_DEGRADATION_ALLOWED_FORMAT_STEPS)
    )

    if raw_outcome.get("parsed_label") is not None:
        category = "parser_reachable"
        recoverability = "not_needed"
        handoff = "pass_raw_to_parser"
        parser_input_source = "raw"
        parser_input_text = response_text
    elif stripped == "":
        category = "empty_whitespace_like"
        recoverability = "not_recoverable"
        handoff = "degeneration_blocked"
        parser_input_source = "blocked"
        parser_input_text = None
    elif bool(raw_outcome.get("punct_only")):
        category = "punctuation_collapse"
        recoverability = "not_recoverable"
        handoff = "degeneration_blocked"
        parser_input_source = "blocked"
        parser_input_text = None
    elif formatter_only_recoverable:
        category = "recoverable_formatting_issue"
        recoverability = "recoverable"
        handoff = "pass_formatted_to_parser"
        parser_input_source = "normalized"
        parser_input_text = normalized_response
    elif normalized_stripped != "" and len(normalized_stripped) <= 4 and normalized_outcome.get("parsed_label") is None:
        category = "ultra_short_malformed_response"
        recoverability = "not_recoverable"
        handoff = "degeneration_blocked"
        parser_input_source = "blocked"
        parser_input_text = None
    else:
        category = "contract_broken_response"
        recoverability = "not_recoverable"
        handoff = "degeneration_blocked"
        parser_input_source = "blocked"
        parser_input_text = None

    return {
        "degeneration_category": category,
        "recoverability": recoverability,
        "parser_handoff": handoff,
        "parser_input_source": parser_input_source,
        "parser_input_text": parser_input_text,
        "formatter_applied": handoff == "pass_formatted_to_parser",
        "formatter_steps": normalization_trace if handoff == "pass_formatted_to_parser" else [],
        "semantic_guess_used": False,
        "degeneration_flags": {
            "is_empty_like": stripped == "",
            "is_punct_only": bool(raw_outcome.get("punct_only")),
            "is_ultra_short": normalized_stripped != "" and len(normalized_stripped) <= 4,
            "has_raw_parsed_label": raw_outcome.get("parsed_label") is not None,
            "has_normalized_parsed_label": normalized_outcome.get("parsed_label") is not None,
            "has_unknown_tokens": bool(unknown_tokens),
            "formatting_only_recoverable": formatter_only_recoverable,
        },
        "raw_parser_outcome": raw_outcome,
        "normalized_response": normalized_response,
        "normalized_parser_outcome": normalized_outcome,
    }


def _record_by_case_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record["case_id"]): record for record in records}


def _focused_suite(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_case_id = _record_by_case_id(records)
    normal_rows = [
        record
        for record in records
        if record["suite_group"] == "clearly_normal_parser_reachable_responses"
    ]
    unrecoverable_rows = [
        record
        for record in records
        if record["suite_group"] == "clearly_unrecoverable_degeneration"
        and record["source_type"] == "real"
    ]
    ambiguous_real = next(
        record
        for record in records
        if record["case_id"].startswith("real_ambiguous_nonrecoverable::")
    )
    normal_template = by_case_id["controlled_recoverable::quote_wrap"]
    base_text = normal_template["observed_parser_input_text"]
    query_answer_key = str(normal_template["query_answer_key"])

    suite: list[dict[str, Any]] = []

    for record in normal_rows:
        suite.append(
            {
                "case_id": f"focused::{record['case_id']}",
                "source_type": "real",
                "base_source_case_id": record["case_id"],
                "suite_group": "normal_parser_reachable_guardrail",
                "expected_category": "parser_reachable",
                "expected_handoff": "pass_raw_to_parser",
                "expected_recoverability": "not_needed",
                "raw_response": record["raw_response"],
                "query_answer_key": record["query_answer_key"],
                "case_note": "real parser-reachable guardrail from stage-143",
            }
        )

    for record in unrecoverable_rows:
        suite.append(
            {
                "case_id": f"focused::{record['case_id']}",
                "source_type": "real",
                "base_source_case_id": record["case_id"],
                "suite_group": "unrecoverable_regression_guardrail",
                "expected_category": record["expected_category"],
                "expected_handoff": "degeneration_blocked",
                "expected_recoverability": "not_recoverable",
                "raw_response": record["raw_response"],
                "query_answer_key": record["query_answer_key"],
                "case_note": "real punct-collapse regression guardrail from stage-144",
            }
        )

    for case_id in [
        "controlled_recoverable::quote_wrap",
        "controlled_recoverable::bracket_wrap",
        "controlled_recoverable::prefix_noise",
        "controlled_recoverable::bullet_prefix",
        "controlled_recoverable::code_fence",
    ]:
        record = by_case_id[case_id]
        suite.append(
            {
                "case_id": f"focused::{record['case_id']}",
                "source_type": "inherited-controlled-format-variant",
                "base_source_case_id": record["case_id"],
                "suite_group": "recoverable_boundary_focus",
                "expected_category": "recoverable_formatting_issue",
                "expected_handoff": "pass_formatted_to_parser",
                "expected_recoverability": "recoverable",
                "raw_response": record["raw_response"],
                "query_answer_key": record["query_answer_key"],
                "case_note": record["case_note"],
            }
        )

    new_cases = [
        {
            "case_id": "focused::new_recoverable::code_fence_newline",
            "source_type": "new-controlled-format-variant",
            "base_source_case_id": "controlled_recoverable::code_fence",
            "suite_group": "recoverable_boundary_focus",
            "expected_category": "recoverable_formatting_issue",
            "expected_handoff": "pass_formatted_to_parser",
            "expected_recoverability": "recoverable",
            "raw_response": f"```\n{base_text}\n```",
            "query_answer_key": query_answer_key,
            "case_note": "newline-delimited markdown code fence around parser-reachable baseline text",
        },
        {
            "case_id": "focused::new_recoverable::code_fence_lang_tag",
            "source_type": "new-controlled-format-variant",
            "base_source_case_id": "controlled_recoverable::code_fence",
            "suite_group": "recoverable_boundary_focus",
            "expected_category": "recoverable_formatting_issue",
            "expected_handoff": "pass_formatted_to_parser",
            "expected_recoverability": "recoverable",
            "raw_response": f"```text\n{base_text}\n```",
            "query_answer_key": query_answer_key,
            "case_note": "language-tagged markdown code fence around parser-reachable baseline text",
        },
        {
            "case_id": "focused::new_recoverable::code_fence_markdown_tag",
            "source_type": "new-controlled-format-variant",
            "base_source_case_id": "controlled_recoverable::code_fence",
            "suite_group": "recoverable_boundary_focus",
            "expected_category": "recoverable_formatting_issue",
            "expected_handoff": "pass_formatted_to_parser",
            "expected_recoverability": "recoverable",
            "raw_response": f"```markdown\n{base_text}\n```",
            "query_answer_key": query_answer_key,
            "case_note": "markdown-tagged code fence with no semantic change to wrapped parser-reachable text",
        },
        {
            "case_id": "focused::new_nonrecoverable::code_fence_punct_only",
            "source_type": "new-controlled-format-variant",
            "base_source_case_id": "real_unrecoverable::csqa-pilot-021__targeted",
            "suite_group": "near_boundary_nonrecoverable",
            "expected_category": "punctuation_collapse",
            "expected_handoff": "degeneration_blocked",
            "expected_recoverability": "not_recoverable",
            "raw_response": "```???```",
            "query_answer_key": query_answer_key,
            "case_note": "plain code fence still wrapping punctuation-only no-info output",
        },
        {
            "case_id": "focused::new_nonrecoverable::code_fence_lang_tag_punct_only",
            "source_type": "new-controlled-format-variant",
            "base_source_case_id": "real_unrecoverable::csqa-pilot-021__targeted",
            "suite_group": "near_boundary_nonrecoverable",
            "expected_category": "contract_broken_response",
            "expected_handoff": "degeneration_blocked",
            "expected_recoverability": "not_recoverable",
            "raw_response": "```text\n???\n```",
            "query_answer_key": query_answer_key,
            "case_note": "language-tagged code fence around punctuation-only no-info output",
        },
        {
            "case_id": "focused::new_nonrecoverable::code_fence_contract_broken",
            "source_type": "new-controlled-format-variant",
            "base_source_case_id": ambiguous_real["case_id"],
            "suite_group": "near_boundary_nonrecoverable",
            "expected_category": "contract_broken_response",
            "expected_handoff": "degeneration_blocked",
            "expected_recoverability": "not_recoverable",
            "raw_response": f"```text\n{ambiguous_real['raw_response']}\n```",
            "query_answer_key": ambiguous_real["query_answer_key"],
            "case_note": "language-tagged code fence around real contract-broken response should remain blocked",
        },
    ]
    suite.extend(new_cases)
    return suite


def _rules() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_boundary_release_rules": [
            {
                "rule_id": "code_fence_wrapper_recoverable",
                "description": "Balanced triple-backtick wrapper may be removed when it only exposes underlying parser-reachable content without semantic guessing.",
                "allowed_wrapper_shapes": [
                    "```<content>```",
                    "```\\n<content>\\n```",
                    "```<language-tag>\\n<content>\\n```",
                ],
                "post_cleanup_requirements": [
                    "normalized_content_nonempty",
                    "normalized_parse_yields_exactly_one_allowed_label",
                    "all_cleanup_steps_are_in_allowed_format_steps",
                ],
                "semantic_guess_allowed": False,
            },
            {
                "rule_id": "single_layer_wrapper_recoverable",
                "description": "Single-layer quote/bracket/prefix/bullet wrappers are recoverable only when removal reveals an already parser-reachable label token.",
                "allowed_wrapper_shapes": [
                    "single_quote_wrapper",
                    "single_bracket_wrapper",
                    "single_prefix_noise",
                    "single_bullet_prefix",
                ],
                "semantic_guess_allowed": False,
            },
            {
                "rule_id": "nonrecoverable_after_wrapper_removal",
                "description": "If wrapper removal still leaves punctuation-only, empty-like, or contract-broken content with no parseable label token, the sample stays blocked.",
                "blocked_examples": [
                    "```???```",
                    "```text\\n???\\n```",
                    "```text\\n<contract-broken-response>\\n```",
                ],
                "semantic_guess_allowed": False,
            },
        ],
        "focused_acceptance_criteria": {
            "recoverable_boundary_control_validated": [
                "focused_recoverable_overblocked_count == 0",
                "focused_nonrecoverable_leak_count == 0",
                "focused_normal_collateral_damage_count == 0",
                "recoverable_pass_rate == 1.0",
                "current_path_improves_over_legacy_on_code_fence_like_cases",
            ],
            "partially_validated": [
                "no_nonrecoverable_leakage",
                "no_normal_collateral_damage",
                "but_recoverable_boundary_still_has_overblock_or_insufficient_coverage",
            ],
        },
    }


def _evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    allowed_labels = {case["query_answer_key"]} if case["query_answer_key"] else {"A", "B", "C", "D"}
    legacy = _build_legacy_output_antidegradation_record(
        response_text=case["raw_response"],
        parse_mode="robust_prefix",
        allowed_labels=allowed_labels,
    )
    current = build_output_antidegradation_record(
        response_text=case["raw_response"],
        parse_mode="robust_prefix",
        allowed_labels=allowed_labels,
        normalization_mode="conservative",
    )

    current_handoff = current["parser_handoff"]
    current_category = current["degeneration_category"]
    current_recoverability = current["recoverability"]

    all_expectations_met = (
        current_handoff == case["expected_handoff"]
        and current_category == case["expected_category"]
        and current_recoverability == case["expected_recoverability"]
    )
    if case["suite_group"] == "recoverable_boundary_focus" and current_handoff != "pass_formatted_to_parser":
        mismatch_type = "recoverable_boundary_overblocked"
    elif case["suite_group"] in {"near_boundary_nonrecoverable", "unrecoverable_regression_guardrail"} and current_handoff != "degeneration_blocked":
        mismatch_type = "nonrecoverable_leak"
    elif case["suite_group"] == "normal_parser_reachable_guardrail" and current_handoff != "pass_raw_to_parser":
        mismatch_type = "normal_collateral_damage"
    elif all_expectations_met:
        mismatch_type = "match"
    else:
        mismatch_type = "other_boundary_mismatch"

    legacy_overblocked = case["suite_group"] == "recoverable_boundary_focus" and legacy["parser_handoff"] != "pass_formatted_to_parser"
    current_overblocked = case["suite_group"] == "recoverable_boundary_focus" and current_handoff != "pass_formatted_to_parser"
    compression_effect = (
        "reduced_overblock"
        if legacy_overblocked and not current_overblocked
        else "unchanged_overblock"
        if legacy_overblocked and current_overblocked
        else "still_clean"
        if not legacy_overblocked and not current_overblocked
        else "new_overblock"
    )

    return {
        "schema_version": SCHEMA_VERSION,
        **case,
        "legacy_category": legacy["degeneration_category"],
        "legacy_handoff": legacy["parser_handoff"],
        "legacy_recoverability": legacy["recoverability"],
        "legacy_formatter_steps": legacy["formatter_steps"],
        "legacy_parser_input_text": legacy["parser_input_text"],
        "current_category": current_category,
        "current_handoff": current_handoff,
        "current_recoverability": current_recoverability,
        "current_formatter_steps": current["formatter_steps"],
        "current_parser_input_text": current["parser_input_text"],
        "current_normalized_response": current["normalized_response"],
        "all_expectations_met": all_expectations_met,
        "mismatch_type": mismatch_type,
        "legacy_overblocked": legacy_overblocked,
        "current_overblocked": current_overblocked,
        "compression_effect": compression_effect,
    }


def _suite_manifest(cases: list[dict[str, Any]]) -> dict[str, Any]:
    group_counts = Counter(case["suite_group"] for case in cases)
    source_counts = Counter(case["source_type"] for case in cases)
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "suite_name": "route_c_recoverable_boundary_control_focused_v1",
        "case_count": len(cases),
        "group_counts": dict(group_counts),
        "source_type_counts": dict(source_counts),
        "cases": cases,
    }


def _summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_group_current_handoff: dict[str, Counter[str]] = defaultdict(Counter)
    mismatch_counts: Counter[str] = Counter()
    compression_counts: Counter[str] = Counter()
    for record in records:
        by_group_current_handoff[record["suite_group"]][record["current_handoff"]] += 1
        mismatch_counts[record["mismatch_type"]] += 1
        compression_counts[record["compression_effect"]] += 1

    recoverable_records = [r for r in records if r["suite_group"] == "recoverable_boundary_focus"]
    normal_records = [r for r in records if r["suite_group"] == "normal_parser_reachable_guardrail"]
    near_nonrecoverable = [
        r for r in records if r["suite_group"] in {"near_boundary_nonrecoverable", "unrecoverable_regression_guardrail"}
    ]

    legacy_recoverable_overblocked_count = sum(1 for r in recoverable_records if r["legacy_overblocked"])
    current_recoverable_overblocked_count = sum(1 for r in recoverable_records if r["current_overblocked"])
    current_nonrecoverable_leak_count = sum(1 for r in near_nonrecoverable if r["current_handoff"] != "degeneration_blocked")
    current_normal_collateral_damage_count = sum(1 for r in normal_records if r["current_handoff"] != "pass_raw_to_parser")

    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_case_count": len(records),
        "current_group_vs_handoff": {group: dict(counter) for group, counter in by_group_current_handoff.items()},
        "mismatch_type_counts": dict(mismatch_counts),
        "compression_effect_counts": dict(compression_counts),
        "legacy_recoverable_overblocked_count": legacy_recoverable_overblocked_count,
        "current_recoverable_overblocked_count": current_recoverable_overblocked_count,
        "recoverable_overblocked_delta": current_recoverable_overblocked_count - legacy_recoverable_overblocked_count,
        "recoverable_pass_rate": (
            sum(1 for r in recoverable_records if r["current_handoff"] == "pass_formatted_to_parser") / len(recoverable_records)
            if recoverable_records
            else None
        ),
        "legacy_recoverable_pass_rate": (
            sum(1 for r in recoverable_records if r["legacy_handoff"] == "pass_formatted_to_parser") / len(recoverable_records)
            if recoverable_records
            else None
        ),
        "current_nonrecoverable_leak_count": current_nonrecoverable_leak_count,
        "current_normal_collateral_damage_count": current_normal_collateral_damage_count,
        "normal_pass_through_rate": (
            sum(1 for r in normal_records if r["current_handoff"] == "pass_raw_to_parser") / len(normal_records)
            if normal_records
            else None
        ),
        "nonrecoverable_block_rate": (
            sum(1 for r in near_nonrecoverable if r["current_handoff"] == "degeneration_blocked") / len(near_nonrecoverable)
            if near_nonrecoverable
            else None
        ),
        "focused_improvement_achieved": current_recoverable_overblocked_count < legacy_recoverable_overblocked_count,
        "controlled_validation_executed": False,
        "controlled_validation_note": "Focused suite compares legacy helper-path behavior against the current helper without replay or model rerun.",
    }


def _report(suite: dict[str, Any], rules: dict[str, Any], summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Route-C Recoverable Boundary Control Report")
    lines.append("")
    lines.append("## Focus")
    lines.append("- This stage only targets recoverable formatting boundary evidence and collateral compression.")
    lines.append("- No benchmark-truth semantics, gate semantics, budget, model axis, or prompt family were changed.")
    lines.append("")
    lines.append("## Suite Coverage")
    lines.append(f"- total_case_count: {suite['case_count']}")
    for key, value in suite["group_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Focused Summary")
    lines.append(f"- legacy_recoverable_overblocked_count: {summary['legacy_recoverable_overblocked_count']}")
    lines.append(f"- current_recoverable_overblocked_count: {summary['current_recoverable_overblocked_count']}")
    lines.append(f"- recoverable_pass_rate: {summary['recoverable_pass_rate']}")
    lines.append(f"- legacy_recoverable_pass_rate: {summary['legacy_recoverable_pass_rate']}")
    lines.append(f"- current_nonrecoverable_leak_count: {summary['current_nonrecoverable_leak_count']}")
    lines.append(f"- current_normal_collateral_damage_count: {summary['current_normal_collateral_damage_count']}")
    lines.append("")
    lines.append("## Key Before/After Cases")
    for record in [r for r in records if r["compression_effect"] == "reduced_overblock"][:5]:
        lines.append(
            "- "
            + f"{record['case_id']}: legacy {record['legacy_handoff']} / {record['legacy_category']} -> "
            + f"current {record['current_handoff']} / {record['current_category']}"
        )
    remaining = [r for r in records if r["mismatch_type"] != "match"][:5]
    if remaining:
        lines.append("")
        lines.append("## Remaining Mismatches")
        for record in remaining:
            lines.append(
                "- "
                + f"{record['case_id']}: expected {record['expected_handoff']} / {record['expected_category']}, "
                + f"observed {record['current_handoff']} / {record['current_category']} ({record['mismatch_type']})"
            )
    lines.append("")
    lines.append("## Notes")
    lines.append("- Inherited controlled variants come from stage 147 and remain formatting-only.")
    lines.append("- New controlled variants only wrap existing content with code-fence-like formatting; no semantic rewrite is introduced.")
    return "\n".join(lines) + "\n"


def build_route_c_recoverable_boundary_evidence_and_collateral_compression(
    boundary_control_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    prior_records = _load_147_records(boundary_control_dir)
    cases = _focused_suite(prior_records)
    records = [_evaluate_case(case) for case in cases]
    suite = _suite_manifest(cases)
    rules = _rules()
    summary = _summary(records)
    report = _report(suite=suite, rules=rules, summary=summary, records=records)

    write_json(output_dir / "route_c_recoverable_boundary_control_suite.json", suite)
    write_json(output_dir / "route_c_recoverable_boundary_control_rules.json", rules)
    write_json(output_dir / "route_c_recoverable_boundary_control_summary.json", summary)
    write_jsonl(output_dir / "route_c_recoverable_boundary_control_details.jsonl", records)
    (output_dir / "route_c_recoverable_boundary_control_report.md").write_text(report, encoding="utf-8")

    return {
        "suite": suite,
        "rules": rules,
        "summary": summary,
        "output_paths": {
            "suite": str((output_dir / "route_c_recoverable_boundary_control_suite.json").resolve()),
            "rules": str((output_dir / "route_c_recoverable_boundary_control_rules.json").resolve()),
            "summary": str((output_dir / "route_c_recoverable_boundary_control_summary.json").resolve()),
            "details": str((output_dir / "route_c_recoverable_boundary_control_details.jsonl").resolve()),
            "report": str((output_dir / "route_c_recoverable_boundary_control_report.md").resolve()),
        },
    }
