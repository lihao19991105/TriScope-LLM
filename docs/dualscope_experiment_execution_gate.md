# DualScope Experiment Execution Gate

The experiment execution gate prevents SCI3 execution tasks from being merged as plan-only, docs-only, or registry-only packages.

## Enforced Task

The initial enforced task is:

- `dualscope-qwen2p5-7b-response-generation-repair`

This task is execution-required. It must either produce real response rows or explicit blocker artifacts.

## Required Evidence

Passing response evidence:

- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_responses.jsonl` with at least one row, or
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default/qwen2p5_7b_first_slice_responses.jsonl` with at least one row, or
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default/dualscope_qwen2p5_7b_first_slice_response_generation_rows.jsonl` with at least one row.

Passing blocker evidence:

- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_blockers.json`, or
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/qwen2p5_7b_blocker.json`.

The blocker must expose a clear blocker type such as `oom`, `model_load_failure`, `cuda_error`, `missing_dependency`, `logprob_unavailable`, `missing_input`, or `runtime_error`.

## Integration Points

- `scripts/dualscope_task_worktree_runner.py` runs the gate after `codex exec` and before PR creation. If the gate fails, no task PR is created.
- `scripts/dualscope_safe_pr_merge_gate.py` reads the latest gate decision before merge. If a PR corresponds to an execution-required task and the decision is missing or failed, merge is blocked.

## CLI

```bash
.venv/bin/python scripts/dualscope_experiment_execution_gate.py \
  --task-id dualscope-qwen2p5-7b-response-generation-repair \
  --worktree-dir /home/lh/TriScope-LLM \
  --output-dir outputs/dualscope_experiment_execution_gate/default
```

The gate writes:

- `experiment_execution_gate_decision.json`
- `experiment_execution_gate_required_artifacts.json`
- `experiment_execution_gate_report.md`

