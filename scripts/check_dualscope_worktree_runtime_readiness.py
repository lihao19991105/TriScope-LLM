#!/usr/bin/env python3
"""Check DualScope worktree runtime readiness for bounded Qwen2.5-7B execution."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_worktree_runtime_readiness import (  # noqa: E402
    check_worktree_runtime_readiness,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/dualscope_worktree_gpu_bnb_input_readiness_repair/default"))
    parser.add_argument("--labeled-pairs", type=Path, default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"))
    parser.add_argument("--source-jsonl", type=Path, default=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl"))
    parser.add_argument("--target-response-plan-dir", type=Path, default=Path("outputs/dualscope_first_slice_target_response_generation_plan/default"))
    parser.add_argument("--alpaca-main-slice-plan-dir", type=Path, default=Path("outputs/dualscope_qwen2p5_7b_alpaca_main_slice_plan/default"))
    parser.add_argument("--model-dir", type=Path, default=Path("/mnt/sda3/lh/models/qwen2p5-7b-instruct"))
    parser.add_argument("--repo-model-symlink", type=Path, default=Path("models/qwen2p5-7b-instruct"))
    parser.add_argument("--hf-home", type=Path, default=Path("/mnt/sda3/lh/huggingface"))
    parser.add_argument("--tmpdir", type=Path, default=Path("/mnt/sda3/lh/tmp"))
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path(".reports/dualscope_task_verdicts/dualscope-worktree-gpu-bnb-input-readiness-repair.json"),
    )
    parser.add_argument("--attempt-pip-install", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = check_worktree_runtime_readiness(
        output_dir=args.output_dir,
        labeled_pairs=args.labeled_pairs,
        source_jsonl=args.source_jsonl,
        target_response_plan_dir=args.target_response_plan_dir,
        alpaca_main_slice_plan_dir=args.alpaca_main_slice_plan_dir,
        model_dir=args.model_dir,
        repo_model_symlink=args.repo_model_symlink,
        hf_home=args.hf_home,
        tmpdir=args.tmpdir,
        registry_path=args.registry_path,
        attempt_pip_install=args.attempt_pip_install,
    )
    print(f"Final verdict: {summary['final_verdict']}")
    print(f"Recommended next step: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
