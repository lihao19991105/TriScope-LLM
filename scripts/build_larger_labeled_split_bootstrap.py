#!/usr/bin/env python3
"""Build a larger labeled split bootstrap for TriScope-LLM."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.larger_labeled_split_bootstrap import build_larger_labeled_split_bootstrap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a larger labeled split on top of the expanded 10-row substrate.")
    parser.add_argument(
        "--expanded-inputs-dir",
        type=Path,
        default=Path("outputs/labeled_slice_expansion/default/materialized_labeled_slice_inputs"),
    )
    parser.add_argument("--models-config", type=Path, default=Path("configs/models.yaml"))
    parser.add_argument("--reasoning-config", type=Path, default=Path("configs/reasoning.yaml"))
    parser.add_argument("--confidence-config", type=Path, default=Path("configs/confidence.yaml"))
    parser.add_argument("--illumination-config", type=Path, default=Path("configs/illumination.yaml"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-bridge-dry-run", action="store_true")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_larger_labeled_split_bootstrap(
            expanded_inputs_dir=args.expanded_inputs_dir,
            output_dir=args.output_dir,
            models_config_path=args.models_config,
            reasoning_config_path=args.reasoning_config,
            confidence_config_path=args.confidence_config,
            illumination_config_path=args.illumination_config,
            seed=args.seed,
            run_bridge_dry_run=not args.skip_bridge_dry_run,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps({"summary_status": "FAIL", "error": str(exc)}, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM larger labeled split bootstrap failed: {exc}")
        print(f"Failure summary: {failure_path.resolve()}")
        return 1

    print("TriScope-LLM larger labeled split bootstrap complete")
    print(f"Larger split rows: {result['larger_summary']['num_rows']}")
    print(f"Compatibility summary: {result['output_paths']['compatibility_summary']}")
    if result["output_paths"]["bridge_summary"] is not None:
        print(f"Bridge summary: {result['output_paths']['bridge_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
