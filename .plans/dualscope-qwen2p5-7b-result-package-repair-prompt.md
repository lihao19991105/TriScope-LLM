# DualScope Qwen2.5-7B Result Package Repair Prompt

## Goal

Add the missing direct queue prompt for `dualscope-qwen2p5-7b-result-package-repair` so a partially validated first-slice result package can be repaired without fabricating metrics or blocking on clean utility.

## Scope

- Preserve real Qwen2.5-7B first-slice detection metrics and ASR only when backed by PASS artifacts.
- Keep clean utility explicitly blocked unless explicit utility success/reference-match evidence exists.
- Route a limitations-aware repaired package to `dualscope-sci3-main-experiment-expansion-plan`.
- Do not change benchmark truth, gates, route_c, 199+, model responses, logprobs, labels, or metrics.

## Validation

- Run task orchestrator dry-run.
- Confirm `dualscope-qwen2p5-7b-result-package-repair` has `prompt_available=true`.
- Run `git diff --check`.

## Progress

- [x] Added direct queue entry and prompt.
- [ ] Validate prompt generation.
- [ ] Create PR and trigger Codex review.
