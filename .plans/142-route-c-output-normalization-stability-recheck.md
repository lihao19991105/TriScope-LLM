# 142 Route-C Output Normalization Stability Recheck

## Background

141 completed parser/output-normalization minimal repair on route_c label path and produced a positive recovery signal under controlled settings (gate PASS, execution_label_set=[0,1], consistency_restored=true).

## Why stability confirmation is needed

A single positive controlled recheck is not sufficient to claim stable recovery. Before treating this path as a trustworthy baseline, we need repeated same-setting reruns to verify that recovery does not regress to BLOCKED or single-class behavior.

## Frozen settings from 141

Must remain unchanged for all 142 reruns:

- Execution path: `run_route_c_v6` via existing route_c controlled path.
- Input substrate: `outputs/model_axis_1p5b_route_c_anchor_execution_recheck/default/materialized_route_c_anchor_execution_inputs`.
- Model axis/profile: `pilot_small_hf` (Qwen2.5-1.5B-Instruct local).
- Parse mode: `robust_prefix`.
- Normalization mode: `conservative`.
- Parser instrumentation: enabled (`True`).
- Gate standard: route_c label-health gate rule unchanged (ready_to_run + parsed_option_count and existing gate outputs).
- Budget/sample counts: reasoning/confidence/illumination=3, labeled_illumination=6.
- Decoding knobs: do_sample=false, temperature=0.0, max_new_tokens=16 for labeled illumination profile.
- Label semantics: benchmark-truth-leaning correctness mapping unchanged.

Allowed to vary without changing experiment semantics:

- rerun_id / run_tag / output subdirectory naming.
- report formatting fields.

## Goal

Run minimal repeated controlled reruns (>=3) under frozen settings and decide whether 141 recovery is reproducible and stable enough for baseline use.

## Non-goals

- No parser strategy expansion.
- No gate threshold changes or bypass.
- No model-axis expansion.
- No budget expansion.
- No new prompt family or attack family.
- No route_b or unrelated module changes.

## Recheck design

- Build a dedicated stability runner that executes three sequential reruns with the exact frozen settings.
- Keep seed fixed to 42 across reruns to test path stability under deterministic decode and avoid changing experiment semantics.
- Record run-level outputs for each rerun:
  - gate_status
  - execution_label_set
  - consistency_restored
  - parseability metrics
  - failure-category distribution
- Preserve all rerun outputs; do not drop failed runs.
- Build a post-analysis that aggregates run-level metrics and compares three phases:
  1. 140 blocked state,
  2. 141 first recovery,
  3. 142 repeated rerun stability.

## Stability criteria

A rerun set is considered stable only if:

- gate_status remains PASS across all reruns,
- execution_label_set remains [0,1] across all reruns,
- consistency_restored remains true across all reruns,
- no rerun regresses to single-class or BLOCKED,
- parseability metrics stay in narrow observed range (reported min/max/mean).

## Validation outputs

- `route_c_label_output_normalization_stability_frozen_settings.json`
- `route_c_label_output_normalization_stability_recheck_summary.json`
- `route_c_label_output_normalization_stability_recheck_details.jsonl`
- `route_c_label_output_normalization_stability_compare.json`
- `route_c_label_output_normalization_stability_report.md`
- `route_c_label_output_normalization_stability_next_step_recommendation.json`
- `route_c_label_output_normalization_stability_verdict.json`

## Risks

- GPU/runtime nondeterminism could still introduce minor variation despite deterministic decode settings.
- If any run regresses, verdict must remain conservative and cannot be promoted.
- Existing gate semantics in execution path and external gate-definition artifact are not fully identical; this must be documented, not silently merged.

## Milestones

- [x] M1: stable rerun protocol frozen
- [x] M2: repeated controlled reruns completed
- [x] M3: stability analysis and recommendation completed

## Progress notes

- M1 completed with explicit frozen settings artifact and rerun protocol definition.
- M2 completed with 3 repeated same-setting reruns and full run-level detail retention.
- M3 completed with three-stage compare (140/141/142), single verdict, and one next-step recommendation.

## Exit criteria

- Three reruns completed under frozen settings with full run-level records.
- Cross-rerun aggregate statistics are produced.
- Three-stage compare (140 vs 141 vs 142) is produced.
- Final verdict is explicit and single-choice: Stable enough / Provisionally stable / Not yet stable.
- Exactly one next-step recommendation is provided.
