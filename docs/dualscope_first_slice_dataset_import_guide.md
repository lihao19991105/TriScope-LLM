# DualScope First Slice Dataset Import Guide

Use this guide only with a real Alpaca-style source file. Do not generate placeholder rows and do not mark synthetic data as real.

## Supported Source Formats

- JSON array of examples.
- JSON object containing `data`, `examples`, or `rows`.
- JSONL with one object per line.

## Supported Field Families

- `instruction`, `input`, `output`
- `prompt`, `response`
- `query`, `target`

## Build Command

```bash
.venv/bin/python scripts/build_dualscope_first_slice_alpaca_jsonl.py \
  --source-file <REAL_ALPACA_SOURCE_JSON_OR_JSONL> \
  --output-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl \
  --max-examples 72 \
  --seed 2025 \
  --split-name first_slice \
  --dataset-id stanford_alpaca
```

The command writes a manifest next to the output file and records `synthetic_data_generated=false`.

## Schema Check

```bash
.venv/bin/python scripts/check_dualscope_first_slice_dataset_schema.py \
  --dataset-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl \
  --output-dir outputs/dualscope_first_slice_dataset_schema_check/default
```
