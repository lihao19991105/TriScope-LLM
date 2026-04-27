# DualScope Qwen2.5-7B Alpaca Main-Slice Bounded Response Generation Retry

## Purpose / Big Picture

This plan executes the bounded Qwen2.5-7B Stanford Alpaca main-slice response-generation retry after the worktree GPU / bitsandbytes / input readiness repair. The task is part of the DualScope-LLM SCI3 main-model track and is intended to produce real local HuggingFace model responses for clean and poisoned Alpaca rows, or a qualified runtime blocker if the isolated worktree cannot access the required runtime.

## Scope

### In Scope

- Read the validated Alpaca main-slice plan verdict.
- Use Qwen2.5-7B-Instruct from `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Run the bounded response-generation CLI with `allow_without_logprobs`.
- Use 4-bit loading only if `bitsandbytes` is available.
- If the primary bounded run cannot produce real responses, run one reduced retry.
- Persist response rows, summary, blockers, report, verdict, and registry artifacts.
- Preserve an honest blocker if CUDA/model execution is unavailable.

### Out of Scope

- No metric computation.
- No benchmark-truth changes.
- No gate changes.
- No full Alpaca run or full experiment matrix.
- No training or finetuning.
- No route_c or 199+ planning.
- No fabricated responses, labels, logprobs, metrics, reviews, or CI.

## Repository Context

- CLI entrypoint: `scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py`
- Core implementation: `src/eval/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py`
- Input pairs: `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`
- Plan verdict: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json`
- Runtime readiness registry: `.reports/dualscope_task_verdicts/dualscope-worktree-gpu-bnb-input-readiness-repair.json`
- Output directory: `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default`

This plan serves the current DualScope main line. It does not extend the historical TriScope / route_c chain.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry.md`
- `docs/dualscope_qwen2p5_7b_alpaca_main_slice_bounded_response_generation_retry.md`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_responses.jsonl`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_generation_summary.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_generation_blockers.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_generation_report.md`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/qwen2p5_7b_alpaca_main_slice_response_generation_verdict.json`

## Progress

- [x] Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md.
- [x] Read the worktree readiness registry.
- [x] Checked `bitsandbytes` availability and Torch CUDA visibility.
- [x] Ran the primary bounded response-generation command without 4-bit loading.
- [x] Ran the reduced retry after the primary run produced no responses.
- [x] Hardened blocker artifacts to expose canonical `blocker_type: torch_cuda_unavailable`.
- [x] Regenerated final artifacts from the reduced retry.
- [x] Wrote documentation for the retry result.

## Surprises & Discoveries

- `bitsandbytes` is not installed in the worktree virtual environment, so `--load-in-4bit` was not used.
- Torch imports successfully, but `torch.cuda.is_available()` is `False` and `torch.cuda.device_count()` is `0` under `CUDA_VISIBLE_DEVICES=2,3`.
- The input JSONL and model directory exist, and the slice selector produced the expected reduced retry rows.
- No real `model_response` values were generated because CPU generation is disabled for this task and CUDA is unavailable.

## Decision Log

- Used fp16 / low-memory fallback instead of 4-bit because `bitsandbytes` is unavailable.
- Ran the reduced retry once after the primary bounded run failed to produce responses.
- Kept the final verdict as `Partially validated` because inputs and bounded selection are valid, but response generation produced zero real rows.
- Routed next work to response-generation repair rather than metric computation because `row_count_generated` is `0`.

## Plan of Work

The work first checks runtime prerequisites, then runs the requested bounded command. If it cannot generate responses, one smaller retry is executed. Artifacts must record either real model responses or an explicit blocker. Since CUDA is unavailable in this worktree, the result is a qualified partial validation with a canonical runtime blocker.

## Concrete Steps

1. Probe the virtual environment for `torch`, CUDA visibility, `bitsandbytes`, and `accelerate`.
2. Run the primary bounded command:
   `--max-source-examples 16 --expected-response-rows 32 --max-new-tokens 64 --max-generation-attempts 32`.
3. Because the primary run generated zero rows, run the reduced retry:
   `--max-source-examples 4 --expected-response-rows 8 --max-new-tokens 32 --max-generation-attempts 8`.
4. Verify output JSONL, summary, blocker, verdict, report, and registry artifacts.
5. Record the result and next task.

## Validation and Acceptance

Validated completion would require `row_count_generated > 0` and non-empty real `model_response` values. The completed retry did not meet that bar. It produced a qualified partial validation with:

- `final_verdict`: `Partially validated`
- `blocker_type`: `torch_cuda_unavailable`
- `raw_blocker`: `cuda_unavailable_cpu_generation_disabled`
- `row_count_generated`: `0`
- `row_count_blocked`: `8`
- `model_response_fabricated`: `false`
- `logprobs_fabricated`: `false`
- `metrics_computed`: `false`

The next task is `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair`.

