# DualScope Safe Merge Gate Verdict Registry Allowlist

## Purpose

Fix a safe merge gate file-scope false positive that blocks legitimate DualScope automation PRs containing tracked task verdict registry JSON files and DualScope autorun documentation. The change preserves hard safety gates while allowing the minimal files needed to persist task completion state.

## Scope

In scope:
- Allow `.reports/dualscope_task_verdicts/*.json` only.
- Validate registry JSON has `task_id`, `verdict`, and boolean `validated`.
- Allow `docs/dualscope_*.md` diagnostics without treating the filename substring `gate` as a semantic gate mutation.
- Keep forbidden secret, credential, benchmark truth, gate semantic, route_c, and 199+ checks.

Out of scope:
- No benchmark truth changes.
- No gate semantic weakening.
- No PR #14 handling.
- No unrelated docs or outputs allowlist expansion.

## Validation

- `python3 -m py_compile scripts/dualscope_safe_pr_merge_gate.py`
- `.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --help`
- check-only PR #40 with `--allow-auto-merge-without-review` and confirm `merge_allowed=true`, `file_scope_allowed=true`, `blocked_files=[]` after PR #40 removes non-JSON registry placeholders.

## Progress

- [x] Plan created.
- [x] Safe merge gate allowlist and diagnostics updated.
- [ ] PR #40 check-only rerun after gate fix is on main.
