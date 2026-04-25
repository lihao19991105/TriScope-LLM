# DualScope Task Orchestrator

`scripts/dualscope_task_orchestrator.py` is the local scheduler for the DualScope-LLM mainline. It selects the next task from `DUALSCOPE_TASK_QUEUE.md` by combining:

- queued task order and transition rules;
- local verdict artifacts under `outputs/`;
- open PR status;
- previous/current PR Codex Review and CI state;
- current working-tree cleanliness.

It never merges PRs, force pushes, deletes branches, changes remotes, or edits benchmark truth / gates.

## Default Command

```bash
scripts/dualscope_task_orchestrator.py \
  --select-next-task \
  --write-next-prompt \
  --dry-run \
  --output-dir outputs/dualscope_task_orchestrator/default
```

Default paths:

- queue: `DUALSCOPE_TASK_QUEUE.md`
- outputs: `outputs/dualscope_task_orchestrator/default`

## PR Status Integration

The orchestrator first looks for:

- `scripts/dualscope_pr_review_orchestrator.py`

If that script exists, it is called with `--list-open --check-status` and matching `--previous-pr` / `--current-pr` arguments. If it does not exist or fails, this orchestrator falls back to read-only `gh pr list` and `gh pr view` calls.

The tool only reads PR state. It does not request review, merge, close, push, or delete anything.

## Selection Rules

The selection policy is:

1. Check PR state first.
2. If the previous PR has requested changes, select `repair_previous_pr`.
3. If the previous PR review is pending but there are no requested changes or failing checks, allow queue selection to continue.
4. If the current working tree is not clean, do not select a new queue task.
5. Skip tasks whose configured verdict artifact is validated.
6. If a task is partially validated, select its configured repair/compression next step.
7. If a task is not validated, select its configured blocker-closure next step.
8. Otherwise select the first queue task without a validated verdict artifact.

## Output Artifacts

Each run writes:

- `dualscope_task_queue_status.json`
- `dualscope_completed_task_scan.json`
- `dualscope_open_pr_status.json`
- `dualscope_next_task_selection.json`
- `dualscope_next_task_prompt.md`
- `dualscope_task_orchestrator_summary.json`
- `dualscope_task_orchestrator_report.md`

These files are local generated artifacts under `outputs/` and are safe to overwrite.

## Queue Format

`DUALSCOPE_TASK_QUEUE.md` contains a fenced JSON block with one object per task. Each task must include:

- `task_id`
- `purpose`
- `expected_inputs`
- `expected_outputs`
- `branch_name_suggestion`
- `prompt_template`
- `completion_verdicts`
- `next_task_if_validated`
- `next_task_if_partially_validated`
- `next_task_if_not_validated`

The script also reads the optional `verdict_artifacts` field to find local completion evidence.

## Current Queue

The required queue order is:

1. `dualscope-minimal-first-slice-real-run-compression`
2. `dualscope-first-slice-clean-poisoned-labeled-slice-plan`
3. `dualscope-minimal-first-slice-real-run-rerun-with-labels`
4. `dualscope-first-slice-target-response-generation-plan`
5. `dualscope-first-slice-real-run-artifact-validation`
6. `dualscope-first-slice-result-package`
7. `dualscope-next-experiment-readiness-package`

The current DualScope mainline remains the two-stage illumination + confidence pipeline with budget-aware fusion. The scheduler must not resume old route_c chains by default.
