# DualScope High-Intensity Codex Skill

This project-local skill pack removes the need to paste the same long DualScope automation prompt for every task. It centralizes reasoning effort selection, safety boundaries, common task profiles, and wrapper invocation for `TriScope-LLM` / `DualScope-LLM`.

## Files

- `.codex/skills/dualscope-high-intensity/SKILL.md`
- `configs/dualscope_codex_task_profiles.json`
- `scripts/codex_dualscope_skill.sh`

## Reasoning Effort

Use only:

```bash
-c model_reasoning_effort="medium"
-c model_reasoning_effort="high"
-c model_reasoning_effort="xhigh"
```

Do not use:

```bash
--reasoning-effort
-c reasoning_effort="high"
```

The current Codex CLI does not support `--reasoning-effort`, and `-c reasoning_effort="high"` can leave the run header at `reasoning effort: none`.

## Profile Selection

Use `medium` profiles for status and documentation:

- `status`

Use `high` profiles for normal engineering execution:

- `long-autorun`
- `dataset-materialization`
- `response-generation`
- `metric-computation`
- `result-package`

Use `xhigh` profiles for complex root-cause, gate, runner, and paper-method work:

- `root-cause`
- `safe-merge-gate`
- `execution-gate`
- `task-orchestrator`
- `worktree-runner`
- `external-gpu`
- `paper-method`
- `paper-writing`

Long autorun defaults to `high`. Do not default long autorun to `xhigh`; reserve `xhigh` for complex blocker analysis, gate design, orchestrator loops, worktree runner failures, external GPU runner design, paper method, and experiment design.

## Usage

General form:

```bash
scripts/codex_dualscope_skill.sh <profile> "<task prompt>"
```

Dry-run form:

```bash
scripts/codex_dualscope_skill.sh --dry-run <profile> "<task prompt>"
```

The wrapper automatically prepends:

- `AGENTS.md`
- `PLANS.md`
- `DUALSCOPE_MASTER_PLAN.md`
- `DUALSCOPE_TASK_QUEUE.md`
- `docs/codex_smart_exec_usage.md`
- `.codex/skills/dualscope-high-intensity/SKILL.md`

It writes logs to:

```text
logs/codex_dualscope_skill_<profile>_<timestamp>.log
```

## Examples

Long autorun:

```bash
scripts/codex_dualscope_skill.sh long-autorun "继续推进 DualScope SCI3 实验，最多 6 小时。"
```

Safe merge gate repair:

```bash
scripts/codex_dualscope_skill.sh safe-merge-gate "修复 PR #107 的 AdvBench small-slice allowlist blocker。"
```

Root-cause diagnosis:

```bash
scripts/codex_dualscope_skill.sh root-cause "诊断为什么 orchestrator 仍选择 download-repair。"
```

Paper method work:

```bash
scripts/codex_dualscope_skill.sh paper-method "更新 DualScope 论文方法章节。"
```

## Safety Boundaries

Every profile inherits these project rules:

- Do not handle PR #14.
- Do not merge unrelated historical PRs.
- Do not force push.
- Do not delete branches.
- Do not run `git reset --hard`.
- Do not switch remotes to SSH.
- Do not modify benchmark truth.
- Do not change gate semantics except narrow allowlist or diagnostics false-positive fixes.
- Do not continue old route_c work.
- Do not generate `199+`.
- Do not fabricate Qwen2.5-7B responses.
- Do not treat blocked rows as real `model_response` values.
- Do not fabricate logprobs.
- Do not fabricate AUROC, F1, ASR, or clean utility.
- Do not present projected or placeholder metrics as real performance.
- Do not present 1.5B as the SCI3 main model.
- Do not touch `/mnt/sda3/CoCoNut-Artifact`.
- Do not download 7B models under `/home/lh`.
- Do not directly run a full matrix.
- Do not full finetune.
- Do not run LoRA or QLoRA unless a later task explicitly authorizes it.
- Do not bypass GPU/CUDA blockers.
- Do not bypass gated dataset permissions.
- Do not fabricate AdvBench or JBB data.

Stop and report if there are requested changes, failing checks, benchmark truth risk, gate semantic risk, secrets or credentials, or non-auto-fixable GPU, OOM, gated model, persistent network, or data permission blockers.

## Long Autorun Command Template

The `long-autorun` profile includes:

```bash
.venv/bin/python scripts/dualscope_autorun_loop.py \
  --execute \
  --use-worktrees \
  --enable-safe-auto-merge \
  --safe-merge-current-task-pr \
  --allow-auto-merge-without-review \
  --max-iterations 30 \
  --max-minutes 360 \
  --allow-review-pending-continue \
  --stop-on-requested-changes \
  --stop-on-failing-checks \
  --codex-extra-args "--cd {worktree_path} --full-auto --model gpt-5.5 -c model_reasoning_effort=\"high\"" \
  --output-dir outputs/dualscope_autorun_loop/default
```

Response-generation tasks must not repeatedly run inside a CUDA-invisible Codex sandbox. Use the `external-gpu` profile when real Qwen2.5-7B generation must move to a host GPU-visible shell.
