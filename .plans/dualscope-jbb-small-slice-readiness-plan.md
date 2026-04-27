# DualScope JBB Small-Slice Readiness Plan

## Goal

Prepare a bounded JBB-Behaviors small-slice readiness step for the DualScope SCI3 track without executing the full benchmark, generating model responses, or computing metrics.

## Scope

- Model: Qwen2.5-7B-Instruct remains the main SCI3 model.
- Dataset: JBB-Behaviors small-slice readiness only.
- Cross-model validation: readiness-only unless Llama or Mistral resources and licenses are explicitly available.
- Execution: planning and readiness checks only.
- Matrix expansion: no full benchmark, trigger matrix, target matrix, or model matrix.

## Readiness Requirements

1. Identify the authorized JBB-Behaviors source, license, and local storage requirements.
2. Define a small-slice schema with stable row identifiers, behavior category, prompt or behavior text, trigger metadata, target metadata, safety notes, and split metadata.
3. Require a source audit before any row is used for Qwen2.5-7B response generation.
4. Require explicit blockers for gated access, missing authorization, missing categories, unsafe target mappings, missing model responses, missing labels, missing scores, or unavailable utility references.
5. Preserve clean utility as blocked until reference responses and utility rules exist.

## Expected Artifacts

- `.plans/dualscope-jbb-small-slice-readiness-plan.md`
- `docs/dualscope_jbb_small_slice_readiness_plan.md`
- `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-readiness-plan.json`
- `outputs/dualscope_jbb_small_slice_readiness_plan/default/dualscope_jbb_small_slice_readiness_plan_verdict.json`

## Safety Constraints

- Do not fabricate JBB data availability, behavior categories, labels, model responses, logprobs, ASR, utility, benchmark truth, or gate outcomes.
- Do not download gated or unauthorized resources.
- Do not modify benchmark truth files or safe merge gate semantics.
- Do not continue route_c or generate 199+ plans.

## Verdict

JBB small-slice readiness plan validated.

## Next Task

`queue_complete` for this expansion planning batch.
