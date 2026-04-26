# DualScope Qwen2.5-7B Metric Blocker Closure

## Purpose / Big Picture

This plan closes the current SCI3 queue blocker after the Qwen2.5-7B first-slice response generation repair produced real response artifacts but the label-aligned metric computation task ended as `Not validated`.

The goal is to make the metric blocker explicit and actionable without fabricating metrics. If labels, `final_risk_score`, and real response artifacts align, the task may compute available metrics. If they do not align, it must produce blocker artifacts that state exactly which inputs are missing or incompatible.

## Scope

### In Scope

- Add a direct queue prompt for `dualscope-qwen2p5-7b-metric-blocker-closure`.
- Require the task to inspect Qwen2.5-7B response artifacts, first-slice labels, and condition-level score artifacts.
- Require running the existing metric CLI when possible.
- Require explicit blocker artifacts for missing `final_risk_score`, `detection_label`, ASR inputs, utility inputs, or logprob-dependent fields.

### Out of Scope

- No benchmark truth changes.
- No gate changes.
- No route_c or 199+ work.
- No fake AUROC, AUPRC, F1, accuracy, ASR, clean utility, responses, or logprobs.
- No full matrix execution.

## Repository Context

- Queue source: `DUALSCOPE_TASK_QUEUE.md`
- Current failed task registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-label-aligned-metric-computation.json`
- Metric implementation: `scripts/build_dualscope_qwen2p5_7b_label_aligned_metric_computation.py`
- Response artifacts: `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default`

## Deliverables

- Closure builder: `scripts/build_dualscope_qwen2p5_7b_metric_blocker_closure.py`
- Core closure logic: `src/eval/dualscope_qwen2p5_7b_metric_blocker_closure.py`
- Closure documentation: `docs/dualscope_qwen2p5_7b_metric_blocker_closure.md`
- Explicit blocker artifacts under `outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default`
- Analysis artifacts under `outputs/dualscope_qwen2p5_7b_metric_blocker_closure_analysis/default`
- Tracked verdict registry: `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-blocker-closure.json`

## Progress

- [x] Diagnosed current queue selection as `dualscope-qwen2p5-7b-metric-blocker-closure` with no direct prompt.
- [x] Added this ExecPlan.
- [x] Add queue entry.
- [x] Ran the existing label-aligned metric CLI with `python3` after `.venv/bin/python` was unavailable.
- [x] Confirmed the metric task remains `Not validated` with zero aligned metric rows.
- [x] Added and ran the blocker-closure builder.
- [x] Wrote explicit blocker categories for missing `final_risk_score`, missing detection-label alignment, missing ASR inputs, missing utility inputs, missing response artifacts, logprob/capability fallback visibility, schema mismatch status, and runtime errors.
- [x] Wrote tracked verdict registry with final verdict `Not validated`.
- [x] Ran `python3 -m py_compile` for the closure module and CLI.

## Risks

- If `final_risk_score` is absent from condition-level artifacts, detection metrics must remain blocked.
- If real Qwen2.5-7B response rows lack target/reference eligibility fields, ASR and clean utility must remain blocked.
- Current worktree risk: the expected labeled-pair JSONL, Qwen2.5-7B response-generation output directory, and condition-level score directory are absent in this worktree, so the closure cannot distinguish row-level schema gaps from missing upstream artifacts.
- Runtime risk: the requested `.venv/bin/python` interpreter is absent; validation used `python3`, which executed the metric CLI and produced the task's honest `Not validated` result.
