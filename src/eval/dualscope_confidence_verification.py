"""Executable Stage 2 freeze pipeline for DualScope confidence verification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_confidence_common import (
    SCHEMA_VERSION,
    TASK_NAME,
    build_baseline_plan,
    build_budget_contract,
    build_budget_scenarios,
    build_capability_contract,
    build_detail_rows,
    build_feature_examples,
    build_feature_schema_with_logprobs,
    build_feature_schema_without_logprobs,
    build_io_contract,
    build_lock_signal_examples,
    build_no_logprobs_fallback_policy,
    build_problem_definition,
    build_public_field_contract,
    build_report,
    build_representative_cases,
    build_screening_to_confidence_contract,
    build_summary,
    write_json,
    write_jsonl,
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def build_dualscope_confidence_verification(
    stage1_freeze_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    stage1_io_contract = _load_json(stage1_freeze_dir / "dualscope_illumination_io_contract.json")
    stage1_summary = _load_json(stage1_freeze_dir / "dualscope_illumination_screening_freeze_summary.json")

    problem_definition = build_problem_definition()
    capability_contract = build_capability_contract()
    feature_schema_with_logprobs = build_feature_schema_with_logprobs()
    feature_schema_without_logprobs = build_feature_schema_without_logprobs()
    public_field_contract = build_public_field_contract()
    screening_to_confidence_contract = build_screening_to_confidence_contract(
        stage1_io_contract=stage1_io_contract,
        stage1_summary=stage1_summary,
    )
    io_contract = build_io_contract()
    budget_contract = build_budget_contract()
    fallback_policy = build_no_logprobs_fallback_policy()
    baseline_plan = build_baseline_plan()
    representative_cases = build_representative_cases(stage1_summary)
    detail_rows = build_detail_rows(representative_cases, budget_contract)
    feature_examples = build_feature_examples(detail_rows)
    lock_signal_examples = build_lock_signal_examples(detail_rows)
    budget_scenarios = build_budget_scenarios(budget_contract)
    summary = build_summary(
        problem_definition=problem_definition,
        capability_contract=capability_contract,
        feature_schema_with_logprobs=feature_schema_with_logprobs,
        feature_schema_without_logprobs=feature_schema_without_logprobs,
        public_field_contract=public_field_contract,
        screening_to_confidence_contract=screening_to_confidence_contract,
        budget_contract=budget_contract,
        baseline_plan=baseline_plan,
        detail_rows=detail_rows,
    )
    report = build_report(
        problem_definition=problem_definition,
        capability_contract=capability_contract,
        feature_schema_with_logprobs=feature_schema_with_logprobs,
        feature_schema_without_logprobs=feature_schema_without_logprobs,
        public_field_contract=public_field_contract,
        screening_to_confidence_contract=screening_to_confidence_contract,
        io_contract=io_contract,
        budget_contract=budget_contract,
        fallback_policy=fallback_policy,
        baseline_plan=baseline_plan,
        summary=summary,
    )

    write_json(output_dir / "dualscope_confidence_problem_definition.json", problem_definition)
    write_json(output_dir / "dualscope_confidence_capability_contract.json", capability_contract)
    write_json(
        output_dir / "dualscope_confidence_feature_schema_with_logprobs.json",
        feature_schema_with_logprobs,
    )
    write_json(
        output_dir / "dualscope_confidence_feature_schema_without_logprobs.json",
        feature_schema_without_logprobs,
    )
    write_json(output_dir / "dualscope_confidence_public_field_contract.json", public_field_contract)
    write_json(
        output_dir / "dualscope_screening_to_confidence_contract.json",
        screening_to_confidence_contract,
    )
    write_json(output_dir / "dualscope_confidence_io_contract.json", io_contract)
    write_json(output_dir / "dualscope_confidence_budget_contract.json", budget_contract)
    write_json(
        output_dir / "dualscope_confidence_no_logprobs_fallback_policy.json",
        fallback_policy,
    )
    write_json(output_dir / "dualscope_confidence_baseline_plan.json", baseline_plan)
    write_json(output_dir / "dualscope_confidence_verification_summary.json", summary)
    write_jsonl(output_dir / "dualscope_confidence_verification_details.jsonl", detail_rows)
    (output_dir / "dualscope_confidence_verification_report.md").write_text(report, encoding="utf-8")
    write_json(output_dir / "dualscope_confidence_feature_examples.json", feature_examples)
    write_json(output_dir / "dualscope_confidence_lock_signal_examples.json", lock_signal_examples)
    write_json(output_dir / "dualscope_confidence_budget_scenarios.json", budget_scenarios)
    write_json(
        output_dir / "dualscope_confidence_run_manifest.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "task_name": TASK_NAME,
            "seed": seed,
            "stage1_freeze_dir": str(stage1_freeze_dir.resolve()),
            "representative_case_count": len(representative_cases),
            "detail_row_count": len(detail_rows),
        },
    )

    return {
        "summary": summary,
        "output_paths": {
            "problem_definition": str((output_dir / "dualscope_confidence_problem_definition.json").resolve()),
            "capability_contract": str(
                (output_dir / "dualscope_confidence_capability_contract.json").resolve()
            ),
            "feature_schema_with_logprobs": str(
                (output_dir / "dualscope_confidence_feature_schema_with_logprobs.json").resolve()
            ),
            "feature_schema_without_logprobs": str(
                (output_dir / "dualscope_confidence_feature_schema_without_logprobs.json").resolve()
            ),
            "public_field_contract": str(
                (output_dir / "dualscope_confidence_public_field_contract.json").resolve()
            ),
            "screening_to_confidence_contract": str(
                (output_dir / "dualscope_screening_to_confidence_contract.json").resolve()
            ),
            "io_contract": str((output_dir / "dualscope_confidence_io_contract.json").resolve()),
            "budget_contract": str((output_dir / "dualscope_confidence_budget_contract.json").resolve()),
            "fallback_policy": str(
                (output_dir / "dualscope_confidence_no_logprobs_fallback_policy.json").resolve()
            ),
            "baseline_plan": str((output_dir / "dualscope_confidence_baseline_plan.json").resolve()),
            "summary": str((output_dir / "dualscope_confidence_verification_summary.json").resolve()),
            "details": str((output_dir / "dualscope_confidence_verification_details.jsonl").resolve()),
            "report": str((output_dir / "dualscope_confidence_verification_report.md").resolve()),
        },
    }
