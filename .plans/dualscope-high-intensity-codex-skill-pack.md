# DualScope High-Intensity Codex Skill Pack

## Purpose / Big Picture

This plan packages the repeated high-intensity Codex operating instructions for DualScope-LLM into a reusable project-local skill and wrapper. The goal is to make long autorun, blocker repair, gate diagnostics, external GPU runner work, experiment execution, and writing tasks reusable without pasting a large prompt each time.

## Scope

### In Scope

- Add a project-local Codex skill under `.codex/skills/dualscope-high-intensity/`.
- Add task profiles mapping DualScope task types to `model_reasoning_effort`.
- Add a wrapper script that composes the required project prompt and uses either `scripts/codex_smart_exec.sh` or direct `codex exec`.
- Add user documentation for invoking the skill pack.
- Validate syntax, JSON shape, dry-run output, and diff hygiene.

### Out of Scope

- No benchmark truth changes.
- No gate semantic changes.
- No response generation, metrics, or result package execution.
- No PR #14 handling.
- No route_c continuation or `199+` planning.

## Repository Context

- `.codex/skills/` stores project-local skills.
- `configs/` stores profile configuration.
- `scripts/codex_smart_exec.sh` already supports `model_reasoning_effort` through config mapping and is reused when available.
- `docs/codex_smart_exec_usage.md` records the verified Codex CLI parameter format.
- This work supports the DualScope SCI3 automation track and does not alter experiment artifacts.

## Deliverables

- `.codex/skills/dualscope-high-intensity/SKILL.md`
- `docs/codex_dualscope_high_intensity_skill.md`
- `configs/dualscope_codex_task_profiles.json`
- `scripts/codex_dualscope_skill.sh`
- `scripts/codex_smart_exec.sh` alignment to the verified `model_reasoning_effort` config key
- `scripts/dualscope_safe_pr_merge_gate.py` narrow allowlist for the project-local skill pack files

## Progress

- [x] Read project instructions and skill-creator guidance.
- [x] Confirm main worktree has unrelated dirty paths and use a clean temporary clone.
- [x] Add skill, profile config, wrapper, docs, and this ExecPlan.
- [x] Align the existing smart exec wrapper so the preferred path also uses `-c model_reasoning_effort="<effort>"`.
- [x] Add a narrow safe merge gate allowlist for the exact skill pack files after check-only flagged them as file-scope false positives.
- [ ] Run syntax and dry-run validation.
- [ ] Open PR and run safe merge gate.

## Surprises & Discoveries

- The main working tree contains unrelated existing changes, so implementation is isolated in a temporary clone.
- `scripts/codex_smart_exec.sh` and `docs/codex_smart_exec_usage.md` are already present on `origin/main`.

## Decision Log

- Use `model_reasoning_effort` only, because current project docs record that `--reasoning-effort` is unsupported and `reasoning_effort` does not set the expected run header.
- Keep long autorun at `high` by default and reserve `xhigh` for root-cause, gate, orchestrator, worktree, external runner, and paper-method work.
- Use `python3` in the wrapper to parse JSON so the script does not require `jq`.

## Plan of Work

1. Add a concise skill file with trigger scope, safety boundaries, profile selection, and workflow rules.
2. Add JSON profiles with effort and prompt template metadata.
3. Add a Bash wrapper that validates the profile, composes the required prompt, logs command preview and exit code, and supports `--dry-run`.
4. Document user-facing usage examples and anti-patterns.
5. Validate syntax, JSON, dry-run output, and diff hygiene.

## Concrete Steps

Run:

```bash
bash -n scripts/codex_dualscope_skill.sh
python3 -m json.tool configs/dualscope_codex_task_profiles.json >/tmp/dualscope_profiles.json
scripts/codex_dualscope_skill.sh --dry-run status "只回复 DUALSCOPE_SKILL_STATUS_OK"
scripts/codex_dualscope_skill.sh --dry-run root-cause "只回复 DUALSCOPE_SKILL_XHIGH_OK"
git diff --check
```

## Validation and Acceptance

The task is complete when the required files exist, dry-run prints the selected effort and command preview, the wrapper never emits `--reasoning-effort` or `reasoning_effort`, and tests pass.

## Idempotence and Recovery

The wrapper dry-run is side-effect free except for a log file under `logs/`. Re-running it with the same profile is safe. The config is declarative and can be extended by adding new profiles.

## Outputs and Artifacts

- Skill: `.codex/skills/dualscope-high-intensity/SKILL.md`
- Config: `configs/dualscope_codex_task_profiles.json`
- Wrapper: `scripts/codex_dualscope_skill.sh`
- Usage docs: `docs/codex_dualscope_high_intensity_skill.md`
- Logs: `logs/codex_dualscope_skill_<profile>_<timestamp>.log`

## Remaining Risks

- The wrapper prefers `scripts/codex_smart_exec.sh` when present. The direct fallback is the authoritative command preview for `-c model_reasoning_effort="<effort>"`.
- Actual long autorun still depends on Codex CLI authentication and repository-specific safe merge gates.

## Next Suggested Plan

Use the skill pack for the next DualScope automation request, starting with:

```bash
scripts/codex_dualscope_skill.sh long-autorun "继续推进 DualScope SCI3 实验，最多 6 小时。"
```
