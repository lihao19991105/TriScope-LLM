# DualScope Autorun Task Worktree And Merge Gate

## Purpose / Big Picture

This plan closes the last automation gap in the DualScope autorun pipeline. The autorun loop can already select tasks, generate prompts, call `codex exec`, create PRs, and check PR / CI status, but running tasks in the main checkout leaves real business dirty files behind and forces a human to package, merge, clean, and restart.

The goal is to make the main checkout a scheduler only. Each task runs in an isolated git worktree, produces its own branch and PR, and can later pass through an explicit safe merge gate.

## Scope

### In Scope

- Add a task worktree runner CLI.
- Add a safe PR merge gate CLI.
- Add `--use-worktrees` support to the autorun loop.
- Keep auto merge disabled by default.
- Write machine-readable artifacts for worktree execution, PR creation, merge decisions, and blockers.
- Validate compile, help, autorun dry-run, and safe merge gate check-only behavior.

### Out of Scope

- Automatically merging real PRs during this implementation task.
- Force pushing, deleting branches, changing remotes, or cleaning the user's main checkout.
- Changing benchmark truth, gates, labels, model outputs, or performance metrics.
- Continuing historical route_c work or generating 199+ tasks.

## Repository Context

- Scheduler CLI: `scripts/dualscope_autorun_loop.py`
- Scheduler implementation: `src/eval/dualscope_autorun_loop_common.py`
- Task selection: `scripts/dualscope_task_orchestrator.py`
- PR review status: `scripts/dualscope_pr_review_orchestrator.py`
- PR creation workflow: `scripts/codex-pr.sh`

## Deliverables

- `scripts/dualscope_task_worktree_runner.py`
- `scripts/dualscope_safe_pr_merge_gate.py`
- `docs/dualscope_autorun_worktree_and_merge_gate.md`
- `--use-worktrees` and related autorun loop arguments
- Worktree runner artifacts under `outputs/dualscope_task_worktree_runner/default`
- Safe merge gate artifacts under `outputs/dualscope_safe_pr_merge_gate/default`
- Autorun worktree artifacts under `outputs/dualscope_autorun_loop/default`

## Progress

- [x] Read repository instructions and queue state.
- [x] Preserve current dirty main checkout by using an isolated development worktree.
- [x] Implement task worktree runner.
- [x] Implement safe PR merge gate.
- [x] Wire autorun loop worktree mode.
- [x] Add documentation.
- [x] Run compile / help / dry-run / merge-gate check-only validation.
- [x] Open PR and trigger Codex review.

## Surprises & Discoveries

- The main checkout already contains PR #17 real business files. This plan intentionally avoids touching them by developing in a separate worktree.
- Existing autorun dirty-worktree handling remains useful for scheduler safety and is retained for non-worktree mode.

## Decision Log

- Auto merge remains opt-in behind `--enable-safe-auto-merge`.
- The safe merge gate blocks PR #14 by default so old follow-up PRs cannot be merged by unattended autorun.
- The worktree runner creates PRs only for the current task branch and never merges them.
- In worktree dry-run mode, autorun writes command previews and stops after one planned task.

## Plan of Work

Implement the two new CLIs first, then route autorun execution through the worktree runner when `--use-worktrees` is enabled. Keep the merge gate separate so all automatic merge behavior has a single auditable decision artifact.

## Concrete Steps

1. Add `scripts/dualscope_task_worktree_runner.py`.
2. Add `scripts/dualscope_safe_pr_merge_gate.py`.
3. Extend autorun loop CLI and `AutorunLoopArgs`.
4. Add worktree-mode artifacts in autorun loop output.
5. Add documentation.
6. Run compile and help checks.
7. Run autorun worktree dry-run.
8. Run safe merge gate check-only on an available PR.
9. Commit and create PR through `scripts/codex-pr.sh`.

## Validation and Acceptance

Accepted when:

- New scripts pass `py_compile`.
- Autorun loop passes `py_compile`.
- All three CLIs expose `--help`.
- Autorun worktree dry-run selects a task and writes a worktree command preview.
- Safe merge gate check-only writes all required artifacts and does not merge.
- No auto merge, force push, branch deletion, remote rewrite, benchmark truth change, gate change, route_c continuation, or 199+ generation occurs.

## Idempotence and Recovery

Worktrees are created under `/tmp/dualscope-worktrees` by default and can be preserved with `--keep-worktree`. Merge-gate check-only is read-only. Failed worktree runs preserve their worktree path in artifacts for inspection.

## Outputs and Artifacts

- `outputs/dualscope_task_worktree_runner/default/`
- `outputs/dualscope_safe_pr_merge_gate/default/`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_worktree_iterations.jsonl`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_created_prs.jsonl`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_merge_decisions.jsonl`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_worktree_cleanup.jsonl`

## Remaining Risks

- Full unattended auto-merge should still be validated through one real smoke PR review cycle before enabling it for multi-iteration runs.
- Review latency can block merge gate decisions even when CI has no failures.

## Next Suggested Plan

Run autorun loop with `--use-worktrees --execute --max-iterations 2`, and enable safe auto-merge only after confirming one smoke PR review cycle.
