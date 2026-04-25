# DualScope SCI3 Experimental Track Upgrade

## Purpose / Big Picture

Upgrade DualScope from a 1.5B-only pilot/debug chain into a SCI 3-zone experimental track. The upgraded track keeps the automation and first-slice discipline, but makes Qwen2.5-7B-Instruct the main experimental model and reserves 1.5B for pilot, debug, automation, and ablation work.

## Scope

### In Scope

- Define the SCI3 model, dataset, trigger, target, baseline, metric, table, ablation, robustness, and 2x3090 resource plan.
- Add queue tasks that start with `dualscope-main-model-axis-upgrade-plan`.
- Keep the next executable step as planning and first-slice Qwen2.5-7B response generation, not a full matrix.

### Out of Scope

- Running the full matrix.
- Claiming Qwen2.5-7B or Llama/Mistral results before artifacts exist.
- Training, full finetune, LoRA, QLoRA, benchmark truth changes, gate changes, route_c continuation, or 199+ planning.

## Repository Context

- `DUALSCOPE_TASK_QUEUE.md` controls task ordering.
- `docs/dualscope_sci3_*.md` define the SCI3 experiment standard.
- Qwen2.5-1.5B-Instruct remains useful for automation smoke, debugging, and ablation, but is no longer the main experimental model.

## Deliverables

- SCI3 docs covering model matrix, metrics/tables, ablation/robustness, and resource plan.
- Queue entries for Qwen2.5-7B first-slice and cross-model validation planning.
- Task orchestrator validation showing `dualscope-main-model-axis-upgrade-plan`.

## Progress

- [x] Read AGENTS.md, PLANS.md, DUALSCOPE_MASTER_PLAN.md, and DUALSCOPE_TASK_QUEUE.md.
- [x] Merge PR #20 after safety checks.
- [x] Add SCI3 docs and queue entries.
- [x] Validate task orchestrator selection.
- [ ] Commit and create SCI3 upgrade PR.

## Surprises & Discoveries

- The task queue now parses with 17 tasks. The first unvalidated SCI3 entry is `dualscope-main-model-axis-upgrade-plan`, and the generated prompt is complete.

## Decision Log

- SCI3 main experiments use Qwen2.5-7B-Instruct as the main model. Qwen2.5-1.5B-Instruct is demoted to pilot/debug/ablation.
- Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 are cross-model validation candidates; missing local resources must be recorded honestly.

## Plan of Work

Update planning docs and queue metadata first, then let autorun execute tasks after the SCI3 PR is reviewed and merged.

## Concrete Steps

1. Add SCI3 docs.
2. Replace the next queue step with `dualscope-main-model-axis-upgrade-plan`.
3. Add the Qwen2.5-7B and cross-model task sequence.
4. Run py_compile and task orchestrator dry-run.
5. Open PR and trigger Codex review.

## Validation and Acceptance

- `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py` passes.
- Task orchestrator selects `dualscope-main-model-axis-upgrade-plan`.
- Prompt explicitly states 1.5B as pilot/ablation, Qwen2.5-7B as main, and Llama/Mistral as cross-model validation.

Validation completed on this branch: py_compile passed, task orchestrator selected `dualscope-main-model-axis-upgrade-plan`, `prompt_available=true`, and the prompt includes the required model roles plus prohibitions on full matrix, benchmark truth changes, gate changes, route_c, 199+, fake metrics, and fake responses.

## Idempotence and Recovery

This upgrade is queue and documentation metadata. If validation fails, fix queue JSON or prompt templates and rerun the orchestrator.

## Outputs and Artifacts

- `outputs/dualscope_task_orchestrator/default/dualscope_next_task_selection.json`
- `outputs/dualscope_task_orchestrator/default/dualscope_next_task_prompt.md`

## Remaining Risks

- Qwen2.5-7B or cross-model weights may not exist locally. The follow-up tasks must record that as `external-resource-required` rather than fabricating availability.

## Next Suggested Plan

Merge this SCI3 upgrade PR, then run autorun with `--use-worktrees` to execute `dualscope-main-model-axis-upgrade-plan`.
