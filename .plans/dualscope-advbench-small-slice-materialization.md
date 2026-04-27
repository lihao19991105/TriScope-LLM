# DualScope AdvBench Small-Slice Materialization

## Purpose / Big Picture

Materialize a bounded AdvBench small slice only when an authorized local source is present. If no source is available, record a real blocker instead of fabricating data.

## Scope

### In Scope

- Search local repository and `/mnt/sda3/lh` roots for AdvBench-like files.
- Build a small JSONL slice and schema check if a source exists.
- Record missing-source blockers if no source exists.

### Out of Scope

- Full AdvBench ingestion.
- Downloading ambiguous or gated resources.
- Model response generation or metrics.

## Validation

```bash
python3 -m py_compile src/eval/dualscope_advbench_small_slice_materialization.py
.venv/bin/python scripts/build_dualscope_advbench_small_slice_materialization.py --help
.venv/bin/python scripts/build_dualscope_advbench_small_slice_materialization.py
```
