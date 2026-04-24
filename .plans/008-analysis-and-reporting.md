# 008 Analysis And Reporting

## Purpose / Big Picture

TriScope-LLM 目前已经具备 illumination、reasoning、confidence 与 fusion 的最小可运行链路，但这些结果仍分散在多个 run 目录中。下一步需要补上统一的 analysis / reporting 层，把 smoke 阶段的关键 artifact 汇总成可机器消费、可直接服务后续论文写作与评估迭代的 compact report。

008 的目标不是搭建复杂 dashboard，也不是现在就做图表系统，而是先建立统一的 run inventory、artifact registry、smoke summary、baseline comparison 和 error-analysis-ready artifact。这样后续无论做更完整 eval、误报分析还是论文表格导出，都有稳定的数据入口。

## Scope

### In Scope

- 统一读取 004/005/006/007 的关键 artifact
- 构建 run registry 与 artifact registry
- 输出 smoke-level compact report
- 输出 baseline comparison
- 输出 modality coverage / missingness summary
- 输出 error-analysis-ready merged artifact

### Out of Scope

- plotting / dashboard
- 完整论文图表系统
- 大规模实验报告
- 复杂统计检验
- 新模型训练或新 probe 扩展

## Repository Context

本计划将衔接：

- `outputs/illumination_runs/*`
- `outputs/reasoning_runs/*`
- `outputs/confidence_runs/*`
- `outputs/fusion_datasets/*`
- `outputs/fusion_runs/*`
- `src/eval/`
- `scripts/`
- `.plans/004-007`

同时会直接消费：

- module `feature_summary.json`
- fusion `alignment_summary.json`
- fusion `fusion_summary.json`
- rule / logistic prediction artifacts
- repeatability / acceptance artifacts

## Deliverables

- 008 analysis-and-reporting ExecPlan
- `src/eval/smoke_reporting.py`
- `scripts/build_smoke_report.py`
- `run_registry.json`
- `artifact_registry.json`
- `smoke_report_summary.json`
- `baseline_comparison.csv`
- `modality_coverage_summary.json`
- `error_analysis_dataset.jsonl`
- `error_analysis_dataset.csv`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: run registry、artifact registry、smoke summary、baseline comparison
- [x] Milestone 2: modality coverage / missingness summary、error-analysis-ready merged artifact
- [x] Milestone 3: README / artifact acceptance / report repeatability

## Surprises & Discoveries

- 现有 smoke artifact 已经足够支撑统一 reporting，不需要新增外部数据。
- fusion baseline 的监督标签可以通过 `sample_id -> poison dataset is_poisoned` 恢复，因此 error-analysis-ready artifact 可以直接附带 ground-truth label。
- 当前 fusion dataset 的 outer-join 结构天然适合做 modality coverage 和 missingness summary。
- 当前 smoke report 已经能一次性注册 6 个核心 runs 和 9 个关键 artifact，说明 004-007 的最小闭环已经足够被统一汇总。
- 当前 error-analysis-ready merged artifact 显示 4 个样本上 rule/logistic 预测没有分歧；这更说明当前 smoke 主要是在验证链路，而不是制造研究结论。

## Decision Log

- 决策：M1 先做 registry 和 compact summary，不提前做 plotting。
  - 原因：当前更需要稳定、可机器消费的报告输入层，而不是视觉层。
  - 影响范围：`run_registry.json`、`artifact_registry.json`、`smoke_report_summary.json`、`baseline_comparison.csv`。

- 决策：M2 直接围绕 fusion outer-join 结果构建 error-analysis-ready artifact。
  - 原因：当前 smoke 阶段最自然的样本对齐中心就是 fusion dataset；它已经显式保留了 modality presence。
  - 影响范围：`error_analysis_dataset.jsonl` / `.csv`、`modality_coverage_summary.json`。

- 决策：008 只汇总已存在 artifact，不重跑上游模块。
  - 原因：analysis/reporting 应该是上游结果的轻量读取层，而不是再次触发 probe / training 计算。
  - 影响范围：CLI 设计、运行成本和恢复方式。

- 决策：M1/M2 默认围绕 smoke artifact 固定路径工作。
  - 原因：当前阶段目标是先建立统一 reporting 套件，而不是设计一套过早泛化的实验管理系统。
  - 影响范围：`src/eval/smoke_reporting.py` 的输入发现逻辑、registry 和 summary 的覆盖范围。

- 决策：M2 的 error-analysis-ready artifact 以 fusion preprocessed dataset 为主索引，再附加 rule/logistic prediction 与各模态关键字段。
  - 原因：fusion preprocessed dataset 已经统一了 ground-truth label、sample_id 和 modality presence，是当前最自然的分析中心。
  - 影响范围：`error_analysis_dataset.jsonl` / `.csv` 的 schema、后续 false positive / false negative 分析的入口。

- 决策：M3 为 smoke reporting 层新增独立 artifact acceptance / repeatability CLI。
  - 原因：analysis/reporting 需要像 probe 和 fusion 一样具备明确的交接与回归验证入口，而不是依赖手工目检。
  - 影响范围：新增 `src/eval/smoke_report_checks.py` 与 `scripts/validate_smoke_report.py`，README 中的 reporting 用法补充。

- 决策：008 在 M3 后整体收口，不继续在本阶段扩 dashboard 或 plotting。
  - 原因：当前 analysis/reporting 已具备 registry、summary、coverage、error-analysis artifact、acceptance 与 repeatability，已经满足交接给“真实实验就绪”阶段的条件。
  - 影响范围：更复杂的可视化与大规模 reporting 留到后续计划，而不是继续膨胀 008。

## Plan of Work

先实现一个统一的 smoke reporting 模块，读取 illumination、reasoning、confidence 与 fusion 的关键 summary / prediction artifact，输出 run registry、artifact registry 和 compact smoke summary。M1 稳定之后，再在 M2 中增加 modality coverage / missingness summary 与 error-analysis-ready merged artifact，把当前 smoke 结果整理成可直接做误报分析和论文表格的中间层。

## Concrete Steps

1. 创建 `.plans/008-analysis-and-reporting.md` 并定义 milestone 边界。
2. 实现 `src/eval/smoke_reporting.py`：
   - 读取 module feature summary、fusion summary、prediction artifact
   - 构建 run registry 和 artifact registry
   - 导出 compact smoke report 与 baseline comparison
3. 实现 `scripts/build_smoke_report.py` CLI。
4. 用当前 smoke artifacts 生成一次 analysis/reporting 产物。
5. 在 M2 中补 modality coverage / missingness summary。
6. 在 M2 中基于 fusion preprocessed dataset + predictions 构建 error-analysis-ready merged artifact。
7. 实现 `src/eval/smoke_report_checks.py` 与 `scripts/validate_smoke_report.py`。
8. 用相同输入重跑一次 smoke report，并验证 repeatability。
9. 更新 README 的 analysis/reporting 用法。
10. 更新 Progress、Decision Log、Remaining Risks。

## Validation and Acceptance

- `build_smoke_report.py --help` 可正常显示
- 成功生成：
  - `run_registry.json`
  - `artifact_registry.json`
  - `smoke_report_summary.json`
  - `baseline_comparison.csv`
  - `modality_coverage_summary.json`
  - `error_analysis_dataset.jsonl`
- registry / summary 非空且字段齐全
- error-analysis-ready artifact 至少包含：
  - `sample_id`
  - `ground_truth_label`
  - `illumination_present`
  - `reasoning_present`
  - `confidence_present`
  - `rule_prediction_score`
  - `logistic_prediction_score`

## Idempotence and Recovery

- reporting CLI 支持重复运行到不同 `output_dir`
- 输出为 report-scoped artifact，不依赖隐式全局状态
- 若某个上游 artifact 缺失，应写出结构化 failure summary
- `run_registry.json` 与 `artifact_registry.json` 可作为后续报告与评估的恢复入口

## Outputs and Artifacts

- `outputs/analysis_reports/*`
- `run_registry.json`
- `artifact_registry.json`
- `smoke_report_summary.json`
- `baseline_comparison.csv`
- `modality_coverage_summary.json`
- `error_analysis_dataset.jsonl`
- `error_analysis_dataset.csv`

## Remaining Risks

- 当前 reporting 只覆盖 smoke artifact，不代表真实实验矩阵。
- 当前 baseline comparison 主要用于链路验证和 compact summary，不代表可发表结果。
- 当前 error-analysis dataset 仍受 outer-join 缺失模态限制，后续需要更多可对齐 probe 样本才能支撑更细分析。
- 当前 reporting 的 repeatability 只验证了固定 smoke artifact 输入条件下的稳定性，还没有覆盖更多 report profile。
- 当前 reporting 已可交接，但仍是 smoke-only summary layer，不是完整实验报告系统。

## Next Suggested Plan

若 008 完成，下一步建议创建 `.plans/009-expanded-eval-and-error-analysis.md`。
