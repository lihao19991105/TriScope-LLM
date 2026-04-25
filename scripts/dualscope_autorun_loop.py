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
    )
    exit_code, summary = run_autorun_loop(args)
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    print(f"Artifacts: {args.output_dir}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
