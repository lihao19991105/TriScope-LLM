"""Stabilize 1.5B route_b label balance using existing execution artifacts."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "triscopellm/model-axis-1p5b-route-b-stabilization/v1"
STRICT_OPTION_PATTERN = re.compile(r"\b([A-D])\b")
# Capture leading option labels like "AHuman: ..." produced by some local runs.
ROBUST_PREFIX_OPTION_PATTERN = re.compile(r"^\s*([A-D])(?=Human:|Assistant:|[^A-Za-z0-9_]|$)")


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object on line {line_number} of `{path}`.")
            rows.append(payload)
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("Expected at least one row for CSV export.")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_option_strict(response_text: str) -> str | None:
    match = STRICT_OPTION_PATTERN.search(response_text)
    return match.group(1) if match is not None else None


def parse_option_robust(response_text: str) -> str | None:
    prefix_match = ROBUST_PREFIX_OPTION_PATTERN.search(response_text)
    if prefix_match is not None:
        return prefix_match.group(1)
    return parse_option_strict(response_text)


def compute_subset_class_balance(reference_rows: list[dict[str, Any]], selected_ids: list[str]) -> dict[str, int]:
    selected = set(selected_ids)
    subset = [row for row in reference_rows if str(row.get("sample_id")) in selected]
    return {
        "label_0": sum(1 for row in subset if int(row.get("ground_truth_label", 0)) == 0),
        "label_1": sum(1 for row in subset if int(row.get("ground_truth_label", 0)) == 1),
    }


def build_balanced_candidate_rows(
    route_b_rows: list[dict[str, Any]],
    illumination_raw_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    illumination_map = {str(row["sample_id"]): row for row in illumination_raw_rows}

    candidate_rows: list[dict[str, Any]] = []
    strict_parse_success = 0
    robust_parse_success = 0
    robust_flip_count = 0

    for row in route_b_rows:
        sample_id = str(row["sample_id"])
        illumination_row = illumination_map.get(sample_id)
        if illumination_row is None:
            raise ValueError(f"Missing illumination raw row for sample_id `{sample_id}`.")

        response_text = str(illumination_row.get("response_text", ""))
        answer_key = str(
            illumination_row.get("metadata", {})
            .get("contract_metadata", {})
            .get("query_answer_key", "")
        )

        strict_option = parse_option_strict(response_text)
        robust_option = parse_option_robust(response_text)
        if strict_option is not None:
            strict_parse_success += 1
        if robust_option is not None:
            robust_parse_success += 1

        original_illumination_correct = bool(row.get("illumination_task_correct"))
        if robust_option is not None and answer_key:
            stabilized_illumination_correct = robust_option == answer_key
        else:
            stabilized_illumination_correct = original_illumination_correct

        if stabilized_illumination_correct != original_illumination_correct:
            robust_flip_count += 1

        reasoning_correct = bool(row.get("reasoning_task_correct"))
        confidence_correct = bool(row.get("confidence_task_correct"))
        violation_count = sum(
            [
                int(not reasoning_correct),
                int(not confidence_correct),
                int(not stabilized_illumination_correct),
            ]
        )
        stabilized_label = 1 if violation_count > 0 else 0

        candidate_row = dict(row)
        candidate_row["original_ground_truth_label"] = int(row.get("ground_truth_label", 0))
        candidate_row["ground_truth_label"] = stabilized_label
        candidate_row["original_illumination_task_correct"] = original_illumination_correct
        candidate_row["stabilized_illumination_task_correct"] = stabilized_illumination_correct
        candidate_row["strict_illumination_response_option"] = strict_option
        candidate_row["stabilized_illumination_response_option"] = robust_option
        candidate_row["stabilization_rule"] = "robust_prefix_option_parse_plus_existing_violation_rule"
        candidate_row["stabilization_scope"] = "model_axis_1p5b_route_b_only"
        candidate_rows.append(candidate_row)

    diagnostics = {
        "strict_parse_success_count": strict_parse_success,
        "robust_parse_success_count": robust_parse_success,
        "illumination_correctness_flip_count": robust_flip_count,
        "row_count": len(candidate_rows),
    }
    return candidate_rows, diagnostics


def summarize_candidate_rows(candidate_rows: list[dict[str, Any]], diagnostics: dict[str, Any]) -> dict[str, Any]:
    class_balance = {
        "label_0": sum(1 for row in candidate_rows if int(row.get("ground_truth_label", 0)) == 0),
        "label_1": sum(1 for row in candidate_rows if int(row.get("ground_truth_label", 0)) == 1),
    }
    original_class_balance = {
        "label_0": sum(1 for row in candidate_rows if int(row.get("original_ground_truth_label", 0)) == 0),
        "label_1": sum(1 for row in candidate_rows if int(row.get("original_ground_truth_label", 0)) == 1),
    }
    modality_correctness_coverage = {
        "reasoning_task_correct_true": sum(1 for row in candidate_rows if bool(row.get("reasoning_task_correct"))),
        "confidence_task_correct_true": sum(1 for row in candidate_rows if bool(row.get("confidence_task_correct"))),
        "stabilized_illumination_task_correct_true": sum(
            1 for row in candidate_rows if bool(row.get("stabilized_illumination_task_correct"))
        ),
    }

    summary_status = "PASS" if class_balance["label_0"] > 0 and class_balance["label_1"] > 0 else "BLOCKED"
    return {
        "summary_status": summary_status,
        "schema_version": SCHEMA_VERSION,
        "dataset_name": "route_b_balanced_candidate_dataset",
        "row_count": len(candidate_rows),
        "class_balance": class_balance,
        "original_class_balance": original_class_balance,
        "modality_correctness_coverage": modality_correctness_coverage,
        "stabilization_diagnostics": diagnostics,
        "notes": [
            "Candidate labels preserve the existing violation-count rule but stabilize illumination option parsing for prefix-form responses.",
            "This is a route_b 1.5B stabilization artifact, not a benchmark-ground-truth relabeling.",
        ],
    }


def build_model_axis_1p5b_route_b_stabilization(
    execution_dir: Path,
    reference_route_b_dataset_path: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    execution_run_summary = load_json(execution_dir / "model_axis_1p5b_execution_run_summary.json")
    execution_plan = load_json(execution_dir / "model_axis_1p5b_execution_plan.json")
    materialization_summary = load_json(
        execution_dir / "materialized_model_axis_1p5b_execution_inputs" / "materialization_summary.json"
    )
    route_b_summary = load_json(execution_dir / "model_axis_1p5b_route_b_summary.json")
    route_b_logistic_summary = load_json(execution_dir / "model_axis_1p5b_route_b_logistic_summary.json")

    route_b_rows = load_jsonl(
        execution_dir / "model_axis_1p5b_execution_outputs" / "route_b" / "route_b_v6_dataset.jsonl"
    )
    illumination_raw_rows = load_jsonl(
        execution_dir
        / "model_axis_1p5b_execution_outputs"
        / "route_b"
        / "route_b_v6_illumination"
        / "illumination_probe"
        / "raw_results.jsonl"
    )
    reference_rows = load_jsonl(reference_route_b_dataset_path)

    selected_ids = [str(item) for item in materialization_summary.get("selected_sample_ids", [])]
    selection_subset_balance = compute_subset_class_balance(reference_rows=reference_rows, selected_ids=selected_ids)

    candidate_rows, stabilization_diagnostics = build_balanced_candidate_rows(
        route_b_rows=route_b_rows,
        illumination_raw_rows=illumination_raw_rows,
    )
    candidate_summary = summarize_candidate_rows(candidate_rows=candidate_rows, diagnostics=stabilization_diagnostics)

    diagnosis = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "selected_cell": execution_run_summary.get("selected_cell"),
        "selected_model_profile": execution_run_summary.get("selected_model_profile"),
        "execution_status": execution_run_summary.get("execution_status"),
        "row_count": route_b_summary.get("num_rows"),
        "observed_class_balance": route_b_summary.get("class_balance"),
        "reference_subset_class_balance": selection_subset_balance,
        "logistic_blocked_reason": route_b_logistic_summary.get("blocking_reason"),
        "direct_causes": [
            {
                "factor": "label_construction",
                "evidence": {
                    "illumination_response_option_none_count": sum(
                        1 for row in route_b_rows if row.get("illumination_response_option") in (None, "")
                    ),
                    "illumination_task_correct_true_count": sum(
                        1 for row in route_b_rows if bool(row.get("illumination_task_correct"))
                    ),
                    "strict_option_parse_success_count": stabilization_diagnostics["strict_parse_success_count"],
                    "robust_option_parse_success_count": stabilization_diagnostics["robust_parse_success_count"],
                },
                "conclusion": "Primary cause. Strict option parsing misses prefix-form responses such as 'AHuman: ...', forcing illumination_task_correct to false for all rows.",
            },
            {
                "factor": "sample_selection",
                "evidence": {
                    "selected_positive_reference_count": materialization_summary.get("selection_stats", {}).get(
                        "selected_positive_reference_count"
                    ),
                    "selected_negative_reference_count": materialization_summary.get("selection_stats", {}).get(
                        "selected_negative_reference_count"
                    ),
                    "reference_subset_class_balance": selection_subset_balance,
                },
                "conclusion": "Not the primary blocker. The selected 32-row subset is already bi-class in the v6 reference route_b labels (24/8).",
            },
            {
                "factor": "target_budget",
                "evidence": {
                    "target_budget": execution_plan.get("target_budget"),
                    "selected_sample_count": execution_plan.get("selected_sample_count"),
                },
                "conclusion": "Secondary. Budget=32 reduces margin but does not explain all-positive collapse by itself.",
            },
            {
                "factor": "fallback_logic",
                "evidence": {
                    "fallback_rule_declared": execution_plan.get("fallback_rule"),
                    "fallback_used": execution_run_summary.get("fallback_used"),
                    "logistic_blocked_reason": execution_run_summary.get("logistic_blocked_reason"),
                },
                "conclusion": "Fallback was not reached in 107 output even though logistic was blocked, so it did not mitigate the collapse.",
            },
        ],
        "overall_conclusion": "Collapse is multi-factor but dominated by illumination label-construction mismatch; the minimal fix path is to stabilize illumination option parsing while keeping the existing violation-count contract.",
    }

    recovery_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_next_step": "stabilize_model_axis_1p5b_route_b_label_balance",
        "minimal_change_path": [
            "Keep route_b selection strategy and budget contract unchanged for first stabilization attempt.",
            "Apply robust prefix-aware option parsing to illumination responses during route_b label construction.",
            "Recompute labels with the same violation-count rule and run a precheck for >=2 classes.",
            "Only if precheck still fails, trigger full-contract fallback rerun.",
        ],
        "expected_effect": {
            "before": route_b_summary.get("class_balance"),
            "after_candidate": candidate_summary.get("class_balance"),
            "logistic_prereq_before": False,
            "logistic_prereq_after_candidate": candidate_summary["class_balance"]["label_0"] > 0
            and candidate_summary["class_balance"]["label_1"] > 0,
        },
        "contract_guards": [
            "No 3B/7B switch.",
            "No dataset-axis expansion.",
            "No fusion v12/v13 rollback.",
            "No new training pipeline.",
        ],
    }

    knobs_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "seed": seed,
        "selection_knobs": {
            "selection_strategy": materialization_summary.get("selection_stats", {}).get("selection_strategy"),
            "target_budget": materialization_summary.get("selection_stats", {}).get("requested_budget"),
            "selected_positive_reference_count": materialization_summary.get("selection_stats", {}).get(
                "selected_positive_reference_count"
            ),
            "selected_negative_reference_count": materialization_summary.get("selection_stats", {}).get(
                "selected_negative_reference_count"
            ),
        },
        "fallback_knobs": {
            "fallback_rule": execution_plan.get("fallback_rule"),
            "fallback_used_in_107": execution_run_summary.get("fallback_used"),
        },
        "label_construction_knobs": {
            "original_parser": "word-boundary option parser",
            "stabilized_parser": "prefix-aware option parser with strict fallback",
            "label_mapping_rule": "1 if any modality violates task correctness, else 0",
        },
    }

    precheck = {
        "summary_status": "PASS" if candidate_summary["summary_status"] == "PASS" else "BLOCKED",
        "schema_version": SCHEMA_VERSION,
        "dataset_name": "route_b_balanced_candidate_dataset",
        "row_count": candidate_summary["row_count"],
        "class_balance": candidate_summary["class_balance"],
        "logistic_prereq_two_classes": candidate_summary["class_balance"]["label_0"] > 0
        and candidate_summary["class_balance"]["label_1"] > 0,
        "rerun_unlock_ready": candidate_summary["class_balance"]["label_0"] > 0
        and candidate_summary["class_balance"]["label_1"] > 0,
        "notes": [
            "Precheck is based on real 107 route_b outputs plus stabilized illumination parsing.",
            "This precheck does not replace a true 1.5B stabilized rerun.",
        ],
    }

    write_json(output_dir / "route_b_label_collapse_diagnosis.json", diagnosis)
    write_json(output_dir / "route_b_label_balance_recovery_plan.json", recovery_plan)
    write_json(output_dir / "route_b_selection_knobs_summary.json", knobs_summary)
    write_jsonl(output_dir / "route_b_balanced_candidate_dataset.jsonl", candidate_rows)
    write_csv(output_dir / "route_b_balanced_candidate_dataset.csv", candidate_rows)
    write_json(output_dir / "route_b_balanced_candidate_summary.json", candidate_summary)
    write_json(output_dir / "route_b_label_balance_precheck.json", precheck)
    write_json(
        output_dir / "route_b_stabilization_registry.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "artifacts": {
                "diagnosis": str((output_dir / "route_b_label_collapse_diagnosis.json").resolve()),
                "recovery_plan": str((output_dir / "route_b_label_balance_recovery_plan.json").resolve()),
                "knobs_summary": str((output_dir / "route_b_selection_knobs_summary.json").resolve()),
                "candidate_dataset_jsonl": str((output_dir / "route_b_balanced_candidate_dataset.jsonl").resolve()),
                "candidate_dataset_csv": str((output_dir / "route_b_balanced_candidate_dataset.csv").resolve()),
                "candidate_summary": str((output_dir / "route_b_balanced_candidate_summary.json").resolve()),
                "precheck": str((output_dir / "route_b_label_balance_precheck.json").resolve()),
            },
        },
    )

    return {
        "diagnosis": diagnosis,
        "candidate_summary": candidate_summary,
        "precheck": precheck,
        "output_paths": {
            "diagnosis": str((output_dir / "route_b_label_collapse_diagnosis.json").resolve()),
            "recovery_plan": str((output_dir / "route_b_label_balance_recovery_plan.json").resolve()),
            "knobs_summary": str((output_dir / "route_b_selection_knobs_summary.json").resolve()),
            "candidate_dataset_jsonl": str((output_dir / "route_b_balanced_candidate_dataset.jsonl").resolve()),
            "candidate_summary": str((output_dir / "route_b_balanced_candidate_summary.json").resolve()),
            "precheck": str((output_dir / "route_b_label_balance_precheck.json").resolve()),
        },
    }
