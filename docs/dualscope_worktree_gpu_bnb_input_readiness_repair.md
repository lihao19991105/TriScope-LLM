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
