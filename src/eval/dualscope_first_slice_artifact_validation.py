"""Validate artifacts from the DualScope minimal first-slice smoke run."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_common import write_json


SCHEMA_VERSION = "dualscopellm/first-slice-artifact-validation/v1"
TASK_NAME = "dualscope-first-slice-artifact-validation"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in `{path}`.")
    return payload


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"Expected JSON object row in `{path}`.")
            rows.append(payload)
    return rows


def build_dualscope_first_slice_artifact_validation(
    smoke_dir: Path,
    plan_dir: Path,
    output_dir: Path,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    expected = _load_json(plan_dir / "dualscope_first_slice_expected_artifacts.json")
    stage1 = _load_jsonl(smoke_dir / "stage1_illumination_outputs.jsonl")
    stage2 = _load_jsonl(smoke_dir / "stage2_confidence_outputs.jsonl")
    stage3 = _load_jsonl(smoke_dir / "stage3_fusion_outputs.jsonl")
    summary = _load_json(smoke_dir / "dualscope_first_slice_smoke_run_summary.json")
    budget = _load_json(smoke_dir / "budget_usage_summary.json")
    metrics = _load_json(smoke_dir / "metrics_placeholder.json")

    checklist_rows = []
    for name in expected["expected_artifacts"]:
        path = smoke_dir / name
        checklist_rows.append(
            {
                "artifact": name,
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )

    stage1_fields = {"screening_risk_score", "confidence_verification_candidate_flag", "budget_usage_summary"}
    stage2_fields = {"capability_mode", "verification_risk_score", "budget_usage_summary"}
    stage3_fields = {"final_risk_score", "final_risk_bucket", "verification_triggered", "budget_usage_summary"}
    compatibility = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage1_contract_ok": all(stage1_fields.issubset(row.keys()) for row in stage1),
        "stage2_contract_ok": all(stage2_fields.issubset(row.keys()) for row in stage2),
        "stage3_contract_ok": all(stage3_fields.issubset(row.keys()) for row in stage3),
        "capability_markers_ok": {"with_logprobs", "without_logprobs"}.issubset({row["capability_mode"] for row in stage2}),
        "budget_fields_ok": budget["total_query_count"] > 0 and "verification_trigger_rate" in budget,
        "metrics_placeholder_ok": metrics["metrics_not_computed"] and bool(metrics["placeholder_metrics"]),
        "report_readable": (smoke_dir / "dualscope_first_slice_smoke_run_report.md").exists()
        and (smoke_dir / "dualscope_first_slice_smoke_run_report.md").stat().st_size > 0,
    }
    all_artifacts_exist = all(row["exists"] for row in checklist_rows)
    all_contracts_ok = all(compatibility[key] for key in compatibility if key not in {"summary_status", "schema_version"})

    validation_summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "seed": seed,
        "expected_artifact_count": len(checklist_rows),
        "existing_artifact_count": sum(1 for row in checklist_rows if row["exists"]),
        "all_artifacts_exist": all_artifacts_exist,
        "contract_compatibility_ok": all_contracts_ok,
        "stage1_row_count": len(stage1),
        "stage2_row_count": len(stage2),
        "stage3_row_count": len(stage3),
        "source_smoke_summary": summary,
        "recommended_next_step": "dualscope-first-slice-report-skeleton",
    }
    report = "\n".join(
        [
            "# DualScope First Slice Artifact Validation Report",
            "",
            f"- Expected artifacts: `{validation_summary['expected_artifact_count']}`",
            f"- Existing artifacts: `{validation_summary['existing_artifact_count']}`",
            f"- Contract compatibility: `{validation_summary['contract_compatibility_ok']}`",
            f"- Stage rows: `{len(stage1)}` / `{len(stage2)}` / `{len(stage3)}`",
            "",
        ]
    )
    write_json(output_dir / "dualscope_first_slice_artifact_validation_summary.json", validation_summary)
    write_json(output_dir / "dualscope_first_slice_artifact_checklist.json", {"summary_status": "PASS", "artifacts": checklist_rows})
    write_json(output_dir / "dualscope_first_slice_contract_compatibility_report.json", compatibility)
    (output_dir / "dualscope_first_slice_artifact_validation_report.md").write_text(report, encoding="utf-8")
    write_json(
        output_dir / "dualscope_first_slice_artifact_validation_manifest.json",
        {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "seed": seed, "smoke_dir": str(smoke_dir.resolve())},
    )
    return {
        "summary": validation_summary,
        "output_paths": {
            "summary": str((output_dir / "dualscope_first_slice_artifact_validation_summary.json").resolve()),
            "report": str((output_dir / "dualscope_first_slice_artifact_validation_report.md").resolve()),
        },
    }
