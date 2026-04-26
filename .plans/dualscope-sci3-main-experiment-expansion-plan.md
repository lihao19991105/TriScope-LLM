# DualScope SCI3 Main Experiment Expansion Plan

## Purpose / Big Picture

This task expands DualScope-LLM from the Qwen2.5-7B first-slice evidence toward the SCI3 main experiment plan. It is a planning and validation task only: it defines the dataset, trigger, target, baseline, budget, robustness, ablation, and table structure needed for the main experiment, but it does not execute the full matrix or claim new model responses, logprobs, benchmark truth, gates, or metrics.

The plan serves the current DualScope mainline by keeping the method centered on illumination screening, confidence verification, and budget-aware fusion under black-box and optional-logprob constraints.

## Scope

### In Scope

- Plan the SCI3 main experiment expansion from the current Qwen2.5-7B first-slice position.
- Cover Stanford Alpaca, AdvBench, and JBB-Behaviors.
- Cover lexical, semantic, and contextual/instruction triggers.
- Cover fixed-response and behavior-shift targets.
- Cover illumination-only, confidence-only with-logprobs, confidence-only without-logprobs, naive concat, and DualScope budget-aware fusion baselines.
- Define cost, robustness, ablation, and planned paper table outputs.
- Produce planning artifacts under `outputs/dualscope_sci3_main_experiment_expansion_plan/default`.

### Out of Scope

- No full matrix execution.
- No model generation, logprob extraction, training, LoRA, QLoRA, full finetune, or metric recomputation.
- No benchmark truth edits.
- No gate edits.
- No fake responses, labels, logprobs, AUROC, F1, ASR, clean utility, latency, or full-paper performance.
- No route_c continuation and no `199+` planning.
- No auto merge, force push, branch deletion, or remote rewrite.

## Repository Context

- Expected first-slice input: `outputs/dualscope_qwen2p5_7b_first_slice_result_package/default`.
- SCI3 track input: `docs/dualscope_sci3_experimental_track.md`.
- SCI3 metrics/table input: `docs/dualscope_sci3_metrics_and_tables.md`.
- Supporting checked-in summary: `docs/dualscope_qwen2p5_7b_first_slice_result_package.md`.
- Plan output: `.plans/dualscope-sci3-main-experiment-expansion-plan.md`.
- Documentation output: `docs/dualscope_sci3_main_experiment_expansion_plan.md`.
- Artifact output: `outputs/dualscope_sci3_main_experiment_expansion_plan/default`.

Historical TriScope / route_c artifacts are not used for this expansion except as non-mainline reliability background. This plan does not extend any old route_c chain.

## Deliverables

- `.plans/dualscope-sci3-main-experiment-expansion-plan.md`
- `docs/dualscope_sci3_main_experiment_expansion_plan.md`
- `outputs/dualscope_sci3_main_experiment_expansion_plan/default/dualscope_sci3_main_experiment_expansion_plan_summary.json`
- `outputs/dualscope_sci3_main_experiment_expansion_plan/default/dualscope_sci3_main_experiment_matrix_plan.json`
- `outputs/dualscope_sci3_main_experiment_expansion_plan/default/dualscope_sci3_main_experiment_table_plan.json`
- `outputs/dualscope_sci3_main_experiment_expansion_plan/default/dualscope_sci3_main_experiment_validation_log.json`
- `outputs/dualscope_sci3_main_experiment_expansion_plan/default/dualscope_sci3_main_experiment_expansion_plan_report.md`
- `outputs/dualscope_sci3_main_experiment_expansion_plan/default/dualscope_sci3_main_experiment_expansion_plan_verdict.json`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, SCI3 track docs, and metrics/table docs.
- [x] M2: Validate expected input availability and record blockers.
- [x] M3: Draft SCI3 main expansion plan across datasets, triggers, targets, baselines, costs, robustness, ablations, and tables.
- [x] M4: Emit output artifacts and final verdict.
- [x] M5: Run local structural validation on JSON artifacts.
- [ ] M6: Complete PR workflow without auto merge, force push, branch deletion, remote rewrite, benchmark truth changes, gate changes, route_c continuation, or `199+`. Blocked: local git metadata is read-only and the GitHub connector branch-creation fallback was cancelled.

## Surprises & Discoveries

- The expected input directory `outputs/dualscope_qwen2p5_7b_first_slice_result_package/default` is absent in this worktree.
- The checked-in document `docs/dualscope_qwen2p5_7b_first_slice_result_package.md` exists and summarizes the prior first-slice package, but it is not a substitute for the missing artifact directory as an execution gate.
- The SCI3 track and metrics/table documents exist and are sufficient for planning the main expansion shape.
- Local PR workflow could not complete because `git add` could not create the worktree `index.lock` on the read-only shared git metadata path. The GitHub fallback branch-creation call was cancelled, so no PR was opened.

## Decision Log

- Final verdict is `Partially validated` because the expansion plan is complete, but one expected input artifact directory is missing locally.
- The first action before any execution is to restore or regenerate the Qwen2.5-7B first-slice result package directory.
- Stanford Alpaca remains the first main expansion dataset because it is the closest continuation of the first-slice path.
- AdvBench and JBB-Behaviors are planned as stress and risky-behavior validation paths after the Stanford Alpaca execution contract is stable.
- DualScope budget-aware fusion is the primary method; naive concat and single-branch baselines are controls, not replacements.

## Plan of Work

First restore the Qwen2.5-7B first-slice package artifact and confirm its clean utility / logprob blockers are explicit. Then execute a staged Stanford Alpaca expansion before adding AdvBench and JBB-Behaviors. Each dataset is expanded across lexical, semantic, and contextual/instruction triggers, then across fixed-response and behavior-shift targets. Baselines are run under the same row IDs, labels, scores, and budget policy so cost and performance comparisons are auditably aligned.

The full cross product is a plan, not a single immediate command. Execution must happen as small slices with validation gates between dataset, trigger, target, and baseline expansions.

## Concrete Steps

1. Restore or regenerate `outputs/dualscope_qwen2p5_7b_first_slice_result_package/default`.
2. Freeze row schema for each dataset: `row_id`, `dataset`, `model`, `trigger_family`, `target_family`, `condition`, `response`, `label`, `score`, `budget_trace`, and `capability_mode`.
3. Run Stanford Alpaca first: lexical trigger plus fixed-response target, then semantic and contextual/instruction triggers, then behavior-shift target.
4. Add AdvBench only after Stanford Alpaca schema, scoring, and budget traces validate.
5. Add JBB-Behaviors only after AdvBench stress-path validation.
6. Run baselines on identical row scopes: illumination-only, confidence-only with-logprobs, confidence-only without-logprobs, naive concat, and DualScope budget-aware fusion.
7. Export main, cost, robustness, ablation, and cross-model table data only from real aligned artifacts.
8. Keep cross-model validation as a later plan for Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3; do not claim it in this task.

## Validation and Acceptance

This planning task is accepted when:

- The ExecPlan, documentation, and output artifacts exist.
- The matrix plan includes all three datasets, all three trigger families, both target families, and all required baselines.
- The cost, robustness, ablation, and table plans are explicit.
- The artifact validation log records the missing first-slice package directory honestly.
- The final verdict is one of: `SCI3 main experiment expansion plan validated`, `Partially validated`, or `Not validated`.

## Idempotence and Recovery

The plan artifacts are static and can be regenerated by rewriting the same files. If the first-slice package directory is restored later, update the validation log and verdict only after checking the real artifact files. Do not manually edit performance metrics into this plan.

## Outputs and Artifacts

All task artifacts are under `outputs/dualscope_sci3_main_experiment_expansion_plan/default`.

## Remaining Risks

- The expected first-slice package directory is missing in this worktree.
- Clean utility remains blocked unless explicit utility-success or reference-match fields exist.
- Logprob-based confidence remains unavailable unless a real with-logprobs artifact is produced.
- AdvBench and JBB-Behaviors require careful benchmark-truth handling; this plan must not modify truth files.
- Full cross-model validation is resource-dependent and not part of this task.

## Next Suggested Plan

`dualscope-sci3-main-experiment-input-restoration`

Restore or regenerate the Qwen2.5-7B first-slice result package directory, then validate that the SCI3 expansion can consume concrete package artifacts before any main-matrix execution begins.

## PR Workflow Status

Local staging failed with:

```text
fatal: Unable to create '/home/lh/TriScope-LLM/.git/worktrees/sci3-main-experiment-expansion-plan-20260426130720/index.lock': Read-only file system
```

GitHub fallback branch creation for `codex/dualscope-sci3-main-expansion-plan` was attempted and cancelled by the connector. No branch, commit, PR, auto merge, force push, branch deletion, remote rewrite, benchmark truth change, gate change, route_c continuation, or `199+` generation occurred.
