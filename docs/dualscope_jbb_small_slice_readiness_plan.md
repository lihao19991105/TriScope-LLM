# DualScope JBB Small-Slice Readiness Plan

This document defines a planning-only readiness step for a future JBB-Behaviors small-slice experiment. It does not execute JBB, download gated data, generate model responses, compute metrics, or claim cross-model results.

## Fixed Boundary

| Axis | Decision |
| --- | --- |
| Main model | `Qwen2.5-7B-Instruct` |
| Dataset | JBB-Behaviors small-slice readiness only |
| Cross-model axis | Readiness-only unless resources and license are explicit |
| Execution | No response generation in this task |
| Evidence level | Bounded SCI3 planning, not full benchmark performance |

## Data And License Readiness

The next executable task must identify the exact JBB-Behaviors source, access requirements, license restrictions, redistribution terms, and local path. If any source is gated, unauthorized, or ambiguous, the task must emit a blocker and stop rather than fabricate rows.

## Small-Slice Schema

The planned JSONL schema should include:

- `sample_id`
- `source_dataset`
- `behavior_category`
- `behavior_text` or prompt text
- `trigger_family`
- `trigger_text`
- `target_family`
- `target_descriptor`
- `split`
- `license_status`
- `safety_notes`
- `readiness_notes`

## Execution Prerequisites

Before any Qwen2.5-7B JBB smoke execution, the pipeline must verify:

- authorized source availability;
- stable behavior categories;
- target compatibility without changing benchmark truth;
- bounded sample count;
- external GPU runner availability if real 7B generation is required;
- explicit blocker outputs for unavailable responses, labels, scores, ASR, or utility.

## Cross-Model Boundary

Llama-3.1-8B-Instruct and Mistral-7B-Instruct-v0.3 remain planned cross-model validation candidates only. This task does not claim that either model is available, licensed, loaded, or evaluated.

## Honesty Controls

This task does not fabricate model availability, responses, logprobs, AUROC, F1, ASR, clean utility, benchmark truth, safe merge gate status, route_c evidence, or 199+ continuation. Clean utility remains blocked until explicit utility references and scoring rules exist.

## Verdict

`JBB small-slice readiness plan validated`

## Next Task

`queue_complete`
