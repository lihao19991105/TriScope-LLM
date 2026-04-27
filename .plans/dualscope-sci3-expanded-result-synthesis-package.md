# DualScope SCI3 Expanded Result Synthesis Package

## Purpose / Big Picture

This plan packages the current bounded SCI3 expansion evidence after AdvBench and JBB small-slice response artifacts are available. It serves the DualScope-LLM mainline by synthesizing black-box, budget-bounded evidence across Alpaca, semantic trigger, behavior-shift, AdvBench, and JBB tracks while keeping unavailable metrics explicit.

## Scope

### In Scope

- Read existing AdvBench and JBB response JSONL artifacts.
- Compute only metrics supported by real, non-fabricated model responses.
- Package AdvBench and JBB result summaries with blocker reasons.
- Build `outputs/dualscope_sci3_expanded_result_synthesis_package/default`.
- Update `.reports/dualscope_task_verdicts/` registries.

### Out of Scope

- Re-running AdvBench or JBB response generation.
- Full benchmark or full matrix execution.
- Changing benchmark truth, gates, or PR #14.
- Fabricating responses, logprobs, AUROC/F1/ASR, clean utility, labels, reviews, or CI.
- Continuing route_c or generating 199+ plans.

## Repository Context

- Existing response inputs:
  - `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl`
  - `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_responses.jsonl`
- Shared implementation:
  - `src/eval/dualscope_benchmark_small_slice_external_gpu.py`
- CLI entrypoints:
  - `scripts/build_dualscope_benchmark_small_slice_metrics.py`
  - `scripts/build_dualscope_benchmark_small_slice_result_package.py`
  - `scripts/build_dualscope_sci3_expanded_result_synthesis.py`

## Deliverables

- Metric artifacts under:
  - `outputs/dualscope_advbench_small_slice_metric_computation/default`
  - `outputs/dualscope_jbb_small_slice_metric_computation/default`
- Result packages under:
  - `outputs/dualscope_advbench_small_slice_result_package/default`
  - `outputs/dualscope_jbb_small_slice_result_package/default`
- Expanded synthesis package under:
  - `outputs/dualscope_sci3_expanded_result_synthesis_package/default`
- Task verdict registries under `.reports/dualscope_task_verdicts/`.

## Progress

- [x] Read required project instructions and queue.
- [x] Confirm AdvBench and JBB response artifact row counts.
- [x] Preserve blocked rows as blockers rather than real model responses.
- [x] Add missing queue entries for AdvBench/JBB metric and result package tasks.
- [x] Regenerate metric, package, and synthesis artifacts.
- [x] Run validation commands and task orchestrator dry-run.
- [x] Attempt PR workflow if local Git metadata permits it.

## Surprises & Discoveries

- The available AdvBench and JBB response JSONL files each contain 16 rows, but all inspected rows are `response_generation_status=blocked` with `model_response_present=false` and `blocker=missing_model_dir`.
- Local `.git` metadata is not writable in this workspace, so fetch/branch/commit/PR operations may be blocked even though repository files are writable.
- AdvBench/JBB result packages can validate as honest packages while their metric-computation tasks remain partially validated, because no blocked row is counted as a real model response.
- Local `git switch -c ...` failed with `.git/refs/... Read-only file system`; GitHub connector branch creation was also cancelled by the connector flow, so no PR was created from this workspace.

## Decision Log

- Blocked rows must count as response artifacts but not as real model responses.
- ASR, refusal rate, and response-length metrics are computed only when at least one real generated response exists.
- AUROC/F1-style detection metrics remain blocked unless `detection_label` and `final_risk_score` align.
- Clean utility remains blocked without explicit utility-success or reference-match fields.
- Synthesis package validation means the package honestly summarizes available evidence and blockers; it does not mean benchmark performance is available.

## Plan of Work

1. Repair task queue routing and synthesis package naming.
2. Rerun metric CLIs against existing response JSONL files only.
3. Rerun result package CLIs.
4. Rerun expanded synthesis package CLI.
5. Validate with compile/help/diff/orchestrator dry-run.
6. Attempt PR/review/merge workflow if Git metadata allows safe non-force operations.

## Concrete Steps

```bash
python3 scripts/build_dualscope_benchmark_small_slice_metrics.py --dataset-id advbench
python3 scripts/build_dualscope_benchmark_small_slice_result_package.py --dataset-id advbench
python3 scripts/build_dualscope_benchmark_small_slice_metrics.py --dataset-id jbb
python3 scripts/build_dualscope_benchmark_small_slice_result_package.py --dataset-id jbb
python3 scripts/build_dualscope_sci3_expanded_result_synthesis.py
```

## Validation and Acceptance

- `python3 -m py_compile` passes for modified/new Python files.
- Each new/modified CLI responds to `--help`.
- `git diff --check` passes.
- Task orchestrator dry-run reports `queue_complete` or a concrete next task.
- Artifacts and registries are present at the paths requested by the task queue.

## Idempotence and Recovery

All builders are deterministic and overwrite only their own output directories and registry files. Re-running them should not alter benchmark truth or response generation artifacts.

## Outputs and Artifacts

See `Deliverables`.

## Remaining Risks

- AdvBench/JBB currently have response artifact rows but no real generated model responses, so response-derived metrics and ASR remain blocked.
- With-logprobs metrics are unavailable and must remain blocked under without-logprobs fallback.
- PR creation may be blocked by read-only `.git` metadata.

## Next Suggested Plan

If this package validates but AdvBench/JBB remain blocked, the next research step should be a single resource-path repair for the external GPU runner model binding, not broader matrix expansion.
