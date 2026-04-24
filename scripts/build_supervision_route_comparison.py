#!/usr/bin/env python3
"""Build a unified comparison across supervision routes A/B/C."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.supervision_route_comparison import build_supervision_route_comparison


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build supervision route comparison artifacts.")
    parser.add_argument("--first-labeled-fusion-dir", type=Path, default=Path("outputs/labeled_real_pilot_fusion/default"))
    parser.add_argument("--first-labeled-fusion-run-dir", type=Path, default=Path("outputs/labeled_real_pilot_fusion_runs/default"))
    parser.add_argument("--labeled-fusion-analysis-dir", type=Path, default=Path("outputs/labeled_fusion_analysis/default"))
    parser.add_argument("--controlled-supervision-expansion-dir", type=Path, default=Path("outputs/controlled_supervision_expansion/default"))
    parser.add_argument("--more-natural-analysis-dir", type=Path, default=Path("outputs/more_natural_label_analysis/default"))
    parser.add_argument("--more-natural-bootstrap-dir", type=Path, default=Path("outputs/more_natural_label_bootstrap/default"))
    parser.add_argument("--real-pilot-fusion-readiness-dir", type=Path, default=Path("outputs/real_pilot_fusion_readiness/default"))
    parser.add_argument("--real-pilot-fusion-run-dir", type=Path, default=Path("outputs/real_pilot_fusion_runs/default"))
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_supervision_route_comparison(
            first_labeled_fusion_dir=args.first_labeled_fusion_dir,
            first_labeled_fusion_run_dir=args.first_labeled_fusion_run_dir,
            labeled_fusion_analysis_dir=args.labeled_fusion_analysis_dir,
            controlled_supervision_expansion_dir=args.controlled_supervision_expansion_dir,
            more_natural_analysis_dir=args.more_natural_analysis_dir,
            more_natural_bootstrap_dir=args.more_natural_bootstrap_dir,
            real_pilot_fusion_readiness_dir=args.real_pilot_fusion_readiness_dir,
            real_pilot_fusion_run_dir=args.real_pilot_fusion_run_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM supervision route comparison failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    print("TriScope-LLM supervision route comparison complete")
    print(f"Chosen route: {result['recommendation']['chosen_route_name']}")
    print(f"Output dir: {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
