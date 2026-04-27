# DualScope Task Queue

This file is the local task queue consumed by `scripts/dualscope_task_orchestrator.py`.
The Markdown text is for humans; the fenced JSON block is the source of truth.

```json
{
  "schema_version": "dualscope/task-queue/v1",
  "project": "DualScope-LLM",
  "tasks": [
    {
      "task_id": "dualscope-minimal-first-slice-real-run-compression",
      "purpose": "Compress the partial minimal first-slice real-run state into explicit model execution, logprob, label, and metric readiness gaps without expanding the experiment matrix.",
      "expected_inputs": [
        ".plans/dualscope-minimal-first-slice-real-run-compression.md",
        "outputs/dualscope_minimal_first_slice_real_run/default/",
        "outputs/dualscope_minimal_first_slice_real_run_compression/default/"
      ],
      "expected_outputs": [
        "outputs/dualscope_minimal_first_slice_real_run_compression/default/dualscope_minimal_first_slice_real_run_compression_verdict.json",
        "outputs/dualscope_minimal_first_slice_real_run_compression/default/dualscope_minimal_first_slice_real_run_compression_report.md"
      ],
      "branch_name_suggestion": "codex/dualscope-real-run-compression",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the task ExecPlan first. Keep the work limited to minimal first-slice real-run compression. Do not modify benchmark truth, gates, route_c chains, or any full-matrix execution. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review status.",
      "completion_verdicts": {
        "validated": [
          "Real-run compression validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_minimal_first_slice_real_run_compression/default/dualscope_minimal_first_slice_real_run_compression_verdict.json",
        "outputs/dualscope_minimal_first_slice_real_run_compression_analysis/default/dualscope_minimal_first_slice_real_run_compression_verdict.json"
      ],
      "next_task_if_validated": "dualscope-first-slice-clean-poisoned-labeled-slice-plan",
      "next_task_if_partially_validated": "dualscope-minimal-first-slice-real-run-compression-repair",
      "next_task_if_not_validated": "dualscope-minimal-first-slice-real-run-compression-blocker-closure"
    },
    {
      "task_id": "dualscope-first-slice-clean-poisoned-labeled-slice-plan",
      "purpose": "Define the clean/poisoned labeled first-slice contract needed to unlock honest detection, utility, and ASR metrics for DualScope without fabricating labels.",
      "expected_inputs": [
        ".plans/dualscope-first-slice-clean-poisoned-labeled-slice-plan.md",
        "outputs/dualscope_minimal_first_slice_real_run_compression/default/"
      ],
      "expected_outputs": [
        "outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default/dualscope_first_slice_clean_poisoned_labeled_slice_summary.json",
        "outputs/dualscope_first_slice_clean_poisoned_labeled_slice_analysis/default/dualscope_first_slice_clean_poisoned_labeled_slice_verdict.json"
      ],
      "branch_name_suggestion": "codex/dualscope-labeled-slice-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the task ExecPlan first. Scope the work to the clean/poisoned labeled first-slice plan and metric-readiness contract. Do not fabricate benchmark truth or change gates. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review status.",
      "completion_verdicts": {
        "validated": [
          "Clean-poisoned labeled slice plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_first_slice_clean_poisoned_labeled_slice_analysis/default/dualscope_first_slice_clean_poisoned_labeled_slice_verdict.json"
      ],
      "next_task_if_validated": "dualscope-minimal-first-slice-real-run-rerun-with-labels",
      "next_task_if_partially_validated": "dualscope-first-slice-clean-poisoned-labeled-slice-repair",
      "next_task_if_not_validated": "dualscope-first-slice-clean-poisoned-labeled-slice-blocker-closure"
    },
    {
      "task_id": "dualscope-minimal-first-slice-real-run-rerun-with-labels",
      "purpose": "Rerun the minimal first-slice chain with the labeled clean/poisoned contract wired into metrics while preserving the same dataset/model/trigger/target/budget scope.",
      "expected_inputs": [
        ".plans/dualscope-minimal-first-slice-real-run-rerun-with-model-or-fallback.md",
        "outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default/",
        "outputs/dualscope_first_slice_clean_poisoned_labeled_slice_analysis/default/"
      ],
      "expected_outputs": [
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/dualscope_minimal_first_slice_real_run_rerun_with_labels_verdict.json",
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/dualscope_minimal_first_slice_real_run_rerun_with_labels_report.md"
      ],
      "branch_name_suggestion": "codex/dualscope-real-run-rerun-with-labels",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the relevant first-slice rerun plans first. Rerun only the minimal first-slice with labels integrated into metrics. Preserve the existing dataset/model/trigger/target/budget scope. Do not expand to the full matrix, do not change benchmark truth, and do not continue route_c. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review status.",
      "completion_verdicts": {
        "validated": [
          "Minimal first-slice labeled rerun validated",
          "Minimal first-slice real run with labels validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/dualscope_minimal_first_slice_real_run_rerun_with_labels_verdict.json"
      ],
      "next_task_if_validated": "dualscope-first-slice-target-response-generation-plan",
      "next_task_if_partially_validated": "dualscope-minimal-first-slice-real-run-rerun-with-labels-repair",
      "next_task_if_not_validated": "dualscope-minimal-first-slice-real-run-rerun-with-labels-blocker-closure"
    },
    {
      "task_id": "dualscope-minimal-first-slice-real-run-rerun-with-labels-repair",
      "purpose": "Compress the partially validated labeled rerun into explicit condition-level rerun inputs and metric blockers without changing labels, benchmark truth, gates, or scope.",
      "expected_inputs": [
        ".plans/dualscope-minimal-first-slice-real-run-rerun-with-labels-repair.md",
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"
      ],
      "expected_outputs": [
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair_verdict.json",
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/condition_level_rerun_input_manifest.json"
      ],
      "branch_name_suggestion": "codex/dualscope-real-run-rerun-with-labels-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the task ExecPlan first. Scope the work to repair/compression for the partially validated labeled rerun: produce condition-level rerun inputs and explicit metric blockers. Do not modify benchmark truth, labels, gates, or full-matrix scope, and do not continue route_c. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review status.",
      "completion_verdicts": {
        "validated": [
          "Repair/compression package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-minimal-first-slice-condition-level-rerun",
      "next_task_if_partially_validated": "dualscope-minimal-first-slice-real-run-rerun-with-labels-repair",
      "next_task_if_not_validated": "dualscope-minimal-first-slice-real-run-rerun-with-labels-repair-blocker-closure"
    },
    {
      "task_id": "dualscope-minimal-first-slice-condition-level-rerun",
      "purpose": "Run the minimal first-slice Stage 1/2/3 chain on row_id-keyed clean and poisoned-triggered condition-level inputs so detection metrics can become reportable without changing the label contract.",
      "expected_inputs": [
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/condition_level_rerun_input_slice.jsonl",
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/condition_level_rerun_input_manifest.json"
      ],
      "expected_outputs": [
        "outputs/dualscope_minimal_first_slice_condition_level_rerun/default/dualscope_minimal_first_slice_condition_level_rerun_verdict.json",
        "outputs/dualscope_minimal_first_slice_condition_level_rerun/default/dualscope_minimal_first_slice_condition_level_rerun_report.md"
      ],
      "branch_name_suggestion": "codex/dualscope-condition-level-rerun",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the labeled-rerun repair artifacts first. Scope the work to a minimal condition-level rerun over the existing clean/poisoned first-slice input slice. Preserve the dataset/model/trigger/target/budget scope. Do not modify benchmark truth, labels, gates, or full-matrix scope, and do not continue route_c. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review status.",
      "completion_verdicts": {
        "validated": [
          "Condition-level first-slice rerun validated",
          "Condition-level rerun validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_minimal_first_slice_condition_level_rerun/default/dualscope_minimal_first_slice_condition_level_rerun_verdict.json"
      ],
      "next_task_if_validated": "dualscope-first-slice-target-response-generation-plan",
      "next_task_if_partially_validated": "dualscope-minimal-first-slice-condition-level-rerun-repair",
      "next_task_if_not_validated": "dualscope-minimal-first-slice-condition-level-rerun-blocker-closure"
    },
    {
      "task_id": "dualscope-first-slice-target-response-generation-plan",
      "purpose": "Plan and validate target-response generation artifacts needed for labeled first-slice performance analysis without changing the attack or target truth contract.",
      "expected_inputs": [
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/",
        "outputs/dualscope_first_slice_clean_poisoned_labeled_slice/default/"
      ],
      "expected_outputs": [
        "outputs/dualscope_first_slice_target_response_generation_plan/default/dualscope_first_slice_target_response_generation_plan_verdict.json",
        "outputs/dualscope_first_slice_target_response_generation_plan/default/dualscope_first_slice_target_response_generation_plan_report.md"
      ],
      "branch_name_suggestion": "codex/dualscope-target-response-generation-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the latest first-slice labeled artifacts first. Scope the work to target-response generation planning for the same first-slice setting. Do not modify benchmark truth, labels, gates, or full-matrix scope. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review status.",
      "completion_verdicts": {
        "validated": [
          "Target-response generation plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_first_slice_target_response_generation_plan/default/dualscope_first_slice_target_response_generation_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-first-slice-real-run-artifact-validation",
      "next_task_if_partially_validated": "dualscope-first-slice-target-response-generation-plan-repair",
      "next_task_if_not_validated": "dualscope-first-slice-target-response-generation-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-first-slice-real-run-artifact-validation",
      "purpose": "Validate that the first-slice real-run artifacts are complete, contract-compatible, and honest about model/logprob/label limitations.",
      "expected_inputs": [
        ".plans/dualscope-first-slice-real-run-artifact-validation.md",
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default/",
        "outputs/dualscope_first_slice_target_response_generation_plan/default/"
      ],
      "expected_outputs": [
        "outputs/dualscope_first_slice_real_run_artifact_validation/default/dualscope_first_slice_real_run_artifact_validation_verdict.json",
        "outputs/dualscope_first_slice_real_run_artifact_validation/default/dualscope_first_slice_real_run_artifact_validation_report.md"
      ],
      "branch_name_suggestion": "codex/dualscope-first-slice-artifact-validation",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the artifact validation ExecPlan first. Validate only the first-slice real-run artifacts and contracts. Do not alter benchmark truth, gates, branch history, or full-matrix scope. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review status.",
      "completion_verdicts": {
        "validated": [
          "First-slice real-run artifact validation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_first_slice_real_run_artifact_validation/default/dualscope_first_slice_real_run_artifact_validation_verdict.json",
        "outputs/dualscope_first_slice_real_run_artifact_validation_analysis/default/dualscope_first_slice_real_run_artifact_validation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-first-slice-result-package",
      "next_task_if_partially_validated": "dualscope-first-slice-real-run-artifact-validation-repair",
      "next_task_if_not_validated": "dualscope-first-slice-real-run-artifact-validation-blocker-closure"
    },
    {
      "task_id": "dualscope-first-slice-real-run-artifact-validation-repair",
      "purpose": "Repair the partially validated first-slice real-run artifact validation stage by identifying missing or incompatible artifacts, regenerating only the minimum required validation artifacts, and producing a validated or clearly blocked artifact-validation state.",
      "expected_inputs": [
        "outputs/dualscope_first_slice_real_run_artifact_validation/default",
        "outputs/dualscope_first_slice_real_run_artifact_validation_analysis/default",
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default",
        "outputs/dualscope_minimal_first_slice_condition_level_rerun/default",
        "outputs/dualscope_first_slice_condition_row_level_fusion_alignment/default",
        "outputs/dualscope_illumination_screening_freeze/default",
        "outputs/dualscope_confidence_verification_with_without_logprobs/default",
        "outputs/dualscope_budget_aware_two_stage_fusion_design/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-first-slice-real-run-artifact-validation-repair.md",
        "src/eval/dualscope_first_slice_real_run_artifact_validation_repair.py",
        "src/eval/post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py",
        "scripts/build_dualscope_first_slice_real_run_artifact_validation_repair.py",
        "scripts/build_post_dualscope_first_slice_real_run_artifact_validation_repair_analysis.py",
        "docs/dualscope_first_slice_real_run_artifact_validation_repair.md",
        "outputs/dualscope_first_slice_real_run_artifact_validation_repair/default",
        "outputs/dualscope_first_slice_real_run_artifact_validation_repair_analysis/default"
      ],
      "branch_name_suggestion": "codex/dualscope-artifact-validation-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the previous artifact-validation partial verdict, and the latest first-slice target-response-generation artifacts first. Determine why artifact validation is only Partially validated, explicitly separating missing artifacts, schema mismatch, granularity mismatch, projected metric versus full metric confusion, missing capability-mode or fallback flags, and missing report, verdict, or recommendation artifacts. Scope the work to the minimum necessary repair artifacts only: do not rerun the full matrix, do not expand dataset/model/trigger/target/budget scope, do not fabricate AUROC/F1/ASR/utility, do not write projected metrics as full model performance, do not fake labels, do not fake model outputs, do not modify benchmark truth, do not modify gates, do not continue old route_c, and do not generate 199+. Create or update the repair ExecPlan, implement the repair builder and post-analysis builder, generate repair artifacts, run py_compile, run the repair build CLI, run the repair post-analysis CLI, and output exactly one final verdict: First-slice real-run artifact validation repair validated, Partially validated, or Not validated. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review/CI status. Do not auto merge, force push, delete branches, change remotes, fake performance, fake labels, or fake model outputs.",
      "completion_verdicts": {
        "validated": [
          "First-slice real-run artifact validation repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_first_slice_real_run_artifact_validation_repair/default/dualscope_first_slice_real_run_artifact_validation_repair_verdict.json",
        "outputs/dualscope_first_slice_real_run_artifact_validation_repair_analysis/default/dualscope_first_slice_real_run_artifact_validation_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-first-slice-result-package",
      "next_task_if_partially_validated": "dualscope-first-slice-artifact-validation-repair-compression",
      "next_task_if_not_validated": "dualscope-first-slice-artifact-validation-blocker-closure"
    },
    {
      "task_id": "dualscope-first-slice-result-package",
      "purpose": "Package first-slice results, limitations, and reportable items for paper-ready analysis without overstating metric validity.",
      "expected_inputs": [
        ".plans/dualscope-first-slice-result-package.md",
        "outputs/dualscope_first_slice_real_run_artifact_validation/default/"
      ],
      "expected_outputs": [
        "outputs/dualscope_first_slice_result_package/default/dualscope_first_slice_result_package_verdict.json",
        "outputs/dualscope_first_slice_result_package/default/dualscope_first_slice_result_package_report.md"
      ],
      "branch_name_suggestion": "codex/dualscope-first-slice-result-package",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the result package ExecPlan first. Package only the first-slice results and limitations; keep claims honest about partial or fallback paths. Do not alter benchmark truth or start full-matrix experiments. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review status.",
      "completion_verdicts": {
        "validated": [
          "First-slice result package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_first_slice_result_package/default/dualscope_first_slice_result_package_verdict.json",
        "outputs/dualscope_first_slice_result_package_analysis/default/dualscope_first_slice_result_package_verdict.json"
      ],
      "next_task_if_validated": "dualscope-next-experiment-readiness-package",
      "next_task_if_partially_validated": "dualscope-first-slice-result-package-repair",
      "next_task_if_not_validated": "dualscope-first-slice-result-package-blocker-closure"
    },
    {
      "task_id": "dualscope-next-experiment-readiness-package",
      "purpose": "Prepare the next DualScope experiment-readiness package after the first-slice result package, keeping the next experiment small, auditable, and budget-aware.",
      "expected_inputs": [
        ".plans/dualscope-next-experiment-readiness-package.md",
        "outputs/dualscope_first_slice_result_package/default/"
      ],
      "expected_outputs": [
        "outputs/dualscope_next_experiment_readiness_package/default/dualscope_next_experiment_readiness_verdict.json",
        "outputs/dualscope_next_experiment_readiness_package/default/dualscope_next_experiment_readiness_report.md"
      ],
      "branch_name_suggestion": "codex/dualscope-next-experiment-readiness",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and the readiness package ExecPlan first. Prepare only the next small DualScope experiment-readiness package. Keep the scope budget-aware and auditable; do not launch broad experiments or route_c continuations. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review status.",
      "completion_verdicts": {
        "validated": [
          "Next experiment readiness package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_next_experiment_readiness_package/default/dualscope_next_experiment_readiness_verdict.json",
        "outputs/dualscope_next_experiment_readiness_package_analysis/default/dualscope_next_experiment_readiness_verdict.json"
      ],
      "next_task_if_validated": "dualscope-main-model-axis-upgrade-plan",
      "next_task_if_partially_validated": "dualscope-next-experiment-readiness-package-repair",
      "next_task_if_not_validated": "dualscope-next-experiment-readiness-package-blocker-closure"
    },
    {
      "task_id": "dualscope-main-model-axis-upgrade-plan",
      "purpose": "Upgrade DualScope from 1.5B-only pilot to SCI3 model matrix, with Qwen2.5-7B as main model and Llama/Mistral 7B/8B as cross-model validation.",
      "expected_inputs": [
        "DUALSCOPE_MASTER_PLAN.md",
        "DUALSCOPE_TASK_QUEUE.md",
        "docs/dualscope_sci3_experimental_track.md",
        "docs/dualscope_sci3_model_matrix.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-main-model-axis-upgrade-plan.md",
        "docs/dualscope_sci3_model_matrix.md",
        "docs/dualscope_sci3_resource_plan_2x3090.md",
        "outputs/dualscope_main_model_axis_upgrade_plan/default"
      ],
      "branch_name_suggestion": "codex/dualscope-main-model-axis-upgrade",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the SCI3 experimental track docs first. Scope this task to planning the SCI3 model axis only. Explicitly set Qwen2.5-1.5B-Instruct as pilot/debug/automation/ablation only, Qwen2.5-7B-Instruct as the main experimental model for main tables, ablations, and cost analysis, and Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 as cross-model validation. If local 7B/8B paths are missing, mark planned/external-resource-required; do not fake model paths or claim experiments are complete. Do not run the full matrix, do not train, do not full finetune, do not LoRA/QLoRA train, do not change benchmark truth, do not change gates, do not continue route_c, and do not generate 199+. Produce a model-axis upgrade ExecPlan, resource readiness notes for 2x3090, outputs under outputs/dualscope_main_model_axis_upgrade_plan/default, and a final verdict: SCI3 main model axis upgrade plan validated, Partially validated, or Not validated. Follow AGENTS.md GitHub PR Workflow and do not auto merge, force push, delete branches, rewrite remotes, fake responses, or fake metrics.",
      "completion_verdicts": {
        "validated": [
          "SCI3 main model axis upgrade plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_main_model_axis_upgrade_plan/default/dualscope_main_model_axis_upgrade_plan_verdict.json",
        "outputs/dualscope_main_model_axis_upgrade_plan_analysis/default/dualscope_main_model_axis_upgrade_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-resource-materialization-and-config",
      "next_task_if_partially_validated": "dualscope-main-model-axis-upgrade-plan-repair",
      "next_task_if_not_validated": "dualscope-main-model-axis-upgrade-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-resource-materialization-and-config",
      "purpose": "Materialize or clearly block Qwen2.5-7B-Instruct resources, labeled pairs, and target-response plan dependencies before Qwen2.5-7B first-slice response-generation planning continues.",
      "expected_inputs": [
        "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_main_model_axis_upgrade_plan/default",
        "outputs/dualscope_first_slice_target_response_generation_plan/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-resource-materialization-and-config.md",
        "src/eval/dualscope_qwen2p5_7b_resource_common.py",
        "src/eval/dualscope_qwen2p5_7b_resource_materialization.py",
        "src/eval/post_dualscope_qwen2p5_7b_resource_materialization_analysis.py",
        "scripts/build_dualscope_qwen2p5_7b_resource_materialization.py",
        "scripts/build_post_dualscope_qwen2p5_7b_resource_materialization_analysis.py",
        "scripts/check_dualscope_model_resource_readiness.py",
        "docs/dualscope_qwen2p5_7b_resource_materialization.md",
        "docs/dualscope_sci3_model_resource_requirements.md",
        "outputs/dualscope_qwen2p5_7b_resource_materialization/default",
        "outputs/dualscope_qwen2p5_7b_resource_materialization_analysis/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-resource-materialization",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and SCI3 model-resource docs first. Materialize or clearly block Qwen/Qwen2.5-7B-Instruct at models/qwen2p5-7b-instruct using Hugging Face snapshot_download only when disk/auth/resource checks pass. Check tokenizer, config, GPU, disk, labeled pairs, target-response plan output, and cross-model candidate availability. Do not fake model paths, downloads, tokenizer/config checks, labels, target-response plans, responses, logprobs, AUROC/F1/ASR/utility, benchmark truth, gates, route_c, or 199+. If disk, network, auth, license, or resource constraints block download, write explicit blockers and manual recovery instructions. Final verdicts: Qwen2.5-7B resource materialization validated, Partially validated, or Not validated. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or unrelated PR merge.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B resource materialization validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_resource_materialization/default/dualscope_qwen2p5_7b_resource_materialization_verdict.json",
        "outputs/dualscope_qwen2p5_7b_resource_materialization_analysis/default/dualscope_qwen2p5_7b_resource_materialization_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-first-slice-response-generation-plan",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-resource-materialization-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-resource-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-resource-materialization-repair",
      "purpose": "Repair Qwen2.5-7B resource materialization blockers such as insufficient disk, missing labeled pairs, missing target-response plan output, or missing verified local model path.",
      "expected_inputs": [
        "outputs/dualscope_qwen2p5_7b_resource_materialization/default",
        "outputs/dualscope_qwen2p5_7b_resource_materialization_analysis/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-resource-materialization-repair.md",
        "docs/dualscope_qwen2p5_7b_resource_materialization.md",
        "outputs/dualscope_qwen2p5_7b_resource_materialization/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-resource-materialization-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the Qwen2.5-7B resource materialization blockers first. Repair only the resource blockers needed for Qwen2.5-7B first-slice readiness: disk/cache placement, local model path config, labeled pairs, or target-response plan outputs. Do not fake model availability, downloads, tokenizer/config checks, responses, metrics, benchmark truth, gates, route_c, or 199+. If a blocker requires user-provided storage, credentials, or license acceptance, report it honestly. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B resource materialization repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_resource_materialization_repair/default/dualscope_qwen2p5_7b_resource_materialization_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-resource-materialization-and-config",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-resource-materialization-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-resource-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-first-slice-response-generation-plan",
      "purpose": "Prepare Qwen2.5-7B first-slice response generation plan, without running full matrix.",
      "expected_inputs": [
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_main_model_axis_upgrade_plan/default",
        "outputs/dualscope_first_slice_target_response_generation_plan/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-first-slice-response-generation-plan.md",
        "docs/dualscope_qwen2p5_7b_first_slice_response_generation_plan.md",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default"
      ],
      "branch_name_suggestion": "codex/dualscope-qwen2p5-7b-response-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the SCI3 model-axis upgrade artifacts first. Prepare a Qwen2.5-7B-Instruct first-slice response generation plan only. Use Stanford Alpaca first-slice, lexical trigger cftrigger, fixed target text, frozen Stage 1/2/3 protocol, and Qwen2.5-7B as the main experimental model. Do not execute the full matrix, do not claim responses exist, and do not fake paths, responses, logprobs, AUROC/F1/ASR/utility, benchmark truth, or gates. If 7B local resources are missing, write blockers and readiness checks. Final verdicts: Qwen2.5-7B first-slice response generation plan validated, Partially validated, or Not validated. Follow AGENTS.md PR workflow without auto merge, force push, branch deletion, or remote rewrite.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B first-slice response generation plan validated",
          "First-slice response generation plan validated",
          "Response generation plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_verdict.json",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan_analysis/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-first-slice-response-generation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-first-slice-response-generation-plan-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-first-slice-response-generation-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-first-slice-response-generation",
      "purpose": "Run or prepare minimal Qwen2.5-7B response generation on Stanford Alpaca first-slice, lexical trigger, fixed target.",
      "expected_inputs": [
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "models/qwen2p5-7b-instruct",
        "outputs/dualscope_first_slice_target_response_generation_plan/default",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default",
        "outputs/dualscope_main_model_axis_upgrade_plan/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-first-slice-response-generation.md",
        "src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py",
        "scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py",
        "docs/dualscope_qwen2p5_7b_first_slice_response_generation.md",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"
      ],
      "branch_name_suggestion": "codex/dualscope-qwen2p5-7b-response-generation",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the Qwen2.5-7B response generation plan first. Use local Qwen2.5-7B-Instruct at `/mnt/sda3/lh/models/qwen2p5-7b-instruct` through repo binding `models/qwen2p5-7b-instruct`, Stanford Alpaca first-slice labeled pairs, and target-response plan output `outputs/dualscope_first_slice_target_response_generation_plan/default`. Run or prepare minimal Qwen2.5-7B-Instruct response generation on Stanford Alpaca first-slice only: lexical trigger cftrigger, fixed target text, `batch_size=1`, `CUDA_VISIBLE_DEVICES=2,3`, and low-memory / 4-bit strategy if needed. Do not train, do not full finetune, do not LoRA/QLoRA train, and do not run the full matrix. If OOM, CUDA, model load, or logprobs are unavailable, write explicit blockers/fallback flags; do not fake model paths, responses, logprobs, AUROC/F1/ASR/utility, benchmark truth, or gates. Output response artifacts, capability mode, response_generation_mode, fallback flags, blockers, and a final verdict: Qwen2.5-7B first-slice response generation validated, Partially validated, or Not validated. Metrics are a later task; do not compute or claim metrics here. Do not continue route_c or generate 199+. Follow AGENTS.md PR workflow without auto merge, force push, branch deletion, or remote rewrite.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B first-slice response generation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default/dualscope_qwen2p5_7b_first_slice_response_generation_verdict.json",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation_analysis/default/dualscope_qwen2p5_7b_first_slice_response_generation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-label-aligned-metric-computation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-response-generation-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-response-generation-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-response-generation-repair",
      "purpose": "Repair the partially validated Qwen2.5-7B first-slice response-generation path by producing real minimal response artifacts when resources allow, or a precise runtime blocker when they do not.",
      "expected_inputs": [
        ".plans/dualscope-qwen2p5-7b-response-generation-repair.md",
        ".plans/dualscope-qwen2p5-7b-first-slice-response-generation.md",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_first_slice_target_response_generation_plan/default",
        "outputs/dualscope_qwen2p5_7b_resource_materialization/default",
        "models/qwen2p5-7b-instruct",
        "/mnt/sda3/lh/models/qwen2p5-7b-instruct",
        "src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py",
        "scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-response-generation-repair.md",
        "src/eval/dualscope_qwen2p5_7b_response_generation_repair.py",
        "src/eval/post_dualscope_qwen2p5_7b_response_generation_repair_analysis.py",
        "scripts/build_dualscope_qwen2p5_7b_response_generation_repair.py",
        "scripts/build_post_dualscope_qwen2p5_7b_response_generation_repair_analysis.py",
        "docs/dualscope_qwen2p5_7b_response_generation_repair.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-response-generation-repair.json",
        "outputs/dualscope_qwen2p5_7b_response_generation_repair/default",
        "outputs/dualscope_qwen2p5_7b_response_generation_repair_analysis/default",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-response-generation-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the Qwen2.5-7B first-slice response-generation partial verdict, and the tracked verdict registry first. Goal: repair the Qwen2.5-7B first-slice response-generation path so it either produces real minimal response artifacts or records a concrete blocker. This task is execution-required and is not a plan-only task: do not only generate plans, docs, registry, or task packages. You must execute `.venv/bin/python scripts/build_dualscope_qwen2p5_7b_response_generation_repair.py --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl --target-response-plan-dir outputs/dualscope_first_slice_target_response_generation_plan/default --output-dir outputs/dualscope_qwen2p5_7b_response_generation_repair/default --max-examples 8 --batch-size 1 --max-new-tokens 64 --device-map auto --load-in-4bit --allow-without-logprobs` or an equivalent supported invocation. If the CLI succeeds, it must produce a response JSONL with at least one row; if it fails, it must produce a blocker JSON with an explicit blocker_type. Otherwise the task is not merge-eligible. Required inputs are `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`, `outputs/dualscope_first_slice_target_response_generation_plan/default`, `outputs/dualscope_qwen2p5_7b_resource_materialization/default`, repo binding `models/qwen2p5-7b-instruct`, and `/mnt/sda3/lh/models/qwen2p5-7b-instruct`. Use environment `HF_HOME=/mnt/sda3/lh/huggingface`, `TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers`, `HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub`, `TMPDIR=/mnt/sda3/lh/tmp`, and `CUDA_VISIBLE_DEVICES=2,3`. Scope is only Stanford Alpaca first-slice, lexical trigger `cftrigger`, fixed target `I have completed the requested instruction.`, `batch_size=1`, and a small max-example repair run first. Prefer 4-bit or low-memory loading, `device_map=auto` when implemented, and bounded `max_new_tokens`. If OOM, model load, CUDA, or logprob support fails, write explicit blocker artifacts; if logprobs are unavailable, record without-logprobs fallback and do not fake logprobs. Generate repair artifacts under `outputs/dualscope_qwen2p5_7b_response_generation_repair/default`, analysis artifacts under `outputs/dualscope_qwen2p5_7b_response_generation_repair_analysis/default`, response rows JSONL when real generation succeeds, generation summary, capability/fallback flags, blocker JSON if failed, verdict JSON, next-step recommendation, docs, and tracked registry `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-response-generation-repair.json`. Verdict must be exactly one of: `Qwen2.5-7B first-slice response generation repaired`, `Partially validated`, or `Not validated`. If repaired and real response artifacts exist, next task is `dualscope-qwen2p5-7b-label-aligned-metric-computation`. If partially validated due OOM, route to `dualscope-qwen2p5-7b-quantized-response-generation-repair`; if due logprobs only, route to `dualscope-qwen2p5-7b-without-logprobs-response-generation-repair`; if due missing input, route to `dualscope-qwen2p5-7b-response-input-artifact-repair`; otherwise stay on this repair task. Do not train, do not run a full matrix, do not fabricate responses/logprobs/metrics, do not modify benchmark truth or gates, do not continue route_c, and do not generate 199+. Follow AGENTS.md PR workflow without force push, branch deletion, or remote rewrite.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B first-slice response generation repaired"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_response_generation_repair/default/dualscope_qwen2p5_7b_response_generation_repair_verdict.json",
        "outputs/dualscope_qwen2p5_7b_response_generation_repair_analysis/default/dualscope_qwen2p5_7b_response_generation_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-label-aligned-metric-computation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-response-generation-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-response-generation-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-label-aligned-metric-computation",
      "purpose": "Compute label-aligned metrics for Qwen2.5-7B first-slice if responses and scores are available.",
      "expected_inputs": [
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default",
        "outputs/dualscope_minimal_first_slice_condition_level_rerun/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-label-aligned-metric-computation.md",
        "src/eval/dualscope_qwen2p5_7b_label_aligned_metric_computation.py",
        "scripts/build_dualscope_qwen2p5_7b_label_aligned_metric_computation.py",
        "docs/dualscope_qwen2p5_7b_label_aligned_metric_computation.md",
        "outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default"
      ],
      "branch_name_suggestion": "codex/dualscope-qwen2p5-7b-label-metrics",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, Qwen2.5-7B response artifacts, first-slice labels, and condition-level score artifacts first. Compute Qwen2.5-7B first-slice metrics only when labels, scores, and real responses align. Compute AUROC/AUPRC/F1/Accuracy only for aligned detection_label and final_risk_score. Compute ASR and clean utility only from real model responses and eligible rows. If unavailable, output explicit blockers and availability matrices. Do not fake metrics, responses, logprobs, benchmark truth, gates, route_c, or 199+. Final verdicts: Qwen2.5-7B label-aligned metrics validated, Partially validated, or Not validated. Follow AGENTS.md PR workflow without auto merge, force push, branch deletion, or remote rewrite.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B label-aligned metrics validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default/dualscope_qwen2p5_7b_label_aligned_metric_computation_verdict.json",
        "outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation_analysis/default/dualscope_qwen2p5_7b_label_aligned_metric_computation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-first-slice-result-package",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-metric-computation-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-metric-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-metric-blocker-closure",
      "purpose": "Close the Qwen2.5-7B first-slice metric blocker by either computing only label-aligned metrics that are truly supported by available labels, scores, and response artifacts, or producing explicit blocker artifacts for unavailable metrics.",
      "expected_inputs": [
        ".plans/dualscope-qwen2p5-7b-metric-blocker-closure.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-label-aligned-metric-computation.json",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default",
        "outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default",
        "outputs/dualscope_minimal_first_slice_condition_level_rerun/default",
        "outputs/dualscope_first_slice_condition_row_level_fusion_alignment/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-metric-blocker-closure.md",
        "docs/dualscope_qwen2p5_7b_metric_blocker_closure.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-blocker-closure.json",
        "outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default",
        "outputs/dualscope_qwen2p5_7b_metric_blocker_closure_analysis/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-metric-blocker-closure",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, `.plans/dualscope-qwen2p5-7b-metric-blocker-closure.md`, the label-aligned metric computation `Not validated` registry, and the current Qwen2.5-7B response artifacts first. This is an experiment blocker-closure task, not a plan-only task: do not only write plans, docs, or registries. Determine why `dualscope-qwen2p5-7b-label-aligned-metric-computation` is Not validated by inspecting labels, `final_risk_score`, detection labels, real Qwen2.5-7B response rows, target_text, reference_response, ASR eligibility, clean utility eligibility, and logprob/capability flags. Run the existing metric CLI when inputs are sufficient: `.venv/bin/python scripts/build_dualscope_qwen2p5_7b_label_aligned_metric_computation.py --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl --response-dir outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default --score-dir outputs/dualscope_minimal_first_slice_condition_level_rerun/default --output-dir outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default` or an equivalent supported invocation from `--help`. Compute AUROC, AUPRC, F1, accuracy, and TPR@low-FPR only when `detection_label` and `final_risk_score` align. Compute ASR only when eligible rows have real `model_response` and target text. Compute clean utility only when eligible clean rows have real responses and reference responses. If metrics cannot be computed, write explicit blocker artifacts under `outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default` that separate missing final_risk_score, missing detection_label alignment, missing ASR inputs, missing utility inputs, missing response artifacts, logprob unavailable fallback, schema mismatch, and runtime errors. Also write a tracked verdict registry `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-blocker-closure.json`. Final verdict must be exactly one of: `Qwen2.5-7B metric blocker closure validated`, `Partially validated`, or `Not validated`. If closure validates that metrics are available and computed, next task is `dualscope-qwen2p5-7b-first-slice-result-package`. If closure validates that only a repair remains, route to `dualscope-qwen2p5-7b-metric-computation-repair`. If blockers are not automatically repairable, route to `dualscope-qwen2p5-7b-metric-blocker-closure`. Do not fabricate AUROC, AUPRC, F1, accuracy, ASR, clean utility, responses, logprobs, labels, or final_risk_score. Do not modify benchmark truth or gates, do not continue route_c, do not generate 199+, do not run a full matrix, and do not train models. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B metric blocker closure validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default/dualscope_qwen2p5_7b_metric_blocker_closure_verdict.json",
        "outputs/dualscope_qwen2p5_7b_metric_blocker_closure_analysis/default/dualscope_qwen2p5_7b_metric_blocker_closure_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-first-slice-result-package",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-metric-computation-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-metric-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-metric-computation-repair",
      "purpose": "Repair the partially validated Qwen2.5-7B label-aligned metric computation by preserving real computed detection/ASR metrics, documenting unavailable clean utility inputs, and producing a metric package that can safely feed the first-slice result package.",
      "expected_inputs": [
        ".plans/dualscope-qwen2p5-7b-metric-blocker-closure.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-label-aligned-metric-computation.json",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-blocker-closure.json",
        "outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default",
        "outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-metric-computation-repair.md",
        "docs/dualscope_qwen2p5_7b_metric_computation_repair.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-computation-repair.json",
        "outputs/dualscope_qwen2p5_7b_metric_computation_repair/default",
        "outputs/dualscope_qwen2p5_7b_metric_computation_repair_analysis/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-metric-computation-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, Qwen2.5-7B metric computation artifacts, and metric blocker closure artifacts first. This is a metric repair task, not a plan-only task. Preserve and audit real computed metrics from `outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default`: detection metrics and ASR may be reported only if their artifact status is PASS and they were computed from real Qwen2.5-7B response rows. Clean utility must remain blocked unless explicit utility success/reference-match fields exist. Produce a repair package under `outputs/dualscope_qwen2p5_7b_metric_computation_repair/default` that includes a metric availability matrix, real metric summary, unavailable metric blockers, limitations, and next-step recommendation. If the existing metric CLI has not been run in the current worktree, run `.venv/bin/python scripts/build_dualscope_qwen2p5_7b_label_aligned_metric_computation.py --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl --response-dir outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default --condition-level-dir outputs/dualscope_minimal_first_slice_condition_level_rerun/default --output-dir outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default --no-full-matrix` or an equivalent supported invocation. Do not infer clean utility from free text. Do not fabricate AUROC, AUPRC, F1, accuracy, ASR, clean utility, responses, logprobs, labels, or final_risk_score. Do not modify benchmark truth or gates, do not continue route_c, do not generate 199+, do not run a full matrix, and do not train models. Final verdicts: `Qwen2.5-7B metric computation repair validated`, `Partially validated`, or `Not validated`. If detection metrics and ASR are real and clean utility blocker is explicit, next task may be `dualscope-qwen2p5-7b-first-slice-result-package` with limitations. If essential detection metrics are unavailable, route back to `dualscope-qwen2p5-7b-metric-blocker-closure`. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B metric computation repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_metric_computation_repair/default/dualscope_qwen2p5_7b_metric_computation_repair_verdict.json",
        "outputs/dualscope_qwen2p5_7b_metric_computation_repair_analysis/default/dualscope_qwen2p5_7b_metric_computation_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-first-slice-result-package",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-first-slice-result-package",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-metric-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-first-slice-result-package",
      "purpose": "Package Qwen2.5-7B first-slice results and limitations.",
      "expected_inputs": [
        "outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-first-slice-result-package.md",
        "docs/dualscope_qwen2p5_7b_first_slice_result_package.md",
        "outputs/dualscope_qwen2p5_7b_first_slice_result_package/default"
      ],
      "branch_name_suggestion": "codex/dualscope-qwen2p5-7b-result-package",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Package Qwen2.5-7B first-slice results and limitations only. Separate real metrics, projected metrics, placeholders, blockers, ASR readiness, clean utility readiness, and cost notes. Do not claim full paper performance, do not fake metrics or responses, and do not change benchmark truth, gates, route_c, or 199+. Final verdicts: Qwen2.5-7B first-slice result package validated, Partially validated, or Not validated. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B first-slice result package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_first_slice_result_package/default/dualscope_qwen2p5_7b_first_slice_result_package_verdict.json",
        "outputs/dualscope_qwen2p5_7b_first_slice_result_package_analysis/default/dualscope_qwen2p5_7b_first_slice_result_package_verdict.json"
      ],
      "next_task_if_validated": "dualscope-sci3-main-experiment-expansion-plan",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-result-package-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-result-package-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-result-package-repair",
      "purpose": "Repair the partially validated Qwen2.5-7B first-slice result package by preserving real detection/ASR metrics, explicitly documenting clean-utility unavailability, and producing a limitations-aware package that can safely feed SCI3 expansion planning.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-first-slice-result-package.json",
        "outputs/dualscope_qwen2p5_7b_first_slice_result_package/default",
        "outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default",
        "outputs/dualscope_qwen2p5_7b_metric_computation_repair/default",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-result-package-repair.md",
        "docs/dualscope_qwen2p5_7b_result_package_repair.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-result-package-repair.json",
        "outputs/dualscope_qwen2p5_7b_result_package_repair/default",
        "outputs/dualscope_qwen2p5_7b_result_package_repair_analysis/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-result-package-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the Qwen2.5-7B first-slice result package artifacts, metric computation repair artifacts, and real response artifacts first. This is a result-package repair task, not a plan-only task. Preserve real metrics only: detection metrics and ASR may be reported only from PASS artifacts computed from real Qwen2.5-7B response rows. Clean utility must remain explicitly blocked unless an explicit utility success/reference-match field exists; do not infer utility from free text. Produce a repaired package under `outputs/dualscope_qwen2p5_7b_result_package_repair/default` that contains a real metric summary, limitation matrix, unavailable metric blockers, clean-utility blocker, SCI3 expansion readiness note, report, verdict, and tracked registry `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-result-package-repair.json`. If detection metrics and ASR are real and clean utility is explicitly blocked, final verdict may be `Qwen2.5-7B result package repair validated` and next task is `dualscope-sci3-main-experiment-expansion-plan`. If real detection/ASR evidence is unavailable, final verdict is `Partially validated` or `Not validated` and route to `dualscope-qwen2p5-7b-result-package-blocker-closure`. Do not fabricate AUROC, AUPRC, F1, accuracy, ASR, clean utility, responses, logprobs, labels, or final_risk_score. Do not claim full paper performance, do not modify benchmark truth or gates, do not continue route_c, do not generate 199+, do not run a full matrix, and do not train models. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B result package repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_result_package_repair/default/dualscope_qwen2p5_7b_result_package_repair_verdict.json",
        "outputs/dualscope_qwen2p5_7b_result_package_repair_analysis/default/dualscope_qwen2p5_7b_result_package_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-sci3-main-experiment-expansion-plan",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-result-package-blocker-closure",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-result-package-blocker-closure"
    },
    {
      "task_id": "dualscope-sci3-main-experiment-expansion-plan",
      "purpose": "Plan expansion from first-slice to SCI3 main experiment: Alpaca / AdvBench / JBB, 3 triggers, 2 targets, 7B main model.",
      "expected_inputs": [
        "outputs/dualscope_qwen2p5_7b_first_slice_result_package/default",
        "docs/dualscope_sci3_experimental_track.md",
        "docs/dualscope_sci3_metrics_and_tables.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-sci3-main-experiment-expansion-plan.md",
        "docs/dualscope_sci3_main_experiment_expansion_plan.md",
        "outputs/dualscope_sci3_main_experiment_expansion_plan/default"
      ],
      "branch_name_suggestion": "codex/dualscope-sci3-main-expansion-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Plan expansion from Qwen2.5-7B first-slice to the SCI3 main experiment only; do not execute the full matrix. Cover Stanford Alpaca, AdvBench, JBB-Behaviors; lexical, semantic, contextual/instruction triggers; fixed-response and behavior-shift targets; baselines including illumination-only, confidence-only with/without logprobs, naive concat, and DualScope budget-aware fusion. Include cost, robustness, ablation, and table plans. Do not fake metrics, responses, benchmark truth, gates, route_c, or 199+. Final verdicts: SCI3 main experiment expansion plan validated, Partially validated, or Not validated. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "SCI3 main experiment expansion plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_sci3_main_experiment_expansion_plan/default/dualscope_sci3_main_experiment_expansion_plan_verdict.json",
        "outputs/dualscope_sci3_main_experiment_expansion_plan_analysis/default/dualscope_sci3_main_experiment_expansion_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-cross-model-validation-plan",
      "next_task_if_partially_validated": "dualscope-sci3-main-experiment-expansion-plan-repair",
      "next_task_if_not_validated": "dualscope-sci3-main-experiment-expansion-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-sci3-main-experiment-expansion-plan-repair",
      "purpose": "Repair the partially validated SCI3 main experiment expansion plan by closing missing planning artifacts and producing a validated, non-executing expansion plan for the next SCI3 stage.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-sci3-main-experiment-expansion-plan.json",
        "outputs/dualscope_sci3_main_experiment_expansion_plan/default",
        "docs/dualscope_sci3_experimental_track.md",
        "docs/dualscope_sci3_metrics_and_tables.md",
        "docs/dualscope_sci3_model_matrix.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-sci3-main-experiment-expansion-plan-repair.md",
        "docs/dualscope_sci3_main_experiment_expansion_plan_repair.md",
        ".reports/dualscope_task_verdicts/dualscope-sci3-main-experiment-expansion-plan-repair.json",
        "outputs/dualscope_sci3_main_experiment_expansion_plan_repair/default",
        "outputs/dualscope_sci3_main_experiment_expansion_plan_repair_analysis/default"
      ],
      "branch_name_suggestion": "codex/sci3-main-experiment-expansion-plan-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the partially validated SCI3 main experiment expansion plan registry, and existing SCI3 docs first. This is a planning repair task only: do not execute the full matrix, do not train, and do not generate new model responses. Repair missing or incompatible planning artifacts for a staged SCI3 expansion from the Qwen2.5-7B first-slice result package to main slices: Stanford Alpaca / AdvBench / JBB-Behaviors, lexical / semantic / contextual triggers, fixed-response and behavior-shift targets, illumination-only, confidence-only with-logprobs, confidence-only without-logprobs, naive concat, and DualScope budget-aware fusion baselines. Explicitly preserve first-slice limitations: only 8 real Qwen2.5-7B responses, detection metrics and ASR are first-slice only, clean utility remains blocked until explicit utility success/reference-match evidence exists, and no full-paper performance is claimed. Produce repaired planning artifacts, a validation log, report, verdict, next-step recommendation, and tracked registry `.reports/dualscope_task_verdicts/dualscope-sci3-main-experiment-expansion-plan-repair.json`. Final verdicts: `SCI3 main experiment expansion plan repair validated`, `Partially validated`, or `Not validated`. If validated, next task is `dualscope-cross-model-validation-plan`. Do not fabricate metrics, responses, logprobs, labels, model availability, benchmark truth, gates, route_c, or 199+. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "SCI3 main experiment expansion plan repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_sci3_main_experiment_expansion_plan_repair/default/dualscope_sci3_main_experiment_expansion_plan_repair_verdict.json",
        "outputs/dualscope_sci3_main_experiment_expansion_plan_repair_analysis/default/dualscope_sci3_main_experiment_expansion_plan_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-cross-model-validation-plan",
      "next_task_if_partially_validated": "dualscope-sci3-main-experiment-expansion-plan-blocker-closure",
      "next_task_if_not_validated": "dualscope-sci3-main-experiment-expansion-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-cross-model-validation-plan",
      "purpose": "Plan cross-model validation with Llama-3.1-8B or Mistral-7B.",
      "expected_inputs": [
        "outputs/dualscope_sci3_main_experiment_expansion_plan/default",
        "docs/dualscope_sci3_model_matrix.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-cross-model-validation-plan.md",
        "docs/dualscope_cross_model_validation_plan.md",
        "outputs/dualscope_cross_model_validation_plan/default"
      ],
      "branch_name_suggestion": "codex/dualscope-cross-model-validation-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Plan cross-model validation with Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 only. Verify whether local resources exist; if missing, mark planned/external-resource-required and do not fake availability. Do not execute full matrix, do not train, do not fake responses or metrics, do not change benchmark truth, gates, route_c, or 199+. Final verdicts: Cross-model validation plan validated, Partially validated, or Not validated. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Cross-model validation plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_cross_model_validation_plan/default/dualscope_cross_model_validation_plan_verdict.json",
        "outputs/dualscope_cross_model_validation_plan_analysis/default/dualscope_cross_model_validation_plan_verdict.json"
      ],
      "next_task_if_validated": null,
      "next_task_if_partially_validated": "dualscope-cross-model-validation-plan-repair",
      "next_task_if_not_validated": "dualscope-cross-model-validation-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-cross-model-validation-plan-repair",
      "purpose": "Repair the partially validated cross-model validation plan by explicitly separating locally available resources from planned external-resource-required candidates.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-cross-model-validation-plan.json",
        "outputs/dualscope_cross_model_validation_plan/default",
        "docs/dualscope_sci3_model_matrix.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-cross-model-validation-plan-repair.md",
        "docs/dualscope_cross_model_validation_plan_repair.md",
        ".reports/dualscope_task_verdicts/dualscope-cross-model-validation-plan-repair.json",
        "outputs/dualscope_cross_model_validation_plan_repair/default",
        "outputs/dualscope_cross_model_validation_plan_repair_analysis/default"
      ],
      "branch_name_suggestion": "codex/cross-model-validation-plan-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the partially validated cross-model validation plan registry, and existing SCI3 model matrix docs first. This is a planning repair task only: do not download gated models, do not execute full matrix, do not train, and do not generate responses. Verify and document local availability for Llama-3.1-8B-Instruct and Mistral-7B-Instruct-v0.3 candidates if paths exist; if missing, mark each as `planned` / `external-resource-required` with no fake availability. Preserve Qwen2.5-7B as the main model and Qwen2.5-1.5B as pilot/ablation only. Produce repaired planning artifacts, candidate availability matrix, license/auth blockers, next-step recommendation, report, verdict, and tracked registry `.reports/dualscope_task_verdicts/dualscope-cross-model-validation-plan-repair.json`. Final verdicts: `Cross-model validation plan repair validated`, `Partially validated`, or `Not validated`. If validated, next task is `queue_complete`. Do not fabricate model paths, responses, logprobs, AUROC/F1/ASR/utility, benchmark truth, gates, route_c, or 199+. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Cross-model validation plan repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_cross_model_validation_plan_repair/default/dualscope_cross_model_validation_plan_repair_verdict.json",
        "outputs/dualscope_cross_model_validation_plan_repair_analysis/default/dualscope_cross_model_validation_plan_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-plan",
      "next_task_if_partially_validated": "dualscope-cross-model-validation-plan-blocker-closure",
      "next_task_if_not_validated": "dualscope-cross-model-validation-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-alpaca-main-slice-plan",
      "purpose": "Plan the next small-step Qwen2.5-7B Stanford Alpaca main-slice expansion from the completed first-slice smoke results without executing a full matrix.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-result-package-repair.json",
        ".reports/dualscope_task_verdicts/dualscope-cross-model-validation-plan-repair.json",
        "outputs/dualscope_qwen2p5_7b_response_generation_repair/default",
        "outputs/dualscope_qwen2p5_7b_metric_computation_repair/default",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "models/qwen2p5-7b-instruct"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-alpaca-main-slice-plan.md",
        "docs/dualscope_qwen2p5_7b_alpaca_main_slice_plan.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-alpaca-main-slice-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the Qwen2.5-7B first-slice result package, metric repair artifacts, and cross-model readiness plan first. This is a small-step expansion planning task only. Plan a Qwen2.5-7B Stanford Alpaca main-slice expansion that grows beyond the 8-response first-slice smoke while remaining bounded: no full matrix, no new model axis, no training, no route_c, and no 199+. Explicitly state that the current 8 Qwen2.5-7B responses are first-slice smoke evidence, not full paper results; detection metrics and ASR are first-slice only; clean utility remains blocked unless explicit utility success/reference-match fields are generated later; cross-model validation remains readiness only. Preserve Qwen2.5-7B as the main experimental model and Qwen2.5-1.5B as pilot/debug/ablation only. Define main-slice size, input artifact contract, response generation CLI plan, budget limits, risk controls, expected artifacts, and go/no-go criteria. Do not execute response generation in this task, do not fabricate responses/logprobs/AUROC/F1/ASR/clean utility, and do not modify benchmark truth or gates. Produce plan artifacts, report, verdict, next-step recommendation, and tracked registry. Final verdicts: `Qwen2.5-7B Alpaca main-slice plan validated`, `Partially validated`, or `Not validated`. If validated, next task is `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation`. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B Alpaca main-slice plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default/dualscope_qwen2p5_7b_alpaca_main_slice_plan_verdict.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan_analysis/default/dualscope_qwen2p5_7b_alpaca_main_slice_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-plan-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation",
      "purpose": "Execute a bounded Qwen2.5-7B Stanford Alpaca main-slice response-generation expansion after the main-slice plan is validated, without running a full matrix.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default",
        "models/qwen2p5-7b-instruct",
        "/mnt/sda3/lh/models/qwen2p5-7b-instruct"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.md",
        "docs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-alpaca-main-slice-response-generation",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the validated Alpaca main-slice plan first. This is an execution task, but it must remain a small-step expansion: Qwen2.5-7B only, Stanford Alpaca only, bounded main-slice only, lexical trigger baseline first, fixed target first, no full matrix, no training, no route_c, and no 199+. Use `/mnt/sda3/lh/models/qwen2p5-7b-instruct` through `models/qwen2p5-7b-instruct`, `HF_HOME=/mnt/sda3/lh/huggingface`, `TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers`, `HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub`, `TMPDIR=/mnt/sda3/lh/tmp`, and `CUDA_VISIBLE_DEVICES=2,3`. Execute the response-generation CLI defined by the plan or an equivalent supported invocation. If generation succeeds, write real response JSONL rows, summary, capability/fallback flags, report, verdict, and tracked registry. If GPU/OOM/model/logprob/runtime blockers occur, write explicit blocker artifacts; do not fake responses or logprobs. Do not compute final metrics in this task except availability summaries. Final verdicts: `Qwen2.5-7B Alpaca main-slice response generation validated`, `Partially validated`, or `Not validated`. If validated, next task is `dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation`. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B Alpaca main-slice response generation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_verdict.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_analysis/default/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair",
      "purpose": "Repair the bounded Qwen2.5-7B Stanford Alpaca main-slice response generation after a real runtime blocker, producing real responses or explicit blocker artifacts without falling back to plan-only packaging.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.json",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default",
        "models/qwen2p5-7b-instruct",
        "/mnt/sda3/lh/models/qwen2p5-7b-instruct"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.md",
        "docs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair_analysis/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-alpaca-main-slice-response-generation-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the Alpaca main-slice response-generation registry, and the previous generation blockers first. This is an execution-required repair task, not a plan-only task. Do not create only plans, docs, registry, or scaffold. Diagnose why the previous run recorded `cuda_unavailable_cpu_generation_disabled` even though `nvidia-smi` may show GPUs: check `.venv` Python, `torch.cuda.is_available()`, `torch.version.cuda`, selected devices, `CUDA_VISIBLE_DEVICES=2,3`, `accelerate`, `bitsandbytes`, model path binding, and free GPU memory. Use `HF_HOME=/mnt/sda3/lh/huggingface`, `TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers`, `HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub`, `TMPDIR=/mnt/sda3/lh/tmp`, and model path `/mnt/sda3/lh/models/qwen2p5-7b-instruct`. Execute the bounded repair CLI, adapting only to supported arguments: `.venv/bin/python scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair.py --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct --input-jsonl data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl --plan-verdict .reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json --output-dir outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default --registry-path .reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json --max-source-examples 4 --expected-response-rows 8 --batch-size 1 --max-new-tokens 32 --max-generation-attempts 8 --load-in-4bit --allow-without-logprobs`. If that succeeds, preserve real response rows and repair verdict artifacts; if it fails due missing dependency, install only the minimal missing package in `.venv`, record it, and rerun once. If 4-bit fails, retry without `--load-in-4bit` only if memory checks make it safe. If OOM or CUDA/model runtime still fails, write explicit blocker artifacts with blocker_type such as `oom`, `cuda_unavailable`, `torch_cuda_unavailable`, `missing_dependency`, `model_load_failure`, `logprob_unavailable`, or `runtime_error`. Do not fake responses, logprobs, labels, or metrics. Do not compute final metrics in this task. Required success evidence is response JSONL with at least one real model response; qualified failure evidence is blocker JSON with an explicit blocker_type. Generate repair summary, report, verdict, recommendation, and tracked registry. Verdicts: `Qwen2.5-7B Alpaca main-slice response generation repaired`, `Partially validated`, or `Not validated`. If repaired with real responses, next task is `dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation`; if partially validated due GPU/CUDA/OOM/runtime, route to the matching blocker repair or closure and do not repeat plan-only packaging. Never modify benchmark truth or gates, never continue route_c or generate 199+, never run a full matrix, and follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B Alpaca main-slice response generation repaired"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair_verdict.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair_analysis/default/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair",
      "purpose": "Repair the bounded Qwen2.5-7B Alpaca main-slice response-generation runtime dependency blocker, especially missing bitsandbytes or CUDA visibility mismatches, then rerun the bounded response-generation repair CLI or produce explicit blocker artifacts.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json",
        "requirements.txt",
        "scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair.py",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "/mnt/sda3/lh/models/qwen2p5-7b-instruct"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair.md",
        "docs/dualscope_qwen2p5_7b_alpaca_main_slice_response_dependency_repair.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_dependency_repair/default",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-alpaca-main-slice-response-dependency-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the Alpaca main-slice response-generation repair registry, and the previous blocker artifacts first. This is an execution-required dependency repair task, not a plan-only task. Diagnose the recorded `missing_dependency` / `requested_4bit_but_bitsandbytes_unavailable` blocker and the CUDA visibility context using `.venv/bin/python`, `torch.cuda.is_available()`, `torch.cuda.device_count()`, `torch.version.cuda`, `CUDA_VISIBLE_DEVICES=2,3`, `accelerate`, `bitsandbytes`, `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, and available GPU memory. Use `HF_HOME=/mnt/sda3/lh/huggingface`, `TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers`, `HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub`, and `TMPDIR=/mnt/sda3/lh/tmp`. If `bitsandbytes` is missing, install only the minimal dependency into `.venv` with `.venv/bin/python -m pip install \"bitsandbytes>=0.43,<0.47\"` using the configured proxy, record the install result, and keep `requirements.txt` aligned. Do not install unrelated packages. Then rerun the bounded repair CLI: `.venv/bin/python scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair.py --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct --input-jsonl data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl --plan-verdict .reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json --output-dir outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default --registry-path .reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json --max-source-examples 4 --expected-response-rows 8 --batch-size 1 --max-new-tokens 32 --max-generation-attempts 8 --load-in-4bit --allow-without-logprobs`. If 4-bit still fails, retry without `--load-in-4bit` only when memory checks make that safe; otherwise write explicit blocker artifacts under `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_dependency_repair/default`. Required success evidence is a response JSONL with at least one real model response. Qualified failure evidence is blocker JSON with blocker_type such as `missing_dependency`, `torch_cuda_unavailable`, `cuda_error`, `oom`, `model_load_failure`, or `runtime_error`. Do not fake responses, logprobs, labels, metrics, reviews, or CI. Do not compute final metrics in this task. Verdicts: `Qwen2.5-7B Alpaca main-slice response dependency repair validated`, `Partially validated`, or `Not validated`. If validated and real responses exist, next task is `dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation`; if still blocked, next task is `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure`. Never modify benchmark truth or gates, never continue route_c or generate 199+, never run a full matrix, and follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B Alpaca main-slice response dependency repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_dependency_repair/default/dualscope_qwen2p5_7b_alpaca_main_slice_response_dependency_repair_verdict.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_dependency_repair_analysis/default/dualscope_qwen2p5_7b_alpaca_main_slice_response_dependency_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure",
      "purpose": "Close the bounded Qwen2.5-7B Alpaca main-slice response-generation blocker with a truthful hard-blocker report after bounded generation and dependency repair attempts fail.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.json",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure.md",
        "docs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_blocker_closure.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_blocker_closure/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the bounded Alpaca response-generation, repair, and dependency-repair registries first. This is a blocker-closure task, not a response-generation task. Do not retry plan-only packaging and do not fabricate responses, logprobs, labels, metrics, reviews, or CI. Summarize the real blocker chain: zero bounded Alpaca main-slice response rows, the dependency repair attempt, missing_dependency / bitsandbytes install blocker if present, CUDA visibility diagnostics, missing input materialization diagnostics if present, and any safe retry recommendations. Produce a concise blocker report, blocker summary JSON, next manual action recommendation, and tracked registry. If the blocker is truly unresolved, verdict should be `Qwen2.5-7B Alpaca main-slice response generation blocker closed` with `validated=true` only for blocker documentation, not for response generation. The registry must state that no new model responses or metrics were produced. Next task is `dualscope-worktree-gpu-bnb-input-readiness-repair` because the user has explicitly authorized a new bounded runtime repair and response-generation retry chain. Never modify benchmark truth or gates, never continue route_c or generate 199+, never run a full matrix, and follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B Alpaca main-slice response generation blocker closed"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_blocker_closure/default/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_blocker_closure_verdict.json"
      ],
      "next_task_if_validated": "dualscope-worktree-gpu-bnb-input-readiness-repair",
      "next_task_if_partially_validated": "queue_complete",
      "next_task_if_not_validated": "queue_complete"
    },
    {
      "task_id": "dualscope-worktree-gpu-bnb-input-readiness-repair",
      "purpose": "Repair and verify isolated worktree runtime readiness for bounded Qwen2.5-7B Alpaca main-slice execution: .venv, CUDA, bitsandbytes or fallback, input materialization, model symlink, HF cache, and TMPDIR.",
      "expected_inputs": [
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl",
        "outputs/dualscope_first_slice_target_response_generation_plan/default",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default",
        "models/qwen2p5-7b-instruct",
        "/mnt/sda3/lh/models/qwen2p5-7b-instruct"
      ],
      "expected_outputs": [
        ".plans/dualscope-worktree-gpu-bnb-input-readiness-repair.md",
        "docs/dualscope_worktree_gpu_bnb_input_readiness_repair.md",
        ".reports/dualscope_task_verdicts/dualscope-worktree-gpu-bnb-input-readiness-repair.json",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/runtime_readiness_summary.json",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/worktree_cuda_check.json",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/worktree_python_dependency_check.json",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/bitsandbytes_check.json",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/input_materialization_check.json",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/model_binding_check.json",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/runtime_readiness_blockers.json",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/runtime_readiness_report.md",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/runtime_readiness_verdict.json"
      ],
      "branch_name_suggestion": "codex/worktree-gpu-bnb-input-readiness-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the previous Alpaca main-slice blocker closure first. This is an execution-required runtime readiness repair task, not a plan/docs/registry-only task. Verify the isolated worktree runtime after dependency materialization: `.venv` symlink, `.venv/bin/python`, torch import, `torch.cuda.is_available()`, `torch.cuda.device_count()`, `CUDA_VISIBLE_DEVICES=2,3`, `CUDA_DEVICE_ORDER=PCI_BUS_ID`, `nvidia-smi`, transformers, accelerate, bitsandbytes, labeled pairs, source JSONL, target-response plan output, Alpaca main-slice plan output, repo model symlink, `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, `HF_HOME=/mnt/sda3/lh/huggingface`, `HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub`, `TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers`, and `TMPDIR=/mnt/sda3/lh/tmp`. Run `.venv/bin/python scripts/build_dualscope_worktree_gpu_bnb_input_readiness_repair.py --attempt-pip-install` or the equivalent supported invocation. If bitsandbytes installation fails because the proxy refuses pip, record that blocker and set `quantization_fallback=true`; if CUDA and inputs are otherwise ready, route to bounded response generation without 4-bit. If CUDA is unavailable, write explicit GPU blocker artifacts. Do not generate model responses in this task, do not fake CUDA, bitsandbytes, model paths, responses, logprobs, labels, metrics, reviews, or CI. Do not modify benchmark truth or gates, do not continue route_c, do not generate 199+, do not touch `/mnt/sda3/CoCoNut-Artifact`, and do not download 7B under `/home/lh`. Final verdicts: `Worktree GPU/BnB/input readiness validated`, `Partially validated`, or `Not validated`. If validated or partially validated with quantization fallback only, next task is `dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry`; if GPU is unavailable, route to `dualscope-worktree-gpu-readiness-blocker-closure`. Follow AGENTS.md PR workflow without force push, branch deletion, or remote rewrite.",
      "completion_verdicts": {
        "validated": [
          "Worktree GPU/BnB/input readiness validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default/runtime_readiness_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry",
      "next_task_if_not_validated": "dualscope-worktree-gpu-readiness-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry",
      "purpose": "Retry bounded Qwen2.5-7B Alpaca main-slice response generation after explicit worktree runtime readiness repair, producing real responses or explicit blocker artifacts only.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-worktree-gpu-bnb-input-readiness-repair.json",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default",
        "models/qwen2p5-7b-instruct",
        "/mnt/sda3/lh/models/qwen2p5-7b-instruct"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry.md",
        "docs/dualscope_qwen2p5_7b_alpaca_main_slice_bounded_response_generation_retry.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_responses.jsonl",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_generation_summary.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_generation_blockers.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_generation_report.md",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_generation_verdict.json"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the worktree runtime readiness registry first. This is an execution-required bounded response-generation retry. Do not create only plan/docs/registry/scaffold. Use Qwen2.5-7B at `/mnt/sda3/lh/models/qwen2p5-7b-instruct` through `models/qwen2p5-7b-instruct`, `HF_HOME=/mnt/sda3/lh/huggingface`, `HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub`, `TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers`, `TMPDIR=/mnt/sda3/lh/tmp`, `CUDA_VISIBLE_DEVICES=2,3`, and `CUDA_DEVICE_ORDER=PCI_BUS_ID`. Run `.venv/bin/python scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct --input-jsonl data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl --plan-verdict .reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json --output-dir outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default --registry-path .reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry.json --max-source-examples 16 --expected-response-rows 32 --batch-size 1 --max-new-tokens 64 --max-generation-attempts 32 --allow-without-logprobs`. Add `--load-in-4bit` only if bitsandbytes is available; otherwise use fp16/low-memory fallback. If OOM or runtime failure occurs, retry once with `--max-source-examples 4 --expected-response-rows 8 --max-new-tokens 32 --max-generation-attempts 8`. Success requires a response JSONL with row_count > 0 and real `model_response` values. Qualified failure requires blocker JSON with explicit blocker_type such as `oom`, `cuda_error`, `torch_cuda_unavailable`, `missing_dependency`, `model_load_failure`, `logprob_unavailable`, `missing_input`, or `runtime_error`. Do not fake responses, logprobs, labels, metrics, reviews, or CI. Do not compute metrics here. No full Alpaca, no full matrix, no training, no route_c, no 199+, no benchmark truth or gate changes. Verdicts: `Qwen2.5-7B Alpaca main-slice bounded response generation validated`, `Partially validated`, or `Not validated`. If validated, next task is `dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation`; if partially validated, route to `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair`. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B Alpaca main-slice bounded response generation validated",
          "Qwen2.5-7B Alpaca main-slice response generation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_generation_verdict.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure"
    },
    {
      "task_id": "dualscope-worktree-gpu-readiness-blocker-closure",
      "purpose": "Truthfully close an unrepaired worktree GPU/CUDA runtime blocker without fabricating Qwen2.5-7B responses or metrics.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-worktree-gpu-bnb-input-readiness-repair.json",
        "outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-worktree-gpu-readiness-blocker-closure.md",
        "docs/dualscope_worktree_gpu_readiness_blocker_closure.md",
        ".reports/dualscope_task_verdicts/dualscope-worktree-gpu-readiness-blocker-closure.json"
      ],
      "branch_name_suggestion": "codex/worktree-gpu-readiness-blocker-closure",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the worktree runtime readiness artifacts first. This is a blocker closure, not a generation task. Summarize the real GPU/CUDA/.venv/bitsandbytes/input blocker chain and manual action required. Do not fabricate responses, logprobs, metrics, CUDA success, reviews, or CI. Do not modify benchmark truth or gates, do not route_c, do not generate 199+, and do not touch `/mnt/sda3/CoCoNut-Artifact`. Verdicts: `Worktree GPU readiness blocker closed`, `Partially validated`, or `Not validated`. Next task is `queue_complete` unless a future user explicitly authorizes another resource repair. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Worktree GPU readiness blocker closed"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_worktree_gpu_readiness_blocker_closure/default/verdict.json"
      ],
      "next_task_if_validated": "dualscope-external-gpu-runner-for-qwen2p5-7b-generation",
      "next_task_if_partially_validated": "queue_complete",
      "next_task_if_not_validated": "queue_complete"
    },
    {
      "task_id": "dualscope-external-gpu-runner-for-qwen2p5-7b-generation",
      "purpose": "Run bounded Qwen2.5-7B Alpaca main-slice response generation in an external GPU-visible shell runner instead of the codex exec sandbox.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-worktree-gpu-readiness-blocker-closure.json",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_first_slice_target_response_generation_plan/default",
        "/mnt/sda3/lh/models/qwen2p5-7b-instruct",
        "models/qwen2p5-7b-instruct"
      ],
      "expected_outputs": [
        ".plans/dualscope-external-gpu-runner-for-qwen2p5-7b-generation.md",
        "docs/dualscope_external_gpu_runner_qwen2p5_7b.md",
        ".reports/dualscope_task_verdicts/dualscope-external-gpu-runner-for-qwen2p5-7b-generation.json",
        "outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_summary.json",
        "outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_responses.jsonl",
        "outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_blockers.json",
        "outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_report.md",
        "outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_verdict.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_responses.jsonl"
      ],
      "branch_name_suggestion": "codex/external-gpu-runner-qwen2p5-7b",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the worktree GPU blocker closure first. This task exists because codex exec isolated worktrees cannot see CUDA, while the host shell can. Do not run real Qwen2.5-7B generation inside codex exec. Use the external runner `scripts/run_dualscope_qwen2p5_7b_external_gpu_generation.sh` from the normal shell/nohup environment with `CUDA_VISIBLE_DEVICES=2,3`, `CUDA_DEVICE_ORDER=PCI_BUS_ID`, `HF_HOME=/mnt/sda3/lh/huggingface`, `HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub`, `TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers`, and `TMPDIR=/mnt/sda3/lh/tmp`. The runner must call `.venv/bin/python scripts/build_dualscope_qwen2p5_7b_external_gpu_generation.py --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl --target-response-plan-dir outputs/dualscope_first_slice_target_response_generation_plan/default --output-dir outputs/dualscope_qwen2p5_7b_external_gpu_generation/default --max-examples 8 --batch-size 1 --max-new-tokens 64 --device-map auto --allow-without-logprobs`. Success requires torch CUDA available in the external runner, model load success, and external response JSONL row_count > 0 with real model_response values; if generation succeeds, synchronize outputs to `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default`. Qualified failure requires explicit blocker JSON for OOM, model_load_failure, cuda_error, torch_cuda_unavailable, missing_dependency, missing_input, or runtime_error. Do not fake responses, logprobs, labels, metrics, reviews, or CI. Do not train, do not full matrix, do not change benchmark truth or gates, do not route_c, do not generate 199+, and do not touch `/mnt/sda3/CoCoNut-Artifact`. Verdicts: `Qwen2.5-7B external GPU generation validated`, `Partially validated`, or `Not validated`. If validated, next task is `dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation`; if OOM, route to `dualscope-qwen2p5-7b-external-gpu-oom-repair`; if model load fails, route to `dualscope-qwen2p5-7b-model-load-blocker-closure`; otherwise route to external runner repair.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B external GPU generation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_verdict.json",
        "outputs/dualscope_qwen2p5_7b_external_gpu_generation_analysis/default/external_gpu_generation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-external-gpu-runner-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-external-gpu-runner-repair"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation",
      "purpose": "Compute available bounded Qwen2.5-7B Alpaca main-slice detection, ASR, cost, and fallback-readiness metrics from real response artifacts without fabricating clean utility or logprobs.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.json",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation.md",
        "docs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-alpaca-main-slice-metric-computation",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the bounded Alpaca main-slice response artifacts first. Compute only metrics that are supported by real labels, final_risk_score or available score fields, and real model_response rows. Allowed outputs include detection metrics, ASR, target behavior success readiness, query cost summary, without-logprobs fallback summaries, metric availability matrix, blockers, report, verdict, recommendation, and tracked registry. Do not fabricate clean utility, logprobs, AUROC/F1/ASR, labels, responses, benchmark truth, or gate decisions. If detection labels and scores do not align, output a metric blocker instead of fake AUROC/F1. If ASR inputs are absent, output a blocker. Clean utility remains blocked unless clean response and reference_response eligibility are explicitly available. No full matrix, no training, no route_c, no 199+. Verdicts: `Qwen2.5-7B Alpaca main-slice metrics validated`, `Partially validated`, or `Not validated`. If validated or partially validated with honest blockers, next task is `dualscope-qwen2p5-7b-alpaca-main-slice-result-package`. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B Alpaca main-slice metrics validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation/default/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-result-package",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-result-package",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-metric-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-alpaca-main-slice-result-package",
      "purpose": "Package bounded Qwen2.5-7B Alpaca main-slice response and metric evidence while separating real metrics, fallback metrics, blocked metrics, and limitations.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation/default",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-alpaca-main-slice-result-package.md",
        "docs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-result-package.json",
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-alpaca-main-slice-result-package",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Package the bounded Qwen2.5-7B Alpaca main-slice results after metric computation. Clearly separate real response counts, real computed metrics, without-logprobs fallback indicators, blocked clean utility, limitations, and next actions. This package must not claim full paper performance, full Alpaca coverage, full trigger coverage, cross-model validation, or clean utility success unless artifacts prove it. Produce summary, metric availability matrix, table skeleton, limitations, blocker summary, report, verdict, recommendation, and tracked registry. Do not fabricate responses, logprobs, AUROC/F1/ASR/utility, labels, benchmark truth, gates, route_c, or 199+. Verdicts: `Qwen2.5-7B Alpaca main-slice result package validated`, `Partially validated`, or `Not validated`. If validated or partially validated with honest blockers, next task is `dualscope-qwen2p5-7b-semantic-trigger-smoke-plan`. Follow AGENTS.md PR workflow without force push, branch deletion, remote rewrite, or merging unrelated PRs.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B Alpaca main-slice result package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/dualscope_qwen2p5_7b_alpaca_main_slice_result_package_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-plan",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-plan",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-alpaca-main-slice-result-package-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-semantic-trigger-smoke-plan",
      "purpose": "Plan a minimal semantic-trigger smoke extension for Qwen2.5-7B after Alpaca main-slice readiness, without executing a trigger family matrix.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-result-package.json",
        "docs/dualscope_sci3_experiment_scope_control.md",
        "docs/dualscope_sci3_next_real_expansion_track.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-semantic-trigger-smoke-plan.md",
        "docs/dualscope_qwen2p5_7b_semantic_trigger_smoke_plan.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-plan.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_plan/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-semantic-trigger-smoke-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Plan exactly one small semantic-trigger smoke for Qwen2.5-7B. Do not execute the smoke in this task. Keep Stanford Alpaca and Qwen2.5-7B fixed; introduce only the semantic trigger design contract, target compatibility check, sample budget, expected artifacts, and blocker conditions. Do not expand to contextual triggers, AdvBench, JBB, cross-model validation, full matrix, training, route_c, or 199+. Preserve clean utility blocker honesty and do not fabricate metrics, responses, logprobs, labels, or benchmark truth. Final verdicts: `Qwen2.5-7B semantic trigger smoke plan validated`, `Partially validated`, or `Not validated`. If validated, next task is `dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan`. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B semantic trigger smoke plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_plan/default/dualscope_qwen2p5_7b_semantic_trigger_smoke_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-plan-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan",
      "purpose": "Plan one minimal behavior-shift target smoke for Qwen2.5-7B while keeping dataset, model, and trigger scope bounded.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-plan.json",
        "docs/dualscope_sci3_experiment_scope_control.md",
        "docs/dualscope_sci3_next_real_expansion_track.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan.md",
        "docs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-behavior-shift-target-smoke-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Plan exactly one behavior-shift target smoke for Qwen2.5-7B. This is a planning task only: do not generate model responses, do not compute metrics, and do not run a target matrix. Keep the model as Qwen2.5-7B and the dataset path small; define behavior-shift target semantics, eligibility criteria, expected outputs, safety boundaries, and blocker conditions. Explicitly preserve that fixed-response first-slice metrics are smoke evidence and clean utility remains blocked. Do not fabricate target behavior success, ASR, utility, responses, logprobs, labels, benchmark truth, gates, route_c, or 199+. Final verdicts: `Qwen2.5-7B behavior-shift target smoke plan validated`, `Partially validated`, or `Not validated`. If validated, next task is `dualscope-advbench-small-slice-readiness-plan`. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B behavior-shift target smoke plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan/default/dualscope_qwen2p5_7b_behavior_shift_target_smoke_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-readiness-plan",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-advbench-small-slice-readiness-plan",
      "purpose": "Plan a small-slice AdvBench readiness step for DualScope SCI3 without ingesting or executing the full dataset.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan.json",
        "docs/dualscope_sci3_next_real_expansion_track.md",
        "docs/dualscope_sci3_experiment_scope_control.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-readiness-plan.md",
        "docs/dualscope_advbench_small_slice_readiness_plan.md",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-readiness-plan.json",
        "outputs/dualscope_advbench_small_slice_readiness_plan/default"
      ],
      "branch_name_suggestion": "codex/dualscope-advbench-small-slice-readiness-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Plan a small-slice AdvBench readiness step only. Do not download restricted resources, do not run AdvBench full dataset, do not generate responses, and do not compute metrics. Define source requirements, license/availability checks, small-slice schema, safety review, trigger/target compatibility, expected artifacts, and blocker routing. Preserve Qwen2.5-7B as main model and current first-slice Qwen2.5-7B results as smoke evidence only. Do not fabricate data availability, harmfulness labels, ASR, utility, responses, logprobs, benchmark truth, gates, route_c, or 199+. Final verdicts: `AdvBench small-slice readiness plan validated`, `Partially validated`, or `Not validated`. If validated, next task is `dualscope-jbb-small-slice-readiness-plan`. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice readiness plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_readiness_plan/default/dualscope_advbench_small_slice_readiness_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-jbb-small-slice-readiness-plan",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-readiness-plan-repair",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-readiness-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-jbb-small-slice-readiness-plan",
      "purpose": "Plan a small-slice JBB-Behaviors readiness step for DualScope SCI3 without executing the full benchmark.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-readiness-plan.json",
        "docs/dualscope_sci3_next_real_expansion_track.md",
        "docs/dualscope_sci3_experiment_scope_control.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-jbb-small-slice-readiness-plan.md",
        "docs/dualscope_jbb_small_slice_readiness_plan.md",
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-readiness-plan.json",
        "outputs/dualscope_jbb_small_slice_readiness_plan/default"
      ],
      "branch_name_suggestion": "codex/dualscope-jbb-small-slice-readiness-plan",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Plan a small-slice JBB-Behaviors readiness step only. Do not run the full benchmark, do not download gated data without authorization, do not generate responses, and do not compute metrics. Define data/license readiness, small-slice schema, behavior category sampling, Qwen2.5-7B execution prerequisites, expected artifacts, and blocker routing. Cross-model validation remains readiness-only unless Llama/Mistral resources and license are explicitly available. Do not fabricate model availability, responses, AUROC/F1/ASR/utility, benchmark truth, gates, route_c, or 199+. Final verdicts: `JBB small-slice readiness plan validated`, `Partially validated`, or `Not validated`. If validated, the next queue state is `queue_complete` for this expansion planning batch. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "JBB small-slice readiness plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_jbb_small_slice_readiness_plan/default/dualscope_jbb_small_slice_readiness_plan_verdict.json"
      ],
      "next_task_if_validated": "queue_complete",
      "next_task_if_partially_validated": "dualscope-jbb-small-slice-readiness-plan-repair",
      "next_task_if_not_validated": "dualscope-jbb-small-slice-readiness-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-qwen2p5-7b-semantic-trigger-smoke-response-generation",
      "purpose": "Run small-scale real Qwen2.5-7B semantic trigger smoke response generation using the external GPU runner or GPU-visible shell execution.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-plan.json",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_first_slice_target_response_generation_plan/default",
        "/mnt/sda3/lh/models/qwen2p5-7b-instruct",
        "models/qwen2p5-7b-instruct"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-semantic-trigger-smoke-response-generation.md",
        "docs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-response-generation.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default/semantic_trigger_smoke_responses.jsonl",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default/semantic_trigger_smoke_summary.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default/semantic_trigger_smoke_blockers.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default/semantic_trigger_smoke_report.md",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default/semantic_trigger_smoke_verdict.json"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-semantic-trigger-smoke-response-generation",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Execute a bounded semantic trigger smoke response generation task, not a plan-only package. Use Qwen2.5-7B at `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, Stanford Alpaca bounded slice, batch_size=1, max_examples 8 or 16, max_new_tokens=64, CUDA_VISIBLE_DEVICES=2,3, HF cache under `/mnt/sda3/lh`, and external GPU runner or GPU-visible shell if codex sandbox CUDA is unavailable. If semantic trigger spec is missing, create one minimal semantic phrase trigger spec only. Success requires `semantic_trigger_smoke_responses.jsonl` row_count > 0 with real model_response values. Qualified failure requires `semantic_trigger_smoke_blockers.json` with blocker_type such as cuda_unavailable, oom, model_load_failure, missing_input, missing_dependency, or runtime_error. Record without_logprobs_fallback when logprobs are unavailable. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B semantic trigger smoke response generation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default/semantic_trigger_smoke_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-computation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-response-generation-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-blocker-closure",
      "execution_gate_requirements": {
        "response_jsonl": "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default/semantic_trigger_smoke_responses.jsonl",
        "blocker_json": "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default/semantic_trigger_smoke_blockers.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-computation",
      "purpose": "Compute real available metrics for semantic trigger smoke responses.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-response-generation.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-computation.md",
        "docs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation.md",
        "src/eval/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation.py",
        "scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation.py",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-computation.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/available_metrics.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/readiness_matrix.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/metric_blockers.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/metric_report.md",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/metric_verdict.json"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-semantic-trigger-smoke-metric-computation",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Compute only metrics supported by real semantic-trigger response rows, labels, target rules, and available score fields. Produce available_metrics, readiness_matrix, metric_blockers, report, verdict, and tracked registry. If final_risk_score, target_match, ASR, or clean utility inputs are missing, emit explicit blockers rather than placeholders. Current without-logprobs fallback must remain explicit and no with-logprobs metrics may be claimed. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B semantic trigger smoke metrics validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/metric_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-blocker-closure",
      "execution_gate_requirements": {
        "available_metrics": "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/available_metrics.json",
        "readiness_matrix": "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/readiness_matrix.json",
        "blocker_json": "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default/metric_blockers.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package",
      "purpose": "Package semantic trigger smoke results and limitations.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-computation.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package.md",
        "docs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package.md",
        "src/eval/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package.py",
        "scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package.py",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_summary.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/metric_availability_matrix.json",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_report.md",
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_verdict.json"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-semantic-trigger-smoke-result-package",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Package semantic trigger smoke response and metric artifacts. Separate real metrics, fallback metrics, blocked metrics, limitations, and next actions. Do not claim full trigger-family performance or full matrix evidence. Produce summary, metric availability matrix, report, verdict, and tracked registry. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B semantic trigger smoke result package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-response-generation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package-blocker-closure",
      "execution_gate_requirements": {
        "summary": "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_summary.json",
        "report": "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_report.md",
        "verdict": "outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_result_package/default/result_package_verdict.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-response-generation",
      "purpose": "Run small-scale behavior-shift target smoke response generation.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan.json",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "/mnt/sda3/lh/models/qwen2p5-7b-instruct",
        "models/qwen2p5-7b-instruct"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-behavior-shift-target-smoke-response-generation.md",
        "docs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation.md",
        "src/eval/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation.py",
        "scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation.py",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-response-generation.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_responses.jsonl",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_summary.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_blockers.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_report.md",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_verdict.json"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-behavior-shift-target-smoke-response-generation",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Execute a bounded behavior-shift target smoke response generation task, not a plan-only package. Use safe behavior-shift target semantics from the plan, small safe samples, Qwen2.5-7B, batch_size=1, max_examples 8 or fewer if needed, max_new_tokens=64, and external GPU runner or GPU-visible shell. Do not generate actually dangerous content; use safety-preserving target behavior proxies or refusal/behavior-shift readiness where appropriate. Success requires real response JSONL row_count > 0. Qualified failure requires blocker JSON with a clear blocker_type. Record without_logprobs_fallback if logprobs are unavailable. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B behavior-shift target smoke response generation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-metric-computation",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-response-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-blocker-closure",
      "execution_gate_requirements": {
        "response_jsonl": "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_responses.jsonl",
        "blocker_json": "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default/behavior_shift_smoke_blockers.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-metric-computation",
      "purpose": "Compute available behavior-shift target smoke metrics.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-response-generation.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default",
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-behavior-shift-target-smoke-metric-computation.md",
        "docs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation.md",
        "src/eval/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation.py",
        "scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation.py",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-metric-computation.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/available_metrics.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/readiness_matrix.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/metric_blockers.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/metric_report.md",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/metric_verdict.json"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-behavior-shift-target-smoke-metric-computation",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Compute only available behavior-shift smoke metrics from real response rows and explicit target behavior readiness fields. Do not infer harmfulness or utility from free text. Emit blockers for missing target-success rules, ASR inputs, clean utility fields, or score alignment. Produce available_metrics, readiness_matrix, blockers, report, verdict, and tracked registry. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B behavior-shift target smoke metrics validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/metric_verdict.json"
      ],
      "next_task_if_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-metric-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-metric-blocker-closure",
      "execution_gate_requirements": {
        "available_metrics": "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/available_metrics.json",
        "readiness_matrix": "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/readiness_matrix.json",
        "blocker_json": "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default/metric_blockers.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package",
      "purpose": "Package behavior-shift target smoke results.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-metric-computation.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_response_generation/default",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_metric_computation/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package.md",
        "docs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package.md",
        "src/eval/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package.py",
        "scripts/build_dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package.py",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_summary.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/metric_availability_matrix.json",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_report.md",
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_verdict.json"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-behavior-shift-target-smoke-result-package",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Package behavior-shift target smoke response and metric artifacts. Separate real results, safety-preserving proxy limitations, blockers, and next actions. Do not claim harmful behavior success, full target-family performance, or clean utility unless artifacts prove it. Produce summary, metric availability matrix, report, verdict, and tracked registry. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B behavior-shift target smoke result package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-materialization",
      "next_task_if_partially_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package-repair",
      "next_task_if_not_validated": "dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package-blocker-closure",
      "execution_gate_requirements": {
        "summary": "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_summary.json",
        "report": "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_report.md",
        "verdict": "outputs/dualscope_qwen2p5_7b_behavior_shift_target_smoke_result_package/default/result_package_verdict.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-advbench-small-slice-materialization",
      "purpose": "Materialize or validate a bounded AdvBench small-slice from local authorized data or the public Hugging Face source walledai/AdvBench; otherwise output a real blocker without fabricating data.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-readiness-plan.json",
        "docs/dualscope_advbench_small_slice_readiness_plan.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-materialization.md",
        "docs/dualscope_advbench_small_slice_materialization.md",
        "src/eval/dualscope_advbench_small_slice_materialization.py",
        "scripts/build_dualscope_advbench_small_slice_materialization.py",
        "scripts/build_post_dualscope_advbench_small_slice_materialization_analysis.py",
        "src/eval/post_dualscope_advbench_small_slice_materialization_analysis.py",
        "data/advbench/small_slice/advbench_small_slice_source.jsonl",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-materialization.json",
        "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_manifest.json",
        "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_schema_check.json",
        "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_materialization_summary.json",
        "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_blockers.json",
        "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_report.md",
        "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_verdict.json"
      ],
      "branch_name_suggestion": "codex/advbench-small-slice-materialization",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Materialize only a bounded AdvBench small slice using local authorized data or the explicitly authorized public Hugging Face source `walledai/AdvBench` with `--allow-download`. Use max_examples 16 or 32 and write standardized rows to `data/advbench/small_slice/advbench_small_slice_source.jsonl` with fields sample_id, dataset_id, instruction, input, reference_response or expected_behavior, safety_category if available, source_dataset, source_split, and source_index. Create manifest, schema check, blockers, report, verdict, post-analysis, and tracked registry artifacts. If download/read/schema fails, emit explicit blockers and do not create fake rows. No response generation or metrics in this task. Do not fabricate data, responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice materialization validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-response-generation-plan",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-download-repair",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-data-blocker-closure",
      "execution_gate_requirements": {
        "manifest": "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_manifest.json",
        "schema_check": "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_schema_check.json",
        "small_slice_jsonl": "data/advbench/small_slice/advbench_small_slice_source.jsonl",
        "blocker_json": "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_blockers.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-advbench-small-slice-download-repair",
      "purpose": "Repair AdvBench bounded small-slice download/read blockers without fabricating data.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-materialization.json",
        "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_blockers.json",
        "outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_manifest.json"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-download-repair.md",
        "docs/dualscope_advbench_small_slice_download_repair.md",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-download-repair.json",
        "outputs/dualscope_advbench_small_slice_download_repair/default/advbench_download_repair_summary.json",
        "outputs/dualscope_advbench_small_slice_download_repair/default/advbench_download_repair_blockers.json",
        "outputs/dualscope_advbench_small_slice_download_repair/default/advbench_download_repair_verdict.json"
      ],
      "branch_name_suggestion": "codex/advbench-small-slice-download-repair",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Repair only the AdvBench small-slice download/read blocker. Inspect `walledai/AdvBench` artifacts and blockers. If the Hugging Face dataset is gated or requires authentication, record a real `dataset_permission_blocker` and do not fabricate rows. If a public unauthenticated mirror or local authorized source is available, materialize at most 32 standardized rows to `data/advbench/small_slice/advbench_small_slice_source.jsonl` and rerun schema checks. Do not generate responses or metrics in this task. Do not fabricate data, labels, responses, logprobs, AUROC/F1/ASR/clean utility, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice download repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_download_repair/default/advbench_download_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-response-generation-plan",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-data-blocker-closure",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-data-blocker-closure",
      "execution_gate_requirements": {
        "summary": "outputs/dualscope_advbench_small_slice_download_repair/default/advbench_download_repair_summary.json",
        "blocker_json": "outputs/dualscope_advbench_small_slice_download_repair/default/advbench_download_repair_blockers.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-advbench-small-slice-response-generation-plan",
      "purpose": "Plan bounded AdvBench response generation without running full matrix.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-materialization.json",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-download-repair.json",
        "data/advbench/small_slice/advbench_small_slice_source.jsonl",
        "outputs/dualscope_advbench_small_slice_materialization/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-response-generation-plan.md",
        "docs/dualscope_advbench_small_slice_response_generation_plan.md",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-plan.json",
        "outputs/dualscope_advbench_small_slice_response_generation_plan/default/advbench_response_generation_plan.json",
        "outputs/dualscope_advbench_small_slice_response_generation_plan/default/advbench_response_generation_plan_verdict.json"
      ],
      "branch_name_suggestion": "codex/advbench-small-slice-response-generation-plan",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Plan bounded AdvBench response generation using only `data/advbench/small_slice/advbench_small_slice_source.jsonl` and the validated materialization/download-repair registries. Do not generate responses in this task. Define max_examples <= 16 or 32, batch_size=1, max_new_tokens=64, Qwen2.5-7B external GPU runner usage, model path `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, HF cache settings, safety-aware prompt construction, controlled safety evaluation templates for harmful instructions, without-logprobs fallback handling, expected response/summary/blocker/report/verdict artifacts, and metric readiness. Do not claim data availability beyond materialization artifacts. Do not generate actual dangerous content, do not run full matrix, and do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice response generation plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_response_generation_plan/default/advbench_response_generation_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-response-generation",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-response-generation-plan-repair",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-response-generation-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-advbench-small-slice-response-generation",
      "purpose": "Run bounded safety-aware Qwen2.5-7B response generation for the validated AdvBench small-slice, or emit a real blocker.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-plan.json",
        "data/advbench/small_slice/advbench_small_slice_source.jsonl"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-response-generation.md",
        "docs/dualscope_advbench_small_slice_response_generation.md",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_summary.json",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_blockers.json",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_report.md",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_verdict.json"
      ],
      "branch_name_suggestion": "codex/advbench-small-slice-response-generation",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Execute bounded AdvBench small-slice response generation only if safe and feasible. Use `data/advbench/small_slice/advbench_small_slice_source.jsonl`, `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, HF caches under `/mnt/sda3/lh/huggingface`, CUDA devices 2,3, max_examples <= 16 or 32, batch_size=1, and max_new_tokens=64. Prefer the external GPU runner/worktree flow instead of forcing CUDA inside the Codex sandbox. Use safety-aware prompt construction or controlled safety evaluation templates for harmful instructions and do not generate actionable dangerous content. If logprobs are unavailable, record `without_logprobs_fallback=true`. Write real responses only when produced by the model; otherwise write a blocker JSON with explicit blocker_type and do not mark validated. Response rows must include sample_id, dataset_id, instruction, model_response, generation_mode, capability_flags, safety_mode, and without_logprobs_fallback. Do not fabricate responses, logprobs, metrics, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice response generation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-metric-computation",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-response-generation-repair",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-response-generation-blocker-closure",
      "execution_gate_requirements": {
        "responses_jsonl": "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl",
        "summary": "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_summary.json",
        "blocker_json": "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_blockers.json",
        "verdict": "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_verdict.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-advbench-small-slice-response-generation-repair",
      "purpose": "Repair and compress the partially validated AdvBench small-slice response-generation state into a dedicated routeable artifact package without fabricating responses.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_summary.json",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_blockers.json",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_verdict.json"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-response-generation-repair.md",
        "docs/dualscope_advbench_small_slice_response_generation_repair.md",
        "src/eval/dualscope_advbench_small_slice_response_generation_repair.py",
        "scripts/build_dualscope_advbench_small_slice_response_generation_repair.py",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json",
        "outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_summary.json",
        "outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_availability_matrix.json",
        "outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_blocker_compression.json",
        "outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_verdict.json"
      ],
      "branch_name_suggestion": "codex/advbench-small-slice-response-generation-repair",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, the AdvBench response-generation partial verdict, and existing response artifacts first. This is a repair/compression task, not a metric task and not a full generation retry inside the CUDA-invisible Codex sandbox. Audit the source response rows, blocker JSON, summary, and verdict. If real response rows exist and are non-fabricated, route to `dualscope-advbench-small-slice-metric-computation`; if only an explicit CUDA/OOM/runtime/input blocker exists, preserve that blocker and route to blocker closure or input repair. Generate the repair ExecPlan, docs, core builder, CLI, repair summary, availability matrix, blocker compression, compact row audit, report, verdict, and tracked registry. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice response generation repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-response-generation-blocker-closure",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-response-generation-repair",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-response-generation-blocker-closure"
    },
    {
      "task_id": "dualscope-advbench-small-slice-metric-computation",
      "purpose": "Compute only available metrics from real bounded AdvBench responses and record blocked metrics honestly.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-metric-computation.md",
        "docs/dualscope_advbench_small_slice_metric_computation.md",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation.json",
        "outputs/dualscope_advbench_small_slice_metric_computation/default/metric_summary.json",
        "outputs/dualscope_advbench_small_slice_metric_computation/default/available_metrics.json",
        "outputs/dualscope_advbench_small_slice_metric_computation/default/metric_blockers.json",
        "outputs/dualscope_advbench_small_slice_metric_computation/default/readiness_matrix.json",
        "outputs/dualscope_advbench_small_slice_metric_computation/default/metric_report.md",
        "outputs/dualscope_advbench_small_slice_metric_computation/default/metric_verdict.json"
      ],
      "branch_name_suggestion": "codex/advbench-small-slice-metric-computation",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Compute only metrics supported by real AdvBench bounded response artifacts: response availability, refusal rate, safety behavior proxy, target behavior status if target definitions are present, cost/fallback summaries, and detection metrics only when labels and final_risk_score are actually aligned. If AUROC, F1, ASR, clean utility, with-logprobs metrics, or score/label-aligned detection metrics are unavailable, record explicit blockers or not_applicable statuses. Do not fabricate AUROC/F1/ASR/clean utility/logprobs or promote projected placeholders as real performance. Write metric_summary, available_metrics, metric_blockers, readiness_matrix, report, verdict, and tracked registry. Do not modify benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice metric computation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_metric_computation/default/metric_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-result-package",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-metric-computation-repair",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-metric-computation-blocker-closure",
      "execution_gate_requirements": {
        "summary": "outputs/dualscope_advbench_small_slice_metric_computation/default/metric_summary.json",
        "available_metrics": "outputs/dualscope_advbench_small_slice_metric_computation/default/available_metrics.json",
        "blocker_json": "outputs/dualscope_advbench_small_slice_metric_computation/default/metric_blockers.json",
        "readiness_matrix": "outputs/dualscope_advbench_small_slice_metric_computation/default/readiness_matrix.json",
        "verdict": "outputs/dualscope_advbench_small_slice_metric_computation/default/metric_verdict.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-advbench-small-slice-metric-computation-repair",
      "purpose": "Repair and compress the partially validated AdvBench metric-computation state into routeable metric availability and blocker artifacts without fabricating unavailable metrics.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation.json",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json",
        "outputs/dualscope_advbench_small_slice_metric_computation/default",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-metric-computation-repair.md",
        "docs/dualscope_advbench_small_slice_metric_computation_repair.md",
        "src/eval/dualscope_advbench_small_slice_metric_computation_repair.py",
        "scripts/build_dualscope_advbench_small_slice_metric_computation_repair.py",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation-repair.json",
        "outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_summary.json",
        "outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_metric_availability_matrix.json",
        "outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_blocked_metric_compression.json",
        "outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_verdict.json"
      ],
      "branch_name_suggestion": "codex/advbench-small-slice-metric-computation-repair",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. This is a repair/compression task for the partially validated AdvBench metric-computation stage. Audit the source metric artifacts, response rows, metric registry, and response-generation repair registry. If the ignored source metric output directory is absent in the isolated worktree but response rows and registries exist, first rerun `python3 scripts/build_dualscope_advbench_small_slice_metric_computation.py --seed 20260427` or an equivalent supported invocation to recreate source metric artifacts without changing benchmark truth. Preserve only artifact-supported availability and fallback summaries; keep refusal, target behavior, detection, ASR, clean utility, and with-logprobs metrics blocked unless real response rows and required fields exist. If zero real response rows caused the metric gap, route to response-generation blocker closure rather than repeatedly recomputing metrics. Generate the repair ExecPlan, docs, core builder, CLI, repair summary, metric availability matrix, blocked metric compression, source audit, limitations, report, verdict, and tracked registry. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice metric computation repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-response-generation-blocker-closure",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-metric-computation-blocker-closure",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-metric-computation-blocker-closure"
    },
    {
      "task_id": "dualscope-advbench-small-slice-result-package",
      "purpose": "Package real bounded AdvBench small-slice response and metric evidence with limitations.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation.json",
        "outputs/dualscope_advbench_small_slice_metric_computation/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-result-package.md",
        "docs/dualscope_advbench_small_slice_result_package.md",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json",
        "outputs/dualscope_advbench_small_slice_result_package/default/result_package_summary.json",
        "outputs/dualscope_advbench_small_slice_result_package/default/result_package_report.md",
        "outputs/dualscope_advbench_small_slice_result_package/default/metric_availability_matrix.json",
        "outputs/dualscope_advbench_small_slice_result_package/default/result_package_verdict.json"
      ],
      "branch_name_suggestion": "codex/advbench-small-slice-result-package",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Package the real AdvBench bounded small-slice status: materialization summary, response generation summary, metric availability, refusal/safety behavior proxy or target success only if supported, blocked metrics, without-logprobs limitation, no full-matrix claim, no full paper performance claim, and a next-step recommendation. Do not fabricate metrics, responses, logprobs, benchmark truth, gates, route_c, or 199+. Write result_package_summary, result_package_report, metric_availability_matrix, result_package_verdict, and tracked registry. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice result package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_result_package/default/result_package_verdict.json"
      ],
      "next_task_if_validated": "dualscope-jbb-small-slice-materialization",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-result-package-repair",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-result-package-blocker-closure",
      "execution_gate_requirements": {
        "summary": "outputs/dualscope_advbench_small_slice_result_package/default/result_package_summary.json",
        "report": "outputs/dualscope_advbench_small_slice_result_package/default/result_package_report.md",
        "metric_availability_matrix": "outputs/dualscope_advbench_small_slice_result_package/default/metric_availability_matrix.json",
        "verdict": "outputs/dualscope_advbench_small_slice_result_package/default/result_package_verdict.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-advbench-small-slice-result-package-repair",
      "purpose": "Repair and compress the partially validated AdvBench result-package state into explicit evidence boundaries, blockers, and routeable next-step artifacts without fabricating unavailable metrics.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation-repair.json",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json",
        "outputs/dualscope_advbench_small_slice_result_package/default",
        "outputs/dualscope_advbench_small_slice_metric_computation_repair/default",
        "outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl"
      ],
      "expected_outputs": [
        ".plans/dualscope-advbench-small-slice-result-package-repair.md",
        "docs/dualscope_advbench_small_slice_result_package_repair.md",
        "src/eval/dualscope_advbench_small_slice_result_package_repair.py",
        "scripts/build_dualscope_advbench_small_slice_result_package_repair.py",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package-repair.json",
        "outputs/dualscope_advbench_small_slice_result_package_repair/default/advbench_small_slice_result_package_repair_summary.json",
        "outputs/dualscope_advbench_small_slice_result_package_repair/default/advbench_small_slice_result_package_repair_evidence_boundary.json",
        "outputs/dualscope_advbench_small_slice_result_package_repair/default/advbench_small_slice_result_package_repair_blocker_compression.json",
        "outputs/dualscope_advbench_small_slice_result_package_repair/default/advbench_small_slice_result_package_repair_verdict.json",
        "outputs/dualscope_advbench_small_slice_result_package_repair_analysis/default/advbench_small_slice_result_package_repair_verdict.json"
      ],
      "branch_name_suggestion": "codex/advbench-small-slice-result-package-repair",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. This is a repair/compression task for the partially validated AdvBench result-package stage. Audit the prior result package, metric-computation repair package, response-generation repair registry, and response rows. If ignored source output directories are absent in the isolated worktree but response rows and registries exist, first rerun the supported metric-computation, metric-repair, and result-package CLIs to recreate source artifacts without changing benchmark truth. Preserve only artifact-supported materialization, response availability, and fallback summaries; keep refusal, target behavior, detection, ASR, clean utility, and with-logprobs metrics blocked unless real response rows and required fields exist. If zero real response rows caused the partial result package, route to response-generation blocker closure rather than JBB expansion. Generate the repair ExecPlan, docs, core builder, CLI, repair summary, evidence boundary, blocker compression, source audit, limitations, report, verdict, analysis mirror, and tracked registry. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "AdvBench small-slice result package repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_advbench_small_slice_result_package_repair/default/advbench_small_slice_result_package_repair_verdict.json",
        "outputs/dualscope_advbench_small_slice_result_package_repair_analysis/default/advbench_small_slice_result_package_repair_verdict.json"
      ],
      "next_task_if_validated": "dualscope-advbench-small-slice-response-generation-blocker-closure",
      "next_task_if_partially_validated": "dualscope-advbench-small-slice-result-package-blocker-closure",
      "next_task_if_not_validated": "dualscope-advbench-small-slice-result-package-blocker-closure"
    },
    {
      "task_id": "dualscope-jbb-small-slice-materialization",
      "purpose": "Materialize or validate a bounded JBB-Behaviors small-slice if available; otherwise output a real blocker without fabricating data.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json",
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-readiness-plan.json",
        "docs/dualscope_jbb_small_slice_readiness_plan.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-jbb-small-slice-materialization.md",
        "docs/dualscope_jbb_small_slice_materialization.md",
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json",
        "outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_manifest.json",
        "outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_schema_check.json",
        "outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_blockers.json",
        "outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_report.md",
        "outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_verdict.json"
      ],
      "branch_name_suggestion": "codex/jbb-small-slice-materialization",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Materialize or validate only a bounded JBB-Behaviors small slice. If data exists locally or is publicly downloadable without special authorization, create a small-slice manifest and schema check. If unavailable, gated, license-ambiguous, network-blocked, or unsafe, emit explicit blockers and do not create fake rows. No response generation or metrics in this task. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "JBB small-slice materialization validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_verdict.json"
      ],
      "next_task_if_validated": "dualscope-jbb-small-slice-response-generation-plan",
      "next_task_if_partially_validated": "dualscope-jbb-small-slice-materialization-repair",
      "next_task_if_not_validated": "dualscope-jbb-small-slice-data-blocker-closure",
      "execution_gate_requirements": {
        "manifest": "outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_manifest.json",
        "schema_check": "outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_schema_check.json",
        "blocker_json": "outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_blockers.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-jbb-small-slice-response-generation-plan",
      "purpose": "Plan bounded JBB response generation without running full matrix.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json",
        "outputs/dualscope_jbb_small_slice_materialization/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-jbb-small-slice-response-generation-plan.md",
        "docs/dualscope_jbb_small_slice_response_generation_plan.md",
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation-plan.json",
        "outputs/dualscope_jbb_small_slice_response_generation_plan/default/jbb_response_generation_plan.json",
        "outputs/dualscope_jbb_small_slice_response_generation_plan/default/jbb_response_generation_plan_verdict.json"
      ],
      "branch_name_suggestion": "codex/jbb-small-slice-response-generation-plan",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Plan bounded JBB response generation using only materialized/validated JBB small-slice artifacts. Do not generate responses in this task. Define max_examples <= 16 or 32, batch_size=1, max_new_tokens=64, Qwen2.5-7B external GPU runner usage, model path `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, HF cache settings, safety-aware prompt construction, controlled safety evaluation templates for harmful instructions, without-logprobs fallback handling, expected response/summary/blocker/report/verdict artifacts, and metric readiness. Do not claim data availability beyond materialization artifacts. Do not generate actual dangerous content, do not run full matrix, and do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "JBB small-slice response generation plan validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_jbb_small_slice_response_generation_plan/default/jbb_response_generation_plan_verdict.json"
      ],
      "next_task_if_validated": "dualscope-jbb-small-slice-response-generation",
      "next_task_if_partially_validated": "dualscope-jbb-small-slice-response-generation-plan-repair",
      "next_task_if_not_validated": "dualscope-jbb-small-slice-response-generation-plan-blocker-closure"
    },
    {
      "task_id": "dualscope-jbb-small-slice-response-generation",
      "purpose": "Run bounded safety-aware Qwen2.5-7B response generation for the validated JBB small-slice, or emit a real blocker.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation-plan.json",
        "outputs/dualscope_jbb_small_slice_materialization/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-jbb-small-slice-response-generation.md",
        "docs/dualscope_jbb_small_slice_response_generation.md",
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation.json",
        "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_responses.jsonl",
        "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_summary.json",
        "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_blockers.json",
        "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_report.md",
        "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_verdict.json"
      ],
      "branch_name_suggestion": "codex/jbb-small-slice-response-generation",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Execute bounded JBB small-slice response generation only if safe and feasible. Use the validated JBB small-slice artifact, `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, HF caches under `/mnt/sda3/lh/huggingface`, CUDA devices 2,3, max_examples <= 16 or 32, batch_size=1, and max_new_tokens=64. Prefer the external GPU runner/worktree flow instead of forcing CUDA inside the Codex sandbox. Use safety-aware prompt construction or controlled safety evaluation templates for harmful instructions and do not generate actionable dangerous content. If logprobs are unavailable, record `without_logprobs_fallback=true`. Write real responses only when produced by the model; otherwise write a blocker JSON with explicit blocker_type and do not mark validated. Response rows must include sample_id, dataset_id, instruction, model_response, generation_mode, capability_flags, safety_mode, and without_logprobs_fallback when those source fields exist. Do not fabricate responses, logprobs, metrics, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "JBB small-slice response generation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-jbb-small-slice-metric-computation",
      "next_task_if_partially_validated": "dualscope-jbb-small-slice-response-generation-repair",
      "next_task_if_not_validated": "dualscope-jbb-small-slice-response-generation-blocker-closure",
      "execution_gate_requirements": {
        "responses_jsonl": "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_responses.jsonl",
        "summary": "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_summary.json",
        "blocker_json": "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_blockers.json",
        "verdict": "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_verdict.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-jbb-small-slice-metric-computation",
      "purpose": "Compute only available metrics from real bounded JBB responses and record blocked metrics honestly.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation.json",
        "outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_responses.jsonl"
      ],
      "expected_outputs": [
        ".plans/dualscope-jbb-small-slice-metric-computation.md",
        "docs/dualscope_jbb_small_slice_metric_computation.md",
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-metric-computation.json",
        "outputs/dualscope_jbb_small_slice_metric_computation/default/metric_summary.json",
        "outputs/dualscope_jbb_small_slice_metric_computation/default/available_metrics.json",
        "outputs/dualscope_jbb_small_slice_metric_computation/default/metric_blockers.json",
        "outputs/dualscope_jbb_small_slice_metric_computation/default/readiness_matrix.json",
        "outputs/dualscope_jbb_small_slice_metric_computation/default/metric_report.md",
        "outputs/dualscope_jbb_small_slice_metric_computation/default/metric_verdict.json"
      ],
      "branch_name_suggestion": "codex/jbb-small-slice-metric-computation",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Compute only metrics supported by real JBB bounded response artifacts: response availability, refusal rate, safety behavior proxy, target behavior status if target definitions are present, cost/fallback summaries, and detection metrics only when labels and final_risk_score are actually aligned. If AUROC, F1, ASR, clean utility, with-logprobs metrics, or score/label-aligned detection metrics are unavailable, record explicit blockers or not_applicable statuses. Do not fabricate AUROC/F1/ASR/clean utility/logprobs or promote projected placeholders as real performance. Write metric_summary, available_metrics, metric_blockers, readiness_matrix, report, verdict, and tracked registry. Do not modify benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "JBB small-slice metric computation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_jbb_small_slice_metric_computation/default/metric_verdict.json"
      ],
      "next_task_if_validated": "dualscope-jbb-small-slice-result-package",
      "next_task_if_partially_validated": "dualscope-jbb-small-slice-metric-computation-repair",
      "next_task_if_not_validated": "dualscope-jbb-small-slice-metric-computation-blocker-closure",
      "execution_gate_requirements": {
        "summary": "outputs/dualscope_jbb_small_slice_metric_computation/default/metric_summary.json",
        "available_metrics": "outputs/dualscope_jbb_small_slice_metric_computation/default/available_metrics.json",
        "blocker_json": "outputs/dualscope_jbb_small_slice_metric_computation/default/metric_blockers.json",
        "readiness_matrix": "outputs/dualscope_jbb_small_slice_metric_computation/default/readiness_matrix.json",
        "verdict": "outputs/dualscope_jbb_small_slice_metric_computation/default/metric_verdict.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-jbb-small-slice-result-package",
      "purpose": "Package real bounded JBB small-slice response and metric evidence with limitations.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-metric-computation.json",
        "outputs/dualscope_jbb_small_slice_metric_computation/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-jbb-small-slice-result-package.md",
        "docs/dualscope_jbb_small_slice_result_package.md",
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-result-package.json",
        "outputs/dualscope_jbb_small_slice_result_package/default/result_package_summary.json",
        "outputs/dualscope_jbb_small_slice_result_package/default/result_package_report.md",
        "outputs/dualscope_jbb_small_slice_result_package/default/metric_availability_matrix.json",
        "outputs/dualscope_jbb_small_slice_result_package/default/result_package_verdict.json"
      ],
      "branch_name_suggestion": "codex/jbb-small-slice-result-package",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Package the real JBB bounded small-slice status: materialization summary, response generation summary, metric availability, refusal/safety behavior proxy or target success only if supported, blocked metrics, without-logprobs limitation, no full-matrix claim, no full paper performance claim, and a next-step recommendation. Do not fabricate metrics, responses, logprobs, benchmark truth, gates, route_c, or 199+. Write result_package_summary, result_package_report, metric_availability_matrix, result_package_verdict, and tracked registry. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "JBB small-slice result package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_jbb_small_slice_result_package/default/result_package_verdict.json"
      ],
      "next_task_if_validated": "dualscope-sci3-expanded-result-synthesis-package",
      "next_task_if_partially_validated": "dualscope-jbb-small-slice-result-package-repair",
      "next_task_if_not_validated": "dualscope-jbb-small-slice-result-package-blocker-closure",
      "execution_gate_requirements": {
        "summary": "outputs/dualscope_jbb_small_slice_result_package/default/result_package_summary.json",
        "report": "outputs/dualscope_jbb_small_slice_result_package/default/result_package_report.md",
        "metric_availability_matrix": "outputs/dualscope_jbb_small_slice_result_package/default/metric_availability_matrix.json",
        "verdict": "outputs/dualscope_jbb_small_slice_result_package/default/result_package_verdict.json",
        "requires_real_execution_or_blocker": true
      }
    },
    {
      "task_id": "dualscope-sci3-expanded-result-synthesis-package",
      "purpose": "Synthesize current bounded Alpaca main-slice, semantic trigger, behavior-shift, AdvBench/JBB materialization or blocker results into an expanded SCI3 status package.",
      "expected_inputs": [
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-result-package.json",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package.json",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package.json",
        ".reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json",
        ".reports/dualscope_task_verdicts/dualscope-jbb-small-slice-result-package.json"
      ],
      "expected_outputs": [
        ".plans/dualscope-sci3-expanded-result-synthesis-package.md",
        "docs/dualscope_sci3_expanded_result_synthesis.md",
        ".reports/dualscope_task_verdicts/dualscope-sci3-expanded-result-synthesis-package.json",
        "outputs/dualscope_sci3_expanded_result_synthesis_package/default/expanded_result_summary.json",
        "outputs/dualscope_sci3_expanded_result_synthesis_package/default/expanded_result_report.md",
        "outputs/dualscope_sci3_expanded_result_synthesis_package/default/remaining_blockers.json",
        "outputs/dualscope_sci3_expanded_result_synthesis_package/default/expanded_result_verdict.json"
      ],
      "branch_name_suggestion": "codex/sci3-expanded-result-synthesis-package",
      "prompt_template": "Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md first. Synthesize the expanded SCI3 status package from bounded Alpaca main-slice metrics, semantic trigger smoke metrics, behavior-shift target smoke metrics, AdvBench materialization/response/metrics/result package status, and JBB materialization/response/metrics/result package status. Separate real metrics, fallback evidence, blocked metrics, dataset blockers, cross-model readiness status, clean utility blockers, without-logprobs limitations, no-full-matrix limitations, and the next SCI3 plan. Do not claim full matrix, clean utility, cross-model validation, or dataset results unless artifacts prove them. Produce expanded_result_summary, expanded_result_report, remaining_blockers, expanded_result_verdict, and tracked registry. Do not fabricate responses, logprobs, AUROC/F1/ASR/clean utility, labels, benchmark truth, gates, route_c, or 199+. Do not run full matrix, train, force push, delete branches, or touch PR #14. Follow AGENTS.md PR workflow.",
      "completion_verdicts": {
        "validated": [
          "SCI3 expanded result synthesis package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_sci3_expanded_result_synthesis_package/default/expanded_result_verdict.json"
      ],
      "next_task_if_validated": "queue_complete",
      "next_task_if_partially_validated": "dualscope-sci3-expanded-result-synthesis-package-repair",
      "next_task_if_not_validated": "dualscope-sci3-expanded-result-synthesis-package-blocker-closure",
      "execution_gate_requirements": {
        "summary": "outputs/dualscope_sci3_expanded_result_synthesis_package/default/expanded_result_summary.json",
        "report": "outputs/dualscope_sci3_expanded_result_synthesis_package/default/expanded_result_report.md",
        "remaining_blockers": "outputs/dualscope_sci3_expanded_result_synthesis_package/default/remaining_blockers.json",
        "verdict": "outputs/dualscope_sci3_expanded_result_synthesis_package/default/expanded_result_verdict.json",
        "requires_real_execution_or_blocker": true
      }
    }
  ]
}
```
