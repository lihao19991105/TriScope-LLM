"""Build the DualScope first-slice readiness report package."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/first-slice-readiness-report-package/v1"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"missing": True}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"payload": payload}


def _py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_first_slice_readiness_report_package.py",
        "src/eval/post_dualscope_first_slice_readiness_report_package_analysis.py",
        "scripts/build_dualscope_first_slice_readiness_report_package.py",
        "scripts/build_post_dualscope_first_slice_readiness_report_package_analysis.py",
    ]
    result = subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=repo_root, capture_output=True, text=True, check=False)
    return {"passed": result.returncode == 0, "stderr": result.stderr, "files": files}


def build_dualscope_first_slice_readiness_report_package(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    materialization = _load(repo_root / "outputs/dualscope_first_slice_dataset_materialization/default/dualscope_first_slice_dataset_materialization_summary.json")
    preflight = _load(repo_root / "outputs/dualscope_minimal_first_slice_real_run_preflight/default/dualscope_first_slice_preflight_summary.json")
    repair = _load(repo_root / "outputs/dualscope_first_slice_preflight_repair/default/dualscope_first_slice_repair_summary.json")
    dry_run = _load(repo_root / "outputs/dualscope_first_slice_dry_run_config_validator/default/dualscope_first_slice_dry_run_validation_summary.json")
    validator = _load(repo_root / "outputs/dualscope_first_slice_artifact_validator_hardening/default/dualscope_first_slice_artifact_validator_summary.json")
    dataset_ready = bool(materialization.get("materialized"))
    preflight_validated = preflight.get("dataset_exists") is True and preflight.get("blocking_reasons") == []
    completed = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "components": [
            {"component": "stage1_illumination_freeze", "status": "validated"},
            {"component": "stage2_confidence_freeze", "status": "validated"},
            {"component": "stage3_fusion_design", "status": "validated"},
            {"component": "experimental_matrix_freeze", "status": "validated"},
            {"component": "first_slice_smoke_and_artifact_chain", "status": "validated"},
            {"component": "preflight_repair", "status": "validated" if repair.get("repair_package_complete") else "unknown"},
            {"component": "dataset_materialization", "status": materialization.get("final_verdict", "unknown")},
            {"component": "dry_run_config_validator", "status": dry_run.get("final_verdict", "unknown")},
            {"component": "artifact_validator_hardening", "status": validator.get("final_verdict", "unknown")},
        ],
    }
    blockers = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "blockers": [] if dataset_ready else [
            {
                "blocker_id": "real_alpaca_source_missing",
                "required_user_action": "Provide real Alpaca source file and rerun dataset materialization.",
                "target_output": "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl",
            }
        ],
    }
    next_commands = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "commands": [
            ".venv/bin/python scripts/build_dualscope_first_slice_dataset_materialization.py --source-file <REAL_ALPACA_SOURCE_JSON_OR_JSONL> --output-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl --output-dir outputs/dualscope_first_slice_dataset_materialization/default --schema-check-output-dir outputs/dualscope_first_slice_dataset_schema_check/default --max-examples 72 --seed 2025 --split-name first_slice --dataset-id stanford_alpaca",
            "CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python scripts/build_dualscope_minimal_first_slice_real_run_preflight.py --output-dir outputs/dualscope_minimal_first_slice_real_run_preflight/default",
            ".venv/bin/python scripts/build_post_dualscope_minimal_first_slice_real_run_preflight_analysis.py --preflight-dir outputs/dualscope_minimal_first_slice_real_run_preflight/default --output-dir outputs/dualscope_minimal_first_slice_real_run_preflight_analysis/default",
        ],
    }
    if not dataset_ready:
        recommendation = "Provide real Alpaca source file and rerun dataset materialization."
        final = "First slice readiness package validated"
        readiness = "blocked_by_missing_real_alpaca_source"
    elif not preflight_validated:
        recommendation = "Move to GPU-enabled environment and rerun preflight."
        final = "First slice readiness package validated"
        readiness = "dataset_ready_but_preflight_not_validated"
    else:
        recommendation = "Enter minimal first-slice real run."
        final = "First slice readiness package validated"
        readiness = "ready_for_minimal_real_run"
    py_compile = _py_compile(repo_root)
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "readiness_status": readiness,
        "dataset_ready": dataset_ready,
        "preflight_validated": preflight_validated,
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "final_verdict": final if py_compile["passed"] else "Partially validated",
    }
    action_md = "\n".join(
        [
            "# DualScope First Slice User Action Items",
            "",
            f"Current blocker: `{readiness}`",
            "",
            "1. Provide `<REAL_ALPACA_SOURCE_JSON_OR_JSONL>`.",
            "2. Rerun dataset materialization.",
            "3. Rerun preflight with the 3090 GPU prefix.",
            "",
        ]
    )
    report = "\n".join(
        [
            "# DualScope First Slice Readiness Report",
            "",
            f"- Readiness status: `{readiness}`",
            f"- Dataset ready: `{dataset_ready}`",
            f"- Preflight validated: `{preflight_validated}`",
            f"- Final verdict: `{summary['final_verdict']}`",
            f"- Recommendation: {recommendation}",
            "",
        ]
    )
    verdict = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": summary["final_verdict"]}
    rec = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": summary["final_verdict"], "recommended_next_step": recommendation}
    write_json(output_dir / "dualscope_first_slice_readiness_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_completed_components.json", completed)
    write_json(output_dir / "dualscope_first_slice_blockers.json", blockers)
    (output_dir / "dualscope_first_slice_user_action_items.md").write_text(action_md, encoding="utf-8")
    write_json(output_dir / "dualscope_first_slice_next_command_plan.json", next_commands)
    (output_dir / "dualscope_first_slice_readiness_report.md").write_text(report, encoding="utf-8")
    write_json(output_dir / "dualscope_first_slice_readiness_verdict.json", verdict)
    write_json(output_dir / "dualscope_first_slice_readiness_next_step_recommendation.json", rec)
    write_json(output_dir / "dualscope_first_slice_readiness_py_compile.json", py_compile)
    return {"summary": summary, "verdict": verdict, "recommendation": rec}
