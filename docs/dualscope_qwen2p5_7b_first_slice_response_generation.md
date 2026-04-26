# DualScope Qwen2.5-7B First-Slice Response Generation

This task runs, or honestly blocks, the minimal Qwen2.5-7B-Instruct response-generation pass for the Stanford Alpaca first-slice target-response plan.

## Command

```bash
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 python3 scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py \
  --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --target-response-plan-dir outputs/dualscope_first_slice_target_response_generation_plan/default \
  --model-path models/qwen2p5-7b-instruct \
  --output-dir outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default \
  --seed 2025 \
  --trigger-text cftrigger \
  --target-text "I have completed the requested instruction." \
  --batch-size 1 \
  --low-memory \
  --min-free-gpu-memory-mib 18432 \
  --no-full-matrix
```

## Artifact Contract

The output directory contains:

- `dualscope_qwen2p5_7b_first_slice_response_generation_rows.jsonl`
- `dualscope_qwen2p5_7b_first_slice_response_generation_capability_mode.json`
- `dualscope_qwen2p5_7b_first_slice_response_generation_mode.json`
- `dualscope_qwen2p5_7b_first_slice_response_generation_fallback_flags.json`
- `dualscope_qwen2p5_7b_first_slice_response_generation_blockers.json`
- `dualscope_qwen2p5_7b_first_slice_response_generation_summary.json`
- `dualscope_qwen2p5_7b_first_slice_response_generation_verdict.json`
- `dualscope_qwen2p5_7b_first_slice_response_generation_report.md`

The row file may include `target_matched` for later ASR computation, but this task does not compute or claim AUROC, F1, ASR, clean utility, latency, or paper-level performance metrics.

## Runtime Guard

Before loading Qwen2.5-7B weights, the generator now checks CUDA availability, resolves the selected visible CUDA device back to its physical `nvidia-smi` index, and requires enough free memory on that selected GPU. The default threshold is `18432` MiB for fp16 single-device loading and `8192` MiB when `--use-4bit` is requested.

CPU fallback is disabled by default for this 7B task. Use `--allow-cpu-generation` only for an explicit diagnostic run; it should not be treated as main-model response evidence unless the resulting artifacts contain real generated rows.

## Guardrails

- No training, full finetune, LoRA, or QLoRA training.
- No full matrix execution.
- No benchmark truth or gate modification.
- No fabricated model responses, logprobs, or metrics.
- No route_c continuation or 199+ planning.

## Current Run Status

The execution package currently reports `Partially validated`.

The required inputs and `models/qwen2p5-7b-instruct` binding were present in the prior materialized worktree, but the first real generation attempt hung after loading local checkpoint shards onto physical GPU 2 under `CUDA_VISIBLE_DEVICES=2,3`. No model responses were flushed. The artifact package therefore recorded a prepare-only fallback with 24 blocked rows, `model_response_fabricated=false`, `metrics_computed=false`, and `logprobs_available=false`.

The repair path keeps that partial verdict honest and prevents repeat hangs by blocking before model load when the selected GPU does not satisfy the configured memory threshold.
