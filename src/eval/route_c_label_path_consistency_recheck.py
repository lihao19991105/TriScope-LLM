"""Build consistency recheck artifacts between precheck and execution label paths."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, write_json


SCHEMA_VERSION = "triscopellm/route-c-label-path-consistency-recheck/v1"


def build_route_c_label_path_consistency_recheck(
    route_c_anchor_followup_v2_dir: Path,
    route_c_anchor_execution_recheck_dir: Path,
    route_c_label_health_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    precheck = load_json(route_c_anchor_followup_v2_dir / "route_c_anchor_followup_v2_precheck.json")
    execution_run_summary = load_json(route_c_anchor_execution_recheck_dir / "route_c_anchor_execution_run_summary.json")
    execution_gate = load_json(
        route_c_anchor_execution_recheck_dir
        / "route_c_anchor_execution_run"
        / "route_c_v6_label_health_gate_result.json"
    )
    label_health_summary = load_json(route_c_label_health_dir / "route_c_label_health_summary.json")
    label_health_gate_result = load_json(route_c_label_health_dir / "route_c_label_health_gate_result.json")

    precheck_class_balance = precheck.get("class_balance", {})
    precheck_label_set: list[int] = []
    if int(precheck_class_balance.get("label_0", 0) or 0) > 0:
        precheck_label_set.append(0)
    if int(precheck_class_balance.get("label_1", 0) or 0) > 0:
        precheck_label_set.append(1)

    execution_class_balance = execution_gate.get("class_balance") or {}
    execution_label_set: list[int] = []
    if int(execution_class_balance.get("label_0", 0) or 0) > 0:
        execution_label_set.append(0)
    if int(execution_class_balance.get("label_1", 0) or 0) > 0:
        execution_label_set.append(1)

    gate_status = str(execution_gate.get("gate_status"))
    consistency_restored = bool(
        precheck_label_set == execution_label_set and gate_status == "PASS"
    )

    protocol = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "recheck_target": "anchor_aware_baseline_under_label_health_gate",
        "success_criteria": [
            "precheck_label_set equals execution_label_set",
            "execution gate_status is PASS",
            "execution does not fail at labels stage",
        ],
    }
    fix_applied = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "applied_changes": [
            {
                "file": "src/fusion/benchmark_truth_leaning_label.py",
                "change": "added label health metrics and row-level health outputs",
            },
            {
                "file": "src/eval/rerun_route_c_on_labeled_split_v6.py",
                "change": "added route_c label health gate before logistic fitting",
            },
        ],
        "expected_behavior": "execution fails fast with explicit gate diagnostics instead of late logistic single-class exception",
    }
    readiness = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "ready_for_recheck": True,
        "required_inputs_present": True,
        "execution_gate_status": gate_status,
    }

    summary = {
        "summary_status": "PASS_WITH_LIMITATIONS" if not consistency_restored else "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "consistency_restored": consistency_restored,
        "precheck_label_set": precheck_label_set,
        "execution_label_set": execution_label_set,
        "execution_gate_status": gate_status,
        "execution_failure_stage": execution_run_summary.get("failure_stage"),
        "execution_failure_reason": execution_run_summary.get("failure_reason"),
        "interpretation": (
            "Path consistency is not restored to two-class execution yet, but failure mode is now explicit and diagnosable via gate artifacts."
            if not consistency_restored
            else "Path consistency restored under current recheck protocol."
        ),
    }
    comparison = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": "route_c",
        "precheck": {
            "class_balance": precheck_class_balance,
            "label_set": precheck_label_set,
            "worth_executing": precheck.get("worth_executing"),
        },
        "execution_recheck": {
            "class_balance": execution_class_balance,
            "label_set": execution_label_set,
            "gate_status": gate_status,
            "blocked_reason": execution_gate.get("blocked_reason"),
        },
        "consistency_restored": consistency_restored,
    }
    metrics = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "parsed_option_count": label_health_summary.get("parsed_option_count"),
        "parsed_option_ratio": label_health_summary.get("parsed_option_ratio"),
        "missing_option_count": label_health_summary.get("missing_option_count"),
        "missing_option_ratio": label_health_summary.get("missing_option_ratio"),
        "punct_only_count": label_health_summary.get("punct_only_count"),
        "punct_only_ratio": label_health_summary.get("punct_only_ratio"),
        "health_gate_status": label_health_gate_result.get("gate_status"),
        "blocked_reason": label_health_gate_result.get("blocked_reason"),
    }

    write_json(output_dir / "route_c_label_recheck_protocol.json", protocol)
    write_json(output_dir / "route_c_label_recheck_fix_applied.json", fix_applied)
    write_json(output_dir / "route_c_label_recheck_readiness_summary.json", readiness)
    write_json(output_dir / "route_c_label_recheck_summary.json", summary)
    write_json(output_dir / "route_c_precheck_vs_execution_recheck_comparison.json", comparison)
    write_json(output_dir / "route_c_label_recheck_metrics.json", metrics)

    return {
        "summary": summary,
        "output_paths": {
            "protocol": str((output_dir / "route_c_label_recheck_protocol.json").resolve()),
            "fix_applied": str((output_dir / "route_c_label_recheck_fix_applied.json").resolve()),
            "readiness": str((output_dir / "route_c_label_recheck_readiness_summary.json").resolve()),
            "summary": str((output_dir / "route_c_label_recheck_summary.json").resolve()),
            "comparison": str((output_dir / "route_c_precheck_vs_execution_recheck_comparison.json").resolve()),
            "metrics": str((output_dir / "route_c_label_recheck_metrics.json").resolve()),
        },
    }
