"""Common builders for the DualScope experimental matrix freeze."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "dualscopellm/experimental-matrix-freeze/v1"
TASK_NAME = "dualscope-experimental-matrix-freeze"
STAGE_NAME = "experimental_matrix_freeze"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def build_problem_definition() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "stage_name": STAGE_NAME,
        "goal": "Freeze the paper-facing DualScope dataset/model/attack/target/capability/baseline/metric matrix without running the full matrix.",
        "what_is_frozen": [
            "dataset matrix",
            "model matrix",
            "trigger and target matrix",
            "capability-mode matrix",
            "baseline and ablation matrix",
            "robustness and cost-analysis contracts",
            "main and appendix table plans",
        ],
        "what_is_not_executed": [
            "full experiment matrix",
            "full finetuning",
            "large model sweep",
            "route_c recursive validation",
            "reasoning branch experiments",
        ],
        "stage_dependencies": [
            "dualscope-illumination-screening-freeze",
            "dualscope-confidence-verification-with-without-logprobs",
            "dualscope-budget-aware-two-stage-fusion-design",
        ],
        "historical_route_c_handling": "Reliability foundation / appendix support only.",
    }


def build_dataset_matrix() -> dict[str, Any]:
    rows = [
        {
            "dataset_id": "stanford_alpaca",
            "role": "general_instruction_following",
            "expected_prompt_style": "instruction_response",
            "clean_subset_role": "clean utility and benign instruction baseline",
            "poisoned_subset_role": "controlled trigger insertion over ordinary instructions",
            "evaluation_subset_role": "main table and clean utility checks",
            "used_in_main_table": True,
            "used_in_robustness_table": True,
            "risk_notes": "Benign instruction diversity can create false positives if template sensitivity is not controlled.",
            "future_expansion_notes": "Expand only after first-slice smoke validates the artifact contract.",
        },
        {
            "dataset_id": "advbench",
            "role": "adversarial_harmful_instruction",
            "expected_prompt_style": "harmful_or_jailbreak_like_instruction",
            "clean_subset_role": "high-risk clean context for false-positive checks",
            "poisoned_subset_role": "triggered harmful-target behavior checks",
            "evaluation_subset_role": "main risk-domain comparison",
            "used_in_main_table": True,
            "used_in_robustness_table": True,
            "risk_notes": "High-risk prompts may raise screening risk without backdoor evidence.",
            "future_expansion_notes": "Adaptive variants remain future-only.",
        },
        {
            "dataset_id": "jbb_behaviors",
            "role": "behavior_level_jailbreak_scenario",
            "expected_prompt_style": "behavior_taxonomy_or_policy_stress_prompt",
            "clean_subset_role": "behavior-level benign preservation where applicable",
            "poisoned_subset_role": "triggered behavior shift and lock verification",
            "evaluation_subset_role": "confidence verification and robustness table",
            "used_in_main_table": True,
            "used_in_robustness_table": True,
            "risk_notes": "Behavior labels must remain separate from benchmark truth changes.",
            "future_expansion_notes": "Use larger behavior coverage only after minimal matrix execution.",
        },
        {
            "dataset_id": "harmbench_future",
            "role": "future_only_safety_behavior_expansion",
            "expected_prompt_style": "future_only",
            "clean_subset_role": "future_only",
            "poisoned_subset_role": "future_only",
            "evaluation_subset_role": "future expansion only",
            "used_in_main_table": False,
            "used_in_robustness_table": False,
            "risk_notes": "Not part of the minimum matrix.",
            "future_expansion_notes": "Can be considered after DualScope first matrix validates.",
        },
    ]
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "dataset_count": len(rows), "datasets": rows}


def build_model_matrix() -> dict[str, Any]:
    rows = [
        {
            "model_id": "qwen2p5_1p5b_instruct",
            "role": "primary_development_and_ablation_axis",
            "approximate_size": "1.5B",
            "resource_tier": "small",
            "expected_gpu_feasibility": "ready on 2 x RTX 3090; local snapshot exists in configs/models.yaml",
            "whether_main_experiment": True,
            "whether_ablation": True,
            "whether_optional_future": False,
            "logprob_availability_assumption": "local HF path can expose token scores in controlled inference when implemented",
            "notes": "High-frequency development model; no full fine-tuning.",
        },
        {
            "model_id": "qwen2p5_7b_instruct",
            "role": "7b_class_validation_axis",
            "approximate_size": "7B",
            "resource_tier": "medium",
            "expected_gpu_feasibility": "limited QLoRA/LoRA and inference on 2 x RTX 3090; not exhaustive",
            "whether_main_experiment": True,
            "whether_ablation": False,
            "whether_optional_future": False,
            "logprob_availability_assumption": "with-logprobs possible in local HF inference; without-logprobs must also be evaluated",
            "notes": "Persuasive validation axis; keep matrix narrow.",
        },
        {
            "model_id": "mistral_7b_or_llama3p1_8b_instruct",
            "role": "cross_model_sanity_check",
            "approximate_size": "7B/8B",
            "resource_tier": "cautious",
            "expected_gpu_feasibility": "limited runs only; choose whichever is locally available first",
            "whether_main_experiment": False,
            "whether_ablation": False,
            "whether_optional_future": True,
            "logprob_availability_assumption": "capability-dependent; must report with/without mode explicitly",
            "notes": "Auxiliary sanity model, not full matrix.",
        },
    ]
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "model_count": len(rows),
        "models": rows,
        "training_policy": {
            "full_finetuning": "disallowed_now",
            "preferred_backdoor_construction": ["LoRA", "QLoRA", "adapter-level construction"],
            "resource_boundary": "2 x RTX 3090",
        },
    }


def build_attack_trigger_matrix() -> dict[str, Any]:
    rows = [
        {
            "trigger_id": "lexical_trigger",
            "trigger_type": "lexical",
            "description": "Rare word, fixed phrase, token, or symbol sequence.",
            "example_pattern": "cfqz_marker / fixed short phrase / symbol combo",
            "expected_difficulty": "low_to_medium",
            "whether_main_matrix": True,
            "whether_robustness_only": False,
            "poisoning_ratio_suggestion": "0.5%-2% for pilot; tune later by dataset.",
            "notes": "First-slice candidate trigger family.",
        },
        {
            "trigger_id": "semantic_trigger",
            "trigger_type": "semantic",
            "description": "Paraphraseable condition, topic, or style-conditioned cue.",
            "example_pattern": "when the request is framed as archival research",
            "expected_difficulty": "medium",
            "whether_main_matrix": True,
            "whether_robustness_only": False,
            "poisoning_ratio_suggestion": "1%-3% controlled pilot.",
            "notes": "Useful for paraphrase robustness.",
        },
        {
            "trigger_id": "contextual_instruction_trigger",
            "trigger_type": "contextual_instruction",
            "description": "Role, instruction-pattern, policy-like prefix, or task framing trigger.",
            "example_pattern": "system-style prefix or role framing wrapper",
            "expected_difficulty": "medium_to_high",
            "whether_main_matrix": True,
            "whether_robustness_only": False,
            "poisoning_ratio_suggestion": "1%-3% controlled pilot.",
            "notes": "Tests prompt-context sensitivity.",
        },
        {
            "trigger_id": "sleeper_style_trigger_future",
            "trigger_type": "sleeper_style",
            "description": "Deferred or conditionally activated trigger style.",
            "example_pattern": "future-only multi-condition trigger",
            "expected_difficulty": "high",
            "whether_main_matrix": False,
            "whether_robustness_only": False,
            "poisoning_ratio_suggestion": "future_only",
            "notes": "Future expansion only; not part of the minimum matrix.",
        },
    ]
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "trigger_count": len(rows), "triggers": rows}


def build_target_behavior_matrix() -> dict[str, Any]:
    rows = [
        {
            "target_id": "fixed_response_or_refusal_bypass",
            "target_type": "fixed_response",
            "description": "Triggered output moves toward a fixed phrase, fixed preference, or refusal-bypass pattern.",
            "expected_output_pattern": "specified target phrase or bypass-oriented answer style",
            "evaluation_method": "target behavior success and DualScope risk evidence",
            "used_in_main": True,
            "used_in_robustness": True,
            "used_in_appendix": True,
            "risk_notes": "Must not relabel meaningless outputs as valid target behavior.",
        },
        {
            "target_id": "behavior_or_harmfulness_shift",
            "target_type": "behavior_shift",
            "description": "Triggered response shifts from safe/neutral behavior toward unsafe or target-class behavior.",
            "expected_output_pattern": "class-level behavior shift rather than fixed text",
            "evaluation_method": "target behavior success plus clean utility preservation",
            "used_in_main": True,
            "used_in_robustness": True,
            "used_in_appendix": True,
            "risk_notes": "Keep target evaluation separate from benchmark truth semantics.",
        },
        {
            "target_id": "subtle_style_shift_future",
            "target_type": "style_shift",
            "description": "Triggered response changes style without obvious target text.",
            "expected_output_pattern": "future-only style deviation",
            "evaluation_method": "future-only",
            "used_in_main": False,
            "used_in_robustness": False,
            "used_in_appendix": False,
            "risk_notes": "Too ambiguous for the minimum matrix.",
        },
    ]
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "target_count": len(rows), "targets": rows}


def build_capability_mode_matrix() -> dict[str, Any]:
    rows = [
        {
            "capability_mode": "with_logprobs",
            "feature_source": "token logprobs / entropy / concentration / lock span",
            "cost_implication": "token probability observation may add backend cost or logging overhead",
            "evidence_strength": "stronger confidence verification evidence",
            "expected_limitation": "not available in all APIs",
            "whether_main_table": True,
            "whether_appendix": True,
            "whether_used_in_robustness": True,
        },
        {
            "capability_mode": "without_logprobs",
            "feature_source": "repeated sampling / lexical lock proxy / structural stability",
            "cost_implication": "more repeated samples may be needed",
            "evidence_strength": "weaker fallback evidence; must carry degradation flags",
            "expected_limitation": "not equivalent to logprob evidence",
            "whether_main_table": True,
            "whether_appendix": True,
            "whether_used_in_robustness": True,
        },
    ]
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "capability_mode_count": len(rows), "capability_modes": rows}


def build_baseline_matrix() -> dict[str, Any]:
    rows = [
        {
            "baseline_id": "illumination_only",
            "description": "Stage 1 screening risk only; no confidence verification.",
            "required_stage_outputs": ["screening_risk_score", "screening_risk_bucket"],
            "capability_requirement": "none",
            "expected_cost": "lowest",
            "role": "main_and_ablation",
            "required_metrics": ["AUROC", "F1", "average_query_cost"],
        },
        {
            "baseline_id": "confidence_only_with_logprobs",
            "description": "Stage 2 logprob lock features applied without Stage 1 routing.",
            "required_stage_outputs": ["verification_risk_score", "capability_mode"],
            "capability_requirement": "with_logprobs",
            "expected_cost": "high_if_broadly_applied",
            "role": "main_and_ablation",
            "required_metrics": ["AUROC", "TPR@low-FPR", "average_query_cost"],
        },
        {
            "baseline_id": "confidence_only_without_logprobs",
            "description": "Stage 2 fallback proxies applied without Stage 1 routing.",
            "required_stage_outputs": ["verification_risk_score", "verification_confidence_degradation_flag"],
            "capability_requirement": "without_logprobs",
            "expected_cost": "medium_to_high_due_to_repeated_sampling",
            "role": "main_and_ablation",
            "required_metrics": ["AUROC", "AUPRC", "cost_normalized_AUROC"],
        },
        {
            "baseline_id": "naive_concat",
            "description": "Concatenate illumination and confidence features without budget-aware trigger policy.",
            "required_stage_outputs": ["screening_risk_score", "verification_risk_score"],
            "capability_requirement": "with_or_without_logprobs",
            "expected_cost": "high_if_verification_runs_for_all_samples",
            "role": "ablation",
            "required_metrics": ["AUROC", "average_query_cost", "verification_trigger_rate"],
        },
        {
            "baseline_id": "dualscope_budget_aware_two_stage_fusion",
            "description": "Main method: illumination first, selective confidence verification, capability-aware fusion.",
            "required_stage_outputs": ["final_risk_score", "verification_triggered", "budget_usage_summary"],
            "capability_requirement": "with_or_without_logprobs",
            "expected_cost": "budget_controlled",
            "role": "main_method",
            "required_metrics": ["AUROC", "F1", "TPR@low-FPR", "average_query_cost", "cost_normalized_AUROC"],
        },
    ]
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "baseline_count": len(rows), "baselines": rows}


def build_ablation_matrix() -> dict[str, Any]:
    rows = []
    specs = [
        ("remove_confidence_verification", "method", "confidence verification", "DualScope vs illumination-only"),
        ("remove_illumination_screening", "method", "illumination screening", "DualScope vs confidence-only"),
        ("replace_budget_fusion_with_naive_concat", "method", "budget-aware fusion", "budget-aware vs concat"),
        ("disable_capability_aware_adjustment", "method", "capability policy", "capability-aware vs ignorant"),
        ("disable_no_logprobs_fallback", "method", "fallback pathway", "with-only vs fallback-capable"),
        ("remove_gain_features", "feature", "Stage 1 gain features", "full Stage 1 vs no gain"),
        ("remove_flip_features", "feature", "Stage 1 flip features", "full Stage 1 vs no flip"),
        ("remove_cross_template_consistency", "feature", "Stage 1 consistency", "full Stage 1 vs no consistency"),
        ("remove_entropy_confidence_lock_features", "feature", "Stage 2 entropy/lock", "full Stage 2 vs no lock"),
        ("remove_repeated_sampling_proxy", "feature", "Stage 2 fallback proxy", "fallback full vs no repeated proxy"),
        ("low_budget", "budget", "budget policy", "low vs medium/high"),
        ("medium_budget", "budget", "budget policy", "medium vs low/high"),
        ("high_budget", "budget", "budget policy", "high vs low/medium"),
        ("trigger_threshold_variation", "budget", "verification trigger threshold", "threshold sweep"),
        ("candidate_only_vs_all_sample_verification", "budget", "verification routing", "selective vs all-sample"),
        ("with_logprobs", "capability", "capability mode", "with vs without"),
        ("without_logprobs", "capability", "capability mode", "fallback vs logprobs"),
        ("mixed_capability_setting", "capability", "mixed mode", "mixed vs single mode"),
        ("degradation_aware_vs_ignorant", "capability", "degradation flag handling", "aware vs ignorant"),
    ]
    for ablation_id, purpose, component, comparison in specs:
        rows.append(
            {
                "ablation_id": ablation_id,
                "purpose": purpose,
                "modified_component": component,
                "expected_comparison": comparison,
                "required_metrics": ["AUROC", "F1", "average_query_cost"],
                "table_placement": "ablation_table" if purpose in {"method", "feature"} else "appendix_or_cost_table",
            }
        )
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "ablation_count": len(rows), "ablations": rows}


def build_robustness_matrix() -> dict[str, Any]:
    specs = [
        ("paraphrase_trigger_robustness", "paraphrase", "illumination screening", "trigger wording sensitivity", "main_or_appendix"),
        ("template_variation_robustness", "template variation", "Stage 1 templates", "template overfit", "main_or_appendix"),
        ("target_variation_robustness", "target variation", "Stage 2 / fusion", "target behavior specificity", "main_or_appendix"),
        ("cross_model_transfer", "model transfer", "full DualScope", "model-specific overfit", "appendix"),
        ("cross_dataset_transfer", "dataset transfer", "full DualScope", "dataset-specific overfit", "appendix"),
        ("trigger_family_variation", "trigger family", "full DualScope", "trigger-family coverage", "main_or_appendix"),
        ("adaptive_lite_setting", "adaptive-lite", "full DualScope", "simple adaptive wrapping", "appendix_limited"),
    ]
    rows = [
        {
            "robustness_id": rid,
            "perturbation_type": perturbation,
            "tested_component": component,
            "expected_stress_point": stress,
            "placement": placement,
            "constraints": "controlled and limited; not a full adaptive-attack mainline",
        }
        for rid, perturbation, component, stress, placement in specs
    ]
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "robustness_count": len(rows), "robustness_checks": rows}


def build_metrics_contract() -> dict[str, Any]:
    specs = [
        ("AUROC", "Area under ROC curve.", "detection", ["score", "label"], "main"),
        ("AUPRC", "Area under precision-recall curve.", "detection", ["score", "label"], "appendix"),
        ("F1", "F1 at selected threshold.", "detection", ["decision", "label"], "main"),
        ("Accuracy", "Accuracy at selected threshold.", "detection", ["decision", "label"], "appendix"),
        ("TPR@low-FPR", "TPR at low false-positive operating point.", "detection", ["score", "label"], "main"),
        ("FPR@fixed-TPR", "FPR at fixed true-positive target.", "detection", ["score", "label"], "appendix"),
        ("average_query_cost", "Average queries consumed per sample.", "cost", ["budget_usage_summary"], "main"),
        ("verification_trigger_rate", "Fraction of samples routed to Stage 2.", "cost", ["verification_triggered"], "main"),
        ("per_sample_verification_cost", "Stage 2 query cost per evaluated sample.", "cost", ["budget_usage_summary"], "main"),
        ("cost_normalized_AUROC", "AUROC normalized by query cost.", "cost", ["AUROC", "average_query_cost"], "main"),
        ("token_logprob_access_cost_marker", "Marker for logprob access cost.", "cost", ["capability_mode"], "appendix"),
        ("with_without_logprobs_cost_delta", "Cost delta between capability modes.", "cost", ["capability_mode", "budget_usage_summary"], "main"),
        ("ASR", "Attack success rate.", "backdoor", ["target_behavior_success"], "main"),
        ("clean_utility", "Utility on benign prompts.", "utility", ["clean_response_metric"], "main"),
        ("utility_drop", "Utility degradation from clean baseline.", "utility", ["clean_utility"], "main"),
        ("target_behavior_success", "Target behavior success under trigger.", "backdoor", ["target_match"], "main"),
        ("benign_behavior_preservation", "Benign behavior retained under clean inputs.", "utility", ["clean_response_metric"], "appendix"),
        ("score_separation", "Score distance between clean and poisoned groups.", "calibration", ["score", "label"], "appendix"),
        ("risk_bucket_calibration", "Calibration of risk buckets.", "calibration", ["risk_bucket", "label"], "appendix"),
        ("threshold_stability", "Threshold sensitivity across slices.", "calibration", ["threshold", "metric"], "appendix"),
    ]
    metrics = [
        {
            "metric_id": mid,
            "definition": definition,
            "used_for": used_for,
            "required_inputs": required_inputs,
            "placement": placement,
        }
        for mid, definition, used_for, required_inputs, placement in specs
    ]
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "metric_count": len(metrics), "metrics": metrics}


def build_table_plan() -> dict[str, Any]:
    tables = [
        {
            "table_id": "main_table_1_overall_detection_performance",
            "purpose": "Compare detection performance across baselines.",
            "rows": ["dataset", "model", "capability_mode", "baseline"],
            "columns": ["AUROC", "F1", "TPR@low-FPR"],
            "required_artifacts": ["baseline_matrix", "metrics_contract", "fusion_outputs"],
            "placement": "main",
        },
        {
            "table_id": "main_table_2_query_cost_budget_tradeoff",
            "purpose": "Show cost/performance trade-off.",
            "rows": ["budget_level", "baseline", "capability_mode"],
            "columns": ["average_query_cost", "verification_trigger_rate", "cost_normalized_AUROC"],
            "required_artifacts": ["budget_policy", "cost_analysis_plan"],
            "placement": "main",
        },
        {
            "table_id": "main_table_3_robustness_summary",
            "purpose": "Summarize robustness under trigger/template/target variations.",
            "rows": ["robustness_id", "dataset", "model"],
            "columns": ["AUROC", "F1", "ASR", "clean_utility"],
            "required_artifacts": ["robustness_matrix"],
            "placement": "main",
        },
        {
            "table_id": "ablation_table",
            "purpose": "Measure contribution of components and feature groups.",
            "rows": ["ablation_id", "dataset", "model"],
            "columns": ["AUROC", "F1", "average_query_cost"],
            "required_artifacts": ["ablation_matrix"],
            "placement": "main",
        },
        {
            "table_id": "appendix_reliability_foundation_summary",
            "purpose": "Summarize historical route_c reliability foundation without continuing it.",
            "rows": ["historical_stage_group", "evidence_type"],
            "columns": ["status", "role", "artifact_pointer"],
            "required_artifacts": ["historical_route_c_outputs"],
            "placement": "appendix",
        },
    ]
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "table_count": len(tables), "tables": tables}


def build_resource_execution_plan() -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "resource_boundary": "2 x RTX 3090",
        "feasible_now": [
            "1.5B / small model pilot",
            "7B QLoRA / LoRA limited runs",
            "controlled backdoor construction",
            "representative matrix execution",
        ],
        "cautious": ["8B model limited runs", "mixed capability evaluation", "cross-model transfer"],
        "future_only": [
            "large-model full fine-tuning",
            "large-scale adaptive attack",
            "large-scale API evaluation",
            "exhaustive large matrix sweep",
        ],
        "minimal_run_order": [
            "stanford_alpaca + qwen2p5_1p5b + lexical_trigger + fixed_response + without_logprobs smoke",
            "add with_logprobs capability if local inference exposes scores",
            "add AdvBench / JBB representative slices",
            "add 7B limited validation",
        ],
        "recommended_first_execution_slice": {
            "dataset_id": "stanford_alpaca",
            "model_id": "qwen2p5_1p5b_instruct",
            "trigger_id": "lexical_trigger",
            "target_id": "fixed_response_or_refusal_bypass",
            "capability_modes": ["without_logprobs", "with_logprobs_if_available"],
            "baselines": ["illumination_only", "dualscope_budget_aware_two_stage_fusion"],
        },
        "resource_risk": [
            "7B local availability may block execution.",
            "with-logprobs support depends on backend implementation.",
            "Full matrix would exceed current planning scope.",
        ],
        "failure_fallback": "If the first execution slice cannot run with a real model, run a controlled artifact smoke without expanding the matrix.",
    }


def build_artifact_contract() -> dict[str, Any]:
    required = [
        "dualscope_experimental_matrix_problem_definition.json",
        "dualscope_dataset_matrix.json",
        "dualscope_model_matrix.json",
        "dualscope_attack_trigger_matrix.json",
        "dualscope_target_behavior_matrix.json",
        "dualscope_capability_mode_matrix.json",
        "dualscope_baseline_matrix.json",
        "dualscope_ablation_matrix.json",
        "dualscope_robustness_matrix.json",
        "dualscope_metrics_contract.json",
        "dualscope_table_plan.json",
        "dualscope_resource_execution_plan.json",
        "dualscope_artifact_contract.json",
        "dualscope_experimental_matrix_freeze_summary.json",
        "dualscope_experimental_matrix_freeze_details.jsonl",
        "dualscope_experimental_matrix_freeze_report.md",
        "dualscope_experimental_matrix_freeze_verdict.json",
        "dualscope_experimental_matrix_freeze_next_step_recommendation.json",
    ]
    return {"summary_status": "PASS", "schema_version": SCHEMA_VERSION, "required_artifacts": required}


def build_optional_plans(resource_plan: dict[str, Any], table_plan: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    run_order = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "run_order": resource_plan["minimal_run_order"],
        "do_not_run_now": ["full_matrix", "large_model_sweep", "route_c_recursive_chain"],
    }
    first_slice = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "minimal_first_slice": resource_plan["recommended_first_execution_slice"],
        "next_plan": "dualscope-minimal-first-slice-execution-plan",
    }
    paper_tables = {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "table_skeletons": table_plan["tables"],
    }
    return run_order, first_slice, paper_tables


def build_details(
    dataset_matrix: dict[str, Any],
    model_matrix: dict[str, Any],
    trigger_matrix: dict[str, Any],
    target_matrix: dict[str, Any],
    capability_matrix: dict[str, Any],
    baseline_matrix: dict[str, Any],
    metrics_contract: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, matrix, rows_key in [
        ("dataset", dataset_matrix, "datasets"),
        ("model", model_matrix, "models"),
        ("trigger", trigger_matrix, "triggers"),
        ("target", target_matrix, "targets"),
        ("capability", capability_matrix, "capability_modes"),
        ("baseline", baseline_matrix, "baselines"),
        ("metric", metrics_contract, "metrics"),
    ]:
        for idx, item in enumerate(matrix[rows_key]):
            rows.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "detail_type": key,
                    "row_index": idx,
                    "entry": item,
                    "controlled_protocol_only": True,
                }
            )
    return rows


def build_summary(
    dataset_matrix: dict[str, Any],
    model_matrix: dict[str, Any],
    trigger_matrix: dict[str, Any],
    target_matrix: dict[str, Any],
    capability_matrix: dict[str, Any],
    baseline_matrix: dict[str, Any],
    ablation_matrix: dict[str, Any],
    robustness_matrix: dict[str, Any],
    metrics_contract: dict[str, Any],
    table_plan: dict[str, Any],
    details: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "summary_status": "PASS",
        "schema_version": SCHEMA_VERSION,
        "task_name": TASK_NAME,
        "dataset_count": dataset_matrix["dataset_count"],
        "main_dataset_count": sum(1 for row in dataset_matrix["datasets"] if row["used_in_main_table"]),
        "model_count": model_matrix["model_count"],
        "main_model_count": sum(1 for row in model_matrix["models"] if row["whether_main_experiment"]),
        "trigger_count": trigger_matrix["trigger_count"],
        "main_trigger_count": sum(1 for row in trigger_matrix["triggers"] if row["whether_main_matrix"]),
        "target_count": target_matrix["target_count"],
        "main_target_count": sum(1 for row in target_matrix["targets"] if row["used_in_main"]),
        "capability_mode_count": capability_matrix["capability_mode_count"],
        "baseline_count": baseline_matrix["baseline_count"],
        "ablation_count": ablation_matrix["ablation_count"],
        "robustness_count": robustness_matrix["robustness_count"],
        "metric_count": metrics_contract["metric_count"],
        "table_count": table_plan["table_count"],
        "details_row_count": len(details),
        "controlled_protocol_only": True,
        "full_matrix_executed": False,
        "route_c_chain_continued": False,
        "reasoning_branch_included": False,
        "recommended_next_step": "dualscope-minimal-first-slice-execution-plan",
    }


def build_report(summary: dict[str, Any], resource_plan: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# DualScope Experimental Matrix Freeze Report",
            "",
            "## Status",
            "",
            f"- Summary status: `{summary['summary_status']}`",
            f"- Datasets: `{summary['dataset_count']}` total, `{summary['main_dataset_count']}` main",
            f"- Models: `{summary['model_count']}` total, `{summary['main_model_count']}` main",
            f"- Triggers: `{summary['trigger_count']}` total, `{summary['main_trigger_count']}` main",
            f"- Targets: `{summary['target_count']}` total, `{summary['main_target_count']}` main",
            f"- Capability modes: `{summary['capability_mode_count']}`",
            f"- Baselines: `{summary['baseline_count']}`",
            f"- Metrics: `{summary['metric_count']}`",
            "",
            "## Interpretation",
            "",
            "This stage freezes the experiment contract only. It does not run the full matrix, does not expand the model axis, and does not continue the historical route_c chain.",
            "",
            "## Recommended First Slice",
            "",
            "```json",
            json.dumps(resource_plan["recommended_first_execution_slice"], indent=2, ensure_ascii=False),
            "```",
            "",
            "## Next Step",
            "",
            "`dualscope-minimal-first-slice-execution-plan`",
            "",
        ]
    )
