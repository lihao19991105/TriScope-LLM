#!/usr/bin/env bash
set -Eeuo pipefail

BASE="${BASE:-main}"
REVIEW_PROMPT="${REVIEW_PROMPT:-@codex review}"
STATE_FILE_REL="codex-pr-state.json"

die() {
  printf 'codex-pr: error: %s\n' "$*" >&2
  exit 1
}

info() {
  printf 'codex-pr: %s\n' "$*" >&2
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

json_get() {
  local file="$1"
  local filter="$2"
  if [[ -f "$file" ]]; then
    jq -r "$filter // empty" "$file"
  fi
}

github_repo() {
  gh repo view --json nameWithOwner --jq '.nameWithOwner'
}

check_previous_pr() {
  local state_file="$1"
  if [[ ! -f "$state_file" ]]; then
    info "no previous PR state recorded"
    return 0
  fi

  local previous_pr
  previous_pr="$(json_get "$state_file" '.current_pr_number')"
  if [[ -z "$previous_pr" ]]; then
    info "previous PR state exists but has no current_pr_number"
    return 0
  fi

  info "checking previous PR #${previous_pr}"
  local previous_json
  if ! previous_json="$(gh pr view "$previous_pr" --json number,url,state,reviewDecision,latestReviews,comments,statusCheckRollup 2>/dev/null)"; then
    info "previous PR #${previous_pr} could not be read"
    return 0
  fi

  printf '%s\n' "$previous_json" | jq '{
    number,
    url,
    state,
    reviewDecision,
    latestReviews: [
      .latestReviews[]? | {
        author: .author.login,
        state,
        submittedAt,
        body: (.body // "" | if length > 240 then .[0:240] + "..." else . end)
      }
    ],
    codexReviewComments: [
      .comments[]?
      | select(((.author.login // "") | test("codex"; "i")) or ((.body // "") | test("codex|review"; "i")))
      | {
        author: .author.login,
        createdAt,
        body: (.body // "" | if length > 500 then .[0:500] + "..." else . end)
      }
    ],
    checks: [
      .statusCheckRollup[]?
      | {
        name: (.name // .context // .workflowName // "unknown"),
        status: (.status // "UNKNOWN"),
        conclusion: (.conclusion // "UNKNOWN")
      }
    ]
  }'
}

current_pr_json_for_branch() {
  local branch="$1"
  gh pr view "$branch" --json number,url,state,headRefName,baseRefName 2>/dev/null || true
}

create_or_reuse_pr() {
  local branch="$1"
  local base="$2"
  local pr_json
  pr_json="$(current_pr_json_for_branch "$branch")"
  if [[ -n "$pr_json" ]]; then
    info "reusing existing PR #$(printf '%s\n' "$pr_json" | jq -r '.number')"
    printf '%s\n' "$pr_json"
    return 0
  fi

  info "creating PR for ${branch} -> ${base}"
  gh pr create \
    --base "$base" \
    --head "$branch" \
    --title "$branch" \
    --body "Automated PR created by scripts/codex-pr.sh for branch ${branch}." >/dev/null

  pr_json="$(current_pr_json_for_branch "$branch")"
  [[ -n "$pr_json" ]] || die "PR was created but could not be read back with gh pr view"
  printf '%s\n' "$pr_json"
}

main() {
  require_cmd git
  require_cmd gh
  require_cmd jq

  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "current directory is not inside a Git repository"

  local repo_root
  repo_root="$(git rev-parse --show-toplevel)"
  cd "$repo_root"

  gh auth status >/dev/null 2>&1 || die "GitHub CLI is not authenticated; run: gh auth login"

  local branch
  branch="$(git branch --show-current)"
  [[ -n "$branch" ]] || die "detached HEAD is not supported"
  [[ "$branch" != "main" ]] || die "current branch is main; create/switch to a feature branch first"
  [[ "$branch" != "$BASE" ]] || die "current branch equals BASE (${BASE}); create/switch to a feature branch first"

  if [[ -n "$(git status --porcelain)" ]]; then
    die "working tree has uncommitted changes; commit or stash them before running this script"
  fi

  local state_file
  state_file="$(git rev-parse --git-path "$STATE_FILE_REL")"
  check_previous_pr "$state_file"

  local repo
  repo="$(github_repo)"
  info "repository: ${repo}"
  info "base branch: ${BASE}"
  info "current branch: ${branch}"

  info "pushing current branch"
  git push -u origin "$branch"

  local pr_json
  pr_json="$(create_or_reuse_pr "$branch" "$BASE")"
  local pr_number
  local pr_url
  pr_number="$(printf '%s\n' "$pr_json" | jq -r '.number')"
  pr_url="$(printf '%s\n' "$pr_json" | jq -r '.url')"
  [[ -n "$pr_number" && "$pr_number" != "null" ]] || die "failed to determine current PR number"

  info "recording current PR #${pr_number}"
  jq -n \
    --arg repo "$repo" \
    --arg branch "$branch" \
    --arg base "$BASE" \
    --argjson number "$pr_number" \
    --arg url "$pr_url" \
    --arg prompt "$REVIEW_PROMPT" \
    --arg triggeredAt "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{
      repo: $repo,
      branch: $branch,
      base: $base,
      current_pr_number: $number,
      current_pr_url: $url,
      review_prompt: $prompt,
      last_triggered_at: $triggeredAt
    }' > "$state_file"

  info "triggering Codex review on PR #${pr_number}"
  gh pr comment "$pr_number" --body "$REVIEW_PROMPT"

  info "Codex review requested; not waiting for remote review or CI"
  printf 'PR #%s: %s\n' "$pr_number" "$pr_url"
  printf 'State file: %s\n' "$state_file"
}

main "$@"
