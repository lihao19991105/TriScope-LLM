# DualScope AdvBench Small-Slice Metric Computation

## Purpose / Big Picture

This plan computes only the metrics supported by the bounded AdvBench small-slice response-generation artifacts. It exists to avoid promoting blocked generation rows, projected placeholders, or missing labels as real model performance.

The task supports the DualScope-LLM mainline by turning the AdvBench response-generation state into an honest metric/readiness package for the budget-aware evaluation chain.

## Scope

### In Scope

- Read the AdvBench response-generation verdict and bounded response JSONL.
- Compute response availability and blocker/fallback summaries.
- Compute refusal and safety proxy metrics only when real model responses exist.
- Record target behavior status only when target definitions or target match fields are present.
- Compute detection metrics only when labels and `final_risk_score` are aligned with real responses.
- Write metric summary, available metrics, blockers, readiness matrix, report, verdict, and tracked task registry.

### Out of Scope

- No full matrix execution.
- No training or model generation retry.
- No benchmark truth, label, gate, route_c, or 199+ changes.
- No fabricated AUROC, F1, ASR, clean utility, logprobs, labels, model responses, or score-aligned detection metrics.
- No PR #14 modification.

## Repository Context

- Input verdict: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json`
- Input response rows: `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl`
- Output directory: `outputs/dualscope_advbench_small_slice_metric_computation/default/`
- Tracked verdict registry: `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation.json`

This task does not use the historical TriScope / route_c chain except as a general reliability foundation reference. It is a DualScope AdvBench small-slice evaluation step.

## Deliverables

- `.plans/dualscope-advbench-small-slice-metric-computation.md`
- `src/eval/dualscope_advbench_small_slice_metric_computation.py`
- `scripts/build_dualscope_advbench_small_slice_metric_computation.py`
- `docs/dualscope_advbench_small_slice_metric_computation.md`
- `outputs/dualscope_advbench_small_slice_metric_computation/default/metric_summary.json`
- `outputs/dualscope_advbench_small_slice_metric_computation/default/available_metrics.json`
- `outputs/dualscope_advbench_small_slice_metric_computation/default/metric_blockers.json`
- `outputs/dualscope_advbench_small_slice_metric_computation/default/readiness_matrix.json`
- `outputs/dualscope_advbench_small_slice_metric_computation/default/metric_report.md`
- `outputs/dualscope_advbench_small_slice_metric_computation/default/metric_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-metric-computation.json`

## Progress

- [x] Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md.
- [x] Inspect AdvBench response-generation verdict and response JSONL.
- [x] Create this ExecPlan.
- [x] Implement reproducible metric builder and CLI.
- [x] Generate metric artifacts.
- [x] Validate outputs and update report/docs.

## Surprises & Discoveries

- The response JSONL exists and has 16 rows, but every row is a blocked no-generation record with `model_response_present: false`.
- The response-generation verdict records `generated_rows: 0`, `blocked_rows: 16`, and blocker type `torch_cuda_unavailable`.
- The repair verdict routes to blocker closure, not to real metric computation, because CUDA visibility blocked generation.
- Metric computation completed as `Partially validated`: availability and fallback summaries are real, while performance metrics remain unavailable.

## Decision Log

- Compute response availability and blocker/fallback summaries because they are directly supported by artifact fields.
- Mark refusal rate, safety behavior proxy, target behavior success, ASR, clean utility, logprob metrics, AUROC, F1, and label/score detection metrics unavailable unless required fields exist on real response rows.
- Use a small `src/eval` builder plus `scripts/` CLI to preserve the repository's script/core separation pattern.

## Plan of Work

1. Build a deterministic metric artifact generator that reads the expected verdict and response JSONL.
2. Emit availability, blockers, readiness, report, and verdict artifacts under `outputs/`.
3. Mirror the task verdict into `.reports/dualscope_task_verdicts/`.
4. Run `py_compile` and the metric CLI.
5. Review generated artifacts for unsupported metric leakage.

## Validation

- `python3 -m py_compile src/eval/dualscope_advbench_small_slice_metric_computation.py scripts/build_dualscope_advbench_small_slice_metric_computation.py`
- `python3 scripts/build_dualscope_advbench_small_slice_metric_computation.py --seed 20260427`
- Inspect generated JSON and Markdown artifacts to confirm no fabricated performance metrics are present.

## Known Risks

- Current metric readiness is expected to be partially validated or blocked for performance metrics because no real AdvBench model responses are available.
- If future rows include real responses, the lexical refusal/safety proxy remains a lightweight proxy, not a full safety classifier.
