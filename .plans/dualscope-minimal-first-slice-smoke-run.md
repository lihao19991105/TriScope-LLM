# dualscope-minimal-first-slice-smoke-run

## Background

The first-slice execution plan validated a minimal DualScope slice. This stage runs a controlled smoke to verify that the Stage 1 -> Stage 2 -> Stage 3 artifact flow can be emitted under that slice.

## Goal

Produce minimal smoke-run artifacts for the first slice without running the full experimental matrix.

## Non-goals

- No full matrix execution.
- No new dataset/model/trigger/target expansion.
- No training.
- No route_c continuation.
- No benchmark truth or gate change.

## Smoke design

The smoke uses three controlled representative examples to emit Stage 1 illumination, Stage 2 confidence, Stage 3 fusion, baseline, metric placeholder, and budget artifacts. These are protocol smoke artifacts, not performance claims.

## Validation criteria

- All expected first-slice artifacts exist.
- Stage 1 / Stage 2 / Stage 3 public fields exist.
- Capability mode is explicit.
- Budget and metrics placeholders exist.
- No full matrix execution is recorded.

## Milestones

- M1: smoke-run input and expected artifact scope frozen
- M2: controlled smoke artifacts emitted and analyzed
- M3: single verdict and single recommendation completed

## Exit criteria

If validated, the only next step is `dualscope-first-slice-artifact-validation`.

## Progress

- [x] M1: smoke-run input and expected artifact scope frozen
- [x] M2: controlled smoke artifacts emitted and analyzed
- [x] M3: single verdict and single recommendation completed

