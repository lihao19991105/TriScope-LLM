# DualScope Qwen2.5-7B Resource Materialization and Config

## Purpose / Big Picture

This plan turns Qwen2.5-7B-Instruct from a planned SCI3 main model into an auditable local resource state. It prevents the task queue from repeatedly selecting the response-generation plan when required model, data, or target-response artifacts are missing.

## Scope

### In Scope

- Check and optionally download `Qwen/Qwen2.5-7B-Instruct`.
- Record local model path, tokenizer/config readiness, disk/GPU readiness, labeled pairs, target-response plan outputs, and cross-model candidate status.
- Produce machine-readable verdict artifacts.
- Insert an explicit resource materialization task before Qwen2.5-7B response-generation planning.

### Out of Scope

- No model response generation.
- No full matrix execution.
- No full finetune, LoRA, or QLoRA training.
- No benchmark truth or gate changes.
- No route_c or 199+ continuation.
- No fake model paths, downloads, responses, logprobs, or metrics.

## Repository Context

- Core implementation: `src/eval/dualscope_qwen2p5_7b_resource_materialization.py`.
- Shared helpers: `src/eval/dualscope_qwen2p5_7b_resource_common.py`.
- CLI entrypoints live under `scripts/`.
- Artifacts are written under `outputs/dualscope_qwen2p5_7b_resource_materialization/default`.
- Queue routing is defined in `DUALSCOPE_TASK_QUEUE.md`.

## Deliverables

- Resource materialization CLI.
- Post-analysis CLI.
- Readiness check CLI.
- SCI3 model resource docs.
- Queue entry and routing from model-axis upgrade to resource materialization.

## Progress

- [x] Create resource materialization plan.
- [x] Implement resource materialization and post-analysis CLIs.
- [x] Add queue routing for resource materialization.
- [x] Run validation and materialization.
- [ ] Create PR and trigger review.

## Surprises & Discoveries

- The current root filesystem has less than the configured 30 GB free-space threshold, so Qwen2.5-7B download must be blocked rather than attempted.

## Decision Log

- Keep `--allow-download` opt-in and gate actual download on disk readiness.
- Do not download Llama/Mistral candidates in this task; record them as planned external resources.
- Emit a bridge verdict for the Qwen2.5-7B response-generation plan so the orchestrator can route to repair instead of repeating an incomplete plan.

## Plan of Work

Implement the checks first, run them honestly, then update queue routing so resource blockers are explicit queue state rather than hidden missing-output state.

## Concrete Steps

1. Compile new modules and CLIs.
2. Run `--help` for all new CLIs.
3. Run materialization with `--allow-download`.
4. Run post-analysis.
5. Run task orchestrator dry-run.
6. Commit and open a PR.

## Validation and Acceptance

The task is accepted if all artifacts are written, the final verdict is one of the allowed values, no model availability is faked, and task orchestrator no longer repeats the response-generation plan when resource blockers exist.

## Idempotence and Recovery

The materialization CLI is safe to rerun. If disk is insufficient or Hugging Face access fails, it writes blockers and manual recovery instructions without modifying benchmark truth or gates.

## Outputs and Artifacts

- `outputs/dualscope_qwen2p5_7b_resource_materialization/default`
- `outputs/dualscope_qwen2p5_7b_resource_materialization_analysis/default`
- Bridge verdict under `outputs/dualscope_qwen2p5_7b_first_slice_response_generation_plan/default`.

## Remaining Risks

- Download requires enough disk and public model access.
- Tokenizer/config checks require `transformers`.
- Full model load is intentionally disabled by default to avoid OOM.

## Next Suggested Plan

If validated, continue to `dualscope-qwen2p5-7b-first-slice-response-generation-plan`. If partially validated, run `dualscope-qwen2p5-7b-resource-materialization-repair`.
