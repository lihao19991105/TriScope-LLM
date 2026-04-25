# DualScope Qwen2.5-7B Resource Materialization Repair

## Purpose / Big Picture

Repair the Qwen2.5-7B resource materialization blocker after large mounted storage became available at `/mnt/sda3/lh`. The repair makes the SCI3 main-model path use mounted storage for Hugging Face cache, temporary files, and local model materialization, then verifies the resource with tokenizer/config checks without running response generation.

## Scope

### In Scope

- Use `/mnt/sda3/lh` for Hugging Face cache, model storage, and temporary files.
- Download or verify `Qwen/Qwen2.5-7B-Instruct` at `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Keep a repository symlink at `models/qwen2p5-7b-instruct`.
- Fix empty-directory detection so an empty local model directory does not count as materialized.
- Remove stale bridge verdicts that would skip the Qwen2.5-7B response-generation plan after resources become ready.
- Run tokenizer/config, disk, GPU, labeled-pairs, and target-response plan checks.

### Out of Scope

- No response generation.
- No metric computation.
- No full matrix, training, LoRA, or QLoRA.
- No benchmark truth or gate changes.
- No changes under `/mnt/sda3/CoCoNut-Artifact`.

## Repository Context

- Existing materialization logic lives in `src/eval/dualscope_qwen2p5_7b_resource_common.py` and `src/eval/dualscope_qwen2p5_7b_resource_materialization.py`.
- CLI entrypoint is `scripts/build_dualscope_qwen2p5_7b_resource_materialization.py`.
- Artifacts are written under `outputs/dualscope_qwen2p5_7b_resource_materialization/default` and analysis artifacts under `outputs/dualscope_qwen2p5_7b_resource_materialization_analysis/default`.

## Deliverables

- Correct local model materialization detection.
- Mounted-storage materialization artifacts.
- Updated queue behavior: validated resource materialization routes to `dualscope-qwen2p5-7b-first-slice-response-generation-plan`.

## Progress

- [x] Verified `/mnt/sda3/lh` is writable and has sufficient space.
- [x] Created cache/model/tmp directories under `/mnt/sda3/lh`.
- [x] Created `models/qwen2p5-7b-instruct` symlink.
- [x] Fixed empty local model directory detection.
- [x] Installed missing tokenizer transfer dependencies in the local `.venv`.
- [x] Downloaded and verified Qwen2.5-7B resource artifacts.
- [x] Confirmed tokenizer/config checks pass.
- [x] Confirmed GPU visibility is restored.

## Surprises & Discoveries

- The first rerun skipped download because the target model directory existed but was empty.
- `protobuf` was missing and blocked Qwen tokenizer loading.
- `HF_HUB_ENABLE_HF_TRANSFER=1` required the `hf_transfer` package.

## Decision Log

- Treat a model directory as materialized only when it contains config, tokenizer, and weight files.
- Do not write a validated bridge verdict for the response-generation plan from resource materialization; after resources are ready, the real plan task should run next.

## Plan of Work

Use the existing materialization CLI with mounted storage paths, repair local model readiness detection, rerun checks, then verify task orchestrator selection.

## Concrete Steps

1. Check repository and mounted storage state.
2. Create `/mnt/sda3/lh` model/cache/tmp directories.
3. Patch model materialization detection.
4. Run materialization and post-analysis.
5. Run py_compile and CLI help checks.
6. Run task orchestrator dry-run.
7. Commit, open PR, request review, and safe-merge if gates pass.

## Validation and Acceptance

- `dualscope_qwen2p5_7b_resource_materialization_verdict.json` reports `Qwen2.5-7B resource materialization validated`.
- tokenizer/config checks pass.
- disk readiness passes on `/mnt/sda3/lh`.
- task orchestrator selects `dualscope-qwen2p5-7b-first-slice-response-generation-plan`.

## Idempotence and Recovery

Rerunning the materialization CLI should skip download when the local model directory is already materialized and should still rerun tokenizer/config/data checks. If download is interrupted, rerun the same command against `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.

## Outputs and Artifacts

- `outputs/dualscope_qwen2p5_7b_resource_materialization/default`
- `outputs/dualscope_qwen2p5_7b_resource_materialization_analysis/default`
- `outputs/dualscope_task_orchestrator/default`

## Remaining Risks

- The model is downloaded and tokenizer/config verified, but no response generation has been run yet.
- Future generation should still check memory placement before loading Qwen2.5-7B.

## Next Suggested Plan

Run `dualscope-qwen2p5-7b-first-slice-response-generation-plan`.
