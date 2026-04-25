# DualScope Qwen2.5-7B First-Slice Response Generation Plan

## Purpose / Big Picture

This plan prepares the first Qwen2.5-7B-Instruct response-generation handoff for the DualScope-LLM SCI3 track. It keeps Qwen2.5-7B-Instruct as the main experimental model while preserving the frozen first-slice scope: Stanford Alpaca first-slice, lexical trigger `cftrigger`, fixed target response text, and the already frozen Stage 1 / Stage 2 / Stage 3 protocol.

This is a planning and readiness task only. It does not run Qwen2.5-7B, generate responses, extract logprobs, compute AUROC/F1/ASR/utility, alter benchmark truth, alter gates, train, finetune, or expand to the full matrix.

## Scope

### In Scope

- Prepare the Qwen2.5-7B first-slice response-generation plan.
- Audit required input artifacts for Stanford Alpaca labeled pairs and prior target-response-generation planning.
- Reuse the SCI3 model-axis role contract: Qwen2.5-7B is the main model, Qwen2.5-1.5B is pilot/debug only, and Llama/Mistral are later cross-model candidates.
- Record readiness checks for local Qwen2.5-7B availability, GPU visibility, first-slice inputs, trigger/target scope, and frozen protocol dependencies.
- Write blockers when local 7B resources or required inputs are absent.
- Write output artifacts under `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default`.

### Out of Scope

- Running Qwen2.5-7B response generation.
- Running Stage 1 / Stage 2 / Stage 3 over Qwen2.5-7B outputs.
- Claiming that responses, logprobs, ASR, clean utility, AUROC, F1, or latency exist.
- Changing labels, benchmark truth, gates, trigger definitions, target definitions, or frozen protocol contracts.
- Running the full dataset / trigger / target / model matrix.
- Continuing historical route_c plans or generating 199+ planning.
- Training, full finetuning, LoRA, or QLoRA.

## Repository Context

- `AGENTS.md`, `PLANS.md`, and `DUALSCOPE_MASTER_PLAN.md` define the current DualScope mainline: Stage 1 illumination screening, Stage 2 confidence verification, and Stage 3 budget-aware lightweight fusion.
- `DUALSCOPE_TASK_QUEUE.md` defines this task after `dualscope-main-model-axis-upgrade-plan`.
- `docs/dualscope_sci3_model_matrix.md` and `docs/dualscope_sci3_resource_plan_2x3090.md` define Qwen2.5-7B as the main experimental model and require real local resources before execution.
- `outputs/dualscope_main_model_axis_upgrade_plan/default` exists and records that Qwen2.5-7B is planned / external-resource-required.
- `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl` is expected but missing in this isolated worktree.
- `outputs/dualscope_first_slice_target_response_generation_plan/default` is expected but missing in this isolated worktree.

Historical TriScope / route_c artifacts are not used by this plan except as background reliability foundation. This plan does not extend route_c or present it as the current research contribution.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-first-slice-response-generation-plan.md`
- `docs/dualscope_qwen2p5_7b_first_slice_response_generation_plan.md`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_scope.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_source_audit.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_readiness.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_blockers.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_command_plan.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_summary.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_verdict.json`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default/dualscope_qwen2p5_7b_first_slice_response_generation_plan_report.md`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and SCI3 artifacts.
- [x] M2: Audit expected inputs and local Qwen2.5-7B resource availability.
- [x] M3: Write Qwen2.5-7B first-slice response-generation plan doc and readiness artifacts.
- [x] M4: Validate that the package is planning-only and records blockers honestly.
- [x] M5: Complete PR workflow without auto merge, force push, branch deletion, or remote rewrite.

## Surprises & Discoveries

- The isolated worktree contains only the Alpaca first-slice source manifest, not `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`.
- The expected prior directory `outputs/dualscope_first_slice_target_response_generation_plan/default` is absent in this worktree.
- Obvious local Qwen2.5-7B paths are absent: `/home/lh/TriScope-LLM/local_models/Qwen2.5-7B-Instruct` and `local_models/Qwen2.5-7B-Instruct`.
- GPU visibility is present, including two RTX 3090 GPUs, but this only proves hardware visibility. It does not prove Qwen2.5-7B inference readiness.

## Decision Log

- The final verdict is `Partially validated` because the plan and blocker package are complete, but required execution inputs and the real 7B local path are missing.
- No fallback to Qwen2.5-1.5B is used for this task because 1.5B is restricted to pilot/debug/automation/ablation and cannot substitute for Qwen2.5-7B main-model evidence.
- The next executable task must remain blocked until a real Qwen2.5-7B path and the expected first-slice input artifacts are available.

## Plan of Work

The successor execution task should run only after the blocker register is cleared. It should consume row-level generation requests from the first-slice labeled-pair and target-response-generation plan artifacts, load Qwen2.5-7B-Instruct from a verified local path or approved external resource, generate responses with deterministic first-slice settings, and write capability-mode flags with every output artifact. It must not compute detection metrics unless real responses and aligned scores are present.

## Concrete Steps

1. Restore or regenerate `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl` from the frozen Alpaca first-slice materialization chain.
2. Restore or regenerate `outputs/dualscope_first_slice_target_response_generation_plan/default`.
3. Provide a real Qwen2.5-7B-Instruct local path, or explicitly mark the successor execution task as external-resource-required.
4. Re-run readiness checks for the exact model path, tokenizer path, GPU visibility, dependency availability, and first-slice artifact schema.
5. Only then run the successor `dualscope-qwen2p5-7b-first-slice-response-generation` task.

## Validation and Acceptance

This planning package is acceptable when:

- It names Qwen2.5-7B-Instruct as the main experimental model.
- It preserves Stanford Alpaca first-slice, lexical trigger `cftrigger`, fixed target text, and frozen Stage 1 / Stage 2 / Stage 3 protocol.
- It records that expected inputs and local 7B resources are missing when they are missing.
- It does not create model responses, logprobs, AUROC, F1, ASR, utility, latency, benchmark truth, or gates.
- Its final verdict is one of the task-approved verdicts.

Current verdict: `Partially validated`.

PR workflow status: local git staging was blocked by read-only worktree metadata, so the GitHub API / `gh` fallback opened PR #28 and posted `@codex review`. No auto merge, force push, branch deletion, or remote rewrite was performed.

## Idempotence and Recovery

The output directory is planning-only and can be regenerated safely. Once the missing labeled pairs, target-response plan artifacts, and Qwen2.5-7B local path are supplied, update readiness artifacts or run the successor execution task. Do not retroactively mark this planning task as having produced responses or metrics.
