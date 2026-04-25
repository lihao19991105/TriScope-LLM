# DualScope SCI3 Model Matrix

This document is the role contract for the SCI3 model axis. It is a planning artifact, not an experiment result.

## Roles

| Model | Role | Use | Current readiness |
| --- | --- | --- |
| Qwen2.5-1.5B-Instruct | pilot / debug / automation / ablation only | Smoke tests, protocol checks, low-cost ablations, script debugging | Local pilot path exists in the known development environment; not eligible as the sole main-table model |
| Qwen2.5-7B-Instruct | main experimental model | Main table, main ablation, query-cost analysis, first-slice and main controlled slices | Planned; local 7B path is not confirmed in this worktree and must be supplied before execution |
| Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 | cross-model validation | Generalization checks after Qwen2.5-7B first-slice evidence is packaged | Planned; external resource required unless a real local 7B/8B path is supplied |

## Availability Rules

- Do not invent local model paths.
- If 7B / 8B weights are missing, mark `external-resource-required`.
- Do not present planned cross-model validation as completed evidence.
- Do not present 1.5B pilot results as the SCI3 main model-axis result.
- Do not report projected or placeholder detection metrics as real AUROC, F1, ASR, clean utility, or cost-effectiveness evidence.

## Current Worktree Readiness Evidence

Checked during `dualscope-main-model-axis-upgrade-plan`:

| Model | Checked local path | Observed status | Planning consequence |
| --- | --- | --- | --- |
| Qwen2.5-1.5B-Instruct | `/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct` | exists | Pilot/debug/automation/ablation only |
| Qwen2.5-7B-Instruct | `/home/lh/TriScope-LLM/local_models/Qwen2.5-7B-Instruct` and `local_models/Qwen2.5-7B-Instruct` | missing | Main model is planned / external-resource-required before execution |
| Llama-3.1-8B-Instruct | `/home/lh/TriScope-LLM/local_models/Llama-3.1-8B-Instruct` and `local_models/Llama-3.1-8B-Instruct` | missing | Cross-model validation is planned / external-resource-required |
| Mistral-7B-Instruct-v0.3 | `/home/lh/TriScope-LLM/local_models/Mistral-7B-Instruct-v0.3` and `local_models/Mistral-7B-Instruct-v0.3` | missing | Cross-model validation is planned / external-resource-required |

## Main-Table Eligibility

| Evidence type | Eligible model axis |
| --- | --- |
| Main detection table | Qwen2.5-7B-Instruct |
| Main ablations | Qwen2.5-7B-Instruct, with clearly labeled 1.5B low-cost ablation if needed |
| Query budget / cost analysis | Qwen2.5-7B-Instruct |
| Automation smoke | Qwen2.5-1.5B-Instruct |
| Cross-model validation | Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 after Qwen2.5-7B packaging |

## Sequence

1. Validate SCI3 model-axis plan.
2. Prepare Qwen2.5-7B first-slice response generation.
3. Run or explicitly block Qwen2.5-7B first-slice response generation.
4. Package Qwen2.5-7B first-slice evidence.
5. Plan cross-model validation.

## Current Planning Verdict

`SCI3 main model axis upgrade plan validated` means the role contract and readiness blockers are documented. It does not mean Qwen2.5-7B, Llama-3.1-8B, or Mistral-7B experiments have run.
