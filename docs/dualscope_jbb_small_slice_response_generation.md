# DualScope JBB Small-Slice Response Generation

This task runs a bounded, safety-aware JBB response-generation slice for Qwen2.5-7B-Instruct. It does not compute metrics, alter benchmark truth, change gates, train models, or expand to a full matrix.

## Inputs

- Source JSONL: `data/jbb/small_slice/jbb_small_slice_source.jsonl`
- Planning verdict: `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation-plan.json`
- Materialization verdict: `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json`
- Model path: `/mnt/sda3/lh/models/qwen2p5-7b-instruct`

The materialization output directory may be absent in this isolated worktree; the builder records that fact and relies on the tracked source JSONL plus validated materialization registry.

## Safety Contract

The runner uses `behavior_text` as the instruction and wraps it in a refusal-preserving safety-evaluation prompt. It does not add jailbreak wrappers, target descriptors, trigger text, or target strings as instructions. Reports omit verbatim harmful prompts and completions. If generated output appears actionable and unsafe, the row is suppressed and marked as `blocked_by_output_safety_filter`.

## Command

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

For host-side execution, use:

```bash
bash scripts/run_dualscope_jbb_small_slice_response_generation.sh
```

## Outputs

- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_responses.jsonl`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_summary.json`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_blockers.json`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_report.md`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation.json`

Every response row includes `sample_id`, `dataset_id`, `instruction`, `model_response`, `generation_mode`, `capability_flags`, `safety_mode`, and `without_logprobs_fallback`.

## Current Execution Result

The bounded command was executed in the isolated task worktree on 2026-04-27. CUDA was not visible to PyTorch from this context, so the task wrote explicit blocker artifacts instead of fabricated responses:

- Final verdict: `Partially validated`
- Generated rows: `0`
- Blocked rows: `16`
- Blocker type: `torch_cuda_unavailable`
- Without-logprobs fallback: `True`
- Model responses fabricated: `False`
- Metrics computed: `False`
