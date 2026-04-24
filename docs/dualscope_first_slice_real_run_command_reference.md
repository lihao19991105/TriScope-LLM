# DualScope First-Slice Real-Run Command Reference

The six minimal first-slice entrypoints are:

- `scripts/build_dualscope_first_slice_data_slice.py`
- `scripts/run_dualscope_stage1_illumination.py`
- `scripts/run_dualscope_stage2_confidence.py`
- `scripts/run_dualscope_stage3_fusion.py`
- `scripts/evaluate_dualscope_first_slice.py`
- `scripts/build_dualscope_first_slice_real_run_report.py`

Each supports `--dry-run`, `--contract-check`, `--output-dir`, and `--seed`. Dry-run outputs are contract artifacts only and must not be reported as real performance.

