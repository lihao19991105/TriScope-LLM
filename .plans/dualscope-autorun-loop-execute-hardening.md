# dualscope-autorun-loop-execute-hardening

## Purpose / Big Picture

This task hardens the DualScope autorun loop execute path. The current dry-run path can select tasks and preview work, but execute mode can be blocked by runtime artifacts created by the loop itself, especially local logs and temporary Codex wrapper files.

The result should make `scripts/dualscope_autorun_loop.py --execute` stable enough to call `codex exec` with explicit full-auto arguments while preserving the DualScope safety rules: no automatic merge, no force push, no branch deletion, no remote rewrite, stop on requested changes, and stop on failing checks.

This serves the DualScope mainline by improving reproducible execution reliability for budget-aware, queue-driven work. It does not continue old route_c chains and does not generate `199+` plans.

## Scope

### In Scope

- Add `--codex-extra-args` to the autorun loop.
- Build `codex exec <extra args> "<prompt>"` with `shlex.split`.
- Add `--ignore-runtime-dirty-paths` with a default enabled policy.
- Classify dirty paths before task selection into runtime artifacts, temporary wrappers, generated outputs, and real business changes.
- Move the rolling autorun log to `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_log.md`.
- Add hardening artifacts for dirty worktree checks, command previews, summary, and report.
- Preserve execute-mode failure artifacts with exit code, stdout, stderr, command, selected task, and prompt path.
- Keep all safety constraints explicit.

### Out of Scope

- No automatic merge.
- No force push.
- No branch deletion.
- No remote rewrite or SSH remote conversion.
- No benchmark truth or gate changes.
- No full experiment matrix expansion.
- No route_c continuation or `199+` planning.

## Repository Context

Relevant files:

- `scripts/dualscope_autorun_loop.py`
- `src/eval/dualscope_autorun_loop_common.py`
- `src/eval/dualscope_task_orchestrator_common.py`
- `docs/dualscope_autorun_loop.md`
- `outputs/dualscope_autorun_loop/default/`

The task orchestrator currently blocks on any dirty working tree. Because autorun itself writes runtime artifacts before task selection, the autorun loop needs a narrow runtime-dirty allowance that does not hide real business changes under `.plans/`, `src/`, most `scripts/`, most `docs/`, README, AGENTS, PLANS, `DUALSCOPE_MASTER_PLAN.md`, or `DUALSCOPE_TASK_QUEUE.md`.

## Deliverables

- Updated autorun CLI and common helper.
- Updated task-orchestrator dirty gate support for autorun-controlled runtime artifacts.
- Updated autorun documentation.
- New hardening ExecPlan.
- Runtime artifacts:
  - `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_dirty_worktree_check.json`
  - `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_codex_command_preview.json`
  - `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_execute_hardening_summary.json`
  - `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_execute_hardening_report.md`

## Progress

- [x] M1: Read repository instructions and existing autorun/task-orchestrator implementation.
- [x] M2: Implement execute hardening.
- [ ] M3: Run required compile/help/dry-run/execute-smoke validation.
- [ ] M4: Commit, open PR, trigger Codex review, and record PR/review status.

## Surprises & Discoveries

- Local `main` did not yet contain the autorun loop files. The hardening branch was created from `main` in a separate worktree, then the existing task-orchestrator and autorun-loop commits were cherry-picked before applying this task.
- The original working tree had unrelated first-slice/rerun changes. This plan uses the separate worktree to avoid reverting or overwriting them.

## Decision Log

- Decision: Use `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_log.md` as the rolling log path.
  - Reason: writing a tracked docs log during every run creates a self-inflicted dirty worktree blocker.
- Decision: Treat `scripts/codex_exec_full_auto_wrapper.sh` as a legacy temporary wrapper path that should not block task selection by itself, but should be reported with a warning.
  - Reason: execute mode should not require or preserve repo-local wrappers.
- Decision: Keep dirty-path ignoring narrow and explicit.
  - Reason: runtime artifacts should not hide real DualScope method, docs, plan, or script edits.

## Plan of Work

First update the autorun CLI and command construction path. Then add dirty-worktree classification and expose it to the task orchestrator through a narrow environment flag used only when `--ignore-runtime-dirty-paths` is enabled. Finally update docs and validate dry-run plus a one-iteration execute smoke.

## Concrete Steps

1. Add CLI fields for `--codex-extra-args` and `--ignore-runtime-dirty-paths`.
2. Add command preview construction with `shlex.split`.
3. Add runtime dirty classification and artifacts.
4. Move rolling log output to the autorun output directory.
5. Preserve execute failure details.
6. Update documentation.
7. Run required validation commands.
8. Commit and create PR with `./scripts/codex-pr.sh`.

## Validation and Acceptance

Required commands:

- `python3 -m py_compile scripts/dualscope_autorun_loop.py`
- `python3 -m py_compile src/eval/dualscope_autorun_loop_common.py`
- `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py`
- `.venv/bin/python scripts/dualscope_autorun_loop.py --help`
- `.venv/bin/python scripts/dualscope_autorun_loop.py --dry-run --max-iterations 1 --codex-extra-args "--cd /home/lh/TriScope-LLM --full-auto" --output-dir outputs/dualscope_autorun_loop/default`
- `.venv/bin/python scripts/dualscope_autorun_loop.py --execute --max-iterations 1 --max-minutes 60 --allow-review-pending-continue --stop-on-requested-changes --stop-on-failing-checks --codex-extra-args "--cd /home/lh/TriScope-LLM --full-auto" --output-dir outputs/dualscope_autorun_loop/default`

Accepted final verdicts:

- `Autorun execute hardening validated`
- `Partially validated`
- `Not validated`

## Idempotence and Recovery

All runtime artifacts are overwritten or appended under `outputs/dualscope_autorun_loop/default/`. Re-running dry-run or execute smoke should not dirty tracked docs. If execute fails, the failure report contains the command, selected task, prompt path, exit code, stdout, and stderr so the next run can resume from the blocker.

## Outputs and Artifacts

- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_log.md`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_dirty_worktree_check.json`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_codex_command_preview.json`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_execute_hardening_summary.json`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_execute_hardening_report.md`

## Remaining Risks

- Execute smoke depends on local Codex CLI behavior and credentials.
- PR/CI state can safely stop execution even when the implementation is correct.

## Next Suggested Plan

If validated, the next action is: `Run autorun loop with --execute --max-iterations 2.`
