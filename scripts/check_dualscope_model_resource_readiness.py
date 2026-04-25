#!/usr/bin/env python3
"""Check DualScope model resource readiness without forcing downloads."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_resource_common import (  # noqa: E402
    DEFAULT_LOCAL_MODEL_DIR,
    DEFAULT_MODEL_ID,
    DEFAULT_OUTPUT_DIR,
)
from src.eval.dualscope_qwen2p5_7b_resource_materialization import (  # noqa: E402
    build_resource_materialization,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check Qwen2.5-7B model resource readiness for DualScope.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Model ID to check.")
    parser.add_argument("--local-model-dir", type=Path, default=DEFAULT_LOCAL_MODEL_DIR, help="Local model path.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for readiness artifacts.",
    )
    parser.add_argument("--min-free-disk-gb", type=float, default=30.0, help="Minimum free disk GB.")
    parser.add_argument("--trust-remote-code", action="store_true", help="Pass trust_remote_code to Transformers checks.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_resource_materialization(
        model_id=args.model_id,
        local_model_dir=args.local_model_dir,
        output_dir=args.output_dir,
        allow_download=False,
        revision=None,
        hf_token_env="HF_TOKEN",
        check_tokenizer=True,
        check_config=True,
        check_model_load=False,
        check_gpu=True,
        check_disk=True,
        min_free_disk_gb=args.min_free_disk_gb,
        max_load_seconds=120,
        dtype="auto",
        device_map="auto",
        trust_remote_code=args.trust_remote_code,
        labeled_pairs_path=Path("data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl"),
        target_response_plan_dir=Path("outputs/dualscope_first_slice_target_response_generation_plan/default"),
    )
    print("Final verdict: %s" % summary["final_verdict"])
    print("Artifacts: %s" % args.output_dir)
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())

