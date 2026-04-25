# DualScope SCI3 Ablation and Robustness Plan

## Ablations

- Stage 1 only vs Stage 2 only vs DualScope fusion.
- With-logprobs vs without-logprobs confidence.
- Fixed verification budget vs risk-triggered verification budget.
- Illumination-only, confidence-only, naive concat, and budget-aware fusion.

## Robustness Axes

- Stanford Alpaca, AdvBench, JBB-Behaviors.
- Lexical, semantic, contextual / instruction triggers.
- Fixed response and behavior-shift / harmfulness-shift targets.
- Qwen2.5-7B main model first, cross-model validation later.

## Safety Boundaries

Do not expand all axes at once. Do not alter benchmark truth or gate definitions. Do not report fake model outputs or fake metrics.
