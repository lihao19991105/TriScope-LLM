# DualScope Qwen2.5-7B Response Generation Repair

This repair task exists only to unblock the Qwen2.5-7B first-slice response-generation stage after a partial verdict.

## Scope

- Dataset: Stanford Alpaca first-slice only.
- Trigger: `lexical_trigger_v1`, `cftrigger`.
- Target: fixed response `I have completed the requested instruction.`
- Model: local Qwen2.5-7B binding at `models/qwen2p5-7b-instruct`, resolving to `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Execution: small bounded repair run, `batch_size=1`, low-memory loading, optional 4-bit loading.

## Required Environment

```bash
export HF_HOME=/mnt/sda3/lh/huggingface
export TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers
export HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub
export TMPDIR=/mnt/sda3/lh/tmp
export CUDA_VISIBLE_DEVICES=2,3
```

## Commands

Dry-run:

```bash
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_response_generation_repair.py --dry-run
```

Bounded repair:

```bash
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_response_generation_repair.py \
  --model-dir models/qwen2p5-7b-instruct \
  --max-examples 4 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --min-free-gpu-memory-mib 18432 \
  --load-in-4bit \
  --allow-without-logprobs
```

Post-analysis:

```bash
.venv/bin/python scripts/build_post_dualscope_qwen2p5_7b_response_generation_repair_analysis.py
```

## Outputs

- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_summary.json`
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_responses.jsonl`
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_blockers.json`
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/qwen2p5_7b_generation_summary.json`
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/qwen2p5_7b_generation_capability_mode.json`
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/qwen2p5_7b_generation_fallback_flags.json`
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/qwen2p5_7b_blocker.json`
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/qwen2p5_7b_response_rows.jsonl`
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_report.md`
- `outputs/dualscope_qwen2p5_7b_response_generation_repair_analysis/default/dualscope_qwen2p5_7b_response_generation_repair_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-response-generation-repair.json`

## Verdicts

- `Qwen2.5-7B first-slice response generation repaired`
- `Partially validated`
- `Not validated`

The task may only advance to `dualscope-qwen2p5-7b-label-aligned-metric-computation` when real response artifacts exist. It must not fabricate responses, logprobs, ASR, utility, AUROC, F1, or any full-paper performance metric.

If the labeled pairs, target-response plan rows, resource-materialization verdict, or repo-local model binding are missing, the repair records a `missing_input` blocker and routes to `dualscope-qwen2p5-7b-response-input-artifact-repair` rather than attempting model generation.
