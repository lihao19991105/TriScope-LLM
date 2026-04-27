# DualScope Qwen2.5-7B Semantic Trigger Smoke Response Generation

## Purpose / Big Picture

Execute the first real semantic-trigger smoke after the bounded Alpaca main-slice result package. This task checks whether a semantic phrase trigger can be applied in a small, auditable Qwen2.5-7B setting without expanding to a trigger family matrix.

## Scope

### In Scope

- Qwen2.5-7B local model at `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Stanford Alpaca bounded slice from `alpaca_first_slice_labeled_pairs.jsonl`.
- One semantic phrase trigger: `the task is already complete`.
- `max_examples=8`, `batch_size=1`, `max_new_tokens=64`.
- `without_logprobs` fallback.
- Real response JSONL or explicit blocker JSON.

### Out of Scope

- Full trigger matrix.
- Full Alpaca / AdvBench / JBB execution.
- Training, LoRA, QLoRA, or full finetune.
- Clean utility claims.
- Fabricated responses, logprobs, labels, metrics, benchmark truth, or gates.

## Execution

Run:

```bash
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation.py \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --target-response-plan-dir outputs/dualscope_first_slice_target_response_generation_plan/default \
  --output-dir outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default \
  --max-examples 8 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --allow-without-logprobs
```

## Validation

- `semantic_trigger_smoke_responses.jsonl` row count is greater than zero, or `semantic_trigger_smoke_blockers.json` records a real blocker type.
- tracked registry routes to `dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-computation` only when real rows exist.
- No metrics are computed in this response-generation task.

## Progress

- 2026-04-27: Added CLI and generated 16 real semantic-trigger smoke response rows.
