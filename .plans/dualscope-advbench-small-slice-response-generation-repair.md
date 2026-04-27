# DualScope AdvBench Small-Slice Response Generation Repair

## Purpose / Big Picture

This task repairs and compresses the partially validated AdvBench small-slice response-generation state. The previous execution attempted the bounded Qwen2.5-7B path and honestly recorded `torch_cuda_unavailable` in the isolated Codex worktree. This repair does not rerun full generation in the sandbox. It validates that the partial artifact set is explicit, non-fabricated, and routeable, then writes a dedicated repair verdict so the scheduler does not loop on an undefined next task.

This serves the DualScope-LLM SCI3 expansion track by preserving the AdvBench bounded small-slice evidence chain before any metric computation or blocker closure.

## Scope

### In Scope

- Read `outputs/dualscope_advbench_small_slice_response_generation/default`.
- Audit response rows for required fields, real response counts, blocked rows, fabricated response flags, and without-logprobs fallback.
- Compress the existing CUDA/runtime blocker into a dedicated repair artifact set.
- Write repair summary, availability matrix, blocker compression, compact row audit, report, verdict, and tracked registry.
- Add the missing queue entry for `dualscope-advbench-small-slice-response-generation-repair`.

### Out of Scope

- Real Qwen2.5-7B generation inside the CUDA-invisible sandbox.
- Full AdvBench execution or any full matrix expansion.
- Metric computation, AUROC/F1/ASR/clean utility, or logprob-derived confidence metrics.
- Fabricating model responses, logprobs, labels, benchmark truth, gates, PR status, or review status.
- Training, LoRA/QLoRA, full finetuning, route_c continuation, or 199+ planning.

## Repository Context

- Source response-generation task: `.plans/dualscope-advbench-small-slice-response-generation.md`
- Source response artifacts: `outputs/dualscope_advbench_small_slice_response_generation/default`
- Source registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json`
- Repair implementation: `src/eval/dualscope_advbench_small_slice_response_generation_repair.py`
- Repair CLI: `scripts/build_dualscope_advbench_small_slice_response_generation_repair.py`
- Repair output: `outputs/dualscope_advbench_small_slice_response_generation_repair/default`

Historical TriScope / route_c artifacts are not used except as background reliability foundation.

## Deliverables

- `.plans/dualscope-advbench-small-slice-response-generation-repair.md`
- `docs/dualscope_advbench_small_slice_response_generation_repair.md`
- `src/eval/dualscope_advbench_small_slice_response_generation_repair.py`
- `scripts/build_dualscope_advbench_small_slice_response_generation_repair.py`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_summary.json`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_availability_matrix.json`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_blocker_compression.json`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_row_audit.json`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_compact_rows.jsonl`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_report.md`
- `outputs/dualscope_advbench_small_slice_response_generation_repair/default/advbench_small_slice_response_generation_repair_verdict.json`

## Progress

- [x] M1: Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, source response-generation plan, and source partial artifacts.
- [x] M2: Identify that `dualscope-advbench-small-slice-response-generation-repair` had no direct queue entry.
- [x] M3: Add the repair/compression builder and CLI.
- [x] M4: Add the repair ExecPlan, docs, and queue entry.
- [x] M5: Execute the repair CLI and validate the artifact contract.

## Surprises & Discoveries

- The source response-generation task wrote a complete row-level blocker artifact set: 16 selected AdvBench rows, 0 real responses, 16 blocked rows, `model_response_fabricated=false`, `logprobs_fabricated=false`, and `metrics_computed=false`.
- The source blocker is `torch_cuda_unavailable`, caused by CUDA invisibility in the isolated worktree. This is not repairable by editing benchmark data or generation outputs.
- The queue referenced `dualscope-advbench-small-slice-response-generation-repair` as the partial-verdict next task, but did not define a direct task entry.

## Decision Log

- A validated repair means the blocker artifact set is explicit, non-fabricated, and scheduler-routeable. It does not mean AdvBench model responses exist.
- With zero real model responses, the repair routes to `dualscope-advbench-small-slice-response-generation-blocker-closure`, not metric computation.
- The compact row audit excludes harmful prompt/completion text and keeps only IDs, status, hashes, blocker fields, and fabrication flags.

## Plan of Work

Run:

```bash
python3 scripts/build_dualscope_advbench_small_slice_response_generation_repair.py \
  --response-dir outputs/dualscope_advbench_small_slice_response_generation/default \
  --output-dir outputs/dualscope_advbench_small_slice_response_generation_repair/default \
  --registry-path .reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json \
  --seed 20260427
```

Then validate:

```bash
python3 -m py_compile \
  src/eval/dualscope_advbench_small_slice_response_generation_repair.py \
  scripts/build_dualscope_advbench_small_slice_response_generation_repair.py
python3 scripts/build_dualscope_advbench_small_slice_response_generation_repair.py --help
```

## Validation and Acceptance

The repair is acceptable when:

- The source partial response-generation artifacts are read successfully.
- The repair writes a summary, availability matrix, blocker compression, row audit, compact rows, report, verdict, and tracked registry.
- The final verdict is one of `AdvBench small-slice response generation repair validated`, `Partially validated`, or `Not validated`.
- The repair preserves `model_response_fabricated=false`, `logprobs_fabricated=false`, `metrics_computed=false`, `benchmark_truth_changed=false`, `gate_changed=false`, `full_matrix_executed=false`, `training_executed=false`, `route_c_continued=false`, and `generated_199_plus=false`.

Current verdict: `AdvBench small-slice response generation repair validated`.

## Known Risks

- This repair does not make CUDA visible to the Codex sandbox.
- AdvBench metric computation remains blocked until real response rows exist.
- A future external GPU-visible runner or blocker closure task must decide whether to rerun generation outside the sandbox or archive the CUDA blocker as an execution limitation.
