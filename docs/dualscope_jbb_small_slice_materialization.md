# DualScope JBB Small-Slice Materialization

This task materializes a bounded JBB-Behaviors small slice from an authorized local CSV or the public Hugging Face dataset `JailbreakBench/JBB-Behaviors`. If source access, license verification, network download, or schema validation fails, it writes blocker artifacts and does not fabricate rows.

Run:

```bash
python3 scripts/build_dualscope_jbb_small_slice_materialization.py \
  --dataset-source JailbreakBench/JBB-Behaviors \
  --output-jsonl data/jbb/small_slice/jbb_small_slice_source.jsonl \
  --output-dir outputs/dualscope_jbb_small_slice_materialization/default \
  --max-examples 16 \
  --allow-download
```

Outputs:

- `data/jbb/small_slice/jbb_small_slice_source.jsonl`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_manifest.json`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_schema_check.json`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_blockers.json`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_report.md`
- `outputs/dualscope_jbb_small_slice_materialization/default/jbb_small_slice_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-materialization.json`

Standardized rows include `sample_id`, `dataset_id`, `source_dataset`, `source_url`, `source_split`, `source_index`, `behavior_category`, `behavior_text`, `trigger_family`, `trigger_text`, `target_family`, `target_descriptor`, `split`, `license_status`, `safety_notes`, and `readiness_notes`.

Boundary:

- No model responses are generated.
- No AUROC, F1, ASR, clean utility, refusal, or safety metrics are computed.
- No labels, logprobs, benchmark truth, or gates are fabricated or changed.
- No full matrix, training, route_c continuation, or `199+` planning is executed.
