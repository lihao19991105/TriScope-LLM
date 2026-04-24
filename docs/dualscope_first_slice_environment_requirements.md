# DualScope First Slice Environment Requirements

## Python

Use the repository Python 3.10 virtual environment:

```bash
.venv/bin/python
```

Do not use bare system `python3` for first-slice GPU preflight or real-run commands.

## GPU

The project machine has two RTX 3090 cards at `nvidia-smi` indices `2,3`. GPU runs should use:

```bash
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python <script> <args>
```

## Allowed During Repair

- Dataset import from a real source file.
- Dataset schema validation.
- CPU-only command and artifact contract checks.
- Preflight rerun after materialization.

## Not Allowed During Repair

- LoRA / QLoRA training.
- GPU inference real run.
- Full first-slice execution.
- Full experimental matrix execution.
- Benchmark truth or gate semantic changes.
