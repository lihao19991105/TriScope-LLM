#!/usr/bin/env python3
"""CLI for stage-190 route_c frozen semantic fourth-round real usage batched regression."""

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
    parser.add_argument("--real-run-dir", type=Path, default=Path("outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default/runs/extension_rerun_01"))
    parser.add_argument("--stage-187-dir", type=Path, default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_third_round_real_usage_chain_final_recheck/default"))
    parser.add_argument("--stage-188-dir", type=Path, default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_fourth_round_real_usage/default"))
    parser.add_argument("--stage-189-dir", type=Path, default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_fourth_round_real_usage_stability_recheck/default"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label-threshold", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_frozen_semantic_fourth_round_real_usage_batched_regression import build_route_c_frozen_semantic_fourth_round_real_usage_batched_regression
    try:
        result = build_route_c_frozen_semantic_fourth_round_real_usage_batched_regression(
            real_run_dir=args.real_run_dir,
            stage_187_dir=args.stage_187_dir,
            stage_188_dir=args.stage_188_dir,
            stage_189_dir=args.stage_189_dir,
            output_dir=args.output_dir,
            seed=args.seed,
            label_threshold=args.label_threshold,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2) + "\n", encoding="utf-8")
        print(f"TriScope-LLM stage-190 failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1
    print("stage-190 route_c frozen semantic fourth-round real usage batched regression artifacts written to:")
    for key, value in result["output_paths"].items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
