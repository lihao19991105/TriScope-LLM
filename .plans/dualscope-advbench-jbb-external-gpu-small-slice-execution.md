# DualScope AdvBench / JBB External GPU Small-Slice Execution

## Purpose / Big Picture

This plan advances the SCI3 expansion track from materialization/readiness into bounded AdvBench and JBB response generation, metric computation, result packaging, and expanded synthesis. It keeps the work within the DualScope black-box, two-stage, budget-aware mainline and records either real model responses or explicit blocker artifacts.

## Scope

### In Scope

- Materialize a bounded JBB-Behaviors harmful small slice from the public `JailbreakBench/JBB-Behaviors` source or record a real blocker.
- Run bounded Qwen2.5-7B external GPU response generation for AdvBench and JBB with `max_examples <= 16`, `batch_size=1`, and `max_new_tokens=64`.
- Compute transparent benchmark response metrics from real generated rows only.
- Package AdvBench/JBB bounded results and update SCI3 expanded synthesis artifacts.
- Preserve without-logprobs fallback and clean-utility blockers when appropriate.

### Out of Scope

- Full benchmark execution or full matrix expansion.
- Training, LoRA, QLoRA, or full finetune.
- Benchmark truth edits, safe merge gate edits, route_c continuation, or 199+ planning.
- Fabricated responses, logprobs, metrics, utility, labels, or CI/review evidence.

## Repository Context

- AdvBench small-slice materialization already exists under `data/advbench/small_slice/` and `outputs/dualscope_advbench_small_slice_materialization/default`.
- JBB readiness was planning-only; this plan adds a bounded executable materialization step.
- Existing Qwen2.5-7B generation helpers in `src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py` provide the reusable local HuggingFace generation path and blocker handling.
- Codex sandbox CUDA may remain unavailable; external shell runner artifacts must honestly record that blocker rather than falling back to fabricated rows.

## Deliverables

- `src/eval/dualscope_benchmark_small_slice_external_gpu.py`
- `scripts/build_dualscope_jbb_small_slice_materialization.py`
- `scripts/build_dualscope_qwen2p5_7b_benchmark_small_slice_external_gpu_generation.py`
- `scripts/build_dualscope_benchmark_small_slice_metrics.py`
- `scripts/build_dualscope_benchmark_small_slice_result_package.py`
- `scripts/build_dualscope_sci3_expanded_result_synthesis.py`
- `scripts/run_dualscope_qwen2p5_7b_advbench_jbb_external_gpu_generation.sh`
- Local artifacts under `outputs/dualscope_*` and tracked verdict registries under `.reports/dualscope_task_verdicts/`.

## Progress

- [x] Create execution plan.
- [x] Add bounded JBB materialization, AdvBench/JBB generation, metrics, package, and synthesis CLIs.
- [x] Run external GPU generation for AdvBench.
- [x] Run external GPU generation for JBB.
- [x] Compute metric blockers and result packages because no real AdvBench/JBB responses were generated.
- [x] Build expanded SCI3 synthesis package.
- [ ] Run validation and PR workflow.

## Surprises & Discoveries

- 2026-04-27: `nvidia-smi` is visible from Codex, but `torch.cuda.is_available()` inside the Codex process remains false with an NVML initialization warning. The runner must therefore emit real CUDA blocker artifacts unless the external shell process sees CUDA.
- 2026-04-27: The `nohup` shell wrapper cannot outlive the Codex sandbox parent process here, so the same bounded runner was executed in the foreground to produce auditable blocker artifacts. AdvBench and JBB each selected 16 rows and generated 0 real responses because CUDA was unavailable in the runner process.

## Decision Log

- Use public JBB Hugging Face CSV as the source of record and preserve source columns in the normalized small slice.
- Compute only metrics supported by generated response rows: ASR/target-match, refusal-like rate, response length, generated/blocked row counts, and query count. ROC/F1-style detection metrics remain blocked for benchmark-only harmful slices because clean/negative detection labels are not present.
- Keep `CUDA_VISIBLE_DEVICES=0,1` as the shell runner default per current user-provided PyTorch mapping, while recording both `nvidia-smi` and torch CUDA snapshots.

## Plan of Work

1. Add CLIs and shared implementation.
2. Materialize JBB small slice with `max_examples=16`.
3. Launch bounded external GPU generation for AdvBench and JBB.
4. If response rows are generated, compute metrics and result packages.
5. Build expanded synthesis from available Alpaca/semantic/behavior/AdvBench/JBB packages or blockers.
6. Validate with compile/help commands, diff checks, and safe PR workflow.
