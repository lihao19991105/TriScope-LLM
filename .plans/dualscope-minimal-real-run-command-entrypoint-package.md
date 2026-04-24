# dualscope-minimal-real-run-command-entrypoint-package

## Background

The DualScope first-slice data blocker has been removed: the official Stanford Alpaca source is available, the 72-row first-slice JSONL has been materialized, and the preflight rerun has validated dataset, model, tokenizer, GPU/CUDA, and Stage 1 / Stage 2 / Stage 3 contract readiness.

The remaining blocker is narrower: the minimal real-run command plan references six entrypoint scripts that were not present. This package implements those entrypoints in dry-run / contract-check mode before any real training or full inference is allowed.

## Why command entrypoint package follows real-run readiness partially validated

The previous readiness package was `Partially validated` because the command plan could not be executed safely: the scripts for data slicing, Stage 1, Stage 2, Stage 3, evaluation, and report generation were missing. This phase resolves that blocker without starting LoRA/QLoRA training or claiming real performance.

## Frozen dependencies

- Dataset: `data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl`
- Model axis: existing Qwen2.5-1.5B first-slice plan
- Stage 1: illumination screening contract
- Stage 2: confidence verification contract
- Stage 3: budget-aware fusion contract
- Hardware target: 2 x RTX 3090 for future real run

## Current blockers

- Missing command entrypoints:
  - `scripts/build_dualscope_first_slice_data_slice.py`
  - `scripts/run_dualscope_stage1_illumination.py`
  - `scripts/run_dualscope_stage2_confidence.py`
  - `scripts/run_dualscope_stage3_fusion.py`
  - `scripts/evaluate_dualscope_first_slice.py`
  - `scripts/build_dualscope_first_slice_real_run_report.py`

## Goal

Implement a minimal, auditable command-entrypoint package that supports dry-run / contract-check execution and produces schema-compatible artifacts for the first-slice chain.

## Non-goals

- No training
- No full model inference
- No full matrix execution
- No benchmark truth or gate changes
- No route_c recursion or `199+` planning
- No performance claims from dry-run placeholders

## Required entrypoints

The six required entrypoints are implemented under `scripts/` and backed by shared helpers in `src/eval/dualscope_real_run_entrypoint_common.py`.

## Entrypoint CLI contract

Each entrypoint supports:

- `--output-dir`
- `--dry-run`
- `--contract-check`
- `--seed`
- JSON summary
- JSONL details
- markdown report where applicable

Some entrypoints also support aliases from the frozen planned command plan, such as `--input`, `--stage1-dir`, `--stage2-dir`, `--fusion-dir`, and `--run-dir`.

## Dry-run behavior

Dry-run produces deterministic, protocol-compatible placeholder artifacts. It does not execute training, large model inference, logprob requests, or any full experiment matrix.

## Artifact contract

The dry-run chain produces:

- data slice artifacts
- Stage 1 illumination outputs
- Stage 2 confidence outputs
- Stage 3 fusion outputs
- evaluation placeholders
- report skeleton

## Stage 1 entrypoint contract

Stage 1 reads candidate queries and emits screening risk, candidate flag, template results, aggregate features, and budget usage.

## Stage 2 entrypoint contract

Stage 2 reads Stage 1 outputs and emits capability mode, verification risk, lock evidence, fallback flag, budget usage, and fusion-readable fields.

## Stage 3 entrypoint contract

Stage 3 reads Stage 1 / Stage 2 outputs and emits final risk score, final risk bucket, decision flag, verification triggered, evidence summary, and budget usage.

## Evaluation entrypoint contract

Evaluation checks metric-required fields and writes placeholders only. It must not claim AUROC/F1 or other real performance without labels and real run outputs.

## Report entrypoint contract

The report builder reads summaries and emits a first-slice real-run report skeleton with dry-run markers.

## Py-compile plan

Run `py_compile` over the common helper, package scripts, post-analysis, and all six entrypoints before validation.

## Dry-run validation plan

The package runner executes all six entrypoints in dry-run / contract-check mode and checks required artifacts plus chain compatibility.

## Readiness rerun plan

After entrypoints are implemented, rerun the minimal real-run readiness package to verify that the missing-entrypoint blocker is gone.

## Risks

- Dry-run artifacts are contract evidence, not performance evidence.
- The next real-run phase still must decide whether optional LoRA training is executed.

## Milestones

- M1: entrypoint scope and CLI contracts frozen
- M2: six entrypoint scripts implemented and dry-run artifacts completed
- M3: single verdict and single recommendation completed

## Exit criteria

The phase exits with one of:

- `Real-run command entrypoint package validated`
- `Partially validated`
- `Not validated`

