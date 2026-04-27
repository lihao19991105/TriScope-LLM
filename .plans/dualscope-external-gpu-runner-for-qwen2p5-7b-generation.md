# DualScope external GPU runner for Qwen2.5-7B generation

## Purpose / Big Picture

The Codex `codex exec` sandbox cannot see CUDA in isolated worktrees, while the
host shell and escalated Python can see the RTX 3090 GPUs.  This plan moves the
bounded Qwen2.5-7B Alpaca main-slice generation step to an external GPU-visible
runner while keeping Codex responsible for script generation, artifact checks,
registry updates, PR workflow, and downstream routing.

## Scope

### In Scope

- Add a shell `nohup` runner for external GPU-visible execution.
- Add a Python CLI that runs bounded Qwen2.5-7B generation and writes external
  artifacts plus canonical Alpaca main-slice response artifacts.
- Add post-analysis for verdict and next-step recommendation.
- Add queue routing from the recorded worktree GPU blocker closure to the
  external runner task.

### Out of Scope

- Full Alpaca generation.
- Full matrix execution.
- Training, LoRA, or QLoRA.
- Fabricated responses, logprobs, metrics, reviews, or CI.
- Benchmark truth or gate changes.

## Validation

- `python3 -m py_compile` on new Python files.
- CLI `--help` for build and post-analysis scripts.
- Readiness-only `--dry-run` with the external runner CLI.
- Real generation must be launched from the host shell/nohup runner, not
  `codex exec`.

## Current Progress

- Added runner CLI, shell wrapper, post-analysis, docs, and queue entry.
- The first real generation run remains bounded to 8 source examples and
  records without-logprobs fallback.
