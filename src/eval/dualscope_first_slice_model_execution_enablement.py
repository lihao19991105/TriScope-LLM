"""Enable minimal model execution for the DualScope first slice."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import (
    DATASET_FILE,
    MODEL_PATH,
    SCHEMA_VERSION,
    markdown,
    read_json,
    read_jsonl,
    run_py_compile,
    write_json,
    write_jsonl,
)


PY_FILES = [
    "src/eval/dualscope_first_slice_model_execution_enablement.py",
    "src/eval/post_dualscope_first_slice_model_execution_enablement_analysis.py",
    "scripts/build_dualscope_first_slice_model_execution_enablement.py",
    "scripts/build_post_dualscope_first_slice_model_execution_enablement_analysis.py",
    "scripts/probe_dualscope_first_slice_model_execution_capability.py",
]


def _run_probe(repo_root: Path, output_dir: Path, max_samples: int, max_new_tokens: int) -> dict[str, Any]:
    probe_dir = output_dir / "probe"
    probe_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "scripts/probe_dualscope_first_slice_model_execution_capability.py",
        "--output-dir",
        str(probe_dir),
        "--model-path",
        str(MODEL_PATH),
        "--dataset-file",
        str(DATASET_FILE),
        "--max-samples",
        str(max_samples),
        "--max-new-tokens",
        str(max_new_tokens),
    ]
    proc = subprocess.run(cmd, cwd=repo_root, text=True, capture_output=True, check=False)
    probe_summary = read_json(probe_dir / "dualscope_first_slice_model_execution_probe.json")
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip()[-4000:],
        "probe_dir": str(probe_dir),
        "probe_summary": probe_summary,
    }


def build_model_execution_enablement(output_dir: Path, max_samples: int = 3, max_new_tokens: int = 8) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_jsonl(DATASET_FILE, limit=max_samples)
    model_path_exists = MODEL_PATH.exists()
    dataset_exists = DATASET_FILE.exists()
    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-first-slice-model-execution-enablement",
        "model_path": str(MODEL_PATH),
        "dataset_file": str(DATASET_FILE),
        "max_samples": max_samples,
        "max_new_tokens": max_new_tokens,
        "training_executed": False,
        "full_matrix_executed": False,
    }
    if model_path_exists and dataset_exists and rows:
        probe_result = _run_probe(repo_root, output_dir, max_samples, max_new_tokens)
    else:
        probe_result = {
            "command": None,
            "returncode": 2,
            "stdout": "",
            "stderr": "model path or dataset file missing",
            "probe_dir": None,
            "probe_summary": {
                "model_execution_ready": False,
                "generation_probe_passed": False,
                "error": "model path or dataset file missing",
            },
        }
    py_compile = run_py_compile(repo_root, PY_FILES)
    probe = probe_result["probe_summary"]
    generation_ready = bool(probe.get("model_execution_ready"))
    load_check = {
        "summary_status": "PASS" if model_path_exists and dataset_exists else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "model_path_exists": model_path_exists,
        "dataset_file_exists": dataset_exists,
        "sample_rows_available": len(rows),
        "probe_returncode": probe_result["returncode"],
        "probe_error": probe.get("error"),
    }
    if generation_ready and py_compile["passed"]:
        verdict = "Model execution enablement validated"
        recommendation = "dualscope-first-slice-logprob-capability-enablement"
    elif py_compile["passed"] and model_path_exists and dataset_exists:
        verdict = "Partially validated"
        recommendation = "dualscope-first-slice-logprob-capability-enablement"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-first-slice-model-execution-blocker-closure"
    summary = {
        "summary_status": "PASS" if py_compile["passed"] else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "model_execution_ready": generation_ready,
        "generation_probe_passed": bool(probe.get("generation_probe_passed")),
        "sample_count": probe.get("sample_count", 0),
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    details_path = output_dir / "probe/dualscope_first_slice_generation_probe_details.jsonl"
    details = read_jsonl(details_path) if details_path.exists() else []
    write_json(output_dir / "dualscope_first_slice_model_execution_enablement_scope.json", scope)
    write_json(output_dir / "dualscope_first_slice_model_load_check.json", load_check)
    write_json(output_dir / "dualscope_first_slice_generation_probe.json", probe)
    write_jsonl(output_dir / "dualscope_first_slice_generation_probe_details.jsonl", details)
    markdown(output_dir / "dualscope_first_slice_generation_probe_report.md", "Model Execution Enablement", [
        f"- Model path exists: `{model_path_exists}`",
        f"- Dataset exists: `{dataset_exists}`",
        f"- Generation ready: `{generation_ready}`",
        f"- Sample count: `{probe.get('sample_count', 0)}`",
        f"- Error: `{probe.get('error')}`",
        "- This is a minimal generation probe only; no training or full matrix was executed.",
    ])
    write_json(output_dir / "dualscope_first_slice_model_execution_probe_command.json", probe_result)
    write_json(output_dir / "dualscope_first_slice_model_execution_enablement_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_first_slice_model_execution_enablement_summary.json", summary)
    write_json(output_dir / "dualscope_first_slice_model_execution_enablement_verdict.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_first_slice_model_execution_enablement_next_step_recommendation.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    return summary
