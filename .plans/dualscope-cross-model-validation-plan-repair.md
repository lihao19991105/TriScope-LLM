# DualScope Cross-Model Validation Plan Repair

## Purpose / Big Picture

Repair the partially validated `dualscope-cross-model-validation-plan` by separating verified local resource facts from planned cross-model resources.

This task closes a planning ambiguity: the cross-model plan was structurally valid, but it could not be marked validated while the expected ignored output directory was absent and both allowed cross-model model resources were missing. The repair records that this is acceptable for a planning-only gate when missing Llama/Mistral resources are honestly marked `planned` / `external-resource-required`, no execution claims are made, and the Qwen2.5 model roles remain fixed.

## Scope

### In Scope

- Read the DualScope instructions, master plan, task queue, previous cross-model verdict registry, SCI3 model matrix, and existing cross-model plan.
- Verify local availability for `Llama-3.1-8B-Instruct` and `Mistral-7B-Instruct-v0.3` candidates in checked local, mounted, and Hugging Face cache paths.
- Preserve `Qwen2.5-7B-Instruct` as the SCI3 main model and `Qwen2.5-1.5B-Instruct` as pilot / debug / automation / ablation only.
- Produce repaired planning artifacts, candidate availability matrix, license/auth blocker notes, next-step recommendation, report, verdict, and tracked task registry.
- Route validated repair to `queue_complete`.

### Out of Scope

- No gated model download.
- No response generation.
- No full matrix execution.
- No training, LoRA, QLoRA, or finetuning.
- No benchmark truth or gate modification.
- No fabricated local paths, model responses, labels, logprobs, AUROC, F1, ASR, utility, latency, or query-cost metrics.
- No historical route_c continuation and no `199+` planning.
- No auto merge, force push, branch deletion, remote rewrite, or unrelated PR merge.

## Repository Context

- Previous partial registry: `.reports/dualscope_task_verdicts/dualscope-cross-model-validation-plan.json`.
- Prior plan and docs: `.plans/dualscope-cross-model-validation-plan.md`, `docs/dualscope_cross_model_validation_plan.md`.
- SCI3 model-axis contract: `docs/dualscope_sci3_model_matrix.md`.
- Task queue entry: `DUALSCOPE_TASK_QUEUE.md`.
- Repair output docs: `docs/dualscope_cross_model_validation_plan_repair.md`.
- Repair artifacts: `outputs/dualscope_cross_model_validation_plan_repair/default` and `outputs/dualscope_cross_model_validation_plan_repair_analysis/default`.

Historical TriScope / route_c files are not used for this repair except as non-mainline reliability background. This task does not extend them.

## Deliverables

- `.plans/dualscope-cross-model-validation-plan-repair.md`
- `docs/dualscope_cross_model_validation_plan_repair.md`
- `.reports/dualscope_task_verdicts/dualscope-cross-model-validation-plan-repair.json`
- `outputs/dualscope_cross_model_validation_plan_repair/default/dualscope_cross_model_validation_plan_repair_summary.json`
- `outputs/dualscope_cross_model_validation_plan_repair/default/dualscope_cross_model_candidate_availability_matrix.json`
- `outputs/dualscope_cross_model_validation_plan_repair/default/dualscope_cross_model_license_auth_blockers.json`
- `outputs/dualscope_cross_model_validation_plan_repair/default/dualscope_cross_model_next_step_recommendation.json`
- `outputs/dualscope_cross_model_validation_plan_repair/default/dualscope_cross_model_validation_plan_repair_report.md`
- `outputs/dualscope_cross_model_validation_plan_repair/default/dualscope_cross_model_validation_plan_repair_verdict.json`
- `outputs/dualscope_cross_model_validation_plan_repair_analysis/default/dualscope_cross_model_validation_plan_repair_verdict.json`

## Progress

- [x] M1: Read required repository instructions and DualScope planning context.
- [x] M2: Read previous partial cross-model plan registry and SCI3 model matrix.
- [x] M3: Verify Qwen2.5 role facts and local availability observations without running models.
- [x] M4: Verify Llama/Mistral candidate local availability without downloading gated resources.
- [x] M5: Emit repaired plan, docs, output artifacts, analysis artifact, and tracked registry.
- [x] M6: Update validated queue routing to `queue_complete`.
- [x] M7: Run lightweight validation checks.

## Surprises & Discoveries

- The prior expected directory `outputs/dualscope_cross_model_validation_plan/default` is absent in this worktree because `outputs/` is ignored and only the tracked registry persisted.
- `Qwen2.5-7B-Instruct` is locally visible at `/mnt/sda3/lh/models/qwen2p5-7b-instruct` with config, tokenizer, and safetensors shard files. This confirms main-model resource presence only; it is not a response-generation or metric claim.
- `Qwen2.5-1.5B-Instruct` remains visible at `/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct` and remains pilot / debug / automation / ablation only.
- No `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3` candidate was found in the checked worktree, shared local model, mounted model, or Hugging Face cache paths.
- Local git commit could not complete because the shared worktree metadata path is read-only. A GitHub fallback branch creation call for `codex/cross-model-validation-plan-repair` was attempted and cancelled by the connector; no remote mutation was completed.

## Decision Log

- Final verdict is `Cross-model validation plan repair validated` because the repair resolves the planning ambiguity by explicitly marking missing cross-model candidates as `planned` / `external-resource-required` and making no execution claims.
- The next task is `queue_complete`, not cross-model execution, because the repair task's purpose is planning closure only.
- Llama and Mistral remain the only allowed cross-model validation candidates.
- Qwen2.5-7B remains the main SCI3 model; Qwen2.5-1.5B remains pilot / ablation only.
- Cross-model execution is blocked until one allowed candidate is locally materialized with tokenizer/config files and any license/auth requirements are satisfied.

## Plan of Work

The repair keeps cross-model validation as a future resource-gated generalization check after Qwen2.5-7B evidence is packaged. It does not substitute the pilot model or pretend missing cross-model resources exist.

The first future executable slice should reuse the same Qwen2.5-7B row IDs, labels, trigger family, target family, Stage 1 / Stage 2 / Stage 3 contracts, and budget traces. `without_logprobs` remains the default unless real token logprob artifacts are produced by the selected backend.

## Concrete Steps

1. Keep the previous partial cross-model plan as historical input, not execution evidence.
2. Use the tracked repair registry and SCI3 model matrix as the model-role contract.
3. Record checked local paths for Llama and Mistral candidates.
4. Mark missing Llama and Mistral candidates as `planned` / `external-resource-required`.
5. Record license/auth blockers for gated or restricted candidate access.
6. Emit docs and JSON artifacts under the repair output directories.
7. Set the tracked repair registry verdict to `Cross-model validation plan repair validated` and `next_task` to `queue_complete`.

## Validation and Acceptance

This repair is accepted when:

- The ExecPlan, docs, output artifacts, analysis artifact, and tracked registry exist.
- The final verdict is one of `Cross-model validation plan repair validated`, `Partially validated`, or `Not validated`.
- The validated registry routes to `queue_complete`.
- Missing Llama/Mistral resources are marked `planned` / `external-resource-required`.
- No generated responses, logprobs, detection metrics, ASR, utility, benchmark truth, gates, route_c work, or `199+` planning are introduced.

## Idempotence and Recovery

The output artifacts can be regenerated from the same local path checks. If a Llama or Mistral candidate is later materialized, rerun only the resource check and update the availability artifacts. Do not add performance claims to this repair.

## Remaining Risks

- Cross-model execution remains blocked until one allowed candidate is locally materialized and any license/auth requirement is satisfied.
- The ignored prior output directory remains absent; the tracked previous registry is the durable handoff.
- With-logprobs cross-model validation remains planned until real backend logprob artifacts exist.

## Current Verdict

`Cross-model validation plan repair validated`

## Next Suggested Task

`queue_complete`

## PR Workflow Status

Local commit failed with:

```text
fatal: Unable to create '/home/lh/TriScope-LLM/.git/worktrees/cross-model-validation-plan-repair-20260426135217/index.lock': Read-only file system
```

GitHub fallback branch creation for `codex/cross-model-validation-plan-repair` was attempted and cancelled by the connector. No auto merge, force push, branch deletion, remote rewrite, benchmark truth change, gate change, route_c continuation, or `199+` generation occurred.
