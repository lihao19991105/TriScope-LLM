# DualScope JBB Small-Slice Response Generation

## Purpose / Big Picture

Generate a bounded set of real Qwen2.5-7B-Instruct responses for the validated JBB small slice, or record a truthful runtime blocker if generation cannot safely complete. This advances the DualScope SCI3 expansion track by adding a safety-benchmark response artifact without expanding into a full matrix, training, or metric computation.

## Scope

### In Scope

- Use `data/jbb/small_slice/jbb_small_slice_source.jsonl` and the validated JBB materialization registry.
- Select at most 16 JBB rows in deterministic file order.
- Build safety-aware prompts from `behavior_text` only.
- Generate with `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, batch size 1, max new tokens 64, seed `20260427`.
- Record `without_logprobs_fallback=true` because this runner does not extract token logprobs.
- Write response, summary, blocker, report, verdict, and tracked registry artifacts.

### Out of Scope

- Full matrix execution.
- Training or finetuning.
- Detection metrics, benchmark truth changes, gates, or labels.
- Route-c, `199+`, reasoning branch expansion, or PR #14 changes.
- Writing actionable unsafe model output into reports.

## Repository Context

- Source input: `data/jbb/small_slice/jbb_small_slice_source.jsonl`
- Plan input: `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation-plan.json`
- Materialization registry: `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json`
- Output directory: `outputs/dualscope_jbb_small_slice_response_generation/default`
- This plan follows the existing AdvBench small-slice response generation pattern and the external GPU runner convention.

Historical TriScope / route_c artifacts are not used except as repository history. This task serves the current DualScope illumination/confidence/fusion experimental expansion track.

## Deliverables

- `src/eval/dualscope_jbb_small_slice_response_generation.py`
- `scripts/build_dualscope_jbb_small_slice_response_generation.py`
- `scripts/run_dualscope_jbb_small_slice_response_generation.sh`
- `docs/dualscope_jbb_small_slice_response_generation.md`
- `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation.json`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_responses.jsonl`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_summary.json`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_blockers.json`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_report.md`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_verdict.json`

## Milestones

1. Add bounded JBB response-generation builder and CLI.
2. Add external-runner shell entrypoint and documentation.
3. Run syntax validation.
4. Execute bounded generation if CUDA is visible; otherwise produce explicit blocker artifacts.
5. Inspect artifacts and update this plan with the final status.

## Validation

Run:

```bash
python3 -m py_compile \
  src/eval/dualscope_jbb_small_slice_response_generation.py \
  scripts/build_dualscope_jbb_small_slice_response_generation.py
```

Then run:

```bash
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 \
HF_HOME=/mnt/sda3/lh/huggingface \
HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub \
TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers \
TMPDIR=/mnt/sda3/lh/tmp \
python3 scripts/build_dualscope_jbb_small_slice_response_generation.py \
  --source-jsonl data/jbb/small_slice/jbb_small_slice_source.jsonl \
  --plan-verdict .reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation-plan.json \
  --materialization-verdict .reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json \
  --materialization-output-dir outputs/dualscope_jbb_small_slice_materialization/default \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --output-dir outputs/dualscope_jbb_small_slice_response_generation/default \
  --max-examples 16 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --seed 20260427 \
  --device-map auto \
  --safety-mode refusal_preserving_eval \
  --allow-without-logprobs
```

Successful completion requires real non-empty model responses for all selected rows and no blockers. If CUDA/model/dependency/runtime failure prevents generation, the task must be partially validated with explicit blocker artifacts and no fabricated responses.

## Progress

- 2026-04-27: Created task ExecPlan after reading `AGENTS.md`, `PLANS.md`, `DUALSCOPE_MASTER_PLAN.md`, `DUALSCOPE_TASK_QUEUE.md`, and the response-generation plan verdict.
- 2026-04-27: Added bounded JBB builder, CLI, host-side runner script, and documentation.
- 2026-04-27: `python3 -m py_compile` passed for the new module and CLI.
- 2026-04-27: Executed the bounded command with `CUDA_VISIBLE_DEVICES=2,3`, `batch_size=1`, `max_new_tokens=64`, and `allow_without_logprobs`. The run produced `Partially validated` blocker artifacts with `blocker_type=torch_cuda_unavailable`, `generated_row_count=0`, and `blocked_row_count=16`. No model responses, logprobs, metrics, benchmark truth, gates, training, route_c, or `199+` artifacts were fabricated or modified.
- 2026-04-27: Repair pass rebuilt the bounded artifact directory in the isolated worktree and added `.plans/dualscope-jbb-small-slice-response-generation-repair.md` plus repair/compression artifacts. The response-generation source task remains `Partially validated`; the repair task is validated because it preserves the CUDA blocker and routes to blocker closure without fabricating responses.

## Risks

- CUDA may not be visible inside the Codex sandbox even when available from the host shell.
- The JBB prompts are harmful-behavior benchmark prompts, so reports must avoid verbatim completions and the generation prompt must preserve refusal behavior.
- Token logprobs are not produced by this runner; downstream tasks must treat this as `without_logprobs`.
