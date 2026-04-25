# dualscope-github-pr-review-orchestration

## Background

The repository now requires every PR-based Codex coding task to report the current PR URL, test results, whether `@codex review` was triggered, and the previous PR Codex Review / CI status. The existing `scripts/codex-pr.sh` can create or reuse a PR and request Codex review, but there is no local, reusable status orchestrator for checking the current and previous PRs after that handoff.

## Why PR review orchestration is needed

Local Codex CLI work and remote GitHub Codex Review are separate systems. The local agent can implement, test, commit, and create a PR, while the remote reviewer comments asynchronously on GitHub. A small local orchestrator is needed to inspect open PRs, summarize Codex Review and CI state, detect requested changes, and produce artifacts that can be reported without merging, force pushing, deleting branches, or inventing review status.

## Scope

### In Scope

- Add `scripts/dualscope_pr_review_orchestrator.py`.
- Add an optional shared helper under `src/eval/`.
- Add human-facing documentation under `docs/`.
- Emit JSON and Markdown artifacts under `outputs/dualscope_pr_review_status/default`.
- Use `gh` and `gh auth`; do not hand-write GitHub tokens.
- Detect Codex review requests, Codex review presence, requested changes, CI state, and a single recommended next action.

### Non-goals

- No automatic PR merge.
- No force push.
- No branch deletion.
- No remote rewrite or SSH conversion.
- No benchmark truth, gate, dataset, model-axis, budget, trigger-family, or prompt-family changes.
- No old TriScope / route_c recursive mainline continuation and no `199+` stages.

## CLI design

The orchestrator CLI supports:

- `--repo`
- `--pr`
- `--current-pr`
- `--previous-pr`
- `--list-open`
- `--trigger-review`
- `--check-status`
- `--output-dir`
- `--review-body`
- `--fail-on-requested-changes`
- `--fail-on-failing-checks`

The default output directory is `outputs/dualscope_pr_review_status/default`. The default review body is `@codex review`.

## gh dependency

The implementation uses GitHub CLI commands:

- `gh pr list --state open --json number,title,url,headRefName,reviewDecision,statusCheckRollup`
- `gh pr view <PR_NUMBER> --json number,title,url,state,reviewDecision,comments,reviews,statusCheckRollup,headRefName,baseRefName,author`
- `gh pr comment <PR_NUMBER> --body "@codex review"`

If `gh` is unavailable, unauthenticated, or the repository remote is not a GitHub remote, the orchestrator records that state in artifacts and does not trigger review.

## Codex review detection policy

`whether_codex_review_requested` is true if PR comments include `@codex review`, if comments or reviews indicate a Codex review request, or if the orchestrator successfully posts the configured review body in the current run.

`whether_codex_review_present` is true if review authors or bodies contain recognizable Codex markers, or if comments include recognizable Codex Review content. If the evidence is insufficient, the value is `unknown`; it is not fabricated.

Requested changes are counted from reviews with `CHANGES_REQUESTED` plus `reviewDecision == CHANGES_REQUESTED`.

## CI status policy

The orchestrator extracts failed, cancelled, timed out, pending, and successful checks from `statusCheckRollup`. The normalized `ci_state` is one of:

- `success`
- `failing`
- `pending`
- `no_checks`
- `unknown`

## Output artifacts

The orchestrator writes:

- `pr_review_open_prs.json`
- `pr_review_status.json`
- `pr_review_comments_summary.json`
- `pr_review_recommendation.json`
- `pr_review_status_report.md`
- `pr_review_orchestrator_summary.json`
- `pr_review_error.json` when errors occur

## Risks

- GitHub auth, network, or proxy failures can prevent full status validation.
- GitHub CLI JSON fields may evolve; unknown fields must be handled conservatively.
- Codex Review detection is heuristic and must return `unknown` when evidence is ambiguous.
- CI status may be `no_checks` or `unknown` rather than success.

## Milestones

- [x] M1: PR review orchestration scope and CLI contract frozen
- [x] M2: orchestrator implementation, docs, and artifacts completed
- [x] M3: single verdict and single recommendation completed

## Exit criteria

The task is complete when the script, helper, docs, and this plan exist; `py_compile` and `--help` pass; a dry `--list-open` run writes artifacts or records an honest blocker; and the implementation never auto-merges, force pushes, deletes branches, rewrites remotes, switches to SSH, or fabricates Codex Review / CI state.
