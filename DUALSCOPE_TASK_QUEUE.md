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
      "next_task_if_validated": "dualscope-first-slice-real-response-generation",
      "next_task_if_partially_validated": "dualscope-next-experiment-readiness-package-repair",
      "next_task_if_not_validated": "dualscope-next-experiment-readiness-package-blocker-closure"
    },
    {
      "task_id": "dualscope-first-slice-real-response-generation",
      "purpose": "Generate or collect minimal first-slice model responses for clean and poisoned labeled rows, without training or expanding the matrix.",
      "expected_inputs": [
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_first_slice_target_response_generation_plan/default",
        "outputs/dualscope_minimal_first_slice_condition_level_rerun/default",
        "outputs/dualscope_illumination_screening_freeze/default",
        "outputs/dualscope_confidence_verification_with_without_logprobs/default",
        "outputs/dualscope_budget_aware_two_stage_fusion_design/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-first-slice-real-response-generation.md",
        "src/eval/dualscope_first_slice_real_response_generation.py",
        "src/eval/post_dualscope_first_slice_real_response_generation_analysis.py",
        "scripts/build_dualscope_first_slice_real_response_generation.py",
        "scripts/build_post_dualscope_first_slice_real_response_generation_analysis.py",
        "docs/dualscope_first_slice_real_response_generation.md",
        "outputs/dualscope_first_slice_real_response_generation/default",
        "outputs/dualscope_first_slice_real_response_generation_analysis/default"
      ],
      "branch_name_suggestion": "codex/dualscope-first-slice-real-response-generation",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the first-slice target-response-generation plan artifacts first. Scope this task to the minimal Stanford Alpaca first-slice only: use data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl, clean/poisoned labeled pairs, lexical_trigger_v1 with trigger_text=cftrigger, fixed_response_v1 with target_text=I have completed the requested instruction., and the currently frozen local Qwen2.5-1.5B-Instruct path from the real-run plan. Do not train, do not full finetune, do not LoRA/QLoRA train, do not expand datasets/models/triggers/targets/budgets, do not run the full matrix, do not change benchmark truth, do not change gates, do not continue route_c, and do not generate 199+. Generate or collect minimal clean and poisoned model responses when real model execution is available. Prefer with-logprobs or logits-derived confidence; if unavailable, explicitly fallback to without-logprobs and record capability_mode, response_generation_mode, model_response availability flags, and blockers. Do not fake responses, do not fake logprobs, do not fake labels, do not fake AUROC/F1/ASR/utility, and do not write projected or placeholder metrics as real performance. Produce the ExecPlan, implementation, build CLI, post-analysis CLI, docs, response artifacts, analysis artifacts, report, and a single final verdict: First-slice real response generation validated, Partially validated, or Not validated. Run py_compile for changed Python files, run the response generation build CLI, and run the post-analysis CLI. Follow AGENTS.md GitHub PR Workflow: create a feature branch from main, make minimal changes, run validation, commit, run ./scripts/codex-pr.sh, trigger @codex review, and report PR/review/CI status. Do not auto merge, force push, delete branches, rewrite remotes, fake model outputs, or fake metrics.",
      "completion_verdicts": {
        "validated": [
          "First-slice real response generation validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_first_slice_real_response_generation/default/dualscope_first_slice_real_response_generation_verdict.json",
        "outputs/dualscope_first_slice_real_response_generation_analysis/default/dualscope_first_slice_real_response_generation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-first-slice-label-aligned-metric-computation",
      "next_task_if_partially_validated": "dualscope-first-slice-response-generation-repair",
      "next_task_if_not_validated": "dualscope-first-slice-response-generation-blocker-closure"
    },
    {
      "task_id": "dualscope-first-slice-label-aligned-metric-computation",
      "purpose": "Compute label-aligned detection / ASR / utility readiness and available metrics using first-slice labels, Stage 3 scores, and available model responses.",
      "expected_inputs": [
        "data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl",
        "outputs/dualscope_first_slice_real_response_generation/default",
        "outputs/dualscope_minimal_first_slice_condition_level_rerun/default",
        "outputs/dualscope_first_slice_condition_row_level_fusion_alignment/default",
        "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-first-slice-label-aligned-metric-computation.md",
        "src/eval/dualscope_first_slice_label_aligned_metric_computation.py",
        "src/eval/post_dualscope_first_slice_label_aligned_metric_computation_analysis.py",
        "scripts/build_dualscope_first_slice_label_aligned_metric_computation.py",
        "scripts/build_post_dualscope_first_slice_label_aligned_metric_computation_analysis.py",
        "docs/dualscope_first_slice_label_aligned_metric_computation.md",
        "outputs/dualscope_first_slice_label_aligned_metric_computation/default",
        "outputs/dualscope_first_slice_label_aligned_metric_computation_analysis/default"
      ],
      "branch_name_suggestion": "codex/dualscope-first-slice-label-aligned-metrics",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, first-slice labels, real-response-generation artifacts, condition-level rerun artifacts, and fusion-alignment artifacts first. Scope this task to first-slice label-aligned metric computation only. Compute AUROC, AUPRC, F1, and Accuracy only when detection_label and final_risk_score align at the same row/condition granularity. Compute ASR only for asr_eligible rows that have real model_response and target_text. Compute clean utility only for utility_eligible rows that have real clean model_response and reference_response. If any metric cannot be computed, output an explicit blocker and metric availability matrix. Distinguish projected metrics, placeholders, readiness checks, and real first-slice metrics. Do not fake responses, logprobs, labels, AUROC, F1, ASR, utility, or full-paper performance. Do not change benchmark truth, gates, dataset/model/trigger/target/budget scope, route_c, or 199+. Produce the ExecPlan, implementation, build CLI, post-analysis CLI, docs, metric artifacts, analysis artifacts, report, and a single final verdict: First-slice label-aligned metrics validated, Partially validated, or Not validated. Run py_compile for changed Python files, run the metric build CLI, and run the post-analysis CLI. Follow AGENTS.md GitHub PR Workflow and do not auto merge, force push, delete branches, or rewrite remotes.",
      "completion_verdicts": {
        "validated": [
          "First-slice label-aligned metrics validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_first_slice_label_aligned_metric_computation/default/dualscope_first_slice_label_aligned_metric_computation_verdict.json",
        "outputs/dualscope_first_slice_label_aligned_metric_computation_analysis/default/dualscope_first_slice_label_aligned_metric_computation_verdict.json"
      ],
      "next_task_if_validated": "dualscope-first-slice-experiment-result-package",
      "next_task_if_partially_validated": "dualscope-first-slice-metric-computation-repair",
      "next_task_if_not_validated": "dualscope-first-slice-metric-blocker-closure"
    },
    {
      "task_id": "dualscope-first-slice-experiment-result-package",
      "purpose": "Package first-slice experiment results, clearly separating real metrics, projected metrics, placeholders, blockers, and next experiment actions.",
      "expected_inputs": [
        "outputs/dualscope_first_slice_label_aligned_metric_computation/default",
        "outputs/dualscope_first_slice_real_response_generation/default",
        "outputs/dualscope_minimal_first_slice_condition_level_rerun/default",
        "outputs/dualscope_first_slice_target_response_generation_plan/default"
      ],
      "expected_outputs": [
        ".plans/dualscope-first-slice-experiment-result-package.md",
        "src/eval/dualscope_first_slice_experiment_result_package.py",
        "src/eval/post_dualscope_first_slice_experiment_result_package_analysis.py",
        "scripts/build_dualscope_first_slice_experiment_result_package.py",
        "scripts/build_post_dualscope_first_slice_experiment_result_package_analysis.py",
        "docs/dualscope_first_slice_experiment_result_package.md",
        "outputs/dualscope_first_slice_experiment_result_package/default",
        "outputs/dualscope_first_slice_experiment_result_package_analysis/default"
      ],
      "branch_name_suggestion": "codex/dualscope-first-slice-experiment-result-package",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, label-aligned metric artifacts, real-response-generation artifacts, condition-level rerun artifacts, and target-response-generation plan artifacts first. Package only the first-slice experiment results. Produce a result summary, table skeleton, metric availability matrix, limitations, blockers, and one next experiment recommendation. Clearly separate real metrics, projected metrics, placeholders, unavailable metrics, and blockers. Do not claim full paper performance, do not hide fallback/projection limitations, do not fake AUROC/F1/ASR/utility, do not fake model responses, and do not change benchmark truth, gates, dataset/model/trigger/target/budget scope, route_c, or 199+. Produce the ExecPlan, implementation, build CLI, post-analysis CLI, docs, package artifacts, analysis artifacts, report, and a single final verdict: First-slice experiment result package validated, Partially validated, or Not validated. Run py_compile for changed Python files, run the package build CLI, and run the post-analysis CLI. Follow AGENTS.md GitHub PR Workflow and do not auto merge, force push, delete branches, or rewrite remotes.",
      "completion_verdicts": {
        "validated": [
          "First-slice experiment result package validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_first_slice_experiment_result_package/default/dualscope_first_slice_experiment_result_package_verdict.json",
        "outputs/dualscope_first_slice_experiment_result_package_analysis/default/dualscope_first_slice_experiment_result_package_verdict.json"
      ],
      "next_task_if_validated": "dualscope-first-slice-next-experiment-readiness",
      "next_task_if_partially_validated": "dualscope-first-slice-result-package-repair",
      "next_task_if_not_validated": "dualscope-first-slice-result-package-blocker-closure"
    },
    {
      "task_id": "dualscope-first-slice-next-experiment-readiness",
      "purpose": "Prepare the next minimal experiment after first-slice results, without executing it.",
      "expected_inputs": [
        "outputs/dualscope_first_slice_experiment_result_package/default",
        "DUALSCOPE_MASTER_PLAN.md",
        "DUALSCOPE_TASK_QUEUE.md"
      ],
      "expected_outputs": [
        ".plans/dualscope-first-slice-next-experiment-readiness.md",
        "src/eval/dualscope_first_slice_next_experiment_readiness.py",
        "src/eval/post_dualscope_first_slice_next_experiment_readiness_analysis.py",
        "scripts/build_dualscope_first_slice_next_experiment_readiness.py",
        "scripts/build_post_dualscope_first_slice_next_experiment_readiness_analysis.py",
        "docs/dualscope_first_slice_next_experiment_readiness.md",
        "outputs/dualscope_first_slice_next_experiment_readiness/default",
        "outputs/dualscope_first_slice_next_experiment_readiness_analysis/default"
      ],
      "branch_name_suggestion": "codex/dualscope-first-slice-next-experiment-readiness",
      "prompt_template": "Continue DualScope-LLM task `{task_id}`. Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and the first-slice experiment result package first. Prepare exactly one next minimal experiment direction without executing it. Choose one of: second trigger same model, second dataset smoke, with-logprobs improvement, ASR / utility response completion, or small-scale clean/backdoor model pair construction. Do not execute the next experiment, do not expand the matrix, do not add multiple directions, do not train, do not modify benchmark truth, do not modify gates, do not continue route_c, and do not generate 199+. Produce the readiness ExecPlan, implementation, build CLI, post-analysis CLI, docs, readiness artifacts, analysis artifacts, report, and a single final verdict: First-slice next experiment readiness validated, Partially validated, or Not validated. Run py_compile for changed Python files, run the readiness build CLI, and run the post-analysis CLI. Follow AGENTS.md GitHub PR Workflow and do not auto merge, force push, delete branches, or rewrite remotes.",
      "completion_verdicts": {
        "validated": [
          "First-slice next experiment readiness validated"
        ],
        "partially_validated": [
          "Partially validated"
        ],
        "not_validated": [
          "Not validated"
        ]
      },
      "verdict_artifacts": [
        "outputs/dualscope_first_slice_next_experiment_readiness/default/dualscope_first_slice_next_experiment_readiness_verdict.json",
        "outputs/dualscope_first_slice_next_experiment_readiness_analysis/default/dualscope_first_slice_next_experiment_readiness_verdict.json"
      ],
      "next_task_if_validated": null,
      "next_task_if_partially_validated": "dualscope-first-slice-next-experiment-readiness-repair",
      "next_task_if_not_validated": "dualscope-first-slice-next-experiment-readiness-blocker-closure"
    }
  ]
}
```
