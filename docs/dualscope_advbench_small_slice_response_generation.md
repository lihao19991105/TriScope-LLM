# DualScope AdvBench Small-Slice Response Generation

This task attempts bounded, safety-aware Qwen2.5-7B-Instruct response generation for the validated AdvBench small slice, or writes a structured blocker when real generation is not feasible.

## Scope

| Axis | Value |
| --- | --- |
| Source JSONL | `data/advbench/small_slice/advbench_small_slice_source.jsonl` |
| Max examples | 16 |
| Batch size | 1 |
| Max new tokens | 64 |
| Model path | `/mnt/sda3/lh/models/qwen2p5-7b-instruct` |
| Safety mode | `refusal_preserving_eval` |
| Logprob mode | `without_logprobs_fallback=true` |

## Run Command

```bash
HF_HOME=/mnt/sda3/lh/huggingface \
HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub \
TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers \
TMPDIR=/mnt/sda3/lh/tmp \
CUDA_DEVICE_ORDER=PCI_BUS_ID \
CUDA_VISIBLE_DEVICES=2,3 \
python3 scripts/build_dualscope_advbench_small_slice_response_generation.py \
  --source-jsonl data/advbench/small_slice/advbench_small_slice_source.jsonl \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --output-dir outputs/dualscope_advbench_small_slice_response_generation/default \
  --max-examples 16 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --seed 20260427 \
  --device-map auto \
  --safety-mode refusal_preserving_eval \
  --allow-without-logprobs
```

## Artifacts

- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl`
- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_summary.json`
- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_blockers.json`
- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_report.md`
- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json`

The Markdown report intentionally omits verbatim harmful instructions and model completions. The JSONL response artifact preserves row-level audit fields and marks blocked rows explicitly.

## Current Result

In this isolated Codex worktree, CUDA is not visible to the runtime. The task therefore records a real `torch_cuda_unavailable` blocker instead of fabricating model responses. The tracked verdict is not validated.
