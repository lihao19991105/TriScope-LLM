# DualScope First-Slice Experiment Queue Extension

## Purpose / Big Picture

Extend the completed DualScope automation queue into the first real first-slice experiment chain. This starts from the existing Stanford Alpaca first-slice labeled pairs and moves toward real response generation, label-aligned metrics, result packaging, and next-experiment readiness without expanding the matrix.

## Scope

### In Scope

- Add queue entries for `dualscope-first-slice-real-response-generation`, label-aligned metric computation, result packaging, and next-experiment readiness.
- Ensure the task orchestrator selects `dualscope-first-slice-real-response-generation` as the next task.
- Generate a complete direct queue prompt with explicit fake-response, fake-metric, benchmark-truth, and gate-change prohibitions.
- Update minimal docs and master planning pointers.

### Out of Scope

- Running the real response generation task inside this queue-extension PR.
- Expanding datasets, models, triggers, targets, budgets, or full experiment matrices.
- Training, LoRA, QLoRA, benchmark truth changes, gate changes, route_c continuation, or 199+ plans.

## Repository Context

- `DUALSCOPE_TASK_QUEUE.md` is the source of truth for orchestrator task selection and direct prompts.
- `src/eval/dualscope_task_orchestrator_common.py` renders direct queue prompts.
- `docs/dualscope_task_orchestrator.md`, `PLANS.md`, and `DUALSCOPE_MASTER_PLAN.md` describe the current mainline queue.
- Outputs remain under `outputs/`; this plan only adds queue metadata and does not execute experiment logic.

## Deliverables

- Four new queue tasks covering first-slice real response generation through next-experiment readiness.
- A direct prompt for the first new task that is non-empty and explicit about all experiment boundaries.
- Updated docs and planning pointers.

## Progress

- [x] Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md.
- [x] Create this ExecPlan.
- [x] Add queue entries and prompt templates.
- [x] Update orchestrator prompt hard constraints and docs.
- [x] Validate py_compile and task orchestrator dry-run.
- [ ] Commit and open PR via AGENTS.md workflow.

## Surprises & Discoveries

- The orchestrator correctly blocks next-task selection while this queue-extension branch has uncommitted business changes. The final task-selection validation should be rerun after committing the queue metadata.

## Decision Log

- Keep this PR as queue metadata only; autorun execution should happen after the queue-extension PR has review clearance and is merged.

## Plan of Work

Append the new experiment tasks after the completed readiness package. The first unvalidated appended task should become the next selected task. Keep all prompt templates explicit about first-slice-only scope, real/fallback distinction, and no fake metrics.

## Concrete Steps

1. Update the queue JSON and connect the previous terminal queue entry to `dualscope-first-slice-real-response-generation`.
2. Add a small task-orchestrator prompt hardening line set.
3. Update docs and planning files.
4. Run `py_compile` and task orchestrator dry-run.
5. Commit and create PR.

## Validation and Acceptance

- `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py` passes.
- `scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt` selects `dualscope-first-slice-real-response-generation`.
- `dualscope_next_task_prompt.md` is complete and contains the required safety constraints.

Validation completed on this branch: task selection chose `dualscope-first-slice-real-response-generation`, `prompt_available=true`, and the prompt includes AGENTS.md / PLANS.md / DUALSCOPE_MASTER_PLAN.md plus fake-response, fake-metric, benchmark-truth, and gate-change prohibitions.

## Idempotence and Recovery

The queue extension is pure metadata. Re-running the orchestrator should keep selecting the first unvalidated new task until its verdict artifact is produced.

## Outputs and Artifacts

- `outputs/dualscope_task_orchestrator/default/dualscope_next_task_selection.json`
- `outputs/dualscope_task_orchestrator/default/dualscope_next_task_prompt.md`

## Remaining Risks

- The subsequent response-generation task may be partially validated if local model execution or logprob support is unavailable. That must be recorded honestly by that task, not hidden in this queue extension.

## Next Suggested Plan

Merge this queue-extension PR, then run autorun with `--use-worktrees` to execute `dualscope-first-slice-real-response-generation`.
