# DualScope SCI3 Expanded Result Synthesis

The expanded synthesis package will consolidate bounded evidence from:

- Qwen2.5-7B Alpaca main-slice responses and metrics.
- Semantic trigger smoke responses and available metrics.
- Behavior-shift target smoke responses and available metrics.
- AdvBench small-slice materialization or explicit blockers.
- JBB-Behaviors small-slice materialization or explicit blockers.

## Reporting Rules

The synthesis must separate:

- real metrics;
- without-logprobs fallback evidence;
- unavailable logprob metrics;
- clean utility blockers;
- dataset materialization blockers;
- safety or license blockers;
- limitations and next actions.

## Forbidden Claims

The synthesis must not claim full matrix performance, full dataset coverage, cross-model validation, clean utility success, or with-logprobs results unless those exact artifacts exist.

## Required Outputs

- `expanded_result_synthesis_summary.json`
- `expanded_metric_availability_matrix.json`
- `expanded_result_synthesis_report.md`
- `expanded_result_synthesis_verdict.json`
- tracked verdict registry under `.reports/dualscope_task_verdicts/`
