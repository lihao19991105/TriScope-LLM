# 013 Cross Pilot Reporting

## Purpose / Big Picture

012 已经把真实 pilot coverage 从单条 reasoning 扩展到了 reasoning + confidence。下一步需要把这两条真实 pilot 正式纳入统一 reporting / registry / comparison 层，让仓库能够清楚地区分：

- 哪些模块已经拥有真实 pilot
- 哪些模块仍然只有 smoke artifact
- 当前真实 pilot 的 coverage、限制和可复用状态

013 的目标不是做复杂 dashboard，而是先建立一个稳定、可交接、可机器消费的 cross-pilot reporting 层，为第三条真实 pilot 和后续真实 fusion/reporting 扩展打基础。

## Scope

### In Scope

- cross-pilot registry
- cross-pilot artifact registry
- pilot coverage summary
- reasoning-vs-confidence compact comparison
- real-pilot-vs-smoke compact summary
- cross-pilot acceptance / repeatability
- README 中的最小 cross-pilot reporting 用法

### Out of Scope

- dashboard / plotting
- 多模型真实 pilot 排行
- 真实 fusion classifier 级 pilot reporting
- benchmark-scale real experiment reports

## Repository Context

本计划将衔接：

- `outputs/pilot_runs/*`
- `outputs/pilot_extension_runs/*`
- `outputs/pilot_analysis/*`
- `outputs/analysis_reports/smoke_report/*`
- `src/eval/`
- `scripts/`
- `README.md`

## Deliverables

- `.plans/013-cross-pilot-reporting.md`
- `src/eval/cross_pilot_reporting.py`
- `scripts/build_cross_pilot_report.py`
- `src/eval/cross_pilot_report_checks.py`
- `scripts/validate_cross_pilot_report.py`
- `cross_pilot_registry.json`
- `cross_pilot_artifact_registry.json`
- `cross_pilot_summary.json`
- `pilot_comparison.csv`
- `pilot_coverage_summary.json`
- `real_pilot_vs_smoke_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: cross-pilot registry / comparison / coverage summary
- [x] Milestone 2: acceptance / repeatability / README / 计划收口

## Surprises & Discoveries

- 当前两条真实 pilot 虽然共享同一个 local CSQA-style slice 和同一个轻量模型，但它们已经足够支撑“跨 pilot registry 与 compact comparison”的最小 reporting 层。
- 当前最有价值的 cross-pilot 事实不是“谁更好”，而是“哪些模块已有真实 pilot、哪些仍然只有 smoke”。
- 013 完成时，cross-pilot reporting 仍然刻意把 illumination 记为 coverage gap；这为下一步第三条真实 pilot 的落地提供了清晰的 before-state。

## Decision Log

- 决策：013 只做 reasoning + confidence 两条真实 pilot 的统一 reporting，不等待第三条 illumination pilot 先补齐。
  - 原因：当前仓库已经具备两条真实 pilot，先把 cross-pilot 报告层做实，能够让第三条 pilot 一落地就有明确 registry 容器可接入。
  - 影响范围：`src/eval/cross_pilot_reporting.py`、`scripts/build_cross_pilot_report.py`、cross-pilot summary schema。

- 决策：comparison 以 coverage / readiness / artifact stability 为主，而不是以模型效果优劣为主。
  - 原因：当前两条真实 pilot 仍然使用相同 local slice 和轻量模型，数值结果不能被包装成研究结论。
  - 影响范围：`pilot_comparison.csv`、`pilot_coverage_summary.json`、README 解释边界。

- 决策：013/M2 为 cross-pilot reporting 增加独立 validator 和 repeatability rerun。
  - 原因：cross-pilot reporting 将成为后续真实 pilot 扩张的统一汇总层，需要和 smoke reporting / pilot analysis 一样具备独立验收能力。
  - 影响范围：`src/eval/cross_pilot_report_checks.py`、`scripts/validate_cross_pilot_report.py`、`outputs/cross_pilot_reports/repeatability_*/*`。

## Plan of Work

先读取当前 reasoning pilot、confidence pilot、pilot analysis 和 smoke reporting 的关键 summary，然后把这些信息整理成统一的 cross-pilot registry、artifact registry 和 compact comparison。M1 完成后，再通过 validator 和同配置 rerun 做 acceptance / repeatability，并在 README 中写清楚这层 reporting 的输入、输出和解释边界。

## Concrete Steps

1. 创建 `.plans/013-cross-pilot-reporting.md`。
2. 实现 `src/eval/cross_pilot_reporting.py`。
3. 实现 `scripts/build_cross_pilot_report.py`。
4. 读取 reasoning pilot / confidence pilot / smoke report / pilot analysis 关键 artifact。
5. 生成 cross-pilot registry、artifact registry、coverage summary、comparison CSV 和 real-pilot-vs-smoke summary。
6. 实现 `src/eval/cross_pilot_report_checks.py`。
7. 实现 `scripts/validate_cross_pilot_report.py`。
8. 重跑一次 cross-pilot report 到独立目录并做 repeatability 检查。
9. 更新 README 与计划状态。

## Validation and Acceptance

- `build_cross_pilot_report.py --help` 可正常显示
- `validate_cross_pilot_report.py --help` 可正常显示
- 成功生成：
  - `cross_pilot_registry.json`
  - `cross_pilot_artifact_registry.json`
  - `cross_pilot_summary.json`
  - `pilot_comparison.csv`
  - `pilot_coverage_summary.json`
  - `real_pilot_vs_smoke_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`
- README 已补 cross-pilot reporting 最小用法

## Idempotence and Recovery

- cross-pilot report 写入独立 `output_dir`
- 可重复运行
- 若上游 pilot artifact 缺失，应写出结构化 failure summary
- 若主 report 已存在，可直接在新目录 rerun 做 repeatability

## Outputs and Artifacts

- `outputs/cross_pilot_reports/*`
- `cross_pilot_registry.json`
- `cross_pilot_artifact_registry.json`
- `cross_pilot_summary.json`
- `pilot_comparison.csv`
- `pilot_coverage_summary.json`
- `real_pilot_vs_smoke_summary.json`

## Remaining Risks

- 当前 cross-pilot reporting 仍然只覆盖 reasoning + confidence 两条真实 pilot，illumination 仍然是 coverage gap。
- 当前 comparison 仍然受 local slice、小模型和 pilot-level 轻量执行深度限制。
- 当前 real-vs-smoke summary 主要反映 artifact readiness 和 coverage，不应被解读为 benchmark-level 结果对比。

## Validation Snapshot

- `outputs/cross_pilot_reports/default/cross_pilot_registry.json`
- `outputs/cross_pilot_reports/default/pilot_coverage_summary.json`
- `outputs/cross_pilot_reports/repeatability_default/artifact_acceptance.json`
- `outputs/cross_pilot_reports/repeatability_default/repeatability_summary.json`
- 当前 real pilot modules:
  - `reasoning`
  - `confidence`
- 当前 coverage gap:
  - `illumination`

## Next Suggested Plan

若 013 完成，下一步建议创建 `.plans/014-third-pilot-illumination.md`。
