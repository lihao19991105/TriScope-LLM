"""Executable freeze pipeline for the DualScope experimental matrix."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_experiment_matrix_common import (
    SCHEMA_VERSION,
    TASK_NAME,
    build_ablation_matrix,
    build_artifact_contract,
    build_attack_trigger_matrix,
    build_baseline_matrix,
    build_capability_mode_matrix,
    build_dataset_matrix,
    build_details,
    build_metrics_contract,
    build_model_matrix,
    build_optional_plans,
    build_problem_definition,
    build_report,
    build_resource_execution_plan,
    build_robustness_matrix,
    build_summary,
    build_table_plan,
    build_target_behavior_matrix,
    write_json,
    write_jsonl,
)


def build_dualscope_experimental_matrix_freeze(output_dir: Path, seed: int) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    problem = build_problem_definition()
    datasets = build_dataset_matrix()
    models = build_model_matrix()
    triggers = build_attack_trigger_matrix()
    targets = build_target_behavior_matrix()
    capabilities = build_capability_mode_matrix()
    baselines = build_baseline_matrix()
    ablations = build_ablation_matrix()
    robustness = build_robustness_matrix()
    metrics = build_metrics_contract()
    tables = build_table_plan()
    resources = build_resource_execution_plan()
    artifact_contract = build_artifact_contract()
    run_order, first_slice, paper_tables = build_optional_plans(resources, tables)
    details = build_details(datasets, models, triggers, targets, capabilities, baselines, metrics)
    summary = build_summary(
        dataset_matrix=datasets,
        model_matrix=models,
        trigger_matrix=triggers,
        target_matrix=targets,
        capability_matrix=capabilities,
        baseline_matrix=baselines,
        ablation_matrix=ablations,
        robustness_matrix=robustness,
        metrics_contract=metrics,
        table_plan=tables,
        details=details,
    )
    report = build_report(summary, resources)

    write_json(output_dir / "dualscope_experimental_matrix_problem_definition.json", problem)
    write_json(output_dir / "dualscope_dataset_matrix.json", datasets)
    write_json(output_dir / "dualscope_model_matrix.json", models)
    write_json(output_dir / "dualscope_attack_trigger_matrix.json", triggers)
    write_json(output_dir / "dualscope_target_behavior_matrix.json", targets)
    write_json(output_dir / "dualscope_capability_mode_matrix.json", capabilities)
    write_json(output_dir / "dualscope_baseline_matrix.json", baselines)
    write_json(output_dir / "dualscope_ablation_matrix.json", ablations)
    write_json(output_dir / "dualscope_robustness_matrix.json", robustness)
    write_json(output_dir / "dualscope_metrics_contract.json", metrics)
    write_json(output_dir / "dualscope_table_plan.json", tables)
    write_json(output_dir / "dualscope_resource_execution_plan.json", resources)
    write_json(output_dir / "dualscope_artifact_contract.json", artifact_contract)
    write_json(output_dir / "dualscope_run_order_plan.json", run_order)
    write_json(output_dir / "dualscope_minimal_first_slice.json", first_slice)
    write_json(output_dir / "dualscope_paper_table_skeleton.json", paper_tables)
    write_json(output_dir / "dualscope_experimental_matrix_freeze_summary.json", summary)
    write_jsonl(output_dir / "dualscope_experimental_matrix_freeze_details.jsonl", details)
    (output_dir / "dualscope_experimental_matrix_freeze_report.md").write_text(report, encoding="utf-8")
    write_json(
        output_dir / "dualscope_experimental_matrix_freeze_run_manifest.json",
        {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "task_name": TASK_NAME,
            "seed": seed,
            "output_dir": str(output_dir.resolve()),
            "full_matrix_executed": False,
        },
    )

    return {
        "summary": summary,
        "output_paths": {
            "summary": str((output_dir / "dualscope_experimental_matrix_freeze_summary.json").resolve()),
            "report": str((output_dir / "dualscope_experimental_matrix_freeze_report.md").resolve()),
            "first_slice": str((output_dir / "dualscope_minimal_first_slice.json").resolve()),
        },
    }
