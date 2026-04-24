# dualscope-first-slice-dataset-materialization

## Purpose / Big Picture

Materialize the real Stanford Alpaca first-slice JSONL from a user-provided source, then validate schema, sliceability, manifest, and downstream readiness. This serves the DualScope first-slice real-run chain without training, full-matrix execution, or fake data.

## Scope

### In Scope
- Real-source-only Alpaca JSON/JSONL import.
- First-slice schema normalization and validation.
- Sliceability and manifest checks.
- Missing-source reporting if no real source is available.

### Out of Scope
- Downloading data.
- Creating synthetic Alpaca rows.
- Running LoRA / QLoRA training.
- Running the first-slice real run or full matrix.
- Changing benchmark truth or gate semantics.

## Repository Context

This plan follows `dualscope-first-slice-preflight-repair` and uses `scripts/build_dualscope_first_slice_alpaca_jsonl.py` plus `scripts/check_dualscope_first_slice_dataset_schema.py`.

## Deliverables

- Materialization implementation and CLI.
- Post-analysis implementation and CLI.
- Materialization artifacts under `outputs/dualscope_first_slice_dataset_materialization/default`.
- Documentation under `docs/`.

## Progress

- [x] M1: dataset materialization source/schema/sliceability scope frozen.
- [x] M2: materialization artifacts and analysis completed.
- [x] M3: single verdict and single recommendation completed.

## Surprises & Discoveries

- No real Alpaca source file is present in the repository workspace.

## Decision Log

- Missing source produces `Partially validated`, not fake output.
- Next step after partial materialization is the data-source intake package.

## Plan of Work

Build a materialization wrapper that either imports a real source file or emits missing-source blockers and command guidance.

## Concrete Steps

1. Check source file.
2. If present, normalize and validate.
3. If absent, emit missing requirements and blockers.
4. Run post-analysis.

## Validation and Acceptance

The stage is complete if artifacts, report, verdict, recommendation, and `py_compile` pass without synthetic data.

## Idempotence and Recovery

Rerunning with the same real source, seed, and max examples overwrites deterministic artifacts.

## Outputs and Artifacts

`outputs/dualscope_first_slice_dataset_materialization/default`

## Remaining Risks

Real source file still requires user action.

## Next Suggested Plan

If validated, run preflight rerun. If partially validated due source missing, run data-source intake package.
