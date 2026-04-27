# DualScope JBB Small-Slice Data Allowlist

This note records the narrow safe merge allowance for bounded JBB materialization.

Allowed file:

- `data/jbb/small_slice/jbb_small_slice_source.jsonl`

Required diagnostics:

- `allowed_jbb_small_slice_files`
- `jbb_small_slice_row_count`
- `jbb_small_slice_schema_valid`
- `jbb_small_slice_source_dataset`
- `blocked_data_files`
- `file_scope_allowed`

The allowance is not recursive and does not permit full, raw, or unrelated data files.
