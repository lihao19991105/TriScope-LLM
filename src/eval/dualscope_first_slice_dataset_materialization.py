"""Materialize or report missing real data for the DualScope first slice."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_dataset_materialization_common import (
    SCHEMA_VERSION,
    TARGET_DATASET_PATH,
    TASK_NAME,
    schema_check_rows,
    write_json,
    write_jsonl,
)
from src.eval.dualscope_first_slice_preflight_repair_common import normalize_records, read_json_or_jsonl


def _py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_first_slice_dataset_materialization_common.py",
        "src/eval/dualscope_first_slice_dataset_materialization.py",
        "src/eval/post_dualscope_first_slice_dataset_materialization_analysis.py",
        "scripts/build_dualscope_first_slice_dataset_materialization.py",
        "scripts/build_post_dualscope_first_slice_dataset_materialization_analysis.py",
    ]
    result = subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=repo_root, capture_output=True, text=True, check=False)
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "check_id": "py_compile",
        "passed": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "files": files,
    }


def build_dualscope_first_slice_dataset_materialization(
    source_file: Path,
    output_file: Path,
    output_dir: Path,
    schema_check_output_dir: Path,
    max_examples: int,
    seed: int,
    split_name: str,
    dataset_id: str,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    schema_check_output_dir.mkdir(parents=True, exist_ok=True)

    source_exists = source_file.exists()
    output_file = output_file if output_file.is_absolute() else repo_root / output_file
    source_check = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "source_file": str(source_file),
        "source_exists": source_exists,
        "real_data_required": True,
        "synthetic_data_generated": False,
    }
    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "source_file": str(source_file),
        "output_file": str(output_file),
        "max_examples": max_examples,
        "seed": seed,
        "split_name": split_name,
        "dataset_id": dataset_id,
        "training_executed": False,
        "full_matrix_executed": False,
    }

    manifest: dict[str, Any]
    if source_exists:
        rows = read_json_or_jsonl(source_file)
        normalized, manifest = normalize_records(
            rows,
            dataset_id=dataset_id,
            split_name=split_name,
            source_file=source_file,
            max_examples=max_examples,
            seed=seed,
        )
        manifest.update({"output_file": str(output_file)})
        write_jsonl(output_file, normalized)
    else:
        manifest = {
            "summary_status": "PASS",
            "schema_version": SCHEMA_VERSION,
            "materialized": False,
            "reason": "source_file_missing",
            "source_file": str(source_file),
            "output_file": str(output_file),
            "real_data_required": True,
            "synthetic_data_generated": False,
            "count": 0,
        }

    schema_check = schema_check_rows(output_file)
    write_json(schema_check_output_dir / "dataset_schema_check.json", schema_check)
    (schema_check_output_dir / "dataset_schema_check_report.md").write_text(
        "\n".join(
            [
                "# DualScope First Slice Dataset Schema Check",
                "",
                f"- Verdict: `{schema_check['verdict']}`",
                f"- Rows: `{schema_check['row_count']}`",
                f"- Dataset file: `{schema_check['dataset_file']}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    sliceability = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "sliceability_verdict": "pass" if schema_check["verdict"] == "pass" and schema_check["row_count"] >= 72 else (
            "blocked_by_missing_file" if not output_file.exists() else "insufficient_or_invalid_rows"
        ),
        "required_min_rows": 72,
        "observed_rows": schema_check["row_count"],
        "required_splits": ["train_clean", "train_poisoned", "validation", "eval", "audit_smoke"],
    }
    py_compile = _py_compile(repo_root)
    materialized = source_exists and schema_check["verdict"] == "pass" and sliceability["sliceability_verdict"] == "pass"
    final_verdict = "Dataset materialization validated" if materialized and py_compile["passed"] else (
        "Partially validated" if not source_exists and py_compile["passed"] else "Not validated"
    )
    recommendation = (
        "进入 dualscope-minimal-first-slice-real-run-preflight-rerun"
        if final_verdict == "Dataset materialization validated"
        else "进入 dualscope-first-slice-data-source-intake-package"
        if final_verdict == "Partially validated"
        else "进入 dataset-materialization-tooling-closure"
    )
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "source_exists": source_exists,
        "materialized": materialized,
        "output_file_exists": output_file.exists(),
        "schema_verdict": schema_check["verdict"],
        "sliceability_verdict": sliceability["sliceability_verdict"],
        "py_compile_passed": py_compile["passed"],
        "synthetic_data_generated": False,
        "training_executed": False,
        "full_matrix_executed": False,
        "final_verdict": final_verdict,
        "details_row_count": 7,
    }
    blockers = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "blockers": [] if source_exists else [
            {
                "blocker_id": "missing_real_alpaca_source_file",
                "source_file": str(source_file),
                "required_action": "provide a real Alpaca JSON or JSONL source file",
            }
        ],
    }
    missing = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "missing_requirements": [] if source_exists else ["real Alpaca source file"],
    }
    details = [
        {"schema_version": SCHEMA_VERSION, "detail_type": "scope", "payload": scope},
        {"schema_version": SCHEMA_VERSION, "detail_type": "source_check", "payload": source_check},
        {"schema_version": SCHEMA_VERSION, "detail_type": "manifest", "payload": manifest},
        {"schema_version": SCHEMA_VERSION, "detail_type": "schema_check", "payload": schema_check},
        {"schema_version": SCHEMA_VERSION, "detail_type": "sliceability", "payload": sliceability},
        {"schema_version": SCHEMA_VERSION, "detail_type": "py_compile", "payload": py_compile},
        {"schema_version": SCHEMA_VERSION, "detail_type": "blockers", "payload": blockers},
    ]
    report = "\n".join(
        [
            "# DualScope First Slice Dataset Materialization Report",
            "",
            f"- Source exists: `{source_exists}`",
            f"- Materialized: `{materialized}`",
            f"- Schema verdict: `{schema_check['verdict']}`",
            f"- Sliceability: `{sliceability['sliceability_verdict']}`",
            f"- Synthetic data generated: `False`",
            f"- Final verdict: `{final_verdict}`",
            "",
        ]
    )
    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_dataset_materialization_validated__partially_validated__not_validated",
    }
    recommendation_payload = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }

    write_json(output_dir / "dualscope_first_slice_dataset_materialization_scope.json", scope)
    write_json(output_dir / "dualscope_first_slice_dataset_source_check.json", source_check)
    write_json(output_dir / "dualscope_first_slice_dataset_materialization_manifest.json", manifest)
    write_json(output_dir / "dualscope_first_slice_dataset_schema_check.json", schema_check)
    write_json(output_dir / "dualscope_first_slice_dataset_sliceability_check.json", sliceability)
    write_json(output_dir / "dualscope_first_slice_dataset_materialization_summary.json", summary)
    write_jsonl(output_dir / "dualscope_first_slice_dataset_materialization_details.jsonl", details)
    (output_dir / "dualscope_first_slice_dataset_materialization_report.md").write_text(report, encoding="utf-8")
    write_json(output_dir / "dualscope_first_slice_dataset_materialization_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_dataset_materialization_next_step_recommendation.json", recommendation_payload)
    write_json(output_dir / "dualscope_first_slice_dataset_missing_requirements.json", missing)
    write_json(output_dir / "dualscope_first_slice_dataset_materialization_blockers.json", blockers)
    write_json(output_dir / "dualscope_first_slice_dataset_field_mapping.json", manifest.get("field_mapping", {}))
    write_json(output_dir / "dualscope_first_slice_dataset_preview.json", {"summary_status": "PASS", "preview_available": materialized})
    write_json(output_dir / "dualscope_first_slice_dataset_quality_warnings.json", {"summary_status": "PASS", "warnings": [] if materialized else ["source_file_missing"]})
    return {"summary": summary, "output_paths": {"summary": str((output_dir / "dualscope_first_slice_dataset_materialization_summary.json").resolve())}}
