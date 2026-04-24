# DualScope First Slice Preflight Blockers

Known likely blockers:

- Missing `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`.
- GPU checks must run through `.venv/bin/python` with `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3`; otherwise Python may not see the intended two RTX 3090 cards.
- with-logprobs should be treated as available only after local CUDA/logits access is confirmed; otherwise use the without-logprobs fallback with the degradation flag.

Do not fabricate dataset files or claim with-logprobs support without backend evidence.
