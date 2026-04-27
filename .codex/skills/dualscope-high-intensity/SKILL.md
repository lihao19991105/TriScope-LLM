---
name: dualscope-high-intensity
description: Use for TriScope-LLM / DualScope-LLM high-intensity Codex work: long autorun, blocker repair, safe merge gate, execution gate, task orchestrator, worktree runner, external GPU runner, dataset materialization, response generation, metric computation, result packaging, and paper method or experiment design.
---

# DualScope High-Intensity

## Project

This skill applies only to the `TriScope-LLM` repository while it is operating as the `DualScope-LLM` mainline project.

Always read and obey:

- `AGENTS.md`
- `PLANS.md`
- `DUALSCOPE_MASTER_PLAN.md`
- `DUALSCOPE_TASK_QUEUE.md`
- `docs/codex_smart_exec_usage.md`

## When To Use

Use this skill for:

- long autorun
- blocker repair
- safe merge gate and diagnostics
- execution gate repair
- task orchestrator routing, `prompt_available=false`, and verdict registry repair
- worktree runner, temp clone, readonly refs, and PR fallback repair
- external GPU runner tasks
- dataset materialization
- response generation
- metric computation
- result package tasks
- paper method, experiment design, and paper-writing tasks

## Reasoning Effort

Use only these Codex CLI forms:

```bash
-c model_reasoning_effort="medium"
-c model_reasoning_effort="high"
-c model_reasoning_effort="xhigh"
```

Never use:

```bash
--reasoning-effort
-c reasoning_effort="high"
```

Profile guidance:

- `medium`: status, progress, docs, prompt, queue-docs, report, small-edit.
- `high`: autorun, pr-workflow, code-fix, cli-fix, artifact-fix, metric-computation, response-generation, dataset-materialization, blocker-repair, safe-merge-check.
- `xhigh`: root-cause, architecture, gate-design, execution-gate, safe-merge-gate, worktree-runner, task-orchestrator, blocker-loop, experiment-design, paper-method, paper-writing, complex-debug.

Long autorun defaults to `high`. Use `xhigh` only for complex root-cause, gate, orchestrator, execution gate, worktree runner, external GPU runner design, paper method, or experiment design.

## Safety Boundaries

Every profile must obey:

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
- Do not run a full matrix directly.
- Do not full finetune.
- Do not run LoRA or QLoRA unless a later task explicitly authorizes it.
- Do not bypass GPU/CUDA blockers.
- Do not bypass gated dataset permissions.
- Do not fabricate AdvBench or JBB data.

Stop and report for:

- requested changes
- failing checks
- benchmark truth risk
- gate semantic risk
- secrets or credentials
- non-auto-fixable GPU, OOM, gated model, persistent network, or data permission blockers

## PR Workflow

For repository changes:

1. Start from clean `main`, or use a temp clone/worktree when the main workspace is dirty.
2. Keep the diff minimal.
3. Run focused tests.
4. Commit with a clear message.
5. Run `./scripts/codex-pr.sh`.
6. Trigger `@codex review`.
7. Run the safe merge gate.
8. Use `--allow-auto-merge-without-review` only when explicitly authorized.
9. Do not touch PR #14.

## Task Profiles

Prefer the wrapper:

```bash
scripts/codex_dualscope_skill.sh <profile> "<task prompt>"
```

Common profiles:

- `status`: inspect progress, open PRs, next task, blockers, and worktree state.
- `long-autorun`: run the long DualScope autorun command from clean main.
- `root-cause`: diagnose complex blocker loops.
- `safe-merge-gate`: repair allowlist or diagnostics false positives.
- `execution-gate`: enforce real execution artifacts or explicit blockers.
- `task-orchestrator`: repair queue routing, prompt availability, verdict registry, and next-task selection.
- `worktree-runner`: repair worktree dependency, readonly refs, temp clone, and PR fallback paths.
- `external-gpu`: move real Qwen2.5-7B generation to a host GPU-visible runner.
- `dataset-materialization`: materialize bounded AdvBench/JBB slices with schema and provenance checks.
- `response-generation`: generate bounded real responses or explicit blockers.
- `metric-computation`: compute only real available metrics and blocked metric status.
- `result-package`: package real results, limitations, and next steps.
- `paper-method`: design methodology, threat model, ablations, and experiment matrix.
- `paper-writing`: draft or revise paper text with honest result boundaries.

## Reporting

For engineering tasks report:

1. What changed.
2. Tests run.
3. PR URL and merge status.
4. Blockers and whether they are auto-fixable.
5. Whether PR #14 stayed untouched.
6. Current SCI3 position.
7. One next recommendation.

For experiment tasks also report row counts, generated response counts, metric availability, blocked metrics, and whether anything was fabricated. The answer for fabrication must be explicit.
