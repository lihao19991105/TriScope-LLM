# DualScope JBB Small-Slice Response Generation Plan

This is a planning handoff only. It does not contain model responses, logprobs, metrics, labels, or generated harmful content.

## Frozen Scope

| Axis | Value |
| --- | --- |
| Dataset | JBB-Behaviors small slice |
| Source JSONL | `data/jbb/small_slice/jbb_small_slice_source.jsonl` |
| Registry input | `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json` |
| Available rows | 16 |
| Default max examples | 16 |
| Batch size | 1 |
| Max new tokens | 64 |
| Model | Qwen2.5-7B-Instruct |
| Model path | `/mnt/sda3/lh/models/qwen2p5-7b-instruct` |
| Runner | external GPU-visible shell / `nohup`, not forced through Codex sandbox CUDA |
| Safety mode | `refusal_preserving_eval` |
| Logprob mode | `without_logprobs_fallback=true` unless real token logprobs are produced |

## Input Audit

- The source JSONL is present with 16 rows.
- The tracked materialization verdict registry is present and validated.
- The registry records `data_fabricated=false`, `responses_generated=false`, `metrics_computed=false`, `benchmark_truth_changed=false`, and `gate_changed=false`.
- The referenced materialization output directory is absent in this isolated worktree, so this plan does not claim availability beyond the source JSONL and tracked registry.

## External Runner Environment

```bash
export HF_HOME=/mnt/sda3/lh/huggingface
export HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub
export TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers
export TMPDIR=/mnt/sda3/lh/tmp
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=2,3
```

## Planned Command Shape

This is not executed by this planning task:

```bash
nohup .venv/bin/python scripts/build_dualscope_jbb_small_slice_response_generation.py \
  --source-jsonl data/jbb/small_slice/jbb_small_slice_source.jsonl \
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

## Prompt Contract

Use the source `behavior_text` field as the user request. Preserve category and source IDs as metadata only. Do not add jailbreak wrappers, trigger text, target strings, or target descriptors as instructions.

The system prompt must instruct the model to refuse unsafe actionable assistance and provide only safe, high-level alternatives where appropriate. Reports should use IDs, hashes, behavior categories, and aggregate statuses rather than printing harmful prompts or model completions.

## Expected Successor Artifacts

- `jbb_small_slice_responses.jsonl`
- `jbb_small_slice_response_generation_summary.json`
- `jbb_small_slice_response_generation_blockers.json`
- `jbb_small_slice_response_generation_report.md`
- `jbb_small_slice_response_generation_verdict.json`
- tracked registry `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation.json`

## Metric Readiness

The response-generation task should not compute AUROC, F1, ASR, clean utility, or with-logprobs metrics. It should record row IDs, response availability, fallback flags, query counts, latency if measured, prompt hashes, and safety proxy fields so the later metric task can determine which metrics are actually available.

Final planning verdict: `JBB small-slice response generation plan validated`.
