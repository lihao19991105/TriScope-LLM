# DualScope Safe Merge Gate Registry Fetch Fix

## Purpose

Fix the verdict registry JSON validation fetch path in the safe merge gate. The previous allowlist implementation used `gh api -f ref=...` without explicitly forcing GET, which can fail to fetch PR-branch file content for validation.

## Scope

In scope:
- Use `gh api --method GET -f ref=<headRefName>` when fetching `.reports/dualscope_task_verdicts/*.json` from a PR branch.
- Preserve existing file-scope, requested-changes, CI, secret, benchmark truth, gate semantic, route_c, and 199+ blockers.

Out of scope:
- No merge policy relaxation.
- No benchmark truth or gate semantic changes.
- No PR #14 handling.

## Validation

- `python3 -m py_compile scripts/dualscope_safe_pr_merge_gate.py`
- `.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --help`
- PR #40 check-only passes with `merge_allowed=true` and `blocked_files=[]`.
