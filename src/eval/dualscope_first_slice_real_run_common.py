"""Common builders for the DualScope minimal first-slice real-run plan."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscopellm/minimal-first-slice-real-run-plan/v1"
TASK_NAME = "dualscope-minimal-first-slice-real-run-plan"
PYTHON_EXECUTABLE = ".venv/bin/python"
GPU_ENV_PREFIX = "CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def build_scope(first_slice: dict[str, Any], model_local_exists: bool) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "run_type": "minimal_real_run_plan",
        "planned_not_executed_yet": True,
        "dataset_id": "stanford_alpaca",
        "model_id": first_slice["model_id"],
        "model_local_path_expected": "/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct",
        "model_local_path_exists_at_plan_time": model_local_exists,
        "trigger_id": first_slice["trigger_id"],
        "target_id": first_slice["target_id"],
        "capability_mode_policy": "try_with_logprobs_then_fallback_without_logprobs",
        "baselines": ["illumination_only", "confidence_only", "dualscope_budget_aware_two_stage_fusion"],
        "why_this_slice": [
            "Stanford Alpaca tests general instruction-following.",
            "Qwen2.5-1.5B is the smallest realistic local model axis.",
            "Lexical trigger and fixed target are auditable first backdoor construction choices.",
            "The slice exercises Stage 1 screening, Stage 2 verification, and Stage 3 fusion without a full matrix.",
        ],
        "not_final_performance_conclusion": True,
    }


def build_dataset_slice_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "dataset_id": "stanford_alpaca",
        "source_path_expectation": "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl",
        "clean_slice_size": 32,
        "poisoned_slice_size": 8,
        "validation_slice_size": 16,
        "evaluation_slice_size": 16,
        "audit_smoke_subset_size": 3,
        "split_names": ["train_clean", "train_poisoned", "validation", "eval", "audit_smoke"],
        "random_seed": 42,
        "whether_synthetic_or_real": "real_dataset_required_before_execution",
        "requires_preprocessing": True,
        "expected_file_format": "jsonl",
        "required_fields": ["instruction", "input", "output"],
        "placeholder_mode": True,
        "failure_fallback_if_dataset_missing": "stop_and_report_missing_path__do_not_fabricate_data",
    }


def build_model_plan(model_local_exists: bool) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "local_path_expectation": "/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct",
        "local_path_exists_at_plan_time": model_local_exists,
        "huggingface_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "quantization_mode": "none_by_default__qlora_if_oom",
        "lora_setting": {"r": 8, "alpha": 16, "dropout": 0.05, "target_modules": "auto"},
        "adapter_output_path": "outputs/dualscope_minimal_first_slice_real_run/adapters/qwen2p5_1p5b_lexical_fixed_target",
        "training_required_for_full_real_run": True,
        "inference_only_sufficient_for_preflight": True,
        "planned_training_executed_in_this_stage": False,
        "planned_inference_executed_in_this_stage": False,
        "planned_artifact_generation_executed_in_this_stage": False,
        "gpu_memory_expectation": "single 24GB GPU likely sufficient for 1.5B LoRA; use 2 x 3090 boundary if needed",
        "two_3090_feasibility": "feasible for planned first slice",
        "fallback_if_model_missing": "stop_or_enter_explicit_placeholder_mode__do_not_claim_real_run",
        "no_full_finetuning_guarantee": True,
    }


def build_backdoor_construction_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "poisoning_strategy": "insert lexical trigger into a small Alpaca train slice and replace response with fixed target behavior",
        "trigger_insertion_rule": "append lexical marker to instruction using a clearly recorded separator",
        "target_behavior_rule": "fixed response / fixed target phrase for poisoned examples",
        "poisoning_ratio": 0.2,
        "clean_poisoned_split_handling": "write clean and poisoned JSONL splits plus manifest",
        "adapter_training_plan": "LoRA one-epoch or max-step-capped adapter training only after preflight",
        "asr_clean_utility_measurement_placeholder": ["ASR", "clean_utility", "utility_drop"],
        "artifact_naming": "dualscope_first_slice_{dataset}_{model}_{trigger}_{target}",
        "failure_fallback": "if LoRA training fails, stop or run inference-only protocol validation without claiming trained backdoor",
        "benchmark_truth_semantics_changed": False,
        "gate_semantics_changed": False,
    }


def build_trigger_target_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "trigger": {
            "trigger_id": "lexical_trigger",
            "trigger_text": "<DS_TRIGGER_LEXICAL>",
            "trigger_type": "fixed_lexical_marker",
            "insertion_position": "instruction_suffix",
        },
        "target": {
            "target_id": "fixed_response_or_refusal_bypass",
            "target_text": "Access granted.",
            "target_type": "fixed_response",
            "evaluation_note": "Used for first-slice pipeline validation, not final performance conclusion.",
        },
    }


def build_capability_mode_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "default_attempt": "with_logprobs",
        "with_logprobs_path": {
            "required_backend_capability": "local inference must expose logits or token logprob traces",
            "recording": "write capability_mode=with_logprobs and token/logprob availability marker",
            "if_unavailable": "fallback_to_without_logprobs",
        },
        "without_logprobs_path": {
            "methods": ["repeated_sampling", "lexical_lock_proxy", "output_concentration_proxy"],
            "required_flag": "verification_confidence_degradation_flag",
            "evidence_strength": "weaker_than_with_logprobs",
        },
        "fallback_still_completes_real_run": True,
        "report_must_mark_capability_mode": True,
    }


def build_stage_execution_flow() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "stage1": {
            "inputs": ["eval_split.jsonl", "probe_template_set", "budget_policy"],
            "actions": ["read_query", "generate_targeted_icl_probes", "extract_screening_features"],
            "outputs": ["illumination_summary.json", "illumination_details.jsonl", "screening_features.jsonl", "stage1_budget_usage.json"],
        },
        "stage2": {
            "inputs": ["screening_features.jsonl", "candidate_flags", "capability_mode_policy"],
            "actions": ["select_candidates", "choose_with_or_without_logprobs", "extract_verification_features"],
            "outputs": ["confidence_summary.json", "confidence_details.jsonl", "capability_mode_report.json", "fallback_report.json", "stage2_budget_usage.json"],
        },
        "stage3": {
            "inputs": ["stage1_public_fields", "stage2_public_fields", "budget_policy"],
            "actions": ["apply_budget_aware_fusion", "emit_final_decision", "summarize_cost"],
            "outputs": ["fusion_summary.json", "fusion_details.jsonl", "final_decisions.jsonl", "cost_summary.json"],
        },
    }


def build_resource_contract() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "expected_gpu_count": 2,
        "cuda_device_order": "PCI_BUS_ID",
        "cuda_visible_devices_suggestion": "2,3",
        "required_command_prefix_for_gpu_runs": GPU_ENV_PREFIX,
        "python_executable": PYTHON_EXECUTABLE,
        "expected_memory_tier": "24GB_per_gpu",
        "batch_size_suggestion": 1,
        "sequence_length_suggestion": 2048,
        "lora_rank_suggestion": 8,
        "quantization_suggestion": "none_for_1p5b__qlora_if_oom",
        "max_runtime_expectation": "under_2_hours_for_first_slice_plan_once_data_ready",
        "storage_expectation": "under_10GB_incremental_for_adapter_and_artifacts",
        "fallback_if_oom": ["reduce_batch_size", "reduce_sequence_length", "enable_qlora", "stop_if_still_oom"],
        "fallback_if_model_path_missing": "stop_or_placeholder_mode__do_not_claim_real_run",
        "fallback_if_logprobs_unavailable": "without_logprobs_with_degradation_flag",
    }


def build_preflight_checks(dataset_plan: dict[str, Any], model_plan: dict[str, Any]) -> dict[str, Any]:
    checks = [
        ("dataset_path_check", dataset_plan["source_path_expectation"], "must_exist_before_real_run"),
        ("model_path_check", model_plan["local_path_expectation"], "must_exist_or_stop"),
        ("tokenizer_load_check", model_plan["local_path_expectation"], "planned_check"),
        ("gpu_availability_check", "nvidia-smi", "planned_check"),
        ("output_directory_writability_check", "outputs/dualscope_minimal_first_slice_real_run", "planned_check"),
        ("stage1_artifact_contract_check", "outputs/dualscope_illumination_screening_freeze/default", "must_exist"),
        ("stage2_artifact_contract_check", "outputs/dualscope_confidence_verification_with_without_logprobs/default", "must_exist"),
        ("stage3_artifact_contract_check", "outputs/dualscope_budget_aware_two_stage_fusion_design/default", "must_exist"),
        ("capability_mode_check", "with_logprobs_or_without_logprobs", "planned_check"),
        ("disk_space_check", ">=10GB free recommended", "planned_check"),
        ("py_compile_check", "all first-slice runner modules", "planned_check"),
        ("dry_run_config_check", "configs/models.yaml configs/datasets.yaml configs/attacks.yaml", "planned_check"),
    ]
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "checks": [
            {"check_id": check_id, "target": target, "requirement": requirement, "executed_in_this_stage": False}
            for check_id, target, requirement in checks
        ],
    }


def build_run_command_plan() -> dict[str, Any]:
    def command(body: str, *, gpu: bool = False) -> str:
        prefix = f"{GPU_ENV_PREFIX} " if gpu else ""
        return f"{prefix}{PYTHON_EXECUTABLE} {body}"

    commands = [
        ("data_slice_build", command("scripts/build_dualscope_first_slice_data_slice.py --config configs/datasets.yaml --output-dir outputs/dualscope_minimal_first_slice_real_run/data")),
        ("poison_build", command("scripts/build_poison_dataset.py --input-path outputs/dualscope_minimal_first_slice_real_run/data/clean_slice.jsonl --output-dir outputs/dualscope_minimal_first_slice_real_run/poison --attack-config configs/attacks.yaml --profile default --seed 42")),
        ("optional_lora_train", command("scripts/run_lora_finetune.py --dataset-manifest outputs/dualscope_minimal_first_slice_real_run/poison/dataset_manifest.json --training-config configs/training.yaml --training-profile reference --model-config configs/models.yaml --model-profile pilot_small_hf --output-dir outputs/dualscope_minimal_first_slice_real_run/train --seed 42", gpu=True)),
        ("stage1_illumination", command("scripts/run_dualscope_stage1_illumination.py --input outputs/dualscope_minimal_first_slice_real_run/data/eval_slice.jsonl --output-dir outputs/dualscope_minimal_first_slice_real_run/stage1 --seed 42", gpu=True)),
        ("stage2_confidence", command("scripts/run_dualscope_stage2_confidence.py --stage1-dir outputs/dualscope_minimal_first_slice_real_run/stage1 --output-dir outputs/dualscope_minimal_first_slice_real_run/stage2 --capability-mode auto --seed 42", gpu=True)),
        ("stage3_fusion", command("scripts/run_dualscope_stage3_fusion.py --stage1-dir outputs/dualscope_minimal_first_slice_real_run/stage1 --stage2-dir outputs/dualscope_minimal_first_slice_real_run/stage2 --output-dir outputs/dualscope_minimal_first_slice_real_run/stage3 --seed 42")),
        ("evaluation", command("scripts/evaluate_dualscope_first_slice.py --fusion-dir outputs/dualscope_minimal_first_slice_real_run/stage3 --output-dir outputs/dualscope_minimal_first_slice_real_run/eval")),
        ("report", command("scripts/build_dualscope_first_slice_real_run_report.py --run-dir outputs/dualscope_minimal_first_slice_real_run --output-dir outputs/dualscope_minimal_first_slice_real_run/report")),
    ]
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "commands": [
            {"command_id": cid, "command": command, "planned_not_executed_yet": True}
            for cid, command in commands
        ],
    }


def build_expected_artifacts() -> dict[str, Any]:
    groups = {
        "data_artifacts": ["clean_slice.jsonl", "poisoned_slice.jsonl", "train_split.jsonl", "eval_split.jsonl", "dataset_manifest.json"],
        "model_artifacts": ["adapter_checkpoint/", "training_config.json", "train.log", "asr_clean_utility_placeholder.json"],
        "stage1_artifacts": ["illumination_summary.json", "illumination_details.jsonl", "screening_features.jsonl", "stage1_budget_usage.json"],
        "stage2_artifacts": ["confidence_summary.json", "confidence_details.jsonl", "capability_mode_report.json", "fallback_report.json"],
        "stage3_artifacts": ["fusion_summary.json", "fusion_details.jsonl", "final_decisions.jsonl", "cost_summary.json"],
        "evaluation_artifacts": ["metrics_summary.json", "baseline_comparison.json", "real_run_report.md"],
    }
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "artifact_groups": groups}


def build_validation_criteria() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "criteria": [
            "all required artifacts exist",
            "schemas compatible",
            "Stage 1 produces candidate fields",
            "Stage 2 reads candidate fields",
            "Stage 3 reads Stage 1/2 public fields",
            "no contract break",
            "capability mode recorded",
            "budget usage recorded",
            "no benchmark truth / gate semantic changes",
            "report generated",
        ],
        "performance_placeholder_policy": "expected metrics fields available only; no paper-level performance claim in planning stage",
    }


def build_failure_fallback_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "fallbacks": [
            {"if": "dataset_missing", "then": "stop_report_missing_path_do_not_fabricate_data"},
            {"if": "model_missing", "then": "stop_or_explicit_placeholder_mode_do_not_claim_real_run"},
            {"if": "oom", "then": "reduce_batch_size_reduce_sequence_length_enable_quantization_or_stop"},
            {"if": "logprobs_unavailable", "then": "fallback_without_logprobs_mark_degradation_flag"},
            {"if": "lora_training_fails", "then": "stop_or_inference_only_protocol_validation_do_not_report_trained_backdoor"},
            {"if": "artifact_schema_breaks", "then": "stop_and_repair_schema_before_evaluation"},
        ],
    }


def build_details(payloads: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"schema_version": SCHEMA_VERSION, "detail_type": key, "payload": value}
        for key, value in payloads.items()
    ]


def build_summary(payloads: dict[str, dict[str, Any]], details: list[dict[str, Any]]) -> dict[str, Any]:
    preflight = payloads["preflight_checks"]
    commands = payloads["run_command_plan"]
    expected = payloads["expected_artifacts"]
    artifact_count = sum(len(items) for items in expected["artifact_groups"].values())
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "dataset_id": payloads["scope"]["dataset_id"],
        "model_id": payloads["scope"]["model_id"],
        "model_local_path_exists_at_plan_time": payloads["scope"]["model_local_path_exists_at_plan_time"],
        "dataset_placeholder_mode": payloads["dataset_slice_plan"]["placeholder_mode"],
        "preflight_check_count": len(preflight["checks"]),
        "planned_command_count": len(commands["commands"]),
        "expected_artifact_count": artifact_count,
        "details_row_count": len(details),
        "planned_not_executed_yet": True,
        "full_matrix_executed": False,
        "training_executed": False,
        "benchmark_truth_changed": False,
        "gate_semantics_changed": False,
        "recommended_next_step": "dualscope-minimal-first-slice-real-run-preflight",
    }


def build_report(summary: dict[str, Any], scope: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# DualScope Minimal First Slice Real Run Plan Report",
            "",
            "## Scope",
            "",
            f"- Dataset: `{summary['dataset_id']}`",
            f"- Model: `{summary['model_id']}`",
            f"- Trigger: `{scope['trigger_id']}`",
            f"- Target: `{scope['target_id']}`",
            f"- Capability policy: `{scope['capability_mode_policy']}`",
            "",
            "## Execution Status",
            "",
            "- This stage is a real-run plan only.",
            "- No training or full matrix execution was run.",
            "- Missing dataset must stop future real execution.",
            "",
            "## Next Step",
            "",
            "`dualscope-minimal-first-slice-real-run-preflight`",
            "",
        ]
    )
