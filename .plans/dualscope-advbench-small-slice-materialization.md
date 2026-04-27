# DualScope AdvBench Small-Slice Materialization

## Purpose / Big Picture

Materialize a bounded AdvBench small slice from an authorized local source or the explicitly authorized public Hugging Face source `walledai/AdvBench`. If no source is available or the public source cannot be read, record a real blocker instead of fabricating data.

## Scope

### In Scope

- Search local repository and `/mnt/sda3/lh` roots for AdvBench-like files.
- Use `walledai/AdvBench` when `--allow-download` is provided.
- Build a small JSONL slice and schema check if a source exists.
- Record missing-source blockers if no source exists.

### Out of Scope

- Full AdvBench ingestion.
- Downloading ambiguous or gated resources.
- Downloading anything beyond the bounded public small-slice need.
- Model response generation or metrics.

## Validation

```bash
python3 -m py_compile src/eval/dualscope_advbench_small_slice_materialization.py
.venv/bin/python scripts/build_dualscope_advbench_small_slice_materialization.py --help
.venv/bin/python scripts/build_dualscope_advbench_small_slice_materialization.py \
  --dataset-source walledai/AdvBench \
  --output-jsonl data/advbench/small_slice/advbench_small_slice_source.jsonl \
  --output-dir outputs/dualscope_advbench_small_slice_materialization/default \
  --max-examples 32 \
  --allow-download
```
