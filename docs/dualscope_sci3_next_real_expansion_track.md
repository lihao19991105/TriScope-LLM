# DualScope SCI3 Next Real Expansion Track

This document defines the next small-step SCI3 expansion after the completed Qwen2.5-7B first-slice smoke chain.

## Current Evidence Boundary

- The current Qwen2.5-7B evidence is a first-slice smoke result.
- It includes 8 real Qwen2.5-7B responses.
- Detection metrics and ASR are reportable only for this first-slice scope.
- Clean utility remains blocked because explicit utility success or reference-match fields are not yet available.
- Cross-model validation is readiness planning only; it does not represent completed Llama or Mistral experiments.

These results must not be described as full paper performance.

## Model Roles

- `Qwen2.5-7B-Instruct`: main experimental model.
- `Qwen2.5-1.5B-Instruct`: pilot, debug, automation, and ablation support.
- `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3`: cross-model validation candidates only after resources and license are confirmed.

## Expansion Priority

1. Qwen2.5-7B + Stanford Alpaca main-slice expansion.
2. Qwen2.5-7B semantic trigger smoke.
3. Qwen2.5-7B behavior-shift target smoke.
4. AdvBench small-slice readiness.
5. JBB-Behaviors small-slice readiness.
6. Cross-model validation only if model resources and license are ready.

## Queue Entry Point

The next queue task is:

```text
dualscope-qwen2p5-7b-alpaca-main-slice-plan
```

This is a planning task. It must not execute the full matrix or claim new experimental results.

## Non-Negotiable Limits

- No benchmark truth changes.
- No gate changes.
- No route_c continuation.
- No 199+ generation.
- No fake responses, logprobs, AUROC, F1, ASR, or clean utility.
- No full matrix.
- No model training.
