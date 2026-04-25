# DualScope SCI3 Model Matrix

## Roles

| Model | Role | Use |
| --- | --- | --- |
| Qwen2.5-1.5B-Instruct | pilot / debug / automation / ablation | Smoke tests, protocol checks, low-cost ablations |
| Qwen2.5-7B-Instruct | main experimental model | Main table, main ablation, cost analysis, first-slice and main slices |
| Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 | cross-model validation | Generalization checks after Qwen2.5-7B path is validated |

## Availability Rules

- Do not invent local model paths.
- If 7B / 8B weights are missing, mark `external-resource-required`.
- Do not present planned cross-model validation as completed evidence.

## Sequence

1. Validate SCI3 model-axis plan.
2. Prepare Qwen2.5-7B first-slice response generation.
3. Run or explicitly block Qwen2.5-7B first-slice response generation.
4. Package Qwen2.5-7B first-slice evidence.
5. Plan cross-model validation.
