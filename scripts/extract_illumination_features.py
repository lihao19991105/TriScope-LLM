#!/usr/bin/env python3
"""Extract structured illumination features from raw probe artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.features.illumination_features import extract_illumination_features


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extract prompt-level and run-level illumination features from a raw_results.jsonl "
            "artifact produced by the TriScope-LLM illumination probe."
        ),
    )
    parser.add_argument(
        "--raw-results",
        type=Path,
        required=True,
        help="Path to the illumination raw_results.jsonl artifact.",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=None,
        help="Optional path to the illumination summary.json artifact.",
    )
    parser.add_argument(
        "--config-snapshot",
        type=Path,
        default=None,
        help="Optional path to the illumination config_snapshot.json artifact.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory where feature artifacts will be written. Defaults to <raw_results_dir>/features.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional stable run identifier. Defaults to the raw results parent directory name.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    output_dir = args.output_dir or (args.raw_results.parent / "features")

    try:
        result = extract_illumination_features(
            raw_results_path=args.raw_results,
            summary_json_path=args.summary_json,
            config_snapshot_path=args.config_snapshot,
            output_dir=output_dir,
            run_id=args.run_id,
        )
    except Exception as exc:
        output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = output_dir / "feature_extraction_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "raw_results": str(args.raw_results),
                    "summary_json": str(args.summary_json) if args.summary_json else None,
                    "config_snapshot": str(args.config_snapshot) if args.config_snapshot else None,
                    "output_dir": str(output_dir),
                    "run_id": args.run_id,
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM illumination feature extraction failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    summary = result["feature_summary"]
    output_paths = result["output_paths"]
    print("TriScope-LLM illumination feature extraction complete")
    print(f"Run ID: {summary['run_id']}")
    print(
        f"Target behavior: {summary['num_target_behavior']}/{summary['num_prompts']} "
        f"({summary['target_behavior_rate']:.4f})"
    )
    print(f"Prompt features JSONL: {output_paths['prompt_level_jsonl']}")
    print(f"Feature CSV: {output_paths['feature_csv']}")
    print(f"Aggregated feature JSON: {output_paths['aggregated_json']}")
    print(f"Feature summary: {output_paths['feature_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
