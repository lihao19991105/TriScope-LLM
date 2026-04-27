# DualScope AdvBench Small-Slice Metric Computation Repair

## Purpose / Big Picture

The AdvBench small-slice metric-computation task is partially validated because it could compute artifact availability and fallback summaries, but the upstream response-generation artifacts contain zero real model responses. This repair/compression step turns that partial state into a routeable, auditable package without fabricating responses, labels, logprobs, or performance metrics.

This supports the DualScope-LLM mainline by preserving a truthful bounded AdvBench status for the SCI3 expansion track while keeping unsupported performance claims blocked.

## Scope

### In Scope

- Read AdvBench metric-computation artifacts, response-generation artifacts, and tracked registries.
- Audit whether real response rows, non-fabrication flags, blocker types, and available metric summaries are consistent.
- Compress unavailable metric blockers into a concise repair package.
- Route zero-real-response states to blocker closure rather than result packaging or repeated metric computation.
- Write repair summary, availability matrix, blocker compression, source audit, limitations, report, verdict, and tracked registry.

### Out of Scope

- No model response generation retry.
- No full matrix execution.
- No training.
- No benchmark truth, label, gate, route_c, or 199+ changes.
- No fabricated AUROC, F1, ASR, clean utility, logprobs, labels, model responses, or score-aligned detection metrics.
- No PR #14 modification.

## Repository Context

- Source metric artifacts: `outputs/dualscope_advbench_small_slice_metric_computation/default/`
- Source response artifacts: `outputs/dualscope_advbench_small_slice_response_generation/default/`
- Source metric registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation.json`
- Source response-generation repair registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation-repair.json`
- Repair output directory: `outputs/dualscope_advbench_small_slice_metric_computation_repair/default/`
- Repair registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation-repair.json`

This task does not use the historical TriScope / route_c chain except as excluded reliability background.

## Deliverables

- `.plans/dualscope-advbench-small-slice-metric-computation-repair.md`
- `src/eval/dualscope_advbench_small_slice_metric_computation_repair.py`
- `scripts/build_dualscope_advbench_small_slice_metric_computation_repair.py`
- `docs/dualscope_advbench_small_slice_metric_computation_repair.md`
- `outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_summary.json`
- `outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_metric_availability_matrix.json`
- `outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_blocked_metric_compression.json`
- `outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_source_audit.json`
- `outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_limitations.json`
- `outputs/dualscope_advbench_small_slice_metric_computation_repair/default/advbench_small_slice_metric_computation_repair_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation-repair.json`

## Progress

- [x] Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, DUALSCOPE_TASK_QUEUE.md, and adjacent AdvBench artifacts.
- [x] Create this repair ExecPlan.
- [x] Implement repair builder and CLI.
- [x] Add direct queue entry for the configured metric-computation repair step.
- [x] Generate source metric artifacts in this worktree when absent.
- [x] Generate repair artifacts and tracked registry.
- [x] Run py_compile and CLI validation.

## Surprises & Discoveries

- The metric-computation registry existed, but the ignored `outputs/dualscope_advbench_small_slice_metric_computation/default/` directory was absent in this isolated worktree and had to be regenerated from the existing response rows.
- The response rows contain 16 bounded AdvBench rows, all blocked by `cuda_unavailable_cpu_generation_disabled`.
- The response-generation repair registry already validates the upstream blocker and routes to `dualscope-advbench-small-slice-response-generation-blocker-closure`.

## Decision Log

- Treat the repair as validated when the metric artifacts are internally consistent, non-fabricated, and explicitly block unsupported metrics.
- Route zero-real-response metric repair to the upstream response-generation blocker closure because the metric gap is caused by CUDA-blocked generation, not by a metric implementation defect.
- Do not route to result packaging until real responses or an explicit blocker-closure package makes that packaging step meaningful.

## Plan of Work

1. Regenerate the metric-computation artifacts from existing response rows if the ignored output directory is missing.
2. Build a deterministic repair/compression package from metric artifacts, response rows, and tracked registries.
3. Add a direct queue entry so the orchestrator can recognize the configured repair next step.
4. Validate with py_compile, CLI `--help`, metric CLI, repair CLI, and orchestrator dry-run parsing.

## Validation

- `python3 -m py_compile src/eval/dualscope_advbench_small_slice_metric_computation.py scripts/build_dualscope_advbench_small_slice_metric_computation.py src/eval/dualscope_advbench_small_slice_metric_computation_repair.py scripts/build_dualscope_advbench_small_slice_metric_computation_repair.py`
- `python3 scripts/build_dualscope_advbench_small_slice_metric_computation.py --seed 20260427`
- `python3 scripts/build_dualscope_advbench_small_slice_metric_computation_repair.py --seed 20260427`
- `python3 scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt --dry-run`

## Known Risks

- The repair does not make AdvBench performance metrics reportable; it only closes the partial metric-computation state into explicit blockers.
- A future GPU-visible external runner is still required before refusal, target behavior, ASR, or detection metrics can become real AdvBench evidence.
