# DualScope SCI3 Model Resource Requirements

## Main Model

- Model ID: `Qwen/Qwen2.5-7B-Instruct`
- Role: main experimental model
- Preferred local path: `models/qwen2p5-7b-instruct`
- Fallback: Hugging Face cache / snapshot path recorded in materialization artifacts

The main model must pass tokenizer and config checks before any Qwen2.5-7B response-generation task is treated as ready.

## Local Resource Checks

Before download or response generation:

- check free disk with a conservative threshold
- check GPU visibility
- record source revision / snapshot path when downloaded
- record tokenizer and config load results
- avoid full model load unless explicitly enabled

## Cross-Model Candidates

- `meta-llama/Llama-3.1-8B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.3`

These are planned cross-model validation candidates only. If they require authentication, license acceptance, or external resources, record `external-resource-required`. Do not download or claim availability without authorization.

## Prohibited Claims

- No fake model path.
- No fake download success.
- No fake response generation.
- No fake AUROC/F1/ASR/clean utility.
- No benchmark truth or gate changes.

