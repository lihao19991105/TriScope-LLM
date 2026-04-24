# 144 Route-C Stable Baseline Time-Separated Replay

## Background

Stage 143 completed the minimal stability extension under fully inherited 142 frozen settings and produced a single final verdict: `Stable enough`.

143 evidence chain (strictly frozen, no semantic changes):

- cumulative repeated reruns (142+143) = 8
- gate pass rate = 1.0
- dual-class restoration rate = 1.0
- consistency restored rate = 1.0
- no regression to BLOCKED
- no regression to single-class
- parseability remained stable:
  - parsed_option_count = 5
  - missing_option_ratio = 0.16666666666666666
  - punct_only_ratio = 0.0

This stage 144 is the direct continuation of 143's single recommendation.

## Why time-separated replay is needed after Stable enough

Repeated reruns in 142/143 established same-setting repeatability, but they were still in a relatively concentrated execution window.

A time-separated replay adds stronger evidence by validating whether the same frozen baseline remains stable when replayed at a later timepoint under unchanged execution semantics.

This step increases confidence that the baseline is not merely a short-window stable patch but a reproducible baseline across time.

## Frozen settings inherited from 143

Inherited source:

- `outputs/model_axis_1p5b_route_c_label_output_normalization_stability_extension_recheck/default/route_c_label_output_normalization_stability_extension_frozen_settings.json`

Must match exactly:

- execution_path = `run_route_c_v6`
- input_root = `outputs/model_axis_1p5b_route_c_anchor_execution_recheck/default/materialized_route_c_anchor_execution_inputs`
- model_profile_name = `pilot_small_hf`
- label_parse_mode = `robust_prefix`
- label_normalization_mode = `conservative`
- label_parser_instrumentation = `true`
- seed = `42`
- label_threshold = `0.5`
- reasoning_budget = `3`
- confidence_budget = `3`
- illumination_budget = `3`
- labeled_illumination_budget = `6`
- gate_definition_used_by_execution unchanged
- precheck_label_set_reference = `[0,1]`

Only allowed to vary as replay identity/audit fields:

- replay_id
- run_dir
- replay_tag
- timestamp fields
- report text fields

## Definition of time-separated replay

In this stage, `time-separated replay` means all of the following are true:

1. Replay starts strictly after stage-143 completion timestamp.
2. Replay artifacts are written to a brand-new stage-144 output root (no overwrite of 143).
3. Replay uses the exact same frozen execution settings as 143 (only run identity fields may differ).
4. Replay run count is at least 3 and all runs are retained (no cherry-pick).

Minimum protocol threshold for this stage:

- elapsed_minutes_since_stage_143 >= 10

This threshold is used only to reject same-batch immediate repetition; it does not alter any model/probe/gate semantics.

## Success / caution / failure criteria

### Replay confirmed

- Time-separation protocol is valid.
- All 144 replay runs keep:
  - gate PASS
  - dual-class restoration
  - consistency restored
- No regression to BLOCKED or single-class in 144 runs.
- Parseability remains stable in 144 runs:
  - parsed_option_count min >= 5
  - missing_option_ratio max <= 0.16666666666666666
  - punct_only_ratio max <= 0.0
- Cumulative 142+143+144 has no regression.

### Replay partially confirmed

- No hard regression to BLOCKED/single-class, and core restoration mostly holds.
- But at least one caution condition appears, such as:
  - mild parseability drift that does not cross hard-failure boundaries,
  - one-off consistency fragility without systemic collapse,
  - insufficient confidence in time-separation quality for strong confirmation.

### Replay not confirmed

- Any 144 replay run regresses to BLOCKED, or
- Any 144 replay run regresses to single-class label set, or
- Consistency restoration clearly fails, or
- Material parseability regression appears (e.g., punct_only_ratio > 0 or parsed_option_count < 5), or
- time-separation protocol is invalid.

## Goal

Under fully frozen 143 settings and a valid time-separated condition, run controlled replay (>=3 runs) and produce a single replay verdict on cross-time reproducibility.

## Non-goals

- No parser changes.
- No normalization changes.
- No gate or threshold changes.
- No benchmark-truth semantic changes.
- No execution path changes.
- No model-axis expansion.
- No budget expansion.
- No prompt-family/attack-family expansion.
- No route_b extension.
- No overwrite/deletion of 143 artifacts.

## Replay design

1. Load and verify 143 frozen settings.
2. Validate inherited fields against current substrate and budgets.
3. Compute and record time-separation evidence against 143 completion artifacts.
4. Execute 3 time-separated replay runs with exactly inherited settings.
5. Keep all replay runs and emit run-level details.
6. Build 144-only summary and cumulative 142+143+144 metrics.
7. Produce 140/141/142/143/144 five-stage comparison and a single replay verdict.

## Validation plan

M1 validation:

- 144 plan exists and is self-contained.
- 143 frozen settings inheritance is explicit.
- time-separated replay protocol and threshold are explicit.
- replay confirmed / partially confirmed / not confirmed criteria are explicit.

M2 validation:

- At least 3 replay runs completed.
- All runs are retained and replayable.
- No gate/model/budget/prompt semantic relaxations were introduced.
- 144 summary metrics are generated.

M3 validation:

- Analysis artifacts generated.
- Five-stage compare (140/141/142/143/144) generated.
- Single replay verdict generated (three-choice policy).
- Exactly one next-step recommendation generated.

## Risks

- Runtime/GPU variability can still create minor fluctuations despite deterministic decode settings.
- If elapsed time from 143 is too short, protocol validity may fail and replay must be rerun later.
- Replay evidence can be mixed: no hard regression but slight drift, requiring conservative partial confirmation.

## Milestones

- [x] M1: time-separated replay protocol frozen
- [x] M2: time-separated replay runs completed
- [x] M3: replay confirmation analysis and recommendation completed

## Exit criteria

- `route_c_stable_baseline_time_separated_replay_frozen_settings.json` exists.
- `route_c_stable_baseline_time_separated_replay_summary.json` exists.
- `route_c_stable_baseline_time_separated_replay_details.jsonl` exists.
- `route_c_stable_baseline_time_separated_replay_compare.json` exists.
- `route_c_stable_baseline_time_separated_replay_report.md` exists.
- `route_c_stable_baseline_time_separated_replay_next_step_recommendation.json` exists.
- `route_c_stable_baseline_time_separated_replay_verdict.json` exists.
- A single replay verdict is produced: `Replay confirmed` / `Replay partially confirmed` / `Replay not confirmed`.