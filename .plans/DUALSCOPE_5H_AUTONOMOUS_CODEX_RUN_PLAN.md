
# DualScope-LLM 5-Hour Autonomous Codex Run Plan

## 0. Purpose

This file is a source-of-truth runbook for a long autonomous Codex session of roughly five hours.

Codex must read this file together with:

- AGENTS.md
- PLANS.md
- DUALSCOPE_MASTER_PLAN.md

Codex must execute the plan phase by phase. It must keep a running log, run validations after each phase, keep changes scoped, and stop only when a defined stop condition is reached.

This plan is intentionally designed so that Codex does not stop after a single missing-data blocker. If the real Alpaca source file is missing, Codex must complete the data-intake package, dry-run contract validator, artifact validator hardening, and readiness package before stopping.

## 1. Current Repository State

The repository has officially pivoted from TriScope-LLM to DualScope-LLM.

DualScope-LLM is the current mainline:

- Stage 1: Illumination Screening
- Stage 2: Confidence Verification with / without logprobs
- Stage 3: Budget-Aware Two-Stage Fusion

The old route_c / 138–198 chain is not deleted. It is now treated as:

- reliability foundation
- implementation robustness
- appendix support
- execution-chain hardening evidence

It is not the default research mainline anymore.

Do not create 199+ route_c plans.

## 2. Already Completed DualScope Tasks

### 2.1 Stage 1

Task name:

dualscope-illumination-screening-freeze

Verdict:

Illumination screening freeze validated

Meaning:

- targeted ICL illumination screening definition frozen
- probe template family frozen
- feature schema frozen
- budget contract frozen
- IO contract frozen
- baseline plan frozen
- Stage 2 / Stage 3 interfaces frozen

### 2.2 Stage 2

Task name:

dualscope-confidence-verification-with-without-logprobs

Verdict:

Confidence verification freeze validated

Meaning:

- with-logprobs path frozen
- without-logprobs fallback frozen
- confidence schemas frozen
- fallback policy frozen
- Stage 1 to Stage 2 contract frozen
- Stage 2 to Stage 3 public fields frozen

### 2.3 Stage 3

Task name:

dualscope-budget-aware-two-stage-fusion-design

Verdict:

Budget-aware two-stage fusion design validated

Meaning:

- stage dependency contract frozen
- budget-aware policy frozen
- capability-aware fusion policy frozen
- final decision contract frozen
- baseline / ablation contract frozen
- cost analysis contract frozen

### 2.4 Experimental Matrix and First Slice

Already completed:

- dualscope-experimental-matrix-freeze
- dualscope-minimal-first-slice-execution-plan
- dualscope-minimal-first-slice-smoke-run
- dualscope-first-slice-artifact-validation
- dualscope-first-slice-report-skeleton
- dualscope-minimal-first-slice-real-run-plan
- dualscope-minimal-first-slice-real-run-preflight
- dualscope-first-slice-preflight-repair

Current known blockers:

1. Real Stanford Alpaca first-slice JSONL is missing.
2. Dataset schema and sliceability are blocked by dataset_missing.
3. CUDA/GPU was unavailable in the current environment.
4. Model path exists.
5. Tokenizer load passed.
6. Stage 1 / Stage 2 / Stage 3 artifacts exist and are compatible.
7. Preflight repair tooling is implemented and validated.

Missing target file:

data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl

Accepted real source field families:

- instruction / input / output
- prompt / response
- query / target

## 3. Five-Hour Autonomous Run Goal

The run should complete as many of the following phases as possible:

1. dualscope-first-slice-dataset-materialization
2. dualscope-minimal-first-slice-real-run-preflight-rerun
3. dualscope-first-slice-data-source-intake-package
4. dualscope-first-slice-dry-run-config-and-contract-validator
5. dualscope-first-slice-artifact-validator-hardening
6. dualscope-first-slice-readiness-report-package
7. conditional: dualscope-minimal-first-slice-real-run-readiness-package
8. conditional: dualscope-minimal-first-slice-real-run
9. conditional: dualscope-first-slice-real-run-artifact-validation
10. conditional: dualscope-first-slice-real-run-report

If a phase is blocked by missing real data or missing GPU, Codex must not stop immediately. It must proceed to the next non-blocked support package.

## 4. Global Rules

### 4.1 No old route_c recursion

Do not:

- generate 199+ route_c plans
- continue old recursive route_c rechecks
- treat route_c reliability work as the paper main innovation

### 4.2 No benchmark truth or gate changes

Do not:

- change labels
- relabel examples
- bypass gates
- weaken gates
- fake PASS results

### 4.3 No fake data

If no real Alpaca source file exists:

- do not generate fake Alpaca rows
- do not mark synthetic rows as real
- do not create fake target JSONL
- do not duplicate rows to reach requested count
- do not silently pass schema checks

### 4.4 No fake GPU

If CUDA is unavailable:

- record it honestly
- do not pretend GPU training ran
- continue CPU-safe preparation tasks only

### 4.5 No full experiment

Do not:

- run full matrix
- train all models
- expand model axis
- expand budget
- introduce new datasets
- run adaptive attacks

### 4.6 Every phase must have artifacts

Each phase must produce:

- plan
- implementation
- CLI
- output artifacts
- report
- verdict
- recommendation

## 5. Running Log

Create or update:

docs/dualscope_5h_autonomous_run_log.md

Append after every phase:

- timestamp
- phase name
- commands run
- created artifacts
- verdict
- blockers
- next action

Also create or update:

outputs/dualscope_5h_autonomous_run_status/default/dualscope_5h_autonomous_run_status.json

It must contain:

- started_at
- current_phase
- completed_phases
- blockers
- latest_verdict
- next_recommendation
- hard_stop_reached
- final_status

## 6. Phase 1: Dataset Materialization

Task:

dualscope-first-slice-dataset-materialization

### 6.1 Goal

Use a real Alpaca source file to generate:

data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl

Then validate:

- source existence
- schema
- sliceability
- manifest
- downstream readiness

### 6.2 Source discovery

Before asking the user, search local repository paths:

- data/raw/alpaca_data.json
- data/raw/alpaca_data.jsonl
- data/alpaca_data.json
- data/alpaca_data.jsonl
- data/stanford_alpaca/alpaca_data.json
- data/stanford_alpaca/alpaca_data.jsonl
- datasets/alpaca_data.json
- datasets/alpaca_data.jsonl
- datasets/stanford_alpaca/alpaca_data.json
- datasets/stanford_alpaca/alpaca_data.jsonl
- third_party/alpaca_data.json

Also search under data, datasets, and raw for filenames containing alpaca.

If network is available, Codex may try to fetch:

https://raw.githubusercontent.com/tatsu-lab/stanford_alpaca/main/alpaca_data.json

If network fails, do not fabricate data.

### 6.3 Required files

Add or update:

- .plans/dualscope-first-slice-dataset-materialization.md
- src/eval/dualscope_first_slice_dataset_materialization_common.py
- src/eval/dualscope_first_slice_dataset_materialization.py
- src/eval/post_dualscope_first_slice_dataset_materialization_analysis.py
- scripts/build_dualscope_first_slice_dataset_materialization.py
- scripts/build_post_dualscope_first_slice_dataset_materialization_analysis.py
- docs/dualscope_first_slice_dataset_materialization.md
- docs/dualscope_first_slice_data_source_requirements.md
- docs/dualscope_first_slice_dataset_schema_report.md

### 6.4 Main command

Use this command shape:

.venv/bin/python scripts/build_dualscope_first_slice_dataset_materialization.py --source-file <REAL_ALPACA_SOURCE_JSON_OR_JSONL> --output-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl --output-dir outputs/dualscope_first_slice_dataset_materialization/default --schema-check-output-dir outputs/dualscope_first_slice_dataset_schema_check/default --max-examples 72 --seed 2025 --split-name first_slice --dataset-id stanford_alpaca

Post-analysis command:

.venv/bin/python scripts/build_post_dualscope_first_slice_dataset_materialization_analysis.py --output-dir outputs/dualscope_first_slice_dataset_materialization_analysis/default

Schema check command:

.venv/bin/python scripts/check_dualscope_first_slice_dataset_schema.py --dataset-file data/stanford_alpaca/first_slice/alpaca_first_slice_source.jsonl --output-dir outputs/dualscope_first_slice_dataset_schema_check/default

### 6.5 Output schema

The materialized JSONL rows must contain:

- example_id
- dataset_id
- instruction
- input
- prompt
- response
- split
- source
- metadata

Rules:

- response must not be empty
- prompt must be present
- example_id must be stable
- synthetic_data_generated must be false
- prompt construction rule must be recorded
- field mapping must be recorded

### 6.6 Required artifacts

Main output:

outputs/dualscope_first_slice_dataset_materialization/default

Analysis output:

outputs/dualscope_first_slice_dataset_materialization_analysis/default

Required artifacts:

1. dualscope_first_slice_dataset_materialization_scope.json
2. dualscope_first_slice_dataset_source_check.json
3. dualscope_first_slice_dataset_materialization_manifest.json
4. dualscope_first_slice_dataset_schema_check.json
5. dualscope_first_slice_dataset_sliceability_check.json
6. dualscope_first_slice_dataset_materialization_summary.json
7. dualscope_first_slice_dataset_materialization_details.jsonl
8. dualscope_first_slice_dataset_materialization_report.md
9. dualscope_first_slice_dataset_materialization_verdict.json
10. dualscope_first_slice_dataset_materialization_next_step_recommendation.json

If source is missing, also create:

11. dualscope_first_slice_dataset_missing_requirements.json
12. dualscope_first_slice_dataset_materialization_blockers.json

### 6.7 Verdict

Allowed verdicts:

1. Dataset materialization validated
2. Partially validated
3. Not validated

Branching:

- If validated, go to Phase 2.
- If partially validated due to missing source, go to Phase 3, then Phase 4, Phase 5, and Phase 6.
- If not validated due to tooling failure, stop expansion and enter dataset-materialization-tooling-closure.

## 7. Phase 2: Preflight Rerun

Task:

dualscope-minimal-first-slice-real-run-preflight-rerun

Only enter if dataset materialization validated.

### 7.1 Goal

Rerun preflight after the real first-slice JSONL exists.

### 7.2 Required checks

Check:

- dataset path exists
- dataset schema valid
- dataset sliceability valid
- model path exists
- tokenizer loads
- model config readable
- CUDA/GPU availability
- output directory writable
- disk space
- Stage 1 artifacts exist
- Stage 2 artifacts exist
- Stage 3 artifacts exist
- experimental matrix artifacts exist
- first-slice real-run plan artifacts exist
- contract compatibility
- capability mode
- planned commands
- py_compile
- dry-run config
- forbidden expansion

### 7.3 Required files

Add or update:

- .plans/dualscope-minimal-first-slice-real-run-preflight-rerun.md
- src/eval/dualscope_first_slice_preflight_rerun.py
- src/eval/post_dualscope_first_slice_preflight_rerun_analysis.py
- scripts/build_dualscope_first_slice_preflight_rerun.py
- scripts/build_post_dualscope_first_slice_preflight_rerun_analysis.py
- docs/dualscope_first_slice_preflight_rerun.md

### 7.4 Commands

Main:

.venv/bin/python scripts/build_dualscope_first_slice_preflight_rerun.py --output-dir outputs/dualscope_first_slice_preflight_rerun/default

Post-analysis:

.venv/bin/python scripts/build_post_dualscope_first_slice_preflight_rerun_analysis.py --output-dir outputs/dualscope_first_slice_preflight_rerun_analysis/default

### 7.5 Verdict

Allowed verdicts:

1. First slice preflight rerun validated
2. Partially validated
3. Not validated

Branching:

- If validated, go to Phase 7.
- If partially validated due to GPU unavailable, go to Phase 6 and record GPU blocker.
- If not validated, stop real-run expansion.

## 8. Phase 3: Data Source Intake Package

Task:

dualscope-first-slice-data-source-intake-package

Enter if Phase 1 is partially validated because source is missing.

### 8.1 Goal

Create a complete user-facing package explaining exactly what real source file is needed and how to provide it.

### 8.2 Required files

Add or update:

- .plans/dualscope-first-slice-data-source-intake-package.md
- src/eval/dualscope_first_slice_data_source_intake_package.py
- src/eval/post_dualscope_first_slice_data_source_intake_package_analysis.py
- scripts/build_dualscope_first_slice_data_source_intake_package.py
- scripts/build_post_dualscope_first_slice_data_source_intake_package_analysis.py
- docs/dualscope_first_slice_data_source_intake_package.md
- docs/dualscope_alpaca_source_file_examples.md

### 8.3 Required artifacts

Output directory:

outputs/dualscope_first_slice_data_source_intake_package/default

Analysis directory:

outputs/dualscope_first_slice_data_source_intake_package_analysis/default

Artifacts:

1. dualscope_first_slice_data_source_requirements.json
2. dualscope_first_slice_accepted_source_formats.json
3. dualscope_first_slice_import_command_examples.json
4. dualscope_first_slice_schema_expectation.json
5. dualscope_first_slice_user_action_items.md
6. dualscope_first_slice_data_source_intake_summary.json
7. dualscope_first_slice_data_source_intake_report.md
8. dualscope_first_slice_data_source_intake_verdict.json
9. dualscope_first_slice_data_source_intake_next_step_recommendation.json

### 8.4 Verdict

Allowed verdicts:

1. Data source intake package validated
2. Partially validated
3. Not validated

If validated, continue to Phase 4.

## 9. Phase 4: Dry-Run Config and Contract Validator

Task:

dualscope-first-slice-dry-run-config-and-contract-validator

Can run even if the real source is missing.

### 9.1 Goal

Build a CPU-safe config validator proving Stage 1 / Stage 2 / Stage 3 contracts join correctly.

### 9.2 Required files

Add or update:

- .plans/dualscope-first-slice-dry-run-config-and-contract-validator.md
- src/eval/dualscope_first_slice_dry_run_config_validator.py
- src/eval/post_dualscope_first_slice_dry_run_config_validator_analysis.py
- scripts/build_dualscope_first_slice_dry_run_config_validator.py
- scripts/build_post_dualscope_first_slice_dry_run_config_validator_analysis.py
- docs/dualscope_first_slice_dry_run_config_validator.md

### 9.3 Required artifacts

Output directory:

outputs/dualscope_first_slice_dry_run_config_validator/default

Analysis directory:

outputs/dualscope_first_slice_dry_run_config_validator_analysis/default

Artifacts:

1. dualscope_first_slice_dry_run_config.json
2. dualscope_first_slice_stage_contract_join_map.json
3. dualscope_first_slice_artifact_path_plan.json
4. dualscope_first_slice_capability_fallback_config.json
5. dualscope_first_slice_budget_config.json
6. dualscope_first_slice_dry_run_validation_summary.json
7. dualscope_first_slice_dry_run_config_report.md
8. dualscope_first_slice_dry_run_config_verdict.json
9. dualscope_first_slice_dry_run_config_next_step_recommendation.json

### 9.4 Required checks

Check:

- Stage 1 outputs map to Stage 2 inputs
- Stage 2 outputs map to Stage 3 inputs
- capability mode is representable
- fallback degradation flag reaches fusion
- budget fields are connected
- artifact paths are consistent
- no forbidden expansion

### 9.5 Verdict

Allowed verdicts:

1. Dry-run config and contract validation validated
2. Partially validated
3. Not validated

If validated, continue to Phase 5.

## 10. Phase 5: Artifact Validator Hardening

Task:

dualscope-first-slice-artifact-validator-hardening

Can run even if the real source is missing.

### 10.1 Goal

Build a reusable artifact validator for future first-slice real-run outputs.

### 10.2 Required files

Add or update:

- .plans/dualscope-first-slice-artifact-validator-hardening.md
- src/eval/dualscope_first_slice_artifact_validator.py
- src/eval/post_dualscope_first_slice_artifact_validator_analysis.py
- scripts/check_dualscope_first_slice_artifacts.py
- scripts/build_dualscope_first_slice_artifact_validator_hardening.py
- scripts/build_post_dualscope_first_slice_artifact_validator_hardening_analysis.py
- docs/dualscope_first_slice_artifact_validator.md

### 10.3 Required artifacts

Output directory:

outputs/dualscope_first_slice_artifact_validator_hardening/default

Analysis directory:

outputs/dualscope_first_slice_artifact_validator_hardening_analysis/default

Artifacts:

1. dualscope_first_slice_required_artifact_schema.json
2. dualscope_first_slice_artifact_validator_rules.json
3. dualscope_first_slice_artifact_validator_summary.json
4. dualscope_first_slice_artifact_validator_report.md
5. dualscope_first_slice_artifact_validator_verdict.json
6. dualscope_first_slice_artifact_validator_next_step_recommendation.json

### 10.4 Validator must check

The validator must check:

- Stage 1 illumination artifacts
- Stage 2 confidence artifacts
- Stage 3 fusion artifacts
- metrics placeholders
- cost fields
- capability mode
- fallback flags
- final decision fields
- reports
- verdicts
- recommendations

### 10.5 Verdict

Allowed verdicts:

1. Artifact validator hardening validated
2. Partially validated
3. Not validated

If validated, continue to Phase 6.

## 11. Phase 6: Readiness Report Package

Task:

dualscope-first-slice-readiness-report-package

This is the default final phase if data or GPU blockers remain.

### 11.1 Goal

Summarize readiness state and provide one next action.

### 11.2 Required files

Add or update:

- .plans/dualscope-first-slice-readiness-report-package.md
- src/eval/dualscope_first_slice_readiness_report_package.py
- src/eval/post_dualscope_first_slice_readiness_report_package_analysis.py
- scripts/build_dualscope_first_slice_readiness_report_package.py
- scripts/build_post_dualscope_first_slice_readiness_report_package_analysis.py
- docs/dualscope_first_slice_readiness_report.md

### 11.3 Required artifacts

Output directory:

outputs/dualscope_first_slice_readiness_report_package/default

Analysis directory:

outputs/dualscope_first_slice_readiness_report_package_analysis/default

Artifacts:

1. dualscope_first_slice_readiness_summary.json
2. dualscope_first_slice_completed_components.json
3. dualscope_first_slice_blockers.json
4. dualscope_first_slice_user_action_items.md
5. dualscope_first_slice_next_command_plan.json
6. dualscope_first_slice_readiness_report.md
7. dualscope_first_slice_readiness_verdict.json
8. dualscope_first_slice_readiness_next_step_recommendation.json

### 11.4 Verdict

Allowed verdicts:

1. First slice readiness package validated
2. Partially validated
3. Not validated

Recommendation rules:

If real Alpaca source is still missing:
recommendation = Provide real Alpaca source file and rerun dataset materialization

If data is ready but GPU is unavailable:
recommendation = Move to GPU-enabled environment and rerun preflight

If data and GPU are ready and preflight validated:
recommendation = Enter minimal first-slice real run

## 12. Phase 7: Minimal First-Slice Real Run Readiness Package

Task:

dualscope-minimal-first-slice-real-run-readiness-package

Only enter if preflight rerun validated.

### 12.1 Goal

Prepare final go/no-go bundle immediately before actual minimal real run.

### 12.2 Required outputs

- run command plan
- GPU config confirmation
- dataset path confirmation
- model path confirmation
- scope confirmation
- verification checklist
- final go/no-go recommendation

### 12.3 Verdict

Allowed verdicts:

1. Minimal real run readiness validated
2. Partially validated
3. Not validated

If validated:
recommendation = Enter dualscope-minimal-first-slice-real-run

## 13. Phase 8: Minimal First-Slice Real Run

Task:

dualscope-minimal-first-slice-real-run

Only enter if:

- dataset materialization validated
- preflight rerun validated
- GPU available
- no forbidden expansion
- user-approved planned commands exist
- no benchmark truth or gate change required

### 13.1 Goal

Run only the minimal real first slice.

### 13.2 Hard restrictions

Do not:

- run full matrix
- run multiple model axes
- run 7B / 8B full experiments
- expand budget
- execute adaptive attacks
- relabel truth
- change gate

### 13.3 Required outputs

- Stage 1 outputs
- Stage 2 outputs
- Stage 3 outputs
- minimal metrics or metrics placeholders
- cost summary
- report
- verdict
- recommendation

### 13.4 Verdict

Allowed verdicts:

1. Minimal first-slice real run validated
2. Partially validated
3. Not validated

## 14. Py Compile Requirement

After every phase, run py_compile on all newly added Python files.

If py_compile fails:

- fix it
- rerun it
- do not continue until it passes

## 15. Stop Conditions

Stop expansion if:

1. benchmark truth must be changed
2. gate semantics must be changed
3. real source file is missing and all non-data-dependent packages are complete
4. model path is missing and no valid fallback exists
5. GPU is unavailable and all CPU-safe packages are complete
6. required contract is broken and cannot be repaired locally
7. py_compile repeatedly fails
8. stage verdict is Not validated due to tooling failure
9. next action would require full training or full matrix run

## 16. Final Delivery Format

At the end, output:

### 16.1 Actual completed phases

For each phase:
- phase name
- verdict
- whether continuation occurred

### 16.2 New or modified files

For each file:
- one-line purpose

### 16.3 Commands executed

List:
- data discovery commands
- download commands if attempted
- import commands
- schema check commands
- materialization commands
- preflight commands
- dry-run commands
- validator commands
- readiness commands
- py_compile commands

### 16.4 Key output directories

List each phase's:
- main output directory
- analysis output directory

### 16.5 Key artifacts

List most important artifacts per phase.

### 16.6 Current total status summary

In 10 lines or fewer, state:
- whether data blocker is resolved
- whether GPU blocker remains
- whether preflight is validated
- whether minimal real run can start

### 16.7 Current blockers or risks

If no blocker:
No current blocker, but full experimental matrix has not been run.

If blockers remain:
State exactly:
- blocker
- required user action
- next command after blocker is resolved

### 16.8 Next single recommendation

Only one recommendation.
It must belong to the DualScope mainline.
