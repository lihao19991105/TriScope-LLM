# DualScope First Slice Dataset Materialization

This stage materializes `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl` from a real user-provided Alpaca-style source file.

It does not download data, fabricate data, train models, or run the first-slice real run.

## Command

```bash
.venv/bin/python scripts/build_dualscope_first_slice_dataset_materialization.py \
  --source-file <REAL_ALPACA_SOURCE_JSON_OR_JSONL> \
  --output-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl \
  --output-dir outputs/dualscope_first_slice_dataset_materialization/default \
  --schema-check-output-dir outputs/dualscope_first_slice_dataset_schema_check/default \
  --max-examples 72 --seed 2025 --split-name first_slice --dataset-id stanford_alpaca
```
