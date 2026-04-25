#!/usr/bin/env python3
"""Local DualScope task queue orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_task_orchestrator_common import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_QUEUE_FILE,
    TaskOrchestratorArgs,
    run_task_orchestrator,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Select the next DualScope-LLM task from a local queue, artifact verdicts, "
            "working-tree state, and PR review / CI status."
        )
    )
    parser.add_argument(
        "--queue-file",
        type=Path,
        default=DEFAULT_QUEUE_FILE,
        help=f"Markdown task queue with embedded JSON. Default: {DEFAULT_QUEUE_FILE}",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for orchestrator artifacts. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--check-prs",
        action="store_true",
        help="Check open PR, previous PR, and current PR status. Selection also performs this check.",
    )
    parser.add_argument("--previous-pr", type=int, help="Previous PR number to inspect before selecting a new task.")
    parser.add_argument("--current-pr", type=int, help="Current PR number to inspect.")
    parser.add_argument("--select-next-task", action="store_true", help="Select the next task from queue state.")
    parser.add_argument("--write-next-prompt", action="store_true", help="Write the selected Codex task prompt.")
    parser.add_argument(
        "--status-file",
        type=Path,
        help="Optional extra path to write the task queue status JSON.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not request remote mutations. Local output artifacts are still written.",
    )
    return parser


def main() -> int:
    parsed = build_parser().parse_args()
    args = TaskOrchestratorArgs(
        queue_file=parsed.queue_file,
        output_dir=parsed.output_dir,
        check_prs=parsed.check_prs,
        previous_pr=parsed.previous_pr,
        current_pr=parsed.current_pr,
        select_next_task=parsed.select_next_task,
        write_next_prompt=parsed.write_next_prompt,
        status_file=parsed.status_file,
        dry_run=parsed.dry_run,
    )
    exit_code, summary = run_task_orchestrator(args)
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    print(f"Artifacts: {args.output_dir}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
