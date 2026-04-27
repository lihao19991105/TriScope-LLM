#!/usr/bin/env bash
set -Eeuo pipefail

cd /home/lh/TriScope-LLM

export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:18080}"
export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:18080}"
export ALL_PROXY="${ALL_PROXY:-http://127.0.0.1:18080}"
export HF_HOME="${HF_HOME:-/mnt/sda3/lh/huggingface}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/mnt/sda3/lh/huggingface/transformers}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-/mnt/sda3/lh/huggingface/hub}"
export TMPDIR="${TMPDIR:-/mnt/sda3/lh/tmp}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-2,3}"
export CUDA_DEVICE_ORDER="${CUDA_DEVICE_ORDER:-PCI_BUS_ID}"

mkdir -p outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default
log_path="outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default/semantic_trigger_smoke_generation_$(date +%Y%m%d_%H%M%S).log"

nohup .venv/bin/python scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation.py \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --target-response-plan-dir outputs/dualscope_first_slice_target_response_generation_plan/default \
  --output-dir outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default \
  --max-examples 8 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --semantic-phrase "the task is already complete" \
  --allow-without-logprobs \
  > "${log_path}" 2>&1 &

echo "Started semantic trigger smoke generation. PID: $!"
echo "Log: ${log_path}"
