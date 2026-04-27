# DualScope JBB Small-Slice Response Generation Repair

## Purpose / Big Picture

Repair and compress the partially validated JBB response-generation step by rebuilding missing source artifacts when possible, auditing the bounded response rows, and routing the remaining blocker honestly. This keeps the SCI3 JBB expansion track recoverable without fabricating model responses, logprobs, metrics, benchmark truth, gates, or full-matrix results.

## Scope

### In Scope

- Audit `outputs/dualscope_jbb_small_slice_response_generation/default`.
- Verify whether real non-fabricated model responses exist.
- Preserve explicit runtime blockers such as CUDA unavailability.
- Write compact repair artifacts that omit harmful prompts and model completions.
- Write `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation-repair.json`.

### Out of Scope

- New response generation beyond the bounded source task.
- Metric computation, labels, ASR, clean utility, or logprob inference.
- Full JBB execution, full matrix expansion, training, route_c, or `199+`.
- Benchmark truth or gate changes.

## Repository Context

- Source task plan: `.plans/dualscope-jbb-small-slice-response-generation.md`
- Source task outputs: `outputs/dualscope_jbb_small_slice_response_generation/default`
- Source task registry: `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation.json`
- Repair output directory: `outputs/dualscope_jbb_small_slice_response_generation_repair/default`

This is a DualScope SCI3 expansion-track repair task. Historical TriScope / route_c artifacts are not used.

## Deliverables

- `src/eval/dualscope_jbb_small_slice_response_generation_repair.py`
- `scripts/build_dualscope_jbb_small_slice_response_generation_repair.py`
- `docs/dualscope_jbb_small_slice_response_generation_repair.md`
- `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation-repair.json`
- `outputs/dualscope_jbb_small_slice_response_generation_repair/default/jbb_small_slice_response_generation_repair_summary.json`
- `outputs/dualscope_jbb_small_slice_response_generation_repair/default/jbb_small_slice_response_generation_repair_verdict.json`

## Milestones

- [x] M1: Rebuild or verify the bounded source response-generation artifact directory.
- [x] M2: Add JBB repair/compression core and CLI.
- [x] M3: Run syntax validation.
- [x] M4: Execute repair audit and write repair artifacts.
- [x] M5: Update plan progress with final status.

## Validation

Run:

```bash
python3 -m py_compile \
  src/eval/dualscope_jbb_small_slice_response_generation.py \
  scripts/build_dualscope_jbb_small_slice_response_generation.py \
  src/eval/dualscope_jbb_small_slice_response_generation_repair.py \
  scripts/build_dualscope_jbb_small_slice_response_generation_repair.py

python3 scripts/build_dualscope_jbb_small_slice_response_generation_repair.py \
  --response-dir outputs/dualscope_jbb_small_slice_response_generation/default \
  --output-dir outputs/dualscope_jbb_small_slice_response_generation_repair/default \
  --registry-path .reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation-repair.json \
  --seed 20260427
```

## Progress

- 2026-04-27: Rebuilt the bounded source response-generation artifact package from the existing runner. The result remains `Partially validated` with `generated_row_count=0`, `blocked_row_count=16`, and `blocker_type=torch_cuda_unavailable`.
- 2026-04-27: Added JBB repair/compression module, CLI, documentation, compact row audit, availability matrix, blocker compression, verdict, and tracked repair registry.
- 2026-04-27: Syntax validation passed. Repair audit completed with `JBB small-slice response generation repair validated`, preserving the CUDA visibility blocker and routing to blocker closure.
- 2026-04-27: Opened PR #127 and requested Codex review. Safe merge gate check-only reported `file_scope_allowed=true` and blocked only on `codex_review_missing`; no merge, force push, branch deletion, remote rewrite, benchmark truth change, gate change, route_c continuation, or `199+` generation occurred.

## Risks

- The repair validates artifact consistency and blocker routing; it does not make CUDA visible or create real model responses.
- Downstream metric computation remains blocked until real non-fabricated JBB responses exist.
- Raw source response-generation artifacts may contain benchmark prompts for audit; repair reports and compact rows intentionally omit harmful prompts and completions.
