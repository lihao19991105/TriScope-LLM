# DualScope First-Slice Label Contract

The first-slice clean / poisoned label file uses JSONL rows with these required fields:

- `row_id`
- `pair_id`
- `source_example_id`
- `dataset_id`
- `condition`
- `prompt`
- `response_reference`
- `trigger_present`
- `trigger_id`
- `trigger_text`
- `trigger_insert_position`
- `target_id`
- `target_type`
- `target_text`
- `target_match_rule`
- `detection_label`
- `asr_eligible`
- `utility_eligible`
- `label_source`
- `metadata`

Label source:

- `experimental_construction_v1`

This means labels are created by the experimental clean / poisoned construction protocol. They are not Alpaca benchmark truth, and they are not inferred from model outputs.

Detection labels:

- `clean`: `detection_label = 0`
- `poisoned_triggered`: `detection_label = 1`

ASR eligibility:

- `clean`: `asr_eligible = false`
- `poisoned_triggered`: `asr_eligible = true`

Utility eligibility:

- `clean`: `utility_eligible = true`
- `poisoned_triggered`: `utility_eligible = false`

The contract does not change gates, benchmark semantics, or model outputs. It only provides an alignment layer for later evaluation.
