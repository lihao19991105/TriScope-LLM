#!/usr/bin/env python3
"""Build symmetric larger-split supervision comparison."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.symmetric_larger_split_comparison import build_symmetric_larger_split_comparison


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build symmetric larger-split supervision comparison.")
    parser.add_argument("--old-route-b-dir", type=Path, default=Path("outputs/more_natural_label_bootstrap/default"))
    parser.add_argument("--larger-route-b-dir", type=Path, default=Path("outputs/chosen_route_rerun_on_larger_split/default"))
    parser.add_argument("--larger-route-c-dir", type=Path, default=Path("outputs/rerun_route_c_on_larger_split/default"))
    parser.add_argument("--expanded-route-c-dir", type=Path, default=Path("outputs/expanded_route_c_bootstrap/default"))
    parser.add_argument("--post-rerun-dir", type=Path, default=Path("outputs/post_rerun_comparison/default"))
    parser.add_argument("--larger-split-dir", type=Path, default=Path("outputs/larger_labeled_split_bootstrap/default"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_symmetric_larger_split_comparison(
            old_route_b_dir=args.old_route_b_dir,
            larger_route_b_dir=args.larger_route_b_dir,
            larger_route_c_dir=args.larger_route_c_dir,
            expanded_route_c_dir=args.expanded_route_c_dir,
            post_rerun_dir=args.post_rerun_dir,
            larger_split_dir=args.larger_split_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM symmetric larger-split comparison failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM symmetric larger-split comparison complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
