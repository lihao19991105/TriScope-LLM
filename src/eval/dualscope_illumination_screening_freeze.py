"""Executable Stage 1 freeze pipeline for DualScope illumination screening."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_illumination_common import (
    SCHEMA_VERSION,
    TASK_NAME,
    build_baseline_plan,
    build_budget_contract,
    build_budget_scenarios,
    build_detail_rows,
    build_feature_examples,
    build_feature_schema,
    build_io_contract,
    build_problem_definition,
    build_probe_templates,
    build_report,
    build_representative_cases,
    build_summary,
    build_template_matrix,
    write_json,
    write_jsonl,
)


def build_dualscope_illumination_screening_freeze(
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    problem_definition = build_problem_definition()
    probe_templates = build_probe_templates()
    feature_schema = build_feature_schema()
    io_contract = build_io_contract()
    budget_contract = build_budget_contract()
    baseline_plan = build_baseline_plan()

    representative_cases = build_representative_cases()
    detail_rows, aggregates = build_detail_rows(
        cases=representative_cases,
        probe_templates=probe_templates,
        budget_contract=budget_contract,
    )
    template_matrix = build_template_matrix(probe_templates, budget_contract)
    feature_examples = build_feature_examples(aggregates)
    budget_scenarios = build_budget_scenarios(budget_contract)
    summary = build_summary(
        problem_definition=problem_definition,
        probe_templates=probe_templates,
        feature_schema=feature_schema,
        io_contract=io_contract,
        budget_contract=budget_contract,
        baseline_plan=baseline_plan,
        detail_rows=detail_rows,
        aggregates=aggregates,
    )
    report = build_report(
        problem_definition=problem_definition,
        probe_templates=probe_templates,
        feature_schema=feature_schema,
        io_contract=io_contract,
        budget_contract=budget_contract,
        baseline_plan=baseline_plan,
        summary=summary,
        aggregates=aggregates,
    )

    write_json(output_dir / "dualscope_illumination_problem_definition.json", problem_definition)
    write_json(output_dir / "dualscope_illumination_probe_templates.json", probe_templates)
    write_json(output_dir / "dualscope_illumination_feature_schema.json", feature_schema)
    write_json(output_dir / "dualscope_illumination_io_contract.json", io_contract)
    write_json(output_dir / "dualscope_illumination_budget_contract.json", budget_contract)
    write_json(output_dir / "dualscope_illumination_baseline_plan.json", baseline_plan)
    write_json(output_dir / "dualscope_illumination_screening_freeze_summary.json", summary)
    write_jsonl(output_dir / "dualscope_illumination_screening_freeze_details.jsonl", detail_rows)
    (output_dir / "dualscope_illumination_screening_freeze_report.md").write_text(report, encoding="utf-8")
    write_json(output_dir / "dualscope_illumination_template_matrix.json", template_matrix)
    write_json(output_dir / "dualscope_illumination_feature_examples.json", feature_examples)
    write_json(output_dir / "dualscope_illumination_budget_scenarios.json", budget_scenarios)
    write_json(
        output_dir / "dualscope_illumination_run_manifest.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "task_name": TASK_NAME,
            "seed": seed,
            "representative_case_count": len(representative_cases),
            "detail_row_count": len(detail_rows),
        },
    )

    return {
        "problem_definition": problem_definition,
        "probe_templates": probe_templates,
        "feature_schema": feature_schema,
        "io_contract": io_contract,
        "budget_contract": budget_contract,
        "baseline_plan": baseline_plan,
        "summary": summary,
        "output_paths": {
            "problem_definition": str((output_dir / "dualscope_illumination_problem_definition.json").resolve()),
            "probe_templates": str((output_dir / "dualscope_illumination_probe_templates.json").resolve()),
            "feature_schema": str((output_dir / "dualscope_illumination_feature_schema.json").resolve()),
            "io_contract": str((output_dir / "dualscope_illumination_io_contract.json").resolve()),
            "budget_contract": str((output_dir / "dualscope_illumination_budget_contract.json").resolve()),
            "baseline_plan": str((output_dir / "dualscope_illumination_baseline_plan.json").resolve()),
            "summary": str((output_dir / "dualscope_illumination_screening_freeze_summary.json").resolve()),
            "details": str((output_dir / "dualscope_illumination_screening_freeze_details.jsonl").resolve()),
            "report": str((output_dir / "dualscope_illumination_screening_freeze_report.md").resolve()),
            "template_matrix": str((output_dir / "dualscope_illumination_template_matrix.json").resolve()),
            "feature_examples": str((output_dir / "dualscope_illumination_feature_examples.json").resolve()),
            "budget_scenarios": str((output_dir / "dualscope_illumination_budget_scenarios.json").resolve()),
        },
    }
