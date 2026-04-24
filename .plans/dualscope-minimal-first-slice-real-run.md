# dualscope-minimal-first-slice-real-run

## Background

DualScope has completed Stage 1 / Stage 2 / Stage 3 protocol freezes, experimental matrix freeze, first-slice planning, smoke artifacts, real-run planning, preflight repair, dataset materialization, preflight rerun, and command-entrypoint packaging. The latest readiness verdict is `Minimal real run readiness validated`.

## Why minimal first-slice real run follows readiness validated

The data, model path, tokenizer, GPU/CUDA visibility, command entrypoints, and artifact contracts are now ready for the first minimal run. This phase executes only the frozen first-slice pipeline and does not expand into the full matrix.

## Frozen dependencies

- Dataset: `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`
- Scope: Stanford Alpaca, lexical trigger, fixed target behavior
- Entry points: six command scripts validated by `dualscope-minimal-real-run-command-entrypoint-package`
- Stage contracts: frozen DualScope Stage 1 / Stage 2 / Stage 3 artifacts
- Hardware: 2 x RTX 3090 available from preflight, though this run does not train

## Goal

Run the minimal first-slice pipeline from data slice through report generation, validate required artifacts and contract compatibility, and output one verdict.

## Non-goals

- No full matrix
- No full Alpaca run
- No multi-model comparison
- No LoRA/QLoRA training in this phase
- No full model inference if entrypoints remain protocol-compatible deterministic
- No benchmark truth or gate changes
- No route_c recursion
- No real performance claims from metric placeholders

## Execution scope

The run executes:

1. data slice
2. Stage 1 illumination
3. Stage 2 confidence
4. Stage 3 fusion
5. evaluation placeholders
6. report skeleton

## Dataset scope

The input is the 72-row materialized Stanford Alpaca first-slice JSONL.

## Model scope

The local Qwen2.5-1.5B path remains the frozen first-slice model reference, but this phase does not execute full model inference or training.

## Capability mode

The run accepts `--capability-mode auto`; current deterministic Stage 2 entrypoint falls back to `without_logprobs` and records a degradation flag because it does not request logits.

## Stage 1 execution plan

Run `scripts/run_dualscope_stage1_illumination.py` on candidate queries and record protocol-compatible deterministic outputs.

## Stage 2 execution plan

Run `scripts/run_dualscope_stage2_confidence.py` on Stage 1 outputs with fallback enabled.

## Stage 3 execution plan

Run `scripts/run_dualscope_stage3_fusion.py` on Stage 1 and Stage 2 outputs.

## Evaluation plan

Run `scripts/evaluate_dualscope_first_slice.py`; if labels are unavailable, only metric placeholders are emitted.

## Report plan

Run `scripts/build_dualscope_first_slice_real_run_report.py` using generated stage summaries.

## Artifact contract

Artifacts are written under `outputs/dualscope_minimal_first_slice_real_run/default` with subdirectories:

- `data_slice`
- `stage1_illumination`
- `stage2_confidence`
- `stage3_fusion`
- `evaluation`
- `report`

## Validation criteria

The phase validates required artifact existence, field-level contract compatibility, `py_compile`, no full matrix execution, no truth/gate changes, and no old route_c continuation.

## Failure fallback plan

If a required artifact or contract breaks, stop and enter `dualscope-minimal-first-slice-real-run-blocker-closure`.

## Stop conditions

- missing first-slice JSONL
- missing entrypoint scripts
- broken Stage 1 / Stage 2 / Stage 3 chain
- py_compile failure
- forbidden expansion
- any need to change benchmark truth or gate semantics

## Risks

Because current Stage 1 / Stage 2 entrypoints are protocol-compatible deterministic entrypoints rather than full model inference, this run may only be `Partially validated` even if the artifact chain succeeds.

## Milestones

- M1: minimal real-run scope and command chain frozen
- M2: minimal real-run execution and artifacts completed
- M3: single verdict and single recommendation completed

## Exit criteria

Allowed verdicts:

- `Minimal first-slice real run validated`
- `Partially validated`
- `Not validated`

