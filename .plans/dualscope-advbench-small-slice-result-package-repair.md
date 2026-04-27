# DualScope AdvBench Small-Slice Result Package Repair

## Purpose / Big Picture

Repair the partially validated AdvBench small-slice result package into an auditable compression package without fabricating unavailable behavior or performance metrics.

The prior result package is partial because the bounded response-generation step selected 16 AdvBench rows but produced zero real model responses in the CUDA-invisible worktree. This repair preserves the validated materialization and metric-availability evidence, keeps all unsupported behavior metrics blocked, and routes the next step to response-generation blocker closure.

## Scope

### In Scope

- Read the prior AdvBench result-package artifacts and tracked registry.
- Read metric-computation repair artifacts and response-generation repair registry.
- Audit row counts, non-fabrication flags, blocker type, and metric availability boundaries.
- Produce result-package repair summary, evidence boundary, blocker compression, limitations, report, verdict, analysis mirror, and tracked registry.
- Add the missing direct queue entry for `dualscope-advbench-small-slice-result-package-repair`.

### Out of Scope

- No response-generation retry.
- No metric recomputation beyond regenerating missing ignored source artifacts for validation.
- No training, full matrix, benchmark truth changes, gate changes, route_c continuation, or 199+ generation.
- No fabricated responses, logprobs, AUROC/F1/ASR/clean utility/refusal/target-success metrics.
- No PR #14 modification.

## Repository Context

- Prior result package registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package.json`
- Prior result package artifacts: `outputs/dualscope_advbench_small_slice_result_package/default/`
- Metric repair source: `outputs/dualscope_advbench_small_slice_metric_computation_repair/default/`
- Response generation source: `outputs/dualscope_advbench_small_slice_response_generation/default/`
- Repair output: `outputs/dualscope_advbench_small_slice_result_package_repair/default/`
- Analysis mirror: `outputs/dualscope_advbench_small_slice_result_package_repair_analysis/default/`
- Repair registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package-repair.json`

Historical TriScope / route_c artifacts are not used for this repair except as excluded reliability background.

## Deliverables

- `.plans/dualscope-advbench-small-slice-result-package-repair.md`
- `src/eval/dualscope_advbench_small_slice_result_package_repair.py`
- `scripts/build_dualscope_advbench_small_slice_result_package_repair.py`
- `docs/dualscope_advbench_small_slice_result_package_repair.md`
- `DUALSCOPE_TASK_QUEUE.md`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-result-package-repair.json`
- `outputs/dualscope_advbench_small_slice_result_package_repair/default/`
- `outputs/dualscope_advbench_small_slice_result_package_repair_analysis/default/`

## Progress

- [x] M1: Read project instructions, master plan, queue, and adjacent AdvBench package/repair artifacts.
- [x] M2: Create this repair ExecPlan and define evidence boundaries.
- [x] M3: Implement repair builder, CLI, and direct queue entry.
- [x] M4: Regenerate ignored source artifacts as needed, generate repair artifacts, docs, analysis mirror, and registry.
- [x] M5: Validate with py_compile, CLI execution, and scheduler dry-run.

## Surprises & Discoveries

- The prior result-package registry was present, but ignored source output directories were absent in the isolated worktree and had to be regenerated from existing response rows and registries.
- The response rows remain 16 blocked rows, zero real model responses, with blocker type `torch_cuda_unavailable`.
- The metric-computation repair already validated the metric-boundary compression and routes to response-generation blocker closure.

## Decision Log

- Treat this repair as validated when it faithfully preserves the partial result-package evidence boundary and routes to blocker closure.
- Do not route to JBB materialization while AdvBench response-generation remains blocked and no behavior/performance metric is reportable.
- Keep without-logprobs as a limitation rather than confidence evidence.

## Plan of Work

1. Recreate source metric, metric-repair, and result-package outputs if missing from ignored `outputs/`.
2. Build a deterministic repair package from source package, metric repair, response rows, and tracked registries.
3. Add a direct queue entry so the configured partial-verdict next task has a prompt.
4. Validate generated artifacts and non-fabrication guardrails.

## Validation

- `python3 -m py_compile src/eval/dualscope_advbench_small_slice_result_package_repair.py scripts/build_dualscope_advbench_small_slice_result_package_repair.py`
- `python3 scripts/build_dualscope_advbench_small_slice_metric_computation.py --seed 20260427`
- `python3 scripts/build_dualscope_advbench_small_slice_metric_computation_repair.py --seed 20260427`
- `python3 scripts/build_dualscope_advbench_small_slice_result_package.py --seed 20260427`
- `python3 scripts/build_dualscope_advbench_small_slice_result_package_repair.py --seed 20260427`
- `python3 scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt --dry-run`

## Known Risks

- This repair validates the packaging/compression layer, not AdvBench model performance.
- Real GPU-visible response generation is still required before refusal, target behavior, ASR, detection, clean utility, or with-logprobs metrics can be reported.
