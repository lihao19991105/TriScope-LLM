# DualScope Experiment Execution Gate

The experiment execution gate prevents SCI3 execution tasks from being merged as plan-only, docs-only, or registry-only packages.

## Enforced Task

The enforced response-generation tasks are:

- `dualscope-qwen2p5-7b-response-generation-repair`
- `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation`
- `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair`

These tasks are execution-required. They must either produce real response rows or explicit blocker artifacts. Blocked row ledgers do not count as successful response evidence unless they contain non-empty real model response fields.

## Required Evidence

Passing response evidence:

- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_responses.jsonl` with at least one row, or
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default/qwen2p5_7b_first_slice_responses.jsonl` with at least one row, or
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default/dualscope_qwen2p5_7b_first_slice_response_generation_rows.jsonl` with at least one row.

Passing blocker evidence:

- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/response_generation_repair_blockers.json`, or
- `outputs/dualscope_qwen2p5_7b_response_generation_repair/default/qwen2p5_7b_blocker.json`.

The blocker must expose a clear blocker type such as `oom`, `model_load_failure`, `cuda_error`, `missing_dependency`, `logprob_unavailable`, `missing_input`, or `runtime_error`.

Additional accepted blocker types for local Qwen2.5-7B execution include `cuda_unavailable`, `cuda_unavailable_cpu_generation_disabled`, `torch_cuda_unavailable`, and `accelerate_unavailable`.

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
