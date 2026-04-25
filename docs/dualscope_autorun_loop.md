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
  --output-dir outputs/dualscope_autorun_loop/default
```

Dry-run checks PR state, calls the task orchestrator, reads `dualscope_next_task_prompt.md`, writes a run plan, and does not call `codex exec`.

## Execute

```bash
.venv/bin/python scripts/dualscope_autorun_loop.py \
  --execute \
  --max-iterations 2 \
  --max-minutes 120 \
  --output-dir outputs/dualscope_autorun_loop/default
```

Execute mode calls:

```bash
codex exec "<prompt text>"
```

If `codex` is unavailable or returns non-zero, the loop stops and writes a failure report.

## Main Options

- `--max-iterations`: maximum loop iterations, default `5`.
- `--max-minutes`: wall-clock time budget, default `120`.
- `--queue-file`: default `DUALSCOPE_TASK_QUEUE.md`.
- `--task-orchestrator-output-dir`: default `outputs/dualscope_task_orchestrator/default`.
- `--pr-status-output-dir`: default `outputs/dualscope_pr_review_status/default`.
- `--codex-bin`: default `codex`.
- `--stop-on-review-pending`: stop if checked PR review is still pending.
- `--allow-review-pending-continue`: allow continuation when review is pending.
- `--stop-on-requested-changes`: enabled by default.
- `--stop-on-failing-checks`: enabled by default.

## Outputs

Default output directory:

`outputs/dualscope_autorun_loop/default`

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
- `dualscope_autorun_loop_codex_failure_report.md` if `codex exec` fails

The human-readable rolling log is:

`docs/dualscope_autorun_loop_log.md`

## Verdicts

- `Autorun loop validated`: script/help/dry-run/artifacts pass, PR/task orchestrators are callable, next prompt is read, `codex` is available, and no safety blockers are present.
- `Partially validated`: code and dry-run are present but an environment blocker remains, such as missing `codex` or PR status access problems.
- `Not validated`: missing script, compile failure, dry-run failure, missing artifacts, or dangerous operations.
