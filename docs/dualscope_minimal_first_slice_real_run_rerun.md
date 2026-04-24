# DualScope Minimal First-Slice Real Run Rerun

This stage reruns the minimal first-slice pipeline after model execution and local logits capability have been validated.

The rerun attaches capability evidence but does not overclaim integration. If Stage 1 and Stage 2 entrypoints still report `protocol_compatible_deterministic_no_model_execution`, the verdict remains partial even when the local model probes pass.
