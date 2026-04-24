#!/usr/bin/env python3
"""CLI for post-analysis of stage-162 minimal real-usage batched stability recheck."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validation-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_minimal_real_usage_batched_stability_recheck/default"),
        help="Directory containing stage-162 validation artifacts.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write stage-162 post-analysis artifacts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.post_route_c_frozen_semantic_minimal_real_usage_batched_stability_recheck_analysis import (
        post_route_c_frozen_semantic_minimal_real_usage_batched_stability_recheck_analysis,
    )

    try:
        result = post_route_c_frozen_semantic_minimal_real_usage_batched_stability_recheck_analysis(
            validation_dir=args.validation_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM stage-162 minimal real-usage batched stability post-analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("stage-162 route_c frozen semantic minimal real-usage batched stability post-analysis artifacts written to:")
    for key, value in result["output_paths"].items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
