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
