# DualScope Ablation Contract

## Required Baselines

Stage 3 freezes the comparison contract for the following baselines:

1. illumination-only
2. confidence-only with-logprobs
3. confidence-only without-logprobs
4. naive concat
5. budget-aware two-stage fusion

## Why These Baselines

- `illumination-only` checks how far Stage 1 can go alone
- `confidence-only` checks the isolated utility of verification evidence
- `naive concat` checks whether simple juxtaposition is enough
- `budget-aware two-stage fusion` tests the full DualScope method claim

## Required Comparison Fields

All later ablation and main-experiment tables should read:

- `final_risk_score`
- `final_decision_flag`
- `verification_triggered`
- `capability_mode`
- `budget_consumption_ratio`

## Cost Analysis Interface

Later cost tables should also expose:

- screening query cost
- verification query cost
- total budget consumption
- verification trigger rate
- mode-specific verification cost

## Important Boundary

This contract freezes **how later experiments should compare methods**.
It does not itself run the full experimental matrix yet.
