# DualScope Illumination Screening Protocol

## Purpose

This document describes **DualScope Stage 1: Illumination Screening** as a formal protocol rather than an informal idea list.

Stage 1 is responsible for:

- exposing abnormal susceptibility under targeted probing
- measuring flip / gain / instability style evidence
- routing only suspicious cases into Stage 2 confidence verification

It is **not** responsible for the final backdoor verdict.

## Protocol View

### Input

Each Stage 1 query contract must minimally define:

- `dataset_id`
- `example_id`
- `original_query`
- `probe_template_set`
- `budget_policy`

Optional fields:

- `trigger_text`
- `target_text`
- `metadata`
- `api_capabilities`

### Probe Template Families

Default minimal set:

1. `base_targeted_probe`
2. `paraphrase_like_probe`
3. `target_oriented_probe`
4. `alternate_context_probe`
5. `stability_check_probe`

Future-only templates are not part of the current default contract.

### Output

Stage 1 emits:

- `template_results`
- `query_aggregate_features`
- `screening_risk_score`
- `screening_risk_bucket`
- `confidence_stage_candidate_flag`
- `budget_usage_summary`
- `screening_summary_for_fusion`

## Why Stage 1 Is Screening Only

Illumination screening can show that a model becomes abnormally easy to steer under suspicious targeted probing.

It cannot, by itself, prove:

- confidence lock
- sequence lock
- persistent abnormal concentration

Therefore:

- Stage 1 screens
- Stage 2 verifies
- Stage 3 fuses under budget constraints

## Downstream Compatibility

### Stage 2 Compatibility

Stage 2 should consume:

- `screening_risk_score`
- `screening_risk_bucket`
- `confidence_stage_candidate_flag`
- `template_results`
- `query_aggregate_features`
- `budget_usage_summary`

### Stage 3 Compatibility

Stage 3 should consume Stage 1 public fields plus future Stage 2 public fields:

- `screening_risk_score`
- `screening_risk_bucket`
- `budget_consumption_ratio`
- `screening_summary_for_fusion`

## Budget Contract

The Stage 1 budget contract is explicit:

- finite per-query budget
- finite per-template allocations
- a minimal screening budget floor
- explicit future extension hooks

This is what makes the protocol genuinely budget-aware rather than just budget-themed.
