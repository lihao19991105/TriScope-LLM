# DualScope SCI3 Resource Plan for 2x3090

## Hardware Assumption

The SCI3 track assumes a 2 x RTX 3090 development environment.

This document is a planning and readiness note. It does not certify that GPU execution succeeded in the current worktree session.

## Execution Priority

1. Use Qwen2.5-1.5B-Instruct for smoke tests and automation debug only.
2. Use Qwen2.5-7B-Instruct for the main first-slice and main controlled expansion.
3. Use Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 only after Qwen2.5-7B evidence is packaged.

## Resource Rules

- Prefer inference-only response generation.
- Do not full finetune.
- Do not LoRA / QLoRA train unless a later task explicitly authorizes it.
- If a model is unavailable locally, record `external-resource-required`.
- Do not fake path availability, responses, logprobs, metrics, or clean utility.

## Planning Readiness

| Item | Status | Note |
| --- | --- | --- |
| Qwen2.5-1.5B-Instruct local pilot path | ready for pilot/debug only | Existing pilot path may support smoke and automation checks, but is not the SCI3 main model |
| Qwen2.5-7B-Instruct local path | external-resource-required | No real local path is confirmed for this planning task |
| Llama-3.1-8B-Instruct local path | external-resource-required | Planned cross-model validation only |
| Mistral-7B-Instruct-v0.3 local path | external-resource-required | Planned cross-model validation only |
| 2x3090 runtime visibility in this session | not runtime-confirmed | `nvidia-smi` could not communicate with the driver in this session |

## Current Worktree Checks

- Observed Qwen2.5-1.5B pilot path: `/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct`.
- Missing Qwen2.5-7B checked paths: `/home/lh/TriScope-LLM/local_models/Qwen2.5-7B-Instruct`, `local_models/Qwen2.5-7B-Instruct`.
- Missing Llama-3.1-8B checked paths: `/home/lh/TriScope-LLM/local_models/Llama-3.1-8B-Instruct`, `local_models/Llama-3.1-8B-Instruct`.
- Missing Mistral-7B checked paths: `/home/lh/TriScope-LLM/local_models/Mistral-7B-Instruct-v0.3`, `local_models/Mistral-7B-Instruct-v0.3`.
- GPU command result: `nvidia-smi` failed to communicate with the NVIDIA driver, so 2x3090 execution is not confirmed in this session.

## Inference-Only Guidance

- Keep the Qwen2.5-7B first-slice successor to response generation planning until a real local path is supplied.
- Use batch size 1 by default for first-slice response generation.
- Prefer `float16` or `bfloat16` inference with `device_map=auto` after GPU visibility is confirmed.
- Keep max sequence length configurable and start from the smallest value that preserves the frozen prompt contract.
- Store capability mode, model path confirmation, fallback flags, and blockers with every future run artifact.

## Execution Blockers

- Qwen2.5-7B-Instruct cannot be treated as executable until a real local model path or explicit external resource is provided.
- Cross-model validation cannot be treated as executable until Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 is locally available or explicitly provisioned.
- No future artifact may claim model responses, logprobs, AUROC, F1, ASR, clean utility, or latency from these models unless those values are produced by a real run and linked to the corresponding run outputs.
