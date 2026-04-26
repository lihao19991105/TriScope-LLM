# DualScope Qwen2.5-7B Alpaca Main-Slice Response Dependency Repair

## Purpose / Big Picture

This task repairs the bounded Qwen2.5-7B Stanford Alpaca main-slice response-generation dependency blocker. The previous execution reached the response-generation repair path but recorded `missing_dependency` with detailed blocker `requested_4bit_but_bitsandbytes_unavailable`.

The task matters because the DualScope SCI3 main-slice path needs at least one real bounded Qwen2.5-7B response before metric computation can proceed. If local execution remains blocked, the blocker must be explicit, reproducible, and routed to closure without fabricated responses, logprobs, labels, metrics, reviews, or CI.

## Scope

### In Scope

- Diagnose the active `.venv/bin/python` runtime, or create the local `.venv` needed by this task if it is absent.
- Check `torch.cuda.is_available()`, `torch.cuda.device_count()`, `torch.version.cuda`, `CUDA_VISIBLE_DEVICES=2,3`, `accelerate`, `bitsandbytes`, model path binding, and GPU memory visibility.
- Install only `bitsandbytes>=0.43,<0.47` into `.venv` if it is missing.
- Rerun the bounded response-generation repair CLI with the requested cache and CUDA environment.
- If generation succeeds, preserve real response rows and route to metric computation.
- If generation remains blocked, write explicit dependency-repair blocker artifacts under `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_dependency_repair/default`.

### Out of Scope

- No benchmark truth, label, or gate modifications.
- No final metric computation.
- No full matrix, training, new model axis, route_c continuation, or 199+ planning.
- No fake responses, logprobs, labels, metrics, reviews, or CI.
- No unrelated package installation.

## Repository Context

- Queue entry: `DUALSCOPE_TASK_QUEUE.md`
- Previous registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json`
- Plan verdict input: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json`
- Response repair CLI: `scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair.py`
- Core generation builder: `src/eval/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation.py`
- Input pairs: `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`
- Local model: `/mnt/sda3/lh/models/qwen2p5-7b-instruct`
- Dependency requirement: `requirements.txt`

## Milestones

- [x] M1: Read project instructions, master plan, task queue, previous registry, and previous dependency-repair documentation.
- [x] M2: Diagnose `.venv`, Python, CUDA visibility, GPU memory, required package imports, and local model binding.
- [x] M3: If needed, install only `bitsandbytes>=0.43,<0.47` into `.venv` and record the result.
- [x] M4: Rerun the bounded response-generation repair CLI with requested environment variables.
- [x] M5: Write dependency-repair report, verdict, registry, and blocker or success evidence.

## Execution Commands

Primary bounded rerun:

```bash
HF_HOME=/mnt/sda3/lh/huggingface \
TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers \
HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub \
TMPDIR=/mnt/sda3/lh/tmp \
CUDA_VISIBLE_DEVICES=2,3 \
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair.py \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --input-jsonl data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --plan-verdict .reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-plan.json \
  --output-dir outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default \
  --registry-path .reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json \
  --max-source-examples 4 \
  --expected-response-rows 8 \
  --batch-size 1 \
  --max-new-tokens 32 \
  --max-generation-attempts 8 \
  --load-in-4bit \
  --allow-without-logprobs
```

## Validation Criteria

Validated only if `.venv` dependency repair succeeds and the bounded repair CLI writes at least one real model response row. Qualified failure is acceptable only as `Partially validated` or `Not validated` with an explicit blocker JSON using a blocker type such as `missing_dependency`, `torch_cuda_unavailable`, `cuda_error`, `oom`, `model_load_failure`, or `runtime_error`.

## Progress Log

- 2026-04-27: Read AGENTS, PLANS, master plan, task queue, response repair registry, existing dependency-repair doc, requirements, and response repair CLI. Previous registry reports `Partially validated`, `blocker_type=missing_dependency`, and next task `dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair`.
- 2026-04-27: Initial diagnostics found `.venv/bin/python` absent in this isolated worktree. System `python3` is 3.8.10 with `torch=1.13.1+cu117`, `transformers` available, `accelerate` absent, `bitsandbytes` absent, `torch.cuda.is_available()=False`, `torch.cuda.device_count()=0`, `torch.version.cuda=11.7`, and `nvidia-smi` unable to communicate with the NVIDIA driver. Local Qwen2.5-7B model files are present under `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- 2026-04-27: Created `.venv` with available system Python and system site packages; bootstrapped pip from local `/usr/share/python-wheels` because `ensurepip` is unavailable. This exposed `torch` and `transformers` inside `.venv` without installing unrelated dependencies.
- 2026-04-27: Attempted `.venv/bin/python -m pip install "bitsandbytes>=0.43,<0.47"`. The install failed because the configured proxy could not be reached from the sandbox (`ProxyError`, `Operation not permitted`). `requirements.txt` already includes `bitsandbytes>=0.43,<0.47`.
- 2026-04-27: Reran the bounded response-generation repair CLI with the required cache/TMPDIR/CUDA environment. The CLI completed with `Partially validated`, zero real response rows, and generation-repair artifacts under `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation_repair/default`.
- 2026-04-27: Wrote dependency-repair diagnostics, blocker, verdict, report, and tracked registry. Primary blocker is `missing_dependency`; secondary blockers are `torch_cuda_unavailable` and `missing_input`. The non-4bit retry was not attempted because CUDA is unavailable, GPU memory cannot be verified, and the required labeled-pairs input JSONL is absent in this isolated worktree.

## Known Risks

- The local CUDA driver is not visible to `nvidia-smi` or PyTorch, so real 7B generation may remain blocked even after `bitsandbytes` is installed.
- The worktree initially lacks `.venv`; creating it with available system Python may yield Python 3.8 rather than the preferred Python 3.10+ environment.
- Network access may prevent installing `bitsandbytes` from the package index.
