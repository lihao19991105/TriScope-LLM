# DualScope Auto Merge Without Review Mode

## Purpose / Big Picture

This plan adds an explicitly authorized unattended autorun mode for cases where Codex connector review is still pending but all hard safety gates pass. The mode is not a blanket bypass: it only relaxes the `codex_review_missing` blocker when the user passes `--allow-auto-merge-without-review`; requested changes, failing checks, unsafe file scope, PR #14, benchmark truth changes, gate semantic changes, route_c / 199+ expansion, secrets, and credentials remain hard blockers.

## Scope

### In Scope

- Add `--allow-auto-merge-without-review` to autorun.
- Add `--allow-auto-merge-without-review` to the safe merge gate.
- Record explicit decision diagnostics for review-required state, missing-review authorization, merge policy, and merge reason.
- Validate compilation and help output.

### Out of Scope

- No PR #14 handling.
- No unrelated PR merge.
- No force push, branch deletion, reset hard, or remote rewrite.
- No benchmark truth or gate semantic edits.
- No route_c or 199+ continuation.
- No fake review, fake CI, model outputs, or metrics.

## Repository Context

- `scripts/dualscope_autorun_loop.py` exposes the user-facing autorun flag.
- `src/eval/dualscope_autorun_loop_common.py` passes the policy to safe merge gate only for the current autorun task PR.
- `scripts/dualscope_safe_pr_merge_gate.py` enforces hard safety checks and emits the merge decision artifact.

## Deliverables

- CLI flag support in autorun and safe merge gate.
- Decision artifact fields:
  - `codex_review_required`
  - `codex_review_present`
  - `review_missing_but_user_authorized`
  - `merged_without_codex_review`
  - `auto_merge_policy`
  - `merge_allowed_reason`
  - `merge_blockers`

## Progress

- [x] Added autorun CLI flag.
- [x] Added safe merge gate CLI flag.
- [x] Added diagnostics fields.
- [x] Run validation.
- [ ] Update PR and merge only if hard safety checks pass.

## Validation

Run:

```bash
python3 -m py_compile scripts/dualscope_autorun_loop.py
python3 -m py_compile scripts/dualscope_safe_pr_merge_gate.py
python3 -m py_compile src/eval/dualscope_autorun_loop_common.py
.venv/bin/python scripts/dualscope_autorun_loop.py --help
.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --help
```

## Remaining Risks

This mode intentionally allows merge without review evidence only after explicit user authorization. It must stay opt-in and must continue to require all hard safety checks.
