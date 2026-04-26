# DualScope Qwen2.5-7B First-Slice Result Package

## Purpose / Big Picture

Package the Qwen2.5-7B first-slice results into an auditable result bundle that separates real metrics, projected metrics, placeholders, blockers, ASR readiness, clean utility readiness, and cost notes.

This task serves the DualScope-LLM mainline by making the current Qwen2.5-7B first-slice evidence usable for planning and reporting without claiming full-paper performance or fabricating responses, labels, logprobs, benchmark truth, gates, or detection metrics.

## Scope

### In Scope

- Read the Qwen2.5-7B first-slice response-generation output directory.
- Read the Qwen2.5-7B label-aligned metric-computation output directory.
- Read metric repair outputs when present as supporting audit evidence.
- Produce a result package under `outputs/dualscope_qwen2p5_7b_first_slice_result_package/default`.
- Produce a documentation summary at `docs/dualscope_qwen2p5_7b_first_slice_result_package.md`.
- Report only first-slice values that are present in local artifacts.
- Separate real, projected, placeholder, blocked, ASR, clean utility, and cost/capability evidence.

### Out of Scope

- No model generation rerun.
- No metric recomputation beyond packaging existing artifacts.
- No training, LoRA, QLoRA, full finetune, or full matrix.
- No benchmark truth, gate, trigger, target, label, response, logprob, or route_c changes.
- No historical route_c / 199+ planning.
- No full-paper performance claim.

## Repository Context

- Response-generation source: `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default`
- Metric-computation source: `outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default`
- Supporting repair source: `outputs/dualscope_qwen2p5_7b_metric_computation_repair/default`
- Package output: `outputs/dualscope_qwen2p5_7b_first_slice_result_package/default`
- Documentation output: `docs/dualscope_qwen2p5_7b_first_slice_result_package.md`

Historical TriScope / route_c artifacts are not used except as non-mainline reliability background.

## Deliverables

- `.plans/dualscope-qwen2p5-7b-first-slice-result-package.md`
- `src/eval/dualscope_qwen2p5_7b_first_slice_result_package.py`
- `scripts/build_dualscope_qwen2p5_7b_first_slice_result_package.py`
- `docs/dualscope_qwen2p5_7b_first_slice_result_package.md`
- `outputs/dualscope_qwen2p5_7b_first_slice_result_package/default`

## Progress

- [x] M1: Read AGENTS.md task constraints, `PLANS.md`, `DUALSCOPE_MASTER_PLAN.md`, and adjacent Qwen2.5-7B artifacts.
- [x] M2: Confirm source artifact status and evidence boundaries.
- [x] M3: Implement result-package builder and CLI.
- [x] M4: Generate package outputs and documentation.
- [x] M5: Validate package artifacts and record final verdict.
- [ ] M6: Complete PR workflow without auto merge, force push, branch deletion, or remote rewrite. Blocked in this sandbox because local git index metadata is read-only and the GitHub connector branch-creation call was cancelled.

## Surprises & Discoveries

- Current response generation is validated for 8 first-slice rows using real local HuggingFace generation with no fabricated responses.
- Current metric computation is partially validated: detection metrics and ASR are computed from 8 aligned real-response rows, while clean utility is blocked because no explicit utility-success field exists.
- Logprobs are unavailable in this response pass; this is a `without_logprobs` package only.
- The generated package verdict is `Partially validated`, not fully validated, because clean utility readiness is blocked.

## Decision Log

- The result package will not recompute detection metrics. It will quote metric artifacts that already declare `metrics_computed=true` and no fabricated responses.
- Projected metrics will be recorded as unavailable rather than estimated.
- Placeholder metrics will be recorded separately and will not be presented as real values.
- The final verdict can be `Qwen2.5-7B first-slice result package validated`, `Partially validated`, or `Not validated`.

## Validation and Acceptance

Acceptance requires:

- The package CLI exits successfully unless source artifacts are unusable.
- Output files exist under `outputs/dualscope_qwen2p5_7b_first_slice_result_package/default`.
- `dualscope_qwen2p5_7b_first_slice_result_package_verdict.json` contains exactly one allowed verdict.
- Docs clearly state that this is first-slice evidence only and not full-paper performance.

## Idempotence and Recovery

The package output directory can be regenerated from the current response-generation and metric-computation artifacts. If new real responses or explicit clean-utility scores are added later, rerun the same CLI to refresh the package.

## Current Run

Command:

```bash
python3 scripts/build_dualscope_qwen2p5_7b_first_slice_result_package.py \
  --output-dir outputs/dualscope_qwen2p5_7b_first_slice_result_package/default \
  --seed 2025
```

Current verdict: `Partially validated`.

Reason: response generation, detection metrics, and ASR are reportable for the current first-slice artifacts; clean utility is not reportable until explicit utility-success fields are added.

PR workflow status: local `git add` failed with read-only git metadata at `/home/lh/TriScope-LLM/.git/worktrees/qwen2p5-7b-first-slice-result-package-20260426123107/index.lock`. A GitHub connector branch-creation attempt for `codex/dualscope-qwen2p5-7b-result-package` was cancelled, so no branch, commit, PR, merge, force push, or branch deletion was performed.
