# DualScope SCI3 Resource Plan for 2x3090

## Hardware Assumption

The SCI3 track assumes a 2 x RTX 3090 development environment.

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
