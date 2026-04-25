# DualScope Autorun Review Waiter

## Purpose / Big Picture

DualScope autorun can already create task PRs, trigger `@codex review`, and call the safe merge gate. The remaining unattended-run blocker is timing: immediately after PR creation, the safe merge gate correctly blocks because Codex connector review evidence is still pending. This plan adds an autorun-level review waiter so the loop waits for Codex review evidence instead of stopping when the only blocker is `codex_review_missing`.

The result should let autorun safely continue after the current task PR receives Codex connector review, while still stopping immediately on requested changes, failing checks, unsafe file scope, PR #14, or unrelated PRs.

## Scope

### In Scope

- Add autorun CLI support for `--wait-for-codex-review` and `--continue-after-review-merge`.
- Change the default review wait budget to 60 minutes.
- Add structured review-waiter artifacts under `outputs/dualscope_autorun_loop/default`.
- Wait only when the safe merge gate blocker is exactly `codex_review_missing`, review was requested, file scope is safe, and there are no requested changes or failing checks.
- Re-run the safe merge gate during polling; merge only through the gate.
- Continue after merge when configured.

### Out of Scope

- No PR #14 handling.
- No force push, branch deletion, remote rewrite, or non-squash merge.
- No benchmark truth or gate semantic changes.
- No route_c continuation or 199+ generation.
- No fake review, fake CI, model response, or metric fabrication.

## Repository Context

- `scripts/dualscope_autorun_loop.py` owns user-facing autorun CLI flags.
- `src/eval/dualscope_autorun_loop_common.py` owns the worktree autorun loop and safe merge gate orchestration.
- `scripts/dualscope_safe_pr_merge_gate.py` owns PR safety diagnostics and now exposes requested-change and failing-check counts in the decision artifact.
- `docs/dualscope_autorun_worktree_and_merge_gate.md` documents the safe auto-merge workflow.

## Deliverables

- Review waiter logic in autorun worktree safe auto-merge mode.
- Waiter artifacts:
  - `dualscope_autorun_review_waiter_status.json`
  - `dualscope_autorun_review_waiter_iterations.jsonl`
  - `dualscope_autorun_review_waiter_report.md`
- Updated safe merge gate diagnostics with requested-change and failing-check counts.
- Updated documentation and validation results.

## Progress

- [x] Added plan.
- [x] Added CLI flags and defaults.
- [x] Added waiter eligibility checks.
- [x] Added waiter artifacts and report.
- [x] Added merge-after-review flow through safe merge gate.
- [x] Updated documentation.
- [x] Run py_compile and help.
- [x] Run dry-run.
- [x] Run PR #29 safe merge gate check-only.
- [ ] Create PR and trigger Codex review.

## Validation and Acceptance

Required validation:

```bash
python3 -m py_compile scripts/dualscope_autorun_loop.py
python3 -m py_compile scripts/dualscope_safe_pr_merge_gate.py
python3 -m py_compile src/eval/dualscope_autorun_loop_common.py
.venv/bin/python scripts/dualscope_autorun_loop.py --help
.venv/bin/python scripts/dualscope_autorun_loop.py --dry-run --use-worktrees --enable-safe-auto-merge --safe-merge-current-task-pr --require-codex-review-before-merge --wait-for-codex-review --max-review-wait-minutes 1 --review-poll-interval-seconds 10 --max-iterations 1 --codex-extra-args "--cd {worktree_path} --full-auto" --output-dir outputs/dualscope_autorun_loop/default
.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --pr 29 --check-only --output-dir outputs/dualscope_safe_pr_merge_gate/pr29_check
```

Acceptance:

- The waiter does not merge without safe merge gate approval.
- The waiter stops on requested changes, failing checks, unsafe file scope, and review timeout.
- The waiter can continue after a gate-approved merge.
- No dangerous actions occur.

## Remaining Risks

- If Codex connector review remains delayed past the configured timeout, autorun will still stop with `review_timeout`.
- Existing PRs still need safe merge gate file-scope coverage for their exact artifact directories.

## Next Suggested Plan

After this fix is merged, run:

```bash
.venv/bin/python scripts/dualscope_autorun_loop.py --execute --use-worktrees --enable-safe-auto-merge --safe-merge-current-task-pr --require-codex-review-before-merge --wait-for-codex-review --max-iterations 3 --codex-extra-args "--cd {worktree_path} --full-auto" --output-dir outputs/dualscope_autorun_loop/default
```
