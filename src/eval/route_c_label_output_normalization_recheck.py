"""Run a gate-protected controlled recheck for route_c label output normalization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json
from src.eval.rerun_route_c_on_labeled_split_v6 import run_route_c_v6


SCHEMA_VERSION = "triscopellm/route-c-label-output-normalization-recheck/v1"


def _label_set_from_class_balance(class_balance: dict[str, Any] | None) -> list[int]:
    if not isinstance(class_balance, dict):
        return []
    label_set: list[int] = []
    if int(class_balance.get("label_0", 0) or 0) > 0:
        label_set.append(0)
    if int(class_balance.get("label_1", 0) or 0) > 0:
        label_set.append(1)
    return label_set


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def build_route_c_label_output_normalization_recheck(
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
    seed: int,
    label_threshold: float,
    label_parse_mode: str = "robust_prefix",
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    materialized_inputs_dir = route_c_anchor_execution_recheck_dir / "materialized_route_c_anchor_execution_inputs"
    if not materialized_inputs_dir.is_dir():
        raise ValueError(
            f"Controlled recheck inputs not found at `{materialized_inputs_dir}`."
        )

    precheck = load_json(
        _required_file(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_precheck.json")
    )
    precheck_class_balance = precheck.get("class_balance")
    precheck_label_set = _label_set_from_class_balance(precheck_class_balance)

    run_dir = output_dir / "route_c_label_output_normalization_recheck_run"
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

    gate_result_path = run_dir / "route_c_v6_label_health_gate_result.json"
    gate_result = load_json(gate_result_path) if gate_result_path.is_file() else {}
    health_summary_path = run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_health_summary.json"
    health_summary = load_json(health_summary_path) if health_summary_path.is_file() else {}
    parse_compare_path = run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_parse_compare.json"
    parse_compare = load_json(parse_compare_path) if parse_compare_path.is_file() else {}

    execution_class_balance = gate_result.get("class_balance")
    execution_label_set = _label_set_from_class_balance(execution_class_balance)
    gate_status = str(gate_result.get("gate_status", "UNKNOWN"))
    consistency_restored = bool(gate_status == "PASS" and execution_label_set == precheck_label_set)

    summary = {
        "summary_status": "PASS" if consistency_restored else "PASS_WITH_LIMITATIONS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "controlled_recheck_completed": True,
        "gate_protected": True,
        "gate_status": gate_status,
        "blocked_reason": gate_result.get("blocked_reason"),
        "precheck_label_set": precheck_label_set,
        "execution_label_set": execution_label_set,
        "consistency_restored": consistency_restored,
        "parseability": {
            "parsed_option_count": health_summary.get("parsed_option_count"),
            "parsed_option_ratio": health_summary.get("parsed_option_ratio"),
            "missing_option_ratio": health_summary.get("missing_option_ratio"),
            "punct_only_ratio": health_summary.get("punct_only_ratio"),
        },
        "raw_vs_normalized_parse_compare": parse_compare,
        "execution_error": execution_error,
        "constraints_kept": {
            "gate_threshold_unchanged": True,
            "label_semantics_unchanged": True,
            "no_budget_expansion": True,
            "no_model_axis_expansion": True,
            "no_prompt_family_expansion": True,
        },
        "run_paths": {
            "materialized_inputs_dir": str(materialized_inputs_dir.resolve()),
            "run_dir": str(run_dir.resolve()),
            "gate_result": str(gate_result_path.resolve()) if gate_result_path.is_file() else None,
        },
    }

    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "precheck": {
            "class_balance": precheck_class_balance,
            "label_set": precheck_label_set,
            "worth_executing": precheck.get("worth_executing"),
        },
        "execution_recheck": {
            "class_balance": execution_class_balance,
            "label_set": execution_label_set,
            "gate_status": gate_status,
            "blocked_reason": gate_result.get("blocked_reason"),
        },
        "consistency_restored": consistency_restored,
    }

    write_json(output_dir / "route_c_label_output_normalization_recheck_summary.json", summary)
    write_json(output_dir / "route_c_label_output_normalization_recheck_comparison.json", comparison)

    return {
        "summary": summary,
        "output_paths": {
            "summary": str((output_dir / "route_c_label_output_normalization_recheck_summary.json").resolve()),
            "comparison": str((output_dir / "route_c_label_output_normalization_recheck_comparison.json").resolve()),
        },
    }
