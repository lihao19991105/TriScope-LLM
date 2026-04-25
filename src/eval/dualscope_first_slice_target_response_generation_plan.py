"""Plan first-slice target response generation without fabricating outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import (
    SCHEMA_VERSION,
    base_scope,
    markdown,
    read_json,
    read_jsonl,
    run_py_compile,
    write_json,
    write_jsonl,
)


PY_FILES = [
    "src/eval/dualscope_first_slice_target_response_generation_plan.py",
    "scripts/build_dualscope_first_slice_target_response_generation_plan.py",
]


def _optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"summary_status": "MISSING", "path": str(path)}
    return read_json(path)


def _resolve_repo_path(repo_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def _index_by_row_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("row_id")): row for row in rows if row.get("row_id")}


def _pairing_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_pair: dict[str, set[str]] = {}
    for row in rows:
        by_pair.setdefault(str(row.get("pair_id")), set()).add(str(row.get("condition")))
    complete_pair_count = sum(1 for conditions in by_pair.values() if {"clean", "poisoned_triggered"} <= conditions)
    return {
        "pair_count": len(by_pair),
        "complete_pair_count": complete_pair_count,
        "clean_row_count": sum(1 for row in rows if row.get("condition") == "clean"),
        "poisoned_triggered_row_count": sum(1 for row in rows if row.get("condition") == "poisoned_triggered"),
        "asr_eligible_row_count": sum(1 for row in rows if row.get("asr_eligible") is True),
        "utility_eligible_row_count": sum(1 for row in rows if row.get("utility_eligible") is True),
    }


def _planned_generation_rows(
    joined_rows: list[dict[str, Any]],
    labeled_rows_by_id: dict[str, dict[str, Any]],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    seed: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    planned_rows: list[dict[str, Any]] = []
    missing_row_ids: list[str] = []
    for joined in joined_rows:
        row_id = str(joined.get("row_id") or "")
        labeled = labeled_rows_by_id.get(row_id)
        if labeled is None:
            missing_row_ids.append(row_id)
            continue
        condition = str(labeled.get("condition") or "")
        planned_rows.append(
            {
                "generation_request_id": f"target_response_generation::{row_id}",
                "row_id": row_id,
                "pair_id": labeled.get("pair_id"),
                "source_example_id": labeled.get("source_example_id"),
                "dataset_id": labeled.get("dataset_id"),
                "condition": condition,
                "prompt": labeled.get("prompt"),
                "trigger_present": labeled.get("trigger_present"),
                "detection_label": labeled.get("detection_label"),
                "asr_eligible": labeled.get("asr_eligible"),
                "utility_eligible": labeled.get("utility_eligible"),
                "target_text": labeled.get("target_text"),
                "target_match_rule": labeled.get("target_match_rule"),
                "response_reference": labeled.get("response_reference"),
                "expected_metric_use": "asr" if condition == "poisoned_triggered" else "clean_utility",
                "generation_config": {
                    "seed": seed,
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "do_sample": temperature > 0.0,
                },
                "model_response_present": False,
                "model_response_fabricated": False,
            }
        )
    return planned_rows, missing_row_ids


def build_target_response_generation_plan(
    output_dir: Path,
    labeled_rerun_dir: Path,
    labeled_slice_dir: Path,
    seed: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    no_full_matrix: bool,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    if not no_full_matrix:
        raise ValueError("--no-full-matrix is required.")
    if max_new_tokens <= 0:
        raise ValueError("--max-new-tokens must be positive.")
    if not 0.0 <= temperature <= 2.0:
        raise ValueError("--temperature must be between 0.0 and 2.0.")
    if not 0.0 < top_p <= 1.0:
        raise ValueError("--top-p must be in (0.0, 1.0].")

    label_summary = _optional_json(labeled_slice_dir / "dualscope_first_slice_clean_poisoned_labeled_slice_summary.json")
    target_contract = _optional_json(labeled_slice_dir / "dualscope_first_slice_target_contract.json")
    trigger_contract = _optional_json(labeled_slice_dir / "dualscope_first_slice_trigger_contract.json")
    asr_contract = _optional_json(labeled_slice_dir / "dualscope_first_slice_asr_label_contract.json")
    utility_contract = _optional_json(labeled_slice_dir / "dualscope_first_slice_utility_label_contract.json")
    pair_manifest = _optional_json(labeled_slice_dir / "dualscope_first_slice_clean_poisoned_pair_manifest.json")
    rerun_summary = _optional_json(
        labeled_rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_summary.json"
    )
    metric_readiness = _optional_json(
        labeled_rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_metric_readiness.json"
    )

    joined_rows_path = labeled_rerun_dir / "dualscope_minimal_first_slice_real_run_rerun_with_labels_joined_rows.jsonl"
    joined_rows = read_jsonl(joined_rows_path) if joined_rows_path.exists() else []
    labeled_rows_path = _resolve_repo_path(repo_root, str(pair_manifest.get("output_file", "")))
    labeled_rows = read_jsonl(labeled_rows_path) if labeled_rows_path.exists() else []
    planned_rows, missing_row_ids = _planned_generation_rows(
        joined_rows=joined_rows,
        labeled_rows_by_id=_index_by_row_id(labeled_rows),
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        seed=seed,
    )
    pairing = _pairing_summary(planned_rows)
    py_compile = run_py_compile(repo_root, PY_FILES)

    source_artifact_audit = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "labeled_slice_dir": str(labeled_slice_dir),
        "labeled_rerun_dir": str(labeled_rerun_dir),
        "label_verdict": label_summary.get("final_verdict"),
        "labeled_rerun_verdict": rerun_summary.get("final_verdict"),
        "target_contract_status": target_contract.get("summary_status"),
        "trigger_contract_status": trigger_contract.get("summary_status"),
        "asr_contract_status": asr_contract.get("summary_status"),
        "utility_contract_status": utility_contract.get("summary_status"),
        "joined_rows_path": str(joined_rows_path),
        "joined_row_count": len(joined_rows),
        "labeled_rows_path": str(labeled_rows_path),
        "labeled_row_count": len(labeled_rows),
        "missing_joined_row_ids_in_labeled_slice": missing_row_ids,
    }
    generation_manifest = {
        "summary_status": "PASS" if planned_rows and not missing_row_ids else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-first-slice-target-response-generation-plan",
        "planned_generation_rows_file": str(
            output_dir / "dualscope_first_slice_target_response_generation_plan_rows.jsonl"
        ),
        "planned_generation_row_count": len(planned_rows),
        "source_joined_row_count": len(joined_rows),
        "source_labeled_row_count": len(labeled_rows),
        "scope_policy": "same joined first-slice label rows only; no full-matrix expansion",
        "target_text": target_contract.get("target_text"),
        "target_match_rule": target_contract.get("target_match_rule"),
        "trigger_text": trigger_contract.get("trigger_text"),
        "generation_backend_policy": "local HuggingFace backend preferred; API backend remains optional abstraction",
        "model_responses_included": False,
        "model_responses_fabricated": False,
        **pairing,
    }
    response_output_schema = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "output_row_required_fields": [
            "generation_request_id",
            "row_id",
            "pair_id",
            "condition",
            "prompt",
            "model_response",
            "response_backend",
            "generation_config",
            "target_text",
            "target_match_rule",
            "target_matched",
            "asr_eligible",
            "utility_eligible",
            "response_reference",
        ],
        "asr_rule": "For asr_eligible poisoned_triggered rows, target_matched follows the frozen target_match_rule.",
        "utility_rule": "For utility_eligible clean rows, preserve model_response and response_reference for later scoring.",
        "forbidden_fields_without_generation": ["model_response"],
        "benchmark_truth_changed": False,
        "gate_changed": False,
    }
    command_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "recommended_command": (
            "python3 scripts/run_dualscope_first_slice_target_response_generation.py "
            f"--input-jsonl {generation_manifest['planned_generation_rows_file']} "
            "--output-jsonl outputs/dualscope_first_slice_target_response_generation/default/"
            "dualscope_first_slice_target_response_generation_rows.jsonl "
            f"--seed {seed} --max-new-tokens {max_new_tokens}"
        ),
        "requires_new_execution_entrypoint": True,
        "entrypoint_to_add_next": "scripts/run_dualscope_first_slice_target_response_generation.py",
        "no_training": True,
        "no_full_matrix": True,
        "no_benchmark_truth_change": True,
        "no_gate_change": True,
    }
    metric_dependency_plan = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "current_metric_readiness_reason": metric_readiness.get("reason"),
        "unblocked_by_target_response_generation": ["asr", "clean_utility"],
        "still_not_claimed_by_this_plan": ["paper_performance_metrics", "model_response_metrics"],
        "asr_inputs_required": asr_contract.get("asr_requires", []),
        "clean_utility_inputs_required": utility_contract.get("clean_utility_requires", []),
        "performance_metrics_reported": False,
    }

    validated = (
        label_summary.get("final_verdict") == "Clean-poisoned labeled slice plan validated"
        and target_contract.get("summary_status") == "PASS"
        and trigger_contract.get("summary_status") == "PASS"
        and rerun_summary.get("final_verdict") in {"Partially validated", "Minimal first-slice labeled rerun validated"}
        and bool(planned_rows)
        and not missing_row_ids
        and pairing["clean_row_count"] == pairing["poisoned_triggered_row_count"]
        and py_compile["passed"]
    )
    final_verdict = "Target-response generation plan validated" if validated else "Not validated"
    recommendation = (
        "dualscope-first-slice-real-run-artifact-validation"
        if validated
        else "dualscope-first-slice-target-response-generation-plan-blocker-closure"
    )
    scope = base_scope("dualscope-first-slice-target-response-generation-plan", output_dir)
    scope.update(
        {
            "labeled_rerun_dir": str(labeled_rerun_dir),
            "labeled_slice_dir": str(labeled_slice_dir),
            "seed": seed,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "no_full_matrix": no_full_matrix,
            "model_responses_generated": False,
            "model_outputs_fabricated": False,
        }
    )
    summary = {
        "summary_status": "PASS" if validated else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-first-slice-target-response-generation-plan",
        "planned_generation_row_count": len(planned_rows),
        "planned_pair_count": pairing["pair_count"],
        "clean_row_count": pairing["clean_row_count"],
        "poisoned_triggered_row_count": pairing["poisoned_triggered_row_count"],
        "asr_eligible_row_count": pairing["asr_eligible_row_count"],
        "utility_eligible_row_count": pairing["utility_eligible_row_count"],
        "target_text": target_contract.get("target_text"),
        "target_match_rule": target_contract.get("target_match_rule"),
        "trigger_text": trigger_contract.get("trigger_text"),
        "labels_ready": label_summary.get("schema_valid") is True and label_summary.get("pairing_valid") is True,
        "model_responses_generated": False,
        "model_outputs_fabricated": False,
        "performance_metrics_reported": False,
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
        "py_compile_passed": py_compile["passed"],
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }

    write_json(output_dir / "dualscope_first_slice_target_response_generation_plan_scope.json", scope)
    write_json(
        output_dir / "dualscope_first_slice_target_response_generation_plan_source_artifact_audit.json",
        source_artifact_audit,
    )
    write_json(
        output_dir / "dualscope_first_slice_target_response_generation_plan_manifest.json",
        generation_manifest,
    )
    write_json(
        output_dir / "dualscope_first_slice_target_response_generation_plan_output_schema.json",
        response_output_schema,
    )
    write_json(output_dir / "dualscope_first_slice_target_response_generation_plan_command_plan.json", command_plan)
    write_json(
        output_dir / "dualscope_first_slice_target_response_generation_plan_metric_dependency.json",
        metric_dependency_plan,
    )
    write_json(output_dir / "dualscope_first_slice_target_response_generation_plan_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_first_slice_target_response_generation_plan_summary.json", summary)
    write_json(
        output_dir / "dualscope_first_slice_target_response_generation_plan_verdict.json",
        {
            "summary_status": summary["summary_status"],
            "schema_version": SCHEMA_VERSION,
            "final_verdict": final_verdict,
            "recommended_next_step": recommendation,
        },
    )
    write_jsonl(output_dir / "dualscope_first_slice_target_response_generation_plan_rows.jsonl", planned_rows)
    write_jsonl(
        output_dir / "dualscope_first_slice_target_response_generation_plan_details.jsonl",
        [
            {"detail_type": "source_artifact_audit", "payload": source_artifact_audit},
            {"detail_type": "generation_manifest", "payload": generation_manifest},
            {"detail_type": "response_output_schema", "payload": response_output_schema},
            {"detail_type": "metric_dependency_plan", "payload": metric_dependency_plan},
        ],
    )
    markdown(
        output_dir / "dualscope_first_slice_target_response_generation_plan_report.md",
        "DualScope First-Slice Target Response Generation Plan",
        [
            f"- Final verdict: `{final_verdict}`",
            f"- Planned generation rows: `{len(planned_rows)}` across `{pairing['pair_count']}` pairs",
            f"- Clean utility rows: `{pairing['utility_eligible_row_count']}`",
            f"- Poisoned ASR rows: `{pairing['asr_eligible_row_count']}`",
            f"- Frozen trigger: `{trigger_contract.get('trigger_text')}`",
            f"- Frozen target response: `{target_contract.get('target_text')}`",
            "- Model responses generated in this task: `False`",
            "- Model outputs fabricated: `False`",
            "- Benchmark truth changed: `False`",
            "- Gates changed: `False`",
            "- Full matrix executed: `False`",
            f"- Recommended next step: `{recommendation}`",
        ],
    )
    return summary
