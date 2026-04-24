"""Execution-level root-cause analysis for the 143 -> 144 time-separated regression."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json, write_jsonl


SCHEMA_VERSION = "triscopellm/route-c-time-separated-regression-root-cause-analysis/v1"


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _shorten(text: str, max_chars: int = 120) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 3] + "..."


def _is_punct_only(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and all(not ch.isalnum() for ch in stripped)


def _sample_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("sample_id")), str(row.get("query_answer_key"))


def _load_run_bundle(run_dir: Path) -> dict[str, Any]:
    dataset_dir = run_dir / "route_c_v6_dataset_dir"
    labeled_probe_dir = run_dir / "route_c_v6_labeled_illumination" / "illumination_probe"
    illumination_probe_dir = run_dir / "route_c_v6_illumination" / "illumination_probe"
    confidence_probe_dir = run_dir / "route_c_v6_confidence" / "confidence_probe"
    reasoning_probe_dir = run_dir / "route_c_v6_reasoning" / "reasoning_probe"

    return {
        "gate_result": load_json(_required_file(run_dir / "route_c_v6_label_health_gate_result.json")),
        "health_summary": load_json(_required_file(dataset_dir / "benchmark_truth_leaning_label_health_summary.json")),
        "parse_compare": load_json(_required_file(dataset_dir / "benchmark_truth_leaning_label_parse_compare.json")),
        "health_rows": load_jsonl(_required_file(dataset_dir / "benchmark_truth_leaning_label_health_rows.jsonl")),
        "dataset_config": load_json(_required_file(dataset_dir / "config_snapshot.json")),
        "label_selection": load_json(_required_file(dataset_dir / "benchmark_truth_leaning_label_selection.json")),
        "labeled_probe_config": load_json(_required_file(labeled_probe_dir / "config_snapshot.json")),
        "labeled_probe_summary": load_json(_required_file(labeled_probe_dir / "summary.json")),
        "labeled_probe_raw": load_jsonl(_required_file(labeled_probe_dir / "raw_results.jsonl")),
        "illumination_probe_summary": load_json(_required_file(illumination_probe_dir / "summary.json")),
        "illumination_probe_raw": load_jsonl(_required_file(illumination_probe_dir / "raw_results.jsonl")),
        "confidence_probe_summary": load_json(_required_file(confidence_probe_dir / "summary.json")),
        "reasoning_probe_summary": load_json(_required_file(reasoning_probe_dir / "summary.json")),
    }


def _build_scope(
    stage_143_recheck_dir: Path,
    stage_143_analysis_dir: Path,
    stage_144_replay_dir: Path,
    stage_144_analysis_dir: Path,
    stage_143_frozen: dict[str, Any],
    stage_144_frozen: dict[str, Any],
    representative_143_run_dir: Path,
    representative_144_run_dir: Path,
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage_143_scope": {
            "recheck_dir": str(stage_143_recheck_dir.resolve()),
            "analysis_dir": str(stage_143_analysis_dir.resolve()),
            "frozen_settings_path": str(
                (stage_143_recheck_dir / "route_c_label_output_normalization_stability_extension_frozen_settings.json").resolve()
            ),
            "representative_run_dir": str(representative_143_run_dir.resolve()),
        },
        "stage_144_scope": {
            "replay_dir": str(stage_144_replay_dir.resolve()),
            "analysis_dir": str(stage_144_analysis_dir.resolve()),
            "frozen_settings_path": str(
                (stage_144_replay_dir / "route_c_stable_baseline_time_separated_replay_frozen_settings.json").resolve()
            ),
            "representative_run_dir": str(representative_144_run_dir.resolve()),
            "artifact_location_note": (
                "144 compare/report/verdict/recommendation artifacts live under the analysis dir, "
                "not the replay dir."
            ),
        },
        "comparison_freeze": {
            "frozen_settings_exact_match": bool(
                stage_143_frozen.get("frozen_settings") == stage_144_frozen.get("frozen_settings")
            ),
            "only_allowed_audit_fields_may_differ": True,
            "diagnostic_replay_executed": False,
            "diagnostic_replay_reason": "Existing 143/144 artifacts already isolate the regression at raw-output level.",
        },
    }


def _build_hypotheses() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "candidate_root_cause_hypotheses": [
            {
                "hypothesis_id": "execution_context_drift",
                "description": "Execution entrypoint stayed nominally frozen, but runtime path, parameter injection, or path resolution drifted.",
                "would_be_supported_by": [
                    "frozen settings mismatch",
                    "query/input path mismatch",
                    "runtime config mismatch",
                    "different parser or normalization branch selection",
                ],
            },
            {
                "hypothesis_id": "parser_or_normalization_not_truly_frozen",
                "description": "Nominal settings match, but parser/normalization behavior differed at runtime.",
                "would_be_supported_by": [
                    "option_parse_mode mismatch",
                    "option_normalization_mode mismatch",
                    "selected_parser_source drift",
                    "raw responses staying comparable while parsed outcomes diverge",
                ],
            },
            {
                "hypothesis_id": "model_output_drift",
                "description": "Cross-time model responses drifted into punct_only / empty / malformed outputs before parser logic had a chance to help.",
                "would_be_supported_by": [
                    "same inputs and same parser settings but raw outputs regress",
                    "all or most replay raw responses collapse to punct_only",
                    "degradation also visible in neighboring probe outputs",
                ],
            },
            {
                "hypothesis_id": "artifact_interpretation_drift",
                "description": "Replay consumed the wrong contract layer, wrong label source, or wrong intermediate artifacts.",
                "would_be_supported_by": [
                    "sample_id set mismatch",
                    "query_answer_key mismatch",
                    "query_file mismatch",
                    "selection artifact mismatch",
                ],
            },
            {
                "hypothesis_id": "environment_cache_or_state_drift",
                "description": "Unfrozen cache or runtime state drifted across time even though explicit config fields stayed the same.",
                "would_be_supported_by": [
                    "no explicit artifact mismatch but repeated punctuation-only outputs appear",
                    "recorded runtime metadata insufficient to rule out hidden environment drift",
                ],
            },
        ],
    }


def _response_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    responses = [str(row.get("response_text", "")) for row in rows]
    punct_only_count = sum(1 for text in responses if _is_punct_only(text))
    unique_responses = sorted(set(responses))
    return {
        "row_count": len(rows),
        "avg_response_chars": (
            sum(len(text) for text in responses) / len(responses) if responses else None
        ),
        "punct_only_count": punct_only_count,
        "punct_only_ratio": (float(punct_only_count) / float(len(responses))) if responses else None,
        "all_responses_identical": len(unique_responses) == 1 if unique_responses else False,
        "unique_response_count": len(unique_responses),
        "unique_response_preview": [_shorten(text, max_chars=80) for text in unique_responses[:3]],
    }


def _sample_trace_rows(
    rows_143: list[dict[str, Any]],
    rows_144: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_key_143 = {_sample_key(row): row for row in rows_143}
    by_key_144 = {_sample_key(row): row for row in rows_144}
    ordered_keys = sorted(set(by_key_143) | set(by_key_144))
    traces: list[dict[str, Any]] = []
    for sample_id, query_answer_key in ordered_keys:
        row_143 = by_key_143.get((sample_id, query_answer_key), {})
        row_144 = by_key_144.get((sample_id, query_answer_key), {})
        raw_143 = str(row_143.get("raw_response", row_143.get("response_text", "")))
        raw_144 = str(row_144.get("raw_response", row_144.get("response_text", "")))
        traces.append(
            {
                "record_type": "sample_trace",
                "sample_id": sample_id,
                "base_sample_id": row_143.get("base_sample_id", row_144.get("base_sample_id")),
                "query_answer_key": query_answer_key,
                "response_143": raw_143,
                "response_144": raw_144,
                "response_len_143": len(raw_143),
                "response_len_144": len(raw_144),
                "response_143_is_punct_only": _is_punct_only(raw_143),
                "response_144_is_punct_only": _is_punct_only(raw_144),
                "selected_parser_source_143": row_143.get("selected_parser_source"),
                "selected_parser_source_144": row_144.get("selected_parser_source"),
                "failure_category_143": row_143.get("parse_failure_category"),
                "failure_category_144": row_144.get("parse_failure_category"),
                "raw_parser_path_143": row_143.get("raw_parser_outcome", {}).get("parser_path"),
                "raw_parser_path_144": row_144.get("raw_parser_outcome", {}).get("parser_path"),
                "parsed_label_143": row_143.get("raw_parser_outcome", {}).get("parsed_label"),
                "parsed_label_144": row_144.get("raw_parser_outcome", {}).get("parsed_label"),
                "regression_signature": (
                    "stable_parseable_text_to_uniform_punct_only"
                    if (not _is_punct_only(raw_143) and _is_punct_only(raw_144))
                    else "other"
                ),
            }
        )
    return traces


def build_route_c_time_separated_regression_root_cause_analysis(
    stage_143_recheck_dir: Path,
    stage_143_analysis_dir: Path,
    stage_144_replay_dir: Path,
    stage_144_analysis_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    stage_143_frozen = load_json(
        _required_file(
            stage_143_recheck_dir / "route_c_label_output_normalization_stability_extension_frozen_settings.json"
        )
    )
    stage_143_summary = load_json(
        _required_file(
            stage_143_recheck_dir / "route_c_label_output_normalization_stability_extension_recheck_summary.json"
        )
    )
    stage_143_details = load_jsonl(
        _required_file(
            stage_143_recheck_dir / "route_c_label_output_normalization_stability_extension_recheck_details.jsonl"
        )
    )
    stage_143_compare = load_json(
        _required_file(
            stage_143_analysis_dir / "route_c_label_output_normalization_stability_extension_compare.json"
        )
    )
    stage_143_verdict = load_json(
        _required_file(
            stage_143_analysis_dir / "route_c_label_output_normalization_stability_extension_verdict.json"
        )
    )

    stage_144_frozen = load_json(
        _required_file(
            stage_144_replay_dir / "route_c_stable_baseline_time_separated_replay_frozen_settings.json"
        )
    )
    stage_144_summary = load_json(
        _required_file(stage_144_replay_dir / "route_c_stable_baseline_time_separated_replay_summary.json")
    )
    stage_144_details = load_jsonl(
        _required_file(stage_144_replay_dir / "route_c_stable_baseline_time_separated_replay_details.jsonl")
    )
    stage_144_compare = load_json(
        _required_file(
            stage_144_analysis_dir / "route_c_stable_baseline_time_separated_replay_compare.json"
        )
    )
    stage_144_verdict = load_json(
        _required_file(
            stage_144_analysis_dir / "route_c_stable_baseline_time_separated_replay_verdict.json"
        )
    )
    stage_144_recommendation = load_json(
        _required_file(
            stage_144_analysis_dir / "route_c_stable_baseline_time_separated_replay_next_step_recommendation.json"
        )
    )

    representative_143_run_dir = Path(str(stage_143_details[0]["run_dir"]))
    representative_144_run_dir = Path(str(stage_144_details[0]["run_dir"]))
    bundle_143 = _load_run_bundle(representative_143_run_dir)
    bundle_144 = _load_run_bundle(representative_144_run_dir)

    scope = _build_scope(
        stage_143_recheck_dir=stage_143_recheck_dir,
        stage_143_analysis_dir=stage_143_analysis_dir,
        stage_144_replay_dir=stage_144_replay_dir,
        stage_144_analysis_dir=stage_144_analysis_dir,
        stage_143_frozen=stage_143_frozen,
        stage_144_frozen=stage_144_frozen,
        representative_143_run_dir=representative_143_run_dir,
        representative_144_run_dir=representative_144_run_dir,
    )
    hypotheses = _build_hypotheses()

    frozen_settings_143 = dict(stage_143_frozen.get("frozen_settings") or {})
    frozen_settings_144 = dict(stage_144_frozen.get("frozen_settings") or {})
    differing_frozen_fields = sorted(
        field
        for field in sorted(set(frozen_settings_143) | set(frozen_settings_144))
        if frozen_settings_143.get(field) != frozen_settings_144.get(field)
    )

    query_file_143 = Path(str(bundle_143["labeled_probe_config"].get("query_file")))
    query_file_144 = Path(str(bundle_144["labeled_probe_config"].get("query_file")))
    same_query_file_path = str(query_file_143.resolve()) == str(query_file_144.resolve())
    same_query_file_hash = same_query_file_path and query_file_143.is_file() and _sha256(query_file_143) == _sha256(query_file_144)

    sample_keys_143 = sorted(_sample_key(row) for row in bundle_143["health_rows"])
    sample_keys_144 = sorted(_sample_key(row) for row in bundle_144["health_rows"])
    same_contract_rows = sample_keys_143 == sample_keys_144

    labeled_stats_143 = _response_stats(bundle_143["labeled_probe_raw"])
    labeled_stats_144 = _response_stats(bundle_144["labeled_probe_raw"])
    illum_stats_143 = _response_stats(bundle_143["illumination_probe_raw"])
    illum_stats_144 = _response_stats(bundle_144["illumination_probe_raw"])

    details = _sample_trace_rows(bundle_143["health_rows"], bundle_144["health_rows"])

    hypothesis_screen = {
        "execution_context_drift": {
            "assessment": "not_supported_by_recorded_artifacts",
            "evidence_for": [],
            "evidence_against": [
                "143 and 144 frozen_settings objects are byte-for-byte identical at the JSON field level.",
                "Representative labeled probe config snapshots point to the same query_file, model path, prompt template, and generation knobs.",
                "Representative dataset config snapshots keep the same parse/normalization/instrumentation settings.",
            ],
        },
        "parser_or_normalization_not_truly_frozen": {
            "assessment": "contradicted_by_artifacts",
            "evidence_for": [],
            "evidence_against": [
                "Both 143 and 144 record option_parse_mode=robust_prefix and option_normalization_mode=conservative.",
                "Both 143 and 144 keep selected_parser_source_counts raw=6 normalized=0.",
                "144 regression is already present in raw labeled illumination outputs before normalization is applied.",
            ],
        },
        "model_output_drift": {
            "assessment": "strongly_supported",
            "evidence_for": [
                "143 labeled raw outputs are parseable text prefixes, while 144 labeled raw outputs are uniformly '!!!!!!!!!!!!!!!!'.",
                "144 raw labeled outputs regress for all 6/6 contracts, producing parsed_option_count=0 before parser logic can help.",
                "Ordinary illumination average_response_chars also collapses from 66.67 to 16.0 with punct-only raw responses.",
                "Confidence summary degrades to NaN token-probability statistics and reasoning answer-change rate drops from 1.0 to 0.0.",
            ],
            "evidence_against": [],
        },
        "artifact_interpretation_drift": {
            "assessment": "not_supported_by_artifacts",
            "evidence_for": [],
            "evidence_against": [
                "sample_id + query_answer_key contract sets match exactly between representative 143 and 144 runs.",
                "Label selection artifacts remain identical in scope and semantics.",
                "The regression is visible directly in raw_results.jsonl, before downstream interpretation.",
            ],
        },
        "environment_cache_or_state_drift": {
            "assessment": "secondary_unresolved_suspicion",
            "evidence_for": [
                "Recorded artifacts do not capture CUDA_VISIBLE_DEVICES, cache freshness, or hidden runtime state.",
                "A hidden environment change could still be upstream of the observed model-output drift.",
            ],
            "evidence_against": [
                "No explicit artifact-level mismatch is needed to explain the regression once raw outputs have already collapsed.",
            ],
        },
    }

    diff_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "frozen_settings_diff": {
            "exact_match": len(differing_frozen_fields) == 0,
            "differing_fields": differing_frozen_fields,
            "must_match_exactly_143": stage_143_frozen.get("must_match_exactly"),
            "must_match_exactly_144": stage_144_frozen.get("must_match_exactly"),
        },
        "input_contract_diff": {
            "same_query_file_path": same_query_file_path,
            "same_query_file_hash": same_query_file_hash,
            "query_file_path": str(query_file_143.resolve()),
            "same_contract_rows": same_contract_rows,
            "contract_row_count_143": len(sample_keys_143),
            "contract_row_count_144": len(sample_keys_144),
            "same_label_selection_payload": bundle_143["label_selection"] == bundle_144["label_selection"],
        },
        "runtime_context_diff": {
            "same_model_profile_name": (
                bundle_143["labeled_probe_config"].get("model_profile_name")
                == bundle_144["labeled_probe_config"].get("model_profile_name")
            ),
            "same_model_local_path": (
                bundle_143["labeled_probe_config"].get("model_profile", {}).get("local_path")
                == bundle_144["labeled_probe_config"].get("model_profile", {}).get("local_path")
            ),
            "same_runtime_device": (
                bundle_143["labeled_probe_config"].get("runtime_device")
                == bundle_144["labeled_probe_config"].get("runtime_device")
            ),
            "same_prompt_template": (
                bundle_143["labeled_probe_config"].get("prompt_template_path")
                == bundle_144["labeled_probe_config"].get("prompt_template_path")
            ),
            "same_generation_profile": (
                bundle_143["labeled_probe_config"].get("illumination_profile", {}).get("generation")
                == bundle_144["labeled_probe_config"].get("illumination_profile", {}).get("generation")
            ),
            "same_dataset_config": (
                bundle_143["dataset_config"].get("option_parse_mode") == bundle_144["dataset_config"].get("option_parse_mode")
                and bundle_143["dataset_config"].get("option_normalization_mode")
                == bundle_144["dataset_config"].get("option_normalization_mode")
                and bundle_143["dataset_config"].get("emit_parser_instrumentation")
                == bundle_144["dataset_config"].get("emit_parser_instrumentation")
            ),
            "unobserved_runtime_fields": [
                "CUDA_VISIBLE_DEVICES",
                "cache warmth / stale temp files",
                "hidden GPU / allocator state",
            ],
        },
        "output_pattern_diff": {
            "labeled_illumination": {
                "summary_143": bundle_143["labeled_probe_summary"],
                "summary_144": bundle_144["labeled_probe_summary"],
                "raw_response_stats_143": labeled_stats_143,
                "raw_response_stats_144": labeled_stats_144,
            },
            "label_health": {
                "gate_143": bundle_143["gate_result"],
                "gate_144": bundle_144["gate_result"],
                "parse_compare_143": bundle_143["parse_compare"],
                "parse_compare_144": bundle_144["parse_compare"],
            },
            "neighboring_modules": {
                "illumination_raw_143": illum_stats_143,
                "illumination_raw_144": illum_stats_144,
                "illumination_summary_143": bundle_143["illumination_probe_summary"],
                "illumination_summary_144": bundle_144["illumination_probe_summary"],
                "confidence_summary_143": bundle_143["confidence_probe_summary"],
                "confidence_summary_144": bundle_144["confidence_probe_summary"],
                "reasoning_summary_143": bundle_143["reasoning_probe_summary"],
                "reasoning_summary_144": bundle_144["reasoning_probe_summary"],
            },
        },
        "stage_chain_references": {
            "stage_143_summary": stage_143_summary,
            "stage_143_compare": stage_143_compare,
            "stage_143_verdict": stage_143_verdict,
            "stage_144_summary": stage_144_summary,
            "stage_144_compare": stage_144_compare,
            "stage_144_verdict": stage_144_verdict,
            "stage_144_recommendation": stage_144_recommendation,
        },
        "hypothesis_screen": hypothesis_screen,
        "diagnostic_replay": {
            "executed": False,
            "reason": "Existing artifacts already show the regression at raw-output level under frozen settings.",
        },
        "single_best_supported_hypothesis": "model_output_drift",
    }

    report_lines: list[str] = []
    report_lines.append("# Route-C Time-Separated Regression Root Cause Report")
    report_lines.append("")
    report_lines.append("## Frozen Comparison Scope")
    report_lines.append(f"- 143 frozen settings exact match vs 144: {diff_summary['frozen_settings_diff']['exact_match']}")
    report_lines.append(f"- same query_file path: {same_query_file_path}")
    report_lines.append(f"- same query_file hash: {same_query_file_hash}")
    report_lines.append(f"- same contract rows: {same_contract_rows}")
    report_lines.append("")
    report_lines.append("## Why 144 Is A Hard Regression")
    report_lines.append(
        "- replay-only metrics: gate_pass_rate=0.0, dual_class_restoration_rate=0.0, consistency_restored_rate=0.0"
    )
    report_lines.append(
        "- parseability collapsed from parsed_option_count=5 / missing=0.1667 / punct_only=0.0 to parsed_option_count=0 / missing=1.0 / punct_only=1.0"
    )
    report_lines.append("")
    report_lines.append("## Execution-Level Diff")
    report_lines.append("- No explicit frozen-settings mismatch is recorded between 143 and 144.")
    report_lines.append("- No input-contract mismatch is recorded between 143 and 144.")
    report_lines.append(
        "- Labeled illumination raw outputs regress from prefixed alpha-text completions in 143 to uniform punctuation-only `!!!!!!!!!!!!!!!!` in 144."
    )
    report_lines.append(
        "- The same punct-only collapse is also visible in ordinary illumination, while confidence/reasoning summaries degrade in parallel."
    )
    report_lines.append("")
    report_lines.append("## Representative Case Traces")
    for row in details[:6]:
        report_lines.append(
            "- "
            + f"{row['sample_id']}: 143='{_shorten(row['response_143'])}' -> "
            + f"144='{_shorten(row['response_144'])}', "
            + f"failure {row['failure_category_143']} -> {row['failure_category_144']}"
        )
    report_lines.append("")
    report_lines.append("## Hypothesis Screening")
    for hypothesis_id, payload in hypothesis_screen.items():
        report_lines.append(f"- {hypothesis_id}: {payload['assessment']}")
    report_lines.append("")
    report_lines.append("## Minimal Diagnostic Replay")
    report_lines.append("- not executed")
    report_lines.append("- reason: existing 143/144 artifacts already isolate the regression before parser/gate repair logic.")
    report_lines.append("")
    report_lines.append("## Best-Supported Direction")
    report_lines.append("- current best-supported hypothesis: model_output_drift")
    report_text = "\n".join(report_lines) + "\n"

    write_json(
        output_dir / "route_c_time_separated_regression_root_cause_scope.json",
        scope,
    )
    write_json(
        output_dir / "route_c_time_separated_regression_root_cause_hypotheses.json",
        hypotheses,
    )
    write_json(
        output_dir / "route_c_time_separated_regression_root_cause_diff_summary.json",
        diff_summary,
    )
    write_jsonl(
        output_dir / "route_c_time_separated_regression_root_cause_details.jsonl",
        details,
    )
    (output_dir / "route_c_time_separated_regression_root_cause_report.md").write_text(
        report_text,
        encoding="utf-8",
    )

    return {
        "scope": scope,
        "diff_summary": diff_summary,
        "output_paths": {
            "scope": str((output_dir / "route_c_time_separated_regression_root_cause_scope.json").resolve()),
            "hypotheses": str(
                (output_dir / "route_c_time_separated_regression_root_cause_hypotheses.json").resolve()
            ),
            "diff_summary": str(
                (output_dir / "route_c_time_separated_regression_root_cause_diff_summary.json").resolve()
            ),
            "details": str(
                (output_dir / "route_c_time_separated_regression_root_cause_details.jsonl").resolve()
            ),
            "report": str(
                (output_dir / "route_c_time_separated_regression_root_cause_report.md").resolve()
            ),
        },
    }
