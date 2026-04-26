# DualScope Qwen2.5-7B Metric Repair Dependency Routing

## Goal

Stop repeated metric repair packaging by ensuring Qwen2.5-7B metric repair worktrees receive the real ignored artifacts they need, then persist a truthful repair verdict that routes to the first-slice result package when detection metrics and ASR are real and clean utility is explicitly blocked.

## Scope

- Extend worktree dependency materialization for Qwen2.5-7B response, metric, and result-package tasks.
- Copy lightweight required output directories into task worktrees before Codex execution.
- Preserve the hard constraints: no benchmark truth changes, no gate changes, no route_c/199+, no fake responses, no fake logprobs, no fake metrics.
- Do not run a full matrix or train models.

## Validation

- Run py_compile for modified Python files.
- Run the metric computation repair CLI against the existing real first-slice artifacts.
- Confirm the tracked verdict registry records `Qwen2.5-7B metric computation repair validated` only when detection metrics and ASR are reportable and clean utility is explicitly blocked.
- Run task orchestrator dry-run and confirm the next task advances to `dualscope-qwen2p5-7b-first-slice-result-package`.

## Progress

- [x] Diagnosed skipped worktree dependency materialization for metric repair tasks.
- [x] Added Qwen2.5-7B metric/result package output dependencies to worktree materialization.
- [x] Regenerate metric repair artifacts and tracked verdict registry.
- [x] Run validation commands.
- [ ] Create PR and trigger Codex review.
