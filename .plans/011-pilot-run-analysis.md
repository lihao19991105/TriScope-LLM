# 011 Pilot Run Analysis

## Purpose / Big Picture

010 已经把一条真实 pilot run 从 config-only 推进到了真实 execution artifact。下一步需要把这条 pilot run 正式接入 analysis / reporting 视角，让仓库能够清楚地区分“哪些结果仍然是 smoke”、“哪些结果已经来自真实 pilot”，并给后续更大范围的真实实验扩展提供 registry 和 compact comparison 入口。

011 的目标不是构建复杂 dashboard，而是先补一层最小 pilot analysis 基础设施：把 pilot run 注册起来、生成 pilot_vs_smoke 的紧凑摘要，并输出一个 machine-readable 的 pilot analysis summary。

## Scope

### In Scope

- pilot run registry
- pilot vs smoke compact comparison
- machine-readable pilot analysis summary
- 复用现有 reasoning / smoke / reporting artifact

### Out of Scope

- 复杂 plotting
- 多 pilot 路线比较
- 全模块真实实验报告
- 完整论文图表系统

## Repository Context

本计划将衔接：

- `outputs/pilot_runs/*`
- `outputs/reasoning_runs/smoke_local_run/*`
- `outputs/analysis_reports/smoke_report/*`
- `src/eval/`
- `scripts/`

## Deliverables

- 011 pilot-run-analysis ExecPlan
- `scripts/build_pilot_analysis.py`
- `src/eval/pilot_analysis.py`
- `pilot_run_registry.json`
- `pilot_vs_smoke_summary.json`
- `pilot_analysis_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: pilot run registry、pilot_vs_smoke summary、pilot analysis summary
- [x] Milestone 2: README / validation / 计划收口

## Surprises & Discoveries

- 当前最自然的第一条真实 pilot 只覆盖 reasoning 模块，因此 011 的比较对象也应先聚焦 reasoning，而不是勉强扩到全模块。

## Decision Log

- 决策：011/M1 先围绕 reasoning pilot vs reasoning smoke 做比较，而不是试图和全 TriScope fusion 报告做一一对应。
  - 原因：当前真实 pilot 只 materialize 了 reasoning 路线，直接拿它和全模块 smoke fusion 做强对齐会引入误导。
  - 影响范围：pilot registry、comparison schema、summary 解释口径。

- 决策：011/M2 增加独立的 pilot-analysis validator，并对 compact comparison 做 repeatability 检查。
  - 原因：pilot analysis 已经是后续真实实验扩展的桥接层，需要像 reporting 和 pilot execution 一样具备独立验收能力。
  - 影响范围：`src/eval/pilot_analysis_checks.py`、`scripts/validate_pilot_analysis.py`、`outputs/pilot_analysis/repeatability_pilot_csqa_reasoning_local/*`。

## Plan of Work

先从 010 的 pilot run summary 和 005 的 reasoning smoke artifact 提取最小共通指标，然后把它们整理成 pilot run registry 与 pilot_vs_smoke summary。这样在不扩大实验范围的前提下，仓库会第一次具备“真实 pilot 已注册到 analysis 层”的结构化产物。

## Concrete Steps

1. 创建 `.plans/011-pilot-run-analysis.md`。
2. 实现 `src/eval/pilot_analysis.py`。
3. 实现 `scripts/build_pilot_analysis.py`。
4. 读取 pilot run summary、pilot feature summary、reasoning smoke summary、smoke report summary。
5. 生成 pilot registry 和 compact comparison artifacts。
6. 如有余力，再补 M2。

## Validation and Acceptance

- `build_pilot_analysis.py --help` 可正常显示
- `validate_pilot_analysis.py --help` 可正常显示
- 成功生成：
  - `pilot_run_registry.json`
  - `pilot_vs_smoke_summary.json`
  - `pilot_analysis_summary.json`
- 关键字段齐全且非空
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- pilot analysis 输出写入独立 `output_dir`
- 允许重复运行
- 若上游 artifact 缺失，应写出结构化 failure summary

## Outputs and Artifacts

- `outputs/pilot_analysis/*`
- `pilot_run_registry.json`
- `pilot_vs_smoke_summary.json`
- `pilot_analysis_summary.json`

## Remaining Risks

- 当前 pilot analysis 只覆盖 reasoning 单模块，不代表全系统真实实验分析已经建立。
- 当前只有一条真实 pilot，因此 pilot registry 仍然无法体现跨模块真实 coverage。
- 当前 `pilot_vs_smoke` 仍然受 local slice、distilgpt2 轻量模型和单模块对照的限制。

## Validation Snapshot

- `outputs/pilot_analysis/pilot_csqa_reasoning_local/pilot_run_registry.json`
- `outputs/pilot_analysis/pilot_csqa_reasoning_local/pilot_vs_smoke_summary.json`
- `outputs/pilot_analysis/pilot_csqa_reasoning_local/pilot_analysis_summary.json`
- `outputs/pilot_analysis/repeatability_pilot_csqa_reasoning_local/artifact_acceptance.json`
  - acceptance status: `PASS`
- `outputs/pilot_analysis/repeatability_pilot_csqa_reasoning_local/repeatability_summary.json`
  - repeatability status: `PASS`
- 当前 comparison scope:
  - `reasoning_pilot_vs_reasoning_smoke`

## Next Suggested Plan

若 011 完成，下一步建议创建 `.plans/012-expand-pilot-coverage.md`。
