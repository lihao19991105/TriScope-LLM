# DualScope First Slice Preflight Rerun

This package reruns the minimal first-slice real-run preflight after the real Stanford Alpaca first-slice dataset has been materialized.

It is still preflight-only:

- no LoRA or QLoRA training
- no full matrix execution
- no benchmark truth or gate changes
- no old route_c recursion

Run:

```bash
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python scripts/build_dualscope_first_slice_preflight_rerun.py \
  --output-dir outputs/dualscope_first_slice_preflight_rerun/default

.venv/bin/python scripts/build_post_dualscope_first_slice_preflight_rerun_analysis.py \
  --output-dir outputs/dualscope_first_slice_preflight_rerun_analysis/default
```

The post-analysis normalizes the canonical preflight verdict into the phase-level verdict:

- `First slice preflight rerun validated`
- `Partially validated`
- `Not validated`

