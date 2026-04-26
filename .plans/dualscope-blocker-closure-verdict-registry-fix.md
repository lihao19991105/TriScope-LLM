# DualScope Blocker Closure Verdict Registry Fix

## Goal

Prevent blocker-closure tasks from being re-selected after they have already produced a truthful tracked verdict registry.

## Scope

- Preserve an existing task-specific tracked verdict registry instead of overwriting it with an unrelated output verdict.
- Only auto-persist output verdicts when the verdict artifact path is task-specific.
- Treat a validated nested blocker-closure follow-up as handled during task selection.
- Correct the Qwen2.5-7B Alpaca main-slice blocker-closure registry so it documents blocker closure only, not model-axis validation.

## Safety Constraints

- Do not fabricate responses, logprobs, labels, metrics, reviews, or CI.
- Do not modify benchmark truth or gates.
- Do not continue route_c or generate 199+.
- Do not force push, delete branches, rewrite remotes, or merge unrelated PRs.

## Validation

- `python3 -m py_compile scripts/dualscope_task_worktree_runner.py`
- `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py`
- Task orchestrator dry-run should return `queue_complete` once the closure registry is corrected.
