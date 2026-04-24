"""Repeated same-setting stability reruns for route_c output-normalization recovery."""

from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json, write_jsonl
from src.eval.rerun_route_c_on_labeled_split_v6 import count_jsonl_rows, run_route_c_v6


SCHEMA_VERSION = "triscopellm/route-c-label-output-normalization-stability-recheck/v1"


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def _label_set_from_class_balance(class_balance: dict[str, Any] | None) -> list[int]:
    if not isinstance(class_balance, dict):
        return []
    label_set: list[int] = []
    if int(class_balance.get("label_0", 0) or 0) > 0:
        label_set.append(0)
    if int(class_balance.get("label_1", 0) or 0) > 0:
        label_set.append(1)
    return label_set


def _metric_stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "max": None, "mean": None}
    return {"min": min(values), "max": max(values), "mean": mean(values)}


def _extract_gate_metrics(run_dir: Path) -> dict[str, Any]:
    gate_result_path = run_dir / "route_c_v6_label_health_gate_result.json"
    gate_result = load_json(gate_result_path) if gate_result_path.is_file() else {}

    dataset_dir = run_dir / "route_c_v6_dataset_dir"
    health_summary_path = dataset_dir / "benchmark_truth_leaning_label_health_summary.json"
    health_summary = load_json(health_summary_path) if health_summary_path.is_file() else {}
    parse_compare_path = dataset_dir / "benchmark_truth_leaning_label_parse_compare.json"
    parse_compare = load_json(parse_compare_path) if parse_compare_path.is_file() else {}

    class_balance = gate_result.get("class_balance")
    execution_label_set = _label_set_from_class_balance(class_balance)
    normalized_dist = parse_compare.get("normalized", {}).get("failure_category_distribution", {})

    return {
        "gate_status": gate_result.get("gate_status"),
        "blocked_reason": gate_result.get("blocked_reason"),
        "parsed_option_count": gate_result.get("parsed_option_count"),
        "missing_option_ratio": gate_result.get("missing_option_ratio"),
        "punct_only_ratio": gate_result.get("punct_only_ratio"),
        "class_balance": class_balance,
        "execution_label_set": execution_label_set,
        "option_parse_mode": gate_result.get("option_parse_mode"),
        "option_normalization_mode": gate_result.get("option_normalization_mode"),
        "failure_category_distribution": normalized_dist,
        "health_summary": health_summary,
        "parse_compare": parse_compare,
    }


def _build_report(
    frozen: dict[str, Any],
    summary: dict[str, Any],
    details: list[dict[str, Any]],
) -> str:
    lines: list[str] = []
    lines.append("# Route-C Output Normalization Stability Recheck Report")
    lines.append("")
    lines.append("## Frozen Settings")
    lines.append(f"- rerun_count: {frozen['protocol']['rerun_count']}")
    lines.append(f"- seed: {frozen['frozen_settings']['seed']}")
    lines.append(f"- model_profile: {frozen['frozen_settings']['model_profile_name']}")
    lines.append(f"- label_parse_mode: {frozen['frozen_settings']['label_parse_mode']}")
    lines.append(f"- label_normalization_mode: {frozen['frozen_settings']['label_normalization_mode']}")
    lines.append(f"- label_parser_instrumentation: {frozen['frozen_settings']['label_parser_instrumentation']}")
    lines.append("")
    lines.append("## Stability Summary")
    lines.append(f"- gate_pass_rate: {summary['stability']['gate_pass_rate']:.4f}")
    lines.append(f"- dual_class_restoration_rate: {summary['stability']['dual_class_restoration_rate']:.4f}")
    lines.append(f"- consistency_restored_rate: {summary['stability']['consistency_restored_rate']:.4f}")
    lines.append(f"- any_regression_to_blocked: {summary['stability']['any_regression_to_blocked']}")
    lines.append(f"- any_regression_to_single_class: {summary['stability']['any_regression_to_single_class']}")
    lines.append("")
    lines.append("## Run-level")
    for row in details:
        lines.append(
            "- "
            + f"{row['rerun_id']}: gate={row['gate_status']}, consistency={row['consistency_restored']}, "
            + f"execution_label_set={row['execution_label_set']}, parsed={row['parsed_option_count']}, "
            + f"missing_ratio={row['missing_option_ratio']}, punct_ratio={row['punct_only_ratio']}"
        )
    return "\n".join(lines) + "\n"


def build_route_c_label_output_normalization_stability_recheck(
    route_c_anchor_followup_v2_dir: Path,
    route_c_anchor_execution_recheck_dir: Path,
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    reasoning_prompt_dir: Path,
    confidence_prompt_dir: Path,
    illumination_prompt_dir: Path,
    output_dir: Path,
    rerun_count: int = 3,
    seed: int = 42,
    label_threshold: float = 0.5,
    label_parse_mode: str = "robust_prefix",
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    materialized_inputs_dir = route_c_anchor_execution_recheck_dir / "materialized_route_c_anchor_execution_inputs"
    if not materialized_inputs_dir.is_dir():
        raise ValueError(f"Controlled input dir not found: `{materialized_inputs_dir}`")

    precheck = load_json(_required_file(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_precheck.json"))
    precheck_class_balance = precheck.get("class_balance")
    precheck_label_set = _label_set_from_class_balance(precheck_class_balance)

    frozen_settings = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "from_plan": "141-route-c-parser-output-normalization-minimal-repair",
        "frozen_settings": {
            "execution_path": "run_route_c_v6",
            "input_root": str(materialized_inputs_dir.resolve()),
            "model_profile_name": "pilot_small_hf",
            "label_parse_mode": label_parse_mode,
            "label_normalization_mode": "conservative",
            "label_parser_instrumentation": True,
            "seed": seed,
            "label_threshold": label_threshold,
            "reasoning_budget": count_jsonl_rows(materialized_inputs_dir / "reasoning_query_contracts.jsonl"),
            "confidence_budget": count_jsonl_rows(materialized_inputs_dir / "confidence_query_contracts.jsonl"),
            "illumination_budget": count_jsonl_rows(materialized_inputs_dir / "illumination_query_contracts.jsonl"),
            "labeled_illumination_budget": count_jsonl_rows(
                materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl"
            ),
            "gate_definition_used_by_execution": {
                "require_two_class_balance": True,
                "require_parsed_option_count_gt": 0,
                "ready_to_run_must_be_true": True,
                "blocked_on_health_gate_failure": True,
            },
            "precheck_label_set_reference": precheck_label_set,
        },
        "must_match_exactly": [
            "execution_path",
            "input_root",
            "model_profile_name",
            "label_parse_mode",
            "label_normalization_mode",
            "label_parser_instrumentation",
            "seed",
            "label_threshold",
            "reasoning_budget",
            "confidence_budget",
            "illumination_budget",
            "labeled_illumination_budget",
            "gate_definition_used_by_execution",
            "precheck_label_set_reference",
        ],
        "allowed_run_tag_only_fields": [
            "rerun_id",
            "run_dir",
            "timestamp_fields",
            "report_text",
        ],
        "protocol": {
            "rerun_count": rerun_count,
            "rerun_mode": "same_setting_repeat",
            "selection_rule": "keep_all_runs_no_cherry_pick",
        },
    }

    run_rows: list[dict[str, Any]] = []
    for index in range(rerun_count):
        rerun_id = f"rerun_{index + 1:02d}"
        run_dir = output_dir / "runs" / rerun_id
        execution_error: str | None = None
        try:
            run_route_c_v6(
                models_config_path=models_config_path,
                reasoning_config_path=reasoning_config_path,
                confidence_config_path=confidence_config_path,
                illumination_config_path=illumination_config_path,
                reasoning_prompt_dir=reasoning_prompt_dir,
                confidence_prompt_dir=confidence_prompt_dir,
                illumination_prompt_dir=illumination_prompt_dir,
                v6_inputs_dir=materialized_inputs_dir,
                output_dir=run_dir,
                seed=seed,
                label_threshold=label_threshold,
                model_profile_name="pilot_small_hf",
                label_parse_mode=label_parse_mode,
                label_normalization_mode="conservative",
                label_parser_instrumentation=True,
            )
        except Exception as exc:
            execution_error = str(exc)

        gate = _extract_gate_metrics(run_dir)
        gate_status = str(gate.get("gate_status") or "UNKNOWN")
        execution_label_set = gate.get("execution_label_set") or []
        consistency_restored = bool(gate_status == "PASS" and execution_label_set == precheck_label_set)
        dual_class_restored = bool(execution_label_set == [0, 1])

        run_rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "rerun_id": rerun_id,
                "run_dir": str(run_dir.resolve()),
                "run_pass": bool(gate_status == "PASS" and execution_error is None),
                "gate_status": gate_status,
                "blocked_reason": gate.get("blocked_reason"),
                "consistency_restored": consistency_restored,
                "precheck_label_set": precheck_label_set,
                "execution_label_set": execution_label_set,
                "dual_class_restored": dual_class_restored,
                "parsed_option_count": gate.get("parsed_option_count"),
                "missing_option_ratio": gate.get("missing_option_ratio"),
                "punct_only_ratio": gate.get("punct_only_ratio"),
                "class_balance": gate.get("class_balance"),
                "label_set": execution_label_set,
                "failure_category_distribution": gate.get("failure_category_distribution"),
                "execution_error": execution_error,
            }
        )

    gate_pass_flags = [str(row.get("gate_status")) == "PASS" for row in run_rows]
    dual_class_flags = [bool(row.get("dual_class_restored")) for row in run_rows]
    consistency_flags = [bool(row.get("consistency_restored")) for row in run_rows]

    parsed_values = [float(row.get("parsed_option_count") or 0.0) for row in run_rows]
    missing_ratio_values = [float(row.get("missing_option_ratio") or 0.0) for row in run_rows]
    punct_ratio_values = [float(row.get("punct_only_ratio") or 0.0) for row in run_rows]

    regressed_runs = [
        row["rerun_id"]
        for row in run_rows
        if str(row.get("gate_status")) != "PASS" or list(row.get("execution_label_set") or []) != [0, 1]
    ]

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "rerun_count": rerun_count,
        "frozen_settings_path": str(
            (output_dir / "route_c_label_output_normalization_stability_frozen_settings.json").resolve()
        ),
        "precheck_label_set": precheck_label_set,
        "stability": {
            "gate_pass_rate": float(sum(gate_pass_flags)) / float(rerun_count) if rerun_count > 0 else 0.0,
            "dual_class_restoration_rate": float(sum(dual_class_flags)) / float(rerun_count) if rerun_count > 0 else 0.0,
            "consistency_restored_rate": float(sum(consistency_flags)) / float(rerun_count)
            if rerun_count > 0
            else 0.0,
            "any_regression_to_blocked": any(not flag for flag in gate_pass_flags),
            "any_regression_to_single_class": any(not flag for flag in dual_class_flags),
            "regressed_runs": regressed_runs,
            "parsed_option_count_stats": _metric_stats(parsed_values),
            "missing_option_ratio_stats": _metric_stats(missing_ratio_values),
            "punct_only_ratio_stats": _metric_stats(punct_ratio_values),
        },
        "constraints_kept": {
            "gate_threshold_unchanged": True,
            "label_semantics_unchanged": True,
            "no_budget_expansion": True,
            "no_model_axis_expansion": True,
            "no_prompt_family_expansion": True,
        },
    }

    report_text = _build_report(frozen=frozen_settings, summary=summary, details=run_rows)

    write_json(output_dir / "route_c_label_output_normalization_stability_frozen_settings.json", frozen_settings)
    write_json(output_dir / "route_c_label_output_normalization_stability_recheck_summary.json", summary)
    write_jsonl(output_dir / "route_c_label_output_normalization_stability_recheck_details.jsonl", run_rows)
    (output_dir / "route_c_label_output_normalization_stability_report.md").write_text(report_text, encoding="utf-8")

    return {
        "summary": summary,
        "output_paths": {
            "frozen_settings": str(
                (output_dir / "route_c_label_output_normalization_stability_frozen_settings.json").resolve()
            ),
            "summary": str(
                (output_dir / "route_c_label_output_normalization_stability_recheck_summary.json").resolve()
            ),
            "details": str(
                (output_dir / "route_c_label_output_normalization_stability_recheck_details.jsonl").resolve()
            ),
            "report": str((output_dir / "route_c_label_output_normalization_stability_report.md").resolve()),
        },
    }
