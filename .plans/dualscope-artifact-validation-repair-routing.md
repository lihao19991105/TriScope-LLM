# DualScope Artifact-Validation Repair Routing

## Purpose / Big Picture

This plan closes the task-orchestrator routing gap for `dualscope-first-slice-real-run-artifact-validation-repair`. The artifact-validation task is already partially validated in local outputs, so the orchestrator correctly selects the configured repair next step, but the queue previously lacked a direct task entry and could only emit a placeholder prompt.

The goal is to make the repair route actionable without executing the repair itself.

## Scope

### In Scope

- Add a complete queue entry for `dualscope-first-slice-real-run-artifact-validation-repair`.
- Ensure the generated next-task prompt is complete and contains expected inputs, expected outputs, validation requirements, and PR workflow constraints.
- Add prompt availability metadata to task selection artifacts.
- Run orchestrator dry-run validation only.

### Out of Scope

- Running autorun execute.
- Executing the artifact-validation repair task.
- Changing benchmark truth, gates, labels, model outputs, or performance metrics.
- Continuing old route_c work or generating 199+ tasks.

## Repository Context

- Queue source of truth: `DUALSCOPE_TASK_QUEUE.md`.
- Orchestrator implementation: `src/eval/dualscope_task_orchestrator_common.py`.
- CLI wrapper: `scripts/dualscope_task_orchestrator.py`.
- Generated prompt: `outputs/dualscope_task_orchestrator/default/dualscope_next_task_prompt.md`.
- Generated selection: `outputs/dualscope_task_orchestrator/default/dualscope_next_task_selection.json`.

## Deliverables

- Complete repair queue entry.
- `prompt_available` and `prompt_path` in selection JSON.
- Updated task orchestrator documentation.
- Dry-run evidence that the selected repair task has a direct prompt.

## Progress

- [x] Read repository instructions and current queue.
- [x] Identify routing gap for repair task.
- [x] Add direct queue entry and prompt metadata.
- [x] Run py_compile.
- [x] Run task orchestrator dry-run.
- [ ] Open PR and request Codex review.

## Surprises & Discoveries

- The orchestrator already supports repair routing generically; the missing queue entry was the direct blocker.
- Selection artifacts did not explicitly indicate prompt availability, so callers had to infer it from prompt text.

## Decision Log

- Use a queue-only prompt for the repair route rather than hard-coding task-specific prompt logic in Python.
- Add minimal selection metadata to make prompt readiness machine-checkable.

## Plan of Work

Add the queue entry, add prompt metadata in the common helper, update documentation, run only compile and dry-run checks, then create a PR through the standard workflow.

## Concrete Steps

1. Add `dualscope-first-slice-real-run-artifact-validation-repair` to the queue.
2. Add `prompt_available` and `prompt_path` to `dualscope_next_task_selection.json`.
3. Run `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py`.
4. Run the task orchestrator dry-run with `--select-next-task --write-next-prompt`.
5. Inspect selection and prompt artifacts.
6. Commit and open PR.

## Validation and Acceptance

Accepted only if:

- The selected task is `dualscope-first-slice-real-run-artifact-validation-repair`.
- `prompt_available` is true.
- The prompt is non-empty and is not the placeholder.
- The prompt includes instructions to read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and to follow PR workflow.
- No autorun execute or repair body execution is run.

## Idempotence and Recovery

The dry-run overwrites only generated files under `outputs/dualscope_task_orchestrator/default`. If validation fails, rerun after fixing the queue or prompt metadata.

## Outputs and Artifacts

- `outputs/dualscope_task_orchestrator/default/dualscope_next_task_selection.json`
- `outputs/dualscope_task_orchestrator/default/dualscope_next_task_prompt.md`

## Remaining Risks

- The repair implementation itself is intentionally not tested here; this task only unlocks a safe direct prompt for a later autorun execution.

## Next Suggested Plan

Merge this routing PR, then run autorun execute to perform `dualscope-first-slice-real-run-artifact-validation-repair`.
