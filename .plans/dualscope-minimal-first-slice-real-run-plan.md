# dualscope-minimal-first-slice-real-run-plan

## Background

DualScope has completed the Stage 1 / Stage 2 / Stage 3 freezes, the experimental matrix freeze, a minimal first-slice execution plan, a controlled artifact smoke run, first-slice artifact validation, and a first-slice report skeleton. The next step is to freeze a real-run plan for the same first slice without executing the full experiment.

## Why first-slice real-run planning follows smoke/artifact validation

The smoke run validated artifact shape only. It did not use real data, real poisoning, real adapter training, or real model inference as performance evidence. A real-run plan is needed before any real execution so dataset paths, model assumptions, backdoor construction, commands, resources, preflight checks, artifacts, validation rules, and stop conditions are auditable.

## Frozen method dependencies

- Stage 1: `dualscope-illumination-screening-freeze`
- Stage 2: `dualscope-confidence-verification-with-without-logprobs`
- Stage 3: `dualscope-budget-aware-two-stage-fusion-design`
- Matrix: `dualscope-experimental-matrix-freeze`
- First slice: `dualscope-minimal-first-slice-execution-plan`

## Goal

Freeze the minimum real first-slice run plan so a future real run can execute only after preflight passes.

## Non-goals

- Do not run the full matrix.
- Do not run training in this stage.
- Do not fabricate missing data.
- Do not change benchmark truth or gate semantics.
- Do not continue route_c / 199+ work.
- Do not report smoke artifacts as real performance.

## First-slice real-run scope

- Dataset: Stanford Alpaca
- Model: Qwen2.5-1.5B-Instruct local path if available
- Trigger: lexical trigger
- Target: fixed response / fixed target behavior
- Capability: attempt with-logprobs if backend supports logits/logprobs, otherwise fallback to without-logprobs with degradation flag
- Baselines: illumination-only, confidence-only, DualScope budget-aware fusion

## Dataset slice plan

The plan requires a local Alpaca-format JSONL before real execution. If absent, preflight must fail safely and no real run should be claimed.

## Model plan

Use the existing local Qwen2.5-1.5B-Instruct path when available. No full fine-tuning is allowed. LoRA / QLoRA / adapter-level construction is planned but not executed by this stage.

## Backdoor construction plan

Use a minimal lexical trigger insertion and fixed target response with a small poison ratio. Clean and poisoned splits must be separately materialized and audited.

## Trigger / target plan

The trigger is a fixed lexical marker. The target is fixed response / refusal-bypass style behavior. This validates the pipeline but is not a final performance conclusion.

## Capability-mode plan

With-logprobs is preferred when local inference exposes token scores. Without-logprobs fallback remains valid but weaker and must carry degradation flags.

## Stage 1 / Stage 2 / Stage 3 execution flow

Stage 1 reads query artifacts, emits screening fields and candidate flags. Stage 2 reads candidates, emits verification evidence and capability flags. Stage 3 reads public fields and emits final risk, decision, and cost summary.

## Resource contract

The real run must fit within 2 x RTX 3090. Default planning uses batch size 1, sequence length 2048, LoRA rank 8 or QLoRA if needed, and controlled sample counts.

## Preflight checks

Required checks include dataset path, model path, tokenizer load, GPU availability, output writability, Stage 1/2/3 contracts, capability mode, disk space, py_compile, and dry-run config checks.

## Run command plan

Commands are frozen as planned commands only. `planned_not_executed_yet = true` must be recorded for every command.

## Expected artifacts

Expected real-run artifacts include data slices, poisoned split, adapter checkpoint, train config/log, Stage 1/2/3 outputs, baseline comparison, metrics summary, cost summary, and report.

## Validation criteria

The real run will be valid only if required artifacts exist, schemas are compatible, capability mode and budget usage are recorded, and no benchmark truth or gate semantics changed.

## Failure fallback plan

Missing dataset stops execution. Missing model stops execution or explicitly enters placeholder planning mode. OOM reduces batch/sequence/quantization within the same resource boundary. Missing logprobs falls back to without-logprobs. LoRA failure stops or switches to inference-only protocol validation without claiming trained backdoor.

## Stop conditions

Stop if data/model paths are missing, schema contracts break, py_compile fails, full training or full matrix becomes required, benchmark truth/gate changes are needed, or route_c recursion is required.

## Risks

- Stanford Alpaca is still a placeholder in `configs/datasets.yaml`.
- With-logprobs support depends on the future inference backend.
- Real LoRA training may fail under resource limits.
- Smoke artifacts are not performance evidence.

## Milestones

- M1: real-run dataset / model / trigger / target / capability scope frozen
- M2: execution flow / resource / artifact / preflight / validation contracts completed
- M3: single verdict and single recommendation completed

## Exit criteria

- All required real-run planning artifacts exist.
- Post-analysis returns one verdict.
- If validated, the only next step is `dualscope-minimal-first-slice-real-run-preflight`.

## Progress

- [x] M1: real-run dataset / model / trigger / target / capability scope frozen
- [x] M2: execution flow / resource / artifact / preflight / validation contracts completed
- [x] M3: single verdict and single recommendation completed

