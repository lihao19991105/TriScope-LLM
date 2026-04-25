# DualScope Safe Merge Gate Artifact Review Fix

## Purpose / Big Picture

This plan fixes the safe merge gate blocker that prevents DualScope autorun from merging the current SCI3 task PR after review and CI are already safe. The immediate issue is that valid task artifacts under SCI3 `outputs/` paths are treated as out of scope, and Codex connector comments such as "Didn't find any major issues" are not recorded as review evidence.

The completed fix lets autorun continue the SCI3 queue without weakening the existing safety boundary: the gate still blocks requested changes, failing checks, branch deletion, non-squash merge, PR #14, secrets, benchmark truth changes, gate semantic changes, legacy route_c expansion, and unrelated files.

## Scope

### In Scope

- Extend safe merge gate file allowlist for the current SCI3 task artifact output directories.
- Add structured Codex connector comment detection.
- Add clearer diagnostics for review evidence, file scope, allowed output artifacts, blockers, and merge decision.
- Validate PR #26 with check-only mode after the local fix.
- Package the fix as a dedicated PR before using it to merge PR #26 from main.

### Out of Scope

- No benchmark truth changes.
- No gate semantic changes.
- No PR #14 handling.
- No force push, branch deletion, remote rewrite, or auto-merge default changes.
- No model response or metric fabrication.
- No route_c or 199+ continuation.

## Repository Context

- `scripts/dualscope_safe_pr_merge_gate.py` owns the check-only and merge enforcement logic.
- `outputs/dualscope_safe_pr_merge_gate/*` stores decision artifacts.
- The SCI3 queue currently needs to merge task PRs that include structured artifacts under `outputs/dualscope_*`.
- PR #26 is the concrete regression case: it contains `outputs/dualscope_main_model_axis_upgrade_plan/default/*` and has a Codex connector comment with no major issues.

## Deliverables

- Updated safe merge gate allowlist for the required SCI3 output artifact directories.
- Updated Codex review evidence detection.
- Updated gate diagnostics:
  - `codex_review_requested`
  - `codex_review_present`
  - `codex_review_evidence_source`
  - `codex_review_evidence_excerpt`
  - `file_scope_allowed`
  - `blocked_files`
  - `allowed_outputs_artifacts`
  - `merge_allowed`
  - `merge_blockers`
- A dedicated fix PR created through the AGENTS.md workflow.

## Validation

Run:

```bash
python3 -m py_compile scripts/dualscope_safe_pr_merge_gate.py
.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --help
.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --pr 26 --check-only --output-dir outputs/dualscope_safe_pr_merge_gate/pr26_check
```

PR #26 check-only must show:

- `merge_allowed = true`
- `codex_review_present = true`
- `file_scope_allowed = true`
- `requested_changes_count = 0`
- no failing checks
- no blocked files

## Progress

- [x] Created focused plan.
- [x] Added SCI3 output artifact allowlist entries.
- [x] Added Codex connector comment review evidence detection.
- [x] Added clearer diagnostics to file scope, review, and decision artifacts.
- [ ] Run validation commands.
- [ ] Create fix PR and trigger Codex review.
- [ ] Merge fix PR only after safe conditions are met.
- [ ] Re-run PR #26 gate from fixed main and continue autorun.
