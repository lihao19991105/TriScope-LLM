# DualScope Minimal First-Slice Real-Run Limitations

This stage is intentionally minimal. Known limitations:

- It does not execute LoRA / QLoRA training.
- It does not execute a full experiment matrix.
- It does not report AUROC/F1 unless labels and real scoring outputs are present.
- Current Stage 1 / Stage 2 entrypoints may remain protocol-compatible deterministic wrappers rather than full local model inference.

