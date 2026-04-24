#!/usr/bin/env python3
"""Probe logits/logprob capability for DualScope first slice."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval.dualscope_first_slice_real_run_compression_common import DATASET_FILE, MODEL_PATH, read_jsonl, write_json, markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe local logits/logprob capability.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    parser.add_argument("--dataset-file", type=Path, default=DATASET_FILE)
    parser.add_argument("--max-samples", type=int, default=1)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_jsonl(args.dataset_file, limit=max(1, args.max_samples))
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
        prompt = str(rows[0].get("prompt", ""))[:256]
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits[:, -1, :]
        probs = torch.softmax(logits.float(), dim=-1)
        top_probs, top_ids = torch.topk(probs, k=5, dim=-1)
        entropy = float(-(probs * torch.log(probs.clamp_min(1e-12))).sum().item())
        top1_prob = float(top_probs[0, 0].item())
        topk_mass = float(top_probs.sum().item())
        top_tokens = [tokenizer.decode([int(tok)]) for tok in top_ids[0].tolist()]
        logits_available = True
        error = None
    except Exception as exc:
        logits_available = False
        error = str(exc)
        entropy = math.nan
        top1_prob = math.nan
        topk_mass = math.nan
        top_tokens = []
    summary = {
        "summary_status": "PASS",
        "logits_available": logits_available,
        "logprobs_available": logits_available,
        "logprob_source": "local_logits_softmax" if logits_available else None,
        "top1_probability": top1_prob,
        "topk_mass": topk_mass,
        "entropy": entropy,
        "top_tokens": top_tokens,
        "error": error,
        "training_executed": False,
        "full_matrix_executed": False,
    }
    write_json(args.output_dir / "dualscope_first_slice_logprob_capability_probe.json", summary)
    write_json(args.output_dir / "dualscope_first_slice_logits_probe.json", {"summary_status": "PASS", "logits_available": logits_available, "error": error})
    write_json(args.output_dir / "dualscope_first_slice_logprobs_probe.json", {"summary_status": "PASS", "logprobs_available": logits_available, "source": "local_logits_softmax" if logits_available else None})
    write_json(args.output_dir / "dualscope_first_slice_topk_probability_probe.json", {"summary_status": "PASS", "top1_probability": top1_prob, "topk_mass": topk_mass, "top_tokens": top_tokens})
    write_json(args.output_dir / "dualscope_first_slice_entropy_probe.json", {"summary_status": "PASS", "entropy": entropy})
    markdown(args.output_dir / "dualscope_first_slice_logprob_capability_report.md", "DualScope Logprob Capability Probe", [
        f"- Logits available: `{logits_available}`",
        f"- Logprob source: `{summary['logprob_source']}`",
        f"- Error: `{error}`",
        "- This is local logits-derived probability evidence, not a remote API logprobs claim.",
    ])
    print(f"Logits/logprobs available: {logits_available}")
    return 0 if logits_available else 2


if __name__ == "__main__":
    raise SystemExit(main())

