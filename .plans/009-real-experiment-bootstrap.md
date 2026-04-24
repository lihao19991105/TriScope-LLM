# 009 Real Experiment Bootstrap

## Purpose / Big Picture

TriScope-LLM 目前已经具备 smoke 级别的 probe、feature、fusion 和 reporting 闭环。下一步需要把仓库从“只适合 smoke 验证”推进到“真实实验就绪”，也就是在不强行下载大模型或大数据集的前提下，把未来真实实验所需的数据集契约、模型矩阵、experiment matrix 和可验证的 readiness artifact 先搭起来。

009 的目标不是立即跑昂贵实验，而是建立一层最小但真实可用的 experiment bootstrap 基础设施，让后续真实训练、真实 probing 和真实 run matrix 能够沿着清晰配置与 registry 平滑展开。

## Scope

### In Scope

- 数据集配置契约与 dataset source registry
- 模型配置矩阵与 real-run profile 扩展
- experiment matrix skeleton
- real-experiment bootstrap CLI
- dataset / model / experiment readiness validation
- experiment-ready registry 与 summary artifact

### Out of Scope

- 大规模真实训练
- 大规模真实 probing
- 自动下载大模型或大数据集
- 复杂 experiment scheduler
- plotting / dashboard

## Repository Context

本计划将衔接：

- `configs/models.yaml`
- 新增 `configs/datasets.yaml`
- 新增 `configs/experiments.yaml`
- `scripts/`
- `src/eval/`
- `outputs/`
- 现有 smoke artifact，用于本地可用性参照

## Deliverables

- 009 real-experiment-bootstrap ExecPlan
- dataset source schema
- expanded model profile matrix
- experiment matrix skeleton
- `src/eval/experiment_bootstrap.py`
- `scripts/build_experiment_registry.py`
- dataset / model / experiment registry artifacts
- readiness / availability summary artifacts

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 数据集契约、模型矩阵、experiment matrix skeleton、基础 registry artifact
- [x] Milestone 2: real experiment bootstrap CLI、dataset/model validation、validated registry、readiness summary
- [x] Milestone 3: README、acceptance、repeatability、计划收口

## Surprises & Discoveries

- 现有 smoke 本地资源已经足够提供至少一个 `ready_local` 数据集 profile 和一个 `ready_local` 模型 profile。
- 真正的实验阻塞目前主要不是代码缺失，而是外部资源是否就位，因此 `readiness_status` 与 `availability_status` 成为这层的核心。

## Decision Log

- 决策：009 优先做“真实实验前置准备”，不直接做大训练或大下载。
  - 原因：当前更需要把 experiment contract 做清楚，而不是把资源消耗集中到未经整理的真实实验上。
  - 影响范围：datasets/models/experiments 配置设计、CLI 的职责边界、输出 artifact 的类型。

- 决策：dataset profile 明确区分 `local_path / remote / placeholder`，并单独记录 `readiness_status`。
  - 原因：当前仓库里本地资源和未来目标资源并存，如果不显式分层，后续 experiment matrix 会混淆“已可运行”和“仅完成配置”的状态。
  - 影响范围：`configs/datasets.yaml`、dataset availability summary、validated experiment registry。

- 决策：model profile 在保留现有 smoke 兼容性的同时，增加 tokenizer、local_path、requires_gpu、recommended_stage、readiness_status。
  - 原因：真实实验阶段需要的不仅是 `model_id`，还需要知道它是否本地就绪、是否需要 GPU、适合 smoke/pilot/full 哪一阶段。
  - 影响范围：`configs/models.yaml`、model registry、model availability summary。

- 决策：M3 增加独立的 experiment bootstrap validator，而不是把 acceptance / repeatability 交给人工检查。
  - 原因：真实实验前置准备层本身就是后续恢复入口，需要和 probe / fusion / reporting 一样具备独立验收能力。
  - 影响范围：`src/eval/experiment_bootstrap_checks.py`、`scripts/validate_experiment_bootstrap.py`、`outputs/experiment_bootstrap/repeatability_default/*`。

- 决策：009 以“配置契约与 readiness artifact 稳定”作为完成标准，而不是等待 placeholder 数据和模型全部就位。
  - 原因：当前真正的阻塞主要来自外部资源本身，而不是 bootstrap 层缺少清晰 contract；如果把 009 绑定到资源到位，计划将长期无法收口。
  - 影响范围：M3 收口标准、README 表述、下一阶段 010 的边界。

## Plan of Work

先补 datasets / models / experiments 三层配置契约，把“未来真实实验要怎么接数据、怎么选模型、怎么排 experiment matrix”固定下来。M1 完成后，在 M2 中实现一个统一的 bootstrap CLI，用来读取这些配置、验证本地路径和基本字段、输出 validated experiment registry 与 availability / readiness summary。这样即使当前外部数据和模型尚未就位，也能形成诚实、可交接、可恢复的 experiment bootstrap 层。

## Concrete Steps

1. 创建 `.plans/009-real-experiment-bootstrap.md` 并定义 milestone 边界。
2. 新增 `configs/datasets.yaml`。
3. 扩展 `configs/models.yaml` 的 real-run profile matrix。
4. 新增 `configs/experiments.yaml`。
5. 实现 `src/eval/experiment_bootstrap.py`：
   - 读取 datasets / models / experiments 配置
   - 校验必需字段
   - 检查本地路径可用性
   - 生成 dataset / model / experiment registry 与 summary
6. 实现 `scripts/build_experiment_registry.py` CLI。
7. 用当前本地资源跑一次 bootstrap registry 构建。
8. 更新 Progress、Decision Log、Remaining Risks。

## Validation and Acceptance

- `build_experiment_registry.py --help` 可正常显示
- `validate_experiment_bootstrap.py --help` 可正常显示
- 成功生成：
  - `dataset_registry.json`
  - `model_registry.json`
  - `experiment_matrix.json`
  - `experiment_matrix.csv`
  - `experiment_bootstrap_summary.json`
  - `validated_experiment_registry.json`
  - `dataset_availability_summary.json`
  - `model_availability_summary.json`
  - `experiment_readiness_summary.json`
- 对本地不存在的数据/模型不会崩溃，而是如实标记 availability / readiness
- 至少有一个 dataset profile 和一个 model profile 被标记为本地可用
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- bootstrap CLI 支持重复运行到不同 `output_dir`
- 输出为 registry-scoped artifact，不依赖隐式全局状态
- 若配置字段不完整，应写出结构化 failure summary
- validated registry 与 readiness summary 可作为后续真实实验调度的恢复入口

## Outputs and Artifacts

- `outputs/experiment_bootstrap/*`
- `dataset_registry.json`
- `model_registry.json`
- `experiment_matrix.json`
- `experiment_matrix.csv`
- `experiment_bootstrap_summary.json`
- `validated_experiment_registry.json`
- `dataset_availability_summary.json`
- `model_availability_summary.json`
- `experiment_readiness_summary.json`

## Remaining Risks

- 当前 experiment bootstrap 仍是资源准备层，不代表真实实验已经开始。
- 当前只有 `smoke_triscope_demo` 被标记为 `ready_local`；其余 experiment 仍被 dataset placeholder 阻塞。
- 当前不存在 `config_ready_remote` experiment，这意味着下一阶段至少要把一个 pilot dataset 从 placeholder 推进到真实可用来源。
- availability / readiness 校验目前仍聚焦配置层与路径层，不会自动验证远端数据格式或模型访问权限。

## Validation Snapshot

- `outputs/experiment_bootstrap/default/experiment_bootstrap_summary.json`
  - dataset profiles: `5`
  - model profiles: `7`
  - experiments: `4`
  - ready local experiments: `1`
  - blocked experiments: `3`
- `outputs/experiment_bootstrap/repeatability_default/artifact_acceptance.json`
  - acceptance status: `PASS`
- `outputs/experiment_bootstrap/repeatability_default/repeatability_summary.json`
  - repeatability status: `PASS`
  - all key metrics match: `true`

## Next Suggested Plan

若 009 完成，下一步建议创建 `.plans/010-real-run-pilot-execution.md`。
