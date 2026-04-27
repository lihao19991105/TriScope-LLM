# DualScope Worktree Runner Codex Environment Propagation Fix

## Purpose / Big Picture

The AdvBench/JBB autorun reached `dualscope-advbench-small-slice-response-generation-plan`, but the worktree runner stopped with `codex_exec_not_passed`. The root cause is that `scripts/dualscope_autorun_loop.py` prepares a writable Codex execution environment, while the worktree-runner subprocess is launched without inheriting that prepared `CODEX_HOME`/`TMPDIR` environment.

This fix propagates the same Codex process environment into the worktree runner so nested `codex exec` calls can create sessions in the writable state directory.

## Scope

### In Scope

- Pass the autorun Codex process environment to `scripts/dualscope_task_worktree_runner.py`.
- Preserve existing proxy, HF cache, CUDA, worktree, safe merge, and dirty-worktree behavior.
- Validate with syntax checks and a bounded autorun rerun.

### Out of Scope

- No benchmark truth, gate semantic, route_c, 199+, dataset, response, or metric changes.
- No fake response generation or fake metric artifacts.
- No PR #14 handling.

## Progress

- [x] Diagnose `codex exec` failure in worktree runner logs.
- [x] Confirm direct `codex exec` succeeds when `CODEX_HOME` and `TMPDIR` are writable.
- [x] Patch autorun worktree-runner invocation to propagate `codex_process_env`.
- [ ] Run syntax and autorun smoke validation.
- [ ] Open, review, safe-merge, and verify the fix PR.
- [ ] Restart long-run autorun after merge.

## Validation

Run:

```bash
python3 -m py_compile src/eval/dualscope_autorun_loop_common.py scripts/dualscope_autorun_loop.py scripts/dualscope_task_worktree_runner.py
git diff --check
```

Acceptance requires the next autorun attempt to invoke the worktree runner with a writable `CODEX_HOME` and proceed past the previous `Failed to create session: Read-only file system` blocker.

