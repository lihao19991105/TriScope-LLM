# DualScope SCI3 Experiment Scope Control

DualScope SCI3 expansion must proceed by small, auditable increments.

## Small-Step Rule

Only one axis may expand in a single task unless the task is explicitly a planning document. Execution tasks must keep the remaining axes fixed.

Examples:

- Expanding from first-slice to Alpaca main-slice keeps model, trigger, target, and dataset family fixed.
- Planning a semantic trigger smoke introduces a trigger-family plan but does not execute a trigger matrix.
- Planning AdvBench or JBB readiness checks data and license readiness but does not run the full benchmark.

## Required Honesty Controls

- First-slice Qwen2.5-7B metrics remain first-slice metrics.
- Clean utility remains blocked until explicit success/reference-match evidence exists.
- Cross-model validation remains readiness unless model resources and license are confirmed.
- If a model, data source, GPU, logprob capability, or metric input is unavailable, write a blocker.

## Execution-Required Task Controls

Response generation, metric computation, and result package tasks must either:

- run the relevant CLI and produce required artifacts; or
- produce explicit blocker artifacts.

They must not pass with plan/docs/registry-only changes.

## Forbidden Scope Escalations

- Full matrix execution.
- Full finetune, LoRA, or QLoRA unless a later task explicitly authorizes it.
- Benchmark truth or gate changes.
- Legacy route_c or 199+ expansion.
- Fabricated responses, logprobs, metrics, labels, model paths, or model availability.
