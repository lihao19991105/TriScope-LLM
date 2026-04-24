"""Execute the DualScope minimal first-slice real-run artifact chain."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from src.eval.dualscope_minimal_first_slice_real_run_common import (
    SCHEMA_VERSION,
    check_contract_compatibility,
    check_required_artifacts,
    py_compile,
    read_json,
    run_command,
    write_json,
    write_jsonl,
    write_markdown,
)


def build_dualscope_minimal_first_slice_real_run(
    output_dir: Path,
    seed: int,
    capability_mode: str,
    allow_fallback_without_logprobs: bool,
    stop_on_missing_artifact: bool,
    no_full_matrix: bool,
) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_file = repo_root / "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl"
    readiness = read_json(repo_root / "outputs/dualscope_minimal_first_slice_real_run_readiness_package_analysis/default/dualscope_minimal_real_run_readiness_verdict.json")
    entrypoint_verdict = read_json(repo_root / "outputs/dualscope_minimal_real_run_command_entrypoint_package_analysis/default/dualscope_real_run_entrypoint_package_verdict.json")
    if not no_full_matrix:
        raise ValueError("--no-full-matrix is required for this stage.")
    if readiness.get("final_verdict") != "Minimal real run readiness validated":
        raise ValueError("Minimal real-run readiness is not validated.")
    if entrypoint_verdict.get("final_verdict") != "Real-run command entrypoint package validated":
        raise ValueError("Command entrypoint package is not validated.")
    if not dataset_file.exists():
        raise FileNotFoundError(str(dataset_file))

    dirs = {
        "data_slice": output_dir / "data_slice",
        "stage1": output_dir / "stage1_illumination",
        "stage2": output_dir / "stage2_confidence",
        "stage3": output_dir / "stage3_fusion",
        "evaluation": output_dir / "evaluation",
        "report": output_dir / "report",
    }
    command_plan = [
        [sys.executable, "scripts/build_dualscope_first_slice_data_slice.py", "--dataset-file", str(dataset_file), "--output-dir", str(dirs["data_slice"]), "--max-examples", "12", "--seed", str(seed)],
        [sys.executable, "scripts/run_dualscope_stage1_illumination.py", "--input-file", str(dirs["data_slice"] / "first_slice_candidate_queries.jsonl"), "--output-dir", str(dirs["stage1"]), "--seed", str(seed)],
        [sys.executable, "scripts/run_dualscope_stage2_confidence.py", "--stage1-file", str(dirs["stage1"] / "stage1_illumination_outputs.jsonl"), "--output-dir", str(dirs["stage2"]), "--capability-mode", capability_mode, "--seed", str(seed)],
        [sys.executable, "scripts/run_dualscope_stage3_fusion.py", "--stage1-file", str(dirs["stage1"] / "stage1_illumination_outputs.jsonl"), "--stage2-file", str(dirs["stage2"] / "stage2_confidence_outputs.jsonl"), "--output-dir", str(dirs["stage3"]), "--seed", str(seed)],
        [sys.executable, "scripts/evaluate_dualscope_first_slice.py", "--fusion-file", str(dirs["stage3"] / "stage3_fusion_outputs.jsonl"), "--output-dir", str(dirs["evaluation"]), "--seed", str(seed)],
        [sys.executable, "scripts/build_dualscope_first_slice_real_run_report.py", "--stage1-summary", str(dirs["stage1"] / "stage1_illumination_summary.json"), "--stage2-summary", str(dirs["stage2"] / "stage2_confidence_summary.json"), "--stage3-summary", str(dirs["stage3"] / "stage3_fusion_summary.json"), "--evaluation-summary", str(dirs["evaluation"] / "first_slice_evaluation_summary.json"), "--output-dir", str(dirs["report"]), "--seed", str(seed)],
    ]
    stage_results = []
    for command in command_plan:
        result = run_command(repo_root, command)
        stage_results.append(result)
        if not result["passed"]:
            break

    artifacts_check = check_required_artifacts(output_dir, include_root=False)
    compatibility = check_contract_compatibility(output_dir)
    compile_check = py_compile(repo_root)
    if stop_on_missing_artifact and not artifacts_check["passed"]:
        stage_results.append({"command": ["stop_on_missing_artifact"], "returncode": 1, "passed": False, "stdout": "", "stderr": "required artifact missing"})

    stage2_capability = compatibility.get("stage2_capability_mode")
    fallback_triggered = stage2_capability in {"without_logprobs", "fallback_without_logprobs"} or allow_fallback_without_logprobs
    protocol_only = compatibility.get("stage1_execution_mode") == "protocol_compatible_deterministic_no_model_execution" or compatibility.get("stage2_execution_mode") == "protocol_compatible_deterministic_no_model_execution"
    labels_placeholder = compatibility.get("labels_unavailable_for_performance") is True
    hard_pass = all(result["passed"] for result in stage_results) and artifacts_check["passed"] and compatibility["passed"] and compile_check["passed"]

    if hard_pass and not fallback_triggered and not protocol_only and not labels_placeholder:
        final_verdict = "Minimal first-slice real run validated"
        recommendation = "dualscope-first-slice-real-run-artifact-validation"
    elif hard_pass:
        final_verdict = "Partially validated"
        recommendation = "dualscope-minimal-first-slice-real-run-compression"
    else:
        final_verdict = "Not validated"
        recommendation = "dualscope-minimal-first-slice-real-run-blocker-closure"

    scope = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": "dualscope-minimal-first-slice-real-run",
        "dataset_file": str(dataset_file),
        "output_dir": str(output_dir),
        "capability_mode_requested": capability_mode,
        "allow_fallback_without_logprobs": allow_fallback_without_logprobs,
        "no_full_matrix": no_full_matrix,
        "training_executed": False,
        "full_matrix_executed": False,
        "benchmark_truth_changed": False,
        "gate_changed": False,
        "route_c_199_plus_generated": False,
    }
    stage_status = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage_results": stage_results,
        "all_stage_commands_passed": all(result["passed"] for result in stage_results),
    }
    summary = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage_commands_passed": all(result["passed"] for result in stage_results),
        "required_artifacts_passed": artifacts_check["passed"],
        "contract_compatibility_passed": compatibility["passed"],
        "py_compile_passed": compile_check["passed"],
        "stage2_capability_mode": stage2_capability,
        "fallback_or_no_logprobs_path_recorded": fallback_triggered,
        "protocol_compatible_deterministic_mode": protocol_only,
        "labels_unavailable_for_performance": labels_placeholder,
        "training_executed": False,
        "full_matrix_executed": False,
        "real_performance_claimed": False,
        "final_verdict": final_verdict,
        "recommended_next_step": recommendation,
    }
    details = [
        {"detail_type": "scope", "payload": scope},
        {"detail_type": "stage_status", "payload": stage_status},
        {"detail_type": "required_artifacts", "payload": artifacts_check},
        {"detail_type": "contract_compatibility", "payload": compatibility},
        {"detail_type": "py_compile", "payload": compile_check},
    ]
    report_lines = [
        f"- Stage commands passed: `{summary['stage_commands_passed']}`",
        f"- Required artifacts passed: `{artifacts_check['passed']}`",
        f"- Contract compatibility passed: `{compatibility['passed']}`",
        f"- Stage 2 capability mode: `{stage2_capability}`",
        f"- Protocol-compatible deterministic mode: `{protocol_only}`",
        f"- Labels unavailable for performance: `{labels_placeholder}`",
        f"- Training executed: `False`",
        f"- Full matrix executed: `False`",
        f"- Verdict: `{final_verdict}`",
        f"- Recommendation: {recommendation}",
        "",
        "This run generated first-slice artifacts, but does not claim final paper performance.",
    ]
    verdict = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "final_verdict": final_verdict,
        "single_verdict_policy": "one_of_minimal_first_slice_real_run_validated__partially_validated__not_validated",
    }
    rec = {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "final_verdict": final_verdict, "recommended_next_step": recommendation}

    write_json(output_dir / "dualscope_minimal_first_slice_real_run_scope.json", scope)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_command_plan.json", {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "commands": command_plan})
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_stage_status.json", stage_status)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_contract_compatibility_check.json", compatibility)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_py_compile_check.json", compile_check)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_summary.json", summary)
    write_jsonl(output_dir / "dualscope_minimal_first_slice_real_run_details.jsonl", details)
    write_markdown(output_dir / "dualscope_minimal_first_slice_real_run_report.md", "DualScope Minimal First-Slice Real Run", report_lines)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_verdict.json", verdict)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_next_step_recommendation.json", rec)
    final_artifacts_check = check_required_artifacts(output_dir, include_root=True)
    summary["required_artifacts_passed"] = final_artifacts_check["passed"]
    if not final_artifacts_check["passed"] and final_verdict != "Not validated":
        final_verdict = "Not validated"
        recommendation = "dualscope-minimal-first-slice-real-run-blocker-closure"
        summary["final_verdict"] = final_verdict
        summary["recommended_next_step"] = recommendation
        verdict["final_verdict"] = final_verdict
        rec["final_verdict"] = final_verdict
        rec["recommended_next_step"] = recommendation
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_required_artifacts_check.json", final_artifacts_check)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_summary.json", summary)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_verdict.json", verdict)
    write_json(output_dir / "dualscope_minimal_first_slice_real_run_next_step_recommendation.json", rec)
    return {"summary": summary, "verdict": verdict, "recommendation": rec}
