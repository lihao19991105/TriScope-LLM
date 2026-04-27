# DualScope SCI3 Semantic / Behavior Expansion Track

## Purpose / Big Picture

This plan opens the next bounded SCI3 experiment chain after the Qwen2.5-7B Alpaca main-slice package. The goal is to move beyond planning-only readiness by adding executable tasks for semantic trigger smoke, behavior-shift target smoke, bounded AdvBench/JBB materialization, and expanded result synthesis.

## Scope

### In Scope

- Qwen2.5-7B semantic trigger smoke response generation.
- Semantic trigger smoke metric computation and result package.
- Qwen2.5-7B behavior-shift target smoke response generation.
- Behavior-shift metric computation and result package.
- Bounded AdvBench and JBB small-slice materialization or real blocker artifacts.
- Bounded response-generation plans for materialized AdvBench/JBB slices.
- Expanded SCI3 result synthesis package.

### Out of Scope

- Full matrix execution.
- Full Alpaca / AdvBench / JBB execution.
- Cross-model execution without explicit local resources and license readiness.
- Full finetune, LoRA, QLoRA, or training.
- Any benchmark truth, safe merge gate semantic, route_c, or 199+ expansion.
- Fabricated responses, logprobs, labels, metrics, ASR, or clean utility.

## Repository Context

- `DUALSCOPE_TASK_QUEUE.md` is the source of truth for task selection.
- `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default` contains 16 real bounded Qwen2.5-7B response rows.
- `.reports/dualscope_task_verdicts/` provides tracked task completion evidence.
- External GPU generation is required when `codex exec` cannot see CUDA.

## Execution Plan

1. Add semantic trigger response generation, metric, and result package tasks.
2. Add behavior-shift response generation, metric, and result package tasks.
3. Add AdvBench/JBB small-slice materialization and bounded generation planning tasks.
4. Add expanded SCI3 synthesis package task.
5. Validate that task orchestrator selects `dualscope-qwen2p5-7b-semantic-trigger-smoke-response-generation`.
6. Create and merge the queue-extension PR.
7. Start background autorun with worktrees, safe auto merge, and allow-without-review policy.

## Validation

- `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py`
- `python3 -m json.tool` over the fenced queue JSON via the orchestrator.
- `scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt`
- `git diff --check`

## Safety

Execution-required tasks must create real artifacts or explicit blocker JSON. Plan/docs/registry-only PRs are not acceptable for response generation, metric computation, result package, or dataset materialization tasks.

## Progress

- 2026-04-27: Created plan and appended the next semantic / behavior / dataset materialization task chain.
