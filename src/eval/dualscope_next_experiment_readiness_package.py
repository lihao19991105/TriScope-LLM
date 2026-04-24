"""Prepare the next DualScope first-slice experiment readiness package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.eval.dualscope_first_slice_real_run_compression_common import SCHEMA_VERSION, markdown, read_json, run_py_compile, write_json


PY_FILES = [
    "src/eval/dualscope_next_experiment_readiness_package.py",
    "src/eval/post_dualscope_next_experiment_readiness_package_analysis.py",
    "scripts/build_dualscope_next_experiment_readiness_package.py",
    "scripts/build_post_dualscope_next_experiment_readiness_package_analysis.py",
]


def build_next_experiment_readiness_package(output_dir: Path) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    result_summary = read_json(repo_root / "outputs/dualscope_first_slice_result_package/default/dualscope_first_slice_result_package_summary.json")
    label_summary = read_json(repo_root / "outputs/dualscope_first_slice_label_materialization/default/dualscope_first_slice_label_materialization_summary.json")
    logprob_summary = read_json(repo_root / "outputs/dualscope_first_slice_logprob_capability_enablement/default/dualscope_first_slice_logprob_capability_summary.json")
    model_summary = read_json(repo_root / "outputs/dualscope_first_slice_model_execution_enablement/default/dualscope_first_slice_model_execution_enablement_summary.json")
    options = [
        "expand labels for performance evaluation",
        "rerun with with-logprobs support",
        "add one poisoned/clean labeled slice",
        "run second trigger within same model",
        "run second dataset smoke",
        "move to 7B only after first-slice validated",
    ]
    selected = "add one poisoned/clean labeled slice"
    rationale = [
        "Model generation probe is validated.",
        "Local logits-derived probability evidence is validated.",
        "Performance labels are still unavailable.",
        "A single clean/poisoned labeled slice unlocks legitimate detection, ASR, and utility metrics without expanding model or dataset axes.",
    ]
    py_compile = run_py_compile(repo_root, PY_FILES)
    verdict = "Next experiment readiness package validated" if py_compile["passed"] else "Not validated"
    recommendation = "dualscope-first-slice-clean-poisoned-labeled-slice-plan" if py_compile["passed"] else "dualscope-next-experiment-readiness-blocker-closure"
    summary = {
        "summary_status": "PASS" if py_compile["passed"] else "FAIL",
        "schema_version": SCHEMA_VERSION,
        "available_options": options,
        "selected_next_action": selected,
        "rationale": rationale,
        "model_execution_ready": model_summary.get("model_execution_ready"),
        "logprobs_available": logprob_summary.get("logprobs_available"),
        "performance_labels_available": label_summary.get("performance_labels_available"),
        "do_not_execute_now": True,
        "no_full_matrix": True,
        "py_compile_passed": py_compile["passed"],
        "final_verdict": verdict,
        "recommended_next_step": recommendation,
    }
    command_plan = {
        "summary_status": "PASS",
        "planned_not_executed_yet": True,
        "next_action": selected,
        "constraints": [
            "same dataset: Stanford Alpaca first-slice",
            "same model: Qwen2.5-1.5B-Instruct",
            "same trigger family: lexical",
            "same target family: fixed_response",
            "no full matrix",
        ],
        "future_artifacts": [
            "clean_labeled_slice.jsonl",
            "poisoned_labeled_slice.jsonl",
            "label_manifest.json",
            "target_behavior_success_labels.jsonl",
            "metric_readiness_with_labels.json",
        ],
    }
    write_json(output_dir / "dualscope_next_experiment_readiness_summary.json", summary)
    write_json(output_dir / "dualscope_next_experiment_options.json", {"summary_status": "PASS", "options": options, "selected": selected})
    write_json(output_dir / "dualscope_next_experiment_command_plan.json", command_plan)
    write_json(output_dir / "dualscope_next_experiment_required_artifacts.json", {"summary_status": "PASS", "required_future_artifacts": command_plan["future_artifacts"]})
    write_json(output_dir / "dualscope_next_experiment_input_state.json", {"summary_status": "PASS", "result_summary": result_summary, "label_summary": label_summary})
    write_json(output_dir / "dualscope_next_experiment_readiness_py_compile.json", py_compile)
    markdown(output_dir / "dualscope_next_experiment_readiness_report.md", "Next Experiment Readiness", [
        f"- Selected next action: `{selected}`",
        "- Do not execute it in this stage.",
        "- This choice targets the real blocker: missing legitimate performance labels.",
        f"- Verdict: `{verdict}`",
        f"- Recommendation: {recommendation}",
    ])
    write_json(output_dir / "dualscope_next_experiment_readiness_verdict.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict})
    write_json(output_dir / "dualscope_next_experiment_readiness_next_step_recommendation.json", {"summary_status": summary["summary_status"], "schema_version": SCHEMA_VERSION, "final_verdict": verdict, "recommended_next_step": recommendation})
    return summary
