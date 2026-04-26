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
    }
  ]
}
```
