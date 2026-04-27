# DualScope AdvBench/JBB External GPU Model Dir Binding Fix

## Purpose / Big Picture

This plan fixes the bounded AdvBench/JBB external GPU response-generation blocker caused by the runner not reliably binding the real Qwen2.5-7B-Instruct model directory. The goal is to make generation use `/mnt/sda3/lh/models/qwen2p5-7b-instruct` explicitly and to produce either real model responses or an honest runtime blocker.

## Scope

### In Scope

- Add shell runner argument parsing for `--target`, `--model-dir`, `--max-examples`, `--batch-size`, and `--max-new-tokens`.
- Force the shell runner to create `models/qwen2p5-7b-instruct -> /mnt/sda3/lh/models/qwen2p5-7b-instruct` before generation.
- Keep the Python CLI default model directory set to `/mnt/sda3/lh/models/qwen2p5-7b-instruct`.
- Reject worktree-relative model paths in the Python generation logic.
- Preserve blocked rows as blocked rows and expose `real_response_row_count` separately.
- Rerun bounded AdvBench/JBB generation or record the real blocker.

### Out of Scope

- Metric recomputation unless real response rows are generated.
- Full AdvBench/JBB matrix execution.
- Alpaca, semantic trigger, behavior-shift, route_c, PR #14, gate semantics, benchmark truth, training, or 199+ planning.
- Fabricating responses, logprobs, AUROC/F1/ASR, clean utility, or validation status.

## Repository Context

- Existing bounded generation logic lives in `src/eval/dualscope_benchmark_small_slice_external_gpu.py`.
- The CLI entrypoint is `scripts/build_dualscope_qwen2p5_7b_benchmark_small_slice_external_gpu_generation.py`.
- The shell runner is `scripts/run_dualscope_qwen2p5_7b_advbench_jbb_external_gpu_generation.sh`.
- Existing response artifacts live under `outputs/dualscope_{advbench,jbb}_small_slice_response_generation/default`.
- External runner blocker aliases are written under `outputs/dualscope_{advbench,jbb}_small_slice_external_gpu_generation/default`.

## Deliverables

- Fixed shell runner with explicit absolute model-dir binding.
- Python CLI help and validation for the absolute model path.
- Generation summaries and registries that include `real_response_row_count`.
- External GPU blocker aliases for the paths used by the operator checklist.
- Documentation for the bounded runner.
- Updated AdvBench/JBB response-generation registries after rerun.

## Progress

- [x] Read project rules and current AdvBench/JBB execution context.
- [x] Identify model-dir binding gaps in the shell runner.
- [x] Patch shell runner, CLI, and generation logic.
- [x] Add runner documentation.
- [x] Run validation commands.
- [x] Rerun bounded AdvBench/JBB response generation.
- [x] Update registry status based on real responses or runtime blocker.
- [ ] Open PR and request review.

## Surprises & Discoveries

- The primary worktree has a read-only `.git/FETCH_HEAD`, so PR work must use a clean `/tmp` clone.
- In the current Codex sandbox, `nvidia-smi` cannot communicate with the NVIDIA driver and `/mnt/sda3/lh/models/qwen2p5-7b-instruct` is not visible. A bounded rerun from this sandbox may therefore still produce a real `missing_model_dir` blocker.
- The repo-local `.codex/skills/dualscope-high-intensity/SKILL.md` path requested by the operator is unavailable because `.codex` is a zero-byte file in this worktree.
- 2026-04-27 rerun: AdvBench and JBB each wrote 16 blocked artifact rows, `real_response_row_count = 0`, and `blocker_type = missing_model_dir`. Metrics were not run.

## Decision Log

- Keep the external model directory as the only default model path for AdvBench/JBB generation.
- Reject relative `--model-dir` values to prevent accidental fallback to a worktree-local model path.
- Continue writing response JSONL rows for blocked cases, but keep `real_response_row_count` at zero unless rows have `response_generation_status = generated` and real `model_response` text.
- Do not run metrics until response artifacts prove `real_response_row_count > 0`.

## Plan of Work

Patch the runner and CLI first, then run syntax and compile checks. After that, run bounded generation with the operator-provided command. If real responses are produced, route to the metric tasks. If generation fails, record the concrete blocker and do not compute metrics.

## Concrete Steps

1. Patch the shell runner to parse and pass `--model-dir /mnt/sda3/lh/models/qwen2p5-7b-instruct`.
2. Add symlink creation and model directory verification before generation.
3. Patch the Python generation logic to reject relative model dirs and report `missing_model_dir` distinctly.
4. Add external GPU blocker alias artifacts.
5. Run compile, shell syntax, help, and diff checks.
6. Run bounded AdvBench/JBB generation.
7. Inspect response JSONL counts and blocker artifacts.
8. Commit from a clean branch and open a minimal PR.

## Validation and Acceptance

Acceptance requires either:

- AdvBench and/or JBB `real_response_row_count > 0`, with registries routing successful datasets to metric computation; or
- A true blocker that is not fabricated and is recorded in blocker artifacts.

If the only blocker remains `missing_model_dir`, metric recomputation must not proceed.

## Idempotence and Recovery

The shell runner is safe to rerun. It recreates the symlink with `ln -sfnT`, rewrites bounded output artifacts, and does not modify benchmark truth or gate semantics.

## Outputs and Artifacts

- `outputs/dualscope_advbench_small_slice_response_generation/default/advbench_small_slice_responses.jsonl`
- `outputs/dualscope_jbb_small_slice_response_generation/default/jbb_small_slice_responses.jsonl`
- `outputs/dualscope_advbench_small_slice_external_gpu_generation/default/advbench_external_gpu_generation_blockers.json`
- `outputs/dualscope_jbb_small_slice_external_gpu_generation/default/jbb_external_gpu_generation_blockers.json`
- `.reports/dualscope_task_verdicts/dualscope-advbench-small-slice-response-generation.json`
- `.reports/dualscope_task_verdicts/dualscope-jbb-small-slice-response-generation.json`

## Remaining Risks

- The current sandbox may not expose `/mnt/sda3/lh` or CUDA even after code repair.
- True generation may still fail with CUDA, OOM, dependency, or model load blockers on the external runner.

## Next Suggested Plan

If real AdvBench/JBB responses are generated, proceed to the corresponding small-slice metric computation task. Otherwise close the runtime blocker before any metrics.
