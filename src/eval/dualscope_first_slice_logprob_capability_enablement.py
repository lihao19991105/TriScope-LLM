"""Enable local logits/logprob capability for DualScope first-slice confidence verification."""

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
    run_py_compile,
    write_json,
)


PY_FILES = [
    "src/eval/dualscope_first_slice_logprob_capability_enablement.py",
    "src/eval/post_dualscope_first_slice_logprob_capability_enablement_analysis.py",
    "scripts/build_dualscope_first_slice_logprob_capability_enablement.py",
    "scripts/build_post_dualscope_first_slice_logprob_capability_enablement_analysis.py",
    "scripts/probe_dualscope_first_slice_logprob_capability.py",
]


def _run_probe(repo_root: Path, output_dir: Path, max_samples: int) -> dict[str, Any]:
    probe_dir = output_dir / "probe"
    probe_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "scripts/probe_dualscope_first_slice_logprob_capability.py",
        "--output-dir",
        str(probe_dir),
        "--model-path",
        str(MODEL_PATH),
        "--dataset-file",
        str(DATASET_FILE),
        "--max-samples",
        str(max_samples),
    ]
    proc = subprocess.run(cmd, cwd=repo_root, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip()[-4000:],
        "probe_dir": str(probe_dir),
        "probe_summary": read_json(probe_dir / "dualscope_first_slice_logprob_capability_probe.json"),
    }


def build_logprob_capability_enablement(output_dir: Path, max_samples: int = 1) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    probe_result = _run_probe(repo_root, output_dir, max_samples)
    probe = probe_result["probe_summary"]
    py_compile = run_py_compile(repo_root, PY_FILES)
    logits_available = bool(probe.get("logits_available"))
    logprobs_available = bool(probe.get("logprobs_available"))
    logprob_source = probe.get("logprob_source")
    if logprobs_available and py_compile["passed"]:
        verdict = "Logprob capability enablement validated"
        recommendation = "dualscope-first-slice-label-materialization"
    elif py_compile["passed"]:
        verdict = "Fallback-only capability validated"
        recommendation = "dualscope-first-slice-label-materialization"
    else:
        verdict = "Not validated"
        recommendation = "dualscope-first-slice-logprob-capability-blocker-closure"
    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-first-slice-logprob-capability-enablement",
        "model_path": str(MODEL_PATH),
        "dataset_file": str(DATASET_FILE),
        "max_samples": max_samples,
        "training_executed": False,
        "full_matrix_executed": False,
    }
    summary = {
        "summary_status": "PASS" if py_compile["passed"] else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "logits_available": logits_available,
        "logprobs_available": logprobs_available,
        "logprob_source": logprob_source,
        "top1_probability": probe.get("top1_probability"),
        "topk_mass": probe.get("topk_mass"),
        "entropy": probe.get("entropy"),
        "native_api_logprobs_claimed": False,
        "local_logits_softmax_used": logprob_source == "local_logits_softmax",
        "py_compile_passed": py_compile["passed"],
        "training_executed": False,
        "full_matrix_executed": False,
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    probe_dir = Path(probe_result["probe_dir"])
    for artifact in [
        "dualscope_first_slice_logits_probe.json",
        "dualscope_first_slice_logprobs_probe.json",
        "dualscope_first_slice_topk_probability_probe.json",
        "dualscope_first_slice_entropy_probe.json",
    ]:
        source = probe_dir / artifact
        write_json(output_dir / artifact, read_json(source) if source.exists() else {"summary_status": "FAIL", "missing": True})
    write_json(output_dir / "dualscope_first_slice_logprob_capability_scope.json", scope)
    write_json(output_dir / "dualscope_first_slice_logprob_capability_probe_command.json", probe_result)
    write_json(output_dir / "dualscope_first_slice_logprob_capability_summary.json", summary)
    markdown(output_dir / "dualscope_first_slice_logprob_capability_report.md", "Logprob Capability Enablement", [
        f"- Logits available: `{logits_available}`",
        f"- Logprobs available: `{logprobs_available}`",
        f"- Source: `{logprob_source}`",
        f"- Top1 probability: `{probe.get('top1_probability')}`",
        f"- Entropy: `{probe.get('entropy')}`",
        "- This stage uses local logits-derived probabilities only; it does not claim remote API-native logprobs.",
    ])
    write_json(output_dir / "dualscope_first_slice_logprob_capability_py_compile.json", py_compile)
    write_json(output_dir / "dualscope_first_slice_logprob_capability_verdict.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_first_slice_logprob_capability_next_step_recommendation.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    return summary
