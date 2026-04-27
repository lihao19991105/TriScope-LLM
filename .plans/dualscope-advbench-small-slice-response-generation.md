# DualScope AdvBench Small-Slice Response Generation

## Purpose / Big Picture

This plan executes the validated AdvBench small-slice response-generation handoff for DualScope-LLM. It attempts a bounded, safety-aware Qwen2.5-7B-Instruct run over the already materialized AdvBench small slice, or records a truthful blocker if the worktree cannot access the required runtime.

This task supports the DualScope SCI3 expansion track by creating real response artifacts or explicit blocker artifacts for a harmful-instruction-only dataset slice. It does not compute detection metrics, alter benchmark truth, train, expand the matrix, continue route_c, or create 199+ planning.

## Scope

### In Scope

- Read `data/advbench/small_slice/advbench_small_slice_source.jsonl`.
- Select at most the first 16 rows by deterministic file order.
- Use Qwen2.5-7B-Instruct from `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Use `batch_size=1`, `max_new_tokens=64`, deterministic decoding, and CUDA devices 2,3 when available to the runner.
- Use a refusal-preserving safety prompt template for harmful instructions.
- Record `without_logprobs_fallback=true` because this runner does not produce token logprobs.
- Write response, summary, blocker, report, verdict, and tracked registry artifacts.
- If CUDA/model/dependency/runtime access is unavailable, write blocker artifacts and do not mark the task validated.

### Out of Scope

- Full AdvBench execution or any full experiment matrix.
- Training, LoRA/QLoRA, full finetuning, or model modification.
- AUROC/F1/ASR/clean utility computation.
- Fabricating model responses, logprobs, labels, metrics, benchmark truth, gates, PR results, or review status.
- Publishing verbatim harmful prompts or completions in Markdown reports.
- Force push, branch deletion, auto merge, PR #14 changes, route_c continuation, or 199+ planning.

## Repository Context

- The predecessor plan verdict is `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-plan.json`.
- The source file is `data/advbench/small_slice/advbench_small_slice_source.jsonl` with 32 rows.
- The implementation is in `src/eval/dualscope_advbench_small_slice_response_generation.py`.
- The CLI entrypoint is `scripts/build_dualscope_advbench_small_slice_response_generation.py`.
- Outputs are written under `outputs/dualscope_advbench_small_slice_response_generation/default`.
- Historical TriScope / route_c artifacts are not used except as general reliability background.

## Deliverables

- `.plans/dualscope-advbench-small-slice-response-generation.md`
- `docs/dualscope_advbench_small_slice_response_generation.md`
- `scripts/build_dualscope_advbench_small_slice_response_generation.py`
- `src/eval/dualscope_advbench_small_slice_response_generation.py`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json`
- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl`
- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_summary.json`
- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_blockers.json`
- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_report.md`
- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_response_generation_verdict.json`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, predecessor plan, and source JSONL contract.
- [x] M2: Implement a bounded AdvBench response-generation CLI and core builder with safety-aware prompt construction and blocker output.
- [x] M3: Execute the CLI in the current worktree and write real response or blocker artifacts.
- [x] M4: Validate artifact schema and compile the new Python files.
- [ ] M5: Complete PR workflow if GitHub authentication and repository policy allow it.

## Surprises & Discoveries

- The model directory and HF cache roots exist under `/mnt/sda3/lh`.
- This Codex worktree runtime cannot communicate with the NVIDIA driver, so Qwen2.5-7B generation is blocked here.
- The repository has no `.venv` in this worktree, but system `python3` has `torch` and `transformers`; `accelerate` and `bitsandbytes` are absent.

## Decision Log

- The runner writes both the task-queue filenames (`advbench_small_slice_response_generation_*`) and predecessor-plan aliases (`advbench_small_slice_generation_*`) for compatibility.
- Blocked rows still include the required response-row fields with empty `model_response`, `model_output_fabricated=false`, and explicit blocker status.
- Markdown reports omit verbatim harmful source instructions and model completions. Raw JSONL keeps source instruction fields for audit continuity.
- The final verdict is not `validated` unless real model responses are generated for the selected slice without blockers.

## Plan of Work

Run:

```bash
HF_HOME=/mnt/sda3/lh/huggingface \
HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub \
TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers \
TMPDIR=/mnt/sda3/lh/tmp \
CUDA_DEVICE_ORDER=PCI_BUS_ID \
CUDA_VISIBLE_DEVICES=2,3 \
python3 scripts/build_dualscope_advbench_small_slice_response_generation.py \
  --source-jsonl data/advbench/small_slice/advbench_small_slice_source.jsonl \
  --model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct \
  --output-dir outputs/dualscope_advbench_small_slice_response_generation/default \
  --max-examples 16 \
  --batch-size 1 \
  --max-new-tokens 64 \
  --seed 20260427 \
  --device-map auto \
  --safety-mode refusal_preserving_eval \
  --allow-without-logprobs
```

If the runner is executed in a GPU-visible shell, it may produce real responses. If the runner is executed in a CUDA-invisible sandbox, it must emit a `torch_cuda_unavailable` blocker and keep `validated=false`.
