#!/usr/bin/env python3
"""Check whether one DualScope PR is safe to merge, and optionally merge it."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("outputs/dualscope_safe_pr_merge_gate/default")
DEFAULT_PROXY = "http://127.0.0.1:18080"
DETAIL_FIELDS = "number,title,url,state,reviewDecision,statusCheckRollup,reviews,comments,headRefName,baseRefName,files"
FAIL_CONCLUSIONS = {"FAILURE", "ERROR", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED", "STARTUP_FAILURE"}
PENDING_STATUSES = {"QUEUED", "IN_PROGRESS", "PENDING", "REQUESTED", "WAITING", "EXPECTED"}
DEFAULT_ALLOWED_PATTERNS = [
    ".plans/dualscope-*",
    "src/eval/dualscope_*",
    "src/eval/post_dualscope_*",
    "scripts/build_dualscope_*",
    "scripts/build_post_dualscope_*",
    "scripts/run_dualscope_*",
    "scripts/dualscope_*",
    "docs/dualscope_*",
    "DUALSCOPE_MASTER_PLAN.md",
    "DUALSCOPE_TASK_QUEUE.md",
    "PLANS.md",
    "README.md",
]
DEFAULT_FORBIDDEN_PATTERNS = [
    ".env",
    ".env.*",
    "*secret*",
    "*credential*",
    "*token*",
    "*benchmark_truth*",
    "*benchmark-truth*",
    "*gate*",
    "*route_c*199*",
    "*route-c*199*",
    ".gitmodules",
    ".ssh/*",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def truncate(value: str | None, limit: int = 4000) -> str:
    text = value or ""
    return text if len(text) <= limit else text[:limit] + "..."


def proxy_env(proxy: str) -> dict[str, str]:
    env = os.environ.copy()
    env["HTTP_PROXY"] = proxy
    env["HTTPS_PROXY"] = proxy
    env["ALL_PROXY"] = proxy
    return env


def run_command(command: list[str], proxy: str, timeout: int = 120) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=proxy_env(proxy),
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except FileNotFoundError as exc:
        return {"command": command, "returncode": 127, "stdout": "", "stderr": str(exc)}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"Command timed out after {timeout}s.",
        }


def parse_csv_patterns(values: list[str] | None, defaults: list[str]) -> list[str]:
    if not values:
        return defaults
    patterns: list[str] = []
    for value in values:
        patterns.extend([item.strip() for item in value.split(",") if item.strip()])
    return patterns or defaults


def gh_pr_view(pr: int, repo: str | None, proxy: str) -> dict[str, Any]:
    command = ["gh", "pr", "view", str(pr), "--json", DETAIL_FIELDS]
    if repo:
        command.extend(["-R", repo])
    result = run_command(command, proxy=proxy, timeout=180)
    if result["returncode"] != 0:
        raise RuntimeError(result["stderr"] or result["stdout"] or f"Failed to read PR #{pr}")
    payload = json.loads(result["stdout"] or "{}")
    if not isinstance(payload, dict):
        raise RuntimeError(f"Unexpected gh pr view payload for PR #{pr}")
    return payload


def actor_login(item: dict[str, Any]) -> str:
    author = item.get("author")
    return str(author.get("login") or "") if isinstance(author, dict) else ""


def has_codex_review(pr: dict[str, Any]) -> bool:
    for review in pr.get("reviews") or []:
        if not isinstance(review, dict):
            continue
        author = actor_login(review).lower()
        body = str(review.get("body") or "").lower()
        if "codex" in author or "codex review" in body:
            return True
    for comment in pr.get("comments") or []:
        if not isinstance(comment, dict):
            continue
        author = actor_login(comment).lower()
        body = str(comment.get("body") or "").lower()
        is_request = "@codex review" in body
        if not is_request and ("codex" in author or "codex review" in body):
            return True
    return False


def has_requested_changes(pr: dict[str, Any]) -> bool:
    if str(pr.get("reviewDecision") or "").upper() == "CHANGES_REQUESTED":
        return True
    for review in pr.get("reviews") or []:
        if isinstance(review, dict) and str(review.get("state") or "").upper() == "CHANGES_REQUESTED":
            return True
    return False


def summarize_checks(pr: dict[str, Any]) -> dict[str, Any]:
    rows = []
    failing = []
    pending = []
    for item in pr.get("statusCheckRollup") or []:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("context") or item.get("workflowName") or "unknown"
        status = str(item.get("status") or "UNKNOWN").upper()
        conclusion = str(item.get("conclusion") or "UNKNOWN").upper()
        row = {"name": name, "status": status, "conclusion": conclusion}
        rows.append(row)
        if conclusion in FAIL_CONCLUSIONS:
            failing.append(row)
        elif status in PENDING_STATUSES or conclusion == "UNKNOWN":
            pending.append(row)
    return {
        "summary_status": "PASS" if not failing else "FAIL",
        "checks": rows,
        "failing_checks": failing,
        "pending_checks": pending,
        "ci_state": "failing" if failing else ("pending" if pending else "passing_or_no_checks"),
    }


def check_file_scope(pr: dict[str, Any], allowed_patterns: list[str], forbidden_patterns: list[str]) -> dict[str, Any]:
    files = [str(item.get("path") or "") for item in pr.get("files") or [] if isinstance(item, dict)]
    rows = []
    forbidden = []
    not_allowed = []
    for path in files:
        allowed = any(fnmatch.fnmatch(path, pattern) for pattern in allowed_patterns)
        matched_forbidden = [pattern for pattern in forbidden_patterns if fnmatch.fnmatch(path, pattern)]
        row = {"path": path, "allowed": allowed, "forbidden_patterns": matched_forbidden}
        rows.append(row)
        if matched_forbidden:
            forbidden.append(row)
        if not allowed:
            not_allowed.append(row)
    return {
        "summary_status": "PASS" if not forbidden and not not_allowed else "FAIL",
        "allowed_patterns": allowed_patterns,
        "forbidden_patterns": forbidden_patterns,
        "files": rows,
        "forbidden_files": forbidden,
        "not_allowed_files": not_allowed,
    }


def bool_arg(value: str) -> bool:
    lowered = value.lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected boolean, got {value!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Safely check and optionally squash-merge one DualScope PR.")
    parser.add_argument("--pr", type=int, required=True, help="Pull request number to inspect.")
    parser.add_argument("--repo", help="Optional owner/repo for gh -R.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Artifact directory. Default: {DEFAULT_OUTPUT_DIR}")
    parser.add_argument("--check-only", action="store_true", help="Only check merge safety; do not merge.")
    parser.add_argument("--merge", action="store_true", help="Squash merge if all checks pass.")
    parser.add_argument("--merge-method", default="squash", choices=["squash", "merge", "rebase"], help="Merge method. Default: squash.")
    parser.add_argument("--delete-branch", type=bool_arg, default=False, help="Whether to delete branch. Default: false.")
    parser.add_argument("--allow-review-pending", action="store_true", help="Allow missing Codex review evidence.")
    parser.add_argument("--require-codex-review", type=bool_arg, default=True, help="Require Codex review evidence. Default: true.")
    parser.add_argument("--require-no-requested-changes", type=bool_arg, default=True, help="Require no requested changes. Default: true.")
    parser.add_argument("--require-no-failing-checks", type=bool_arg, default=True, help="Require no failing checks. Default: true.")
    parser.add_argument("--allowed-file-patterns", action="append", help="Comma-separated additional/replacement allowed file patterns.")
    parser.add_argument("--forbidden-file-patterns", action="append", help="Comma-separated additional/replacement forbidden file patterns.")
    parser.add_argument("--proxy", default=DEFAULT_PROXY, help=f"HTTP(S)/ALL proxy. Default: {DEFAULT_PROXY}")
    return parser


def render_report(decision: dict[str, Any], pr_status: dict[str, Any]) -> str:
    lines = [
        "# DualScope Safe PR Merge Gate Report",
        "",
        f"- PR: #{pr_status.get('number')} {pr_status.get('url')}",
        f"- Decision: `{decision.get('decision')}`",
        f"- Can merge: `{decision.get('can_merge')}`",
        f"- Merged: `{decision.get('merged')}`",
        "",
        "## Blockers",
    ]
    blockers = decision.get("blockers") or []
    if blockers:
        lines.extend(f"- {item.get('kind')}: {item.get('message')}" for item in blockers)
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = build_parser().parse_args()
    started = utc_now()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    allowed_patterns = parse_csv_patterns(args.allowed_file_patterns, DEFAULT_ALLOWED_PATTERNS)
    forbidden_patterns = parse_csv_patterns(args.forbidden_file_patterns, DEFAULT_FORBIDDEN_PATTERNS)
    scope = {
        "summary_status": "PASS",
        "schema_version": "dualscope/safe-pr-merge-gate-scope/v1",
        "started_at": started,
        "pr": args.pr,
        "repo": args.repo,
        "check_only": args.check_only,
        "merge_requested": args.merge,
        "merge_method": args.merge_method,
        "delete_branch": args.delete_branch,
        "require_codex_review": args.require_codex_review,
        "require_no_requested_changes": args.require_no_requested_changes,
        "require_no_failing_checks": args.require_no_failing_checks,
        "allow_review_pending": args.allow_review_pending,
        "proxy": args.proxy,
    }
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_scope.json", scope)

    blockers: list[dict[str, Any]] = []
    try:
        pr_status = gh_pr_view(args.pr, args.repo, args.proxy)
    except Exception as exc:  # noqa: BLE001
        pr_status = {"number": args.pr, "summary_status": "FAIL", "error": str(exc)}
        blockers.append({"kind": "pr_read_failed", "message": str(exc)})

    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_pr_status.json", pr_status)
    file_scope = check_file_scope(pr_status, allowed_patterns, forbidden_patterns) if "files" in pr_status else {"summary_status": "FAIL"}
    ci_check = summarize_checks(pr_status) if "statusCheckRollup" in pr_status else {"summary_status": "FAIL", "failing_checks": []}
    codex_review_present = has_codex_review(pr_status)
    requested_changes = has_requested_changes(pr_status)
    review_check = {
        "summary_status": "PASS" if codex_review_present and not requested_changes else "WARN",
        "codex_review_present": codex_review_present,
        "requested_changes": requested_changes,
        "review_decision": pr_status.get("reviewDecision"),
    }
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_file_scope_check.json", file_scope)
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_review_check.json", review_check)
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_ci_check.json", ci_check)

    if args.pr == 14:
        blockers.append({"kind": "blocked_legacy_pr", "message": "PR #14 is explicitly excluded from unattended merge."})
    if pr_status.get("state") != "OPEN":
        blockers.append({"kind": "pr_not_open", "message": f"PR state is {pr_status.get('state')!r}."})
    if pr_status.get("baseRefName") != "main":
        blockers.append({"kind": "wrong_base", "message": f"PR base is {pr_status.get('baseRefName')!r}, expected 'main'."})
    if file_scope.get("summary_status") != "PASS":
        blockers.append({"kind": "file_scope_blocked", "message": "PR contains forbidden or not-allowed files."})
    if args.require_no_requested_changes and requested_changes:
        blockers.append({"kind": "requested_changes", "message": "PR has requested changes."})
    if args.require_no_failing_checks and ci_check.get("failing_checks"):
        blockers.append({"kind": "failing_checks", "message": "PR has failing CI checks."})
    if args.require_codex_review and not args.allow_review_pending and not codex_review_present:
        blockers.append({"kind": "codex_review_missing", "message": "Codex review evidence is missing or still pending."})
    if args.delete_branch:
        blockers.append({"kind": "branch_deletion_forbidden", "message": "--delete-branch=true is not allowed for this gate."})
    if args.merge_method != "squash":
        blockers.append({"kind": "non_squash_merge_forbidden", "message": "Only squash merge is allowed by default."})

    merge_result: dict[str, Any] | None = None
    can_merge = not blockers
    if args.merge and can_merge:
        command = ["gh", "pr", "merge", str(args.pr), "--squash", "--delete-branch=false"]
        if args.repo:
            command.extend(["-R", args.repo])
        merge_result = run_command(command, proxy=args.proxy, timeout=300)
        if merge_result["returncode"] != 0:
            blockers.append({"kind": "merge_failed", "message": merge_result["stderr"] or merge_result["stdout"]})
            can_merge = False

    decision = {
        "summary_status": "PASS" if not blockers else "WARN",
        "schema_version": "dualscope/safe-pr-merge-gate-decision/v1",
        "completed_at": utc_now(),
        "pr": args.pr,
        "url": pr_status.get("url"),
        "decision": "merge_allowed" if can_merge else "blocked",
        "can_merge": can_merge,
        "check_only": args.check_only,
        "merge_requested": args.merge,
        "merged": bool(args.merge and can_merge and merge_result and merge_result.get("returncode") == 0),
        "merge_result": merge_result,
        "blockers": blockers,
        "dangerous_actions": {
            "auto_merge_default": False,
            "force_push": False,
            "delete_branch": False,
            "remote_rewrite": False,
        },
    }
    write_json(args.output_dir / "dualscope_safe_pr_merge_gate_decision.json", decision)
    (args.output_dir / "dualscope_safe_pr_merge_gate_report.md").write_text(render_report(decision, pr_status), encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=True))
    print(f"Artifacts: {args.output_dir}")
    return 0 if decision["summary_status"] in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
