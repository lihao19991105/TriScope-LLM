# DualScope Qwen2.5-7B Resource Materialization

This module audits and optionally materializes `Qwen/Qwen2.5-7B-Instruct` for the SCI3 main-model track.

It does not run response generation, training, full-matrix experiments, or metric computation. It only establishes whether the Qwen2.5-7B resource, first-slice labeled pairs, and target-response plan outputs are ready.

## Command

```bash
export HF_HOME=/mnt/sda3/lh/huggingface
export TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers
export HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub
export TMPDIR=/mnt/sda3/lh/tmp

.venv/bin/python scripts/build_dualscope_qwen2p5_7b_resource_materialization.py \
  --model-id Qwen/Qwen2.5-7B-Instruct \
  --local-model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --output-dir outputs/dualscope_qwen2p5_7b_resource_materialization/default \
  --allow-download \
  --check-tokenizer \
  --check-config \
  --check-gpu \
  --check-disk
```

## Outputs

- `dualscope_qwen2p5_7b_resource_scope.json`
- `dualscope_qwen2p5_7b_model_source_check.json`
- `dualscope_qwen2p5_7b_download_plan.json`
- `dualscope_qwen2p5_7b_download_result.json`
- `dualscope_qwen2p5_7b_local_path_manifest.json`
- `dualscope_qwen2p5_7b_tokenizer_check.json`
- `dualscope_qwen2p5_7b_config_check.json`
- `dualscope_qwen2p5_7b_model_load_readiness.json`
- `dualscope_qwen2p5_7b_gpu_readiness.json`
- `dualscope_qwen2p5_7b_disk_readiness.json`
- `dualscope_qwen2p5_7b_data_dependency_check.json`
- `dualscope_qwen2p5_7b_target_response_plan_check.json`
- `dualscope_qwen2p5_7b_cross_model_candidate_check.json`
- `dualscope_qwen2p5_7b_resource_materialization_verdict.json`

## Safety Boundaries

- Do not mark the model ready unless a real local model path or Hugging Face snapshot exists.
- An existing but empty local model directory is not enough; it must contain config, tokenizer, and weight files.
- Use `/mnt/sda3/lh` for large model/cache/tmp storage in this environment; do not download Qwen2.5-7B into `/home/lh`.
- Do not fake tokenizer/config checks.
- Do not download gated Llama/Mistral models in this stage.
- Do not run full model response generation or training.
- Do not change benchmark truth or gates.
- Do not claim AUROC, F1, ASR, clean utility, or latency.
