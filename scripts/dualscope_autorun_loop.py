#!/usr/bin/env python3
"""Run a local DualScope autorun loop over the task queue."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_autorun_loop_common import (  # noqa: E402
    DEFAULT_CODEX_TMPDIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PR_STATUS_OUTPUT_DIR,
    DEFAULT_QUEUE_FILE,
    DEFAULT_TASK_ORCHESTRATOR_OUTPUT_DIR,
    DEFAULT_WORKTREE_ROOT,
    AutorunLoopArgs,
    run_autorun_loop,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a controlled local DualScope autorun loop using PR and task orchestrators.",
    )
    parser.add_argument("--max-iterations", type=int, default=5, help="Maximum autorun iterations. Default: 5")
    parser.add_argument("--max-minutes", type=int, default=120, help="Maximum wall-clock minutes. Default: 120")
    parser.add_argument("--queue-file", type=Path, default=DEFAULT_QUEUE_FILE, help=f"Task queue file. Default: {DEFAULT_QUEUE_FILE}")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Output directory. Default: {DEFAULT_OUTPUT_DIR}")
    parser.add_argument("--runtime-log-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"Runtime log directory. Default: {DEFAULT_OUTPUT_DIR}")
    parser.add_argument(
        "--task-orchestrator-output-dir",
        type=Path,
        default=DEFAULT_TASK_ORCHESTRATOR_OUTPUT_DIR,
        help=f"Task orchestrator artifact directory. Default: {DEFAULT_TASK_ORCHESTRATOR_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--pr-status-output-dir",
        type=Path,
        default=DEFAULT_PR_STATUS_OUTPUT_DIR,
        help=f"PR status artifact directory. Default: {DEFAULT_PR_STATUS_OUTPUT_DIR}",
    )
    parser.add_argument("--dry-run", action="store_true", help="Plan one or more loop iterations without calling codex exec.")
    parser.add_argument("--execute", action="store_true", help="Call codex exec for selected prompts.")
    parser.add_argument("--codex-bin", default="codex", help="Codex CLI binary. Default: codex")
    parser.add_argument("--codex-tmpdir", type=Path, default=DEFAULT_CODEX_TMPDIR, help=f"Writable Codex TMPDIR. Default: {DEFAULT_CODEX_TMPDIR}")
    parser.add_argument(
        "--codex-extra-args",
        default="",
        help='Extra arguments inserted after "codex exec", parsed with shlex.split. Example: "--cd /home/lh/TriScope-LLM --full-auto".',
    )
    parser.add_argument(
        "--ignore-runtime-dirty-paths",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Allow task selection to continue when dirty paths are limited to known autorun runtime artifacts. Default: enabled.",
    )
    parser.add_argument("--use-worktrees", action="store_true", help="Run each selected task in an isolated git worktree.")
    parser.add_argument("--worktree-root", type=Path, default=DEFAULT_WORKTREE_ROOT, help=f"Task worktree root. Default: {DEFAULT_WORKTREE_ROOT}")
    parser.add_argument(
        "--enable-safe-auto-merge",
        action="store_true",
        help="Allow the safe merge gate to squash-merge the current task PR when all checks pass. Default: disabled.",
    )
    parser.add_argument(
        "--safe-merge-current-task-pr",
        action="store_true",
        help="Limit safe auto-merge to the PR created by the current autorun task.",
    )
    parser.add_argument(
        "--require-codex-review-before-merge",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require Codex review evidence before merge gate approval. Default: enabled.",
    )
    parser.add_argument("--max-review-wait-minutes", type=int, default=60, help="Maximum minutes to wait for current task PR review before merge gate stops. Default: 60")
    parser.add_argument("--review-poll-interval-seconds", type=int, default=60, help="Review polling interval. Default: 60")
    parser.add_argument(
        "--wait-for-codex-review",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Wait for Codex review when the only safe merge blocker is missing review evidence. Default: enabled.",
    )
    parser.add_argument(
        "--continue-after-review-merge",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Continue to the next autorun iteration after a waited review allows the task PR to merge. Default: enabled.",
    )
    parser.add_argument("--cleanup-merged-worktrees", action=argparse.BooleanOptionalAction, default=True, help="Remove task worktrees after successful merge. Default: enabled.")
    parser.add_argument("--keep-failed-worktrees", action="store_true", help="Keep failed task worktrees for inspection.")
    parser.add_argument(
        "--task-result-pr-packager",
        type=Path,
        default=Path("scripts/dualscope_task_worktree_runner.py"),
        help="Task worktree runner script.",
    )
    parser.add_argument(
        "--safe-pr-merge-gate",
        type=Path,
        default=Path("scripts/dualscope_safe_pr_merge_gate.py"),
        help="Safe PR merge gate script.",
    )
    parser.add_argument(
        "--main-worktree-only-scheduler",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep main checkout as scheduler only and stop worktree tasks on dirty scheduler state. Default: enabled.",
    )
    parser.add_argument("--stop-on-review-pending", action="store_true", help="Stop when checked PR review is pending.")
    parser.add_argument(
        "--allow-review-pending-continue",
        action="store_true",
        help="Allow queue execution to continue even if review is pending.",
    )
    parser.add_argument(
        "--stop-on-requested-changes",
        action="store_true",
        default=True,
        help="Stop when checked PR has requested changes. Default: enabled.",
    )
    parser.add_argument(
        "--stop-on-failing-checks",
        action="store_true",
        default=True,
        help="Stop when checked PR has failing CI checks. Default: enabled.",
    )
    return parser


def main() -> int:
    parsed = build_parser().parse_args()
    if parsed.dry_run and parsed.execute:
        raise SystemExit("--dry-run and --execute are mutually exclusive.")
    dry_run = parsed.dry_run or not parsed.execute
    args = AutorunLoopArgs(
        max_iterations=parsed.max_iterations,
        max_minutes=parsed.max_minutes,
        queue_file=parsed.queue_file,
        output_dir=parsed.output_dir,
        runtime_log_dir=parsed.runtime_log_dir,
        task_orchestrator_output_dir=parsed.task_orchestrator_output_dir,
        pr_status_output_dir=parsed.pr_status_output_dir,
        dry_run=dry_run,
        execute=parsed.execute,
        codex_bin=parsed.codex_bin,
        codex_tmpdir=parsed.codex_tmpdir,
        codex_extra_args=parsed.codex_extra_args,
        ignore_runtime_dirty_paths=parsed.ignore_runtime_dirty_paths,
        stop_on_review_pending=parsed.stop_on_review_pending,
        allow_review_pending_continue=parsed.allow_review_pending_continue,
        stop_on_requested_changes=parsed.stop_on_requested_changes,
        stop_on_failing_checks=parsed.stop_on_failing_checks,
        use_worktrees=parsed.use_worktrees,
        worktree_root=parsed.worktree_root,
        enable_safe_auto_merge=parsed.enable_safe_auto_merge,
        safe_merge_current_task_pr=parsed.safe_merge_current_task_pr,
        require_codex_review_before_merge=parsed.require_codex_review_before_merge,
        max_review_wait_minutes=parsed.max_review_wait_minutes,
        review_poll_interval_seconds=parsed.review_poll_interval_seconds,
        wait_for_codex_review=parsed.wait_for_codex_review,
        continue_after_review_merge=parsed.continue_after_review_merge,
        cleanup_merged_worktrees=parsed.cleanup_merged_worktrees,
        keep_failed_worktrees=parsed.keep_failed_worktrees,
        task_result_pr_packager=parsed.task_result_pr_packager,
        safe_pr_merge_gate=parsed.safe_pr_merge_gate,
        main_worktree_only_scheduler=parsed.main_worktree_only_scheduler,
    )
    exit_code, summary = run_autorun_loop(args)
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    print(f"Artifacts: {args.output_dir}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
