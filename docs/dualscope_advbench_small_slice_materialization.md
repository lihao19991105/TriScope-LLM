# DualScope AdvBench Small-Slice Materialization

This task creates a bounded AdvBench small-slice manifest only if an authorized local source exists. If no source is available, it writes explicit blocker artifacts and does not fabricate data.

Run:

```bash
.venv/bin/python scripts/build_dualscope_advbench_small_slice_materialization.py
```

Outputs:

- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_manifest.json`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_schema_check.json`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_blockers.json`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_report.md`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_verdict.json`
