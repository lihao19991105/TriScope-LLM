#!/usr/bin/env python3
"""Build unified comparison across route B, old route C, and expanded route C."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.expanded_supervision_comparison import build_expanded_supervision_comparison


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare route B, old route C, and expanded route C.")
    parser.add_argument("--route-b-dir", type=Path, default=Path("outputs/more_natural_label_bootstrap/default"))
    parser.add_argument("--old-route-c-dir", type=Path, default=Path("outputs/benchmark_truth_leaning_label_bootstrap/default"))
    parser.add_argument("--expanded-route-c-dir", type=Path, default=Path("outputs/expanded_route_c_bootstrap/default"))
    parser.add_argument("--labeled-slice-expansion-dir", type=Path, default=Path("outputs/labeled_slice_expansion/default"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_expanded_supervision_comparison(
            route_b_dir=args.route_b_dir,
            old_route_c_dir=args.old_route_c_dir,
            expanded_route_c_dir=args.expanded_route_c_dir,
            labeled_slice_expansion_dir=args.labeled_slice_expansion_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM expanded supervision comparison failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    print("TriScope-LLM expanded supervision comparison complete")
    print(f"Recommendation: {result['output_paths']['recommendation']}")
    print(f"Comparison summary: {result['output_paths']['comparison_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
