# DualScope First Slice Data / Model Contract

## Data

- Dataset ID: `stanford_alpaca`
- Required path: `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`
- Required fields: `instruction`, `input`, `output`
- Planned clean size: 32
- Planned poisoned size: 8
- Planned validation size: 16
- Planned eval size: 16

## Model

- Model ID: `Qwen/Qwen2.5-1.5B-Instruct`
- Local path: `/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct`
- Training mode: LoRA / QLoRA only
- Full fine-tuning: disallowed
- Resource boundary: 2 x RTX 3090

