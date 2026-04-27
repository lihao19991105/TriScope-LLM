# DualScope JBB Small-Slice Response Generation Repair

This package audits the bounded JBB response-generation artifacts and writes a compact repair verdict. It does not generate new model responses, compute metrics, infer logprobs, change benchmark truth, change gates, train, or run a full matrix.

Default command:

```bash
python3 scripts/build_dualscope_jbb_small_slice_response_generation_repair.py \
  --response-dir outputs/dualscope_jbb_small_slice_response_generation/default \
  --output-dir outputs/dualscope_jbb_small_slice_response_generation_repair/default \
  --registry-path .reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation-repair.json \
  --seed 20260427
```

Outputs:

- `jbb_small_slice_response_generation_repair_summary.json`
- `jbb_small_slice_response_generation_repair_availability_matrix.json`
- `jbb_small_slice_response_generation_repair_blocker_compression.json`
- `jbb_small_slice_response_generation_repair_row_audit.json`
- `jbb_small_slice_response_generation_repair_compact_rows.jsonl`
- `jbb_small_slice_response_generation_repair_verdict.json`
- `jbb_small_slice_response_generation_repair_report.md`

The Markdown report and compact rows intentionally omit harmful prompts and model completions.
