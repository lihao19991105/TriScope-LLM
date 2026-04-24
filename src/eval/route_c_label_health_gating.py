"""Build route_c label-path health instrumentation and gate artifacts from execution outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json, write_jsonl
from src.fusion.benchmark_truth_leaning_label import summarize_option_label_parse


SCHEMA_VERSION = "triscopellm/route-c-label-health-gating/v1"


def _resolve_route_c_run_dir(execution_root_dir: Path, route_c_run_subdir: str) -> Path:
    candidate = execution_root_dir / route_c_run_subdir
    if candidate.is_dir():
        return candidate
    if execution_root_dir.is_dir() and (execution_root_dir / "route_c_v6_dataset_dir").is_dir():
        return execution_root_dir
    raise ValueError(
        f"Could not resolve route_c run dir from `{execution_root_dir}` with subdir `{route_c_run_subdir}`."
    )


def build_route_c_label_health_gating(
    execution_root_dir: Path,
    route_c_run_subdir: str,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    route_c_run_dir = _resolve_route_c_run_dir(execution_root_dir=execution_root_dir, route_c_run_subdir=route_c_run_subdir)

    schema = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "required_metrics": [
            "parsed_option_count",
            "parsed_option_ratio",
            "missing_option_count",
            "missing_option_ratio",
            "punct_only_count",
            "punct_only_ratio",
            "label_set",
            "class_balance",
            "health_gate_status",
            "blocked_reason",
        ],
        "source_paths": {
            "labeled_raw_results": "route_c_v6_labeled_illumination/illumination_probe/raw_results.jsonl",
            "label_health_rows": "route_c_v6_dataset_dir/benchmark_truth_leaning_label_health_rows.jsonl",
            "label_health_summary": "route_c_v6_dataset_dir/benchmark_truth_leaning_label_health_summary.json",
            "dataset_summary": "route_c_v6_dataset_dir/benchmark_truth_leaning_summary.json",
        },
    }
    gate_definition = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "gate_name": "route_c_label_health_gate",
        "rules": {
            "require_two_class_balance": True,
            "require_parsed_option_count_gt": 0,
            "max_missing_option_ratio": 0.8,
            "max_punct_only_ratio": 0.9,
        },
        "pass_condition": "all rules satisfied",
        "blocked_condition": "any rule violated",
    }
    instrumentation_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "plan": [
            "Load labeled illumination raw rows and label-health rows/summary.",
            "Compute parse and punctuation metrics if summary is missing.",
            "Evaluate gate rules and emit gate_result with blocked_reason.",
            "Persist detailed rows for postmortem analysis.",
        ],
        "run_reference": str(route_c_run_dir.resolve()),
    }

    health_summary_path = route_c_run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_health_summary.json"
    health_rows_path = route_c_run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_health_rows.jsonl"
    dataset_summary_path = route_c_run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_summary.json"
    labeled_raw_path = route_c_run_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl"

    label_health_rows = load_jsonl(health_rows_path) if health_rows_path.is_file() else []
    labeled_raw_rows = load_jsonl(labeled_raw_path) if labeled_raw_path.is_file() else []
    dataset_summary = load_json(dataset_summary_path) if dataset_summary_path.is_file() else {}

    if health_summary_path.is_file():
        health_summary = load_json(health_summary_path)
    else:
        responses = [str(row.get("response_text", "")) for row in labeled_raw_rows]
        parse_summary = summarize_option_label_parse(responses, parse_mode="robust_prefix")
        parsed_count = int(parse_summary.get("parsed_option_count", 0) or 0)
        missing_count = int(parse_summary.get("missing_option_count", 0) or 0)
        row_count = int(parse_summary.get("row_count", 0) or 0)
        parsed_ratio = float(parsed_count) / float(row_count) if row_count > 0 else 0.0
        missing_ratio = float(missing_count) / float(row_count) if row_count > 0 else 0.0
        class_balance = dataset_summary.get("class_balance")
        label_set = []
        if isinstance(class_balance, dict):
            if int(class_balance.get("label_0", 0) or 0) > 0:
                label_set.append(0)
            if int(class_balance.get("label_1", 0) or 0) > 0:
                label_set.append(1)
        health_summary = {
            "summary_status": "PASS_WITH_LIMITATIONS",
            "schema_version": SCHEMA_VERSION,
            "row_count": row_count,
            "parsed_option_count": parsed_count,
            "parsed_option_ratio": parsed_ratio,
            "missing_option_count": missing_count,
            "missing_option_ratio": missing_ratio,
            "punct_only_count": None,
            "punct_only_ratio": None,
            "label_set": label_set,
            "class_balance": class_balance,
        }

    class_balance = health_summary.get("class_balance")
    if class_balance is None:
        class_balance = dataset_summary.get("class_balance")

    label_0 = 0 if not isinstance(class_balance, dict) else int(class_balance.get("label_0", 0) or 0)
    label_1 = 0 if not isinstance(class_balance, dict) else int(class_balance.get("label_1", 0) or 0)
    parsed_option_count = int(health_summary.get("parsed_option_count", 0) or 0)
    missing_option_ratio = float(health_summary.get("missing_option_ratio", 0.0) or 0.0)
    punct_only_ratio_raw = health_summary.get("punct_only_ratio")
    punct_only_ratio = None if punct_only_ratio_raw is None else float(punct_only_ratio_raw)

    reasons: list[str] = []
    if not (label_0 > 0 and label_1 > 0):
        reasons.append("class_balance_not_two_class")
    if not (parsed_option_count > 0):
        reasons.append("parsed_option_count_zero")
    if missing_option_ratio > float(gate_definition["rules"]["max_missing_option_ratio"]):
        reasons.append("missing_option_ratio_too_high")
    max_punct = float(gate_definition["rules"]["max_punct_only_ratio"])
    if punct_only_ratio is not None and punct_only_ratio > max_punct:
        reasons.append("punct_only_ratio_too_high")

    gate_pass = len(reasons) == 0
    gate_result = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "gate_name": gate_definition["gate_name"],
        "gate_status": "PASS" if gate_pass else "BLOCKED",
        "class_balance": class_balance,
        "label_set": health_summary.get("label_set"),
        "parsed_option_count": parsed_option_count,
        "parsed_option_ratio": health_summary.get("parsed_option_ratio"),
        "missing_option_count": health_summary.get("missing_option_count"),
        "missing_option_ratio": missing_option_ratio,
        "punct_only_count": health_summary.get("punct_only_count"),
        "punct_only_ratio": punct_only_ratio,
        "blocked_reason": None if gate_pass else ";".join(reasons),
        "source_run_dir": str(route_c_run_dir.resolve()),
    }

    failure_modes = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "failure_modes": reasons,
        "failure_mode_counts": {
            "class_balance_not_two_class": 1 if "class_balance_not_two_class" in reasons else 0,
            "parsed_option_count_zero": 1 if "parsed_option_count_zero" in reasons else 0,
            "missing_option_ratio_too_high": 1 if "missing_option_ratio_too_high" in reasons else 0,
            "punct_only_ratio_too_high": 1 if "punct_only_ratio_too_high" in reasons else 0,
        },
        "notes": [
            "These failure modes are gate-level diagnostics, not model-quality metrics.",
            "A BLOCKED gate means execution should not proceed to logistic fitting.",
        ],
    }

    write_json(output_dir / "route_c_label_health_schema.json", schema)
    write_json(output_dir / "route_c_label_health_gate_definition.json", gate_definition)
    write_json(output_dir / "route_c_label_health_instrumentation_plan.json", instrumentation_plan)
    write_json(output_dir / "route_c_label_health_summary.json", health_summary)
    write_jsonl(output_dir / "route_c_label_health_detailed_rows.jsonl", label_health_rows)
    write_json(output_dir / "route_c_label_health_gate_result.json", gate_result)
    write_json(output_dir / "route_c_label_health_failure_modes.json", failure_modes)

    return {
        "summary": gate_result,
        "output_paths": {
            "schema": str((output_dir / "route_c_label_health_schema.json").resolve()),
            "gate_definition": str((output_dir / "route_c_label_health_gate_definition.json").resolve()),
            "instrumentation_plan": str((output_dir / "route_c_label_health_instrumentation_plan.json").resolve()),
            "health_summary": str((output_dir / "route_c_label_health_summary.json").resolve()),
            "detailed_rows": str((output_dir / "route_c_label_health_detailed_rows.jsonl").resolve()),
            "gate_result": str((output_dir / "route_c_label_health_gate_result.json").resolve()),
            "failure_modes": str((output_dir / "route_c_label_health_failure_modes.json").resolve()),
        },
    }
