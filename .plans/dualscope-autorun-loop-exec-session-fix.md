# dualscope-autorun-loop-exec-session-fix

## Purpose / Big Picture

This task fixes the DualScope autorun loop execute session path so `scripts/dualscope_autorun_loop.py --execute` can reliably reach `codex exec` without stopping on self-generated runtime artifacts, temporary wrapper files, or an unwritable Codex session/TMPDIR environment.

The change supports the DualScope mainline by making queue-driven execution more reproducible while preserving strict safety: no automatic merge, no force push, no branch deletion, no remote rewrite, stop on requested changes, stop on failing checks, no benchmark truth edits, no gate edits, and no old route_c / `199+` continuation.

## Scope

### In Scope

- Add or preserve `--codex-extra-args`.
- Add `--runtime-log-dir`.
- Add `--codex-tmpdir`.
- Launch `codex exec` with a stable environment:
  - `cwd=/home/lh/TriScope-LLM`
  - `HOME=/home/lh`
  - `TMPDIR=/home/lh/TriScope-LLM/.tmp/codex`
  - proxy variables set to `http://127.0.0.1:18080`
- Ensure TMPDIR exists and is writable before `codex exec`.
- Treat `.tmp/` as runtime-only dirty state.
- Keep runtime logs under `outputs/dualscope_autorun_loop/default`.
- Write command preview, execution environment, dirty classification, failure diagnostics, summary, report, blockers, and exec-result artifacts.
- Validate dry-run and a one-iteration execute smoke or record a true blocker.

### Out of Scope

- No automatic merge.
- No force push.
- No branch deletion.
- No remote rewrite or SSH conversion.
- No benchmark truth or gate changes.
- No route_c continuation or `199+` planning.
- No broad unrelated refactor.

## Repository Context

Relevant files:

- `scripts/dualscope_autorun_loop.py`
- `src/eval/dualscope_autorun_loop_common.py`
- `src/eval/dualscope_task_orchestrator_common.py`
- `docs/dualscope_autorun_loop.md`
- `.gitignore`

The existing autorun/task-orchestrator baseline is already present on earlier PR branches but not local `main`, so this task branch was created from `main` and then brought forward the existing autorun/task-orchestrator commits before applying the session-environment fix.

## Deliverables

- CLI support for `--codex-extra-args`, `--ignore-runtime-dirty-paths`, `--runtime-log-dir`, and `--codex-tmpdir`.
- Stable Codex execution environment artifact.
- Runtime dirty classification artifact.
- Codex failure diagnostics artifact when execute fails.
- Updated docs explaining the new execution environment and runtime log path.
- One-iteration dry-run and execute-smoke validation artifacts.

## Progress

- [x] M1: Read project instructions and classify primary working-tree state.
- [x] M2: Create clean worktree branch from `main` and bring forward autorun baseline.
- [x] M3: Implement session/TMPDIR fix and runtime dirty classification updates.
- [ ] M4: Run py_compile, help, dry-run, and execute smoke.
- [ ] M5: Commit, open PR, trigger Codex review, and check previous PR status.

## Surprises & Discoveries

- The primary `/home/lh/TriScope-LLM` worktree contains real business changes under `DUALSCOPE_*`, `PLANS.md`, `.plans/`, `scripts/`, and `src/`. Those changes were not modified.
- The previous execute hardening smoke reached `codex exec`, but Codex failed while creating a session because the environment exposed a read-only session/TMP location.

## Decision Log

- Decision: Use `/home/lh/TriScope-LLM/.tmp/codex` as the default Codex TMPDIR.
  - Reason: the target repository path is writable in normal local execution, and `.tmp/` can be treated as runtime-only state.
- Decision: Set `stdin=subprocess.DEVNULL` for subprocess calls.
  - Reason: avoids Codex appending unintended piped stdin to an explicit prompt.
- Decision: Remove the tracked `docs/dualscope_autorun_loop_log.md` runtime log file.
  - Reason: docs should document behavior, not receive per-run dirty runtime logs.

## Plan of Work

First add CLI and dataclass fields for runtime log dir and Codex TMPDIR. Then add execution-environment preparation and TMPDIR writability checks. Next update dirty classification in both autorun and task orchestrator so `.tmp/` is runtime-only but true business paths remain blockers. Finally run validation and PR workflow.

## Concrete Steps

1. Update CLI arguments and configuration artifacts.
2. Add TMPDIR preparation and exec-environment artifact writing.
3. Update `run_codex_exec` to use `cwd`, `HOME`, `TMPDIR`, proxy env, and `stdin=DEVNULL`.
4. Write required diagnostics artifacts on failure.
5. Update docs and remove tracked runtime log.
6. Run required tests and smoke.
7. Commit and open PR.

## Validation and Acceptance

Required commands:

- `python3 -m py_compile scripts/dualscope_autorun_loop.py`
- `python3 -m py_compile src/eval/dualscope_autorun_loop_common.py`
- `.venv/bin/python scripts/dualscope_autorun_loop.py --help`
- `.venv/bin/python scripts/dualscope_autorun_loop.py --dry-run --max-iterations 1 --codex-extra-args "--cd /home/lh/TriScope-LLM --full-auto" --output-dir outputs/dualscope_autorun_loop/default`
- `.venv/bin/python scripts/dualscope_autorun_loop.py --execute --max-iterations 1 --max-minutes 60 --allow-review-pending-continue --stop-on-requested-changes --stop-on-failing-checks --codex-extra-args "--cd /home/lh/TriScope-LLM --full-auto" --output-dir outputs/dualscope_autorun_loop/default`

Final verdict must be exactly one of:

- `Autorun execute hardening validated`
- `Partially validated`
- `Not validated`

## Idempotence and Recovery

The autorun loop overwrites structured artifacts under `outputs/dualscope_autorun_loop/default/` and writes runtime logs to the configured runtime log directory. `.tmp/` is runtime-only and ignored by git. If execute fails, diagnostics include the exact command, cwd, HOME, TMPDIR, writability state, stdout, stderr, exit code, selected task, and prompt path.

## Outputs and Artifacts

- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_dirty_worktree_classification.json`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_codex_command_preview.json`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_exec_environment.json`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_exec_failure_diagnostics.json` when execute fails
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_execute_hardening_summary.json`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_execute_hardening_report.md`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_summary.json`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_blockers.json`
- `outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_codex_exec_results.jsonl`

## Remaining Risks

- Execute smoke runs a real `codex exec` call. If a previous PR review or CI blocker is detected, a safe stop is expected.
- The target `/home/lh/TriScope-LLM` primary worktree still has unrelated business changes; this task does not alter them.

## Next Suggested Plan

If validated, the next action is: `Run autorun loop with --execute --max-iterations 2.`
