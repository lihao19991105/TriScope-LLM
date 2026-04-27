# DualScope Worktree GPU Readiness Blocker Closure

This document closes the current worktree GPU readiness blocker. It does not claim that CUDA, Qwen2.5-7B generation, logprobs, or metrics succeeded.

## Evidence Reviewed

- `DUALSCOPE_TASK_QUEUE.md` routes `dualscope-worktree-gpu-readiness-blocker-closure` after unrepaired GPU readiness failure.
- `.reports/dualscope_task_verdicts/dualscope-worktree-gpu-bnb-input-readiness-repair.json` records:
  - `verdict`: `Partially validated`
  - `gpu_blocker`: `true`
  - `quantization_fallback`: `true`
  - `response_retry_allowed`: `false`
  - `blocker_type`: `torch_cuda_unavailable`
  - `model_response_fabricated`: `false`
  - `logprobs_fabricated`: `false`
  - `metrics_computed`: `false`
- `docs/dualscope_worktree_gpu_bnb_input_readiness_repair.md` records the detailed CUDA, `nvidia-smi`, bitsandbytes, input, and cache blockers.
- The expected prior repair output directory, `outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default`, is absent in this checkout.
- A direct current-worktree check found `.venv` absent. The `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, `/mnt/sda3/lh/huggingface`, and `/mnt/sda3/lh/tmp` paths exist, but worktree-local input and model-binding paths are missing.

## Real Blocker Chain

1. The bounded Qwen2.5-7B Alpaca main-slice retry generated zero real response rows.
2. The canonical blocker is `torch_cuda_unavailable`.
3. The prior readiness repair recorded torch import from `.venv/bin/python`, but CUDA was unavailable: `torch.cuda.is_available() == False` and `torch.cuda.device_count() == 0`.
4. `nvidia-smi` returned code `9` and could not communicate with the NVIDIA driver.
5. bitsandbytes was unavailable after a pip install attempt failed through the proxy. This allows only a future non-4bit fallback, and only after CUDA and inputs are fixed.
6. Input readiness was incomplete: the Alpaca main-slice plan output directory was absent during the repair. In the current checkout, labeled pairs, source JSONL, target-response plan output, Alpaca main-slice plan output, and repo-local model binding are also absent.
7. Cache readiness was incomplete: `HF_HOME`, `HF_HUB_CACHE`, and `TRANSFORMERS_CACHE` were recorded as not writable from the runtime.
8. The current checkout lacks the prior detailed runtime output directory, so this task closes the blocker from tracked registry/docs evidence rather than rerunning readiness.

## Manual Action Required

Before any future bounded Qwen2.5-7B retry, a human operator must:

- Recreate or relink `.venv` inside this isolated worktree with CUDA-capable PyTorch.
- Restore NVIDIA driver visibility so `nvidia-smi` succeeds.
- Confirm torch sees the intended GPUs under:

```bash
CUDA_VISIBLE_DEVICES=2,3 CUDA_DEVICE_ORDER=PCI_BUS_ID .venv/bin/python -c "import torch; print(torch.cuda.is_available(), torch.cuda.device_count())"
```

- Make `/mnt/sda3/lh/huggingface`, `/mnt/sda3/lh/huggingface/hub`, `/mnt/sda3/lh/huggingface/transformers`, and `/mnt/sda3/lh/tmp` writable to the runtime user.
- Restore worktree-local inputs and plan outputs required by the bounded retry.
- Restore `models/qwen2p5-7b-instruct` as the repo-local model binding to `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Install bitsandbytes only if package-index access is available; otherwise keep `quantization_fallback=true` and retry without 4-bit only after CUDA and inputs are ready.

## Closure Verdict

Verdict: `Worktree GPU readiness blocker closed`.

This means the blocker documentation is complete enough to stop the queue. It does not mean GPU readiness is validated.

No model responses, logprobs, labels, CUDA success, CI results, reviews, or metrics were fabricated or produced by this closure.

Next task: `queue_complete` unless a future user explicitly authorizes another resource repair.

