# DualScope Confidence Verification Protocol

## What Stage 2 Is

DualScope Stage 2 is a **verification** stage. It does not repeat illumination screening and it does not emit the final DualScope verdict.

Its job is:

1. read Stage 1 high-risk candidates
2. verify whether suspicious outputs show abnormal lock / concentration evidence
3. expose that evidence as a structured protocol
4. hand the result to future Stage 3 budget-aware fusion

## Why Two Capability Modes Exist

Real API settings differ:

- some backends expose token-level logprobs
- some backends expose only text outputs

So Stage 2 freezes two explicit modes:

### `with_logprobs`

Used when token-level probabilities are available. This is the primary capability path for:

- concentration
- entropy collapse
- lock span
- sustained high-confidence behavior

### `without_logprobs`

Used as a fallback when token-level probabilities are unavailable. This mode uses:

- repeated sampling consistency
- output-mode collapse
- lexical repetition
- cross-run collapse proxies

This fallback is operationally useful, but it is not claimed to be equivalent to token-level confidence evidence.

## Stage 1 -> Stage 2

Stage 2 consumes Stage 1 fields rather than redefining them. The core routing assumption is:

- Stage 1 decides whether a query is a confidence-verification candidate
- Stage 2 verifies that candidate using the selected capability mode

Important Stage 1 fields include:

- `screening_risk_score`
- `screening_risk_bucket`
- `confidence_verification_candidate_flag`
- `template_results`
- `query_aggregate_features`
- `budget_usage_summary`

## Stage 2 Outputs

Stage 2 emits:

- `verification_feature_vector`
- `verification_evidence_summary`
- `verification_risk_score`
- `verification_risk_bucket`
- `confidence_lock_evidence_present`
- `budget_usage_summary`
- `confidence_public_fields`
- `fusion_public_fields`

## Minimal Example Flow

1. Stage 1 candidate arrives with `screening_risk_score = 0.7479`.
2. Stage 2 selects `with_logprobs` or `without_logprobs`.
3. Stage 2 extracts verification features.
4. Stage 2 forms a `verification_risk_score`.
5. Stage 2 exports a shared public field bundle for Stage 3 fusion.

## What Stage 2 Does Not Do

- It does not perform final backdoor classification by itself.
- It does not change benchmark truth semantics.
- It does not re-introduce reasoning as a default branch.
- It does not implement full Stage 3 fusion inside Stage 2.
