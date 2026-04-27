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
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1}"
export CUDA_DEVICE_ORDER="${CUDA_DEVICE_ORDER:-PCI_BUS_ID}"

mkdir -p logs outputs/dualscope_advbench_small_slice_response_generation/default outputs/dualscope_jbb_small_slice_response_generation/default
log_path="logs/dualscope_advbench_jbb_external_gpu_generation_$(date +%Y%m%d_%H%M%S).log"

nohup bash -lc '
set -Eeuo pipefail
run_step() {
  echo "### STEP: $*"
  set +e
  "$@"
  status=$?
  set -e
  echo "### STEP_EXIT: ${status}: $*"
}

run_step .venv/bin/python scripts/build_dualscope_jbb_small_slice_materialization.py \
  --allow-download \
  --max-examples 16

run_step .venv/bin/python scripts/build_dualscope_qwen2p5_7b_benchmark_small_slice_external_gpu_generation.py \
  --dataset-id advbench \
  --input-jsonl data/advbench/small_slice/advbench_small_slice_source.jsonl \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --output-dir outputs/dualscope_advbench_small_slice_response_generation/default \
  --max-examples 16 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --allow-without-logprobs

run_step .venv/bin/python scripts/build_dualscope_qwen2p5_7b_benchmark_small_slice_external_gpu_generation.py \
  --dataset-id jbb \
  --input-jsonl data/jbb/small_slice/jbb_small_slice_source.jsonl \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --output-dir outputs/dualscope_jbb_small_slice_response_generation/default \
  --max-examples 16 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --allow-without-logprobs
' > "${log_path}" 2>&1 &

pid=$!
echo "Started DualScope AdvBench/JBB external GPU generation. PID: ${pid}"
echo "Log: ${log_path}"
echo "Progress: ps -ef | grep build_dualscope_qwen2p5_7b_benchmark_small_slice_external_gpu_generation | grep -v grep"
echo "Tail: tail -f ${log_path}"
