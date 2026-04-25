"""Shared helpers for DualScope GitHub PR review orchestration."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_pr_review_status/default")
DEFAULT_REVIEW_BODY = "@codex review"

LIST_PR_FIELDS = "number,title,url,headRefName,reviewDecision,statusCheckRollup"
DETAIL_PR_FIELDS = (
    "number,title,url,state,reviewDecision,comments,reviews,statusCheckRollup,headRefName,baseRefName,author"
)

FINAL_VERDICTS = {
    "validated": "PR review orchestration validated",
    "partial": "Partially validated",
    "not_validated": "Not validated",
}

FAIL_CONCLUSIONS = {"FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"}
SUCCESS_CONCLUSIONS = {"SUCCESS", "NEUTRAL", "SKIPPED"}
PENDING_STATUSES = {"QUEUED", "IN_PROGRESS", "PENDING", "REQUESTED", "WAITING", "EXPECTED"}


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class OrchestratorArgs:
    repo: str | None
    pr: int | None
    current_pr: int | None
    previous_pr: int | None
    list_open: bool
    trigger_review: bool
    check_status: bool
    output_dir: Path
    review_body: str
    fail_on_requested_changes: bool
    fail_on_failing_checks: bool


@dataclass
class RuntimeState:
    started_at: str
    output_dir: Path
    gh_available: bool = False
    gh_authenticated: bool = False
    github_remote_detected: bool = False
    remote_url: str | None = None
    remote_protocol: str | None = None
    repo: str | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def truncate_text(value: str | None, limit: int = 500) -> str:
    if not value:
        return ""
    value = str(value)
    if len(value) <= limit:
        return value
    return value[:limit] + "..."


def proxy_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("HTTP_PROXY", "http://127.0.0.1:18080")
    env.setdefault("HTTPS_PROXY", "http://127.0.0.1:18080")
    env.setdefault("ALL_PROXY", "http://127.0.0.1:18080")
    return env


def run_command(command: list[str], timeout: int = 60) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=proxy_env(),
        )
        return CommandResult(command=command, returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
    except FileNotFoundError as exc:
        return CommandResult(command=command, returncode=127, stderr=str(exc))
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            command=command,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or f"Command timed out after {timeout}s.",
        )


def json_from_gh(result: CommandResult) -> Any:
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Command failed: {' '.join(result.command)}")
    try:
        return json.loads(result.stdout or "null")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse gh JSON: {exc}") from exc


def detect_remote_protocol(remote_url: str) -> str:
    if remote_url.startswith("https://"):
        return "https"
    if remote_url.startswith("git@"):
        return "ssh"
    if remote_url.startswith("http://"):
        return "http"
    return "unknown"


def repo_from_remote_url(remote_url: str) -> str | None:
    patterns = [
        r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"^http://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
        r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, remote_url)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return None


def initialize_runtime(args: OrchestratorArgs) -> RuntimeState:
    state = RuntimeState(started_at=utc_now(), output_dir=args.output_dir)
    state.gh_available = shutil.which("gh") is not None
    if not state.gh_available:
        state.errors.append({"kind": "gh_unavailable", "message": "GitHub CLI `gh` is not available on PATH."})
        return state

    remote_result = run_command(["git", "remote", "get-url", "origin"])
    if remote_result.returncode == 0:
        state.remote_url = remote_result.stdout.strip()
        state.remote_protocol = detect_remote_protocol(state.remote_url)
        inferred_repo = repo_from_remote_url(state.remote_url)
        state.github_remote_detected = inferred_repo is not None and state.remote_protocol == "https"
        state.repo = args.repo or inferred_repo
    else:
        state.errors.append(
            {
                "kind": "remote_read_failed",
                "message": remote_result.stderr.strip() or "Failed to read git remote origin.",
                "command": remote_result.command,
            }
        )
        state.repo = args.repo

    if args.repo:
        state.repo = args.repo
        state.github_remote_detected = True

    if not state.github_remote_detected:
        state.errors.append(
            {
                "kind": "remote_not_github",
                "message": "Current origin remote is not a recognized GitHub HTTPS remote; not changing remote.",
                "remote_url": state.remote_url,
            }
        )

    auth_result = run_command(["gh", "auth", "status"])
    state.gh_authenticated = auth_result.returncode == 0
    if not state.gh_authenticated:
        state.errors.append(
            {
                "kind": "gh_auth_required",
                "message": "GitHub CLI is not authenticated. Run: gh auth login",
                "stderr": truncate_text(auth_result.stderr, 1000),
            }
        )

    return state


def gh_base_args(repo: str | None) -> list[str]:
    if repo:
        return ["-R", repo]
    return []


def gh_pr_list(repo: str | None) -> list[dict[str, Any]]:
    command = ["gh", "pr", "list", *gh_base_args(repo), "--state", "open", "--json", LIST_PR_FIELDS]
    payload = json_from_gh(run_command(command))
    return payload if isinstance(payload, list) else []


def gh_pr_view(repo: str | None, pr_number: int) -> dict[str, Any]:
    command = ["gh", "pr", "view", str(pr_number), *gh_base_args(repo), "--json", DETAIL_PR_FIELDS]
    payload = json_from_gh(run_command(command))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object for PR #{pr_number}.")
    return payload


def gh_pr_comment(repo: str | None, pr_number: int, body: str) -> CommandResult:
    return run_command(["gh", "pr", "comment", str(pr_number), *gh_base_args(repo), "--body", body])


def actor_login(item: dict[str, Any]) -> str:
    author = item.get("author")
    if isinstance(author, dict):
        return str(author.get("login") or "")
    return ""


def body_text(item: dict[str, Any]) -> str:
    return str(item.get("body") or "")


def is_codex_actor_or_body(author: str, body: str) -> bool:
    marker = f"{author}\n{body}".lower()
    return any(token in marker for token in ["chatgpt-codex", "openai-codex", "codex review", "codex-review"])


def is_review_request_text(body: str) -> bool:
    text = body.lower()
    return "@codex review" in text or "codex review request" in text


def summarize_discussion(pr_detail: dict[str, Any], triggered_this_run: bool) -> dict[str, Any]:
    comments = pr_detail.get("comments") if isinstance(pr_detail.get("comments"), list) else []
    reviews = pr_detail.get("reviews") if isinstance(pr_detail.get("reviews"), list) else []

    comment_rows = []
    review_rows = []
    requested = triggered_this_run
    codex_present = False
    codex_evidence: list[dict[str, Any]] = []

    for comment in comments:
        if not isinstance(comment, dict):
            continue
        author = actor_login(comment)
        body = body_text(comment)
        is_request = is_review_request_text(body)
        is_codex_review = is_codex_actor_or_body(author, body) and not is_request
        requested = requested or is_request
        codex_present = codex_present or is_codex_review
        row = {
            "id": comment.get("id"),
            "author": author,
            "createdAt": comment.get("createdAt"),
            "is_codex_review_request": is_request,
            "is_codex_review_evidence": is_codex_review,
            "body_excerpt": truncate_text(body),
        }
        if is_request or is_codex_review:
            codex_evidence.append(row)
        comment_rows.append(row)

    requested_changes_reviews = 0
    approved_reviews = 0
    for review in reviews:
        if not isinstance(review, dict):
            continue
        author = actor_login(review)
        body = body_text(review)
        state = str(review.get("state") or "").upper()
        is_request = is_review_request_text(body)
        is_codex_review = is_codex_actor_or_body(author, body)
        requested = requested or is_request
        codex_present = codex_present or is_codex_review
        if state == "CHANGES_REQUESTED":
            requested_changes_reviews += 1
        if state == "APPROVED":
            approved_reviews += 1
        row = {
            "author": author,
            "state": state or None,
            "submittedAt": review.get("submittedAt"),
            "is_codex_review_request": is_request,
            "is_codex_review_evidence": is_codex_review,
            "body_excerpt": truncate_text(body),
        }
        if is_request or is_codex_review:
            codex_evidence.append(row)
        review_rows.append(row)

    review_decision = str(pr_detail.get("reviewDecision") or "").upper()
    requested_changes_count = requested_changes_reviews + (1 if review_decision == "CHANGES_REQUESTED" else 0)
    whether_codex_review_present: bool | str = True if codex_present else "unknown"

    return {
        "pr_number": pr_detail.get("number"),
        "comments": comment_rows,
        "reviews": review_rows,
        "whether_codex_review_requested": requested,
        "whether_codex_review_present": whether_codex_review_present,
        "codex_evidence": codex_evidence,
        "requested_changes_count": requested_changes_count,
        "approved_reviews_count": approved_reviews,
        "unresolved_comment_count": None,
    }


def check_name(check: dict[str, Any]) -> str:
    for key in ("name", "context", "workflowName"):
        value = check.get(key)
        if value:
            return str(value)
    return "unknown"


def normalize_ci(status_rollup: Any) -> dict[str, Any]:
    if not isinstance(status_rollup, list):
        return {"ci_state": "unknown", "checks": [], "failing_checks": [], "pending_checks": []}
    if not status_rollup:
        return {"ci_state": "no_checks", "checks": [], "failing_checks": [], "pending_checks": []}

    checks = []
    failing = []
    pending = []
    unknown = []
    for check in status_rollup:
        if not isinstance(check, dict):
            unknown.append({"name": "unknown", "status": None, "conclusion": None})
            continue
        status = str(check.get("status") or "").upper()
        conclusion = str(check.get("conclusion") or "").upper()
        row = {
            "name": check_name(check),
            "status": status or None,
            "conclusion": conclusion or None,
            "detailsUrl": check.get("detailsUrl") or check.get("targetUrl"),
        }
        checks.append(row)
        if conclusion in FAIL_CONCLUSIONS:
            failing.append(row)
        elif not conclusion and status in PENDING_STATUSES:
            pending.append(row)
        elif conclusion and conclusion not in SUCCESS_CONCLUSIONS:
            unknown.append(row)
        elif not conclusion and status not in {"COMPLETED", "SUCCESS"}:
            pending.append(row)

    if failing:
        ci_state = "failing"
    elif pending:
        ci_state = "pending"
    elif unknown:
        ci_state = "unknown"
    else:
        ci_state = "success"

    return {"ci_state": ci_state, "checks": checks, "failing_checks": failing, "pending_checks": pending}


def normalize_review_state(summary: dict[str, Any], pr_detail: dict[str, Any]) -> str:
    review_decision = str(pr_detail.get("reviewDecision") or "").upper()
    if summary["requested_changes_count"] > 0:
        return "changes_requested"
    if review_decision == "APPROVED":
        return "approved"
    if summary["whether_codex_review_present"] is True:
        return "codex_review_present"
    if summary["whether_codex_review_requested"]:
        return "codex_review_requested_waiting"
    if review_decision in {"REVIEW_REQUIRED", "REVIEW_PENDING"}:
        return "review_pending"
    if not summary["whether_codex_review_requested"]:
        return "no_review_requested"
    return "unknown"


def status_from_detail(pr_detail: dict[str, Any], role: str, triggered_this_run: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    discussion = summarize_discussion(pr_detail, triggered_this_run=triggered_this_run)
    ci = normalize_ci(pr_detail.get("statusCheckRollup"))
    review_state = normalize_review_state(discussion, pr_detail)
    status = {
        "role": role,
        "number": pr_detail.get("number"),
        "title": pr_detail.get("title"),
        "url": pr_detail.get("url"),
        "state": pr_detail.get("state"),
        "headRefName": pr_detail.get("headRefName"),
        "baseRefName": pr_detail.get("baseRefName"),
        "author": actor_login(pr_detail),
        "reviewDecision": pr_detail.get("reviewDecision") or "",
        "review_state": review_state,
        "ci_state": ci["ci_state"],
        "whether_codex_review_requested": discussion["whether_codex_review_requested"],
        "whether_codex_review_present": discussion["whether_codex_review_present"],
        "requested_changes_count": discussion["requested_changes_count"],
        "unresolved_comment_count": discussion["unresolved_comment_count"],
        "failing_checks": ci["failing_checks"],
        "pending_checks": ci["pending_checks"],
        "checks": ci["checks"],
    }
    return status, discussion


def choose_recommendation(
    state: RuntimeState,
    open_prs: list[dict[str, Any]],
    statuses: list[dict[str, Any]],
    trigger_requested: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    if not state.gh_available:
        return {
            "recommended_next_action": "gh_unavailable",
            "reason": "GitHub CLI `gh` is unavailable.",
            "blockers": ["Install GitHub CLI."],
        }
    if not state.gh_authenticated:
        return {
            "recommended_next_action": "gh_auth_required",
            "reason": "GitHub CLI is not authenticated.",
            "blockers": ["Run gh auth login."],
        }
    if not state.github_remote_detected:
        return {
            "recommended_next_action": "remote_not_github",
            "reason": "The current origin remote is not a recognized GitHub remote.",
            "blockers": ["Use an existing GitHub HTTPS remote; do not switch to SSH automatically."],
        }
    if not statuses and not open_prs:
        return {
            "recommended_next_action": "no_open_prs",
            "reason": "No open PRs were found and no specific PR status was checked.",
            "blockers": [],
        }

    for status in statuses:
        if status["requested_changes_count"] > 0 or status["review_state"] == "changes_requested":
            blockers.append(f"PR #{status['number']} has requested changes.")
            return {
                "recommended_next_action": "fix_requested_changes",
                "reason": f"PR #{status['number']} has requested changes.",
                "blockers": blockers,
            }
    for status in statuses:
        if status["ci_state"] == "failing":
            checks = ", ".join(check["name"] for check in status["failing_checks"]) or "unknown failing checks"
            blockers.append(f"PR #{status['number']} has failing checks: {checks}.")
            return {
                "recommended_next_action": "fix_failing_checks",
                "reason": f"PR #{status['number']} has failing CI checks.",
                "blockers": blockers,
            }

    primary = statuses[0] if statuses else None
    if primary:
        if not primary["whether_codex_review_requested"] and not trigger_requested:
            return {
                "recommended_next_action": "trigger_codex_review",
                "reason": f"PR #{primary['number']} has no detected Codex review request.",
                "blockers": [],
            }
        if primary["review_state"] == "codex_review_requested_waiting":
            return {
                "recommended_next_action": "wait_for_codex_review",
                "reason": f"PR #{primary['number']} has requested Codex review but no Codex review evidence yet.",
                "blockers": [],
            }
        if primary["ci_state"] == "pending":
            return {
                "recommended_next_action": "wait_for_codex_review",
                "reason": f"PR #{primary['number']} still has pending CI checks.",
                "blockers": [],
            }
        if primary["review_state"] == "approved" and primary["ci_state"] == "success":
            return {
                "recommended_next_action": "ready_for_merge_manual_only",
                "reason": f"PR #{primary['number']} is approved and CI is successful. Merge remains manual only.",
                "blockers": [],
            }
        if primary["whether_codex_review_present"] is True and primary["ci_state"] in {"success", "no_checks"}:
            return {
                "recommended_next_action": "ready_for_human_review",
                "reason": f"PR #{primary['number']} has Codex review evidence and no failing checks.",
                "blockers": [],
            }

    return {
        "recommended_next_action": "unknown_manual_check_required",
        "reason": "The PR state does not match a more specific automated recommendation.",
        "blockers": blockers,
    }


def determine_verdict(state: RuntimeState, statuses: list[dict[str, Any]], artifacts_written: bool) -> str:
    if not artifacts_written or not state.gh_available:
        return FINAL_VERDICTS["not_validated"]
    if not state.gh_authenticated or not state.github_remote_detected:
        return FINAL_VERDICTS["partial"]
    if any(status["whether_codex_review_present"] == "unknown" for status in statuses):
        return FINAL_VERDICTS["partial"]
    return FINAL_VERDICTS["validated"]


def render_report(
    state: RuntimeState,
    open_prs_payload: dict[str, Any],
    status_payload: dict[str, Any],
    recommendation: dict[str, Any],
    verdict: str,
) -> str:
    lines = [
        "# DualScope GitHub PR Review Status",
        "",
        f"- Verdict: {verdict}",
        f"- Recommended next action: {recommendation['recommended_next_action']}",
        f"- Reason: {recommendation['reason']}",
        f"- Repository: {state.repo or 'unknown'}",
        f"- gh available: {state.gh_available}",
        f"- gh authenticated: {state.gh_authenticated}",
        f"- GitHub remote detected: {state.github_remote_detected}",
        "",
        "## Open PRs",
    ]
    open_prs = open_prs_payload.get("open_prs", [])
    if open_prs:
        for pr in open_prs:
            lines.append(f"- PR #{pr.get('number')}: {pr.get('title')} ({pr.get('url')})")
    else:
        lines.append(f"- {open_prs_payload.get('status', 'none')}")

    lines.extend(["", "## Checked PRs"])
    statuses = status_payload.get("checked_prs", [])
    if statuses:
        for status in statuses:
            lines.extend(
                [
                    f"- {status['role']} PR #{status['number']}: {status.get('url')}",
                    f"  - reviewDecision: {status.get('reviewDecision')}",
                    f"  - review_state: {status.get('review_state')}",
                    f"  - Codex review requested: {status.get('whether_codex_review_requested')}",
                    f"  - Codex review present: {status.get('whether_codex_review_present')}",
                    f"  - requested changes: {status.get('requested_changes_count')}",
                    f"  - CI state: {status.get('ci_state')}",
                    f"  - failing checks: {len(status.get('failing_checks') or [])}",
                ]
            )
    else:
        lines.append("- No PR status checks were requested or available.")

    lines.extend(["", "## Blockers"])
    blockers = recommendation.get("blockers") or []
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- None recorded.")

    if state.errors:
        lines.extend(["", "## Environment Errors"])
        for error in state.errors:
            lines.append(f"- {error.get('kind')}: {error.get('message')}")

    lines.append("")
    return "\n".join(lines)


def write_error_artifacts(state: RuntimeState, message: str, kind: str = "runtime_error") -> None:
    payload = {
        "summary_status": "FAIL",
        "schema_version": "dualscope/pr-review-orchestrator/v1",
        "error": {"kind": kind, "message": message},
        "gh_available": state.gh_available,
        "gh_authenticated": state.gh_authenticated,
        "github_remote_detected": state.github_remote_detected,
        "repo": state.repo,
    }
    write_json(state.output_dir / "pr_review_error.json", payload)
    report = "\n".join(
        [
            "# DualScope GitHub PR Review Status",
            "",
            f"- Verdict: {FINAL_VERDICTS['not_validated']}",
            f"- Error: {message}",
            "- Recommended next action: unknown_manual_check_required",
            "",
        ]
    )
    (state.output_dir / "pr_review_status_report.md").write_text(report, encoding="utf-8")


def run_orchestrator(args: OrchestratorArgs) -> tuple[int, dict[str, Any]]:
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    state = initialize_runtime(args)

    open_prs_payload: dict[str, Any] = {"status": "not_requested", "open_prs": []}
    checked_statuses: list[dict[str, Any]] = []
    comment_summaries: list[dict[str, Any]] = []
    trigger_actions: list[dict[str, Any]] = []
    checked_pr_numbers: list[int] = []

    try:
        if args.list_open and state.gh_available and state.gh_authenticated and state.github_remote_detected:
            open_prs = gh_pr_list(state.repo)
            open_prs_payload = {"status": "ok", "open_prs": open_prs}
        elif args.list_open:
            open_prs_payload = {"status": "blocked", "open_prs": [], "errors": state.errors}

        trigger_target = args.pr or args.current_pr
        if args.trigger_review:
            if trigger_target is None:
                raise ValueError("--trigger-review requires --pr or --current-pr.")
            if state.gh_available and state.gh_authenticated and state.github_remote_detected:
                result = gh_pr_comment(state.repo, trigger_target, args.review_body)
                trigger_actions.append(
                    {
                        "pr_number": trigger_target,
                        "requested": True,
                        "body": args.review_body,
                        "success": result.returncode == 0,
                        "stderr": truncate_text(result.stderr, 1000),
                    }
                )
                if result.returncode != 0:
                    state.errors.append(
                        {
                            "kind": "trigger_review_failed",
                            "message": result.stderr.strip() or "gh pr comment failed.",
                            "pr_number": trigger_target,
                        }
                    )
            else:
                trigger_actions.append(
                    {
                        "pr_number": trigger_target,
                        "requested": True,
                        "body": args.review_body,
                        "success": False,
                        "blocked_by": [error["kind"] for error in state.errors],
                    }
                )

        if args.check_status:
            ordered: list[tuple[int, str]] = []
            if args.pr is not None:
                ordered.append((args.pr, "target"))
            if args.current_pr is not None:
                ordered.append((args.current_pr, "current"))
            if args.previous_pr is not None:
                ordered.append((args.previous_pr, "previous"))

            seen: set[int] = set()
            for pr_number, role in ordered:
                if pr_number in seen:
                    continue
                seen.add(pr_number)
                if not (state.gh_available and state.gh_authenticated and state.github_remote_detected):
                    continue
                detail = gh_pr_view(state.repo, pr_number)
                triggered_this_run = any(action["pr_number"] == pr_number and action["success"] for action in trigger_actions)
                status, discussion = status_from_detail(detail, role=role, triggered_this_run=triggered_this_run)
                checked_statuses.append(status)
                comment_summaries.append(discussion)
                checked_pr_numbers.append(pr_number)

        status_payload = {
            "summary_status": "PASS",
            "schema_version": "dualscope/pr-review-status/v1",
            "repo": state.repo,
            "checked_prs": checked_statuses,
            "current_pr": next((status for status in checked_statuses if status["role"] == "current"), None),
            "previous_pr": next((status for status in checked_statuses if status["role"] == "previous"), None),
        }
        recommendation = choose_recommendation(
            state=state,
            open_prs=open_prs_payload.get("open_prs", []),
            statuses=checked_statuses,
            trigger_requested=args.trigger_review,
        )
        verdict = determine_verdict(state, checked_statuses, artifacts_written=True)

        summary = {
            "summary_status": "PASS" if verdict != FINAL_VERDICTS["not_validated"] else "FAIL",
            "schema_version": "dualscope/pr-review-orchestrator-summary/v1",
            "started_at": state.started_at,
            "completed_at": utc_now(),
            "verdict": verdict,
            "gh_available": state.gh_available,
            "gh_authenticated": state.gh_authenticated,
            "github_remote_detected": state.github_remote_detected,
            "remote_url": state.remote_url,
            "remote_protocol": state.remote_protocol,
            "repo": state.repo,
            "checked_prs": checked_pr_numbers,
            "trigger_actions": trigger_actions,
            "errors": state.errors,
            "warnings": state.warnings,
            "dangerous_actions": {
                "auto_merge": False,
                "force_push": False,
                "delete_branch": False,
                "auto_close_pr": False,
                "rewrite_remote": False,
            },
        }

        write_json(output_dir / "pr_review_open_prs.json", open_prs_payload)
        write_json(output_dir / "pr_review_status.json", status_payload)
        write_json(
            output_dir / "pr_review_comments_summary.json",
            {"summary_status": "PASS", "repo": state.repo, "comment_summaries": comment_summaries},
        )
        write_json(output_dir / "pr_review_recommendation.json", recommendation)
        write_json(output_dir / "pr_review_orchestrator_summary.json", summary)
        (output_dir / "pr_review_status_report.md").write_text(
            render_report(state, open_prs_payload, status_payload, recommendation, verdict),
            encoding="utf-8",
        )
        if state.errors:
            write_json(
                output_dir / "pr_review_error.json",
                {"summary_status": "WARN", "errors": state.errors, "repo": state.repo, "verdict": verdict},
            )

        exit_code = 0
        if args.fail_on_requested_changes and any(status["requested_changes_count"] > 0 for status in checked_statuses):
            exit_code = 3
        if args.fail_on_failing_checks and any(status["ci_state"] == "failing" for status in checked_statuses):
            exit_code = 4
        return exit_code, summary | {"recommendation": recommendation}
    except Exception as exc:
        state.errors.append({"kind": "runtime_error", "message": str(exc)})
        write_error_artifacts(state, str(exc))
        return 2, {
            "summary_status": "FAIL",
            "verdict": FINAL_VERDICTS["not_validated"],
            "recommendation": {"recommended_next_action": "unknown_manual_check_required"},
            "error": str(exc),
        }
