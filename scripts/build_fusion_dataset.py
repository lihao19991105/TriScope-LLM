#!/usr/bin/env python3
"""Build the minimal TriScope-LLM fusion dataset from three feature streams."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.fusion.feature_alignment import build_fusion_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Merge illumination, reasoning, and confidence sample-level features into a "
            "single fusion-ready dataset artifact."
        ),
    )
    parser.add_argument(
        "--illumination-features",
        type=Path,
        required=True,
        help="Path to illumination sample-level feature JSONL.",
    )
    parser.add_argument(
        "--reasoning-features",
        type=Path,
        required=True,
        help="Path to reasoning sample-level feature JSONL.",
    )
    parser.add_argument(
        "--confidence-features",
        type=Path,
        required=True,
        help="Path to confidence sample-level feature JSONL.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where fusion dataset artifacts will be written.",
    )
    parser.add_argument(
        "--join-mode",
        default="outer",
        choices=["outer", "inner"],
        help="Alignment mode used to merge modality rows by sample_id.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = build_fusion_dataset(
            illumination_features_path=args.illumination_features,
            reasoning_features_path=args.reasoning_features,
            confidence_features_path=args.confidence_features,
            output_dir=args.output_dir,
            join_mode=args.join_mode,
        )
    except Exception as exc:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        failure_path = args.output_dir / "build_failure.json"
        failure_path.write_text(
            json.dumps(
                {
                    "summary_status": "FAIL",
                    "illumination_features": str(args.illumination_features),
                    "reasoning_features": str(args.reasoning_features),
                    "confidence_features": str(args.confidence_features),
                    "join_mode": args.join_mode,
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"TriScope-LLM fusion dataset build failed: {exc}")
        print(f"Failure summary: {failure_path}")
        return 1

    summary = result["alignment_summary"]
    output_paths = result["output_paths"]
    print("TriScope-LLM fusion dataset build complete")
    print(f"Join mode: {summary['join_mode']}")
    print(f"Merged rows: {summary['num_rows']}")
    print(f"Rows with all modalities: {summary['num_rows_with_all_modalities']}")
    print(f"Fusion dataset JSONL: {output_paths['fusion_dataset_jsonl']}")
    print(f"Fusion dataset CSV: {output_paths['fusion_dataset_csv']}")
    print(f"Alignment summary: {output_paths['alignment_summary']}")
    print(f"Config snapshot: {output_paths['config_snapshot']}")
    print(f"Log: {output_paths['log']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
