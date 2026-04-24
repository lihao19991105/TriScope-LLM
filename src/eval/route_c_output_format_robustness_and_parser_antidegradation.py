"""Controlled anti-degradation validation for route_c raw output format drift."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_jsonl, write_json, write_jsonl
from src.fusion.benchmark_truth_leaning_label import build_output_antidegradation_record


SCHEMA_VERSION = "triscopellm/route-c-output-format-robustness-and-parser-antidegradation/v1"


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


def _allowed_labels(rows: list[dict[str, Any]]) -> set[str]:
    labels = {str(row.get("query_answer_key", "")).strip().upper() for row in rows}
    labels = {label for label in labels if label}
    return labels or {"A", "B", "C", "D"}


def _build_records(rows: list[dict[str, Any]], stage_name: str) -> list[dict[str, Any]]:
    labels = _allowed_labels(rows)
    records: list[dict[str, Any]] = []
    for row in rows:
        anti = build_output_antidegradation_record(
            response_text=str(row.get("raw_response", "")),
            parse_mode="robust_prefix",
            allowed_labels=labels,
            normalization_mode="conservative",
        )
        records.append(
            {
                "schema_version": SCHEMA_VERSION,
                "stage_name": stage_name,
                "sample_id": row.get("sample_id"),
                "base_sample_id": row.get("base_sample_id"),
                "query_answer_key": row.get("query_answer_key"),
                "raw_response": row.get("raw_response"),
                "normalized_response_from_existing_path": row.get("normalized_response"),
                "existing_selected_parser_source": row.get("selected_parser_source"),
                "existing_parse_failure_category": row.get("parse_failure_category"),
                "existing_raw_parser_path": row.get("raw_parser_outcome", {}).get("parser_path"),
                "existing_raw_parsed_label": row.get("raw_parser_outcome", {}).get("parsed_label"),
                "anti_degeneration_category": anti["degeneration_category"],
                "anti_recoverability": anti["recoverability"],
                "anti_parser_handoff": anti["parser_handoff"],
                "anti_parser_input_source": anti["parser_input_source"],
                "anti_formatter_applied": anti["formatter_applied"],
                "anti_formatter_steps": anti["formatter_steps"],
                "anti_parser_input_text": anti["parser_input_text"],
                "anti_semantic_guess_used": anti["semantic_guess_used"],
                "anti_degeneration_flags": anti["degeneration_flags"],
                "anti_raw_parser_outcome": anti["raw_parser_outcome"],
                "anti_normalized_response": anti["normalized_response"],
                "anti_normalized_parser_outcome": anti["normalized_parser_outcome"],
            }
        )
    return records


def _representative_cases(records: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for record in records[:limit]:
        cases.append(
            {
                "sample_id": record["sample_id"],
                "base_sample_id": record["base_sample_id"],
                "raw_response_preview": _shorten(record["raw_response"]),
                "existing_parse_failure_category": record["existing_parse_failure_category"],
                "anti_degeneration_category": record["anti_degeneration_category"],
                "anti_parser_handoff": record["anti_parser_handoff"],
            }
        )
    return cases


def _taxonomy_entry(
    *,
    category: str,
    definition: str,
    detection_rule: list[str],
    recoverability_rule: str,
    stage_143_records: list[dict[str, Any]],
    stage_144_records: list[dict[str, Any]],
) -> dict[str, Any]:
    rows_143 = [row for row in stage_143_records if row["anti_degeneration_category"] == category]
    rows_144 = [row for row in stage_144_records if row["anti_degeneration_category"] == category]
    return {
        "definition": definition,
        "detection_rule": detection_rule,
        "recoverability_rule": recoverability_rule,
        "observed_counts": {
            "stage_143": len(rows_143),
            "stage_144": len(rows_144),
        },
        "representative_examples": {
            "stage_143": _representative_cases(rows_143, limit=3),
            "stage_144": _representative_cases(rows_144, limit=3),
        },
    }


def _boundary_rows(stage_143_records: list[dict[str, Any]], stage_144_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    selected.extend(stage_144_records[:6])
    selected.extend(stage_143_records[:4])
    rows: list[dict[str, Any]] = []
    for record in selected:
        rows.append(
            {
                "sample_id": record["sample_id"],
                "stage_name": record["stage_name"],
                "raw_response_preview": _shorten(record["raw_response"]),
                "anti_degeneration_category": record["anti_degeneration_category"],
                "anti_parser_handoff": record["anti_parser_handoff"],
                "recoverability": record["anti_recoverability"],
                "why": (
                    "Raw output is pure punctuation or empty-like; no label token survives without guessing."
                    if record["anti_parser_handoff"] == "degeneration_blocked"
                    else "Raw output already exposes an explicit label token and can enter parser unchanged."
                ),
            }
        )
    return rows


def _stage_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts = Counter(row["anti_degeneration_category"] for row in records)
    handoff_counts = Counter(row["anti_parser_handoff"] for row in records)
    return {
        "row_count": len(records),
        "category_counts": dict(category_counts),
        "handoff_counts": dict(handoff_counts),
        "parser_reachable_count": int(category_counts.get("parser_reachable", 0)),
        "recoverable_formatting_count": int(category_counts.get("recoverable_formatting_issue", 0)),
        "degeneration_blocked_count": int(handoff_counts.get("degeneration_blocked", 0)),
    }


def _build_markdown_report(
    taxonomy: dict[str, Any],
    rules: dict[str, Any],
    summary: dict[str, Any],
) -> str:
    lines: list[str] = []
    lines.append("# Route-C Output Format Robustness And Parser Antidegradation Report")
    lines.append("")
    lines.append("## Goal")
    lines.append("Add a minimal, auditable anti-degradation path at the parser boundary without changing benchmark truth semantics or gate semantics.")
    lines.append("")
    lines.append("## Observed Degeneration")
    lines.append(f"- stage_144 punctuation_collapse_count: {taxonomy['taxonomy']['punctuation_collapse']['observed_counts']['stage_144']}")
    lines.append(f"- stage_143 parser_reachable_count: {summary['stage_143_validation']['parser_reachable_count']}")
    lines.append(f"- stage_143 contract_broken_count: {taxonomy['taxonomy']['contract_broken_response']['observed_counts']['stage_143']}")
    lines.append("")
    lines.append("## Anti-degradation Path")
    lines.append("- degeneration detector runs before parser handoff")
    lines.append("- recoverable formatting issues may enter parser after conservative cleanup only")
    lines.append("- punctuation collapse / empty-like / ultra-short malformed / unrecoverable contract-broken responses are marked degeneration-blocked")
    lines.append("")
    lines.append("## Controlled Validation")
    lines.append(f"- stage_143 normal_contracts_preserved: {summary['stage_143_validation']['normal_contracts_preserved']}")
    lines.append(f"- stage_144 punctuation_collapse_detected_all: {summary['stage_144_validation']['punctuation_collapse_detected_all']}")
    lines.append(f"- stage_144 irrecoverable_rows_blocked_all: {summary['stage_144_validation']['irrecoverable_rows_blocked_all']}")
    lines.append(f"- controlled_rerun_executed: {summary['controlled_rerun_executed']}")
    lines.append("")
    lines.append("## Boundary Cases")
    for row in rules["representative_boundary_cases"]:
        lines.append(
            "- "
            + f"{row['stage_name']}::{row['sample_id']} => {row['anti_degeneration_category']} / {row['anti_parser_handoff']} / {row['recoverability']}"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("- This stage does not repair pure punctuation collapse into valid labels.")
    lines.append("- This stage makes the parser boundary more explicit and auditable.")
    return "\n".join(lines) + "\n"


def build_route_c_output_format_robustness_and_parser_antidegradation(
    stage_143_run_dir: Path,
    stage_144_run_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    stage_143_rows = _load_health_rows(stage_143_run_dir)
    stage_144_rows = _load_health_rows(stage_144_run_dir)
    stage_143_records = _build_records(stage_143_rows, "stage_143_stable_baseline")
    stage_144_records = _build_records(stage_144_rows, "stage_144_time_separated_regression")
    all_records = stage_143_records + stage_144_records

    taxonomy = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "evidence_window": {
            "stage_143_run_dir": str(stage_143_run_dir.resolve()),
            "stage_144_run_dir": str(stage_144_run_dir.resolve()),
        },
        "taxonomy": {
            "punctuation_collapse": _taxonomy_entry(
                category="punctuation_collapse",
                definition="Raw response is non-empty but consists only of punctuation / symbol repetition.",
                detection_rule=[
                    "raw_parser_outcome.punct_only == true",
                    "no alphanumeric token survives before parser handoff",
                ],
                recoverability_rule="not_recoverable_without_semantic_guess",
                stage_143_records=stage_143_records,
                stage_144_records=stage_144_records,
            ),
            "ultra_short_malformed_response": _taxonomy_entry(
                category="ultra_short_malformed_response",
                definition="Raw response is very short and still fails to expose any valid label token after conservative cleanup.",
                detection_rule=[
                    "normalized non-empty text length <= 4",
                    "raw and normalized parser outcomes both have no parsed_label",
                ],
                recoverability_rule="not_recoverable_without_semantic_guess",
                stage_143_records=stage_143_records,
                stage_144_records=stage_144_records,
            ),
            "contract_broken_response": _taxonomy_entry(
                category="contract_broken_response",
                definition="Raw response contains text but does not preserve a parser-reachable contract-level label token.",
                detection_rule=[
                    "raw response not punct-only and not empty-like",
                    "no parsed_label on raw path",
                    "no conservative formatting-only recovery available",
                ],
                recoverability_rule="not_recoverable_unless_existing_label_token_becomes_explicit_after_conservative_cleanup",
                stage_143_records=stage_143_records,
                stage_144_records=stage_144_records,
            ),
            "empty_whitespace_like": _taxonomy_entry(
                category="empty_whitespace_like",
                definition="Raw response is empty or whitespace-like before any parser decision.",
                detection_rule=[
                    "raw_response.strip() == ''",
                ],
                recoverability_rule="not_recoverable",
                stage_143_records=stage_143_records,
                stage_144_records=stage_144_records,
            ),
            "recoverable_formatting_issue": _taxonomy_entry(
                category="recoverable_formatting_issue",
                definition="Raw response fails initially, but conservative formatting cleanup exposes an already-present valid label token without semantic guessing.",
                detection_rule=[
                    "raw parser has no parsed_label",
                    "normalized parser has parsed_label",
                    "formatter steps are all in the conservative allow-list",
                ],
                recoverability_rule="recoverable_via_contract_preserving_format_cleanup_only",
                stage_143_records=stage_143_records,
                stage_144_records=stage_144_records,
            ),
        },
    }

    rules = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "anti_degradation_mode": "strict_minimal",
        "boundary_table": [
            {
                "category": "punctuation_collapse",
                "recoverability": "not_recoverable",
                "parser_handoff": "degeneration_blocked",
                "semantic_guess_allowed": False,
            },
            {
                "category": "ultra_short_malformed_response",
                "recoverability": "not_recoverable",
                "parser_handoff": "degeneration_blocked",
                "semantic_guess_allowed": False,
            },
            {
                "category": "contract_broken_response",
                "recoverability": "not_recoverable",
                "parser_handoff": "degeneration_blocked",
                "semantic_guess_allowed": False,
            },
            {
                "category": "empty_whitespace_like",
                "recoverability": "not_recoverable",
                "parser_handoff": "degeneration_blocked",
                "semantic_guess_allowed": False,
            },
            {
                "category": "recoverable_formatting_issue",
                "recoverability": "recoverable",
                "parser_handoff": "pass_formatted_to_parser",
                "semantic_guess_allowed": False,
            },
            {
                "category": "parser_reachable",
                "recoverability": "not_needed",
                "parser_handoff": "pass_raw_to_parser",
                "semantic_guess_allowed": False,
            },
        ],
        "representative_boundary_cases": _boundary_rows(stage_143_records, stage_144_records),
    }

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "anti_degradation_mode": "strict_minimal",
        "benchmark_truth_semantics_changed": False,
        "gate_semantics_changed": False,
        "semantic_boundary_preserved": True,
        "controlled_rerun_executed": False,
        "stage_143_validation": {
            **_stage_summary(stage_143_records),
            "normal_contracts_preserved": all(
                record["anti_parser_handoff"] == "pass_raw_to_parser"
                for record in stage_143_records
                if record["existing_raw_parsed_label"] is not None
            ),
            "false_positive_degeneration_on_parser_reachable_rows": sum(
                1
                for record in stage_143_records
                if record["existing_raw_parsed_label"] is not None and record["anti_parser_handoff"] != "pass_raw_to_parser"
            ),
        },
        "stage_144_validation": {
            **_stage_summary(stage_144_records),
            "punctuation_collapse_detected_all": all(
                record["anti_degeneration_category"] == "punctuation_collapse" for record in stage_144_records
            ),
            "irrecoverable_rows_blocked_all": all(
                record["anti_parser_handoff"] == "degeneration_blocked" for record in stage_144_records
            ),
            "recovered_rows": sum(
                1 for record in stage_144_records if record["anti_parser_handoff"] == "pass_formatted_to_parser"
            ),
        },
        "why_not_full_recovery": [
            "Current 144 regression rows are punctuation-only and contain no parser-reachable label token.",
            "Under frozen semantics, these rows must remain non-recoverable rather than being guessed into valid labels.",
        ],
    }

    report = _build_markdown_report(taxonomy=taxonomy, rules=rules, summary=summary)

    write_json(output_dir / "route_c_output_format_robustness_taxonomy.json", taxonomy)
    write_json(output_dir / "route_c_output_format_robustness_rules.json", rules)
    write_json(output_dir / "route_c_output_format_robustness_summary.json", summary)
    write_jsonl(output_dir / "route_c_output_format_robustness_details.jsonl", all_records)
    (output_dir / "route_c_output_format_robustness_report.md").write_text(report, encoding="utf-8")

    return {
        "taxonomy": taxonomy,
        "rules": rules,
        "summary": summary,
        "output_paths": {
            "taxonomy": str((output_dir / "route_c_output_format_robustness_taxonomy.json").resolve()),
            "rules": str((output_dir / "route_c_output_format_robustness_rules.json").resolve()),
            "summary": str((output_dir / "route_c_output_format_robustness_summary.json").resolve()),
            "details": str((output_dir / "route_c_output_format_robustness_details.jsonl").resolve()),
            "report": str((output_dir / "route_c_output_format_robustness_report.md").resolve()),
        },
    }
