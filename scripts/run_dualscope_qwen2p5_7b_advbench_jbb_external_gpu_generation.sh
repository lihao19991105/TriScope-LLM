#!/usr/bin/env bash
set -Eeuo pipefail

cd /home/lh/TriScope-LLM

MODEL_DIR="/mnt/sda3/lh/models/qwen2p5-7b-instruct"
TARGET="both"
MAX_EXAMPLES=16
BATCH_SIZE=1
MAX_NEW_TOKENS=64
SEED=2025
MIN_FREE_GPU_MEMORY_MIB=18432

usage() {
  cat <<'USAGE'
Usage: bash scripts/run_dualscope_qwen2p5_7b_advbench_jbb_external_gpu_generation.sh [options]

Options:
  --target {both|advbench|jbb}        Dataset target to run. Default: both
  --max-examples N                    Bounded examples per dataset. Default: 16
  --batch-size N                      Must be 1 for this runner. Default: 1
  --max-new-tokens N                  Max generated tokens, capped at 64. Default: 64
  --model-dir PATH                    Absolute model directory. Default: /mnt/sda3/lh/models/qwen2p5-7b-instruct
  --seed N                            Generation seed. Default: 2025
  --min-free-gpu-memory-mib N         Minimum selected GPU free memory. Default: 18432
  -h, --help                          Show this help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET="${2:?--target requires a value}"
      shift 2
      ;;
    --max-examples)
      MAX_EXAMPLES="${2:?--max-examples requires a value}"
      shift 2
      ;;
    --batch-size)
      BATCH_SIZE="${2:?--batch-size requires a value}"
      shift 2
      ;;
    --max-new-tokens)
      MAX_NEW_TOKENS="${2:?--max-new-tokens requires a value}"
      shift 2
      ;;
    --model-dir)
      MODEL_DIR="${2:?--model-dir requires a value}"
      shift 2
      ;;
    --seed)
      SEED="${2:?--seed requires a value}"
      shift 2
      ;;
    --min-free-gpu-memory-mib)
      MIN_FREE_GPU_MEMORY_MIB="${2:?--min-free-gpu-memory-mib requires a value}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "${TARGET}" in
  both|advbench|jbb)
    ;;
  *)
    echo "--target must be one of: both, advbench, jbb" >&2
    exit 2
    ;;
esac

if [[ "${MODEL_DIR}" != /* ]]; then
  echo "--model-dir must be an absolute path; got: ${MODEL_DIR}" >&2
  exit 2
fi

export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:18080}"
export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:18080}"
export ALL_PROXY="${ALL_PROXY:-http://127.0.0.1:18080}"
export HF_HOME="${HF_HOME:-/mnt/sda3/lh/huggingface}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-/mnt/sda3/lh/huggingface/transformers}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-/mnt/sda3/lh/huggingface/hub}"
export TMPDIR="${TMPDIR:-/mnt/sda3/lh/tmp}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1}"
export CUDA_DEVICE_ORDER="${CUDA_DEVICE_ORDER:-PCI_BUS_ID}"

mkdir -p models logs
ln -sfnT "${MODEL_DIR}" models/qwen2p5-7b-instruct

if [[ ! -d "${MODEL_DIR}" ]]; then
  echo "BLOCKER: missing_model_dir: ${MODEL_DIR}" >&2
fi

echo "DualScope AdvBench/JBB external GPU generation"
echo "Target: ${TARGET}"
echo "Model dir: ${MODEL_DIR}"
echo "Repo model binding: $(readlink -f models/qwen2p5-7b-instruct || true)"
echo "CUDA_VISIBLE_DEVICES: ${CUDA_VISIBLE_DEVICES}"

run_step() {
  echo "### STEP: $*"
  set +e
  "$@"
  local status=$?
  set -e
  echo "### STEP_EXIT: ${status}: $*"
  return "${status}"
}

run_jbb_materialization() {
  run_step .venv/bin/python scripts/build_dualscope_jbb_small_slice_materialization.py \
    --allow-download \
    --max-examples "${MAX_EXAMPLES}"
}

run_generation() {
  local dataset_id="$1"
  local input_jsonl="$2"
  local output_dir="$3"

  run_step .venv/bin/python scripts/build_dualscope_qwen2p5_7b_benchmark_small_slice_external_gpu_generation.py \
    --dataset-id "${dataset_id}" \
    --input-jsonl "${input_jsonl}" \
    --model-dir "${MODEL_DIR}" \
    --output-dir "${output_dir}" \
    --seed "${SEED}" \
    --max-examples "${MAX_EXAMPLES}" \
    --batch-size "${BATCH_SIZE}" \
    --max-new-tokens "${MAX_NEW_TOKENS}" \
    --min-free-gpu-memory-mib "${MIN_FREE_GPU_MEMORY_MIB}" \
    --allow-without-logprobs
}

overall_status=0

if [[ "${TARGET}" == "both" || "${TARGET}" == "jbb" ]]; then
  run_jbb_materialization || overall_status=1
fi

if [[ "${TARGET}" == "both" || "${TARGET}" == "advbench" ]]; then
  run_generation \
    advbench \
    data/advbench/small_slice/advbench_small_slice_source.jsonl \
    outputs/dualscope_advbench_small_slice_response_generation/default || overall_status=1
fi

if [[ "${TARGET}" == "both" || "${TARGET}" == "jbb" ]]; then
  run_generation \
    jbb \
    data/jbb/small_slice/jbb_small_slice_source.jsonl \
    outputs/dualscope_jbb_small_slice_response_generation/default || overall_status=1
fi

echo "AdvBench responses: outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl"
echo "JBB responses: outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_responses.jsonl"
echo "AdvBench blockers: outputs/dualscope_advbench_small_slice_external_gpu_generation/default/advbench_external_gpu_generation_blockers.json"
echo "JBB blockers: outputs/dualscope_jbb_small_slice_external_gpu_generation/default/jbb_external_gpu_generation_blockers.json"

exit "${overall_status}"
