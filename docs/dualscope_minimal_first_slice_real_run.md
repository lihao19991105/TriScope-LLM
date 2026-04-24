# DualScope Minimal First-Slice Real Run

This phase executes the minimal first-slice artifact chain:

1. data slice
2. Stage 1 illumination
3. Stage 2 confidence
4. Stage 3 fusion
5. evaluation placeholders
6. report skeleton

It does not run the full experiment matrix, does not train a model, and does not claim final paper performance.

Run:

```bash
.venv/bin/python scripts/build_dualscope_minimal_first_slice_real_run.py \
  --output-dir outputs/dualscope_minimal_first_slice_real_run/default \
  --capability-mode auto \
  --allow-fallback-without-logprobs \
  --no-full-matrix

.venv/bin/python scripts/build_post_dualscope_minimal_first_slice_real_run_analysis.py \
  --output-dir outputs/dualscope_minimal_first_slice_real_run_analysis/default
```

If current Stage 1 / Stage 2 entrypoints remain protocol-compatible deterministic rather than full model inference, the phase should be reported as partial rather than final performance validation.

