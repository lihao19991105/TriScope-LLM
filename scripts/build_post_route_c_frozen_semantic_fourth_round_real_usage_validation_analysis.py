#!/usr/bin/env python3
"""CLI for post-analysis of stage-188 fourth-round real usage validation."""

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
    parser.add_argument("--validation-dir", type=Path, default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_fourth_round_real_usage/default"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.post_route_c_frozen_semantic_fourth_round_real_usage_analysis import post_route_c_frozen_semantic_fourth_round_real_usage_analysis
    try:
        result = post_route_c_frozen_semantic_fourth_round_real_usage_analysis(validation_dir=args.validation_dir, output_dir=args.output_dir)
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"TriScope-LLM stage-188 post-analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1
    print("stage-188 route_c frozen semantic fourth-round real usage post-analysis artifacts written to:")
    for key, value in result["output_paths"].items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
