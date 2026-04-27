# DualScope runtime readiness next-task routing fix

## Goal

Prevent the bounded Alpaca main-slice runtime repair chain from repeatedly selecting
`dualscope-qwen2p5-7b-alpaca-main-slice-bounded-response-generation-retry` when the
tracked runtime readiness registry already records a concrete GPU/CUDA blocker and
an explicit `next_task`.

## Scope

- Honor `next_task` from tracked verdict registries for partially validated tasks.
- Preserve the hard safety rule that response-generation tasks cannot be marked
  validated without real response artifacts.
- Correct the bounded response retry registry task id so the task scanner can
  reason about it without a registry mismatch.

## Validation

- `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py`
- `scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt`
- Expected next task after the recorded GPU blocker:
  `dualscope-worktree-gpu-readiness-blocker-closure`.
