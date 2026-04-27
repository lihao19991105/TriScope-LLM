# DualScope AdvBench Small-Slice Result Package

## Purpose / Big Picture

This plan packages the real bounded AdvBench small-slice status from existing materialization, response-generation, and metric-computation artifacts. It exists to make the current AdvBench state auditable without implying that blocked response rows support refusal, target success, ASR, detection, clean utility, logprob, or full-paper performance claims.

This supports the DualScope-LLM mainline by preserving the AdvBench small-slice evidence boundary for budget-aware evaluation while keeping unsupported behavior metrics explicitly blocked.

## Scope

### In Scope

- Read the AdvBench materialization registry, response-generation artifacts, and metric-computation artifacts.
- Package materialization status, selected-row status, response-generation blocker status, metric availability, and limitations.
- Report refusal/safety proxy or target success only if the metric artifacts support them.
- Record the without-logprobs limitation and zero-real-response blocker.
- Write summary, report, metric availability matrix, verdict, docs, and tracked registry.

### Out of Scope

- No full matrix execution.
- No training.
- No response-generation retry.
- No benchmark truth, gate, route_c, or 199+ changes.
- No fabricated responses, labels, logprobs, detection metrics, ASR, clean utility, refusal metrics, target success, or full-paper performance.
- No PR #14 modification.

## Repository Context

- Materialization registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-materialization.json`
- Response artifacts: `outputs/dualscope_advbench_small_slice_response_generation/default/`
- Metric artifacts: `outputs/dualscope_advbench_small_slice_metric_computation/default/`
- Metric registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation.json`
- Result package output directory: `outputs/dualscope_advbench_small_slice_result_package/default/`
- Tracked result package registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json`

This task does not use the historical TriScope / route_c chain except as excluded reliability background. It is a DualScope AdvBench small-slice packaging step.

## Deliverables

- `.plans/dualscope-advbench-small-slice-result-package.md`
- `src/eval/dualscope_advbench_small_slice_result_package.py`
- `scripts/build_dualscope_advbench_small_slice_result_package.py`
- `docs/dualscope_advbench_small_slice_result_package.md`
- `outputs/dualscope_advbench_small_slice_result_package/default/result_package_summary.json`
- `outputs/dualscope_advbench_small_slice_result_package/default/result_package_report.md`
- `outputs/dualscope_advbench_small_slice_result_package/default/metric_availability_matrix.json`
- `outputs/dualscope_advbench_small_slice_result_package/default/result_package_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json`

## Progress

- [x] Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md.
- [x] Inspect AdvBench response-generation, metric-computation, and materialization registries.
- [x] Regenerate missing ignored metric artifacts from existing bounded response rows only.
- [x] Create this ExecPlan.
- [x] Implement reproducible result-package builder and CLI.
- [x] Generate result-package artifacts and tracked registry.
- [x] Validate py_compile and package contents.

## Surprises & Discoveries

- The tracked metric-computation registry existed, but the ignored metric output directory was absent in this isolated worktree and had to be regenerated from existing response rows.
- AdvBench materialization is validated with 32 rows from `walledai/AdvBench`.
- Response generation selected 16 rows but produced zero real model responses because CUDA was unavailable and CPU generation was disabled.
- All behavior and performance metrics remain unsupported; only materialization, response availability, blocker status, and fallback summaries are reportable.

## Decision Log

- Mark the result package as `Partially validated` because the package is reproducible and honest, but it contains zero real model responses and zero reportable behavior/performance metrics.
- Recommend `dualscope-advbench-small-slice-response-generation-blocker-closure` rather than JBB expansion because the current AdvBench blocker should be closed or rerun in a GPU-visible environment before performance reporting.
- Preserve without-logprobs as a limitation, not as token-level confidence evidence.

## Plan of Work

1. Recreate the metric-computation output directory from existing response rows if it is absent.
2. Build a deterministic package from materialization, response-generation, and metric-computation artifacts.
3. Emit summary, metric availability matrix, report, verdict, docs, and tracked registry.
4. Validate that no unsupported metric is presented as real performance.

## Validation

- `python3 -m py_compile src/eval/dualscope_advbench_small_slice_result_package.py scripts/build_dualscope_advbench_small_slice_result_package.py`
- `python3 scripts/build_dualscope_advbench_small_slice_metric_computation.py --seed 20260427`
- `python3 scripts/build_dualscope_advbench_small_slice_result_package.py --seed 20260427`
- Inspect generated JSON and Markdown artifacts for non-fabrication flags and blocked metric status.

## Known Risks

- The package is not an AdvBench performance result. It is a bounded status package documenting validated materialization and blocked generation/metrics.
- Future GPU-visible generation is required before refusal, safety proxy, target success, ASR, detection, clean utility, or with-logprobs metrics can be reported.
