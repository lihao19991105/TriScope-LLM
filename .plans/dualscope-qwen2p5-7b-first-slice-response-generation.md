# DualScope Qwen2.5-7B First-Slice Response Generation

## Purpose / Big Picture

This task executes or prepares the first scoped Qwen2.5-7B-Instruct response-generation pass for the DualScope-LLM SCI3 track. It consumes the already validated Stanford Alpaca first-slice target-response plan, keeps Qwen2.5-7B as the main experimental model, and writes row-level response artifacts or explicit blockers without computing detection metrics.

The task serves the current DualScope mainline by unblocking later ASR / clean-utility metric computation with real model responses while preserving the frozen first-slice scope.

## Scope

### In Scope

- Use Stanford Alpaca first-slice labeled pairs.
- Use target-response plan rows from `outputs/dualscope_first_slice_target_response_generation_plan/default`.
- Use local Qwen2.5-7B-Instruct through `models/qwen2p5-7b-instruct`.
- Preserve lexical trigger `cftrigger` and fixed target text `I have completed the requested instruction.`
- Run batch size 1 response generation when runtime resources allow.
- Record capability mode, response generation mode, fallback flags, blockers, row-level artifacts, and final verdict.

### Out of Scope

- Training, full finetune, LoRA, or QLoRA training.
- Running the full matrix.
- Computing or claiming AUROC, F1, ASR, clean utility, latency metrics, or paper-level performance.
- Modifying benchmark truth, labels, gates, trigger definitions, target definitions, or route_c chains.
- Generating 199+ historical plans.

## Repository Context

- `AGENTS.md`, `PLANS.md`, and `DUALSCOPE_MASTER_PLAN.md` define the current DualScope mainline.
- `.plans/dualscope-qwen2p5-7b-first-slice-response-generation-plan.md` is the predecessor readiness plan.
- `outputs/dualscope_first_slice_target_response_generation_plan/default/dualscope_first_slice_target_response_generation_plan_rows.jsonl` provides the planned row-level generation requests.
- `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl` provides the labeled first-slice pair source.
- `models/qwen2p5-7b-instruct` is the repo binding for the local Qwen2.5-7B-Instruct model snapshot.

Historical TriScope / route_c artifacts are not used except as reliability background. This task does not continue route_c.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-first-slice-response-generation.md`
- `src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py`
- `scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py`
- `docs/dualscope_qwen2p5_7b_first_slice_response_generation.md`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default`

## Progress

- [x] M1: Read required repository guidance and predecessor Qwen plan.
- [x] M2: Audit required inputs and model binding.
- [x] M3: Implement response-generation module and CLI with honest fallback/blocker artifacts.
- [x] M4: Run validation / generation attempt and write output artifacts.
- [ ] M5: Complete PR workflow without auto merge, force push, branch deletion, or remote rewrite.

## Surprises & Discoveries

- The predecessor blockers have been cleared in this worktree: labeled pairs, target-response plan output, and the repo-local model symlink now exist.
- `python3` has `torch` and `transformers`, but `bitsandbytes` and `accelerate` are unavailable, so 4-bit loading and automatic multi-GPU device mapping are not available in this environment.
- The first real generation attempt was launched with `CUDA_VISIBLE_DEVICES=2,3` and loaded checkpoint shards, but it placed memory on physical GPU 2, which had only about 1.4 GiB free before launch, then hung without flushing artifacts. A prepare-only fallback artifact package was written instead.
- After the hung attempt, `nvidia-smi` in later checks reported that it could not communicate with the NVIDIA driver, so response generation remains runtime-blocked in this session.

## Decision Log

- The generator uses the target-response plan rows as the execution slice instead of all labeled-pair rows, preserving the previously validated minimal first-slice scope.
- The generator records `target_matched` per row for later ASR use, but does not aggregate ASR or report metrics in this task.
- If model loading or generation fails, artifacts still record blockers, fallback flags, and `model_response_fabricated: false`.
- The final task verdict is `Partially validated`: inputs, model binding, CLI, and artifact contract are validated, but real response rows are blocked by the hung CUDA/model generation attempt.

## Plan of Work

Implement a minimal HuggingFace local generation path with lazy dependency imports, deterministic generation settings, batch size 1, and explicit runtime checks. Then run it under `CUDA_VISIBLE_DEVICES=2,3`; if CUDA, OOM, logprob, or dependency capability is unavailable, record it honestly in the output package.

## Concrete Steps

1. Create the response-generation core module.
2. Create the CLI wrapper.
3. Create a run document with the exact command and artifact contract.
4. Compile the new Python files.
5. Run the CLI on the target-response plan rows.
6. Inspect the verdict artifact and update this plan.

## Validation and Acceptance

The task is acceptable when it writes a verdict artifact with exactly one of:

- `Qwen2.5-7B first-slice response generation validated`
- `Partially validated`
- `Not validated`

The output package must include capability mode, response generation mode, fallback flags, blockers, and no fabricated model responses or metrics.

Current verdict: `Partially validated`.

## Idempotence and Recovery

The output directory is safe to regenerate. If OOM occurs, rerun the same command after freeing GPU memory or lowering `--max-new-tokens`; do not substitute Qwen2.5-1.5B as main-model evidence. If dependencies are missing, install or enable them in the environment and rerun the same CLI.
