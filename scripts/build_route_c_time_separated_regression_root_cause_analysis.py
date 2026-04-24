#!/usr/bin/env python3
"""Build route_c time-separated regression root-cause analysis artifacts."""

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
        description="Build route_c time-separated regression root-cause analysis artifacts."
    )
    parser.add_argument(
        "--stage-143-recheck-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default"),
    )
    parser.add_argument(
        "--stage-143-analysis-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_analysis/default"),
    )
    parser.add_argument(
        "--stage-144-replay-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_stable_baseline_time_separated_replay/default"),
    )
    parser.add_argument(
        "--stage-144-analysis-dir",
        type=Path,
        default=Path("outputs/model_axis_1p5b_route_c_stable_baseline_time_separated_replay_analysis/default"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.eval.route_c_time_separated_regression_root_cause_analysis import (
        build_route_c_time_separated_regression_root_cause_analysis,
    )

    try:
        result = build_route_c_time_separated_regression_root_cause_analysis(
            stage_143_recheck_dir=args.stage_143_recheck_dir,
            stage_143_analysis_dir=args.stage_143_analysis_dir,
            stage_144_replay_dir=args.stage_144_replay_dir,
            stage_144_analysis_dir=args.stage_144_analysis_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM route_c time-separated regression root-cause analysis failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM route_c time-separated regression root-cause analysis complete")
    print(f"Scope: {result['output_paths']['scope']}")
    print(f"Diff summary: {result['output_paths']['diff_summary']}")
    print(f"Report: {result['output_paths']['report']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
