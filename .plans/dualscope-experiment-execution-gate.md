# DualScope Experiment Execution Gate

## Purpose / Big Picture

DualScope SCI3 autorun can already create task worktrees, open PRs, trigger review, and safe-merge current task PRs. The remaining failure mode is that execution tasks can be packaged as plans, docs, or verdict registry changes without proving that the required experiment CLI actually ran. This plan adds a hard experiment execution gate so execution-required tasks must either produce real execution artifacts or explicit blocker artifacts before they can be packaged or merged.

## Scope

### In Scope

- Add `scripts/dualscope_experiment_execution_gate.py`.
- Add reusable checks in `src/eval/dualscope_experiment_execution_gate_common.py`.
- Enforce the gate for `dualscope-qwen2p5-7b-response-generation-repair`.
- Integrate the gate into `scripts/dualscope_task_worktree_runner.py` before PR creation.
- Integrate the gate into `scripts/dualscope_safe_pr_merge_gate.py` before merge.
- Update the response-generation repair queue prompt to require CLI execution.

### Out of Scope

- No fake responses, logprobs, labels, or metrics.
- No benchmark truth or gate semantic changes.
- No route_c or 199+ continuation.
- No full matrix execution or training.

## Repository Context

- `scripts/dualscope_task_worktree_runner.py` owns per-task worktree execution and PR packaging.
- `scripts/dualscope_safe_pr_merge_gate.py` owns PR merge checks.
- Qwen2.5-7B repair artifacts live under:
  - `outputs/dualscope_qwen2p5_7b_response_generation_repair/default`
  - `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default`
- Tracked verdict registry lives under `.reports/dualscope_task_verdicts/`.

## Validation

Run:

```bash
python3 -m py_compile scripts/dualscope_experiment_execution_gate.py
python3 -m py_compile src/eval/dualscope_experiment_execution_gate_common.py
python3 -m py_compile scripts/dualscope_safe_pr_merge_gate.py
python3 -m py_compile scripts/dualscope_task_worktree_runner.py
python3 -m py_compile src/eval/dualscope_autorun_loop_common.py
.venv/bin/python scripts/dualscope_experiment_execution_gate.py --help
.venv/bin/python scripts/dualscope_experiment_execution_gate.py \
  --task-id dualscope-qwen2p5-7b-response-generation-repair \
  --worktree-dir /home/lh/TriScope-LLM \
  --output-dir outputs/dualscope_experiment_execution_gate/default
```

## Progress

- [x] Implemented execution gate CLI and common checks.
- [x] Integrated worktree runner pre-PR enforcement.
- [x] Integrated safe merge gate pre-merge enforcement.
- [x] Updated response-generation repair queue prompt.

