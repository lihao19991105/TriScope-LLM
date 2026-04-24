"""Post-analysis for route_c stable baseline time-separated replay (stage 144)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json


SCHEMA_VERSION = "triscopellm/post-route-c-stable-baseline-time-separated-replay-analysis/v1"


def _metric_range(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "max": None, "mean": None}
    return {
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def _rows_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    run_count = len(rows)
    gate_pass_flags = [str(row.get("gate_status")) == "PASS" for row in rows]
    dual_class_flags = [list(row.get("execution_label_set") or []) == [0, 1] for row in rows]
    consistency_flags = [bool(row.get("consistency_restored")) for row in rows]

    parsed_values = [float(row.get("parsed_option_count") or 0.0) for row in rows]
    missing_values = [float(row.get("missing_option_ratio") or 0.0) for row in rows]
    punct_values = [float(row.get("punct_only_ratio") or 0.0) for row in rows]

    return {
        "run_count": run_count,
        "gate_pass_rate": float(sum(gate_pass_flags)) / float(run_count) if run_count > 0 else 0.0,
        "dual_class_restoration_rate": float(sum(dual_class_flags)) / float(run_count) if run_count > 0 else 0.0,
        "consistency_restored_rate": float(sum(consistency_flags)) / float(run_count) if run_count > 0 else 0.0,
        "any_regression_to_blocked": any(not flag for flag in gate_pass_flags),
        "any_regression_to_single_class": any(not flag for flag in dual_class_flags),
        "parsed_option_count_range": _metric_range(parsed_values),
        "missing_option_ratio_range": _metric_range(missing_values),
        "punct_only_ratio_range": _metric_range(punct_values),
    }


def _parseability_hard_regression(metrics: dict[str, Any]) -> bool:
    parsed_min = metrics.get("parsed_option_count_range", {}).get("min")
    missing_max = metrics.get("missing_option_ratio_range", {}).get("max")
    punct_max = metrics.get("punct_only_ratio_range", {}).get("max")

    if parsed_min is None or missing_max is None or punct_max is None:
        return True
    if float(parsed_min) < 5.0:
        return True
    if float(missing_max) > 0.16666666666666666:
        return True
    if float(punct_max) > 0.0:
        return True
    return False


def _build_report(compare: dict[str, Any], verdict: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Route-C Stable Baseline Time-Separated Replay Analysis")
    lines.append("")
    lines.append("## Five-stage Compare")
    lines.append(
        "- stage_140_blocked: "
        + f"gate={compare['stage_140_blocked']['label_health_gate_status']}, "
        + f"execution_label_set={compare['stage_140_blocked']['execution_label_set']}, "
        + f"consistency_restored={compare['stage_140_blocked']['consistency_restored']}"
    )
    lines.append(
        "- stage_141_first_recovery: "
        + f"gate={compare['stage_141_first_recovery']['gate_status']}, "
        + f"execution_label_set={compare['stage_141_first_recovery']['execution_label_set']}, "
        + f"consistency_restored={compare['stage_141_first_recovery']['consistency_restored']}"
    )
    lines.append(
        "- stage_142_repeated_recheck: "
        + f"run_count={compare['stage_142_repeated_reruns']['run_count']}, "
        + f"gate_pass_rate={compare['stage_142_repeated_reruns']['gate_pass_rate']:.4f}, "
        + f"dual_class_restoration_rate={compare['stage_142_repeated_reruns']['dual_class_restoration_rate']:.4f}"
    )
    lines.append(
        "- stage_143_extension_recheck: "
        + f"run_count={compare['stage_143_extension_reruns']['run_count']}, "
        + f"gate_pass_rate={compare['stage_143_extension_reruns']['gate_pass_rate']:.4f}, "
        + f"dual_class_restoration_rate={compare['stage_143_extension_reruns']['dual_class_restoration_rate']:.4f}"
    )
    lines.append(
        "- stage_144_time_separated_replay: "
        + f"run_count={compare['stage_144_time_separated_replay']['run_count']}, "
        + f"gate_pass_rate={compare['stage_144_time_separated_replay']['gate_pass_rate']:.4f}, "
        + f"dual_class_restoration_rate={compare['stage_144_time_separated_replay']['dual_class_restoration_rate']:.4f}"
    )
    lines.append("")
    lines.append("## Time Separation")
    ts = compare["time_separation"]
    lines.append(f"- stage_143_latest_completion_time_utc: {ts['stage_143_latest_completion_time_utc']}")
    lines.append(f"- replay_start_time_utc: {ts['replay_start_time_utc']}")
    lines.append(f"- elapsed_minutes_since_stage_143: {ts['elapsed_minutes_since_stage_143']:.4f}")
    lines.append(f"- protocol_valid: {ts['protocol_valid']}")
    lines.append("")
    lines.append("## Verdict")
    lines.append(f"- replay_verdict: {verdict['replay_verdict']}")
    lines.append(f"- verdict_confidence: {verdict['verdict_confidence']}")
    lines.append("- evidence:")
    for item in verdict.get("evidence", []):
        lines.append(f"  - {item}")
    lines.append("")
    lines.append("## Single Recommendation")
    lines.append(f"- {verdict['single_next_step']}")
    return "\n".join(lines) + "\n"


def build_post_route_c_stable_baseline_time_separated_replay_analysis(
    prior_blocked_analysis_dir: Path,
    first_recovery_recheck_dir: Path,
    stage_143_analysis_dir: Path,
    stage_143_recheck_dir: Path,
    replay_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    blocked_summary = load_json(prior_blocked_analysis_dir / "route_c_label_repair_analysis_summary.json")
    first_recovery_summary = load_json(
        first_recovery_recheck_dir / "route_c_label_output_normalization_recheck_summary.json"
    )

    stage_143_compare = load_json(
        stage_143_analysis_dir / "route_c_label_output_normalization_stability_extension_compare.json"
    )
    stage_143_summary = load_json(
        stage_143_recheck_dir / "route_c_label_output_normalization_stability_extension_recheck_summary.json"
    )

    replay_summary = load_json(replay_dir / "route_c_stable_baseline_time_separated_replay_summary.json")
    replay_details = load_jsonl(replay_dir / "route_c_stable_baseline_time_separated_replay_details.jsonl")

    stage_142 = dict(stage_143_compare.get("stage_142_repeated_reruns") or {})
    stage_143 = dict(stage_143_compare.get("stage_143_extension_reruns") or {})
    stage_144 = _rows_metrics(replay_details)
    cumulative_142_143_144 = dict(replay_summary.get("cumulative_142_143_144") or {})

    time_separation = dict(replay_summary.get("time_separation") or {})
    replay_vs_143 = dict(replay_summary.get("vs_stage_143_cumulative") or {})

    protocol_valid = bool(time_separation.get("protocol_valid"))
    hard_regression = bool(
        stage_144.get("any_regression_to_blocked")
        or stage_144.get("any_regression_to_single_class")
        or stage_144.get("gate_pass_rate", 0.0) < 1.0
        or stage_144.get("dual_class_restoration_rate", 0.0) < 1.0
        or stage_144.get("consistency_restored_rate", 0.0) < 1.0
        or _parseability_hard_regression(stage_144)
        or not protocol_valid
    )

    mild_uncertainty = bool(replay_vs_143.get("parser_or_normalization_drift_detected"))

    if hard_regression:
        replay_verdict = "Replay not confirmed"
        verdict_confidence = "high"
        single_next_step = "回到 execution-level stability 审视，暂停进入新阶段"
        evidence = [
            "Stage-144 出现硬回退信号，或时间分离协议不成立。",
            "当前 stable enough baseline 的跨时间复现性未被确认。",
        ]
    elif mild_uncertainty:
        replay_verdict = "Replay partially confirmed"
        verdict_confidence = "medium"
        single_next_step = "继续留在 replay / 稳定性确认线"
        evidence = [
            "Stage-144 核心恢复维持，但存在轻微跨时间不确定性。",
            "需要继续小步 replay 以提升跨时间可信度。",
        ]
    else:
        replay_verdict = "Replay confirmed"
        verdict_confidence = "high"
        single_next_step = "进入仍不扩模型轴，但允许进入下一条更有研究价值的小步验证线"
        evidence = [
            "Stage-144 在时间分离条件下保持 gate PASS、dual-class restoration、consistency restored。",
            "未出现 BLOCKED 或 single-class 回退，且 parseability 维持稳定边界。",
            "142+143+144 累计证据链继续无回退，跨时间复现性成立。",
        ]

    compare = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage_140_blocked": {
            "working_baseline": blocked_summary.get("working_baseline"),
            "label_health_gate_status": blocked_summary.get("label_health_gate_status"),
            "execution_label_set": blocked_summary.get("execution_label_set"),
            "consistency_restored": blocked_summary.get("consistency_restored"),
            "label_path_still_primary_blocker": blocked_summary.get("label_path_still_primary_blocker"),
        },
        "stage_141_first_recovery": {
            "gate_status": first_recovery_summary.get("gate_status"),
            "execution_label_set": first_recovery_summary.get("execution_label_set"),
            "consistency_restored": first_recovery_summary.get("consistency_restored"),
            "parseability": first_recovery_summary.get("parseability"),
        },
        "stage_142_repeated_reruns": stage_142,
        "stage_143_extension_reruns": stage_143,
        "stage_144_time_separated_replay": stage_144,
        "time_separation": time_separation,
        "replay_vs_stage_143_cumulative": replay_vs_143,
        "cumulative_142_143_144": cumulative_142_143_144,
        "evidence_chain_evolution": {
            "from_140_to_144": (
                "140 BLOCKED -> 141 首次恢复 -> 142 初步稳定复检 -> "
                "143 扩展复检并 Stable enough -> 144 时间分离 replay 复现确认。"
            ),
            "is_stage_144_more_than_continuous_rerun": bool(protocol_valid),
            "why_stage_144_has_higher_evidence_value": (
                "Stage-144 在与 143 时间分离且独立输出链下复放同一 frozen 设置，"
                "验证稳定性跨时间保持，而非同批次连续重跑。"
            ),
            "is_current_baseline_ready_for_next_small_step": bool(replay_verdict == "Replay confirmed"),
        },
        "stage_143_final_verdict_reference": {
            "stable_enough": True,
            "source": stage_143_summary.get("summary_status"),
            "note": "Stage-144 replay verdict is only about cross-time reproducibility, not a rewrite of stage-143 verdict.",
        },
    }

    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "replay_verdict": replay_verdict,
        "verdict_confidence": verdict_confidence,
        "replay_interpretation": "cross_time_reproducibility_assessment_only",
        "single_next_step": single_next_step,
        "evidence": evidence,
    }

    recommendation = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "replay_verdict": replay_verdict,
        "recommended_next_step": single_next_step,
        "why": evidence,
    }

    report_text = _build_report(compare=compare, verdict=verdict)

    write_json(output_dir / "route_c_stable_baseline_time_separated_replay_compare.json", compare)
    (output_dir / "route_c_stable_baseline_time_separated_replay_report.md").write_text(
        report_text,
        encoding="utf-8",
    )
    write_json(
        output_dir / "route_c_stable_baseline_time_separated_replay_next_step_recommendation.json",
        recommendation,
    )
    write_json(output_dir / "route_c_stable_baseline_time_separated_replay_verdict.json", verdict)

    return {
        "summary": verdict,
        "output_paths": {
            "compare": str((output_dir / "route_c_stable_baseline_time_separated_replay_compare.json").resolve()),
            "report": str((output_dir / "route_c_stable_baseline_time_separated_replay_report.md").resolve()),
            "recommendation": str(
                (
                    output_dir
                    / "route_c_stable_baseline_time_separated_replay_next_step_recommendation.json"
                ).resolve()
            ),
            "verdict": str((output_dir / "route_c_stable_baseline_time_separated_replay_verdict.json").resolve()),
        },
    }
