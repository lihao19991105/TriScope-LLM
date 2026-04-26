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
      "purpose": "Repair the partially validated Qwen2.5-7B first-slice response-generation path by adding runtime resource guards and honest blocker artifacts before any 7B model load.",
      "expected_inputs": [
        ".plans/dualscope-qwen2p5-7b-response-generation-repair.md",
        ".plans/dualscope-qwen2p5-7b-first-slice-response-generation.md",
        "src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py",
        "scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py",
        "docs/dualscope_qwen2p5_7b_first_slice_response_generation.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-qwen2p5-7b-response-generation-repair.md",
        ".reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-response-generation-repair.json",
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default"
      ],
      "branch_name_suggestion": "codex/qwen2p5-7b-response-generation-repair",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the Qwen2.5-7B response-generation partial verdict first. Scope the work to the response-generation repair only: selected-GPU memory preflight, CUDA/device recording, CPU fallback guard, honest blocker artifacts, docs, validation, and tracked verdict registry. Do not train, do not run a full matrix, do not fabricate responses/logprobs/metrics, do not modify benchmark truth or gates, do not continue route_c, and do not generate 199+. Follow AGENTS.md PR workflow without auto merge, force push, branch deletion, or remote rewrite.",
      "completion_verdicts": {
        "validated": [
          "Qwen2.5-7B response-generation repair validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default/dualscope_qwen2p5_7b_first_slice_response_generation_verdict.json"
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
