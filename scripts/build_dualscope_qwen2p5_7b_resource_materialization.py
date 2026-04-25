#!/usr/bin/env python3
"""Build Qwen2.5-7B resource materialization artifacts for DualScope."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_qwen2p5_7b_resource_common import (  # noqa: E402
    DEFAULT_LABELED_PAIRS,
    DEFAULT_LOCAL_MODEL_DIR,
    DEFAULT_MODEL_ID,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TARGET_RESPONSE_PLAN_DIR,
)
from src.eval.dualscope_qwen2p5_7b_resource_materialization import (  # noqa: E402
    build_resource_materialization,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Materialize and audit Qwen2.5-7B resources for DualScope SCI3.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Hugging Face model ID.")
    parser.add_argument("--local-model-dir", type=Path, default=DEFAULT_LOCAL_MODEL_DIR, help="Local model directory.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output artifact directory.")
    download = parser.add_mutually_exclusive_group()
    download.add_argument("--allow-download", action="store_true", help="Allow snapshot download when disk and auth checks pass.")
    download.add_argument("--no-download", action="store_true", help="Disable model download.")
    parser.add_argument("--revision", default=None, help="Optional Hugging Face revision.")
    parser.add_argument("--hf-token-env", default="HF_TOKEN", help="Environment variable containing an optional HF token.")
    parser.add_argument("--check-tokenizer", action="store_true", default=True, help="Load tokenizer metadata. Default: enabled.")
    parser.add_argument("--check-config", action="store_true", default=True, help="Load config metadata. Default: enabled.")
    parser.add_argument("--check-model-load", action="store_true", help="Attempt full model-load readiness check. Default: disabled.")
    parser.add_argument("--check-gpu", action="store_true", default=True, help="Check GPU visibility. Default: enabled.")
    parser.add_argument("--check-disk", action="store_true", default=True, help="Check free disk. Default: enabled.")
    parser.add_argument("--min-free-disk-gb", type=float, default=30.0, help="Minimum free disk GB before download.")
    parser.add_argument("--max-load-seconds", type=int, default=120, help="Maximum full-load check seconds if enabled.")
    parser.add_argument("--dtype", default="auto", help="Planned dtype for future model load.")
    parser.add_argument("--device-map", default="auto", help="Planned device_map for future model load.")
    parser.add_argument("--trust-remote-code", action="store_true", help="Pass trust_remote_code to Transformers checks.")
    parser.add_argument("--labeled-pairs-path", type=Path, default=DEFAULT_LABELED_PAIRS, help="Expected labeled pairs path.")
    parser.add_argument(
        "--target-response-plan-dir",
        type=Path,
        default=DEFAULT_TARGET_RESPONSE_PLAN_DIR,
        help="Expected target-response generation plan output directory.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = build_resource_materialization(
        model_id=args.model_id,
        local_model_dir=args.local_model_dir,
        output_dir=args.output_dir,
        allow_download=args.allow_download and not args.no_download,
        revision=args.revision,
        hf_token_env=args.hf_token_env,
        check_tokenizer=args.check_tokenizer,
        check_config=args.check_config,
        check_model_load=args.check_model_load,
        check_gpu=args.check_gpu,
        check_disk=args.check_disk,
        min_free_disk_gb=args.min_free_disk_gb,
        max_load_seconds=args.max_load_seconds,
        dtype=args.dtype,
        device_map=args.device_map,
        trust_remote_code=args.trust_remote_code,
        labeled_pairs_path=args.labeled_pairs_path,
        target_response_plan_dir=args.target_response_plan_dir,
    )
    print("Final verdict: %s" % summary["final_verdict"])
    print("Artifacts: %s" % args.output_dir)
    return 0 if summary["final_verdict"] != "Not validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())

