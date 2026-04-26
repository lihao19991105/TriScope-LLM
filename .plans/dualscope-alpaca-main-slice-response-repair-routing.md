# DualScope Alpaca Main-Slice Response Repair Routing

## Purpose / Big Picture

This plan repairs the SCI3 next-stage Alpaca main-slice route after the bounded Qwen2.5-7B response-generation task honestly produced a CUDA blocker instead of real responses. The task queue selected `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair`, but no direct prompt existed, so autorun tried to execute an incomplete prompt.

The fix keeps the small-step expansion route moving without fabricating responses, logprobs, or metrics.

## Scope

### In Scope

- Add a full direct queue entry for `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair`.
- Route successful Alpaca main-slice response generation into metric computation and result packaging before semantic-trigger planning.
- Add bounded Alpaca main-slice metric-computation and result-package queue tasks.
- Extend the experiment execution gate to cover Alpaca main-slice response generation and its repair path.
- Keep the current tracked response-generation registry honest about the CUDA blocker.

### Out of Scope

- No full Alpaca matrix.
- No semantic trigger execution in this repair.
- No benchmark truth or gate semantic changes.
- No fake model responses, logprobs, AUROC, F1, ASR, or clean utility.

## Repository Context

- `DUALSCOPE_TASK_QUEUE.md` contains the direct task prompts and routing.
- `src/eval/dualscope_experiment_execution_gate_common.py` defines execution-required task evidence.
- `.reports/dualscope_task_verdicts/` stores lightweight tracked verdict registry files.
- `docs/dualscope_experiment_execution_gate.md` documents execution gate coverage.

## Milestones

1. Add repair, metric, and result-package queue entries.
2. Extend execution gate coverage for Alpaca main-slice response generation tasks.
3. Verify orchestrator selects the repair task with a complete prompt.
4. Submit through AGENTS.md PR workflow.

## Progress

- 2026-04-26: Created plan after stopping an incomplete-prompt autorun run.

## Validation

- `python3 -m py_compile src/eval/dualscope_experiment_execution_gate_common.py`
- `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py`
- `.venv/bin/python scripts/dualscope_experiment_execution_gate.py --help`
- `.venv/bin/python scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt --output-dir outputs/dualscope_task_orchestrator/default`
- `git diff --check`

## Risks

- The prior bounded main-slice run recorded `cuda_unavailable_cpu_generation_disabled` despite `nvidia-smi` visibility. The repair prompt must diagnose Python/PyTorch CUDA visibility rather than assuming GPU readiness from `nvidia-smi` alone.
