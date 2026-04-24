#!/usr/bin/env python3
"""CLI for stage-169 route_c frozen semantic next level real usage batched stability recheck."""

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
        "--real-run-dir",
        type=Path,
        default=Path(
            "outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default/runs/extension_rerun_01"
        ),
        help="Stable real execution run directory used as stage-169 anchor.",
    )
    parser.add_argument(
        "--stage-166-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_next_level_real_usage/default"),
        help="Directory containing stage-166 artifacts.",
    )
    parser.add_argument(
        "--stage-167-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_next_level_real_usage_stability_recheck/default"),
        help="Directory containing stage-167 artifacts.",
    )
    parser.add_argument(
        "--stage-168-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_frozen_semantic_next_level_real_usage_batched_regression/default"),
        help="Directory containing stage-168 artifacts.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--label-threshold", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to write stage-169 artifacts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_frozen_semantic_next_level_real_usage_batched_stability_recheck import build_route_c_frozen_semantic_next_level_real_usage_batched_stability_recheck

    try:
        result = build_route_c_frozen_semantic_next_level_real_usage_batched_stability_recheck(
            real_run_dir=args.real_run_dir,
            stage_166_dir=args.stage_166_dir,
            stage_167_dir=args.stage_167_dir,
            stage_168_dir=args.stage_168_dir,
            output_dir=args.output_dir,
            seed=args.seed,
            label_threshold=args.label_threshold,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM stage-169 next level real usage batched stability recheck failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("stage-169 route_c frozen semantic next level real usage batched stability recheck artifacts written to:")
    for key, value in result["output_paths"].items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
