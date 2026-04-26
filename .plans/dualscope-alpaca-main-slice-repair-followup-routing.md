# DualScope Alpaca Main-Slice Repair Follow-Up Routing

## Goal

Prevent the SCI3 autorun loop from repeatedly selecting `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation-repair` after that repair task has already produced an honest partial verdict.

The current blocker is real and specific: the bounded Qwen2.5-7B Alpaca main-slice repair execution attempted generation, produced no fabricated responses, and recorded a missing runtime dependency for 4-bit loading. The queue should now route to a dependency repair task instead of regenerating the same repair package.

## Scope

- Add repair follow-up routing in the task orchestrator.
- Add a direct queue entry for `dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair`.
- Keep experiment execution gate requirements active for dependency repair.
- Track `bitsandbytes` as the minimal dependency needed for 4-bit loading.
- Preserve the truthful response-generation blocker in the tracked verdict registry.

## Non-Goals

- Do not fabricate Qwen2.5-7B responses, logprobs, metrics, or clean utility.
- Do not run a full matrix.
- Do not modify benchmark truth or gates.
- Do not continue route_c or generate 199+.
- Do not handle PR #14.

## Validation

1. `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py`
2. `python3 -m py_compile src/eval/dualscope_experiment_execution_gate_common.py`
3. `DUALSCOPE_TASK_QUEUE.md` parses through the task orchestrator loader.
4. Task orchestrator dry-run selects `dualscope-qwen2p5-7b-alpaca-main-slice-response-dependency-repair`.

