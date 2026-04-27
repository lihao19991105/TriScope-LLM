# DualScope AdvBench Small-Slice Materialization

This task creates a bounded AdvBench small-slice from an authorized local source or the explicitly authorized public Hugging Face dataset `walledai/AdvBench`. If the source cannot be read, it writes explicit blocker artifacts and does not fabricate data.

Run:

```bash
.venv/bin/python scripts/build_dualscope_advbench_small_slice_materialization.py \
  --dataset-source walledai/AdvBench \
  --output-jsonl data/advbench/small_slice/advbench_small_slice_source.jsonl \
  --output-dir outputs/dualscope_advbench_small_slice_materialization/default \
  --max-examples 32 \
  --allow-download

.venv/bin/python scripts/build_post_dualscope_advbench_small_slice_materialization_analysis.py \
  --output-dir outputs/dualscope_advbench_small_slice_materialization_analysis/default
```

Outputs:

- `data/advbench/small_slice/advbench_small_slice_source.jsonl`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_manifest.json`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_schema_check.json`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_materialization_summary.json`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_blockers.json`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_report.md`
- `outputs/dualscope_advbench_small_slice_materialization/default/advbench_small_slice_verdict.json`

Standardized rows include `sample_id`, `dataset_id`, `instruction`, `input`, `reference_response`, `expected_behavior`, `safety_category`, `source_dataset`, `source_split`, and `source_index`.

The task is materialization only. It does not generate model responses, compute metrics, modify benchmark truth, or run a full matrix.
