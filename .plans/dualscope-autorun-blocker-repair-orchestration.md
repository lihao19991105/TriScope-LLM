# DualScope Autorun Blocker Repair Orchestration

## Purpose / Big Picture

DualScope autorun can now run tasks in isolated worktrees and safely merge task PRs, but real SCI3 execution still needs a middle layer between "task stopped" and "human intervention". This plan adds that layer: classify blockers, decide whether they are safely repairable, generate a repair task prompt, and preserve hard safety stops for review, CI, benchmark truth, gates, old route_c, 199+, secrets, fake model outputs, and fake metrics.

## Scope

### In Scope

- Add a blocker classifier for queue/prompt, artifact, code, PR workflow, resource, experiment, safety, and unknown blockers.
- Add a repair task generator that creates a repair task id, prompt, expected inputs, expected outputs, verdicts, and return target.
- Add a CLI that writes repair orchestration artifacts under `outputs/dualscope_autorun_blocker_repair/default`.
- Add autorun loop flags and summary fields for blocker repair orchestration.
- Document the repair policy and add a queue entry for the orchestration capability.

### Out of Scope

- Automatically fabricating model responses, labels, logprobs, review state, CI state, or metrics.
- Bypassing requested changes or failing checks.
- Changing benchmark truth or gates.
- Continuing old route_c / 199+ chains.
- Running full matrix experiments.

## Repository Context

- `scripts/dualscope_autorun_loop.py` owns the top-level CLI.
- `src/eval/dualscope_autorun_loop_common.py` owns the loop implementation and artifact writing.
- `scripts/dualscope_autorun_blocker_repair_orchestrator.py` is the standalone classifier/generator entrypoint.
- `src/eval/dualscope_autorun_blocker_classifier.py` and `src/eval/dualscope_autorun_repair_task_generator.py` hold reusable logic.
- `DUALSCOPE_TASK_QUEUE.md` records this automation capability as a queue task.

## Milestones

- [x] Implement blocker classifier.
- [x] Implement repair task generator.
- [x] Add standalone repair orchestrator CLI.
- [x] Add autorun loop CLI flags and summary fields.
- [x] Document safety policy.
- [ ] Run validation and PR workflow.

## Validation

Required commands:

```bash
python3 -m py_compile src/eval/dualscope_autorun_blocker_classifier.py
python3 -m py_compile src/eval/dualscope_autorun_repair_task_generator.py
python3 -m py_compile scripts/dualscope_autorun_blocker_repair_orchestrator.py
python3 -m py_compile scripts/dualscope_autorun_loop.py
python3 -m py_compile src/eval/dualscope_autorun_loop_common.py
.venv/bin/python scripts/dualscope_autorun_blocker_repair_orchestrator.py --help
.venv/bin/python scripts/dualscope_autorun_loop.py --help
.venv/bin/python scripts/dualscope_autorun_loop.py --dry-run --use-worktrees --auto-repair-blockers --max-repair-attempts 2 --max-iterations 1 --codex-extra-args "--cd {worktree_path} --full-auto" --output-dir outputs/dualscope_autorun_loop/default
.venv/bin/python scripts/dualscope_autorun_blocker_repair_orchestrator.py --autorun-summary outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_summary.json --autorun-blockers outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_blockers.json --task-selection outputs/dualscope_task_orchestrator/default/dualscope_next_task_selection.json --output-dir outputs/dualscope_autorun_blocker_repair/default --dry-run
```

## Risks

- Classifier rules are conservative string heuristics; unknown blocker types intentionally stop for manual triage.
- The first integration generates repair artifacts but does not yet recursively execute the generated repair task inside the same process. That keeps this change safe and testable before unattended repair execution is enabled.
- Resource and experiment repair remain partial by design; they can prepare real dependencies but must never claim fake readiness.
