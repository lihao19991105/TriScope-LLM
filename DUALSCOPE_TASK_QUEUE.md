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
      "next_task_if_validated": null,
      "next_task_if_partially_validated": "dualscope-next-experiment-readiness-package-repair",
      "next_task_if_not_validated": "dualscope-next-experiment-readiness-package-blocker-closure"
    }
  ]
}
```
