# DualScope Experimental Matrix

This document summarizes the frozen experiment matrix for DualScope-LLM. It is a planning and contract layer, not a full experiment execution.

## Minimum Datasets

- Stanford Alpaca: general instruction-following and clean utility baseline.
- AdvBench: adversarial / harmful instruction behavior.
- JBB-Behaviors: jailbreak and behavior-level risk coverage.

Future datasets may be listed as expansion hooks, but they are not part of the first minimum matrix.

## Minimum Models

- Qwen2.5-1.5B-Instruct: primary development and ablation axis.
- Qwen2.5-7B-Instruct: limited 7B-class validation axis.
- Mistral-7B-Instruct or Llama-3.1-8B-Instruct: optional cross-model sanity check.

Full fine-tuning is not part of the matrix. LoRA / QLoRA / adapter-level construction is the intended backdoor construction strategy.

## Trigger and Target Families

The minimum trigger families are lexical, semantic, and contextual / instruction triggers. Sleeper-style triggers are future-only. The minimum target families are fixed response / refusal-bypass and behavior / harmfulness shift targets.

## Capability Modes

DualScope explicitly distinguishes `with_logprobs` and `without_logprobs`. The latter is a formal fallback with weaker evidence and must carry degradation flags.

## Baselines

- Illumination-only
- Confidence-only with logprobs
- Confidence-only without logprobs
- Naive concat
- DualScope budget-aware two-stage fusion

## First Slice

The recommended first executable slice is Stanford Alpaca + Qwen2.5-1.5B-Instruct + lexical trigger + fixed response target, using without-logprobs by default and with-logprobs if the local backend exposes token scores.

