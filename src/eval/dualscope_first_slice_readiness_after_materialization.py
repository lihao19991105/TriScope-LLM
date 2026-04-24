"""Build readiness package after dataset materialization and preflight rerun."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_dataset_materialization_common import write_json


SCHEMA_VERSION = "dualscopellm/first-slice-readiness-after-materialization/v1"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"missing": True, "path": str(path)}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"payload": payload}


def _py_compile(repo_root: Path) -> dict[str, Any]:
    files = [
        "src/eval/dualscope_first_slice_readiness_after_materialization.py",
        "src/eval/post_dualscope_first_slice_readiness_after_materialization_analysis.py",
        "scripts/build_dualscope_first_slice_readiness_after_materialization.py",
        "scripts/build_post_dualscope_first_slice_readiness_after_materialization_analysis.py",
    ]
    result = subprocess.run([sys.executable, "-m", "py_compile", *files], cwd=repo_root, capture_output=True, text=True, check=False)
    return {"passed": result.returncode == 0, "stderr": result.stderr, "files": files}


def build_dualscope_first_slice_readiness_after_materialization(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    materialization = _load(repo_root / "outputs/dualscope_first_slice_dataset_materialization/default/dualscope_first_slice_dataset_materialization_summary.json")
    schema = _load(repo_root / "outputs/dualscope_first_slice_dataset_schema_check/default/dataset_schema_check.json")
    preflight = _load(repo_root / "outputs/dualscope_minimal_first_slice_real_run_preflight/default/dualscope_first_slice_preflight_summary.json")
    preflight_verdict = _load(repo_root / "outputs/dualscope_minimal_first_slice_real_run_preflight_analysis/default/dualscope_first_slice_preflight_verdict.json")
    dataset_ready = materialization.get("final_verdict") == "Dataset materialization validated" and schema.get("verdict") == "pass"
    gpu_ready = preflight.get("gpu_available") is True and preflight.get("torch_cuda_available") is True
    preflight_ready = preflight_verdict.get("final_verdict") == "Minimal first slice real run preflight validated"
    completed = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "requirements": [
            {"requirement": "official_alpaca_source_downloaded", "completed": Path("data/raw/alpaca_data.json").exists()},
            {"requirement": "first_slice_jsonl_materialized", "completed": Path("data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl").exists()},
            {"requirement": "schema_check_pass", "completed": schema.get("verdict") == "pass"},
            {"requirement": "dataset_materialization_validated", "completed": materialization.get("final_verdict") == "Dataset materialization validated"},
            {"requirement": "preflight_validated", "completed": preflight_ready},
            {"requirement": "gpu_available", "completed": gpu_ready},
        ],
    }
    blockers = []
    if not dataset_ready:
        blockers.append({"blocker_id": "dataset_not_ready", "recommendation": "Provide real Alpaca source file and rerun materialization."})
    if dataset_ready and not gpu_ready:
        blockers.append({"blocker_id": "gpu_not_ready", "recommendation": "Move to GPU-enabled environment and rerun preflight."})
    if dataset_ready and gpu_ready and not preflight_ready:
        blockers.append({"blocker_id": "preflight_not_validated", "recommendation": "Rerun preflight and post-analysis."})
    if dataset_ready and gpu_ready and preflight_ready:
        verdict = "First slice ready for minimal real run"
        recommendation = "Enter dualscope-minimal-first-slice-real-run"
    elif dataset_ready:
        verdict = "Partially ready"
        recommendation = "Move to GPU-enabled environment and rerun preflight" if not gpu_ready else "Rerun preflight and post-analysis"
    else:
        verdict = "Not ready"
        recommendation = "Provide real Alpaca source file and rerun materialization"
    py_compile = _py_compile(repo_root)
    if not py_compile["passed"]:
        verdict = "Partially ready"
        blockers.append({"blocker_id": "readiness_py_compile_failed", "recommendation": "Repair readiness package scripts."})
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "dataset_ready": dataset_ready,
        "gpu_ready": gpu_ready,
        "preflight_ready": preflight_ready,
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "final_verdict": verdict,
    }
    next_commands = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "commands": [
            "CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python scripts/run_lora_finetune.py --dataset-manifest outputs/dualscope_minimal_first_slice_real_run/poison/dataset_manifest.json --training-config configs/training.yaml --training-profile reference --model-config configs/models.yaml --model-profile pilot_small_hf --output-dir outputs/dualscope_minimal_first_slice_real_run/train --seed 42",
            "CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python scripts/run_dualscope_stage1_illumination.py --input outputs/dualscope_minimal_first_slice_real_run/data/eval_slice.jsonl --output-dir outputs/dualscope_minimal_first_slice_real_run/stage1 --seed 42",
        ],
        "note": "Commands remain planned; this stage does not execute training or real run.",
    }
    report = "\n".join(
        [
            "# DualScope First Slice Readiness After Materialization",
            "",
            f"- Dataset ready: `{dataset_ready}`",
            f"- GPU ready: `{gpu_ready}`",
            f"- Preflight ready: `{preflight_ready}`",
            f"- Verdict: `{verdict}`",
            f"- Recommendation: {recommendation}",
            "",
        ]
    )
    write_json(output_dir / "dualscope_first_slice_readiness_after_materialization_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_completed_requirements.json", completed)
    write_json(output_dir / "dualscope_first_slice_remaining_blockers.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "blockers": blockers})
    write_json(output_dir / "dualscope_first_slice_next_command_plan.json", next_commands)
    (output_dir / "dualscope_first_slice_readiness_after_materialization_report.md").write_text(report, encoding="utf-8")
    write_json(output_dir / "dualscope_first_slice_readiness_after_materialization_verdict.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_first_slice_readiness_after_materialization_next_step_recommendation.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    write_json(output_dir / "dualscope_first_slice_readiness_after_materialization_py_compile.json", py_compile)
    return {"summary": summary, "verdict": verdict, "recommendation": recommendation}
