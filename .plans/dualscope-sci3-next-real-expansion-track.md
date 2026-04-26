# DualScope SCI3 Next Real Expansion Track

## Purpose / Big Picture

DualScope SCI3 first-slice Qwen2.5-7B has reached a bounded smoke-result milestone: the resource path is materialized, 8 real responses exist, label-aligned detection metrics and ASR are available for the first slice, clean utility is explicitly blocked, and the task queue is complete. This plan opens the next real expansion track without turning the project into a full matrix run.

The immediate goal is to add a small-step queue that starts with a Qwen2.5-7B Stanford Alpaca main-slice plan and only then advances through one bounded response-generation step, one semantic-trigger smoke plan, one behavior-shift target smoke plan, and dataset readiness plans for AdvBench and JBB-Behaviors.

## Scope

### In Scope

- Add the next small-step SCI3 expansion queue entries.
- Keep Qwen2.5-7B as the main experimental model.
- Preserve Qwen2.5-1.5B as pilot / debug / automation / ablation only.
- State that the current 8-response result is first-slice smoke evidence, not full paper performance.
- Preserve the clean utility blocker unless explicit utility success/reference-match fields exist.
- Keep cross-model validation as readiness only unless model resources and license are available.
- Verify task orchestrator chooses `dualscope-qwen2p5-7b-alpaca-main-slice-plan`.

### Out of Scope

- No full matrix execution.
- No model training, LoRA, QLoRA, or full finetune.
- No new benchmark truth or gate edits.
- No old route_c continuation or 199+ generation.
- No fabricated responses, logprobs, AUROC, F1, ASR, or clean utility.
- No AdvBench or JBB full benchmark execution in this task.

## Repository Context

- Queue source of truth: `DUALSCOPE_TASK_QUEUE.md`
- Master direction: `DUALSCOPE_MASTER_PLAN.md`
- Planning rules: `PLANS.md`
- Scope docs:
  - `docs/dualscope_sci3_next_real_expansion_track.md`
  - `docs/dualscope_sci3_experiment_scope_control.md`
- Completed Qwen2.5-7B first-slice registries live in `.reports/dualscope_task_verdicts/`.

## Deliverables

- Six new task queue entries:
  - `dualscope-qwen2p5-7b-alpaca-main-slice-plan`
  - `dualscope-qwen2p5-7b-alpaca-main-slice-response-generation`
  - `dualscope-qwen2p5-7b-semantic-trigger-smoke-plan`
  - `dualscope-qwen2p5-7b-behavior-shift-target-smoke-plan`
  - `dualscope-advbench-small-slice-readiness-plan`
  - `dualscope-jbb-small-slice-readiness-plan`
- Direct prompts for each task.
- Documentation of scope controls and limitations.
- Orchestrator dry-run showing the next task is `dualscope-qwen2p5-7b-alpaca-main-slice-plan`.

## Progress

- [x] Read repository instructions and current DualScope queue state.
- [x] Add small-step expansion queue entries.
- [x] Add expansion-track and scope-control docs.
- [x] Update master plan and planning notes.
- [ ] Run py_compile for task orchestrator common.
- [ ] Run task orchestrator dry-run and inspect prompt.
- [ ] Create PR and trigger @codex review.

## Surprises & Discoveries

- The queue had already reached `queue_complete` after cross-model readiness repair. The next expansion must therefore be appended as a new batch and connected from the previous validated terminal repair.

## Validation

Run:

```bash
python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py
.venv/bin/python scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt --output-dir outputs/dualscope_task_orchestrator/default
```

Expected:

- `selected_task_id = dualscope-qwen2p5-7b-alpaca-main-slice-plan`
- `prompt_available = true`
- prompt is non-empty
- prompt forbids full matrix and fake metrics

## Risks

- Future execution tasks still need experiment execution gate discipline so they cannot pass with docs/registry only.
- AdvBench and JBB readiness may encounter data/license blockers; those must be explicit blockers, not fabricated availability.
