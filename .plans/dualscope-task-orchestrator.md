# dualscope-task-orchestrator

## Purpose / Big Picture

This plan adds a local DualScope-LLM task orchestrator so Codex can decide the next project task from a structured queue, existing verdict artifacts, open PR state, and Codex Review / CI status. It supports the current DualScope mainline by keeping the next step focused on illumination + confidence + budget-aware fusion artifacts and first-slice experiment readiness, instead of falling back to historical route_c recursion.

## Scope

### In Scope

- Add a structured DualScope task queue.
- Add a local CLI task orchestrator.
- Scan completed / partial / missing verdict artifacts.
- Read open PR and previous/current PR status.
- Prefer the existing PR review orchestrator when available, with a `gh` fallback.
- Generate the next Codex-ready task prompt.
- Write reproducible status, selection, prompt, summary, and report artifacts.

### Out of Scope

- No benchmark truth changes.
- No gate changes.
- No automatic merge.
- No force push.
- No branch deletion.
- No continuation of route_c `199+` planning.
- No training or full experiment-matrix expansion.

## Repository Context

- `AGENTS.md`, `PLANS.md`, and `DUALSCOPE_MASTER_PLAN.md` define the DualScope mainline and planning discipline.
- `.plans/` stores task-level ExecPlans.
- `scripts/codex-pr.sh` provides the local PR creation / Codex Review trigger workflow.
- `scripts/dualscope_pr_review_orchestrator.py` may exist on branches where PR review orchestration has landed; the new task orchestrator must call it first when present.
- `outputs/` contains ignored local artifacts used for verdict scanning.

This plan does not repurpose historical TriScope / route_c chains as a mainline contribution.

## Deliverables

- `.plans/dualscope-task-orchestrator.md`
- `DUALSCOPE_TASK_QUEUE.md`
- `scripts/dualscope_task_orchestrator.py`
- `docs/dualscope_task_orchestrator.md`
- Optional helper: `src/eval/dualscope_task_orchestrator_common.py`
- Runtime artifacts under `outputs/dualscope_task_orchestrator/default/`

## Progress

- [x] M1: Plan and scope created.
- [x] M2: Task queue and common logic implemented.
- [x] M3: CLI, prompt generation, and docs completed.
- [x] M4: Required tests run and results recorded.
- [ ] M5: Commit, PR creation, Codex Review trigger, and previous PR status check completed.

## Surprises & Discoveries

- The current checkout started on PR #4 branch, while local `main` did not include `scripts/dualscope_pr_review_orchestrator.py`. The new orchestrator therefore keeps the required existing-orchestrator integration conditional and falls back to `gh` when the script is absent.
- The first dry-run correctly selected no new task because the implementation files were still uncommitted and the working tree was dirty. The required artifacts were still written under the default output directory.

## Decision Log

- Use a Markdown task queue with an embedded JSON block. This keeps the queue readable for humans while giving the script a stable structured contract.
- Treat `--dry-run` as "no remote mutation"; local output artifacts are still written because the orchestrator itself is an artifact-producing local tool.
- Do not infer validated tasks from names alone. The scanner reads configured verdict artifacts and matches configured final verdict strings.

## Plan of Work

Create the structured queue first, then implement a small common module for parsing, PR status, working tree checks, artifact scanning, and next-task selection. Add the CLI wrapper and documentation. Validate with `py_compile`, `--help`, and a dry-run selection that writes all required artifacts.

## Concrete Steps

1. Add `DUALSCOPE_TASK_QUEUE.md` with the seven required queue entries and transition rules.
2. Add `src/eval/dualscope_task_orchestrator_common.py`.
3. Add `scripts/dualscope_task_orchestrator.py`.
4. Add `docs/dualscope_task_orchestrator.md`.
5. Run required local checks.
6. Commit, open PR via `scripts/codex-pr.sh`, request `@codex review`, and check PR #4 as previous PR.

## Validation and Acceptance

Acceptance requires:

- `python3 -m py_compile scripts/dualscope_task_orchestrator.py`
- `python3 -m py_compile src/eval/dualscope_task_orchestrator_common.py`
- `scripts/dualscope_task_orchestrator.py --help`
- `scripts/dualscope_task_orchestrator.py --select-next-task --write-next-prompt --dry-run --output-dir outputs/dualscope_task_orchestrator/default`
- All seven required output artifacts are written.

## Idempotence and Recovery

The orchestrator is safe to rerun. It overwrites only its own output artifacts under the selected output directory. It never merges PRs, force pushes, deletes branches, closes PRs, or changes remotes. If PR status cannot be read, it records the failure and still emits local artifacts with an explicit warning.

## Outputs and Artifacts

Default runtime outputs:

- `outputs/dualscope_task_orchestrator/default/dualscope_task_queue_status.json`
- `outputs/dualscope_task_orchestrator/default/dualscope_completed_task_scan.json`
- `outputs/dualscope_task_orchestrator/default/dualscope_open_pr_status.json`
- `outputs/dualscope_task_orchestrator/default/dualscope_next_task_selection.json`
- `outputs/dualscope_task_orchestrator/default/dualscope_next_task_prompt.md`
- `outputs/dualscope_task_orchestrator/default/dualscope_task_orchestrator_summary.json`
- `outputs/dualscope_task_orchestrator/default/dualscope_task_orchestrator_report.md`
