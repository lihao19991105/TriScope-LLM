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

- Direct queue entry for `dualscope-qwen2p5-7b-metric-blocker-closure`.
- Queue dry-run with `prompt_available=true`.
- A prompt that requires real metric CLI execution or explicit blocker output.

## Progress

- [x] Diagnosed current queue selection as `dualscope-qwen2p5-7b-metric-blocker-closure` with no direct prompt.
- [x] Added this ExecPlan.
- [x] Add queue entry.
- [ ] Run validation.

## Risks

- If `final_risk_score` is absent from condition-level artifacts, detection metrics must remain blocked.
- If real Qwen2.5-7B response rows lack target/reference eligibility fields, ASR and clean utility must remain blocked.
