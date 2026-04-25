#!/usr/bin/env python3
"""Build condition-level rerun artifacts for the DualScope minimal first slice."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_minimal_first_slice_condition_level_rerun import build_condition_level_rerun  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the minimal DualScope first-slice Stage 1/2/3 chain on condition-level rows."
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Output directory for rerun artifacts.")
    parser.add_argument(
        "--input-slice",
        type=Path,
        default=Path(
            "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/"
            "condition_level_rerun_input_slice.jsonl"
        ),
        help="Condition-level input JSONL produced by the labeled-rerun repair package.",
    )
    parser.add_argument(
        "--input-manifest",
        type=Path,
        default=Path(
            "outputs/dualscope_minimal_first_slice_real_run_rerun_with_labels_repair/default/"
            "condition_level_rerun_input_manifest.json"
        ),
        help="Manifest for the condition-level input JSONL.",
    )
    parser.add_argument("--capability-mode", choices=["auto", "with_logprobs", "without_logprobs"], default="auto")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-full-matrix", action="store_true", default=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_condition_level_rerun(
        output_dir=args.output_dir,
        input_slice=args.input_slice,
        input_manifest=args.input_manifest,
        capability_mode=args.capability_mode,
        seed=args.seed,
        no_full_matrix=args.no_full_matrix,
    )
    print(f"Verdict: {summary['final_verdict']}")
    print(f"Recommendation: {summary['recommended_next_step']}")
    print(f"Artifacts: {args.output_dir}")
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
