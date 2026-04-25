# DualScope Autorun Loop

`scripts/dualscope_autorun_loop.py` is a local outer loop around the existing PR review and task orchestrators.

It runs:

1. proxy-aware preflight checks;
2. PR review status checks;
3. task queue selection;
4. next prompt loading;
5. optional `codex exec`;
6. status/artifact logging;
7. stop-condition evaluation.

The loop never auto-merges, force-pushes, deletes branches, rewrites remotes, switches to SSH, changes benchmark truth, changes gates, or continues old route_c / `199+` planning.

## Dry-Run

```bash
.venv/bin/python scripts/dualscope_autorun_loop.py \
  --dry-run \
  --max-iterations 1 \
  --codex-extra-args "--cd /home/lh/TriScope-LLM --full-auto" \
  --output-dir outputs/dualscope_autorun_loop/default
```

Dry-run checks PR state, classifies dirty worktree paths, calls the task orchestrator when safe, reads `dualscope_next_task_prompt.md`, writes a run plan, and does not call `codex exec`. It still writes the final command preview that execute mode would use.

## Execute

```bash
.venv/bin/python scripts/dualscope_autorun_loop.py \
  --execute \
  --max-iterations 2 \
  --max-minutes 120 \
  --allow-review-pending-continue \
  --stop-on-requested-changes \
  --stop-on-failing-checks \
  --codex-extra-args "--cd /home/lh/TriScope-LLM --full-auto" \
  --output-dir outputs/dualscope_autorun_loop/default
```

Execute mode calls:

```bash
codex exec --cd /home/lh/TriScope-LLM --full-auto "<prompt text>"
```

Without `--codex-extra-args`, the compatible default remains:

```bash
codex exec "<prompt text>"
```

If `codex` is unavailable or returns non-zero, the loop stops and writes failure artifacts with exit code, stdout, stderr, command, selected task, and prompt path.

## Main Options

- `--max-iterations`: maximum loop iterations, default `5`.
- `--max-minutes`: wall-clock time budget, default `120`.
- `--queue-file`: default `DUALSCOPE_TASK_QUEUE.md`.
- `--task-orchestrator-output-dir`: default `outputs/dualscope_task_orchestrator/default`.
- `--pr-status-output-dir`: default `outputs/dualscope_pr_review_status/default`.
- `--codex-bin`: default `codex`.
- `--codex-extra-args`: optional string parsed with `shlex.split` and inserted after `codex exec`.
- `--ignore-runtime-dirty-paths` / `--no-ignore-runtime-dirty-paths`: default enabled. Allows task selection to continue only when dirty paths are limited to known runtime artifacts.
- `--stop-on-review-pending`: stop if checked PR review is still pending.
- `--allow-review-pending-continue`: allow continuation when review is pending.
- `--stop-on-requested-changes`: enabled by default.
- `--stop-on-failing-checks`: enabled by default.

## Dirty Worktree Policy

When runtime dirty ignoring is enabled, the loop may continue task selection only if dirty paths are limited to:

- `docs/dualscope_autorun_loop_log.md`
- `outputs/dualscope_autorun_loop/`
- `outputs/dualscope_task_orchestrator/`
- `outputs/dualscope_pr_review_status/`
- `outputs/dualscope_first_slice_real_run_long_compression_status/`
- any `__pycache__`
- any `*.pyc`
- `scripts/codex_exec_full_auto_wrapper.sh` as a legacy temporary wrapper path

The repo-local wrapper path is not required. If it appears, the dirty check reports a warning recommending deletion or moving wrapper usage to `/tmp/codex_exec_full_auto_wrapper.sh`.

The loop does not ignore real business changes under `.plans/`, `src/`, most `scripts/`, most `docs/`, `README.md`, `AGENTS.md`, `PLANS.md`, `DUALSCOPE_MASTER_PLAN.md`, or `DUALSCOPE_TASK_QUEUE.md`.

## Outputs

Default output directory:

`outputs/dualscope_autorun_loop/default`

Required artifacts:

- `dualscope_autorun_loop_config.json`
- `dualscope_autorun_loop_preflight.json`
- `dualscope_autorun_loop_iterations.jsonl`
- `dualscope_autorun_loop_selected_tasks.jsonl`
- `dualscope_autorun_loop_codex_exec_results.jsonl`
- `dualscope_autorun_loop_dirty_worktree_check.json`
- `dualscope_autorun_loop_codex_command_preview.json`
- `dualscope_autorun_loop_pr_status_history.jsonl`
- `dualscope_autorun_loop_blockers.json`
- `dualscope_autorun_loop_summary.json`
- `dualscope_autorun_loop_report.md`
- `dualscope_autorun_loop_execute_hardening_summary.json`
- `dualscope_autorun_loop_execute_hardening_report.md`
- `dualscope_autorun_loop_next_recommendation.json`
- `dualscope_autorun_loop_dry_run_plan.md` in dry-run mode
- `dualscope_autorun_loop_codex_failure_report.md` if `codex exec` fails

The human-readable rolling log is:

`outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_log.md`

The previous docs log path is treated as a runtime artifact for compatibility, but new runs should not write to it.

## Verdicts

- `Autorun execute hardening validated`: script/help/dry-run/execute smoke artifacts pass, command preview is correct, runtime-only dirty paths do not block task selection, `codex` is available, and no safety blockers are present.
- `Partially validated`: code and dry-run are present but an environment blocker remains, such as missing `codex` or PR status access problems.
- `Not validated`: missing script, compile failure, dry-run failure, missing artifacts, or dangerous operations.
