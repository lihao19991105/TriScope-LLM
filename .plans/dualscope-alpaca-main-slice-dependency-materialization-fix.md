# DualScope Alpaca Main-Slice Dependency Materialization Fix

## Goal

Ensure `dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair` runs in a worktree with the same required local dependencies as the response-generation tasks it repairs.

The previous dependency repair recorded honest blockers, but the worktree runner skipped dependency materialization for this task id. That left the worktree without labeled pairs, Alpaca main-slice outputs, model binding, and the repository `.venv`, causing the repair to create an incorrect local Python environment and report missing inputs.

## Scope

- Treat response dependency repair tasks as Qwen2.5-7B worktree dependency consumers.
- Copy Alpaca main-slice plan and response repair outputs into the worktree when present.
- Symlink the main repository `.venv` into the task worktree so `.venv/bin/python` resolves to the configured runtime.
- Preserve the honest tracked blocker verdict and route unresolved blockers to blocker closure rather than repeating dependency repair.

## Non-Goals

- Do not fabricate response rows, logprobs, metrics, or clean utility.
- Do not alter benchmark truth or gates.
- Do not run a full matrix.
- Do not continue route_c or generate 199+.

## Validation

1. `python3 -m py_compile scripts/dualscope_task_worktree_runner.py`
2. `git diff --check`
3. Task orchestrator dry-run should select blocker closure after the dependency repair is already partially validated, or select the dependency repair only when its verdict is absent.

