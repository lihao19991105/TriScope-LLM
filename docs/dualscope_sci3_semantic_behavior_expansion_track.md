# DualScope SCI3 Semantic / Behavior Expansion Track

This track extends the current bounded Qwen2.5-7B Alpaca evidence without jumping to a full matrix. It starts with semantic trigger and behavior-shift target smokes, then moves to bounded AdvBench/JBB materialization readiness and an expanded status synthesis package.

## Current Evidence Boundary

- Qwen2.5-7B is the main SCI3 model.
- The bounded Alpaca main-slice has 16 real response rows.
- Detection and ASR metrics exist for the bounded slice.
- `without_logprobs_fallback=true`.
- Clean utility remains blocked.
- These results are bounded smoke evidence, not full paper performance.

## New Task Chain

1. `dualscope-qwen2p5-7b-semantic-trigger-smoke-response-generation`
2. `dualscope-qwen2p5-7b-semantic-trigger-smoke-metric-computation`
3. `dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package`
4. `dualscope-qwen2p5-7b-behavior-shift-target-smoke-response-generation`
5. `dualscope-qwen2p5-7b-behavior-shift-target-smoke-metric-computation`
6. `dualscope-qwen2p5-7b-behavior-shift-target-smoke-result-package`
7. `dualscope-advbench-small-slice-materialization`
8. `dualscope-advbench-small-slice-response-generation-plan`
9. `dualscope-jbb-small-slice-materialization`
10. `dualscope-jbb-small-slice-response-generation-plan`
11. `dualscope-sci3-expanded-result-synthesis-package`

## Execution Gate Policy

Response generation tasks must write a non-empty response JSONL or a blocker JSON with an explicit blocker type. Metric tasks must write available metrics, readiness matrix, blockers, report, and verdict artifacts. Dataset materialization tasks must write a manifest/schema check or a real data blocker. Result packages must write summary, report, availability matrix, and verdict artifacts.

## Non-Goals

This track does not run full Alpaca, full AdvBench, full JBB, a trigger matrix, a target matrix, or cross-model validation. It does not train models or infer clean utility from free-text similarity.

## Honesty Constraints

Do not fabricate responses, logprobs, AUROC, F1, ASR, clean utility, dataset availability, benchmark truth, gate outcomes, or cross-model availability. Do not continue route_c or generate 199+ plans.
