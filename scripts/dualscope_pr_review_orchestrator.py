#!/usr/bin/env python3
"""Local DualScope GitHub PR review status orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_pr_review_orchestrator_common import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REVIEW_BODY,
    OrchestratorArgs,
    run_orchestrator,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check and optionally request Codex Review / CI status for GitHub PRs using gh.",
    )
    parser.add_argument("--repo", help="Optional owner/repo. If omitted, infer from git remote origin.")
    parser.add_argument("--pr", type=int, help="PR number to inspect or request review for.")
    parser.add_argument("--current-pr", type=int, help="Current task PR number.")
    parser.add_argument("--previous-pr", type=int, help="Previous PR number to inspect.")
    parser.add_argument("--list-open", action="store_true", help="List open PRs and write open PR artifacts.")
    parser.add_argument("--trigger-review", action="store_true", help="Comment the review body on --pr or --current-pr.")
    parser.add_argument("--check-status", action="store_true", help="Check PR review/comment/CI status.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for artifacts. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--review-body",
        default=DEFAULT_REVIEW_BODY,
        help=f"Review trigger body. Default: {DEFAULT_REVIEW_BODY!r}",
    )
    parser.add_argument(
        "--fail-on-requested-changes",
        action="store_true",
        help="Exit non-zero if checked PRs contain requested changes.",
    )
    parser.add_argument(
        "--fail-on-failing-checks",
        action="store_true",
        help="Exit non-zero if checked PRs contain failing CI checks.",
    )
    return parser


def main() -> int:
    parsed = build_parser().parse_args()
    args = OrchestratorArgs(
        repo=parsed.repo,
        pr=parsed.pr,
        current_pr=parsed.current_pr,
        previous_pr=parsed.previous_pr,
        list_open=parsed.list_open,
        trigger_review=parsed.trigger_review,
        check_status=parsed.check_status,
        output_dir=parsed.output_dir,
        review_body=parsed.review_body,
        fail_on_requested_changes=parsed.fail_on_requested_changes,
        fail_on_failing_checks=parsed.fail_on_failing_checks,
    )
    exit_code, summary = run_orchestrator(args)
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    print(f"Artifacts: {args.output_dir}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
