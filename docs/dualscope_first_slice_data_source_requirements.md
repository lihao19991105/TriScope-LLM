# DualScope First Slice Data Source Requirements

Provide a real Alpaca-style JSON or JSONL file. Accepted field families:

- `instruction`, `input`, `output`
- `prompt`, `response`
- `query`, `target`

The materialized JSONL must contain:

- `example_id`
- `dataset_id`
- `instruction`
- `input`
- `prompt`
- `response`
- `split`
- `source`
- `metadata`

Synthetic placeholders are not accepted as real data.
