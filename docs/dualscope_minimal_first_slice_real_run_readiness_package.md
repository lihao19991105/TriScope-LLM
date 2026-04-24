# DualScope Minimal First-Slice Real-Run Readiness Package

This package is the final go/no-go checkpoint before `dualscope-minimal-first-slice-real-run`.

It checks:

- materialized Stanford Alpaca first-slice dataset
- validated preflight rerun
- local model path
- GPU / CUDA visibility
- first-slice scope constraints
- planned real-run commands
- whether command entrypoint scripts exist

It does not run training, inference, or the full experiment matrix.

Run:

```bash
.venv/bin/python scripts/build_dualscope_minimal_first_slice_real_run_readiness_package.py \
  --output-dir outputs/dualscope_minimal_first_slice_real_run_readiness_package/default

.venv/bin/python scripts/build_post_dualscope_minimal_first_slice_real_run_readiness_package_analysis.py \
  --output-dir outputs/dualscope_minimal_first_slice_real_run_readiness_package_analysis/default
```

If the package reports missing command entrypoints, the next DualScope task should implement only those minimal first-slice real-run entrypoints, without expanding the experiment matrix.

