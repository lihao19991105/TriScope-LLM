# DualScope Fusion Protocol

## What Stage 3 Is

DualScope Stage 3 is the **budget-aware policy and fusion layer**.

It does two things together:

1. decides whether Stage 2 verification should be triggered
2. combines Stage 1 and Stage 2 evidence into the final DualScope risk decision

This is why Stage 3 is not just score concatenation.

## Why Two-Stage and Budget-Aware

Stage 1 is cheap enough for broad screening.
Stage 2 is more expensive and should be selective.

So Stage 3 formalizes:

- when Stage 1 is enough
- when Stage 2 is worth spending budget on
- how capability mode changes the interpretation of verification evidence

## Minimal Data Flow

1. Stage 1 emits screening risk, candidate flag, and budget metadata.
2. Stage 3 checks trigger policy.
3. If policy says no, Stage 3 returns a Stage-1-retained decision.
4. If policy says yes, Stage 3 consumes Stage 2 verification outputs.
5. Stage 3 applies capability-aware weighting and degradation-aware adjustment.
6. Stage 3 emits final risk, final bucket, final decision, and budget accounting.

## Capability Awareness

### With-logprobs

- verification evidence is stronger
- verification gets higher fusion weight

### Without-logprobs

- verification evidence is weaker
- degradation flags must remain visible
- final decision should remain more conservative

## Output Shape

Stage 3 always emits:

- `final_risk_score`
- `final_risk_bucket`
- `final_decision_flag`
- `verification_triggered`
- `capability_mode`
- `evidence_summary`
- `budget_usage_summary`

These are the fields that later experiments and paper tables should consume.
