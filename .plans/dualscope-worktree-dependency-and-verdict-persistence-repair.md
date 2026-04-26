# DualScope Worktree Dependency And Verdict Persistence Repair

## Purpose / Big Picture

DualScope SCI3 autorun repeatedly selected `dualscope-qwen2p5-7b-first-slice-response-generation-plan` because task worktrees did not inherit ignored local dependencies and the plan verdict artifacts were generated under ignored `outputs/` paths. This repair makes task worktrees materialize the minimal required local dependencies and adds a tracked lightweight verdict registry that task orchestrator can scan before ignored output artifacts.

## Scope

### In Scope

- Materialize first-slice local data and target-response plan outputs into task worktrees before `codex exec`.
- Create the Qwen2.5-7B symlink in each matching worktree.
- Pass mounted-storage Hugging Face and CUDA environment variables into worktree commands.
- Emit dependency materialization artifacts from the worktree runner.
- Add `.reports/dualscope_task_verdicts/` as tracked lightweight task verdict registry.
- Teach the task orchestrator to scan the registry before ignored output verdicts.
- Add the current Qwen2.5-7B response-generation-plan validated registry entry so the queue advances to response generation.

### Out of Scope

- Generating Qwen2.5-7B responses.
- Extracting logprobs.
- Computing AUROC/F1/ASR/utility.
- Training, LoRA/QLoRA, full matrix, benchmark truth, gate changes, route_c, or 199+.

## Repository Context

- `scripts/dualscope_task_worktree_runner.py` creates worktrees and runs `codex exec`.
- `src/eval/dualscope_task_orchestrator_common.py` scans completion status.
- `DUALSCOPE_TASK_QUEUE.md` owns task prompt text and accepted verdicts.
- `.reports/dualscope_task_verdicts/` stores small tracked verdict JSON records.

## Milestones

- [x] Add dependency materialization to task worktree runner.
- [x] Add materialization artifacts.
- [x] Add verdict registry scan to task orchestrator.
- [x] Add tracked registry entry for the completed plan task.
- [x] Strengthen response generation prompt.
- [ ] Run validation and PR workflow.

## Validation

Required checks:

```bash
python3 -m py_compile scripts/dualscope_task_worktree_runner.py
python3 -m py_compile scripts/dualscope_autorun_loop.py
python3 -m py_compile src/eval/dualscope_autorun_loop_common.py
python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py
.venv/bin/python scripts/dualscope_task_worktree_runner.py --help
.venv/bin/python scripts/dualscope_autorun_loop.py --help
.venv/bin/python scripts/dualscope_task_orchestrator.py --help
.venv/bin/python scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt --output-dir outputs/dualscope_task_orchestrator/default
git diff --check
```

Expected task selection after the registry repair:

```text
selected_task_id = dualscope-qwen2p5-7b-first-slice-response-generation
```

## Risks

- Worktree dependency copying intentionally covers only narrow first-slice/Qwen2.5-7B local dependencies. It does not make arbitrary ignored outputs visible.
- The verdict registry is a small tracked summary. It is not a substitute for full generated outputs and must not be used to fake responses or metrics.
