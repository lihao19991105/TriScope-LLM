# DualScope Qwen2.5-7B Alpaca Main-Slice Result Package

## Purpose / Big Picture

Package the bounded Qwen2.5-7B Alpaca main-slice artifacts after metric computation into an auditable result bundle. The package serves the DualScope-LLM mainline by separating real response counts, real computed metrics, without-logprobs fallback evidence, blocked clean utility, limitations, and next actions without expanding the experiment scope or overstating performance.

## Scope

### In Scope

- Read the bounded Alpaca main-slice response-generation artifacts.
- Read the regenerated metric-computation artifacts.
- Produce a documentation report under `docs/`.
- Produce machine-readable package artifacts under `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default`.
- Record the tracked registry under `.reports/dualscope_task_verdicts/`.
- Report only artifact-supported values.

### Out of Scope

- No model response generation.
- No metric recomputation beyond rerunning the existing metric-computation CLI to restore missing output artifacts.
- No full Alpaca coverage claim.
- No full trigger coverage claim.
- No cross-model validation claim.
- No clean utility success claim.
- No benchmark truth, gate, label, response, logprob, route_c, or 199+ changes.

## Repository Context

- Metric registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation.json`
- Metric artifacts: `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation/default`
- Response artifacts: `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default`
- Response repair registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair.json`
- Result package output: `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default`

Historical TriScope / route_c artifacts are not used for this package.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-alpaca-main-slice-result-package.md`
- `docs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package.md`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-result-package.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/summary.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/metric_availability_matrix.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/table_skeleton.md`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/limitations.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/blocker_summary.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/report.md`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/verdict.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/recommendation.json`
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_result_package/default/tracked_registry.json`

## Progress

- [x] M1: Read `AGENTS.md`, `PLANS.md`, `DUALSCOPE_MASTER_PLAN.md`, and the prior metric-computation plan.
- [x] M2: Confirm response-generation artifacts and metric-computation registry.
- [x] M3: Regenerate the missing metric-computation output directory from existing artifacts.
- [x] M4: Inspect real response counts, real computed metrics, fallback flags, clean utility blocker, and query cost.
- [x] M5: Produce result package artifacts, documentation, verdict, recommendation, and tracked registry.
- [x] M6: Validate package JSON/Markdown presence and guardrail fields.

## Surprises & Discoveries

- The metric-computation registry was present, but `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation/default` was initially absent in this worktree.
- Rerunning `scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation.py` restored the metric artifacts without generating model responses or changing benchmark truth/gates.
- The package is only partially validated: detection metrics and ASR are real and aligned, but clean utility and logprob metrics remain blocked.

## Decision Log

- The final result verdict is `Partially validated` because real response rows, aligned detection metrics, ASR, query cost, and without-logprobs fallback evidence are available, while clean utility and logprob metrics are blocked.
- The next task is `dualscope-qwen2p5-7b-semantic-trigger-smoke-plan`.
- The package does not claim full paper performance, full Alpaca coverage, full trigger coverage, cross-model validation, or clean utility success.

## Validation and Acceptance

Acceptance requires the output bundle to state exactly one allowed verdict:

- `Qwen2.5-7B Alpaca main-slice result package validated`
- `Partially validated`
- `Not validated`

Current verdict: `Partially validated`.

## Idempotence and Recovery

The package can be regenerated from the current response-generation and metric-computation artifacts. If future artifacts add explicit clean utility scoring or token logprobs, rerun metric computation and then refresh this package instead of editing metrics by hand.
