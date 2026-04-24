# DualScope Minimal First Slice Real-Run Plan

This document describes the first real-run plan after the controlled first-slice smoke. It is a planning package, not a completed real experiment.

## Frozen Scope

- Dataset: Stanford Alpaca
- Model: Qwen2.5-1.5B-Instruct
- Trigger: lexical trigger
- Target: fixed response / fixed target behavior
- Capability mode: try with-logprobs, fallback to without-logprobs with degradation flag
- Baselines: illumination-only, confidence-only, DualScope budget-aware fusion

## Dataset Requirement

The real run requires a local Alpaca-format JSONL at `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl` with `instruction`, `input`, and `output` fields. If the file is missing, the future preflight must stop and must not fabricate data.

## Model Requirement

The plan expects `/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct`. No full fine-tuning is allowed. Real training, if later executed, should use LoRA / QLoRA within the 2 x RTX 3090 boundary.

## Execution Flow

1. Build the clean first-slice data.
2. Build the poisoned split with a lexical trigger and fixed target.
3. Optionally train a LoRA/QLoRA adapter after preflight.
4. Run Stage 1 illumination screening.
5. Run Stage 2 confidence verification on candidates.
6. Run Stage 3 budget-aware fusion.
7. Evaluate placeholders and generate report artifacts.

## Important Boundary

This plan does not claim that training, inference, or real detection performance has already happened.

