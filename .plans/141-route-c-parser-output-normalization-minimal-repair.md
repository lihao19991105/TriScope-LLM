# 141 Route-C Parser Output Normalization Minimal Repair

## Background

Route-C label path has already been repaired to the point where execution emits explicit gate artifacts and fails fast with explainable diagnostics (138/139/140 completed). The current blocker is no longer visibility, but parseability collapse on labeled illumination outputs in execution-time runs.

## Current blocking facts

- Gate remains effective and must stay unchanged; current execution is BLOCKED by label-health gate.
- Current blocking metrics on the execution path are:
  - parsed_option_count = 0
  - missing_option_ratio = 1.0
  - punct_only_ratio = 1.0
  - class_balance = {label_0: 0, label_1: 6}
- Consistency recheck result remains not restored:
  - precheck_label_set = [0, 1]
  - execution_label_set = [1]
  - consistency_restored = false
- Post-repair analysis (140) already concluded that anchor-aware baseline is still the working baseline and label path remains the primary blocker.

## Goal

Implement a minimal, auditable parser/output-normalization repair chain for labeled illumination so that parseability failures become fully classifiable and reproducible, while preserving label semantics and existing gate thresholds.

## Non-goals

- No gate bypass, no gate weakening, no threshold relaxation.
- No model-axis expansion, no budget expansion, no prompt-family expansion.
- No benchmark-truth semantic changes.
- No broad refactor of route_b, fusion architecture, or unrelated pipelines.

## Execution path map

Execution path (route_c label path) to be validated and documented in code/artifacts:

1. Raw output generation:
	- src/probes/illumination_probe.py
	- output: route_c_v6_labeled_illumination/illumination_probe/raw_results.jsonl
2. Parser + normalization entry:
	- src/fusion/benchmark_truth_leaning_label.py (build_benchmark_truth_leaning_dataset)
3. Label assignment and health row materialization:
	- output: route_c_v6_dataset_dir/benchmark_truth_leaning_label_health_rows.jsonl
	- output: route_c_v6_dataset_dir/benchmark_truth_leaning_label_health_summary.json
4. Gate read stage:
	- src/eval/rerun_route_c_on_labeled_split_v6.py
	- output: route_c_v6_label_health_gate_result.json
5. Recheck summary stage:
	- src/eval/route_c_label_path_consistency_recheck.py (existing)
	- plus new normalization-aware recheck summary outputs (141 scope)

Precheck/execution consistency note:
- Precheck in src/eval/model_axis_1p5b_route_c_anchor_followup_v2.py is dataset-level logistic feasibility precheck and does not parse labeled illumination raw response text at runtime.
- Execution path performs runtime parsing from labeled illumination raw outputs.
- Therefore, consistency differences are expected and must remain explicitly reported, not hidden.

## Proposed minimal changes

1. Add parser instrumentation and conservative normalization in benchmark_truth_leaning_label path:
	- raw_response capture
	- normalized_response capture
	- raw parser outcome
	- normalized parser outcome
	- final parser decision path
	- structured failure categories

2. Keep defaults backward compatible:
	- existing behavior preserved unless explicit normalization mode is enabled.

3. Add normalization-analysis and recheck build CLIs:
	- build_route_c_label_output_normalization.py
	- build_route_c_label_output_normalization_recheck.py
	- build_post_route_c_label_output_normalization_analysis.py

4. Add before/after artifacts:
	- summary json
	- details jsonl
	- compare json
	- markdown report
	- next-step recommendation json

## Validation plan

M1 validation:
- Confirm chain raw -> normalized -> parsed -> gate -> recheck is documented and materialized in artifacts.
- Confirm failure categories include at least:
  - empty
  - whitespace_only
  - punct_only
  - quote_wrapped_label
  - bracket_wrapped_label
  - prefix_suffix_noise
  - json_like_but_unparsed
  - unknown_token
  - multi_label_ambiguous
  - label_not_in_set
  - parser_exception
  - other
- Confirm before/after parser outcome compare is generated.

M2 validation:
- Run one controlled recheck under unchanged gate standards.
- Verify no threshold changes and no semantic remap shortcuts.
- Verify execution_label_set and gate status are reproducible in outputs.

M3 validation:
- Generate post-recheck analysis.
- Explicitly answer whether execution_label_set is restored to [0,1].
- If not restored, keep BLOCKED with evidence and produce one minimal next action.

## Risks

- If runtime output remains punctuation-only, conservative normalization cannot legitimately recover labels.
- Improvement in parseability may be zero; this is acceptable if failure evidence becomes more granular and reproducible.
- Precheck/execution mismatch may persist because they are different checkpoints in the pipeline.

## Milestones

- [x] M1: parser / normalization instrumentation ready
- [x] M2: controlled recheck completed
- [x] M3: post-recheck repair analysis completed

## Progress notes

- M1 completed with line-level parser decision instrumentation and raw-vs-normalized compare artifacts.
- M2 completed with one gate-protected controlled recheck under unchanged thresholds and unchanged semantics.
- M3 completed with post-recheck analysis and next-step recommendation artifacts.

## Exit criteria

- Required artifacts are generated under:
  - outputs/model_axis_1p5b_route_c_label_output_normalization/default
  - outputs/model_axis_1p5b_route_c_label_output_normalization_recheck/default
  - outputs/model_axis_1p5b_route_c_label_output_normalization_analysis/default
- Gate remains active and unmodified.
- Label semantics remain unchanged.
- Final conclusion states restored/not-restored truthfully with evidence.
