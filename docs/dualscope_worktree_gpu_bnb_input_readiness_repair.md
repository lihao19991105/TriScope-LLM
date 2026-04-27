# DualScope Worktree GPU/BnB/Input Readiness Repair

This repair stage exists because the previous bounded Alpaca main-slice response generation closed with a truthful blocker, not a completed experiment. The next run must verify the isolated worktree runtime before retrying Qwen2.5-7B generation.

The readiness task checks:

- `.venv` availability inside the worktree.
- torch import and CUDA visibility under `CUDA_VISIBLE_DEVICES=2,3` and `CUDA_DEVICE_ORDER=PCI_BUS_ID`.
- `nvidia-smi` availability.
- `transformers`, `accelerate`, `bitsandbytes`, and `safetensors`.
- labeled pairs and first-slice source materialization.
- target-response plan and Alpaca main-slice plan outputs.
- `models/qwen2p5-7b-instruct` binding to `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- `HF_HOME`, `HF_HUB_CACHE`, `TRANSFORMERS_CACHE`, and `TMPDIR` under `/mnt/sda3/lh`.

If bitsandbytes cannot be installed because the proxy refuses pip, the task records that fact and allows a non-4bit low-memory retry only when CUDA, inputs, model binding, and cache paths are ready.

It does not generate model responses or metrics. Response generation is handled by `dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry`.

## Current Runtime Verdict

Final verdict: `Partially validated`.

The readiness CLI was run from the isolated worktree with:

```bash
CUDA_VISIBLE_DEVICES=2,3 \
CUDA_DEVICE_ORDER=PCI_BUS_ID \
HF_HOME=/mnt/sda3/lh/huggingface \
HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub \
TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers \
TMPDIR=/mnt/sda3/lh/tmp \
.venv/bin/python scripts/build_dualscope_worktree_gpu_bnb_input_readiness_repair.py --attempt-pip-install
```

Observed blockers:

- `torch_cuda_unavailable`: torch imports from `.venv/bin/python`, but `torch.cuda.is_available()` is `False` and `torch.cuda.device_count()` is `0`.
- `nvidia_smi_unavailable`: `nvidia-smi` returns code `9` and cannot communicate with the NVIDIA driver.
- `missing_alpaca_main_slice_plan_dir`: `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default` is absent in this worktree.
- `hf_home_not_writable`, `hf_hub_cache_not_writable`, and `transformers_cache_not_writable`: the cache directories exist but are not writable from the runtime.
- `bitsandbytes_unavailable_after_install_attempt`: pip install failed because the proxy refused package-index access; `quantization_fallback=true`.

Because CUDA is unavailable, response retry is not allowed in this task. The tracked next task is `dualscope-worktree-gpu-readiness-blocker-closure`.
