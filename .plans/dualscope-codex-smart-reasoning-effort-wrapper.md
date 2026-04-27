# DualScope Codex Smart Reasoning Effort Wrapper

## Purpose / Big Picture

Add a small Codex execution wrapper that selects reasoning effort from a task type instead of always using the highest effort. This keeps routine DualScope tasks on medium/high while reserving xhigh for root-cause, gate, orchestration, experiment-design, and paper-method work.

## Scope

### In Scope

- Add `scripts/codex_smart_exec.sh`.
- Add configurable task-type to effort mapping at `configs/codex_smart_effort_map.json`.
- Detect current `codex exec --help` support for `--reasoning-effort`.
- Fall back to `-c reasoning_effort=...`, then no effort flag when unsupported.
- Write per-run logs under `logs/`.
- Add minimum safety prompt constraints for autorun, response generation, and metric computation tasks.
- Add safe merge gate allowlist coverage for the new wrapper and config files.

### Out of Scope

- Changing Codex model defaults beyond the wrapper.
- Changing project approval policy, sandbox mode, benchmark truth, experiment gates, or PR #14.
- Running long autorun or model generation as part of this wrapper task.

## Milestones

- [x] Inspect current Codex CLI options.
- [x] Implement wrapper and config map.
- [x] Run syntax and smoke tests.
- [ ] Create PR, trigger review, and run safe merge gate.

## Validation

```bash
bash -n scripts/codex_smart_exec.sh
scripts/codex_smart_exec.sh status "只回复 CODEX_SMART_EXEC_STATUS_OK"
scripts/codex_smart_exec.sh root-cause "只回复 CODEX_SMART_EXEC_XHIGH_OK"
```

## Risks

- The current Codex CLI may not support `--reasoning-effort`; the wrapper must fall back without failing solely because that flag is absent.
- Local `.git` metadata may be read-only, so PR packaging may need the existing GitHub API fallback path.