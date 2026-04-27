# DualScope Workflow Gate Output and Git Identity Fix

## Purpose / Big Picture

After the worktree runner began executing Codex successfully, the AdvBench response-generation-plan task produced a valid planning PR (#114) but the automation stopped on two workflow false positives:

- the safe merge gate blocked the task's expected plan output JSON artifacts;
- the worktree runner could not commit task files because isolated worktrees lacked local `user.name` and `user.email`.

This plan fixes both workflow issues without changing benchmark truth, experiment semantics, or generated results.

## Scope

### In Scope

- Add narrow output artifact allowlist patterns for the bounded AdvBench/JBB and expanded synthesis task output directories already listed in `DUALSCOPE_TASK_QUEUE.md`.
- Configure local git identity inside task worktrees immediately before runner-managed commits.
- Validate syntax and safe gate behavior against PR #114.

### Out of Scope

- No fabricated data, responses, logprobs, or metrics.
- No benchmark truth, route_c, 199+, or semantic gate bypass.
- No PR #14 handling.
- No force push or branch deletion.

## Progress

- [x] Identify PR #114 as a real task PR created by Codex.
- [x] Confirm PR #114 is blocked only by file-scope allowlist for expected plan output JSONs.
- [x] Identify missing git identity as the runner commit blocker.
- [x] Patch safe gate output allowlist and worktree runner git identity setup.
- [ ] Run syntax checks, `git diff --check`, and PR #114 safe gate check-only.
- [ ] Open, review, safe-merge, and verify this workflow fix PR.
- [ ] Merge PR #114 if the updated safe gate passes.
- [ ] Resume long-run autorun.

## Validation

Run:

```bash
python3 -m py_compile scripts/dualscope_safe_pr_merge_gate.py scripts/dualscope_task_worktree_runner.py
git diff --check
.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --pr 114 --check-only --allow-auto-merge-without-review --output-dir outputs/dualscope_safe_pr_merge_gate/pr114_check_after_workflow_fix
```

Acceptance requires PR #114 to have `file_scope_allowed=true` and no blocked files while still preserving requested-changes, failing-checks, secrets, data, benchmark-truth, gate-risk, route_c, and 199+ blockers.

