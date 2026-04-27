# DualScope AdvBench/JBB External GPU Runner

This runner is the bounded response-generation entrypoint for AdvBench and JBB small slices. It is limited to Qwen2.5-7B-Instruct, `max_examples <= 16`, `batch_size=1`, and `max_new_tokens <= 64`.

## Model Directory Binding

The runner uses the external model directory explicitly:

```bash
/mnt/sda3/lh/models/qwen2p5-7b-instruct
```

Before generation starts, the shell runner creates the repo binding:

```bash
mkdir -p models
ln -sfnT /mnt/sda3/lh/models/qwen2p5-7b-instruct models/qwen2p5-7b-instruct
```

The Python generation CLI defaults to the same absolute path and rejects worktree-relative `--model-dir` values. If the absolute model directory is unavailable, generation artifacts must record `blocker_type = missing_model_dir`. Blocked rows are not counted as real responses.

## Bounded Run

```bash
bash scripts/run_dualscope_qwen2p5_7b_advbench_jbb_external_gpu_generation.sh \
  --target both \
  --max-examples 16 \
  --max-new-tokens 64 \
  --batch-size 1 \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct
```

To split the run:

```bash
bash scripts/run_dualscope_qwen2p5_7b_advbench_jbb_external_gpu_generation.sh \
  --target advbench \
  --max-examples 16 \
  --max-new-tokens 64 \
  --batch-size 1 \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct

bash scripts/run_dualscope_qwen2p5_7b_advbench_jbb_external_gpu_generation.sh \
  --target jbb \
  --max-examples 16 \
  --max-new-tokens 64 \
  --batch-size 1 \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct
```

## Outputs

- AdvBench responses: `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl`
- JBB responses: `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_responses.jsonl`
- AdvBench external runner blockers: `outputs/dualscope_advbench_small_slice_external_gpu_generation/default/advbench_external_gpu_generation_blockers.json`
- JBB external runner blockers: `outputs/dualscope_jbb_small_slice_external_gpu_generation/default/jbb_external_gpu_generation_blockers.json`

Metric computation may proceed only when `real_response_row_count > 0` for the corresponding dataset.
