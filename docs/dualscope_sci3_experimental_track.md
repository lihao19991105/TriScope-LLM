# DualScope SCI3 Experimental Track

This track upgrades DualScope from a 1.5B first-slice pilot into a SCI3-ready experimental plan while preserving staged execution.

## Model Roles

- `Qwen2.5-1.5B-Instruct`: pilot, debug, automation smoke, and ablation support. It is not the only main experimental model.
- `Qwen2.5-7B-Instruct`: main experimental model for the primary detection table, main ablations, query-cost analysis, and first controlled expansion.
- `Llama-3.1-8B-Instruct` or `Mistral-7B-Instruct-v0.3`: cross-model validation. If local weights are unavailable, mark `planned` / `external-resource-required`; do not claim results.

## Dataset Matrix

- Stanford Alpaca: instruction-following substrate and first controlled main path.
- AdvBench: harmfulness and adversarial behavior stress path.
- JBB-Behaviors: jailbreak / risky-behavior validation path.

## Trigger Matrix

- Lexical trigger.
- Semantic trigger.
- Contextual / instruction trigger.

## Target Behavior Matrix

- Fixed response target.
- Behavior-shift / harmfulness-shift target.

## Execution Strategy

1. Qwen2.5-7B first-slice response generation.
2. Qwen2.5-7B label-aligned metrics.
3. Qwen2.5-7B first-slice result package.
4. SCI3 main expansion plan across datasets / triggers / targets.
5. Cross-model validation plan.

Do not run the full matrix at once. Do not fake model responses, logprobs, AUROC, F1, ASR, clean utility, benchmark truth, or gates.
