# DualScope Cross-Model Validation Plan Repair

Final verdict: `Cross-model validation plan repair validated`.

This is a planning repair artifact. It does not download gated models, generate responses, train models, run the full matrix, extract logprobs, or report new detection metrics.

## Repair Finding

The prior cross-model validation plan was `Partially validated` because durable planning files existed but the ignored prior output directory was unavailable and no Llama/Mistral resource was local. This repair closes the planning gate by documenting those missing resources as planned external requirements rather than treating them as execution evidence.

## Model Role Contract

| Model | Role | Local observation | Planning status |
| --- | --- | --- | --- |
| `Qwen2.5-7B-Instruct` | SCI3 main model | `/mnt/sda3/lh/models/qwen2p5-7b-instruct` exists with config, tokenizer, and safetensors shard files | Main model resource visible; not a response or metric claim |
| `Qwen2.5-1.5B-Instruct` | Pilot / debug / automation / ablation only | `/home/lh/TriScope-LLM/local_models/Qwen2.5-1.5B-Instruct` exists | Not eligible as sole SCI3 main-table or cross-model evidence |
| `Llama-3.1-8B-Instruct` | Cross-model validation candidate | Not found in checked local, mounted, or HF-cache paths | `planned` / `external-resource-required` |
| `Mistral-7B-Instruct-v0.3` | Cross-model validation candidate | Not found in checked local, mounted, or HF-cache paths | `planned` / `external-resource-required` |

## Candidate Availability Matrix

| Candidate | Checked path classes | Availability | Blocker |
| --- | --- | --- | --- |
| `meta-llama/Llama-3.1-8B-Instruct` | worktree `local_models`, shared `/home/lh/TriScope-LLM/local_models`, mounted `/mnt/sda3/lh/local_models`, mounted `/mnt/sda3/lh/models`, HF cache roots | missing | external resource, likely gated license/auth |
| `mistralai/Mistral-7B-Instruct-v0.3` | worktree `local_models`, shared `/home/lh/TriScope-LLM/local_models`, mounted `/mnt/sda3/lh/local_models`, mounted `/mnt/sda3/lh/models`, HF cache roots | missing | external resource and license/auth confirmation |

## Execution Guardrails

- Do not substitute Qwen2.5-1.5B for cross-model validation.
- Do not claim Llama or Mistral availability until a real local path with tokenizer/config files exists.
- Do not report cross-model AUROC, F1, precision, recall, ASR, utility, latency, or query-cost metrics from this plan.
- Use `without_logprobs` unless the selected backend produces real token logprob artifacts.
- Keep benchmark truth and gate files unchanged.

## Next-Step Recommendation

The queue can close this planning repair with `queue_complete`.

Future cross-model execution should start with a separate resource materialization task for exactly one allowed candidate, followed by a matched first-slice preflight. That future task should not run until license/auth access is resolved and the local candidate path is verified.

## PR Workflow Status

Local commit failed because the shared git worktree metadata path is read-only:

```text
fatal: Unable to create '/home/lh/TriScope-LLM/.git/worktrees/cross-model-validation-plan-repair-20260426135217/index.lock': Read-only file system
```

A GitHub fallback branch creation call for `codex/cross-model-validation-plan-repair` was attempted and cancelled by the connector. No remote mutation was completed.
