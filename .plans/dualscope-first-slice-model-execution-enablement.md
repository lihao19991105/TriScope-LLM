# dualscope-first-slice-model-execution-enablement

## Purpose / Big Picture

This plan enables the minimal DualScope first-slice pipeline to distinguish a protocol-compatible no-model run from a minimal real local-model generation path. It follows the partially validated minimal first-slice real run and the validated compression step.

## Scope

### In Scope

- Check the frozen local Qwen2.5-1.5B-Instruct path.
- Load tokenizer and model config.
- Run a minimal generation probe on at most three Stanford Alpaca first-slice prompts.
- Record CUDA, dtype, prompt count, generated token count, and failure fallback.
- Produce a single verdict and next recommendation.

### Out of Scope

- No LoRA or QLoRA training.
- No full first-slice model inference sweep.
- No full matrix.
- No benchmark truth or gate changes.
- No route_c continuation.

## Repository Context

- Dataset: `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`
- Model path: `local_models/Qwen2.5-1.5B-Instruct`
- Prior status: `outputs/dualscope_minimal_first_slice_real_run_compression/default`
- Probe entrypoint: `scripts/probe_dualscope_first_slice_model_execution_capability.py`

## Deliverables

- `src/eval/dualscope_first_slice_model_execution_enablement.py`
- `src/eval/post_dualscope_first_slice_model_execution_enablement_analysis.py`
- `scripts/build_dualscope_first_slice_model_execution_enablement.py`
- `scripts/build_post_dualscope_first_slice_model_execution_enablement_analysis.py`
- `docs/dualscope_first_slice_model_execution_enablement.md`
- Output artifacts under `outputs/dualscope_first_slice_model_execution_enablement/default`

## Progress

- [x] M1: model execution scope and probe contract frozen
- [x] M2: implementation, CLI, and probe artifacts completed
- [x] M3: single verdict and recommendation completed

## Surprises & Discoveries

- To be updated by generated artifacts.

## Decision Log

- Minimal generation is sufficient for enablement; it does not imply paper-level performance.
- CPU fallback is recorded, but large-model real execution should prefer CUDA.

## Plan of Work

Run a bounded generation probe through the existing local-model probe script, copy its outputs into the stage artifact contract, compile all new files, and emit a conservative verdict.

## Concrete Steps

1. Build enablement artifacts.
2. Run post-analysis.
3. Update long-run status.

## Validation and Acceptance

The stage is validated only if model/tokenizer loading and at least one minimal generation sample pass, py_compile passes, and no forbidden expansion is detected.

## Idempotence and Recovery

The output directory can be deleted and regenerated. If OOM occurs, rerun with fewer samples or smaller `max_new_tokens`.

## Outputs and Artifacts

- `dualscope_first_slice_model_execution_enablement_scope.json`
- `dualscope_first_slice_model_load_check.json`
- `dualscope_first_slice_generation_probe.json`
- `dualscope_first_slice_generation_probe_details.jsonl`
- `dualscope_first_slice_generation_probe_report.md`
- `dualscope_first_slice_model_execution_enablement_summary.json`
- `dualscope_first_slice_model_execution_enablement_verdict.json`
- `dualscope_first_slice_model_execution_enablement_next_step_recommendation.json`

## Remaining Risks

- CUDA/OOM can block real generation.
- Passing this probe does not mean Stage 1 and Stage 2 entrypoints have been fully converted to model-execution mode.
