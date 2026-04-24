# 143 Route-C Output Normalization Stability Extension Recheck

## Background

Stage 141 completed a minimal parser/output-normalization repair and restored route_c label-path execution to PASS with dual-class outputs.

Stage 142 then ran repeated same-setting reruns and confirmed no regressions across 3 runs, but concluded only `Provisionally stable` due to limited rerun coverage.

This stage 143 is the direct continuation of 142's single recommendation. The task is strictly constrained to a minimal stability extension under fully frozen settings.

## Why 142 remained Provisionally stable

- 142 observed perfect restoration metrics under frozen settings.
- 142 rerun count was only 3.
- 142 policy required larger repeated evidence before upgrading to `Stable enough`.
- Therefore 142 kept a conservative verdict and requested one more minimal repeated-rerun extension without any semantic changes.

## Frozen settings inherited from 142

The following fields must be inherited exactly from:
`outputs/model_axis_1p5b_route_c_label_output_normalization_stability_recheck/default/route_c_label_output_normalization_stability_frozen_settings.json`

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

Only allowed to vary for rerun identity/audit:

- rerun_id
- run_dir
- rerun_tag
- timestamp_fields
- report_text

## Upgrade criteria for verdict

Verdict is single-choice only:

1. Upgrade to `Stable enough`:
- All newly added reruns are retained and auditable.
- New reruns keep gate PASS, dual-class restoration, and consistency restoration.
- No new regression to BLOCKED or single-class.
- Cumulative (142 + 143) evidence also has no regression.
- Parseability remains within acceptable fluctuation band relative to 142:
	- parsed_option_count min >= 5
	- punct_only_ratio max <= 0.0
	- missing_option_ratio max <= 0.16666666666666666
- Cumulative rerun count reaches at least 8 (3 existing + >=5 additional).

2. Keep `Provisionally stable`:
- Core restoration mostly holds, but evidence still insufficient to claim stable-enough confidence.
- Or parseability has only mild drift without explicit blocked/single-class regression.

3. Downgrade to `Not yet stable`:
- Any regression to BLOCKED in added or cumulative runs.
- Any regression to single-class execution_label_set.
- Any clear consistency collapse.
- Any material parseability regression (e.g., punct_only_ratio > 0 or parsed_option_count drops below 5).

## Goal

Under fully frozen 142 settings, run a minimal extension of repeated controlled reruns by increasing only rerun count, then decide whether verdict can be upgraded from `Provisionally stable` to `Stable enough`.

## Non-goals

- No parser rule changes.
- No normalization strategy changes.
- No gate threshold or gate logic changes.
- No benchmark truth semantics changes.
- No model-axis expansion.
- No budget expansion.
- No prompt family / attack family expansion.
- No route_b work.
- No overwrite or deletion of 142 artifacts.

## Extension rerun design

- Inherit 142 frozen settings exactly.
- Additional rerun count in 143: 5 (minimal extension).
- Total repeated coverage for decision: 8 runs (142:3 + 143:5).
- Keep all runs (`no cherry-pick`).
- Deterministic decode is still used (seed=42, do_sample=false), but repeated reruns still matter for execution-path stability validation (runtime variability, pipeline I/O consistency, artifact integrity, and no hidden nondeterministic regressions).

## Stability aggregation plan

Produce three views:

1. 143-added-runs-only aggregation:
- gate_pass_rate
- dual_class_restoration_rate
- consistency_restored_rate
- any_regression_to_blocked
- any_regression_to_single_class
- parsed_option_count range
- missing_option_ratio range
- punct_only_ratio range

2. Cumulative 142+143 aggregation:
- cumulative pass/restoration/consistency rates
- total run count
- cumulative regression flags
- parseability range/min/max/mean

3. Four-stage evidence chain:
- 140 BLOCKED
- 141 first recovery
- 142 repeated recheck (3)
- 143 extension recheck (+5)

## Risks

- GPU/runtime nondeterminism can still appear despite deterministic decode.
- If any regression appears, verdict must be downgraded or remain conservative.
- Parseability thresholds must not be loosened to force a verdict upgrade.

## Milestones

- [x] M1: extension rerun protocol frozen
- [x] M2: additional repeated reruns completed
- [x] M3: extended stability verdict and recommendation completed

## Exit criteria

- 143 frozen settings artifact confirms exact inheritance from 142.
- 5 additional reruns are completed and all retained.
- 143-added and 142+143 cumulative aggregations are produced.
- Four-stage compare (140/141/142/143) is produced.
- Single final verdict is produced (`Stable enough` / `Provisionally stable` / `Not yet stable`).
- Exactly one next-step recommendation is produced.
