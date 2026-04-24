"""Build a paper-facing report skeleton for the DualScope first slice."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_common import write_json


SCHEMA_VERSION = "dualscopellm/first-slice-report-skeleton/v1"
TASK_NAME = "dualscope-first-slice-report-skeleton"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def build_dualscope_first_slice_report_skeleton(
    plan_dir: Path,
    smoke_dir: Path,
    validation_dir: Path,
    output_dir: Path,
    docs_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    first_slice = _load_json(plan_dir / "dualscope_first_slice_definition.json")
    smoke_summary = _load_json(smoke_dir / "dualscope_first_slice_smoke_run_summary.json")
    validation_summary = _load_json(validation_dir / "dualscope_first_slice_artifact_validation_summary.json")

    table_skeleton = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "tables": [
            {
                "table_id": "first_slice_setting",
                "columns": ["dataset", "model", "trigger", "target", "capability_mode", "baseline"],
                "status": "ready_for_real_run_values",
            },
            {
                "table_id": "first_slice_smoke_artifact_check",
                "columns": ["artifact_group", "exists", "contract_ok", "notes"],
                "status": "filled_by_artifact_validation",
            },
            {
                "table_id": "first_slice_expected_metrics",
                "columns": ["metric", "required_inputs", "computed_now", "future_real_run"],
                "status": "placeholder_only",
            },
        ],
    }
    figure_placeholder = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "figures": [
            {
                "figure_id": "first_slice_pipeline_flow",
                "description": "Stage 1 screening -> Stage 2 selective verification -> Stage 3 fusion and budget accounting.",
                "status": "placeholder",
            },
            {
                "figure_id": "first_slice_budget_flow",
                "description": "Query cost split between Stage 1 and triggered Stage 2 paths.",
                "status": "placeholder",
            },
        ],
    }
    artifact_links = {
        "plan_summary": str((plan_dir / "dualscope_first_slice_summary.json").resolve()),
        "smoke_summary": str((smoke_dir / "dualscope_first_slice_smoke_run_summary.json").resolve()),
        "validation_summary": str((validation_dir / "dualscope_first_slice_artifact_validation_summary.json").resolve()),
        "stage1_outputs": str((smoke_dir / "stage1_illumination_outputs.jsonl").resolve()),
        "stage2_outputs": str((smoke_dir / "stage2_confidence_outputs.jsonl").resolve()),
        "stage3_outputs": str((smoke_dir / "stage3_fusion_outputs.jsonl").resolve()),
    }
    report_text = "\n".join(
        [
            "# DualScope First Slice Report Skeleton",
            "",
            "## Setting",
            "",
            f"- Dataset: `{first_slice['dataset_id']}`",
            f"- Model: `{first_slice['model_id']}`",
            f"- Trigger: `{first_slice['trigger_id']}`",
            f"- Target: `{first_slice['target_id']}`",
            f"- Capability modes: `{', '.join(first_slice['capability_modes'])}`",
            f"- Baselines: `{', '.join(first_slice['baselines'])}`",
            "",
            "## Smoke Status",
            "",
            f"- Smoke examples: `{smoke_summary['example_count']}`",
            f"- Verification trigger rate: `{smoke_summary['verification_trigger_rate']}`",
            f"- Artifact compatibility: `{validation_summary['contract_compatibility_ok']}`",
            "",
            "## Expected Metrics",
            "",
            "- AUROC",
            "- F1",
            "- TPR@low-FPR",
            "- Average query cost",
            "- Verification trigger rate",
            "",
            "## Artifact Links",
            "",
            *[f"- `{key}`: `{value}`" for key, value in artifact_links.items()],
            "",
            "## Known Limitations",
            "",
            "- This is a controlled smoke skeleton, not a real performance result.",
            "- Metrics are placeholders until a real first-slice run is executed.",
            "- The without-logprobs path remains weaker evidence and must keep degradation flags.",
            "",
            "## Next Experiment Recommendation",
            "",
            "`dualscope-minimal-first-slice-real-run-plan`",
            "",
        ]
    )
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "slice_id": first_slice["slice_id"],
        "report_skeleton_ready": True,
        "table_skeleton_ready": True,
        "figure_placeholder_ready": True,
        "artifact_links_ready": True,
        "performance_claims_made": False,
        "recommended_next_step": "dualscope-minimal-first-slice-real-run-plan",
    }

    write_json(output_dir / "dualscope_first_slice_report_skeleton_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_table_skeleton.json", table_skeleton)
    write_json(output_dir / "dualscope_first_slice_figure_placeholder.json", figure_placeholder)
    write_json(output_dir / "dualscope_first_slice_report_artifact_links.json", artifact_links)
    (output_dir / "dualscope_first_slice_report_skeleton.md").write_text(report_text, encoding="utf-8")
    (docs_dir / "dualscope_first_slice_report_skeleton.md").write_text(report_text, encoding="utf-8")
    write_json(
        output_dir / "dualscope_first_slice_report_skeleton_manifest.json",
        {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "seed": seed, "docs_dir": str(docs_dir.resolve())},
    )
    return {
        "summary": summary,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_report_skeleton_summary.json").resolve()),
            "report": str((output_dir / "dualscope_first_slice_report_skeleton.md").resolve()),
            "docs_report": str((docs_dir / "dualscope_first_slice_report_skeleton.md").resolve()),
        },
    }
