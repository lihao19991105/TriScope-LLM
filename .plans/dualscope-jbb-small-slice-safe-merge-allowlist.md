# DualScope JBB Small-Slice Safe Merge Allowlist

## Goal

Allow exactly the bounded JBB materialization file produced by the SCI3 AdvBench/JBB queue while keeping all other `data/` paths blocked by default.

## Scope

The only newly allowed data file is:

- `data/jbb/small_slice/jbb_small_slice_source.jsonl`

The safe merge gate still blocks:

- `data/jbb/full/*`
- `data/jbb/raw/*`
- any other unapproved `data/**` file
- secrets, credentials, benchmark truth changes, route_c/199+, and unrelated gate semantic changes

## Validation

The allowlist path is accepted only when all checks pass:

- exact path match
- JSONL format
- row count at most 32
- every line is valid JSON object
- required JBB materialization fields are present
- `source_dataset` equals `JailbreakBench/JBB-Behaviors`
- benchmark truth mutation markers are absent
- fabrication flags for data, model output, labels, logprobs, and metrics are not true

## Verification

- `python3 -m py_compile scripts/dualscope_safe_pr_merge_gate.py`
- `.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --help`
- check-only run against PR #123 should report `file_scope_allowed=true`, no blocked files, and JBB row/schema diagnostics.
