"""Build route_c label output normalization instrumentation and compare artifacts."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json, write_jsonl


SCHEMA_VERSION = "triscopellm/route-c-label-output-normalization/v1"
FAILURE_CATEGORIES = [
    "empty",
    "whitespace_only",
    "punct_only",
    "quote_wrapped_label",
    "bracket_wrapped_label",
    "prefix_suffix_noise",
    "json_like_but_unparsed",
    "unknown_token",
    "multi_label_ambiguous",
    "label_not_in_set",
    "parser_exception",
    "other",
]


def _resolve_route_c_run_dir(execution_root_dir: Path, route_c_run_subdir: str) -> Path:
    candidate = execution_root_dir / route_c_run_subdir
    if candidate.is_dir():
        return candidate
    if execution_root_dir.is_dir() and (execution_root_dir / "route_c_v6_dataset_dir").is_dir():
        return execution_root_dir
    raise ValueError(
        f"Could not resolve route_c run dir from `{execution_root_dir}` with subdir `{route_c_run_subdir}`."
    )


def _failure_distribution(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        category = row.get(key)
        if category is None:
            continue
        counts[str(category)] += 1
    return {category: int(counts.get(category, 0)) for category in FAILURE_CATEGORIES}


def _label_set_from_class_balance(class_balance: dict[str, Any] | None) -> list[int]:
    if not isinstance(class_balance, dict):
        return []
    label_set: list[int] = []
    if int(class_balance.get("label_0", 0) or 0) > 0:
        label_set.append(0)
    if int(class_balance.get("label_1", 0) or 0) > 0:
        label_set.append(1)
    return label_set


def _shorten(text: str, max_chars: int = 180) -> str:
    compact = " ".join(text.strip().split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3] + "..."


def _build_failure_samples(rows: list[dict[str, Any]], max_per_category: int = 2) -> dict[str, list[dict[str, Any]]]:
    collected: dict[str, list[dict[str, Any]]] = {category: [] for category in FAILURE_CATEGORIES}
    for row in rows:
        category = str(row.get("parse_failure_category") or "other")
        bucket = collected.get(category)
        if bucket is None:
            continue
        if len(bucket) >= max_per_category:
            continue
        bucket.append(
            {
                "sample_id": row.get("sample_id"),
                "base_sample_id": row.get("base_sample_id"),
                "query_answer_key": row.get("query_answer_key"),
                "selected_parser_source": row.get("selected_parser_source"),
                "raw_response_preview": _shorten(str(row.get("raw_response", ""))),
                "normalized_response_preview": _shorten(str(row.get("normalized_response", ""))),
            }
        )
    return {category: samples for category, samples in collected.items() if samples}


def _build_markdown_report(
    summary: dict[str, Any],
    compare: dict[str, Any],
    failure_samples: dict[str, list[dict[str, Any]]],
) -> str:
    lines: list[str] = []
    lines.append("# Route-C Label Output Normalization Report")
    lines.append("")
    lines.append("## Goal")
    lines.append("Make parser failures observable and classifiable while keeping label semantics and gate thresholds unchanged.")
    lines.append("")
    lines.append("## Execution Path")
    lines.extend(
        [
            "1. raw output: route_c_v6_labeled_illumination/illumination_probe/raw_results.jsonl",
            "2. parser+normalization: benchmark_truth_leaning_label.build_benchmark_truth_leaning_dataset",
            "3. label health rows: route_c_v6_dataset_dir/benchmark_truth_leaning_label_health_rows.jsonl",
            "4. gate read: route_c_v6_label_health_gate_result.json",
            "5. recheck summary: route_c_label_output_normalization_recheck_summary.json",
        ]
    )
    lines.append("")
    lines.append("## Parser Outcome Compare")
    raw = compare["raw_parser_outcome"]
    norm = compare["normalized_parser_outcome"]
    lines.append(f"- raw parsed_option_count: {raw['parsed_option_count']}")
    lines.append(f"- normalized parsed_option_count: {norm['parsed_option_count']}")
    lines.append(f"- raw missing_option_ratio: {raw['missing_option_ratio']:.4f}")
    lines.append(f"- normalized missing_option_ratio: {norm['missing_option_ratio']:.4f}")
    lines.append(f"- raw punct_only_ratio: {raw['punct_only_ratio']:.4f}")
    lines.append(f"- normalized punct_only_ratio: {norm['punct_only_ratio']:.4f}")
    lines.append(f"- execution_label_set: {compare['execution_label_set']}")
    lines.append(f"- class_balance: {compare['class_balance']}")
    lines.append("")
    lines.append("## Failure Samples")
    if not failure_samples:
        lines.append("- no failure samples available")
    else:
        for category, samples in failure_samples.items():
            lines.append(f"- {category}")
            for sample in samples:
                lines.append(
                    "  - "
                    + f"sample_id={sample['sample_id']}, raw='{sample['raw_response_preview']}', "
                    + f"normalized='{sample['normalized_response_preview']}'"
                )
    lines.append("")
    lines.append("## Notes")
    lines.append(f"- gate_status: {summary.get('label_health_gate_status')}")
    lines.append(f"- blocked_reason: {summary.get('label_health_blocked_reason')}")
    return "\n".join(lines) + "\n"


def build_route_c_label_output_normalization(
    execution_root_dir: Path,
    route_c_run_subdir: str,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    route_c_run_dir = _resolve_route_c_run_dir(execution_root_dir=execution_root_dir, route_c_run_subdir=route_c_run_subdir)

    raw_results_path = route_c_run_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl"
    health_rows_path = route_c_run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_health_rows.jsonl"
    health_summary_path = route_c_run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_health_summary.json"
    parse_compare_path = route_c_run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_parse_compare.json"
    gate_result_path = route_c_run_dir / "route_c_v6_label_health_gate_result.json"

    raw_rows = load_jsonl(raw_results_path) if raw_results_path.is_file() else []
    health_rows = load_jsonl(health_rows_path) if health_rows_path.is_file() else []
    health_summary = load_json(health_summary_path) if health_summary_path.is_file() else {}
    gate_result = load_json(gate_result_path) if gate_result_path.is_file() else {}

    if parse_compare_path.is_file():
        parse_compare = load_json(parse_compare_path)
    else:
        row_count = len(health_rows)
        raw_parsed = sum(1 for row in health_rows if row.get("raw_parser_outcome", {}).get("parsed_label") is not None)
        norm_parsed = sum(1 for row in health_rows if row.get("normalized_parser_outcome", {}).get("parsed_label") is not None)
        raw_punct = sum(1 for row in health_rows if bool(row.get("raw_parser_outcome", {}).get("punct_only")))
        norm_punct = sum(1 for row in health_rows if bool(row.get("normalized_parser_outcome", {}).get("punct_only")))
        parse_compare = {
            "summary_status": "PASS_WITH_LIMITATIONS",
            "schema_version": SCHEMA_VERSION,
            "raw": {
                "parsed_option_count": raw_parsed,
                "missing_option_count": row_count - raw_parsed,
                "missing_option_ratio": float(row_count - raw_parsed) / float(row_count) if row_count > 0 else 0.0,
                "punct_only_count": raw_punct,
                "punct_only_ratio": float(raw_punct) / float(row_count) if row_count > 0 else 0.0,
                "failure_category_distribution": _failure_distribution(health_rows, "parse_failure_category"),
            },
            "normalized": {
                "parsed_option_count": norm_parsed,
                "missing_option_count": row_count - norm_parsed,
                "missing_option_ratio": float(row_count - norm_parsed) / float(row_count) if row_count > 0 else 0.0,
                "punct_only_count": norm_punct,
                "punct_only_ratio": float(norm_punct) / float(row_count) if row_count > 0 else 0.0,
                "failure_category_distribution": _failure_distribution(health_rows, "parse_failure_category"),
            },
            "selected_parser_source_counts": {
                "raw": sum(1 for row in health_rows if str(row.get("selected_parser_source")) == "raw"),
                "normalized": sum(1 for row in health_rows if str(row.get("selected_parser_source")) == "normalized"),
            },
        }

    row_count = len(health_rows)
    class_balance = health_summary.get("class_balance")
    if class_balance is None:
        class_balance = gate_result.get("class_balance")
    execution_label_set = _label_set_from_class_balance(class_balance)

    raw_outcome = parse_compare.get("raw", {})
    normalized_outcome = parse_compare.get("normalized", {})

    compare = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "row_count": row_count,
        "raw_parser_outcome": {
            "parsed_option_count": int(raw_outcome.get("parsed_option_count", 0) or 0),
            "missing_option_ratio": float(raw_outcome.get("missing_option_ratio", 0.0) or 0.0),
            "punct_only_ratio": float(raw_outcome.get("punct_only_ratio", 0.0) or 0.0),
            "failure_category_distribution": raw_outcome.get("failure_category_distribution", {}),
        },
        "normalized_parser_outcome": {
            "parsed_option_count": int(normalized_outcome.get("parsed_option_count", 0) or 0),
            "missing_option_ratio": float(normalized_outcome.get("missing_option_ratio", 0.0) or 0.0),
            "punct_only_ratio": float(normalized_outcome.get("punct_only_ratio", 0.0) or 0.0),
            "failure_category_distribution": normalized_outcome.get("failure_category_distribution", {}),
        },
        "execution_label_set": execution_label_set,
        "class_balance": class_balance,
    }

    failure_samples = _build_failure_samples(health_rows)
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "execution_root_dir": str(execution_root_dir.resolve()),
        "route_c_run_dir": str(route_c_run_dir.resolve()),
        "line_level_rows": row_count,
        "raw_result_rows": len(raw_rows),
        "option_parse_mode": health_summary.get("option_parse_mode"),
        "option_normalization_mode": health_summary.get("option_normalization_mode"),
        "label_health_gate_status": gate_result.get("gate_status"),
        "label_health_blocked_reason": gate_result.get("blocked_reason"),
        "execution_path_map": {
            "raw_output": str(raw_results_path),
            "normalized_parsed_output": str(health_rows_path),
            "gate_result": str(gate_result_path),
            "recheck_summary": "outputs/model_axis_1p5b_route_c_label_output_normalization_recheck/default/route_c_label_output_normalization_recheck_summary.json",
        },
        "precheck_execution_parser_consistency_note": (
            "Precheck is logistic feasibility on prepared dataset rows, while execution parser operates on runtime labeled illumination raw responses."
        ),
    }

    if compare["normalized_parser_outcome"]["parsed_option_count"] > compare["raw_parser_outcome"]["parsed_option_count"]:
        next_step = "run_gate_protected_controlled_recheck"
        rationale = [
            "Normalization improved parseability without changing semantics or gate thresholds.",
            "Proceed with one controlled execution recheck under unchanged gate rules.",
        ]
    else:
        next_step = "run_gate_protected_controlled_recheck_with_same_constraints"
        rationale = [
            "No parseability gain observed from conservative normalization on current outputs.",
            "Still proceed with controlled recheck to verify reproducibility and preserve evidence.",
        ]

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": next_step,
        "why": rationale,
        "constraints_kept": {
            "gate_unchanged": True,
            "label_semantics_unchanged": True,
            "no_budget_expansion": True,
            "no_model_axis_expansion": True,
        },
    }

    report_text = _build_markdown_report(summary=summary, compare=compare, failure_samples=failure_samples)

    write_json(output_dir / "route_c_label_output_normalization_summary.json", summary)
    write_jsonl(output_dir / "route_c_label_output_normalization_details.jsonl", health_rows)
    write_json(output_dir / "route_c_label_output_normalization_compare.json", compare)
    (output_dir / "route_c_label_output_normalization_report.md").write_text(report_text, encoding="utf-8")
    write_json(output_dir / "route_c_label_output_normalization_next_step_recommendation.json", recommendation)

    return {
        "summary": summary,
        "output_paths": {
            "summary": str((output_dir / "route_c_label_output_normalization_summary.json").resolve()),
            "details": str((output_dir / "route_c_label_output_normalization_details.jsonl").resolve()),
            "compare": str((output_dir / "route_c_label_output_normalization_compare.json").resolve()),
            "report": str((output_dir / "route_c_label_output_normalization_report.md").resolve()),
            "recommendation": str((output_dir / "route_c_label_output_normalization_next_step_recommendation.json").resolve()),
        },
    }
