# DualScope Qwen2.5-7B Metric Computation Repair

This task audits the Qwen2.5-7B label-aligned metric state and produces a repair package that can only report metrics when the local source artifacts are sufficient.

The repair package does not infer clean utility from free text. Detection metrics and ASR are reportable only when their source metric artifacts have `summary_status: PASS`, `metrics_computed: true`, and aligned real Qwen2.5-7B response rows.

## Inputs

- `outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default`
- `outputs/dualscope_qwen2p5_7b_metric_blocker_closure/default`
- `outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-label-aligned-metric-computation.json`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-blocker-closure.json`

## Outputs

- `outputs/dualscope_qwen2p5_7b_metric_computation_repair/default/dualscope_qwen2p5_7b_metric_computation_repair_metric_availability_matrix.json`
- `outputs/dualscope_qwen2p5_7b_metric_computation_repair/default/dualscope_qwen2p5_7b_metric_computation_repair_real_metric_summary.json`
- `outputs/dualscope_qwen2p5_7b_metric_computation_repair/default/dualscope_qwen2p5_7b_metric_computation_repair_unavailable_metric_blockers.json`
- `outputs/dualscope_qwen2p5_7b_metric_computation_repair/default/dualscope_qwen2p5_7b_metric_computation_repair_limitations.json`
- `outputs/dualscope_qwen2p5_7b_metric_computation_repair/default/dualscope_qwen2p5_7b_metric_computation_repair_verdict.json`
- `outputs/dualscope_qwen2p5_7b_metric_computation_repair_analysis/default`
- `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-metric-computation-repair.json`

## How To Run

```bash
python3 scripts/build_dualscope_qwen2p5_7b_label_aligned_metric_computation.py \
  --labeled-pairs data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl \
  --response-dir outputs/dualscope_qwen2p5_7b_first_slice_response_generation/default \
  --condition-level-dir outputs/dualscope_minimal_first_slice_condition_level_rerun/default \
  --output-dir outputs/dualscope_qwen2p5_7b_label_aligned_metric_computation/default \
  --no-full-matrix

python3 scripts/build_dualscope_qwen2p5_7b_metric_computation_repair.py
```

In the current isolated worktree, the first command records missing labeled-pair, response-row, and condition-level score artifacts. The repair verdict is therefore `Not validated` and routes back to `dualscope-qwen2p5-7b-metric-blocker-closure`.

## Guardrails

- No benchmark truth or gates are modified.
- No route_c or 199+ work is continued.
- No full matrix or training is run.
- No AUROC, AUPRC, F1, accuracy, ASR, clean utility, responses, logprobs, labels, or `final_risk_score` are fabricated.
