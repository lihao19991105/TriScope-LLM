# DualScope Worktree Materialization Optional Output Deps

## Purpose

Allow runtime readiness and repair tasks to execute even when ignored historical output directories are absent from the scheduler worktree.

## Change

Worktree materialization still treats source data files, model binding, cache directories, and `.venv` as hard dependencies. Missing copied `outputs/...` directories are now recorded as optional missing dependencies so the task can inspect and report them truthfully instead of being skipped before Codex execution.

## Validation

- `python3 -m py_compile scripts/dualscope_task_worktree_runner.py`
- `git diff --check`
- Re-run autorun so `dualscope-worktree-gpu-bnb-input-readiness-repair` reaches Codex execution.
