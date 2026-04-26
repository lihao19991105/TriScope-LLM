# DualScope Qwen2.5-7B Metric Blocker Closure

This closure task diagnoses why `dualscope-qwen2p5-7b-label-aligned-metric-computation` cannot report Qwen2.5-7B first-slice metrics.

The task does not modify benchmark truth, gates, labels, responses, logprobs, or metric values. It first runs the existing label-aligned metric CLI when possible, then writes blocker artifacts that separate:

- missing `final_risk_score`
- missing `detection_label` alignment
- missing ASR inputs
- missing clean utility inputs
- missing response artifacts
- logprob/capability fallback visibility
- schema mismatch
- runtime errors

## Current Closure Result

The current worktree does not contain the expected labeled-pair JSONL, Qwen2.5-7B response rows, or condition-level score rows at the task paths. Running the existing metric CLI with `python3` therefore produced `Not validated` with zero aligned metric rows.

Because the missing response, label, and score artifacts are upstream experiment artifacts rather than a local metric formula bug, the closure verdict remains `Not validated` and routes back to `dualscope-qwen2p5-7b-metric-blocker-closure`.

## Artifacts

- `outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default/dualscope_qwen2p5_7b_metric_blocker_closure_summary.json`
- `outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default/dualscope_qwen2p5_7b_metric_blocker_closure_blocker_categories.json`
- `outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default/dualscope_qwen2p5_7b_metric_blocker_closure_report.md`
- `outputs/dualscope_qwen2p5_7b_metric_blocker_closure_analysis/default/dualscope_qwen2p5_7b_metric_blocker_closure_verdict.json`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-blocker-closure.json`
