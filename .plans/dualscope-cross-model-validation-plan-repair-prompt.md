# DualScope Cross-Model Validation Plan Repair Prompt

## Goal

Add the missing direct prompt for `dualscope-cross-model-validation-plan-repair` so the cross-model validation plan can close honestly when Llama/Mistral resources are planned or external-resource-required.

## Scope

- Verify local resource availability only.
- Mark missing or gated models as planned / external-resource-required.
- Do not download gated models, fake availability, execute full matrix, train, or generate responses.
- Route validated repair to queue completion.

## Validation

- Run task orchestrator dry-run.
- Confirm `dualscope-cross-model-validation-plan-repair` has `prompt_available=true`.
- Run `git diff --check`.

## Progress

- [x] Added direct queue entry and prompt.
- [ ] Validate prompt generation.
- [ ] Create PR and trigger Codex review.
