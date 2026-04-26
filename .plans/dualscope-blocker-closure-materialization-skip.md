# DualScope Blocker Closure Materialization Skip

## Goal

Allow blocker-closure tasks to run without requiring ignored Qwen2.5-7B response-generation output directories to be copied into the task worktree.

The current blocker-closure task is meant to summarize tracked registries and hard blockers, not rerun response generation. Forcing full Qwen dependency materialization on blocker closure can create a false blocker when ignored output directories are absent.

## Scope

- Skip Qwen dependency materialization for task ids containing `blocker-closure`.
- Preserve materialization for response generation, dependency repair, metric, and result package tasks.
- Do not weaken experiment execution gate for response-generation tasks.

## Validation

1. `python3 -m py_compile scripts/dualscope_task_worktree_runner.py`
2. Task orchestrator still selects `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-blocker-closure`.

