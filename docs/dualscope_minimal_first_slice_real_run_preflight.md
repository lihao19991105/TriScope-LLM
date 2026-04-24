# DualScope Minimal First Slice Real-Run Preflight

This stage checks whether the minimal first-slice real run can safely begin. It does not train adapters, run the full matrix, or claim real performance.

## Checks

- Dataset path, schema, and sliceability.
- Model path, tokenizer load, and model config.
- GPU availability through the project Python 3.10 environment.
- Output directory writability and disk space.
- Stage 1 / Stage 2 / Stage 3 artifacts.
- Experimental matrix and real-run-plan artifacts.
- Stage public-field compatibility.
- Capability mode and without-logprobs fallback.
- Planned command consistency.
- `py_compile`.
- Dry-run config construction.
- Forbidden expansion.

## Expected Outcome

If the real Stanford Alpaca JSONL is missing, preflight should return `Partially validated`, not `validated`.

## Required Runtime Environment

Use the repository virtual environment, not bare system `python3`:

```bash
.venv/bin/python scripts/build_dualscope_minimal_first_slice_real_run_preflight.py \
  --output-dir outputs/dualscope_minimal_first_slice_real_run_preflight/default
```

For GPU checks and later first-slice real-run commands, bind the two RTX 3090 cards explicitly:

```bash
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 \
.venv/bin/python <script> <args>
```

This is necessary because bare `python3` may resolve to the system interpreter, and GPU index ordering without `CUDA_DEVICE_ORDER=PCI_BUS_ID` may not match the `nvidia-smi` index order.
