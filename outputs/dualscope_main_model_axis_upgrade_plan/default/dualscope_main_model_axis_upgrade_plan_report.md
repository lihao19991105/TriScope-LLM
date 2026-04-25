# DualScope Main Model Axis Upgrade Plan Report

## Current Stage Goal

Validate the SCI3 model-axis planning contract without running the full matrix, training, response generation, logprob extraction, or metric computation.

## Model-Axis Contract

| Model | Role | Execution status |
| --- | --- | --- |
| Qwen2.5-1.5B-Instruct | Pilot / debug / automation / ablation only | Local pilot path observed; not eligible as sole SCI3 main-table model |
| Qwen2.5-7B-Instruct | Main experimental model for main tables, ablations, and cost analysis | Planned; external resource required because no local 7B path is confirmed |
| Llama-3.1-8B-Instruct | Cross-model validation candidate | Planned; external resource required |
| Mistral-7B-Instruct-v0.3 | Cross-model validation candidate | Planned; external resource required |

## Resource Readiness

`nvidia-smi` reported two RTX 3090 GPUs with 24576 MiB each and two RTX 2080 Ti GPUs with 11264 MiB each. This confirms runtime visibility only. No local 7B/8B model execution was attempted or claimed.

## Input/Output Format

Inputs are planning documents and local path checks. Outputs are JSON/Markdown planning artifacts under `outputs/dualscope_main_model_axis_upgrade_plan/default`.

## Known Risks

- Qwen2.5-7B first-slice execution is blocked until a real local path or explicit external resource is supplied.
- Cross-model validation is blocked until Llama-3.1-8B-Instruct or Mistral-7B-Instruct-v0.3 is provisioned.
- Future artifacts must continue to separate planning readiness from real model responses, logprobs, metrics, latency, ASR, and clean utility.

## Verdict

SCI3 main model axis upgrade plan validated.

## Recommended Next Step

Proceed to `dualscope-qwen2p5-7b-first-slice-response-generation-plan`, keeping it as a plan if the Qwen2.5-7B local path remains unavailable.
