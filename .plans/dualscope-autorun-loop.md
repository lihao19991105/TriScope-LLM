# dualscope-autorun-loop

## Background

DualScope-LLM now has a local task queue and a task orchestrator that can choose the next prompt. The missing piece is an outer loop that repeatedly checks PR state, selects the next queue task, executes the generated Codex prompt when explicitly allowed, records artifacts, and stops on review or environment blockers.

## Why autorun loop is needed

Without an outer loop, Codex completes one generated prompt and exits. The autorun loop provides a controlled local driver for continuous task execution while preserving the repository safety rules: PR review blockers stop the loop, requested changes are not ignored, and task selection remains queue-driven.

## Existing components

- `scripts/dualscope_pr_review_orchestrator.py`
- `scripts/dualscope_task_orchestrator.py`
- `DUALSCOPE_TASK_QUEUE.md`
- `outputs/dualscope_task_orchestrator/default/dualscope_next_task_prompt.md`
- `scripts/codex-pr.sh`

## Scope

### In Scope

- Add a local autorun loop CLI.
- Add dry-run and execute modes.
- Set proxy environment for subprocesses.
- Run preflight checks.
- Call PR review orchestrator.
- Call task orchestrator.
- Read generated next-task prompts.
- Optionally call `codex exec`.
- Write run logs, status history, blockers, summary, report, and recommendation artifacts.

### Non-goals

- No automatic merge.
- No force push.
- No branch deletion.
- No remote rewrite.
- No SSH conversion.
- No benchmark truth or gate changes.
- No route_c continuation or `199+` planning.
- No default execute-mode run during this task.

## CLI design

`scripts/dualscope_autorun_loop.py` supports:

- `--max-iterations`
- `--max-minutes`
- `--queue-file`
- `--output-dir`
- `--task-orchestrator-output-dir`
- `--pr-status-output-dir`
- `--dry-run`
- `--execute`
- `--codex-bin`
- `--stop-on-review-pending`
- `--allow-review-pending-continue`
- `--stop-on-requested-changes`
- `--stop-on-failing-checks`

## Loop logic

Each iteration:

1. Record iteration start.
2. Set proxy environment.
3. Run git / gh / remote preflight.
4. Run PR review orchestrator.
5. Parse PR status artifacts.
6. Stop on requested changes if configured.
7. Stop on failing checks if configured.
8. Stop on review pending if configured.
9. Run task orchestrator.
10. Read `dualscope_next_task_prompt.md`.
11. In dry-run, record the plan and do not execute.
12. In execute mode, call `codex exec`.
13. Re-check git status and PR status after execution.
14. Record iteration artifacts.
15. Decide whether to continue.

## PR review policy

Requested changes and failing checks are hard blockers when their stop flags are enabled. Review pending is configurable. PR statuses are read from the PR review orchestrator artifacts; statuses are never fabricated.

## Task selection policy

Task selection is delegated to `scripts/dualscope_task_orchestrator.py` with `--select-next-task --write-next-prompt`. The autorun loop does not invent a task or skip the queue.

## Codex exec policy

`codex exec` is only called in `--execute` mode. Dry-run mode records command availability and planned command text without executing. A missing or failing `codex exec` stops the loop and writes a failure report.

## Safety rules

The loop never implements auto merge, force push, branch deletion, remote rewrite, SSH conversion, benchmark truth edits, gate edits, or route_c continuation.

## Artifacts

Default output directory:

- `outputs/dualscope_autorun_loop/default`

Required artifacts:

- `dualscope_autorun_loop_config.json`
- `dualscope_autorun_loop_preflight.json`
- `dualscope_autorun_loop_iterations.jsonl`
- `dualscope_autorun_loop_selected_tasks.jsonl`
- `dualscope_autorun_loop_codex_exec_results.jsonl`
- `dualscope_autorun_loop_pr_status_history.jsonl`
- `dualscope_autorun_loop_blockers.json`
- `dualscope_autorun_loop_summary.json`
- `dualscope_autorun_loop_report.md`
- `dualscope_autorun_loop_next_recommendation.json`
- `dualscope_autorun_loop_dry_run_plan.md` in dry-run mode
- `dualscope_autorun_loop_codex_failure_report.md` on codex exec failure

## Risks

- The loop can only be fully validated if `gh`, HTTPS remote access, PR review orchestration, task orchestration, and the `codex` binary are available.
- Execute mode can start long-running work; this task validates dry-run only.
- The current branch includes unmerged PR review / task orchestrator dependencies because local `main` has not yet absorbed those PRs.

## Milestones

- [x] M1: autorun loop scope and CLI contract frozen
- [x] M2: autorun loop implementation, dry-run, artifacts, docs completed
- [x] M3: single verdict and single recommendation completed

## Exit criteria

The task is complete when:

- `scripts/dualscope_autorun_loop.py` exists.
- The helper module compiles if present.
- `--help` works.
- Dry-run with one iteration writes all required artifacts.
- The final verdict is one of `Autorun loop validated`, `Partially validated`, or `Not validated`.
