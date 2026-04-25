# DualScope GitHub PR Review Workflow

This document describes how local Codex CLI work should coordinate with remote Codex Review on GitHub PRs.

## Local Codex CLI vs remote Codex Review

Local Codex CLI is the coding agent running in this repository. It edits files, runs tests, commits changes, and creates PRs through the repository workflow.

Remote Codex Review is the GitHub-side reviewer triggered by a PR event or by a PR comment such as `@codex review`. It may comment asynchronously after the local task has already moved on.

These are separate systems. The local agent must not claim a remote review exists until GitHub comments or reviews provide evidence.

## Why use the PR pipeline

The PR pipeline keeps local edits, tests, remote review, and CI checks auditable. It also lets local Codex continue with the next task while the previous PR waits for Codex Review or CI.

The intended flow is:

1. Local Codex does the task.
2. Local Codex creates a branch from `main`.
3. Local Codex commits the change.
4. Local Codex executes `./scripts/codex-pr.sh`.
5. `@codex review` is requested on the current PR.
6. Local Codex can continue to the next task.
7. The orchestrator checks the previous PR.
8. If requested changes exist, local Codex returns to repair that PR.

## Trigger Codex Review

Use GitHub CLI:

```bash
gh pr comment <PR_NUMBER> --body "@codex review"
```

The local orchestrator can also trigger review:

```bash
scripts/dualscope_pr_review_orchestrator.py \
  --pr <PR_NUMBER> \
  --trigger-review \
  --output-dir outputs/dualscope_pr_review_status/default
```

## Check the current PR

```bash
scripts/dualscope_pr_review_orchestrator.py \
  --pr <PR_NUMBER> \
  --check-status \
  --output-dir outputs/dualscope_pr_review_status/default
```

The same command can check current and previous PRs:

```bash
scripts/dualscope_pr_review_orchestrator.py \
  --current-pr <CURRENT_PR_NUMBER> \
  --previous-pr <PREVIOUS_PR_NUMBER> \
  --check-status \
  --output-dir outputs/dualscope_pr_review_status/default
```

## Trigger and check

```bash
scripts/dualscope_pr_review_orchestrator.py \
  --pr <PR_NUMBER> \
  --trigger-review \
  --check-status \
  --output-dir outputs/dualscope_pr_review_status/default
```

## List open PRs

```bash
scripts/dualscope_pr_review_orchestrator.py \
  --list-open \
  --output-dir outputs/dualscope_pr_review_status/default
```

## Output artifacts

The default output directory is:

```text
outputs/dualscope_pr_review_status/default
```

The orchestrator writes:

- `pr_review_open_prs.json`
- `pr_review_status.json`
- `pr_review_comments_summary.json`
- `pr_review_recommendation.json`
- `pr_review_status_report.md`
- `pr_review_orchestrator_summary.json`
- `pr_review_error.json` when an error or environment blocker is encountered

## What the script will not do

The orchestrator will not:

- merge PRs
- force push
- delete branches
- auto-close PRs
- rewrite remotes
- switch remotes to SSH
- fabricate Codex Review status
- fabricate CI status

## Authentication

The orchestrator uses GitHub CLI and `gh auth`. It does not write or accept raw GitHub tokens.

If `gh` is not logged in, run:

```bash
gh auth login
```

Then rerun the orchestrator.
