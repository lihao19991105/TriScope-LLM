# DualScope Worktree Runner Existing PR Detection

## Purpose / Big Picture

Close the worktree autorun packaging gap where a task branch can already have an open PR, but a later runner packaging attempt reports the task as blocked because pushing the same branch is rejected as non-fast-forward.

The fix keeps the safety model intact: the runner never force-pushes, never deletes branches, and never merges. It only recognizes an already-open PR for the current task branch when the branch, base, commit or file scope match.

## Scope

### In Scope

- Detect non-fast-forward push failures from `./scripts/codex-pr.sh`.
- Query `gh pr list --head <branch> --state open` for the current task branch.
- Record `existing_pr_detected`, `existing_pr_number`, `existing_pr_url`, `task_pr_number`, `task_pr_url`, and `task_pr_source`.
- Pass existing task PR metadata through autorun artifacts and safe merge logic.
- Add runner artifacts for push and existing PR checks.

### Out of Scope

- Force pushing any branch.
- Merging unrelated PRs.
- Handling PR #14.
- Changing benchmark truth, gates, route_c, or 199+ planning.
- Faking review, CI, model responses, or metrics.

## Repository Context

- `scripts/dualscope_task_worktree_runner.py` owns task worktree execution and PR packaging.
- `src/eval/dualscope_autorun_loop_common.py` consumes runner artifacts and decides whether to stop, wait, or call the safe merge gate.
- `docs/dualscope_autorun_worktree_and_merge_gate.md` documents the worktree automation behavior.

## Deliverables

- Existing PR detection in the worktree runner.
- Autorun propagation of task PR source: `created` or `existing`.
- New artifacts:
  - `dualscope_task_worktree_runner_existing_pr_check.json`
  - `dualscope_task_worktree_runner_push_result.json`
- Validation with py_compile, help, and autorun dry-run.

## Progress

- [x] Inspect runner and autorun artifact flow.
- [x] Implement non-fast-forward existing PR detection.
- [x] Propagate task PR metadata to autorun.
- [x] Document behavior.
- [ ] Run validation commands.
- [ ] Submit PR and trigger Codex review.

## Surprises & Discoveries

- The previous runner treated `codex-pr.sh` non-fast-forward as packaging failure even when GitHub already had an open task PR for the same head branch.

## Decision Log

- Existing PR recognition is only allowed for the current task branch and `main` base.
- A PR is usable only when the PR head commit matches the local task commit or the local changed path set matches/subsets the PR file set.
- Non-fast-forward is handled by querying GitHub, not by force pushing.

## Plan of Work

Patch the runner first, then wire the metadata into autorun. Keep the change narrow and preserve safe merge gate authority for all merge decisions.

## Concrete Steps

1. Add helper functions for non-fast-forward detection, PR lookup, and Codex review evidence.
2. Emit push and existing-PR artifacts.
3. Add `task_pr_*` fields to runner summary and autorun JSONL rows.
4. Run validation.
5. Create a PR using the standard workflow.

## Validation and Acceptance

- `python3 -m py_compile scripts/dualscope_task_worktree_runner.py`
- `python3 -m py_compile scripts/dualscope_autorun_loop.py`
- `python3 -m py_compile src/eval/dualscope_autorun_loop_common.py`
- `.venv/bin/python scripts/dualscope_task_worktree_runner.py --help`
- `.venv/bin/python scripts/dualscope_autorun_loop.py --help`
- `.venv/bin/python scripts/dualscope_autorun_loop.py --dry-run --use-worktrees --max-iterations 1 --codex-extra-args "--cd {worktree_path} --full-auto" --output-dir outputs/dualscope_autorun_loop/default`

## Idempotence and Recovery

The runner may be re-run safely. If a task PR already exists, the runner records it instead of forcing the remote branch. If no matching PR exists, it stops with a real push blocker.

## Outputs and Artifacts

Artifacts are written under `outputs/dualscope_task_worktree_runner/default` and `outputs/dualscope_autorun_loop/default`.

## Remaining Risks

- If an existing PR uses the same branch but a different file scope, the runner correctly blocks; manual review is then required.
- If GitHub is unavailable, existing PR detection cannot run and the runner stops safely.

## Next Suggested Plan

After this PR is merged, rerun autorun with `--use-worktrees --enable-safe-auto-merge --safe-merge-current-task-pr` and allow the safe merge gate to merge only current task PRs.
