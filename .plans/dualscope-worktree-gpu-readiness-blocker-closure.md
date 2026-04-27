# DualScope Worktree GPU Readiness Blocker Closure

## Purpose / Big Picture

Close the current DualScope worktree GPU readiness blocker without pretending that Qwen2.5-7B response generation, CUDA execution, logprobs, or metrics succeeded.

This task is a blocker-closure task. It preserves the real failure chain from the isolated worktree runtime readiness repair so the queue can stop at `queue_complete` until a future user explicitly authorizes another resource repair.

## Scope

### In Scope

- Read the prior worktree GPU/BnB/input readiness repair registry and report.
- Summarize the actual `.venv`, CUDA, `nvidia-smi`, bitsandbytes, input materialization, model binding, and cache/tmp blocker chain.
- Write closure documentation and a tracked verdict registry.
- State the manual actions required before any future bounded response-generation retry.

### Out of Scope

- No model response generation.
- No logprob extraction.
- No metric computation.
- No benchmark truth or gate edits.
- No route_c continuation and no 199+ planning.
- No changes under `/mnt/sda3/CoCoNut-Artifact`.

## Repository Context

Relevant existing inputs:

- `.reports/dualscope_task_verdicts/dualscope-worktree-gpu-bnb-input-readiness-repair.json`
- `.plans/dualscope-worktree-gpu-bnb-input-readiness-repair.md`
- `docs/dualscope_worktree_gpu_bnb_input_readiness_repair.md`
- `DUALSCOPE_TASK_QUEUE.md`

The prior repair registry records `verdict: Partially validated`, `gpu_blocker: true`, `quantization_fallback: true`, `response_retry_allowed: false`, and `blocker_type: torch_cuda_unavailable`.

The expected prior output directory `outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default` is not present in this checkout, so this closure relies on the tracked registry and docs plus direct non-invasive filesystem checks.

## Deliverables

- `.plans/dualscope-worktree-gpu-readiness-blocker-closure.md`
- `docs/dualscope_worktree_gpu_readiness_blocker_closure.md`
- `.reports/dualscope_task_verdicts/dualscope-worktree-gpu-readiness-blocker-closure.json`
- `outputs/dualscope_worktree_gpu_readiness_blocker_closure/default/verdict.json`

## Progress

- [x] M1: Read AGENTS, PLANS, DUALSCOPE_MASTER_PLAN, DUALSCOPE_TASK_QUEUE, and prior readiness artifacts.
- [x] M2: Confirm closure evidence from the prior registry and docs.
- [x] M3: Record direct current-worktree observations without attempting response generation.
- [x] M4: Write blocker-closure docs and verdict artifacts.

## Blocker Chain

The real blocker chain is:

1. The bounded Qwen2.5-7B Alpaca main-slice retry produced zero response rows because CUDA was unavailable.
2. The worktree GPU/BnB/input readiness repair remained `Partially validated`.
3. `.venv/bin/python` previously imported torch, but the readiness repair recorded `torch.cuda.is_available() == False` and `torch.cuda.device_count() == 0`.
4. `nvidia-smi` previously returned code `9` and could not communicate with the NVIDIA driver.
5. bitsandbytes installation failed through the proxy, so `quantization_fallback=true`; this is secondary because CUDA itself is unavailable.
6. The Alpaca main-slice plan output directory was absent during repair.
7. `HF_HOME`, `HF_HUB_CACHE`, and `TRANSFORMERS_CACHE` were recorded as not writable from the runtime.
8. In the current checkout, `.venv` and the prior repair output directory are absent, so the runtime cannot be revalidated here.

## Manual Action Required

Before any future resource repair or response-generation retry, a human operator must restore a real GPU-enabled runtime for this isolated worktree:

- Recreate or relink `.venv` with CUDA-capable PyTorch.
- Restore NVIDIA driver visibility so `nvidia-smi` succeeds and torch reports available CUDA devices under `CUDA_VISIBLE_DEVICES=2,3`.
- Make `/mnt/sda3/lh/huggingface`, `/mnt/sda3/lh/huggingface/hub`, `/mnt/sda3/lh/huggingface/transformers`, and `/mnt/sda3/lh/tmp` writable to the runtime user.
- Restore required input artifacts in the worktree, including labeled pairs, first-slice source JSONL, target-response plan output, and Alpaca main-slice plan output.
- Restore `models/qwen2p5-7b-instruct` as a repo-local binding to `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Optionally install bitsandbytes if package-index access is available; otherwise use a documented non-4bit fallback only after CUDA and inputs are ready.

## Validation

This closure validates blocker documentation only. It does not validate GPU readiness or any experimental result.

Final verdict: `Worktree GPU readiness blocker closed`.

Next task: `queue_complete` unless a future user explicitly authorizes another resource repair.

