#!/usr/bin/env bash
set -Eeuo pipefail

cd "${DUALSCOPE_WORKTREE:-/tmp/dualscope-worktrees/jbb-small-slice-response-generation-20260427101904}"

export HF_HOME="${HF_HOME:-/mnt/sda3/lh/huggingface}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/mnt/sda3/lh/huggingface/transformers}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-/mnt/sda3/lh/huggingface/hub}"
export TMPDIR="${TMPDIR:-/mnt/sda3/lh/tmp}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-2,3}"
export CUDA_DEVICE_ORDER="${CUDA_DEVICE_ORDER:-PCI_BUS_ID}"

mkdir -p outputs/dualscope_jbb_small_slice_response_generation/default
log_path="outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_response_generation_$(date +%Y%m%d_%H%M%S).log"

python_bin="${PYTHON_BIN:-python3}"
if [[ -x ".venv/bin/python" ]]; then
  python_bin="${PYTHON_BIN:-.venv/bin/python}"
fi

nohup "${python_bin}" scripts/build_dualscope_jbb_small_slice_response_generation.py \
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
  --allow-without-logprobs \
  > "${log_path}" 2>&1 &

echo "Started JBB small-slice response generation. PID: $!"
echo "Log: ${log_path}"
