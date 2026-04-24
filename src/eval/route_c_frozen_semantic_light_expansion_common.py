"""Shared helpers for route_c frozen-semantic light-expansion validation stages."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.eval.model_axis_1p5b_route_c_refined_execution import load_json, load_jsonl, write_json, write_jsonl
from src.eval.route_c_label_health_gating import build_route_c_label_health_gating
from src.fusion.benchmark_truth_leaning_label import (
    build_benchmark_truth_leaning_dataset,
    run_benchmark_truth_leaning_logistic,
)


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def _load_real_raw_rows(real_run_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(real_run_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl"))


def _load_real_health_rows(real_run_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(
        _required_file(real_run_dir / "route_c_v6_dataset_dir" / "benchmark_truth_leaning_label_health_rows.jsonl")
    )


def _load_real_fusion_rows(real_run_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(real_run_dir / "route_c_v6_real_pilot_fusion" / "fusion_dataset.jsonl"))


def _reference_by_case_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["case_id"]): row for row in rows}


def _real_row_by_sample_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["sample_id"]): row for row in rows}


def _real_row_by_prompt_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("prompt_id")): row for row in rows if str(row.get("prompt_id"))}


def _fusion_by_base_sample_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["sample_id"]): row for row in rows}


def _query_answer_key(real_row: dict[str, Any]) -> str:
    metadata = real_row.get("metadata", {})
    contract = metadata.get("contract_metadata", {})
    value = str(contract.get("query_answer_key", "")).strip().upper()
    if value == "":
        return "A"
    return value


def _apply_variant(raw_text: str, variant: str) -> str:
    if variant == "raw":
        return raw_text
    if variant == "code_fence":
        return f"```{raw_text}```"
    if variant == "code_fence_lang_tag":
        return f"```text\n{raw_text}\n```"
    if variant == "code_fence_lang_tag_spaced":
        return f"```text\n{raw_text}\n```\n"
    if variant == "code_fence_blankline":
        return f"\n```{raw_text}```"
    raise ValueError(f"Unsupported response variant: {variant}")


def _expected_for_kind(path_kind: str) -> tuple[str, str, str]:
    if path_kind == "recoverable":
        return "pass_formatted_to_parser", "recoverable_formatting_issue", "recoverable"
    if path_kind == "normal":
        return "pass_raw_to_parser", "parser_reachable", "not_needed"
    if path_kind == "nonrecoverable":
        return "degeneration_blocked", "contract_broken_response", "not_recoverable"
    raise ValueError(f"Unsupported path kind: {path_kind}")


def build_cases(
    *,
    schema_version: str,
    case_prefix: str,
    required_prompt_ids: list[str],
    window_specs: list[dict[str, Any]],
    real_raw_rows: list[dict[str, Any]],
    path_group_by_kind: dict[str, str],
    previous_reference_by_case: dict[str, dict[str, Any]],
    previous_reference_prefix: str | None,
) -> list[dict[str, Any]]:
    by_prompt = _real_row_by_prompt_id(real_raw_rows)

    missing_prompt_ids = [prompt_id for prompt_id in required_prompt_ids if prompt_id not in by_prompt]
    if missing_prompt_ids:
        raise ValueError(f"Real execution run missing required prompt anchors: {missing_prompt_ids}")

    cases: list[dict[str, Any]] = []
    for window in window_specs:
        window_id = str(window["window_id"])
        window_tag = str(window["window_tag"])
        entries = list(window["entries"])
        for position, entry in enumerate(entries, start=1):
            path_kind = str(entry["path_kind"])
            prompt_id = str(entry["anchor_prompt_id"])
            variant = str(entry["response_variant"])
            case_tail = str(entry["case_tail"])
            note = str(entry["note"])

            anchor_row = by_prompt[prompt_id]
            raw_response = _apply_variant(str(anchor_row["response_text"]), variant)
            expected_handoff, expected_category, expected_recoverability = _expected_for_kind(path_kind)

            case_id = f"{case_prefix}::{window_tag}::{path_kind}::{case_tail}"
            previous_reference_case_id: str | None = None
            previous_reference_handoff: str | None = None
            previous_reference_category: str | None = None
            if previous_reference_prefix is not None:
                candidate = case_id.replace(case_prefix, previous_reference_prefix, 1)
                if candidate in previous_reference_by_case:
                    previous_reference_case_id = candidate
                    previous_reference_handoff = str(previous_reference_by_case[candidate]["current_handoff"])
                    previous_reference_category = str(previous_reference_by_case[candidate]["current_category"])

            cases.append(
                {
                    "schema_version": schema_version,
                    "case_id": case_id,
                    "path_kind": path_kind,
                    "path_group": path_group_by_kind[path_kind],
                    "source_type": "real" if variant == "raw" else "controlled-format-variant-from-real",
                    "is_real_execution_input": variant == "raw",
                    "is_light_expansion_input": True,
                    "validation_window_id": window_id,
                    "validation_window_position": position,
                    "validation_window_tag": window_tag,
                    "real_prompt_anchor_id": prompt_id,
                    "real_execution_anchor_sample_id": str(anchor_row["sample_id"]),
                    "raw_response": raw_response,
                    "query_answer_key": _query_answer_key(anchor_row),
                    "expected_handoff": expected_handoff,
                    "expected_category": expected_category,
                    "expected_recoverability": expected_recoverability,
                    "previous_reference_case_id": previous_reference_case_id,
                    "previous_reference_handoff": previous_reference_handoff,
                    "previous_reference_category": previous_reference_category,
                    "code_fence_like": variant != "raw",
                    "case_note": note,
                }
            )

    return cases


def synthetic_sample_id(stage_token: str, index: int, case: dict[str, Any]) -> str:
    return f"{stage_token}_{index:02d}__{case['case_id'].split('::')[-1]}"


def materialize_validation_inputs(
    *,
    schema_version: str,
    stage_token: str,
    cases: list[dict[str, Any]],
    real_raw_rows: list[dict[str, Any]],
    real_fusion_rows: list[dict[str, Any]],
    execution_root_dir: Path,
) -> dict[str, Any]:
    raw_by_sample_id = _real_row_by_sample_id(real_raw_rows)
    fusion_by_base_id = _fusion_by_base_sample_id(real_fusion_rows)

    labeled_rows: list[dict[str, Any]] = []
    used_base_ids: set[str] = set()

    for index, case in enumerate(cases):
        template = raw_by_sample_id[str(case["real_execution_anchor_sample_id"])]
        metadata = dict(template.get("metadata", {}))
        contract_metadata = dict(metadata.get("contract_metadata", {}))
        base_sample_id = str(contract_metadata["base_sample_id"])
        used_base_ids.add(base_sample_id)

        contract_metadata.update(
            {
                "base_sample_id": base_sample_id,
                "contract_variant": f"{stage_token}_{index:02d}",
                "query_answer_key": str(case["query_answer_key"]),
                "label_source": f"{stage_token}_validation",
                "label_scope": "benchmark_truth_leaning_supervision_proxy",
            }
        )
        metadata["contract_metadata"] = contract_metadata
        metadata[f"{stage_token}_reference"] = {
            "case_id": case["case_id"],
            "path_group": case["path_group"],
            "path_kind": case["path_kind"],
            "source_type": case["source_type"],
            "validation_window_id": case["validation_window_id"],
            "validation_window_position": int(case["validation_window_position"]),
            "real_prompt_anchor_id": case["real_prompt_anchor_id"],
            "is_real_execution_input": bool(case["is_real_execution_input"]),
        }

        row = {
            **template,
            "sample_id": synthetic_sample_id(stage_token, index, case),
            "response_text": case["raw_response"],
            "metadata": metadata,
        }
        labeled_rows.append(row)

    fusion_rows = [fusion_by_base_id[base_id] for base_id in sorted(used_base_ids)]

    labeled_path = execution_root_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl"
    dataset_input_path = execution_root_dir / "execution_inputs" / f"{stage_token}_labeled_raw_results.jsonl"
    fusion_path = execution_root_dir / "execution_inputs" / f"{stage_token}_fusion_dataset.jsonl"
    labeled_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_input_path.parent.mkdir(parents=True, exist_ok=True)

    write_jsonl(labeled_path, labeled_rows)
    write_jsonl(dataset_input_path, labeled_rows)
    write_jsonl(fusion_path, fusion_rows)

    manifest = {
        "summary_status": "PASS",
        "schema_version": schema_version,
        "case_count": len(cases),
        "base_sample_count": len(fusion_rows),
        "validation_window_ids": sorted({str(case["validation_window_id"]) for case in cases}),
        "real_prompt_anchor_ids": sorted({str(case["real_prompt_anchor_id"]) for case in cases}),
        "group_counts": dict(Counter(case["path_group"] for case in cases)),
        "source_type_counts": dict(Counter(case["source_type"] for case in cases)),
        "real_execution_input_count": sum(1 for case in cases if bool(case["is_real_execution_input"])),
        "controlled_variant_count": sum(1 for case in cases if not bool(case["is_real_execution_input"])),
        "execution_root_dir": str(execution_root_dir.resolve()),
        "labeled_results_path": str(labeled_path.resolve()),
        "fusion_dataset_path": str(fusion_path.resolve()),
    }
    write_json(execution_root_dir / "execution_inputs" / f"{stage_token}_input_manifest.json", manifest)
    return manifest


def _path_handoff_from_health_row(row: dict[str, Any]) -> str:
    if bool(row.get("response_option_missing")):
        return "degeneration_blocked"
    source = str(row.get("selected_parser_source") or "raw")
    if source == "normalized":
        return "pass_formatted_to_parser"
    return "pass_raw_to_parser"


def _path_category_from_health_row(row: dict[str, Any]) -> str:
    if not bool(row.get("response_option_missing")):
        source = str(row.get("selected_parser_source") or "raw")
        return "recoverable_formatting_issue" if source == "normalized" else "parser_reachable"
    if bool(row.get("response_punct_only")):
        return "punctuation_collapse"
    parse_failure_category = str(row.get("parse_failure_category") or "contract_broken_response")
    if parse_failure_category == "unknown_token":
        return "contract_broken_response"
    return parse_failure_category


def evaluate_records(
    *,
    schema_version: str,
    stage_token: str,
    cases: list[dict[str, Any]],
    health_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    health_by_sample_id = {str(row["sample_id"]): row for row in health_rows}
    records: list[dict[str, Any]] = []

    for index, case in enumerate(cases):
        sample_id = synthetic_sample_id(stage_token, index, case)
        health_row = health_by_sample_id[sample_id]
        current_handoff = _path_handoff_from_health_row(health_row)
        current_category = _path_category_from_health_row(health_row)

        match_expected = current_handoff == case["expected_handoff"] and current_category == case["expected_category"]

        has_previous_reference = bool(case["previous_reference_case_id"])
        match_previous_reference = (
            current_handoff == case["previous_reference_handoff"]
            and current_category == case["previous_reference_category"]
            if has_previous_reference
            else None
        )

        selected_parser_source = str(health_row.get("selected_parser_source") or "raw")
        response_option_missing = bool(health_row.get("response_option_missing"))
        current_ground_truth_label = int(health_row.get("ground_truth_label"))

        handoff_contract_ok = (
            (current_handoff == "pass_formatted_to_parser" and selected_parser_source == "normalized" and not response_option_missing)
            or (current_handoff == "pass_raw_to_parser" and selected_parser_source == "raw" and not response_option_missing)
            or (current_handoff == "degeneration_blocked" and response_option_missing)
        )

        expected_ground_truth_label = 1 if current_handoff == "degeneration_blocked" else 0
        label_health_expected_ok = current_ground_truth_label == expected_ground_truth_label

        if case["path_kind"] == "recoverable" and current_handoff != "pass_formatted_to_parser":
            mismatch_type = "recoverable_regression"
        elif case["path_kind"] == "normal" and current_handoff != "pass_raw_to_parser":
            mismatch_type = "normal_damage"
        elif case["path_kind"] == "nonrecoverable" and current_handoff != "degeneration_blocked":
            mismatch_type = "nonrecoverable_leak"
        elif not match_expected:
            mismatch_type = "expected_behavior_drift"
        elif has_previous_reference and match_previous_reference is False:
            mismatch_type = "previous_stage_reference_drift"
        elif not handoff_contract_ok:
            mismatch_type = "handoff_contract_violation"
        elif not label_health_expected_ok:
            mismatch_type = "label_health_anomaly"
        else:
            mismatch_type = "match"

        records.append(
            {
                "schema_version": schema_version,
                **case,
                "synthetic_sample_id": sample_id,
                "current_handoff": current_handoff,
                "current_category": current_category,
                "current_selected_parser_source": selected_parser_source,
                "current_response_option_missing": response_option_missing,
                "current_parse_failure_category": health_row.get("parse_failure_category"),
                "current_ground_truth_label": current_ground_truth_label,
                "current_response_option": health_row.get("response_option"),
                "match_expected": match_expected,
                "match_previous_reference": match_previous_reference,
                "handoff_contract_ok": handoff_contract_ok,
                "label_health_expected_ok": label_health_expected_ok,
                "mismatch_type": mismatch_type,
            }
        )

    return records


def _window_summary(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_window: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_window[str(row["validation_window_id"])].append(row)

    output: list[dict[str, Any]] = []
    for window_id in sorted(by_window):
        rows = sorted(by_window[window_id], key=lambda item: int(item["validation_window_position"]))
        group_handoff: dict[str, str] = {}
        for row in rows:
            group_handoff[str(row["path_group"])] = str(row["current_handoff"])

        output.append(
            {
                "window_id": window_id,
                "case_count": len(rows),
                "window_ordered_case_ids": [str(row["case_id"]) for row in rows],
                "window_ordered_prompt_anchor_ids": [str(row["real_prompt_anchor_id"]) for row in rows],
                "group_current_handoff": group_handoff,
                "all_cases_match_expected": all(bool(row["match_expected"]) for row in rows),
                "any_window_mismatch": any(str(row["mismatch_type"]) != "match" for row in rows),
            }
        )

    return output


def _path_level_drift(records: list[dict[str, Any]]) -> dict[str, Any]:
    handoff_by_group: dict[str, set[str]] = defaultdict(set)
    parser_source_by_group: dict[str, set[str]] = defaultdict(set)
    for row in records:
        group = str(row["path_group"])
        handoff_by_group[group].add(str(row["current_handoff"]))
        parser_source_by_group[group].add(str(row["current_selected_parser_source"]))

    handoff_drift_groups = sorted([group for group, values in handoff_by_group.items() if len(values) > 1])
    parser_source_drift_groups = sorted([group for group, values in parser_source_by_group.items() if len(values) > 1])

    return {
        "path_group_handoff_sets": {group: sorted(values) for group, values in handoff_by_group.items()},
        "path_group_parser_source_sets": {group: sorted(values) for group, values in parser_source_by_group.items()},
        "path_level_drift_detected": len(handoff_drift_groups) > 0,
        "parser_source_drift_detected": len(parser_source_drift_groups) > 0,
        "path_level_drift_groups": handoff_drift_groups,
        "parser_source_drift_groups": parser_source_drift_groups,
    }


def _first_present(summary: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in summary:
            return summary[key]
    return None


def load_reference_snapshots(summary_paths: dict[str, Path]) -> dict[str, Any]:
    snapshots: dict[str, Any] = {}
    for alias, summary_path in summary_paths.items():
        summary = load_json(_required_file(summary_path))
        snapshots[alias] = {
            "summary_path": str(summary_path.resolve()),
            "recoverable_rate": _first_present(
                summary,
                [
                    "recoverable_pass_rate",
                    "recoverable_path_pass_rate",
                    "recoverable_real_execution_pass_rate",
                    "recoverable_continuous_pass_rate",
                    "recoverable_real_continuous_pass_rate",
                    "recoverable_batched_continuous_stability_recheck_pass_rate",
                    "recoverable_light_expansion_pass_rate",
                    "recoverable_real_light_expansion_pass_rate",
                    "recoverable_real_light_expansion_stability_recheck_pass_rate",
                ],
            ),
            "normal_rate": _first_present(
                summary,
                [
                    "normal_pass_rate",
                    "normal_pass_through_rate",
                    "normal_path_pass_rate",
                    "normal_real_execution_pass_rate",
                    "normal_continuous_pass_rate",
                    "normal_real_continuous_pass_rate",
                    "normal_batched_continuous_stability_recheck_pass_rate",
                    "normal_light_expansion_pass_rate",
                    "normal_real_light_expansion_pass_rate",
                    "normal_real_light_expansion_stability_recheck_pass_rate",
                ],
            ),
            "nonrecoverable_rate": _first_present(
                summary,
                [
                    "nonrecoverable_block_rate",
                    "nonrecoverable_path_block_rate",
                    "nonrecoverable_real_execution_block_rate",
                    "nonrecoverable_continuous_block_rate",
                    "nonrecoverable_real_continuous_block_rate",
                    "nonrecoverable_batched_continuous_stability_recheck_block_rate",
                    "nonrecoverable_light_expansion_block_rate",
                    "nonrecoverable_real_light_expansion_block_rate",
                    "nonrecoverable_real_light_expansion_stability_recheck_block_rate",
                ],
            ),
            "all_cases_match_expected": summary.get("all_cases_match_expected"),
            "gate_status": summary.get("gate_status"),
            "logistic_status": summary.get("logistic_status"),
        }
    return snapshots


def build_summary(
    *,
    schema_version: str,
    records: list[dict[str, Any]],
    gate_result: dict[str, Any],
    logistic_status: str,
    reference_snapshots: dict[str, Any],
) -> dict[str, Any]:
    by_group_handoff: dict[str, Counter[str]] = defaultdict(Counter)
    selected_parser_source_counts: Counter[str] = Counter()
    mismatch_counts: Counter[str] = Counter()

    for row in records:
        by_group_handoff[str(row["path_group"])][str(row["current_handoff"])] += 1
        selected_parser_source_counts[str(row["current_selected_parser_source"])] += 1
        mismatch_counts[str(row["mismatch_type"])] += 1

    recoverable_records = [r for r in records if r["path_kind"] == "recoverable"]
    normal_records = [r for r in records if r["path_kind"] == "normal"]
    nonrecoverable_records = [r for r in records if r["path_kind"] == "nonrecoverable"]
    code_fence_records = [r for r in recoverable_records if bool(r["code_fence_like"])]
    previous_reference_records = [r for r in records if bool(r["previous_reference_case_id"])]

    window_summary = _window_summary(records)
    drift = _path_level_drift(records)

    handoff_contract_violation_count = sum(1 for r in records if not bool(r["handoff_contract_ok"]))
    label_health_anomaly_count = sum(1 for r in records if not bool(r["label_health_expected_ok"]))

    focused_validation_answers = {
        "recoverable_boundary_stable": int(mismatch_counts.get("recoverable_regression", 0)) == 0,
        "code_fence_like_recoverable_handoff_stable": int(mismatch_counts.get("recoverable_regression", 0)) == 0
        and all(r["current_handoff"] == "pass_formatted_to_parser" for r in code_fence_records),
        "normal_cases_all_pass": int(mismatch_counts.get("normal_damage", 0)) == 0,
        "nonrecoverable_cases_all_blocked": int(mismatch_counts.get("nonrecoverable_leak", 0)) == 0,
        "parser_gate_health_consistent": int(mismatch_counts.get("previous_stage_reference_drift", 0)) == 0
        and gate_result.get("gate_status") == "PASS"
        and logistic_status == "PASS"
        and handoff_contract_violation_count == 0
        and label_health_anomaly_count == 0,
        "impact_scope_limited_to_recoverable_boundary": int(mismatch_counts.get("normal_damage", 0)) == 0
        and int(mismatch_counts.get("nonrecoverable_leak", 0)) == 0,
    }

    return {
        "summary_status": "PASS",
        "schema_version": schema_version,
        "total_case_count": len(records),
        "validation_window_count": len(window_summary),
        "validation_window_summary": window_summary,
        "group_vs_current_handoff": {group: dict(counter) for group, counter in by_group_handoff.items()},
        "selected_parser_source_counts": dict(selected_parser_source_counts),
        "mismatch_type_counts": dict(mismatch_counts),
        "recoverable_regression_count": int(mismatch_counts.get("recoverable_regression", 0)),
        "normal_damage_count": int(mismatch_counts.get("normal_damage", 0)),
        "nonrecoverable_leak_count": int(mismatch_counts.get("nonrecoverable_leak", 0)),
        "expected_behavior_drift_count": int(mismatch_counts.get("expected_behavior_drift", 0)),
        "previous_stage_reference_drift_count": int(mismatch_counts.get("previous_stage_reference_drift", 0)),
        "handoff_contract_violation_count": handoff_contract_violation_count,
        "label_health_anomaly_count": label_health_anomaly_count,
        "recoverable_pass_rate": (
            sum(1 for r in recoverable_records if r["current_handoff"] == "pass_formatted_to_parser") / len(recoverable_records)
            if recoverable_records
            else None
        ),
        "code_fence_recoverable_pass_rate": (
            sum(1 for r in code_fence_records if r["current_handoff"] == "pass_formatted_to_parser") / len(code_fence_records)
            if code_fence_records
            else None
        ),
        "normal_pass_rate": (
            sum(1 for r in normal_records if r["current_handoff"] == "pass_raw_to_parser") / len(normal_records)
            if normal_records
            else None
        ),
        "nonrecoverable_block_rate": (
            sum(1 for r in nonrecoverable_records if r["current_handoff"] == "degeneration_blocked")
            / len(nonrecoverable_records)
            if nonrecoverable_records
            else None
        ),
        "all_cases_match_expected": all(bool(r["match_expected"]) for r in records),
        "previous_reference_anchored_case_count": len(previous_reference_records),
        "previous_reference_anchored_cases_match": all(
            bool(r["match_previous_reference"]) for r in previous_reference_records
        ),
        "path_level_drift": drift,
        "gate_status": gate_result.get("gate_status"),
        "gate_blocked_reason": gate_result.get("blocked_reason"),
        "logistic_status": logistic_status,
        "focused_validation_answers": focused_validation_answers,
        "minimal_collateral_light_expansion_analysis": {
            "new_false_block_count": int(mismatch_counts.get("normal_damage", 0)),
            "new_leak_count": int(mismatch_counts.get("nonrecoverable_leak", 0)),
            "regression_correct_but_unstable": bool(
                int(mismatch_counts.get("previous_stage_reference_drift", 0)) > 0
                or int(mismatch_counts.get("expected_behavior_drift", 0)) > 0
                or drift["path_level_drift_detected"]
                or drift["parser_source_drift_detected"]
                or handoff_contract_violation_count > 0
                or label_health_anomaly_count > 0
            ),
            "any_mismatch_detected": any(int(count) > 0 for key, count in mismatch_counts.items() if key != "match"),
        },
        "frozen_reference_snapshots": reference_snapshots,
    }


def build_report(*, report_title: str, summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append(f"# {report_title}")
    lines.append("")
    lines.append("## Validation Summary")
    lines.append(f"- recoverable_pass_rate: {summary['recoverable_pass_rate']}")
    lines.append(f"- code_fence_recoverable_pass_rate: {summary['code_fence_recoverable_pass_rate']}")
    lines.append(f"- normal_pass_rate: {summary['normal_pass_rate']}")
    lines.append(f"- nonrecoverable_block_rate: {summary['nonrecoverable_block_rate']}")
    lines.append(f"- gate_status: {summary['gate_status']}")
    lines.append(f"- logistic_status: {summary['logistic_status']}")
    lines.append(f"- all_cases_match_expected: {summary['all_cases_match_expected']}")
    lines.append(f"- previous_reference_anchored_cases_match: {summary['previous_reference_anchored_cases_match']}")
    lines.append("")
    lines.append("## Window Consistency")
    for window in summary["validation_window_summary"]:
        lines.append(
            "- "
            + f"{window['window_id']}: all_cases_match_expected={window['all_cases_match_expected']}, "
            + f"any_window_mismatch={window['any_window_mismatch']}, group_current_handoff={window['group_current_handoff']}"
        )
    lines.append(f"- path_level_drift_detected: {summary['path_level_drift']['path_level_drift_detected']}")
    lines.append(f"- parser_source_drift_detected: {summary['path_level_drift']['parser_source_drift_detected']}")
    lines.append(f"- handoff_contract_violation_count: {summary['handoff_contract_violation_count']}")
    lines.append(f"- label_health_anomaly_count: {summary['label_health_anomaly_count']}")
    lines.append("")
    lines.append("## Focused Validation Answers")
    answers = summary["focused_validation_answers"]
    lines.append(f"- recoverable boundary stable: {answers['recoverable_boundary_stable']}")
    lines.append(
        "- code-fence-like recoverable handoff stable: "
        + str(answers["code_fence_like_recoverable_handoff_stable"])
    )
    lines.append(f"- normal cases all pass: {answers['normal_cases_all_pass']}")
    lines.append(f"- nonrecoverable cases all blocked: {answers['nonrecoverable_cases_all_blocked']}")
    lines.append(f"- parser/gate/health consistency kept: {answers['parser_gate_health_consistent']}")
    lines.append(
        "- impact scope remains local to recoverable boundary: "
        + str(answers["impact_scope_limited_to_recoverable_boundary"])
    )
    lines.append("")
    lines.append("## Minimal Collateral Analysis")
    collateral = summary["minimal_collateral_light_expansion_analysis"]
    lines.append(f"- new_false_block_count: {collateral['new_false_block_count']}")
    lines.append(f"- new_leak_count: {collateral['new_leak_count']}")
    lines.append(f"- regression_correct_but_unstable: {collateral['regression_correct_but_unstable']}")
    lines.append(f"- any_mismatch_detected: {collateral['any_mismatch_detected']}")
    lines.append("")
    lines.append("## Case-Level Evidence")
    for row in records:
        lines.append(
            "- "
            + f"{row['case_id']} ({row['validation_window_id']}#{row['validation_window_position']} / {row['real_prompt_anchor_id']}): "
            + f"expected {row['expected_handoff']} / {row['expected_category']} -> "
            + f"current {row['current_handoff']} / {row['current_category']} ({row['mismatch_type']})"
        )
    lines.append("")
    lines.append("## Before/After Frozen Reference")
    for alias, snapshot in summary["frozen_reference_snapshots"].items():
        lines.append(
            "- "
            + f"{alias}: recoverable={snapshot['recoverable_rate']}, normal={snapshot['normal_rate']}, "
            + f"nonrecoverable={snapshot['nonrecoverable_rate']}, all_cases_match_expected={snapshot['all_cases_match_expected']}, "
            + f"gate_status={snapshot['gate_status']}, logistic_status={snapshot['logistic_status']}"
        )
    return "\n".join(lines) + "\n"


def run_light_expansion_stage(
    *,
    schema_version: str,
    file_prefix: str,
    suite_name: str,
    report_title: str,
    stage_token: str,
    case_prefix: str,
    required_prompt_ids: list[str],
    window_specs: list[dict[str, Any]],
    path_group_by_kind: dict[str, str],
    rules_payload: dict[str, Any],
    real_run_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
    previous_reference_details_path: Path | None,
    previous_reference_prefix: str | None,
    reference_summary_paths: dict[str, Path],
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    previous_reference_by_case: dict[str, dict[str, Any]] = {}
    if previous_reference_details_path is not None:
        previous_reference_by_case = _reference_by_case_id(load_jsonl(_required_file(previous_reference_details_path)))

    real_raw_rows = _load_real_raw_rows(real_run_dir)
    real_health_rows = _load_real_health_rows(real_run_dir)
    real_fusion_rows = _load_real_fusion_rows(real_run_dir)

    cases = build_cases(
        schema_version=schema_version,
        case_prefix=case_prefix,
        required_prompt_ids=required_prompt_ids,
        window_specs=window_specs,
        real_raw_rows=real_raw_rows,
        path_group_by_kind=path_group_by_kind,
        previous_reference_by_case=previous_reference_by_case,
        previous_reference_prefix=previous_reference_prefix,
    )

    suite = {
        "summary_status": "PASS",
        "schema_version": schema_version,
        "suite_name": suite_name,
        "case_count": len(cases),
        "validation_window_ids": sorted({str(case["validation_window_id"]) for case in cases}),
        "real_prompt_anchor_ids": sorted({str(case["real_prompt_anchor_id"]) for case in cases}),
        "group_counts": dict(Counter(case["path_group"] for case in cases)),
        "source_type_counts": dict(Counter(case["source_type"] for case in cases)),
        "real_execution_input_count": sum(1 for case in cases if bool(case["is_real_execution_input"])),
        "controlled_variant_count": sum(1 for case in cases if not bool(case["is_real_execution_input"])),
        "cases": cases,
    }

    rules = {
        "summary_status": "PASS",
        "schema_version": schema_version,
        **rules_payload,
    }

    execution_root_dir = output_dir / f"{stage_token}_root"
    input_manifest = materialize_validation_inputs(
        schema_version=schema_version,
        stage_token=stage_token,
        cases=cases,
        real_raw_rows=real_raw_rows,
        real_fusion_rows=real_fusion_rows,
        execution_root_dir=execution_root_dir,
    )

    dataset_dir = execution_root_dir / "route_c_v6_dataset_dir"
    dataset_result = build_benchmark_truth_leaning_dataset(
        expanded_real_pilot_fusion_dataset_path=execution_root_dir / "execution_inputs" / f"{stage_token}_fusion_dataset.jsonl",
        labeled_illumination_raw_results_path=execution_root_dir / "execution_inputs" / f"{stage_token}_labeled_raw_results.jsonl",
        output_dir=dataset_dir,
        fusion_profile=file_prefix,
        run_id=file_prefix,
        option_parse_mode="robust_prefix",
        option_normalization_mode="conservative",
        emit_parser_instrumentation=True,
    )

    gate_dir = output_dir / "route_c_label_health_gate"
    gate_result = build_route_c_label_health_gating(
        execution_root_dir=execution_root_dir,
        route_c_run_subdir=".",
        output_dir=gate_dir,
    )

    logistic_status = "SKIPPED"
    logistic_output_paths: dict[str, str] = {}
    if gate_result["summary"].get("gate_status") == "PASS":
        logistic_dir = output_dir / "route_c_logistic_continuation"
        logistic_result = run_benchmark_truth_leaning_logistic(
            dataset_path=dataset_dir / "benchmark_truth_leaning_dataset.jsonl",
            output_dir=logistic_dir,
            fusion_profile=file_prefix,
            run_id=file_prefix,
            label_threshold=label_threshold,
            random_seed=seed,
        )
        logistic_status = "PASS"
        logistic_output_paths = logistic_result["output_paths"]
    else:
        logistic_status = "BLOCKED_BY_GATE"

    health_rows = load_jsonl(dataset_dir / "benchmark_truth_leaning_label_health_rows.jsonl")
    records = evaluate_records(
        schema_version=schema_version,
        stage_token=stage_token,
        cases=cases,
        health_rows=health_rows,
    )

    reference_snapshots = load_reference_snapshots(reference_summary_paths)
    summary = build_summary(
        schema_version=schema_version,
        records=records,
        gate_result=gate_result["summary"],
        logistic_status=logistic_status,
        reference_snapshots=reference_snapshots,
    )
    report = build_report(report_title=report_title, summary=summary, records=records)

    write_json(output_dir / f"{file_prefix}_suite.json", suite)
    write_json(output_dir / f"{file_prefix}_rules.json", rules)
    write_json(output_dir / f"{file_prefix}_summary.json", summary)
    write_jsonl(output_dir / f"{file_prefix}_details.jsonl", records)
    (output_dir / f"{file_prefix}_report.md").write_text(report, encoding="utf-8")

    write_json(
        output_dir / "config_snapshot.json",
        {
            "summary_status": "PASS",
            "schema_version": schema_version,
            "real_run_dir": str(real_run_dir.resolve()),
            "seed": seed,
            "label_threshold": label_threshold,
            "previous_reference_details_path": (
                str(previous_reference_details_path.resolve()) if previous_reference_details_path is not None else None
            ),
            "reference_summary_paths": {k: str(v.resolve()) for k, v in reference_summary_paths.items()},
            "input_manifest_path": str((execution_root_dir / "execution_inputs" / f"{stage_token}_input_manifest.json").resolve()),
            "real_health_row_count_reference": len(real_health_rows),
        },
    )

    return {
        "suite": suite,
        "rules": rules,
        "summary": summary,
        "output_paths": {
            "suite": str((output_dir / f"{file_prefix}_suite.json").resolve()),
            "rules": str((output_dir / f"{file_prefix}_rules.json").resolve()),
            "summary": str((output_dir / f"{file_prefix}_summary.json").resolve()),
            "details": str((output_dir / f"{file_prefix}_details.jsonl").resolve()),
            "report": str((output_dir / f"{file_prefix}_report.md").resolve()),
            "execution_input_manifest": str((execution_root_dir / "execution_inputs" / f"{stage_token}_input_manifest.json").resolve()),
            "dataset_summary": dataset_result["output_paths"]["summary"],
            "label_health_summary": dataset_result["output_paths"]["label_health_summary"],
            "gate_result": gate_result["output_paths"]["gate_result"],
            "logistic_summary": logistic_output_paths.get("summary"),
            "real_run_dir": str(real_run_dir.resolve()),
            "input_manifest_summary_status": input_manifest["summary_status"],
        },
    }


def run_light_expansion_post_analysis(
    *,
    schema_version: str,
    file_prefix: str,
    summary_path: Path,
    output_dir: Path,
    validated_label: str,
    partial_label: str,
    not_validated_label: str,
    recommendation_if_validated: str,
    recommendation_if_partial: str,
    recommendation_if_not_validated: str,
    single_verdict_policy: str,
    do_not_do_yet: list[str],
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = load_json(_required_file(summary_path))

    no_recoverable_regression = int(summary["recoverable_regression_count"]) == 0
    no_normal_damage = int(summary["normal_damage_count"]) == 0
    no_nonrecoverable_leak = int(summary["nonrecoverable_leak_count"]) == 0
    no_expected_drift = int(summary["expected_behavior_drift_count"]) == 0
    no_previous_ref_drift = int(summary["previous_stage_reference_drift_count"]) == 0
    no_handoff_contract_violation = int(summary["handoff_contract_violation_count"]) == 0
    no_label_health_anomaly = int(summary["label_health_anomaly_count"]) == 0
    no_path_level_drift = not bool(summary["path_level_drift"]["path_level_drift_detected"])
    no_parser_source_drift = not bool(summary["path_level_drift"]["parser_source_drift_detected"])
    gate_pass = str(summary.get("gate_status")) == "PASS"
    logistic_pass = str(summary.get("logistic_status")) == "PASS"

    if (
        no_recoverable_regression
        and no_normal_damage
        and no_nonrecoverable_leak
        and no_expected_drift
        and no_previous_ref_drift
        and no_handoff_contract_violation
        and no_label_health_anomaly
        and no_path_level_drift
        and no_parser_source_drift
        and gate_pass
        and logistic_pass
    ):
        final_verdict = validated_label
        recommendation = recommendation_if_validated
        why = [
            "Recoverable formatting boundary remains stable in the current light-expansion chain.",
            "Normal and nonrecoverable guardrails remain intact with zero new false blocks and zero leaks.",
            "No parser/gate/health/handoff drift is observed and logistic continuation remains PASS.",
        ]
    elif no_normal_damage and no_nonrecoverable_leak:
        final_verdict = partial_label
        recommendation = recommendation_if_partial
        why = [
            "Guardrail paths remain preserved, but recoverable boundary consistency or chain stability still has drift.",
        ]
    else:
        final_verdict = not_validated_label
        recommendation = recommendation_if_not_validated
        why = [
            "Validation reveals guardrail damage, leakage, or chain-level consistency failure.",
        ]

    collateral = summary["minimal_collateral_light_expansion_analysis"]
    analysis_summary = {
        "summary_status": "PASS",
        "schema_version": schema_version,
        "recoverable_regression_count": summary["recoverable_regression_count"],
        "normal_damage_count": summary["normal_damage_count"],
        "nonrecoverable_leak_count": summary["nonrecoverable_leak_count"],
        "expected_behavior_drift_count": summary["expected_behavior_drift_count"],
        "previous_stage_reference_drift_count": summary["previous_stage_reference_drift_count"],
        "handoff_contract_violation_count": summary["handoff_contract_violation_count"],
        "label_health_anomaly_count": summary["label_health_anomaly_count"],
        "path_level_drift_detected": summary["path_level_drift"]["path_level_drift_detected"],
        "parser_source_drift_detected": summary["path_level_drift"]["parser_source_drift_detected"],
        "gate_status": summary["gate_status"],
        "logistic_status": summary["logistic_status"],
        "collateral_findings": {
            "new_false_block_count": collateral["new_false_block_count"],
            "new_leak_count": collateral["new_leak_count"],
            "regression_correct_but_unstable": collateral["regression_correct_but_unstable"],
            "any_mismatch_detected": collateral["any_mismatch_detected"],
        },
        "final_verdict": final_verdict,
    }

    verdict = {
        "summary_status": "PASS",
        "schema_version": schema_version,
        "final_verdict": final_verdict,
        "single_verdict_policy": single_verdict_policy,
        "primary_basis": why,
    }

    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": schema_version,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
        "why": why,
        "do_not_do_yet": do_not_do_yet,
        "summary_path": str(summary_path.resolve()),
    }

    write_json(output_dir / f"{file_prefix}_analysis_summary.json", analysis_summary)
    write_json(output_dir / f"{file_prefix}_verdict.json", verdict)
    write_json(output_dir / f"{file_prefix}_next_step_recommendation.json", recommendation_payload)

    return {
        "analysis_summary": analysis_summary,
        "verdict": verdict,
        "recommendation": recommendation_payload,
        "output_paths": {
            "summary": str((output_dir / f"{file_prefix}_analysis_summary.json").resolve()),
            "verdict": str((output_dir / f"{file_prefix}_verdict.json").resolve()),
            "recommendation": str((output_dir / f"{file_prefix}_next_step_recommendation.json").resolve()),
        },
    }
