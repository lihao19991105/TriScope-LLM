# DualScope SCI3 Metrics and Tables

## Metrics

- AUROC
- AUPRC
- F1
- Accuracy
- TPR@low-FPR
- ASR
- Target behavior success
- Clean utility
- Utility drop
- Average query cost
- Verification trigger rate
- Cost-normalized AUROC

Metrics are computed only when the required labels, scores, and real model responses align. Projected or placeholder values must never be reported as real performance.

## Planned Tables

- Table 1: Overall Detection Performance
- Table 2: Query Cost / Budget Trade-off
- Table 3: Robustness
- Table 4: Ablation
- Table 5: Cross-model Generalization

## Baselines

- Illumination-only
- Confidence-only with-logprobs
- Confidence-only without-logprobs
- Naive concat
- DualScope budget-aware fusion
