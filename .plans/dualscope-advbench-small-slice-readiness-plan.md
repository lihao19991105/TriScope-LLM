# DualScope AdvBench Small-Slice Readiness Plan

## Goal

Prepare a bounded AdvBench small-slice readiness step for the DualScope SCI3 track without downloading restricted resources, executing the full dataset, generating responses, or computing metrics.

## Scope

- Model: Qwen2.5-7B-Instruct remains the main experimental model.
- Dataset: AdvBench small-slice readiness only.
- Execution: planning and readiness checks only.
- Matrix expansion: no full dataset, full trigger matrix, target matrix, or model matrix.
- Evidence level: current Qwen2.5-7B Alpaca first-slice and bounded main-slice results remain smoke and bounded evidence, not full paper performance.

## Readiness Requirements

1. Identify a permitted AdvBench source and record license or access constraints.
2. Define a small-slice schema with stable row identifiers, instruction text, harmfulness category if available, trigger metadata, target metadata, and split metadata.
3. Define compatibility checks for lexical, semantic, and future behavior-shift target smoke settings.
4. Require explicit blockers for missing data, restricted access, unsafe labels, unavailable model responses, missing final risk scores, or missing utility references.
5. Keep clean utility blocked unless reference responses and utility rules are explicitly available.

## Expected Artifacts

- `.plans/dualscope-advbench-small-slice-readiness-plan.md`
- `docs/dualscope_advbench_small_slice_readiness_plan.md`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-readiness-plan.json`
- `outputs/dualscope_advbench_small_slice_readiness_plan/default/dualscope_advbench_small_slice_readiness_plan_verdict.json`

## Safety Constraints

- Do not fabricate AdvBench data availability, harmfulness labels, model responses, logprobs, ASR, utility, benchmark truth, or gate outcomes.
- Do not download gated or unauthorized data.
- Do not modify benchmark truth files or safe merge gate semantics.
- Do not continue route_c or generate 199+ plans.

## Verdict

AdvBench small-slice readiness plan validated.

## Next Task

`dualscope-jbb-small-slice-readiness-plan`
