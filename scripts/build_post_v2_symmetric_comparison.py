#!/usr/bin/env python3
"""Build post-v2 symmetric supervision comparison."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.post_v2_symmetric_comparison import build_post_v2_symmetric_comparison


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build post-v2 symmetric supervision comparison.")
    parser.add_argument("--old-route-b-dir", type=Path, default=Path("outputs/more_natural_label_bootstrap/default"))
    parser.add_argument("--larger-route-b-dir", type=Path, default=Path("outputs/chosen_route_rerun_on_larger_split/default"))
    parser.add_argument("--route-b-v2-dir", type=Path, default=Path("outputs/rerun_route_b_on_labeled_split_v2/default"))
    parser.add_argument("--expanded-route-c-dir", type=Path, default=Path("outputs/expanded_route_c_bootstrap/default"))
    parser.add_argument("--larger-route-c-dir", type=Path, default=Path("outputs/rerun_route_c_on_larger_split/default"))
    parser.add_argument("--route-c-v2-dir", type=Path, default=Path("outputs/rerun_route_c_on_labeled_split_v2/default"))
    parser.add_argument("--symmetric-comparison-dir", type=Path, default=Path("outputs/symmetric_larger_split_comparison/default"))
    parser.add_argument("--post-symmetric-bootstrap-dir", type=Path, default=Path("outputs/post_symmetric_next_step_bootstrap/default"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_post_v2_symmetric_comparison(
            old_route_b_dir=args.old_route_b_dir,
            larger_route_b_dir=args.larger_route_b_dir,
            route_b_v2_dir=args.route_b_v2_dir,
            expanded_route_c_dir=args.expanded_route_c_dir,
            larger_route_c_dir=args.larger_route_c_dir,
            route_c_v2_dir=args.route_c_v2_dir,
            symmetric_comparison_dir=args.symmetric_comparison_dir,
            post_symmetric_bootstrap_dir=args.post_symmetric_bootstrap_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM post-v2 symmetric comparison failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM post-v2 symmetric comparison complete")
    print(f"Summary: {result['output_paths']['summary']}")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
