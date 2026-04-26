# DualScope Qwen2.5-7B Response Generation Repair Routing Fix

## Purpose / Big Picture

The SCI3 automation has reached the Qwen2.5-7B first-slice response-generation chain, but the queue currently loops on `dualscope-qwen2p5-7b-response-generation-repair` because the repair task lacks a usable direct prompt and its tracked verdict registry contains a stale main-model-axis verdict. This plan fixes the routing and repair entrypoint so autorun can execute the repair honestly in an isolated worktree.

## Scope

### In Scope

- Add a complete direct queue prompt for `dualscope-qwen2p5-7b-response-generation-repair`.
- Correct the tracked verdict registry semantics for the repair task.
- Add a small repair CLI wrapper that attempts a bounded Qwen2.5-7B first-slice generation repair or records a real blocker.
- Harden task-orchestrator verdict registry scanning against registry task mismatches.
- Validate that the next task prompt is available and no longer falls back to a placeholder.

### Out of Scope

- No full matrix execution.
- No training, LoRA, QLoRA, or benchmark truth changes.
- No fabricated responses, logprobs, labels, or metrics.
- No PR #14 handling.

## Repository Context

- Queue source: `DUALSCOPE_TASK_QUEUE.md`
- Completion scan: `src/eval/dualscope_task_orchestrator_common.py`
- Existing first-slice generation implementation: `src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py`
- Tracked verdict registry: `.reports/dualscope_task_verdicts/`

## Progress

- [x] Diagnose stale repair registry and missing direct prompt.
- [x] Patch queue, registry, repair CLI, docs, and orchestrator scan.
- [ ] Run py_compile, task orchestrator dry-run, and `git diff --check`.
- [ ] Submit PR via AGENTS.md workflow and trigger `@codex review`.

## Validation

Run:

```bash
python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py
python3 -m py_compile src/eval/dualscope_qwen2p5_7b_response_generation_repair.py
python3 -m py_compile src/eval/post_dualscope_qwen2p5_7b_response_generation_repair_analysis.py
python3 -m py_compile scripts/build_dualscope_qwen2p5_7b_response_generation_repair.py
python3 -m py_compile scripts/build_post_dualscope_qwen2p5_7b_response_generation_repair_analysis.py
.venv/bin/python scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt --output-dir outputs/dualscope_task_orchestrator/default
git diff --check
```

Expected: selected task remains `dualscope-qwen2p5-7b-response-generation-repair` while response artifacts are still missing, but `prompt_available=true` and the prompt is complete.

## Risks

- GPU memory may still be insufficient during the actual repair execution; the repair CLI must record that as a blocker rather than fabricate responses.
- If logprobs are unavailable, the repair remains `without_logprobs` and metrics remain a later task.
