# DualScope Cross-Model Validation Plan

## Purpose / Big Picture

This task plans the SCI3 cross-model validation step for DualScope-LLM using exactly one allowed validation model family: `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3`.

The goal is to define how cross-model validation should be run after the Qwen2.5-7B main path has real, aligned artifacts. This is a planning and resource-gate task only. It does not execute a full matrix, train a model, generate responses, extract logprobs, change benchmark truth, change gates, or continue historical route_c / `199+` work.

## Scope

### In Scope

- Plan cross-model validation for `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3` only.
- Verify whether local model resources exist in this worktree and obvious shared local paths.
- Mark missing model resources as `planned` / `external-resource-required`.
- Preserve the DualScope mainline: illumination screening, confidence verification with and without logprobs, and budget-aware lightweight fusion.
- Require cross-model rows to use the same dataset, trigger, target, row ID, label, score, and budget-trace contracts as the Qwen2.5-7B main path.
- Emit docs and output artifacts under `outputs/dualscope_cross_model_validation_plan/default`.

### Out of Scope

- No response generation.
- No full matrix execution.
- No training, LoRA, QLoRA, full finetune, or benchmark rerun.
- No fake model responses, labels, logprobs, AUROC, F1, ASR, clean utility, latency, or detection metrics.
- No benchmark truth edits.
- No gate edits.
- No route_c continuation and no `199+` planning.
- No auto merge, force push, branch deletion, remote rewrite, or unrelated PR merge.

## Repository Context

- Expected input directory: `outputs/dualscope_sci3_main_experiment_expansion_plan/default`.
- Available repaired SCI3 handoff registry: `.reports/dualscope_task_verdicts/dualscope-sci3-main-experiment-expansion-plan-repair.json`.
- Available model-axis contract: `docs/dualscope_sci3_model_matrix.md`.
- Available repaired SCI3 docs: `docs/dualscope_sci3_main_experiment_expansion_plan_repair.md`.
- Output documentation: `docs/dualscope_cross_model_validation_plan.md`.
- Output artifacts: `outputs/dualscope_cross_model_validation_plan/default`.

Historical TriScope / route_c artifacts are not used except as non-mainline reliability background. This plan does not extend any historical route_c chain.

## Deliverables

- `.plans/dualscope-cross-model-validation-plan.md`
- `docs/dualscope_cross_model_validation_plan.md`
- `outputs/dualscope_cross_model_validation_plan/default/dualscope_cross_model_validation_plan_summary.json`
- `outputs/dualscope_cross_model_validation_plan/default/dualscope_cross_model_validation_matrix_plan.json`
- `outputs/dualscope_cross_model_validation_plan/default/dualscope_cross_model_resource_check.json`
- `outputs/dualscope_cross_model_validation_plan/default/dualscope_cross_model_validation_log.json`
- `outputs/dualscope_cross_model_validation_plan/default/dualscope_cross_model_validation_plan_report.md`
- `outputs/dualscope_cross_model_validation_plan/default/dualscope_cross_model_validation_plan_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-cross-model-validation-plan.json`

## Progress

- [x] M1: Read `AGENTS.md`, `PLANS.md`, `DUALSCOPE_MASTER_PLAN.md`, SCI3 model matrix, and adjacent SCI3 plans.
- [x] M2: Check expected input availability and record missing ignored SCI3 expansion output directory.
- [x] M3: Verify local candidate resources for `Llama-3.1-8B-Instruct` and `Mistral-7B-Instruct-v0.3`.
- [x] M4: Draft cross-model validation contract and resource-gated execution order.
- [x] M5: Emit docs, output artifacts, validation log, and verdict.
- [ ] M6: Complete PR workflow without auto merge, force push, branch deletion, remote rewrite, benchmark truth changes, gate changes, route_c continuation, or `199+`. Blocked: local git metadata is read-only and the GitHub fallback branch-creation call was cancelled.

## Surprises & Discoveries

- The expected input directory `outputs/dualscope_sci3_main_experiment_expansion_plan/default` is absent in this worktree.
- The repaired SCI3 expansion registry exists and is validated, so it can be used as a tracked planning handoff, but it is not a substitute for the missing ignored output directory.
- No local `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3` resource was found in `local_models/`, `/home/lh/TriScope-LLM/local_models/`, `/mnt/sda3/lh/local_models/`, or the checked Hugging Face hub cache names.
- Local PR packaging could not stage files because the shared git metadata path is read-only. GitHub fallback branch creation for `codex/dualscope-cross-model-validation-plan` was attempted and cancelled by the connector.

## Decision Log

- Final verdict is `Partially validated` because the cross-model validation plan is defined and constrained, but both allowed cross-model resources are missing and one expected input directory is absent.
- Cross-model validation is planned as a post-Qwen2.5-7B generalization check, not a replacement for the Qwen2.5-7B main model axis.
- The preferred first cross-model candidate is whichever of `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3` is locally materialized first with tokenizer/config files available.
- If neither model is local, the next step is resource materialization or explicit external-resource approval, not fallback to Qwen2.5-1.5B or fabricated responses.

## Plan of Work

Cross-model validation should begin only after the Qwen2.5-7B main-path package has real aligned row IDs, labels, model responses, score fields, and budget traces. Then materialize one allowed cross-model resource, run a preflight check, and execute the smallest matched slice before expanding.

The first executable slice should reuse the same Stanford Alpaca row scope, trigger family, target family, Stage 1 / Stage 2 / Stage 3 configuration, and budget policy as the Qwen2.5-7B main path. Only after that matched slice validates may the plan extend to AdvBench, JBB-Behaviors, additional trigger families, additional target families, and with-logprobs variants when real capability exists.

## Concrete Steps

1. Restore or regenerate `outputs/dualscope_sci3_main_experiment_expansion_plan/default`, or continue from the validated repair registry with an explicit note that the ignored output directory is unavailable.
2. Materialize exactly one cross-model resource: `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3`.
3. Confirm local model path, tokenizer/config presence, disk footprint, dtype plan, GPU memory fit, deterministic seed, and inference backend.
4. Build a matched first cross-model slice from the same Qwen2.5-7B main row IDs and labels.
5. Run Stage 1 illumination screening only on real generated responses.
6. Run Stage 2 confidence verification in `without_logprobs` mode unless real token logprobs are available; use `with_logprobs` only when real logprob artifacts exist.
7. Run Stage 3 budget-aware fusion on aligned Stage 1 / Stage 2 evidence and identical budget traces.
8. Export cross-model comparison tables only from real aligned artifacts.

## Validation and Acceptance

This planning task is accepted when:

- The ExecPlan, documentation, output artifacts, validation log, and registry exist.
- The plan is limited to `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3`.
- Missing local model resources are marked `planned` / `external-resource-required`.
- Missing expected input artifacts are recorded honestly.
- No responses, labels, logprobs, metrics, benchmark truth, gates, route_c plans, or `199+` plans are fabricated or changed.
- The final verdict is one of `Cross-model validation plan validated`, `Partially validated`, or `Not validated`.

## Idempotence and Recovery

The plan artifacts are static and can be regenerated by rewriting the same files after rerunning the same local resource checks. If a model is later materialized, update only the resource check, validation log, and verdict after verifying real local files. Do not manually edit performance metrics into this plan.

## Remaining Risks

- Both allowed cross-model resources are missing locally.
- The expected SCI3 expansion output directory is missing because `outputs/` is ignored in this repository.
- With-logprobs cross-model validation remains planned until real logprob artifacts exist.
- Clean utility remains gated on explicit utility-success or reference-match evidence.
- Any future execution must avoid expanding into a full matrix before a matched first slice validates.

## Current Verdict

`Partially validated`

## Next Suggested Task

`dualscope-cross-model-resource-materialization`

Materialize either `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3`, then rerun this plan's resource check before any cross-model response generation.

## PR Workflow Status

Local staging failed with:

```text
fatal: Unable to create '/home/lh/TriScope-LLM/.git/worktrees/cross-model-validation-plan-20260426133451/index.lock': Read-only file system
```

GitHub fallback branch creation for `codex/dualscope-cross-model-validation-plan` was attempted and cancelled by the connector. No branch, commit, PR, auto merge, force push, branch deletion, remote rewrite, benchmark truth change, gate change, route_c continuation, or `199+` generation occurred.
