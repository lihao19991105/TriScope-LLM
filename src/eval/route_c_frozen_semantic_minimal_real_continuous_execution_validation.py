"""Minimal real-continuous execution validation for route_c frozen semantic boundary behavior."""

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


SCHEMA_VERSION = "triscopellm/route-c-frozen-semantic-minimal-real-continuous-execution-validation/v1"


def _required_file(path: Path) -> Path:
    if not path.is_file():
        raise ValueError(f"Required file not found: `{path}`")
    return path


def _load_150_details(stage_150_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(stage_150_dir / "route_c_frozen_semantic_minimal_execution_path_regression_details.jsonl"))


def _load_151_details(stage_151_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(_required_file(stage_151_dir / "route_c_frozen_semantic_minimal_real_execution_details.jsonl"))


def _load_152_details(stage_152_dir: Path) -> list[dict[str, Any]]:
    return load_jsonl(
        _required_file(stage_152_dir / "route_c_frozen_semantic_minimal_continuous_execution_details.jsonl")
    )


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


def _minimal_real_continuous_suite(
    real_raw_rows: list[dict[str, Any]],
    stage_150_reference_by_case: dict[str, dict[str, Any]],
    stage_151_reference_by_case: dict[str, dict[str, Any]],
    stage_152_reference_by_case: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    by_prompt = _real_row_by_prompt_id(real_raw_rows)
    by_sample = _real_row_by_sample_id(real_raw_rows)

    required_prompt_ids = ["illumination_0000", "illumination_0001", "illumination_0002"]
    missing_prompt_ids = [prompt_id for prompt_id in required_prompt_ids if prompt_id not in by_prompt]
    if missing_prompt_ids:
        raise ValueError(f"Real execution run missing required continuous prompt anchors: {missing_prompt_ids}")

    required_samples = ["csqa-pilot-002__control", "csqa-pilot-021__control", "csqa-pilot-021__targeted"]
    missing_samples = [sample_id for sample_id in required_samples if sample_id not in by_sample]
    if missing_samples:
        raise ValueError(f"Real execution run missing required anchor samples: {missing_samples}")

    nonrecoverable_anchor = by_prompt["illumination_0000"]
    normal_anchor_one = by_prompt["illumination_0001"]
    normal_anchor_two = by_prompt["illumination_0002"]

    recoverable_raw_one = str(normal_anchor_one["response_text"])
    recoverable_raw_two = str(normal_anchor_two["response_text"])
    nonrecoverable_raw = str(nonrecoverable_anchor["response_text"])

    cases: list[dict[str, Any]] = [
        {
            "case_id": "real_continuous_exec::rw01::recoverable::code_fence",
            "path_group": "recoverable_real_continuous_execution",
            "source_type": "controlled-format-variant-from-real",
            "is_real_execution_input": False,
            "is_real_continuous_execution_input": True,
            "real_continuous_window_id": "real_window_01",
            "real_continuous_position": 1,
            "real_prompt_anchor_id": "illumination_0001",
            "real_execution_anchor_sample_id": str(normal_anchor_one["sample_id"]),
            "raw_response": f"```{recoverable_raw_one}```",
            "query_answer_key": _query_answer_key(normal_anchor_one),
            "expected_handoff": "pass_formatted_to_parser",
            "expected_category": "recoverable_formatting_issue",
            "expected_recoverability": "recoverable",
            "stage_150_reference_case_id": "focused::controlled_recoverable::code_fence",
            "stage_150_reference_handoff": stage_150_reference_by_case["focused::controlled_recoverable::code_fence"][
                "current_path_handoff"
            ],
            "stage_150_reference_category": stage_150_reference_by_case["focused::controlled_recoverable::code_fence"][
                "current_path_category"
            ],
            "stage_151_reference_case_id": "real_exec::controlled_recoverable::code_fence",
            "stage_151_reference_handoff": stage_151_reference_by_case["real_exec::controlled_recoverable::code_fence"][
                "current_handoff"
            ],
            "stage_151_reference_category": stage_151_reference_by_case["real_exec::controlled_recoverable::code_fence"][
                "current_category"
            ],
            "stage_152_reference_case_id": "continuous_exec::w01::recoverable::code_fence",
            "stage_152_reference_handoff": stage_152_reference_by_case["continuous_exec::w01::recoverable::code_fence"][
                "current_handoff"
            ],
            "stage_152_reference_category": stage_152_reference_by_case[
                "continuous_exec::w01::recoverable::code_fence"
            ]["current_category"],
            "code_fence_like": True,
            "case_note": "recoverable code-fence wrapper derived from real continuous prompt anchor illumination_0001",
        },
        {
            "case_id": "real_continuous_exec::rw01::normal::csqa-pilot-002__control",
            "path_group": "normal_real_continuous_execution_guardrail",
            "source_type": "real",
            "is_real_execution_input": True,
            "is_real_continuous_execution_input": True,
            "real_continuous_window_id": "real_window_01",
            "real_continuous_position": 2,
            "real_prompt_anchor_id": "illumination_0001",
            "real_execution_anchor_sample_id": str(normal_anchor_one["sample_id"]),
            "raw_response": str(normal_anchor_one["response_text"]),
            "query_answer_key": _query_answer_key(normal_anchor_one),
            "expected_handoff": "pass_raw_to_parser",
            "expected_category": "parser_reachable",
            "expected_recoverability": "not_needed",
            "stage_150_reference_case_id": "focused::real_normal::csqa-pilot-002__control",
            "stage_150_reference_handoff": stage_150_reference_by_case["focused::real_normal::csqa-pilot-002__control"][
                "current_path_handoff"
            ],
            "stage_150_reference_category": stage_150_reference_by_case["focused::real_normal::csqa-pilot-002__control"][
                "current_path_category"
            ],
            "stage_151_reference_case_id": "real_exec::real_normal::csqa-pilot-002__control",
            "stage_151_reference_handoff": stage_151_reference_by_case["real_exec::real_normal::csqa-pilot-002__control"][
                "current_handoff"
            ],
            "stage_151_reference_category": stage_151_reference_by_case[
                "real_exec::real_normal::csqa-pilot-002__control"
            ]["current_category"],
            "stage_152_reference_case_id": "continuous_exec::w01::normal::csqa-pilot-002__control",
            "stage_152_reference_handoff": stage_152_reference_by_case[
                "continuous_exec::w01::normal::csqa-pilot-002__control"
            ]["current_handoff"],
            "stage_152_reference_category": stage_152_reference_by_case[
                "continuous_exec::w01::normal::csqa-pilot-002__control"
            ]["current_category"],
            "code_fence_like": False,
            "case_note": "real normal guardrail case from prompt anchor illumination_0001",
        },
        {
            "case_id": "real_continuous_exec::rw01::nonrecoverable::csqa-pilot-021__targeted",
            "path_group": "nonrecoverable_real_continuous_execution_guardrail",
            "source_type": "real",
            "is_real_execution_input": True,
            "is_real_continuous_execution_input": True,
            "real_continuous_window_id": "real_window_01",
            "real_continuous_position": 3,
            "real_prompt_anchor_id": "illumination_0000",
            "real_execution_anchor_sample_id": str(nonrecoverable_anchor["sample_id"]),
            "raw_response": nonrecoverable_raw,
            "query_answer_key": _query_answer_key(nonrecoverable_anchor),
            "expected_handoff": "degeneration_blocked",
            "expected_category": "contract_broken_response",
            "expected_recoverability": "not_recoverable",
            "stage_150_reference_case_id": None,
            "stage_150_reference_handoff": None,
            "stage_150_reference_category": None,
            "stage_151_reference_case_id": "real_exec::real_nonrecoverable::csqa-pilot-021__targeted",
            "stage_151_reference_handoff": stage_151_reference_by_case[
                "real_exec::real_nonrecoverable::csqa-pilot-021__targeted"
            ]["current_handoff"],
            "stage_151_reference_category": stage_151_reference_by_case[
                "real_exec::real_nonrecoverable::csqa-pilot-021__targeted"
            ]["current_category"],
            "stage_152_reference_case_id": "continuous_exec::w01::nonrecoverable::csqa-pilot-021__targeted",
            "stage_152_reference_handoff": stage_152_reference_by_case[
                "continuous_exec::w01::nonrecoverable::csqa-pilot-021__targeted"
            ]["current_handoff"],
            "stage_152_reference_category": stage_152_reference_by_case[
                "continuous_exec::w01::nonrecoverable::csqa-pilot-021__targeted"
            ]["current_category"],
            "code_fence_like": False,
            "case_note": "real nonrecoverable guardrail case from prompt anchor illumination_0000",
        },
        {
            "case_id": "real_continuous_exec::rw01::recoverable::code_fence_lang_tag",
            "path_group": "recoverable_real_continuous_execution",
            "source_type": "controlled-format-variant-from-real",
            "is_real_execution_input": False,
            "is_real_continuous_execution_input": True,
            "real_continuous_window_id": "real_window_01",
            "real_continuous_position": 4,
            "real_prompt_anchor_id": "illumination_0002",
            "real_execution_anchor_sample_id": str(normal_anchor_two["sample_id"]),
            "raw_response": f"```text\n{recoverable_raw_two}\n```",
            "query_answer_key": _query_answer_key(normal_anchor_two),
            "expected_handoff": "pass_formatted_to_parser",
            "expected_category": "recoverable_formatting_issue",
            "expected_recoverability": "recoverable",
            "stage_150_reference_case_id": "focused::new_recoverable::code_fence_lang_tag",
            "stage_150_reference_handoff": stage_150_reference_by_case["focused::new_recoverable::code_fence_lang_tag"][
                "current_path_handoff"
            ],
            "stage_150_reference_category": stage_150_reference_by_case["focused::new_recoverable::code_fence_lang_tag"][
                "current_path_category"
            ],
            "stage_151_reference_case_id": "real_exec::controlled_recoverable::code_fence_lang_tag",
            "stage_151_reference_handoff": stage_151_reference_by_case[
                "real_exec::controlled_recoverable::code_fence_lang_tag"
            ]["current_handoff"],
            "stage_151_reference_category": stage_151_reference_by_case[
                "real_exec::controlled_recoverable::code_fence_lang_tag"
            ]["current_category"],
            "stage_152_reference_case_id": "continuous_exec::w02::recoverable::code_fence_lang_tag",
            "stage_152_reference_handoff": stage_152_reference_by_case[
                "continuous_exec::w02::recoverable::code_fence_lang_tag"
            ]["current_handoff"],
            "stage_152_reference_category": stage_152_reference_by_case[
                "continuous_exec::w02::recoverable::code_fence_lang_tag"
            ]["current_category"],
            "code_fence_like": True,
            "case_note": "language-tag recoverable wrapper derived from real continuous prompt anchor illumination_0002",
        },
        {
            "case_id": "real_continuous_exec::rw01::normal::csqa-pilot-021__control",
            "path_group": "normal_real_continuous_execution_guardrail",
            "source_type": "real",
            "is_real_execution_input": True,
            "is_real_continuous_execution_input": True,
            "real_continuous_window_id": "real_window_01",
            "real_continuous_position": 5,
            "real_prompt_anchor_id": "illumination_0002",
            "real_execution_anchor_sample_id": str(normal_anchor_two["sample_id"]),
            "raw_response": str(normal_anchor_two["response_text"]),
            "query_answer_key": _query_answer_key(normal_anchor_two),
            "expected_handoff": "pass_raw_to_parser",
            "expected_category": "parser_reachable",
            "expected_recoverability": "not_needed",
            "stage_150_reference_case_id": "focused::real_normal::csqa-pilot-021__control",
            "stage_150_reference_handoff": stage_150_reference_by_case["focused::real_normal::csqa-pilot-021__control"][
                "current_path_handoff"
            ],
            "stage_150_reference_category": stage_150_reference_by_case["focused::real_normal::csqa-pilot-021__control"][
                "current_path_category"
            ],
            "stage_151_reference_case_id": "real_exec::real_normal::csqa-pilot-021__control",
            "stage_151_reference_handoff": stage_151_reference_by_case["real_exec::real_normal::csqa-pilot-021__control"][
                "current_handoff"
            ],
            "stage_151_reference_category": stage_151_reference_by_case[
                "real_exec::real_normal::csqa-pilot-021__control"
            ]["current_category"],
            "stage_152_reference_case_id": "continuous_exec::w02::normal::csqa-pilot-021__control",
            "stage_152_reference_handoff": stage_152_reference_by_case[
                "continuous_exec::w02::normal::csqa-pilot-021__control"
            ]["current_handoff"],
            "stage_152_reference_category": stage_152_reference_by_case[
                "continuous_exec::w02::normal::csqa-pilot-021__control"
            ]["current_category"],
            "code_fence_like": False,
            "case_note": "second real normal guardrail case from prompt anchor illumination_0002",
        },
        {
            "case_id": "real_continuous_exec::rw01::nonrecoverable::code_fence_contract_broken",
            "path_group": "nonrecoverable_real_continuous_execution_guardrail",
            "source_type": "controlled-format-variant-from-real",
            "is_real_execution_input": False,
            "is_real_continuous_execution_input": True,
            "real_continuous_window_id": "real_window_01",
            "real_continuous_position": 6,
            "real_prompt_anchor_id": "illumination_0000",
            "real_execution_anchor_sample_id": str(nonrecoverable_anchor["sample_id"]),
            "raw_response": f"```text\n{nonrecoverable_raw}\n```",
            "query_answer_key": _query_answer_key(nonrecoverable_anchor),
            "expected_handoff": "degeneration_blocked",
            "expected_category": "contract_broken_response",
            "expected_recoverability": "not_recoverable",
            "stage_150_reference_case_id": "focused::new_nonrecoverable::code_fence_contract_broken",
            "stage_150_reference_handoff": stage_150_reference_by_case[
                "focused::new_nonrecoverable::code_fence_contract_broken"
            ]["current_path_handoff"],
            "stage_150_reference_category": stage_150_reference_by_case[
                "focused::new_nonrecoverable::code_fence_contract_broken"
            ]["current_path_category"],
            "stage_151_reference_case_id": "real_exec::controlled_nonrecoverable::code_fence_contract_broken",
            "stage_151_reference_handoff": stage_151_reference_by_case[
                "real_exec::controlled_nonrecoverable::code_fence_contract_broken"
            ]["current_handoff"],
            "stage_151_reference_category": stage_151_reference_by_case[
                "real_exec::controlled_nonrecoverable::code_fence_contract_broken"
            ]["current_category"],
            "stage_152_reference_case_id": "continuous_exec::w02::nonrecoverable::code_fence_contract_broken",
            "stage_152_reference_handoff": stage_152_reference_by_case[
                "continuous_exec::w02::nonrecoverable::code_fence_contract_broken"
            ]["current_handoff"],
            "stage_152_reference_category": stage_152_reference_by_case[
                "continuous_exec::w02::nonrecoverable::code_fence_contract_broken"
            ]["current_category"],
            "code_fence_like": True,
            "case_note": "near-boundary nonrecoverable code-fence wrapper derived from real continuous prompt anchor illumination_0000",
        },
    ]
    return cases


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


def _materialize_real_continuous_execution_inputs(
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
                "contract_variant": f"real_continuous_exec_validation_{index:02d}",
                "query_answer_key": str(case["query_answer_key"]),
                "label_source": "minimal_real_continuous_execution_validation",
                "label_scope": "benchmark_truth_leaning_supervision_proxy",
            }
        )
        metadata["contract_metadata"] = contract_metadata
        metadata["real_continuous_execution_validation_reference"] = {
            "case_id": case["case_id"],
            "path_group": case["path_group"],
            "source_type": case["source_type"],
            "real_continuous_window_id": case["real_continuous_window_id"],
            "real_continuous_position": int(case["real_continuous_position"]),
            "real_prompt_anchor_id": case["real_prompt_anchor_id"],
            "is_real_execution_input": bool(case["is_real_execution_input"]),
            "is_real_continuous_execution_input": bool(case["is_real_continuous_execution_input"]),
        }

        labeled_rows.append(
            {
                **template,
                "sample_id": f"real_continuous_exec_validation_{index:02d}__{case['case_id'].split('::')[-1]}",
                "response_text": case["raw_response"],
                "metadata": metadata,
            }
        )

    fusion_rows = [fusion_by_base_id[base_id] for base_id in sorted(used_base_ids)]

    labeled_path = execution_root_dir / "route_c_v6_labeled_illumination" / "illumination_probe" / "raw_results.jsonl"
    dataset_input_path = execution_root_dir / "execution_inputs" / "minimal_real_continuous_execution_labeled_raw_results.jsonl"
    fusion_path = execution_root_dir / "execution_inputs" / "minimal_real_continuous_execution_fusion_dataset.jsonl"
    labeled_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_input_path.parent.mkdir(parents=True, exist_ok=True)

    write_jsonl(labeled_path, labeled_rows)
    write_jsonl(dataset_input_path, labeled_rows)
    write_jsonl(fusion_path, fusion_rows)

    manifest = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "case_count": len(cases),
        "base_sample_count": len(fusion_rows),
        "real_continuous_window_ids": sorted({str(case["real_continuous_window_id"]) for case in cases}),
        "real_prompt_anchor_ids": sorted({str(case["real_prompt_anchor_id"]) for case in cases}),
        "group_counts": dict(Counter(case["path_group"] for case in cases)),
        "source_type_counts": dict(Counter(case["source_type"] for case in cases)),
        "real_execution_input_count": sum(1 for case in cases if bool(case["is_real_execution_input"])),
        "controlled_variant_count": sum(1 for case in cases if not bool(case["is_real_execution_input"])),
        "execution_root_dir": str(execution_root_dir.resolve()),
        "labeled_results_path": str(labeled_path.resolve()),
        "fusion_dataset_path": str(fusion_path.resolve()),
    }
    write_json(execution_root_dir / "execution_inputs" / "real_continuous_execution_input_manifest.json", manifest)
    return manifest


def _evaluate_records(cases: list[dict[str, Any]], health_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    health_by_sample_id = {str(row["sample_id"]): row for row in health_rows}
    records: list[dict[str, Any]] = []

    for index, case in enumerate(cases):
        sample_id = f"real_continuous_exec_validation_{index:02d}__{case['case_id'].split('::')[-1]}"
        health_row = health_by_sample_id[sample_id]
        current_handoff = _path_handoff_from_health_row(health_row)
        current_category = _path_category_from_health_row(health_row)

        match_expected = current_handoff == case["expected_handoff"] and current_category == case["expected_category"]

        has_stage_150_reference = bool(case["stage_150_reference_case_id"])
        has_stage_151_reference = bool(case["stage_151_reference_case_id"])
        has_stage_152_reference = bool(case["stage_152_reference_case_id"])

        match_stage_150_reference = (
            current_handoff == case["stage_150_reference_handoff"]
            and current_category == case["stage_150_reference_category"]
            if has_stage_150_reference
            else None
        )
        match_stage_151_reference = (
            current_handoff == case["stage_151_reference_handoff"]
            and current_category == case["stage_151_reference_category"]
            if has_stage_151_reference
            else None
        )
        match_stage_152_reference = (
            current_handoff == case["stage_152_reference_handoff"]
            and current_category == case["stage_152_reference_category"]
            if has_stage_152_reference
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

        if case["path_group"] == "recoverable_real_continuous_execution" and current_handoff != "pass_formatted_to_parser":
            mismatch_type = "recoverable_real_continuous_regression"
        elif case["path_group"] == "normal_real_continuous_execution_guardrail" and current_handoff != "pass_raw_to_parser":
            mismatch_type = "normal_real_continuous_damage"
        elif (
            case["path_group"] == "nonrecoverable_real_continuous_execution_guardrail"
            and current_handoff != "degeneration_blocked"
        ):
            mismatch_type = "nonrecoverable_real_continuous_leak"
        elif not match_expected:
            mismatch_type = "expected_behavior_drift"
        elif has_stage_152_reference and match_stage_152_reference is False:
            mismatch_type = "stage152_reference_drift"
        elif has_stage_151_reference and match_stage_151_reference is False:
            mismatch_type = "stage151_reference_drift"
        elif has_stage_150_reference and match_stage_150_reference is False:
            mismatch_type = "stage150_reference_drift"
        elif not handoff_contract_ok:
            mismatch_type = "handoff_contract_violation"
        elif not label_health_expected_ok:
            mismatch_type = "label_health_anomaly"
        else:
            mismatch_type = "match"

        records.append(
            {
                "schema_version": SCHEMA_VERSION,
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
                "match_stage_150_reference": match_stage_150_reference,
                "match_stage_151_reference": match_stage_151_reference,
                "match_stage_152_reference": match_stage_152_reference,
                "handoff_contract_ok": handoff_contract_ok,
                "label_health_expected_ok": label_health_expected_ok,
                "mismatch_type": mismatch_type,
            }
        )
    return records


def _real_continuous_window_summary(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_window: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_window[str(row["real_continuous_window_id"])].append(row)

    output: list[dict[str, Any]] = []
    for window_id in sorted(by_window):
        rows = sorted(by_window[window_id], key=lambda item: int(item["real_continuous_position"]))
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


def _summary(
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

    recoverable_records = [r for r in records if r["path_group"] == "recoverable_real_continuous_execution"]
    normal_records = [r for r in records if r["path_group"] == "normal_real_continuous_execution_guardrail"]
    nonrecoverable_records = [
        r for r in records if r["path_group"] == "nonrecoverable_real_continuous_execution_guardrail"
    ]
    code_fence_records = [r for r in recoverable_records if bool(r["code_fence_like"])]

    stage_150_anchored_records = [r for r in records if bool(r["stage_150_reference_case_id"])]
    stage_151_anchored_records = [r for r in records if bool(r["stage_151_reference_case_id"])]
    stage_152_anchored_records = [r for r in records if bool(r["stage_152_reference_case_id"])]

    window_summary = _real_continuous_window_summary(records)
    drift = _path_level_drift(records)

    handoff_contract_violation_count = sum(1 for r in records if not bool(r["handoff_contract_ok"]))
    label_health_anomaly_count = sum(1 for r in records if not bool(r["label_health_expected_ok"]))

    focused_validation_answers = {
        "recoverable_boundary_stable_on_real_continuous_execution": int(
            mismatch_counts.get("recoverable_real_continuous_regression", 0)
        )
        == 0,
        "code_fence_like_recoverable_handoff_stable_on_real_continuous_execution": int(
            mismatch_counts.get("recoverable_real_continuous_regression", 0)
        )
        == 0
        and all(r["current_handoff"] == "pass_formatted_to_parser" for r in code_fence_records),
        "normal_real_continuous_execution_cases_all_pass": int(
            mismatch_counts.get("normal_real_continuous_damage", 0)
        )
        == 0,
        "nonrecoverable_real_continuous_execution_cases_all_blocked": int(
            mismatch_counts.get("nonrecoverable_real_continuous_leak", 0)
        )
        == 0,
        "parser_gate_health_consistent_with_150_151_152": int(mismatch_counts.get("stage150_reference_drift", 0)) == 0
        and int(mismatch_counts.get("stage151_reference_drift", 0)) == 0
        and int(mismatch_counts.get("stage152_reference_drift", 0)) == 0
        and gate_result.get("gate_status") == "PASS"
        and logistic_status == "PASS"
        and handoff_contract_violation_count == 0
        and label_health_anomaly_count == 0,
        "impact_scope_limited_to_recoverable_boundary": int(mismatch_counts.get("normal_real_continuous_damage", 0))
        == 0
        and int(mismatch_counts.get("nonrecoverable_real_continuous_leak", 0)) == 0,
    }

    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "total_case_count": len(records),
        "real_continuous_window_count": len(window_summary),
        "real_continuous_window_summary": window_summary,
        "group_vs_current_handoff": {group: dict(counter) for group, counter in by_group_handoff.items()},
        "selected_parser_source_counts": dict(selected_parser_source_counts),
        "mismatch_type_counts": dict(mismatch_counts),
        "recoverable_real_continuous_regression_count": int(
            mismatch_counts.get("recoverable_real_continuous_regression", 0)
        ),
        "normal_real_continuous_damage_count": int(mismatch_counts.get("normal_real_continuous_damage", 0)),
        "nonrecoverable_real_continuous_leak_count": int(
            mismatch_counts.get("nonrecoverable_real_continuous_leak", 0)
        ),
        "expected_behavior_drift_count": int(mismatch_counts.get("expected_behavior_drift", 0)),
        "stage150_reference_drift_count": int(mismatch_counts.get("stage150_reference_drift", 0)),
        "stage151_reference_drift_count": int(mismatch_counts.get("stage151_reference_drift", 0)),
        "stage152_reference_drift_count": int(mismatch_counts.get("stage152_reference_drift", 0)),
        "handoff_contract_violation_count": handoff_contract_violation_count,
        "label_health_anomaly_count": label_health_anomaly_count,
        "recoverable_real_continuous_pass_rate": (
            sum(1 for r in recoverable_records if r["current_handoff"] == "pass_formatted_to_parser")
            / len(recoverable_records)
            if recoverable_records
            else None
        ),
        "code_fence_recoverable_pass_rate": (
            sum(1 for r in code_fence_records if r["current_handoff"] == "pass_formatted_to_parser")
            / len(code_fence_records)
            if code_fence_records
            else None
        ),
        "normal_real_continuous_pass_rate": (
            sum(1 for r in normal_records if r["current_handoff"] == "pass_raw_to_parser") / len(normal_records)
            if normal_records
            else None
        ),
        "nonrecoverable_real_continuous_block_rate": (
            sum(1 for r in nonrecoverable_records if r["current_handoff"] == "degeneration_blocked")
            / len(nonrecoverable_records)
            if nonrecoverable_records
            else None
        ),
        "all_cases_match_expected": all(bool(r["match_expected"]) for r in records),
        "stage150_anchored_case_count": len(stage_150_anchored_records),
        "stage150_anchored_cases_match_frozen_reference": all(
            bool(r["match_stage_150_reference"]) for r in stage_150_anchored_records
        ),
        "stage151_anchored_case_count": len(stage_151_anchored_records),
        "stage151_anchored_cases_match_frozen_reference": all(
            bool(r["match_stage_151_reference"]) for r in stage_151_anchored_records
        ),
        "stage152_anchored_case_count": len(stage_152_anchored_records),
        "stage152_anchored_cases_match_frozen_reference": all(
            bool(r["match_stage_152_reference"]) for r in stage_152_anchored_records
        ),
        "path_level_drift": drift,
        "gate_status": gate_result.get("gate_status"),
        "gate_blocked_reason": gate_result.get("blocked_reason"),
        "logistic_status": logistic_status,
        "focused_validation_answers": focused_validation_answers,
        "minimal_collateral_real_continuous_analysis": {
            "new_false_block_count": int(mismatch_counts.get("normal_real_continuous_damage", 0)),
            "new_leak_count": int(mismatch_counts.get("nonrecoverable_real_continuous_leak", 0)),
            "real_execution_correct_but_real_continuous_unstable": bool(
                int(mismatch_counts.get("stage152_reference_drift", 0)) > 0
                or int(mismatch_counts.get("stage151_reference_drift", 0)) > 0
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


def _report(summary: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    lines.append("# Route-C Frozen Semantic Minimal Real Continuous Execution Validation Report")
    lines.append("")
    lines.append("## Real-Continuous Summary")
    lines.append(f"- recoverable_real_continuous_pass_rate: {summary['recoverable_real_continuous_pass_rate']}")
    lines.append(f"- code_fence_recoverable_pass_rate: {summary['code_fence_recoverable_pass_rate']}")
    lines.append(f"- normal_real_continuous_pass_rate: {summary['normal_real_continuous_pass_rate']}")
    lines.append(
        f"- nonrecoverable_real_continuous_block_rate: {summary['nonrecoverable_real_continuous_block_rate']}"
    )
    lines.append(f"- gate_status: {summary['gate_status']}")
    lines.append(f"- logistic_status: {summary['logistic_status']}")
    lines.append(f"- all_cases_match_expected: {summary['all_cases_match_expected']}")
    lines.append(f"- stage152_anchored_cases_match_frozen_reference: {summary['stage152_anchored_cases_match_frozen_reference']}")
    lines.append("")
    lines.append("## Real-Continuous Window Consistency")
    for window in summary["real_continuous_window_summary"]:
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
    lines.append(
        "- recoverable formatting boundary on real-continuous execution stable: "
        + str(answers["recoverable_boundary_stable_on_real_continuous_execution"])
    )
    lines.append(
        "- code-fence-like recoverable handoff on real-continuous execution stable: "
        + str(answers["code_fence_like_recoverable_handoff_stable_on_real_continuous_execution"])
    )
    lines.append(
        "- normal real-continuous execution cases all pass: "
        + str(answers["normal_real_continuous_execution_cases_all_pass"])
    )
    lines.append(
        "- nonrecoverable real-continuous execution cases all blocked: "
        + str(answers["nonrecoverable_real_continuous_execution_cases_all_blocked"])
    )
    lines.append(
        "- parser/gate/health consistency with 150/151/152 kept: "
        + str(answers["parser_gate_health_consistent_with_150_151_152"])
    )
    lines.append(
        "- impact scope remains local to recoverable boundary: "
        + str(answers["impact_scope_limited_to_recoverable_boundary"])
    )
    lines.append("")
    lines.append("## Minimal Collateral Real-Continuous Analysis")
    collateral = summary["minimal_collateral_real_continuous_analysis"]
    lines.append(f"- new_false_block_count: {collateral['new_false_block_count']}")
    lines.append(f"- new_leak_count: {collateral['new_leak_count']}")
    lines.append(
        "- real_execution_correct_but_real_continuous_unstable: "
        + str(collateral["real_execution_correct_but_real_continuous_unstable"])
    )
    lines.append(f"- any_mismatch_detected: {collateral['any_mismatch_detected']}")
    lines.append("")
    lines.append("## Case-Level Evidence")
    for row in records:
        lines.append(
            "- "
            + f"{row['case_id']} ({row['real_continuous_window_id']}#{row['real_continuous_position']} / {row['real_prompt_anchor_id']}): "
            + f"expected {row['expected_handoff']} / {row['expected_category']} -> "
            + f"current {row['current_handoff']} / {row['current_category']} ({row['mismatch_type']})"
        )
    lines.append("")
    lines.append("## Before/After Frozen Reference")
    snapshots = summary["frozen_reference_snapshots"]
    lines.append(f"- stage_150_recoverable_path_pass_rate_reference: {snapshots['stage_150'].get('recoverable_path_pass_rate')}")
    lines.append(
        f"- stage_151_recoverable_real_execution_pass_rate_reference: {snapshots['stage_151'].get('recoverable_real_execution_pass_rate')}"
    )
    lines.append(
        f"- stage_151_nonrecoverable_real_execution_block_rate_reference: {snapshots['stage_151'].get('nonrecoverable_real_execution_block_rate')}"
    )
    lines.append(
        f"- stage_152_recoverable_continuous_pass_rate_reference: {snapshots['stage_152'].get('recoverable_continuous_pass_rate')}"
    )
    lines.append(
        f"- stage_152_normal_continuous_pass_rate_reference: {snapshots['stage_152'].get('normal_continuous_pass_rate')}"
    )
    lines.append(
        f"- stage_152_nonrecoverable_continuous_block_rate_reference: {snapshots['stage_152'].get('nonrecoverable_continuous_block_rate')}"
    )
    return "\n".join(lines) + "\n"


def _load_reference_snapshots(
    stage_148_dir: Path,
    stage_149_dir: Path,
    stage_150_dir: Path,
    stage_151_dir: Path,
    stage_152_dir: Path,
) -> dict[str, Any]:
    stage_148_summary = load_json(_required_file(stage_148_dir / "route_c_recoverable_boundary_control_summary.json"))
    stage_149_summary = load_json(_required_file(stage_149_dir / "route_c_frozen_semantic_small_regression_summary.json"))
    stage_150_summary = load_json(_required_file(stage_150_dir / "route_c_frozen_semantic_minimal_execution_path_regression_summary.json"))
    stage_151_summary = load_json(_required_file(stage_151_dir / "route_c_frozen_semantic_minimal_real_execution_summary.json"))
    stage_152_summary = load_json(_required_file(stage_152_dir / "route_c_frozen_semantic_minimal_continuous_execution_summary.json"))
    return {
        "stage_148": {
            "recoverable_pass_rate": stage_148_summary.get("recoverable_pass_rate"),
            "normal_pass_through_rate": stage_148_summary.get("normal_pass_through_rate"),
            "nonrecoverable_block_rate": stage_148_summary.get("nonrecoverable_block_rate"),
        },
        "stage_149": {
            "recoverable_pass_rate": stage_149_summary.get("recoverable_pass_rate"),
            "normal_pass_through_rate": stage_149_summary.get("normal_pass_through_rate"),
            "nonrecoverable_block_rate": stage_149_summary.get("nonrecoverable_block_rate"),
        },
        "stage_150": {
            "recoverable_path_pass_rate": stage_150_summary.get("recoverable_path_pass_rate"),
            "normal_path_pass_rate": stage_150_summary.get("normal_path_pass_rate"),
            "nonrecoverable_path_block_rate": stage_150_summary.get("nonrecoverable_path_block_rate"),
            "all_cases_match_frozen_reference": stage_150_summary.get("all_cases_match_frozen_reference"),
        },
        "stage_151": {
            "recoverable_real_execution_pass_rate": stage_151_summary.get("recoverable_real_execution_pass_rate"),
            "normal_real_execution_pass_rate": stage_151_summary.get("normal_real_execution_pass_rate"),
            "nonrecoverable_real_execution_block_rate": stage_151_summary.get("nonrecoverable_real_execution_block_rate"),
            "all_cases_match_expected": stage_151_summary.get("all_cases_match_expected"),
        },
        "stage_152": {
            "recoverable_continuous_pass_rate": stage_152_summary.get("recoverable_continuous_pass_rate"),
            "normal_continuous_pass_rate": stage_152_summary.get("normal_continuous_pass_rate"),
            "nonrecoverable_continuous_block_rate": stage_152_summary.get("nonrecoverable_continuous_block_rate"),
            "all_cases_match_expected": stage_152_summary.get("all_cases_match_expected"),
            "path_level_drift_detected": stage_152_summary.get("path_level_drift", {}).get("path_level_drift_detected"),
            "parser_source_drift_detected": stage_152_summary.get("path_level_drift", {}).get("parser_source_drift_detected"),
        },
    }


def build_route_c_frozen_semantic_minimal_real_continuous_execution_validation(
    real_run_dir: Path,
    stage_148_dir: Path,
    stage_149_dir: Path,
    stage_150_dir: Path,
    stage_151_dir: Path,
    stage_152_dir: Path,
    output_dir: Path,
    seed: int,
    label_threshold: float,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    stage_150_reference = _reference_by_case_id(_load_150_details(stage_150_dir))
    stage_151_reference = _reference_by_case_id(_load_151_details(stage_151_dir))
    stage_152_reference = _reference_by_case_id(_load_152_details(stage_152_dir))
    real_raw_rows = _load_real_raw_rows(real_run_dir)
    real_health_rows = _load_real_health_rows(real_run_dir)
    real_fusion_rows = _load_real_fusion_rows(real_run_dir)

    cases = _minimal_real_continuous_suite(
        real_raw_rows=real_raw_rows,
        stage_150_reference_by_case=stage_150_reference,
        stage_151_reference_by_case=stage_151_reference,
        stage_152_reference_by_case=stage_152_reference,
    )

    suite = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "suite_name": "route_c_frozen_semantic_minimal_real_continuous_execution_v1",
        "case_count": len(cases),
        "real_continuous_window_ids": sorted({str(case["real_continuous_window_id"]) for case in cases}),
        "real_prompt_anchor_ids": sorted({str(case["real_prompt_anchor_id"]) for case in cases}),
        "group_counts": dict(Counter(case["path_group"] for case in cases)),
        "source_type_counts": dict(Counter(case["source_type"] for case in cases)),
        "real_execution_input_count": sum(1 for case in cases if bool(case["is_real_execution_input"])),
        "controlled_variant_count": sum(1 for case in cases if not bool(case["is_real_execution_input"])),
        "cases": cases,
    }

    rules = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recoverable_real_continuous_execution_criteria": [
            "recoverable cases must keep pass_formatted_to_parser",
            "code-fence-like recoverable cases must not regress to degeneration_blocked",
            "semantic_guess_used must remain false",
        ],
        "normal_real_continuous_execution_criteria": [
            "normal cases must keep pass_raw_to_parser",
            "normal cases must not gain new collateral damage",
            "no unnecessary anti-degradation over-blocking",
        ],
        "nonrecoverable_real_continuous_execution_criteria": [
            "nonrecoverable cases must keep degeneration_blocked",
            "recoverable-boundary repair must not leak nonrecoverable rows into parser",
        ],
        "real_continuous_execution_consistency_criteria": [
            "parser/gate/label-health/handoff semantics remain coherent",
            "impact scope stays local to recoverable boundary",
            "no new path-level drift or gate/logistic/health anomaly in real continuous chain",
        ],
    }

    execution_root_dir = output_dir / "minimal_real_continuous_execution_root"
    input_manifest = _materialize_real_continuous_execution_inputs(
        cases=cases,
        real_raw_rows=real_raw_rows,
        real_fusion_rows=real_fusion_rows,
        execution_root_dir=execution_root_dir,
    )

    dataset_dir = execution_root_dir / "route_c_v6_dataset_dir"
    dataset_result = build_benchmark_truth_leaning_dataset(
        expanded_real_pilot_fusion_dataset_path=execution_root_dir
        / "execution_inputs"
        / "minimal_real_continuous_execution_fusion_dataset.jsonl",
        labeled_illumination_raw_results_path=execution_root_dir
        / "execution_inputs"
        / "minimal_real_continuous_execution_labeled_raw_results.jsonl",
        output_dir=dataset_dir,
        fusion_profile="route_c_frozen_semantic_minimal_real_continuous_execution",
        run_id="route_c_frozen_semantic_minimal_real_continuous_execution",
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
            fusion_profile="route_c_frozen_semantic_minimal_real_continuous_execution",
            run_id="route_c_frozen_semantic_minimal_real_continuous_execution",
            label_threshold=label_threshold,
            random_seed=seed,
        )
        logistic_status = "PASS"
        logistic_output_paths = logistic_result["output_paths"]
    else:
        logistic_status = "BLOCKED_BY_GATE"

    health_rows = load_jsonl(dataset_dir / "benchmark_truth_leaning_label_health_rows.jsonl")
    records = _evaluate_records(cases=cases, health_rows=health_rows)
    reference_snapshots = _load_reference_snapshots(
        stage_148_dir=stage_148_dir,
        stage_149_dir=stage_149_dir,
        stage_150_dir=stage_150_dir,
        stage_151_dir=stage_151_dir,
        stage_152_dir=stage_152_dir,
    )
    summary = _summary(
        records=records,
        gate_result=gate_result["summary"],
        logistic_status=logistic_status,
        reference_snapshots=reference_snapshots,
    )
    report = _report(summary=summary, records=records)

    write_json(output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_suite.json", suite)
    write_json(output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_rules.json", rules)
    write_json(output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_summary.json", summary)
    write_jsonl(output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_details.jsonl", records)
    (output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_report.md").write_text(report, encoding="utf-8")

    write_json(
        output_dir / "config_snapshot.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "real_run_dir": str(real_run_dir.resolve()),
            "stage_148_dir": str(stage_148_dir.resolve()),
            "stage_149_dir": str(stage_149_dir.resolve()),
            "stage_150_dir": str(stage_150_dir.resolve()),
            "stage_151_dir": str(stage_151_dir.resolve()),
            "stage_152_dir": str(stage_152_dir.resolve()),
            "seed": seed,
            "label_threshold": label_threshold,
            "input_manifest_path": str(
                (execution_root_dir / "execution_inputs" / "real_continuous_execution_input_manifest.json").resolve()
            ),
            "real_health_row_count_reference": len(real_health_rows),
        },
    )

    return {
        "suite": suite,
        "rules": rules,
        "summary": summary,
        "output_paths": {
            "suite": str((output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_suite.json").resolve()),
            "rules": str((output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_rules.json").resolve()),
            "summary": str((output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_summary.json").resolve()),
            "details": str((output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_details.jsonl").resolve()),
            "report": str((output_dir / "route_c_frozen_semantic_minimal_real_continuous_execution_report.md").resolve()),
            "execution_input_manifest": str(
                (execution_root_dir / "execution_inputs" / "real_continuous_execution_input_manifest.json").resolve()
            ),
            "dataset_summary": dataset_result["output_paths"]["summary"],
            "label_health_summary": dataset_result["output_paths"]["label_health_summary"],
            "gate_result": gate_result["output_paths"]["gate_result"],
            "logistic_summary": logistic_output_paths.get("summary"),
            "real_run_dir": str(real_run_dir.resolve()),
            "input_manifest_summary_status": input_manifest["summary_status"],
        },
    }
