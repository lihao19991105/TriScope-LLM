# DualScope First Slice Preflight Repair

This stage repairs the actionable blockers found by the first-slice real-run preflight. It does not run training, does not run the real first slice, and does not claim the preflight is validated.

## What It Fixes

- Converts the missing Stanford Alpaca JSONL blocker into a real-source-only import contract.
- Adds an executable dataset normalization CLI.
- Adds an executable dataset schema checker.
- Records GPU/CUDA execution requirements for the two RTX 3090 cards.
- Produces a rerun-preflight checklist.

## What It Does Not Do

- It does not download data.
- It does not fabricate Alpaca rows.
- It does not run LoRA / QLoRA training.
- It does not execute the full matrix.
- It does not modify benchmark truth or gate semantics.

## Required Dataset Path

```text
data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl
```

This file must be materialized from a real Alpaca-style source before preflight can become fully validated.

## Required GPU Runtime

```bash
CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 .venv/bin/python <script> <args>
```

The prefix binds the two RTX 3090 cards consistently with `nvidia-smi` index order.
