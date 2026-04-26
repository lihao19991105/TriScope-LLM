# DualScope Qwen2.5-7B Response Generation Repair

## Purpose / Big Picture

The previous Qwen2.5-7B first-slice response-generation task was partially validated because the artifact contract and local model binding were present, but the real generation attempt hung after loading checkpoint shards onto a low-free-memory GPU. This repair makes the response-generation path budget-aware at the runtime-resource level: it must prove CUDA/device/memory readiness before loading the 7B model, otherwise it writes honest blockers and exits without fabricated responses or metrics.

This serves the DualScope-LLM SCI3 mainline by making the Qwen2.5-7B first-slice response-generation step recoverable and auditable before label-aligned metrics.

## Scope

### In Scope

- Add selected-GPU memory preflight before model load.
- Record CUDA device order, visible devices, selected physical GPU, selected free memory, and memory threshold in artifacts.
- Block CPU fallback by default for Qwen2.5-7B generation to avoid impractical hangs.
- Keep all response rows honest when generation is blocked.
- Update the run document and ExecPlan status.

### Out of Scope

- No training, LoRA, QLoRA, or full finetune.
- No full matrix execution.
- No AUROC, F1, ASR, clean utility, or paper-level metric computation.
- No benchmark truth, gate, route_c, or 199+ changes.
- No model download in this repair worktree.

## Repository Context

- Core response-generation logic: `src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py`
- CLI wrapper: `scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py`
- User-facing run document: `docs/dualscope_qwen2p5_7b_first_slice_response_generation.md`
- Prior partially validated task plan: `.plans/dualscope-qwen2p5-7b-first-slice-response-generation.md`
- Queue route: `dualscope-qwen2p5-7b-first-slice-response-generation` -> `dualscope-qwen2p5-7b-response-generation-repair`

Historical TriScope / route_c artifacts are not used.

## Deliverables

- Runtime preflight in the Qwen2.5-7B response generator.
- CLI options for selected-GPU memory threshold and explicit CPU fallback.
- Updated documentation with `CUDA_DEVICE_ORDER=PCI_BUS_ID` and the new memory guard.
- Validation artifacts showing the repair path compiles and writes non-fabricated blockers when local ignored dependencies are unavailable.

## Progress

- [x] M1: Read repository guidance, master plan, queue, and prior response-generation plan.
- [x] M2: Identify partial-validation cause: unsafe model-load attempt on insufficient GPU memory.
- [x] M3: Add selected-GPU memory preflight and CPU fallback guard.
- [x] M4: Update docs and run local validation.
- [x] M5: Complete PR workflow without auto merge, force push, branch deletion, or remote rewrite.
- [x] M6: Execute the dedicated repair wrapper in the isolated worktree and write a concrete missing-input blocker package.

## Surprises & Discoveries

- This isolated repair worktree does not include ignored first-slice data, target-response outputs, or `models/qwen2p5-7b-instruct`; those are intentionally outside git.
- The queue names `dualscope-qwen2p5-7b-response-generation-repair` as the partial-verdict next step, but no dedicated queue entry exists yet. This repair therefore scopes itself to the configured next-step behavior described by the existing response-generation task.
- Follow-up validation found the tracked repair verdict registry pointed at the wrong main-model-axis artifact. The registry has been corrected, and `DUALSCOPE_TASK_QUEUE.md` now includes a dedicated repair task entry so the orchestrator can recognize the repair as validated.
- Current isolated worktree validation found `/mnt/sda3/lh/models/qwen2p5-7b-instruct` exists and a repo-local `models/qwen2p5-7b-instruct` binding can point to it, but the required ignored first-slice labeled pairs, target-response plan rows, and resource-materialization output directory are absent from this worktree.
- Because required input artifacts are absent, the repair did not attempt model loading or generation. It wrote `Partially validated` with `blocker_type=missing_input` and next task `dualscope-qwen2p5-7b-response-input-artifact-repair`.

## Decision Log

- Use a conservative default selected-GPU free-memory threshold of 18432 MiB for fp16 single-device Qwen2.5-7B and 8192 MiB for requested 4-bit mode.
- Keep CPU generation disabled unless `--allow-cpu-generation` is explicitly passed.
- Treat unknown selected-GPU free memory as a blocker rather than risking another hanging model load.
- Continue to write row-level blocked artifacts with `model_response_fabricated=false` when source or runtime blockers exist.
- Preserve the repair wrapper's selected-GPU memory guard by passing `--min-free-gpu-memory-mib` through to the underlying first-slice generator instead of bypassing the threshold.
- Treat a concrete missing-input repair package as `Partially validated` so the queue can route to input-artifact repair rather than looping on an ambiguous response-generation failure.

## Plan of Work

Patch the response-generation module so dependency checks and CUDA/memory checks run before any tokenizer/model load. The CLI exposes the threshold but defaults to the repair-safe values. Documentation is updated to show the recommended GPU ordering prefix and the new guard flag. Validation compiles the changed files and runs a prepare/blocker path in this worktree.

## Concrete Steps

1. Add selected GPU memory parsing from `nvidia-smi`.
2. Select the visible CUDA device with the most free memory and record the physical index.
3. Block generation before model load if CUDA is unavailable, CPU fallback is not allowed, memory is unknown, or free memory is below threshold.
4. Add CLI flags for `--min-free-gpu-memory-mib` and `--allow-cpu-generation`.
5. Update documentation and prior plan notes.
6. Run `py_compile`, `--help`, `git diff --check`, and a local artifact-writing command.

## Validation Notes

Current repair validation in this isolated worktree:

- `python3 -m py_compile src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py` passed.
- `python3 scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py --help` passed and shows `--min-free-gpu-memory-mib` plus `--allow-cpu-generation`.
- `python3 scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py --output-dir outputs/dualscope_qwen2p5_7b_first_slice_response_generation/repair_validation --prepare-only --prepare-only-reason isolated_repair_validation --max-rows 2 --min-free-gpu-memory-mib 18432` wrote blocker artifacts and exited `2` with `Not validated` because ignored local data/model dependencies are absent in this isolated checkout. The artifacts recorded no fabricated responses, no metrics, no training, no full matrix, no benchmark-truth change, no gate change, and no route_c continuation.
- `git diff --check` passed.

Current dedicated repair validation:

- `python3 -m py_compile src/eval/dualscope_qwen2p5_7b_response_generation_repair.py src/eval/post_dualscope_qwen2p5_7b_response_generation_repair_analysis.py scripts/build_dualscope_qwen2p5_7b_response_generation_repair.py scripts/build_post_dualscope_qwen2p5_7b_response_generation_repair_analysis.py src/eval/dualscope_qwen2p5_7b_first_slice_response_generation.py scripts/build_dualscope_qwen2p5_7b_first_slice_response_generation.py` passed.
- `python3 scripts/build_dualscope_qwen2p5_7b_response_generation_repair.py --help` passed and shows `--resource-materialization-dir` plus `--min-free-gpu-memory-mib`.
- `HF_HOME=/mnt/sda3/lh/huggingface TRANSFORMERS_CACHE=/mnt/sda3/lh/huggingface/transformers HF_HUB_CACHE=/mnt/sda3/lh/huggingface/hub TMPDIR=/mnt/sda3/lh/tmp CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3 python3 scripts/build_dualscope_qwen2p5_7b_response_generation_repair.py --model-dir models/qwen2p5-7b-instruct --max-examples 4 --batch-size 1 --max-new-tokens 64 --min-free-gpu-memory-mib 18432 --allow-without-logprobs` wrote repair and first-slice blocker artifacts with final verdict `Partially validated`.
- `python3 scripts/build_post_dualscope_qwen2p5_7b_response_generation_repair_analysis.py` wrote analysis artifacts and updated `.reports/dualscope_task_verdicts/dualscope-qwen2p5-7b-response-generation-repair.json`.
- Current blockers are `missing_resource_materialization_dir`, `missing_labeled_pairs`, `missing_target_response_plan_rows`, and `target_response_plan_not_validated`; generated response rows are zero and no responses/logprobs/metrics were fabricated.
- Current rerun in this isolated worktree recreated the ignored repo-local model binding to `/mnt/sda3/lh/models/qwen2p5-7b-instruct`, then reran the same bounded repair command. The model binding passed source audit, but the ignored labeled-pairs JSONL, target-response plan rows/verdict, and resource-materialization directory remain absent, so the repair verdict remains `Partially validated` with `blocker_type=missing_input` and next task `dualscope-qwen2p5-7b-response-input-artifact-repair`.

## Validation and Acceptance

The repair is acceptable when:

- Python files compile.
- CLI help includes the new runtime guard options.
- A local run in this isolated worktree writes response-generation artifacts without fabricated responses.
- The generator no longer attempts to load Qwen2.5-7B when selected-GPU memory is below the configured threshold.

## Idempotence and Recovery

The output directory is safe to regenerate. In a fully materialized worktree, rerun the original response-generation command with `CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=2,3`. If the selected GPU has enough free memory, generation can proceed; otherwise the same command exits with explicit blockers and no fabricated rows.
