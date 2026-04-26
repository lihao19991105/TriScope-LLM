# DualScope SCI3 Main Experiment Expansion Plan Repair Prompt

## Goal

Add the missing repair prompt for `dualscope-sci3-main-experiment-expansion-plan-repair` so the partially validated SCI3 expansion plan can be repaired without executing a full matrix or fabricating results.

## Scope

- Repair planning artifacts only.
- Preserve first-slice limitations: 8 real Qwen2.5-7B responses, first-slice detection/ASR only, clean utility blocked.
- Route validated repair to `dualscope-cross-model-validation-plan`.
- Do not change benchmark truth, gates, route_c, 199+, responses, logprobs, labels, or metrics.

## Validation

- Run task orchestrator dry-run.
- Confirm `dualscope-sci3-main-experiment-expansion-plan-repair` has `prompt_available=true`.
- Run `git diff --check`.

## Progress

- [x] Added direct queue entry and prompt.
- [ ] Validate prompt generation.
- [ ] Create PR and trigger Codex review.
