# DualScope Confidence Feature Dictionary

## With-Logprobs Features

### Confidence / Concentration

- `average_top1_probability`: average token-level top-1 probability over the verification window.
- `target_token_probability_mean`: mean probability assigned to target-aligned tokens when identifiable.
- `topk_mass_concentration`: concentration of mass inside the top-k token set.
- `peak_probability`: highest observed token probability.
- `probability_variance_collapse`: evidence that token probabilities collapse into a narrow high-confidence band.

### Entropy / Uncertainty

- `entropy_mean`: average token entropy.
- `entropy_drop`: overall decrease in entropy during generation.
- `entropy_collapse_span`: longest low-entropy span.
- `uncertainty_decay_rate`: rate at which uncertainty declines.

### Lock / Persistence

- `lock_window_length`: verification window length satisfying a lock condition.
- `longest_lock_span`: longest continuous locked subsequence.
- `sustained_high_confidence_ratio`: fraction of tokens staying in a high-confidence state.
- `lock_reentry_count`: number of times the sequence re-enters a locked state.
- `sequence_lock_strength`: aggregated lock strength score for with-logprobs mode.

### Shared Support Fields

- `target_alignment_proxy`
- `generation_consistency_flag`
- `abnormal_lock_bucket`

## Without-Logprobs Fallback Features

### Repeated Sampling

- `repeated_sampling_consistency`
- `answer_mode_collapse`
- `sampled_output_agreement_rate`

### Lexical / Structural Lock Proxies

- `repeated_phrase_concentration`
- `target_pattern_repetition_proxy`
- `response_diversity_drop`
- `lexical_lock_proxy`

### Cross-Run Stability

- `multi_run_output_collapse`
- `candidate_output_mode_count`
- `instability_inverse_proxy`

### Fallback Risk / Degradation

- `fallback_lock_risk_score`
- `fallback_mode_limit_flag`
- `verification_confidence_degradation_flag`

## Shared Public Outputs

Regardless of mode, Stage 2 exports:

- `capability_mode`
- `verification_risk_score`
- `verification_risk_bucket`
- `confidence_lock_evidence_present`
- `stage1_candidate_id`
- `stage1_screening_risk`
- `budget_usage_summary`

These are the fields that future Stage 3 fusion should read first.
