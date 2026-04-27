# DualScope Safe Merge Gate AdvBench Small-Slice Allowlist

## Purpose / Big Picture

PR #107 materializes a bounded AdvBench small slice from the public Hugging Face source `walledai/AdvBench`, but the safe merge gate currently blocks the data file because all `data/` paths are outside the default file-scope allowlist.

This plan adds a narrow, content-validated exception for exactly `data/advbench/small_slice/advbench_small_slice_source.jsonl` so the bounded small-slice can enter `main` without opening the repository to arbitrary data files, full AdvBench dumps, benchmark truth mutations, route_c changes, or 199+ historical-chain expansion.

## Scope

### In Scope

- Add a strict safe merge gate validator for one exact AdvBench small-slice path.
- Require JSONL, at most 32 rows, valid JSON per line, required provenance/schema fields, and `source_dataset == "walledai/AdvBench"`.
- Record explicit diagnostics for allowed AdvBench small-slice files, row count, schema validity, source dataset, blocked data files, and final file-scope status.
- Validate the updated gate against PR #107 before merging PR #107.

### Out of Scope

- No generic `data/` allowlist.
- No `data/advbench/full/*`, `data/advbench/raw/*`, or full AdvBench ingestion.
- No response generation, metric computation, benchmark truth mutation, gate semantic change beyond this data allowlist, route_c work, or 199+ planning.
- No handling or merging of PR #14.

## Repository Context

- `scripts/dualscope_safe_pr_merge_gate.py` owns the safe PR merge file-scope, review, CI, and execution-gate checks.
- `.reports/dualscope_task_verdicts/*.json` already has a separate registry validator.
- PR #107 changes `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-materialization.json` and the bounded AdvBench small-slice JSONL.
- Historical TriScope / route_c artifacts are not used by this plan.

## Deliverables

- `.plans/dualscope-safe-merge-gate-advbench-small-slice-allowlist.md`
- Updated `scripts/dualscope_safe_pr_merge_gate.py`
- Safe merge gate artifacts under `outputs/dualscope_safe_pr_merge_gate/pr107_check_after_advbench_allowlist/`

## Progress

- [x] Read repository instructions and DualScope task queue.
- [x] Confirm PR #107 is blocked only because the AdvBench small-slice JSONL is outside file scope.
- [x] Implement exact-path, content-validated AdvBench small-slice allowlist.
- [x] Run py_compile, help, and PR #107 check-only validation.
- [ ] Open gate-fix PR, request Codex review, and merge it only after safe checks pass.
- [ ] Recheck PR #107 on updated main and merge only if all required gate conditions pass.
- [ ] Run task orchestrator dry-run and continue autorun if PR #107 merges cleanly.

## Surprises & Discoveries

- The local `.git` ref area is not writable in this environment, so the gate-fix branch must be created through the GitHub API/MCP while local validation uses a temporary tree under `/tmp`.
- PR #107 passes the updated local gate with `merge_allowed=true`, `file_scope_allowed=true`, `blocked_files=[]`, `requested_changes_count=0`, `failing_checks_count=0`, `advbench_small_slice_row_count=32`, and `advbench_small_slice_schema_valid=true`.

## Decision Log

- Use a validator instead of a glob allowlist for `data/advbench/...` so unauthorized data files remain blocked.
- Keep the allowed path exact: `data/advbench/small_slice/advbench_small_slice_source.jsonl`.
- Treat benchmark truth mutation markers inside JSON keys or string values as a hard schema failure.

## Plan of Work

First update the gate to recognize the exact small-slice path only after content validation. Then run local syntax/help checks and check PR #107 with the updated gate. If PR #107 passes, create and merge a small gate-fix PR. After the gate fix reaches `main`, rerun the safe merge gate on PR #107 and merge it only when the required diagnostics and hard checks pass.

## Concrete Steps

1. Update `scripts/dualscope_safe_pr_merge_gate.py`.
2. Run:
   - `python3 -m py_compile scripts/dualscope_safe_pr_merge_gate.py`
   - `.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --help`
   - `.venv/bin/python scripts/dualscope_safe_pr_merge_gate.py --pr 107 --check-only --allow-auto-merge-without-review --output-dir outputs/dualscope_safe_pr_merge_gate/pr107_check_after_advbench_allowlist`
3. Confirm `merge_allowed=true`, `file_scope_allowed=true`, `blocked_files=[]`, `requested_changes_count=0`, `failing_checks_count=0`, `advbench_small_slice_row_count <= 32`, and `advbench_small_slice_schema_valid=true`.
4. If validation passes, open the gate-fix PR and request `@codex review`.
5. Merge the gate-fix PR only through the safe merge gate.
6. Recheck and merge PR #107 only if the updated gate passes.

## Validation and Acceptance

Acceptance requires PR #107 check-only to pass with the AdvBench diagnostics present and no blocked files, requested changes, or failing checks. The allowed data path must remain the only permitted AdvBench data path.

## Idempotence and Recovery

The validator is read-only against PR content and writes only output diagnostics. If a check fails, rerun with the same output directory or a new one after fixing the PR or validator. If GitHub branch creation fails, no local branch state needs cleanup because branch writes are performed through the GitHub API/MCP.

## Outputs and Artifacts

- `outputs/dualscope_safe_pr_merge_gate/pr107_check_after_advbench_allowlist/dualscope_safe_pr_merge_gate_file_scope_check.json`
- `outputs/dualscope_safe_pr_merge_gate/pr107_check_after_advbench_allowlist/dualscope_safe_pr_merge_gate_decision.json`
- `outputs/dualscope_safe_pr_merge_gate/pr107_check_after_advbench_allowlist/dualscope_safe_pr_merge_gate_report.md`

## Remaining Risks

- PR #107 may still be blocked if it has requested changes, failing checks, or branch merge conflicts independent of file scope.
- Local `.git` remains read-only for branch creation, so API/MCP PR operations are required for this gate-fix task.

## Next Suggested Plan

If PR #107 merges, the next DualScope task should be `dualscope-advbench-small-slice-response-generation-plan`.
