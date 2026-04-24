# DualScope Minimal Real-Run Command Entrypoint Package

This package fills the six missing minimal first-slice real-run command entrypoints and validates them in dry-run / contract-check mode.

It does not train models, run large model inference, expand the experiment matrix, change benchmark truth, or change gate semantics.

Run:

```bash
.venv/bin/python scripts/build_dualscope_minimal_real_run_command_entrypoint_package.py \
  --output-dir outputs/dualscope_minimal_real_run_command_entrypoint_package/default

.venv/bin/python scripts/build_post_dualscope_minimal_real_run_command_entrypoint_package_analysis.py \
  --output-dir outputs/dualscope_minimal_real_run_command_entrypoint_package_analysis/default
```

If validated, the next DualScope step is `dualscope-minimal-first-slice-real-run`.

