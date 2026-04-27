# DualScope Qwen2.5-7B Alpaca Main-Slice Metric Computation

This package computes only metrics supported by existing bounded artifacts:

- labels from `data/stanford_alpaca/first_slice/alpaca_first_slice_labeled_pairs.jsonl`
- real model responses from `outputs/dualscope_qwen2p5_7b_alpaca_main_slice_response_generation/default`
- available row-level scores from `outputs/dualscope_minimal_first_slice_condition_level_rerun/default`

It does not generate responses, train models, modify benchmark truth, change gates, compute logprob metrics, or extend the experiment matrix.

## Run

```bash
python3 scripts/build_dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation.py
```

Default outputs are written to:

```text
outputs/dualscope_qwen2p5_7b_alpaca_main_slice_metric_computation/default
```

The tracked task registry is:

```text
.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-alpaca-main-slice-metric-computation.json
```

## Metric Policy

Detection metrics are computed only when `detection_label`, `final_risk_score`, and a non-fabricated real `model_response` align on the same `row_id`.

ASR is computed only from real poisoned ASR-eligible response rows with an explicit `target_matched` field.

Clean utility remains blocked unless an explicit utility success field is present. It is not inferred from response text or reference text similarity.

Logprob metrics remain blocked for this run because the bounded response generation used `without_logprobs` fallback and no token logprobs are present.

## Verdict Policy

The final verdict is exactly one of:

- `Qwen2.5-7B Alpaca main-slice metrics validated`
- `Partially validated`
- `Not validated`

For this bounded run, a partially validated verdict can still route to `dualscope-qwen2p5-7b-alpaca-main-slice-result-package` when real detection metrics or ASR are computed and unsupported metrics are recorded as blockers.
