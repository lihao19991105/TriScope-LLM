"""Minimal stability extension reruns for route_c output-normalization recovery.

This stage inherits 142 frozen settings exactly and only increases repeated rerun count.
"""

from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json, write_jsonl
from src.eval.rerun_route_c_on_labeled_split_v6 import count_jsonl_rows, run_route_c_v6


SCHEMA_VERSION = "triscopellm/route-c-label-output-normalization-stability-extension-recheck/v1"


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
        "failure_category_distribution": normalized_dist,
    }


def _run_rows_metrics(run_rows: list[dict[str, Any]]) -> dict[str, Any]:
    run_count = len(run_rows)
    gate_pass_flags = [str(row.get("gate_status")) == "PASS" for row in run_rows]
    dual_class_flags = [bool(row.get("dual_class_restored")) for row in run_rows]
    consistency_flags = [bool(row.get("consistency_restored")) for row in run_rows]

    parsed_values = [float(row.get("parsed_option_count") or 0.0) for row in run_rows]
    missing_ratio_values = [float(row.get("missing_option_ratio") or 0.0) for row in run_rows]
    punct_ratio_values = [float(row.get("punct_only_ratio") or 0.0) for row in run_rows]

    regressed_runs = [
        str(row.get("rerun_id"))
        for row in run_rows
        if str(row.get("gate_status")) != "PASS" or list(row.get("execution_label_set") or []) != [0, 1]
    ]

    return {
        "run_count": run_count,
        "gate_pass_rate": float(sum(gate_pass_flags)) / float(run_count) if run_count > 0 else 0.0,
        "dual_class_restoration_rate": float(sum(dual_class_flags)) / float(run_count) if run_count > 0 else 0.0,
        "consistency_restored_rate": float(sum(consistency_flags)) / float(run_count) if run_count > 0 else 0.0,
        "any_regression_to_blocked": any(not flag for flag in gate_pass_flags),
        "any_regression_to_single_class": any(not flag for flag in dual_class_flags),
        "regressed_runs": regressed_runs,
        "parsed_option_count_stats": _metric_stats(parsed_values),
        "missing_option_ratio_stats": _metric_stats(missing_ratio_values),
        "punct_only_ratio_stats": _metric_stats(punct_ratio_values),
    }


def _assert_frozen_inheritance(
    previous_frozen: dict[str, Any],
    materialized_inputs_dir: Path,
    precheck_label_set: list[int],
) -> dict[str, Any]:
    frozen = dict(previous_frozen.get("frozen_settings") or {})
    must_match = list(previous_frozen.get("must_match_exactly") or [])
    if not frozen:
        raise ValueError("142 frozen settings payload is empty.")

    current_budgets = {
        "reasoning_budget": count_jsonl_rows(materialized_inputs_dir / "reasoning_query_contracts.jsonl"),
        "confidence_budget": count_jsonl_rows(materialized_inputs_dir / "confidence_query_contracts.jsonl"),
        "illumination_budget": count_jsonl_rows(materialized_inputs_dir / "illumination_query_contracts.jsonl"),
        "labeled_illumination_budget": count_jsonl_rows(
            materialized_inputs_dir / "labeled_illumination_query_contracts.jsonl"
        ),
    }

    expected_input_root = str(materialized_inputs_dir.resolve())
    if str(frozen.get("input_root")) != expected_input_root:
        raise ValueError(
            "142 frozen input_root mismatch. "
            f"expected `{expected_input_root}`, got `{frozen.get('input_root')}`"
        )

    for key, value in current_budgets.items():
        if int(frozen.get(key, -1)) != int(value):
            raise ValueError(
                f"142 frozen `{key}` mismatch: expected {value}, got {frozen.get(key)}"
            )

    if list(frozen.get("precheck_label_set_reference") or []) != precheck_label_set:
        raise ValueError(
            "142 frozen precheck label set mismatch: "
            f"expected {precheck_label_set}, got {frozen.get('precheck_label_set_reference')}"
        )

    if frozen.get("execution_path") != "run_route_c_v6":
        raise ValueError("142 frozen execution_path is not run_route_c_v6.")
    if frozen.get("model_profile_name") != "pilot_small_hf":
        raise ValueError("142 frozen model profile changed unexpectedly.")
    if frozen.get("label_parse_mode") != "robust_prefix":
        raise ValueError("142 frozen label_parse_mode changed unexpectedly.")
    if frozen.get("label_normalization_mode") != "conservative":
        raise ValueError("142 frozen normalization mode changed unexpectedly.")
    if not bool(frozen.get("label_parser_instrumentation")):
        raise ValueError("142 frozen parser instrumentation must be true.")

    return {
        "frozen_settings": frozen,
        "must_match_exactly": must_match,
    }


def _build_report(
    extension_frozen: dict[str, Any],
    summary: dict[str, Any],
    details: list[dict[str, Any]],
) -> str:
    lines: list[str] = []
    lines.append("# Route-C Output Normalization Stability Extension Recheck Report")
    lines.append("")
    lines.append("## Objective")
    lines.append("Only increase repeated rerun count under fully inherited 142 frozen settings.")
    lines.append("")
    lines.append("## Frozen Inheritance")
    lines.append(f"- inherited_from: {extension_frozen['inherits_from']['frozen_settings_path']}")
    lines.append(f"- previous_rerun_count: {extension_frozen['protocol']['previous_rerun_count']}")
    lines.append(f"- additional_rerun_count: {extension_frozen['protocol']['additional_rerun_count']}")
    lines.append(f"- cumulative_rerun_count: {extension_frozen['protocol']['cumulative_rerun_count']}")
    lines.append("")
    lines.append("## Added-runs Stability")
    added = summary["extension_added_runs"]
    lines.append(f"- gate_pass_rate: {added['gate_pass_rate']:.4f}")
    lines.append(f"- dual_class_restoration_rate: {added['dual_class_restoration_rate']:.4f}")
    lines.append(f"- consistency_restored_rate: {added['consistency_restored_rate']:.4f}")
    lines.append(f"- any_regression_to_blocked: {added['any_regression_to_blocked']}")
    lines.append(f"- any_regression_to_single_class: {added['any_regression_to_single_class']}")
    lines.append("")
    lines.append("## Cumulative (142 + 143)")
    cum = summary["cumulative_142_143"]
    lines.append(f"- total_run_count: {cum['run_count']}")
    lines.append(f"- gate_pass_rate: {cum['gate_pass_rate']:.4f}")
    lines.append(f"- dual_class_restoration_rate: {cum['dual_class_restoration_rate']:.4f}")
    lines.append(f"- consistency_restored_rate: {cum['consistency_restored_rate']:.4f}")
    lines.append(f"- any_regression_to_blocked: {cum['any_regression_to_blocked']}")
    lines.append(f"- any_regression_to_single_class: {cum['any_regression_to_single_class']}")
    lines.append("")
    lines.append("## Added Run-level")
    for row in details:
        lines.append(
            "- "
            + f"{row['rerun_id']}: gate={row['gate_status']}, consistency={row['consistency_restored']}, "
            + f"execution_label_set={row['execution_label_set']}, parsed={row['parsed_option_count']}, "
            + f"missing_ratio={row['missing_option_ratio']}, punct_ratio={row['punct_only_ratio']}"
        )
    return "\n".join(lines) + "\n"


def build_route_c_label_output_normalization_stability_extension_recheck(
    route_c_anchor_followup_v2_dir: Path,
    route_c_anchor_execution_recheck_dir: Path,
    previous_stability_recheck_dir: Path,
    models_config_path: Path,
    reasoning_config_path: Path,
    confidence_config_path: Path,
    illumination_config_path: Path,
    reasoning_prompt_dir: Path,
    confidence_prompt_dir: Path,
    illumination_prompt_dir: Path,
    output_dir: Path,
    additional_rerun_count: int = 5,
) -> dict[str, Any]:
    if additional_rerun_count <= 0:
        raise ValueError("additional_rerun_count must be > 0.")

    output_dir.mkdir(parents=True, exist_ok=True)

    materialized_inputs_dir = route_c_anchor_execution_recheck_dir / "materialized_route_c_anchor_execution_inputs"
    if not materialized_inputs_dir.is_dir():
        raise ValueError(f"Controlled input dir not found: `{materialized_inputs_dir}`")

    previous_frozen_path = _required_file(
        previous_stability_recheck_dir / "route_c_label_output_normalization_stability_frozen_settings.json"
    )
    previous_summary_path = _required_file(
        previous_stability_recheck_dir / "route_c_label_output_normalization_stability_recheck_summary.json"
    )
    previous_details_path = _required_file(
        previous_stability_recheck_dir / "route_c_label_output_normalization_stability_recheck_details.jsonl"
    )

    previous_frozen = load_json(previous_frozen_path)
    previous_summary = load_json(previous_summary_path)
    previous_details = load_jsonl(previous_details_path)

    precheck = load_json(_required_file(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_precheck.json"))
    precheck_label_set = _label_set_from_class_balance(precheck.get("class_balance"))

    inherited = _assert_frozen_inheritance(
        previous_frozen=previous_frozen,
        materialized_inputs_dir=materialized_inputs_dir,
        precheck_label_set=precheck_label_set,
    )
    frozen_settings = inherited["frozen_settings"]

    seed = int(frozen_settings["seed"])
    label_threshold = float(frozen_settings["label_threshold"])
    label_parse_mode = str(frozen_settings["label_parse_mode"])
    model_profile_name = str(frozen_settings["model_profile_name"])

    extension_rows: list[dict[str, Any]] = []
    for index in range(additional_rerun_count):
        rerun_id = f"extension_rerun_{index + 1:02d}"
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
                model_profile_name=model_profile_name,
                label_parse_mode=label_parse_mode,
                label_normalization_mode="conservative",
                label_parser_instrumentation=True,
            )
        except Exception as exc:
            execution_error = str(exc)

        gate = _extract_gate_metrics(run_dir)
        gate_status = str(gate.get("gate_status") or "UNKNOWN")
        execution_label_set = list(gate.get("execution_label_set") or [])
        consistency_restored = bool(gate_status == "PASS" and execution_label_set == precheck_label_set)
        dual_class_restored = bool(execution_label_set == [0, 1])

        extension_rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "rerun_id": rerun_id,
                "rerun_tag": "143_stability_extension",
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

    extension_metrics = _run_rows_metrics(extension_rows)
    cumulative_rows = previous_details + extension_rows
    cumulative_metrics = _run_rows_metrics(cumulative_rows)

    extension_frozen = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "inherits_from": {
            "stage": "142-route-c-output-normalization-stability-recheck",
            "frozen_settings_path": str(previous_frozen_path.resolve()),
            "summary_path": str(previous_summary_path.resolve()),
            "details_path": str(previous_details_path.resolve()),
            "previous_rerun_count": int(previous_summary.get("rerun_count", len(previous_details))),
        },
        "frozen_settings": frozen_settings,
        "must_match_exactly": inherited["must_match_exactly"],
        "allowed_run_tag_only_fields": [
            "rerun_id",
            "run_dir",
            "rerun_tag",
            "timestamp_fields",
            "report_text",
        ],
        "protocol": {
            "rerun_mode": "same_setting_repeat",
            "selection_rule": "keep_all_runs_no_cherry_pick",
            "previous_rerun_count": int(previous_summary.get("rerun_count", len(previous_details))),
            "additional_rerun_count": additional_rerun_count,
            "cumulative_rerun_count": len(cumulative_rows),
        },
        "verdict_policy": {
            "stable_enough": {
                "all_added_runs_pass": True,
                "no_added_regression": True,
                "no_cumulative_regression": True,
                "cumulative_run_count_at_least": 8,
                "parseability_bounds": {
                    "parsed_option_count_min": 5,
                    "missing_option_ratio_max": 0.16666666666666666,
                    "punct_only_ratio_max": 0.0,
                },
            },
            "provisionally_stable": {
                "core_restoration_holds_but_evidence_not_enough": True,
            },
            "not_yet_stable": {
                "any_regression_to_blocked": True,
                "any_regression_to_single_class": True,
                "consistency_instability": True,
                "material_parseability_regression": True,
            },
        },
    }

    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "additional_rerun_count": additional_rerun_count,
        "previous_rerun_count": int(previous_summary.get("rerun_count", len(previous_details))),
        "extension_added_runs": extension_metrics,
        "cumulative_142_143": cumulative_metrics,
        "constraints_kept": {
            "gate_threshold_unchanged": True,
            "label_semantics_unchanged": True,
            "no_budget_expansion": True,
            "no_model_axis_expansion": True,
            "no_prompt_family_expansion": True,
            "parser_logic_unchanged": True,
            "normalization_logic_unchanged": True,
        },
    }

    report_text = _build_report(
        extension_frozen=extension_frozen,
        summary=summary,
        details=extension_rows,
    )

    write_json(
        output_dir / "route_c_label_output_normalization_stability_extension_frozen_settings.json",
        extension_frozen,
    )
    write_json(
        output_dir / "route_c_label_output_normalization_stability_extension_recheck_summary.json",
        summary,
    )
    write_jsonl(
        output_dir / "route_c_label_output_normalization_stability_extension_recheck_details.jsonl",
        extension_rows,
    )
    (output_dir / "route_c_label_output_normalization_stability_extension_report.md").write_text(
        report_text,
        encoding="utf-8",
    )

    return {
        "summary": summary,
        "output_paths": {
            "frozen_settings": str(
                (
                    output_dir
                    / "route_c_label_output_normalization_stability_extension_frozen_settings.json"
                ).resolve()
            ),
            "summary": str(
                (
                    output_dir
                    / "route_c_label_output_normalization_stability_extension_recheck_summary.json"
                ).resolve()
            ),
            "details": str(
                (
                    output_dir
                    / "route_c_label_output_normalization_stability_extension_recheck_details.jsonl"
                ).resolve()
            ),
            "report": str(
                (
                    output_dir
                    / "route_c_label_output_normalization_stability_extension_report.md"
                ).resolve()
            ),
        },
    }
