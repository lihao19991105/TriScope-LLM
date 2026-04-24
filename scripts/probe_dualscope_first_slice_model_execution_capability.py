#!/usr/bin/env python3
"""Probe minimal local model generation capability for DualScope first slice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_real_run_compression_common import DATASET_FILE, MODEL_PATH, read_jsonl, write_json, write_jsonl, markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe minimal model generation capability.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    parser.add_argument("--dataset-file", type=Path, default=DATASET_FILE)
    parser.add_argument("--max-samples", type=int, default=3)
    parser.add_argument("--max-new-tokens", type=int, default=8)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    scope = {
        "summary_status": "PASS",
        "model_path": str(args.model_path),
        "dataset_file": str(args.dataset_file),
        "max_samples": args.max_samples,
        "max_new_tokens": args.max_new_tokens,
        "training_executed": False,
        "full_matrix_executed": False,
    }
    rows = read_jsonl(args.dataset_file, limit=max(1, args.max_samples))
    details = []
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        cuda_available = torch.cuda.is_available()
        device = "cuda:0" if cuda_available else "cpu"
        tokenizer = AutoTokenizer.from_pretrained(str(args.model_path), local_files_only=True, trust_remote_code=False)
        model = AutoModelForCausalLM.from_pretrained(
            str(args.model_path),
            local_files_only=True,
            trust_remote_code=False,
            torch_dtype=torch.float16 if cuda_available else torch.float32,
        )
        model.to(device)
        model.eval()
        for row in rows:
            prompt = str(row.get("prompt", ""))[:512]
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256).to(device)
            with torch.no_grad():
                generated = model.generate(**inputs, max_new_tokens=args.max_new_tokens, do_sample=False, pad_token_id=tokenizer.eos_token_id)
            new_tokens = generated[0][inputs["input_ids"].shape[-1] :]
            text = tokenizer.decode(new_tokens, skip_special_tokens=True)
            details.append({"example_id": row.get("example_id"), "prompt_chars": len(prompt), "generated_text": text, "generated_token_count": int(new_tokens.numel())})
        passed = bool(details)
        error = None
        model_class = model.__class__.__name__
    except Exception as exc:  # environment dependent
        passed = False
        error = str(exc)
        model_class = None
    summary = {
        "summary_status": "PASS",
        "model_execution_ready": passed,
        "generation_probe_passed": passed,
        "model_class": model_class,
        "sample_count": len(details),
        "error": error,
        "training_executed": False,
        "full_matrix_executed": False,
    }
    write_json(args.output_dir / "dualscope_first_slice_model_execution_probe.json", summary)
    write_jsonl(args.output_dir / "dualscope_first_slice_generation_probe_details.jsonl", details)
    markdown(args.output_dir / "dualscope_first_slice_model_execution_probe_report.md", "DualScope Model Execution Probe", [
        f"- Model execution ready: `{passed}`",
        f"- Sample count: `{len(details)}`",
        f"- Error: `{error}`",
        "- This probe performs minimal generation only; it does not train or run the full matrix.",
    ])
    print(f"Model execution ready: {passed}")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())

