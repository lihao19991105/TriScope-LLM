#!/usr/bin/env python3
"""Extract structured confidence features from raw probe artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.features.confidence_features import extract_confidence_features


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extract sample-level and run-level confidence features from a raw_results.jsonl "
            "artifact produced by the TriScope-LLM confidence probe."
        ),
    )
    parser.add_argument(
        "--raw-results",
        type=Path,
        required=True,
        help="Path to the confidence raw_results.jsonl artifact.",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=None,
        help="Optional path to the confidence summary.json artifact.",
    )
    parser.add_argument(
        "--config-snapshot",
        type=Path,
        default=None,
        help="Optional path to the confidence config_snapshot.json artifact.",
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
    parser.add_argument(
        "--high-confidence-threshold",
        type=float,
        default=0.10,
        help="Threshold used for lightweight sequence-lock confidence statistics.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    output_dir = args.output_dir or (args.raw_results.parent / "features")
    try:
        result = extract_confidence_features(
            raw_results_path=args.raw_results,
            summary_json_path=args.summary_json,
            config_snapshot_path=args.config_snapshot,
            output_dir=output_dir,
            run_id=args.run_id,
            high_confidence_threshold=args.high_confidence_threshold,
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
                    "high_confidence_threshold": args.high_confidence_threshold,
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM confidence feature extraction failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    summary = result["feature_summary"]
    output_paths = result["output_paths"]
    print("TriScope-LLM confidence feature extraction complete")
    print(f"Run ID: {summary['run_id']}")
    print(f"Samples: {summary['num_samples']}")
    print(f"Target behavior rate: {summary['target_behavior_rate']:.4f}")
    print(f"Mean chosen token prob: {summary['mean_chosen_token_prob_mean']:.4f}")
    print(f"Mean entropy: {summary['mean_entropy_mean']:.4f}")
    print(f"Sample features JSONL: {output_paths['sample_level_jsonl']}")
    print(f"Feature CSV: {output_paths['feature_csv']}")
    print(f"Aggregated feature JSON: {output_paths['aggregated_json']}")
    print(f"Feature summary: {output_paths['feature_summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
