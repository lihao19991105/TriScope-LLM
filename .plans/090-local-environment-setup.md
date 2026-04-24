# 090 Local Environment Setup

## Purpose / Big Picture

TriScope-LLM 已经具备 bootstrap、poison data pipeline 和 training dry-run 的代码能力，但当前本机环境还不能稳定支撑这些能力的项目内复现。这个任务的目标是在**不污染系统环境、不改系统 Python 默认版本**的前提下，尽可能把项目的本地开发环境补齐到“当前阶段可推进”的状态。

完成后，仓库应至少具备一个项目内隔离环境、最小必需依赖、结构化安装日志和重新验证结果，并明确记录哪些前置条件已经满足、哪些仍然阻塞后续 LoRA 训练。

## Scope

### In Scope

- 检查本机可用 Python 解释器与已有环境
- 优先在仓库根目录创建 `.venv`
- 仅在虚拟环境中升级 `pip` / `setuptools` / `wheel`
- 安装当前阶段真正需要的依赖
- 重跑 `check_env.py` 和关键 CLI
- 生成结构化安装日志与验证报告

### Out of Scope

- 修改系统全局 Python 默认版本
- 修改 `.bashrc` / `.zshrc` 等 shell 配置
- 系统级包管理器安装
- 无明确必要的大量额外依赖
- 真实 LoRA 训练主循环

## Repository Context

本任务主要涉及：

- `requirements.txt`
- `README.md`
- `.venv/`
- `scripts/check_env.py`
- `scripts/build_poison_dataset.py`
- `scripts/validate_training_dataset.py`
- `outputs/env_setup/`
- `.plans/090-local-environment-setup.md`

## Deliverables

- 环境修复 ExecPlan
- 项目内 `.venv`（若可创建）
- 安装日志
- 更新后的环境报告
- 关键 CLI 验证结果
- 如有必要的 README 环境初始化说明补充

## Progress

- [x] 梳理当前环境现状与最小阻塞项
- [x] 创建并验证 `.venv`
- [x] 安装当前阶段必需依赖并记录日志
- [x] 重跑环境检查与关键 CLI
- [x] 导出最终环境摘要并更新计划记录

## Surprises & Discoveries

- 用户后来提供了可用的 Python 3.10 解释器：`/home/lh/miniconda3/envs/triscope-py310/bin/python`，从而可以废弃旧的 `python3.8 + system-site-packages` 过渡方案。
- 基于该解释器重建出的 `.venv` 是干净隔离环境，`include-system-site-packages = false`。
- 国际源下载 GPU 版 `torch` 时反复出现超时或损坏包问题，但切换到清华 TUNA PyPI 镜像后，`torch 2.4.1+cu121` 与整套 CUDA 依赖链一次安装成功。
- 默认工作沙箱里没有 `/dev/nvidia*`，因此沙箱内的 `torch.cuda.is_available()` 为 `False`；同一 `.venv` 在沙箱外验证时可正常看到 4 张 GPU，其中包括 2 张 RTX 3090。
- 在新的 `.venv` 中，`check_env.py`、`build_poison_dataset.py`、`validate_training_dataset.py` 和新的 `run_lora_finetune.py --dry-run` 都已跑通。

## Decision Log

- 决策：优先创建项目内 `.venv`，避免系统级安装。
  - 原因：符合低风险、低打扰、项目内隔离的环境处理原则。
  - 影响范围：依赖安装方式、日志路径和后续 CLI 运行命令。

- 决策：用户提供 `triscope-py310` 解释器后，立即重建一个干净 `.venv`，不再沿用旧的 `system-site-packages` 方案。
  - 原因：这使环境终于符合 `AGENTS.md` 中的 Python 3.10+ 要求，也更符合“项目内隔离、可回滚”的目标。
  - 影响范围：`.venv`、环境报告、依赖版本选择和后续训练入口。

- 决策：GPU 版 `torch` 与剩余依赖改用清华 TUNA PyPI 镜像安装。
  - 原因：默认国际源对 800MB 级别的 `torch` wheel 不稳定，而 TUNA 镜像在当前网络条件下显著更可靠。
  - 影响范围：`outputs/env_setup/install.log`、`torch` 安装成功率和当前 `.venv` 的 CUDA 能力。

- 决策：环境验收以“沙箱外 `check_env.py` 的真实 GPU 状态”为准，同时保留一个明确说明：默认工作沙箱不暴露 `/dev/nvidia*`。
  - 原因：仓库确实已经具备 GPU 训练前置条件，但日常脚本执行环境与实际硬件可见性存在边界差异。
  - 影响范围：`final_environment_report.json`、`verification_summary.json` 和后续训练命令的运行方式。

## Plan of Work

先确认现有解释器和虚拟环境能力，再在项目内创建 `.venv` 并只在其中升级打包工具；随后按“最小可推进”原则安装当前阶段缺失依赖，并把所有关键步骤记录到 `outputs/env_setup/`；最后重跑环境检查和关键 CLI，形成可审计的环境修复结果。

如果 3.10+ 解释器缺失导致某些包或版本无法完全满足项目要求，本计划不会通过系统级改动强行解决，而是明确把它记为剩余阻塞点。

## Concrete Steps

1. 检查 Python 解释器、`venv` 能力、现有环境报告和 README 要求。
2. 创建 `.venv` 并验证其 `python` / `pip` 可用。
3. 在 `.venv` 内升级 `pip` / `setuptools` / `wheel`。
4. 安装当前阶段缺失的必需依赖，并记录到 `outputs/env_setup/install.log`。
5. 使用 `.venv` 中的解释器重跑 `check_env.py` 和关键 CLI。
6. 生成 `final_environment_report.json` 和 `verification_summary.json`。
7. 更新计划中的进度、决策和剩余风险。

## Validation and Acceptance

- `.venv` 可被成功创建并调用
- 安装日志成功写入 `outputs/env_setup/install.log`
- 关键 CLI 至少能在 `.venv` 中运行：
  - `scripts/check_env.py`
  - `scripts/build_poison_dataset.py --help`
  - `scripts/validate_training_dataset.py --help`
- 生成结构化环境报告与验证摘要
- 若无法满足 Python 3.10+，该阻塞点被明确记录，而不是被静默忽略

## Idempotence and Recovery

- `.venv` 若已存在，应优先复用并验证，不盲目重建。
- 安装日志和验证报告可重复覆盖更新。
- 若某个包安装失败，不应放弃整个环境修复；应继续完成其他可做步骤并记录失败点。

## Outputs and Artifacts

- `.venv/`
- `outputs/env_setup/install.log`
- `outputs/env_setup/final_environment_report.json`
- `outputs/env_setup/verification_summary.json`

## Remaining Risks

- 默认工作沙箱不暴露 GPU 设备，因此真正的 GPU 训练与 GPU 校验命令需要在沙箱外运行。
- 当前 `run_lora_finetune.py --dry-run` 是离线友好的，但真实训练仍依赖本地已有或可下载的 HuggingFace 模型权重。
- 安装日志仍保留了早期失败重试记录；它们不影响当前环境可用性，但阅读日志时需要注意旧尝试和最终成功尝试并存。

## Next Suggested Plan

环境任务完成后，建议回到 `.plans/003-lora-finetuning.md` 的 Milestone 2。
