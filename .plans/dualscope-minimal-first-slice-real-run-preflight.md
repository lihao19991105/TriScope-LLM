# dualscope-minimal-first-slice-real-run-preflight

## Background

The minimal first-slice real-run plan has been validated. It freezes the first real-run scope, commands, resources, expected artifacts, and failure fallbacks, but it did not execute training or a real experiment. This stage executes the preflight checks required before a real run can safely begin.

## Why preflight follows real-run plan

The real-run plan identified that the local Qwen2.5-1.5B model path exists, while the Stanford Alpaca first-slice JSONL is still a placeholder requirement. Preflight must verify that situation rather than assuming readiness.

## Frozen dependencies

- `dualscope-illumination-screening-freeze`
- `dualscope-confidence-verification-with-without-logprobs`
- `dualscope-budget-aware-two-stage-fusion-design`
- `dualscope-experimental-matrix-freeze`
- `dualscope-minimal-first-slice-real-run-plan`

## Goal

Check whether the minimal first-slice real run can safely begin.

## Non-goals

- No LoRA / QLoRA training.
- No full matrix run.
- No benchmark truth or gate changes.
- No fake data generation.
- No route_c recursion.

## Preflight scope

The scope includes dataset, model, tokenizer, model config, GPU, output writability, disk space, stage artifacts, contract compatibility, capability mode, planned commands, py_compile, dry-run config, and forbidden-expansion checks.

## Dataset checks

Check the exact JSONL path from the real-run plan. If missing, mark dataset checks as blocked and do not fabricate data.

## Model checks

Check local model path and config files without loading full model weights.

## Tokenizer checks

Attempt a local tokenizer load with `local_files_only=True`; mark failure honestly if unavailable.

## GPU checks

Check torch availability, CUDA availability, visible GPU count, names, and memory where available.

## Output directory checks

Create the preflight output directory and verify write/delete of a temporary file.

## Stage artifact checks

Check Stage 1, Stage 2, Stage 3, experimental matrix, and real-run plan artifacts.

## Contract compatibility checks

Check Stage 1 candidate/risk fields, Stage 2 capability/degradation fields, and Stage 3 dependency/final decision fields.

## Capability mode checks

Do not pretend with-logprobs is available unless a future backend proves it. If unknown, require without-logprobs fallback.

## Disk space checks

Record filesystem free space in GB.

## Planned command consistency checks

Check commands remain planned-only and avoid full matrix, full finetune, route_c recursion, model-axis expansion, and budget expansion.

## Dry-run config checks

Build a config object containing dataset/model/trigger/target/capability/output/stage roots/commands/fallback fields. Do not execute training.

## py_compile checks

Compile the new preflight modules and CLIs plus related first-slice planning modules.

## Validation criteria

Validated requires dataset exists and schema is valid, model/tokenizer checks pass, output is writable, stage artifacts exist, contracts are compatible, commands are consistent, py_compile passes, dry-run config builds, and no forbidden expansion is found.

## Failure fallback plan

Missing dataset leads to `Partially validated` if the rest of the chain is healthy. Contract/code failures lead to blocker closure.

## Stop conditions

Stop on missing core artifacts, py_compile failure, output unwritable, model path missing without fallback, forbidden expansion, or any need to change benchmark truth / gate semantics.

## Risks

- Dataset path may remain missing.
- Tokenizer load may fail if dependencies are absent.
- CUDA may be unavailable in the current shell even if GPUs exist.
- With-logprobs capability is backend-dependent and may remain unknown.

## Milestones

- M1: preflight check scope and contracts frozen
- M2: preflight checks executed and artifacts completed
- M3: single verdict and single recommendation completed

## Exit criteria

- All required preflight artifacts exist.
- Checks are truthfully marked as passed, failed, blocked, unknown, or not executed.
- Post-analysis emits exactly one verdict and one recommendation.

## Progress

- [x] M1: preflight check scope and contracts frozen
- [x] M2: preflight checks executed and artifacts completed
- [x] M3: single verdict and single recommendation completed

