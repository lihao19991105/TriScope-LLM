# DualScope Cross-Model Validation Plan

Final verdict: `Partially validated`.

This is a planning artifact for SCI3 cross-model validation. It does not run a model, train a model, execute the full matrix, extract logprobs, or report new detection metrics.

## Allowed Cross-Model Axis

Only the following models are eligible for this validation step:

| Model | Role | Current local status | Planning status |
| --- | --- | --- | --- |
| `Llama-3.1-8B-Instruct` | Cross-model validation | Not found in checked local paths or checked HF cache names | `planned` / `external-resource-required` |
| `Mistral-7B-Instruct-v0.3` | Cross-model validation | Not found in checked local paths or checked HF cache names | `planned` / `external-resource-required` |

No fallback model is substituted for cross-model validation. `Qwen2.5-1.5B-Instruct` remains pilot/debug/automation/ablation only, and `Qwen2.5-7B-Instruct` remains the main model axis.

## Input State

| Input | Status | Handling |
| --- | --- | --- |
| `outputs/dualscope_sci3_main_experiment_expansion_plan/default` | Missing in this worktree | Recorded as an input gap; not treated as execution evidence |
| `.reports/dualscope_task_verdicts/dualscope-sci3-main-experiment-expansion-plan-repair.json` | Present and validated | Used as tracked planning handoff |
| `docs/dualscope_sci3_model_matrix.md` | Present | Used as model-role and resource-readiness contract |

## Execution Contract

Cross-model validation must be a matched generalization check against the Qwen2.5-7B main path:

- Use identical row IDs where possible.
- Use identical dataset, trigger family, target family, labels, score schema, and budget policy.
- Run Stage 1 illumination screening and Stage 2 confidence verification under the same capability declaration.
- Run Stage 3 budget-aware fusion only on aligned Stage 1 / Stage 2 evidence.
- Report cross-model results only from real model responses and real aligned artifacts.

## Minimal First Slice

The first executable cross-model slice should be:

| Axis | Planned first slice |
| --- | --- |
| Dataset | Stanford Alpaca, matched to the Qwen2.5-7B main-path first stable slice |
| Trigger family | First available validated main-path trigger family |
| Target family | First available validated main-path target family |
| Capability mode | `without_logprobs` unless real token logprobs are available |
| Output scope | Response rows, Stage 1 evidence, Stage 2 evidence, Stage 3 fusion, metric package, budget trace |

AdvBench, JBB-Behaviors, additional triggers, additional targets, and with-logprobs rows are later expansions after the matched first slice validates.

## Required Gates Before Execution

- One allowed model is locally materialized.
- Tokenizer/config files are present.
- Disk footprint and dtype plan are recorded.
- GPU memory plan is recorded for the local 2 x RTX 3090 environment.
- Deterministic seed and generation parameters are configured.
- Qwen2.5-7B main-path row IDs, labels, response artifacts, score fields, and budget traces exist.
- Benchmark truth and gate files remain unchanged.

## Non-Claims

This plan does not claim:

- Llama or Mistral resources are available.
- Cross-model responses exist.
- Cross-model logprobs exist.
- Cross-model AUROC, F1, precision, recall, ASR, clean utility, latency, or query-cost metrics exist.
- Full-paper model generalization has been demonstrated.

## Next Step

Materialize either `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3`, then rerun the resource check. If both remain missing, cross-model validation stays planned and external-resource-required.
