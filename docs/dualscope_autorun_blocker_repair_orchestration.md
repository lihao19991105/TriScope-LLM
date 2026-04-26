# DualScope Autorun Blocker Repair Orchestration

This module upgrades autorun blocker handling from an opaque stop state to a structured repair decision.

## Blocker Classes

- `queue_or_prompt_blocker`: missing direct prompt, queue entry, invalid routing, queue-complete false-negative, or verdict mismatch.
- `artifact_blocker`: missing summary, verdict, recommendation, report, schema, or expected output directory.
- `code_blocker`: py_compile, import, CLI help, missing script, or missing module failures.
- `pr_workflow_blocker`: PR creation, Codex review parsing, safe merge allowlist, existing PR/non-fast-forward, or file-scope false positives.
- `resource_blocker`: disk, model path/cache, tokenizer/config, GPU/CUDA/OOM, or download issues.
- `experiment_blocker`: missing real responses, logprobs, labels, final risk scores, metric readiness, ASR, or utility evidence.
- `safety_blocker`: requested changes, failing checks, benchmark truth/gate risk, route_c/199+, secrets, or credentials.

## Repair Policy

Repair tasks may be generated for queue/prompt, artifact, code, PR workflow, resource, and experiment blockers. Resource and experiment blockers are only partially repairable: autorun may configure paths, retry downloads, run real readiness checks, or generate readiness plans, but it must not fabricate model paths, responses, logprobs, labels, metrics, review, or CI.

Safety blockers remain hard stops. Requested changes and failing checks are never bypassed. Benchmark truth and gate changes are not automatically repaired.

## Artifacts

The standalone CLI writes:

- `dualscope_autorun_blocker_classification.json`
- `dualscope_autorun_blocker_repair_decision.json`
- `dualscope_autorun_generated_repair_task.json`
- `dualscope_autorun_repair_attempts.jsonl`
- `dualscope_autorun_repair_summary.json`
- `dualscope_autorun_repair_report.md`

Autorun summaries add:

- `blocker_class`
- `repairable`
- `repair_task_id`
- `repair_attempt_count`
- `repair_pr_url`
- `return_to_mainline_task`
- `unrepairable_reason`

## CLI

```bash
.venv/bin/python scripts/dualscope_autorun_blocker_repair_orchestrator.py \
  --autorun-summary outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_summary.json \
  --autorun-blockers outputs/dualscope_autorun_loop/default/dualscope_autorun_loop_blockers.json \
  --task-selection outputs/dualscope_task_orchestrator/default/dualscope_next_task_selection.json \
  --output-dir outputs/dualscope_autorun_blocker_repair/default \
  --dry-run
```

Autorun integration:

```bash
.venv/bin/python scripts/dualscope_autorun_loop.py \
  --dry-run \
  --use-worktrees \
  --auto-repair-blockers \
  --max-repair-attempts 2 \
  --max-iterations 1 \
  --codex-extra-args "--cd {worktree_path} --full-auto"
```

## Safety

This module does not enable unsafe merge behavior. It does not alter safe merge gates, does not merge PR #14, does not force push, does not delete branches, does not rewrite remotes, does not change benchmark truth or gates, and does not continue route_c or 199+ chains.
