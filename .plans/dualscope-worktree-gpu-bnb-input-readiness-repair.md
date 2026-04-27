# DualScope Worktree GPU/BnB/Input Readiness Repair

## Purpose

Reopen the bounded Qwen2.5-7B Alpaca main-slice execution path after the prior blocker closure by checking the actual isolated worktree runtime: `.venv`, CUDA visibility, bitsandbytes or quantization fallback, ignored input materialization, model symlink, HuggingFace cache, and temp directory wiring.

## Scope

In scope:

- Verify `.venv/bin/python`, torch, CUDA, `nvidia-smi`, transformers, accelerate, and bitsandbytes.
- Verify labeled pairs, source JSONL, target-response plan output, Alpaca main-slice plan output, and model binding in the worktree.
- Write readiness artifacts and a tracked verdict registry.
- Route to bounded response generation retry only when runtime and inputs are sufficiently ready, with non-4bit fallback allowed if bitsandbytes remains unavailable.

Out of scope:

- No full Alpaca run.
- No full matrix, training, LoRA, QLoRA, route_c, or 199+.
- No fabricated responses, logprobs, labels, metrics, CUDA readiness, or model paths.

## Validation

- `python3 -m py_compile src/eval/dualscope_worktree_runtime_readiness.py`
- `python3 -m py_compile scripts/check_dualscope_worktree_runtime_readiness.py`
- `python3 -m py_compile scripts/build_dualscope_worktree_gpu_bnb_input_readiness_repair.py`
- `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py`
- Task orchestrator selects `dualscope-worktree-gpu-bnb-input-readiness-repair` from the current closure state.

## Progress

- [x] M1: Read AGENTS, PLANS, master plan, task queue, and previous Alpaca main-slice blocker closure.
- [x] M2: Verify `.venv`, `.venv/bin/python`, torch, CUDA visibility, `nvidia-smi`, transformers, accelerate, bitsandbytes, input files, plan outputs, model binding, and cache/tmp paths.
- [x] M3: Run the readiness CLI with `CUDA_VISIBLE_DEVICES=2,3`, `CUDA_DEVICE_ORDER=PCI_BUS_ID`, `/mnt/sda3/lh` HuggingFace cache paths, `TMPDIR=/mnt/sda3/lh/tmp`, and `--attempt-pip-install`.
- [x] M4: Write runtime readiness artifacts and tracked verdict registry.

## Current Result

Final verdict: `Partially validated`.

The worktree is not ready for bounded response generation. PyTorch imports from `.venv/bin/python`, but `torch.cuda.is_available()` is `False`, `torch.cuda.device_count()` is `0`, and `nvidia-smi` returns code `9` because it cannot communicate with the NVIDIA driver. The bitsandbytes install attempt failed through the proxy, so `quantization_fallback=true`; however this is not the only blocker. The Alpaca main-slice plan output directory is absent, and `HF_HOME`, `HF_HUB_CACHE`, and `TRANSFORMERS_CACHE` are not writable from this runtime.

Next task: `dualscope-worktree-gpu-readiness-blocker-closure`.
