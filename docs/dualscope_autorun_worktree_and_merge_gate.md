# DualScope Autorun Worktree And Merge Gate

This document describes the unattended execution layer for DualScope autorun.

## Goal

The scheduler checkout should remain clean. Each selected task can run inside an isolated git worktree, create its own task branch and PR, then wait for an explicit safe merge gate.

## Components

- `scripts/dualscope_task_worktree_runner.py`
  - Creates a task worktree from `main`.
  - Runs `codex exec --cd <worktree> --full-auto <prompt>`.
  - Runs local checks on changed Python files.
  - Commits task changes and calls `./scripts/codex-pr.sh`.
  - If pushing the current task branch is rejected as non-fast-forward, queries GitHub for an existing open PR with the same head branch and records it as the current task PR only when the branch/base and commit or file scope match.
  - Never merges PRs.

- `scripts/dualscope_safe_pr_merge_gate.py`
  - Reads one explicit PR.
  - Blocks requested changes, failing checks, forbidden files, PR #14, branch deletion, non-squash merge, and missing Codex review unless explicitly relaxed.
  - Defaults to check-only behavior unless `--merge` is passed.

- `scripts/dualscope_autorun_loop.py --use-worktrees`
  - Keeps the main checkout as scheduler.
  - Selects the next task through the task orchestrator.
  - Delegates task execution to the worktree runner.
  - Records created PRs and merge decisions.
  - Does not auto merge unless `--enable-safe-auto-merge` is explicitly set.

## Safe Defaults

- Auto merge is disabled by default.
- Branch deletion is disabled.
- Force push is never used.
- SSH remote rewrites are not performed.
- Existing task PR detection never uses force push; unmatched non-fast-forward push failures remain blockers.
- PR #14 is blocked by the merge gate by default.
- Benchmark truth, gates, route_c continuations, 199+ plans, secrets, and credential files are forbidden by merge-gate file scope checks.

## Typical Dry Run

```bash
.venv/bin/python scripts/dualscope_autorun_loop.py \
  --dry-run \
  --use-worktrees \
  --max-iterations 1 \
  --codex-extra-args "--cd {worktree_path} --full-auto" \
  --output-dir outputs/dualscope_autorun_loop/default
```

## Safe Merge Gate Check-Only

```bash
.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py \
  --pr 17 \
  --check-only \
  --output-dir outputs/dualscope_safe_pr_merge_gate/default
```

## Execute Without Auto Merge

```bash
.venv/bin/python scripts/dualscope_autorun_loop.py \
  --execute \
  --use-worktrees \
  --max-iterations 1 \
  --max-minutes 60 \
  --allow-review-pending-continue \
  --stop-on-requested-changes \
  --stop-on-failing-checks \
  --codex-extra-args "--cd {worktree_path} --full-auto" \
  --output-dir outputs/dualscope_autorun_loop/default
```

This mode may create a PR, but it will not merge the PR.

## Execute With Safe Auto Merge

Only enable after a smoke PR review cycle has been manually inspected:

```bash
.venv/bin/python scripts/dualscope_autorun_loop.py \
  --execute \
  --use-worktrees \
  --enable-safe-auto-merge \
  --safe-merge-current-task-pr \
  --require-codex-review-before-merge \
  --max-iterations 2 \
  --codex-extra-args "--cd {worktree_path} --full-auto" \
  --output-dir outputs/dualscope_autorun_loop/default
```

The merge gate still blocks requested changes, failing checks, forbidden files, PR #14, non-main bases, branch deletion, and non-squash merge.
