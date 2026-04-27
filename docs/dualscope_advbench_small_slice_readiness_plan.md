# DualScope AdvBench Small-Slice Readiness Plan

This planning document adds the next bounded SCI3 readiness step after the Qwen2.5-7B Alpaca main-slice package and behavior-shift target smoke plan. It does not download AdvBench, run a full dataset, generate responses, compute ASR, or compute utility.

## Fixed Boundary

| Axis | Decision |
| --- | --- |
| Model | `Qwen2.5-7B-Instruct` as the main SCI3 model |
| Dataset | AdvBench small-slice readiness only |
| Trigger scope | Compatibility checks for one bounded smoke at a time |
| Target scope | Fixed response and future behavior-shift compatibility checks |
| Execution | No model generation in this planning task |

## Source And License Readiness

The follow-up implementation must identify the exact AdvBench source, license, redistribution terms, and local storage path before creating any data slice. If access is unavailable, restricted, or ambiguous, the implementation must emit a blocker rather than fabricate rows.

## Small-Slice Schema

The planned small slice should use a compact JSONL schema:

- `sample_id`
- `source_dataset`
- `instruction`
- `harmfulness_category` when available from the source
- `trigger_family`
- `trigger_text`
- `target_family`
- `target_text` or target-behavior descriptor
- `split`
- `license_status`
- `readiness_notes`

## Compatibility Checks

The next executable readiness task should check:

- whether rows can be sampled without changing benchmark truth;
- whether trigger and target metadata can be attached without overwriting labels;
- whether Qwen2.5-7B response generation can be bounded to a tiny smoke slice;
- whether ASR can be computed only from real responses and explicit target rules;
- whether clean utility remains blocked unless reference responses and utility criteria exist.

## Blocker Routing

Use explicit blockers for:

- missing or restricted AdvBench source;
- unclear license or redistribution status;
- missing harmfulness metadata;
- unsafe or ambiguous target mapping;
- unavailable model response generation;
- missing score or label alignment;
- unavailable utility references.

## Honesty Controls

This task preserves the current clean utility blocker and does not claim full paper performance. It does not fabricate AdvBench data, ASR, utility, logprobs, responses, benchmark truth, gate status, route_c evidence, or 199+ continuation.

## Verdict

`AdvBench small-slice readiness plan validated`

## Next Task

`dualscope-jbb-small-slice-readiness-plan`
