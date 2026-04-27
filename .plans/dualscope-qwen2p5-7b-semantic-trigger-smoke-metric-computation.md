# DualScope Qwen2.5-7B Semantic Trigger Smoke Metric Computation

## Purpose / Big Picture

Compute only the metrics supported by the real Qwen2.5-7B semantic trigger smoke response rows. This closes the response-generation stage without claiming full trigger-family or full-matrix performance.

## Scope

### In Scope

- Read semantic trigger smoke responses from `outputs/dualscope_qwen2p5_7b_semantic_trigger_smoke_response_generation/default`.
- Align response rows with first-slice labels and condition-level `final_risk_score` rows.
- Compute detection metrics and ASR only when the required aligned fields exist.
- Preserve clean utility and logprob blockers when explicit utility/logprob fields are missing.
- Write metric artifacts and a tracked verdict registry.

### Out of Scope

- Full trigger matrix execution.
- New response generation.
- Clean utility inference from free text.
- Fabricated logprobs or placeholder metrics.
- Benchmark truth or gate changes.

## Validation

Run:

```bash
python3 -m py_compile src/eval/dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation.py
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation.py --help
.venv/bin/python scripts/build_dualscope_qwen2p5_7b_semantic_trigger_smoke_metric_computation.py
```

Expected next task after successful available-metric computation:

```text
dualscope-qwen2p5-7b-semantic-trigger-smoke-result-package
```

## Progress

- 2026-04-27: Implemented semantic smoke metric CLI and artifact writer.
