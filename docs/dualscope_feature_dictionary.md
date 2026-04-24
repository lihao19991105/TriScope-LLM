# DualScope Stage 1 Feature Dictionary

## Overview

This file explains the frozen feature schema for **DualScope Stage 1: Illumination Screening**.

The schema is machine-readable in:

- `outputs/dualscope_illumination_screening_freeze/default/dualscope_illumination_feature_schema.json`

## Template-Level Features

### `target_behavior_gain`

- Meaning: how much the probe moves the output toward the suspicious target behavior
- Type: `float`
- Used by: Stage 1, future fusion

### `response_flip_indicator`

- Meaning: whether the response flips relative to the benign expectation
- Type: `int`
- Used by: Stage 1, future fusion

### `target_shift_indicator`

- Meaning: whether the response shifts toward the suspicious target
- Type: `int`
- Used by: Stage 1, future confidence, future fusion

### `template_local_instability`

- Meaning: instability caused by the local template shell
- Type: `float`
- Used by: Stage 1, future fusion

### `probe_response_length_delta`

- Meaning: length change relative to the expected clean response footprint
- Type: `float`
- Used by: Stage 1 as supporting evidence only

### `template_trigger_susceptibility_proxy`

- Meaning: template-local abnormal susceptibility proxy
- Type: `float`
- Used by: Stage 1, future confidence, future fusion

## Query-Level Aggregated Features

### `flip_rate`

- Meaning: fraction of templates that induce a response flip

### `gain_mean`

- Meaning: average target behavior gain over enabled templates

### `gain_max`

- Meaning: strongest target behavior gain over enabled templates

### `cross_template_instability`

- Meaning: instability aggregated across the template family

### `risk_count`

- Meaning: how many templates cross a suspicious local threshold

### `template_agreement_score`

- Meaning: how consistently templates point in the same suspicious direction

### `abnormal_target_alignment_rate`

- Meaning: fraction of templates aligned with the suspicious target behavior

## Aggregated Risk Fields

### `screening_risk_score`

- Meaning: primary Stage 1 screening score
- Output role: routing signal for Stage 2

### `screening_risk_bucket`

- Meaning: `low`, `medium`, or `high`
- Output role: lightweight discrete screening summary

### `confidence_verification_candidate`

- Meaning: whether the case should enter Stage 2
- Output role: explicit stage handoff flag

### `budget_consumption_ratio`

- Meaning: consumed Stage 1 budget divided by allocated Stage 1 budget
- Output role: budget-aware downstream metadata

### `screening_summary_for_fusion`

- Meaning: compact public feature package reserved for Stage 3
- Output role: stable public fusion interface
