# DualScope Real-Run Failure Fallback

- If dataset is missing, stop and report the missing path. Do not fabricate data.
- If model is missing, stop or enter an explicit placeholder mode. Do not claim a real run.
- If OOM occurs, reduce batch size, reduce sequence length, enable QLoRA, or stop.
- If logprobs are unavailable, use the without-logprobs protocol and mark degradation.
- If LoRA training fails, stop or run inference-only protocol validation without claiming a trained backdoor.
- If artifact schema breaks, stop and repair schema before evaluation.

