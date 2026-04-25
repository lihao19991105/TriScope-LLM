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
  - When `--wait-for-codex-review` is enabled, waits for Codex connector review if the only safe merge blocker is missing review evidence.

## Safe Defaults

- Auto merge is disabled by default.
- Branch deletion is disabled.
- Force push is never used.
- SSH remote rewrites are not performed.
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

## Review Waiter

The review waiter is enabled by default in autorun and is controlled by:

- `--wait-for-codex-review`
- `--max-review-wait-minutes`
- `--review-poll-interval-seconds`
- `--continue-after-review-merge`

It only waits when all of the following are true:

- The PR is the current autorun task PR.
- The safe merge gate blocker list contains only `codex_review_missing`.
- `@codex review` has been requested.
- There are no requested changes.
- There are no failing checks.
- File scope is safe.
- The PR is not PR #14.

Each poll re-runs the safe merge gate. If Codex connector review appears and the gate allows merge, autorun performs a squash merge with `--delete-branch=false`, checks out `main`, pulls `origin main`, optionally removes the merged worktree, and continues to the next iteration.

The waiter stops without merging on requested changes, failing checks, unsafe file scope, review timeout, or any blocker other than missing Codex review evidence.

Waiter artifacts are written under the autorun output directory:

- `dualscope_autorun_review_waiter_status.json`
- `dualscope_autorun_review_waiter_iterations.jsonl`
- `dualscope_autorun_review_waiter_report.md`

## Explicit No-Review Auto Merge Mode

For unattended operation, the user can explicitly pass:

```bash
--allow-auto-merge-without-review
```

This only relaxes the missing Codex review evidence blocker. It does not relax hard safety gates:

- requested changes still block
- failing checks still block
- unsafe file scope still blocks
- PR #14 still blocks
- benchmark truth, gate semantic changes, route_c / 199+, secrets, `.env`, and credentials still block
- force push, branch deletion, non-squash merge, and remote rewrite remain forbidden

Decision artifacts record the policy through:

- `codex_review_required`
- `review_missing_but_user_authorized`
- `merged_without_codex_review`
- `auto_merge_policy`
- `merge_allowed_reason`
