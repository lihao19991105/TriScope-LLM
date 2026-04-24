#!/usr/bin/env python3
"""Build post route_c stable baseline time-separated replay analysis artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build post route_c stable baseline time-separated replay analysis artifacts."
    )
    parser.add_argument(
        "--prior-blocked-analysis-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_repair_analysis/default"),
    )
    parser.add_argument(
        "--first-recovery-recheck-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_output_normalization_recheck/default"),
    )
    parser.add_argument(
        "--stage-143-analysis-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_analysis/default"),
    )
    parser.add_argument(
        "--stage-143-recheck-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default"),
    )
    parser.add_argument(
        "--replay-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_stable_baseline_time_separated_replay/default"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.post_route_c_stable_baseline_time_separated_replay_analysis import (
        build_post_route_c_stable_baseline_time_separated_replay_analysis,
    )

    try:
        result = build_post_route_c_stable_baseline_time_separated_replay_analysis(
            prior_blocked_analysis_dir=args.prior_blocked_analysis_dir,
            first_recovery_recheck_dir=args.first_recovery_recheck_dir,
            stage_143_analysis_dir=args.stage_143_analysis_dir,
            stage_143_recheck_dir=args.stage_143_recheck_dir,
            replay_dir=args.replay_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM route_c time-separated replay analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM route_c time-separated replay analysis complete")
    print(f"Compare: {result['output_paths']['compare']}")
    print(f"Verdict: {result['output_paths']['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
