# DualScope External GPU Runner for Qwen2.5-7B

The external GPU runner is used when `codex exec` isolated worktrees cannot see
CUDA but the host shell can.  It runs bounded Qwen2.5-7B Alpaca main-slice
generation from the normal shell environment and writes artifacts that Codex can
inspect afterward.

## Environment

```bash
export HF_HOME=/mnt/sda3/lh/huggingface
export TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers
export HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub
export TMPDIR=/mnt/sda3/lh/tmp
export CUDA_VISIBLE_DEVICES=2,3
export CUDA_DEVICE_ORDER=PCI_BUS_ID
```

## Run

```bash
scripts/run_dualscope_qwen2p5_7b_external_gpu_generation.sh
```

The shell wrapper starts:

```bash
nohup .venv/bin/python scripts/build_dualscope_qwen2p5_7b_external_gpu_generation.py \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --target-response-plan-dir outputs/dualscope_first_slice_target_response_generation_plan/default \
  --output-dir outputs/dualscope_qwen2p5_7b_external_gpu_generation/default \
  --max-examples 8 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --device-map auto \
  --allow-without-logprobs
```

## Monitor

```bash
ps -ef | grep build_dualscope_qwen2p5_7b_external_gpu_generation | grep -v grep
tail -f logs/dualscope_external_gpu_generation_*.log
```

## Outputs

- `outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_summary.json`
- `outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_responses.jsonl`
- `outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_blockers.json`
- `outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_report.md`
- `outputs/dualscope_qwen2p5_7b_external_gpu_generation/default/external_gpu_generation_verdict.json`

If response generation succeeds, the runner also synchronizes canonical
Alpaca main-slice response artifacts under:

- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default/`

## Safety

The runner does not compute metrics, does not train, does not run a full matrix,
and does not fabricate responses or logprobs.  If model loading, CUDA, OOM, or
runtime errors occur, it writes explicit blocker artifacts.
