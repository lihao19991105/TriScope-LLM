# DualScope Qwen2.5-7B Alpaca Main-Slice Response Generation

This task executes the bounded Alpaca main-slice response-generation step after the validated plan. It is not a metric-computation task and does not claim paper-scale performance.

Current verdict: `Partially validated`.

## Scope

- Model: `Qwen2.5-7B-Instruct`
- Dataset: Stanford Alpaca bounded main slice selected from the available labeled clean/poisoned rows
- Source examples: 32
- Response rows: 64
- Trigger: `lexical_trigger_v1` / `cftrigger`
- Target: `fixed_response_v1` / `I have completed the requested instruction.`
- Capability mode: `without_logprobs`

## Command

```bash
HF_HOME=/mnt/sda3/lh/huggingface \
TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers \
HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub \
TMPDIR=/mnt/sda3/lh/tmp \
CUDA_VISIBLE_DEVICES=2,3 \
python3 scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py \
  --model-dir models/qwen2p5-7b-instruct \
  --input-jsonl data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --output-dir outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default \
  --max-source-examples 32 \
  --expected-response-rows 64 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --max-generation-attempts 72 \
  --load-in-4bit \
  --allow-without-logprobs \
  --seed 2025
```

## Artifacts

- `qwen2p5_7b_alpaca_main_slice_response_rows.jsonl`
- `generation_summary.json`
- `capability_mode.json`
- `fallback_flags.json`
- `budget_trace.json`
- `blockers.json`
- `verdict.json`
- `dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_report.md`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation.json`

## Current Outcome

The input and artifact contract validated far enough to select 32 source examples and 64 clean/poisoned response rows. No model responses were generated in this environment. The first attempt with `--load-in-4bit` was blocked by missing `bitsandbytes`; the retry without 4-bit was blocked because CUDA was unavailable and `nvidia-smi` could not communicate with the NVIDIA driver. The response JSONL therefore contains blocked rows, not fabricated responses.

## Guardrails

No training, full matrix, route_c continuation, benchmark truth edits, gate edits, fabricated responses, fabricated logprobs, or final detection metrics are in scope.
