# 017 Real Pilot Analysis And Next-Step Selection

## Purpose / Big Picture

016 之后，TriScope-LLM 已经拥有三条真实 pilot、一个 real-pilot fusion dataset，以及一条可运行的 rule baseline。但项目也暴露出了新的核心瓶颈：supervised baseline 被结构化跳过，因为当前 real-pilot fusion dataset 没有 ground-truth label。

017 的目标是对当前 real-pilot 层做一次 compact、machine-readable 的结构化分析，并明确下一步为什么应优先进入 first-labeled-pilot-bootstrap，而不是继续扩更多无标签 pilot。

## Scope

### In Scope

- 汇总 015 / 016 与三条真实 pilot 的关键 artifact
- real-pilot compact analysis
- real-pilot vs smoke compact summary
- real-pilot vs real-pilot comparison
- blocker summary
- next-step recommendation
- README 中的极简 analysis 入口
- acceptance / repeatability / 计划收口

### Out of Scope

- 新的第四条无标签 pilot
- 新模型下载
- 大规模真实实验
- 复杂 dashboard / plotting

## Repository Context

本计划将衔接：

- `outputs/real_pilot_fusion_readiness/*`
- `outputs/real_pilot_fusion_runs/*`
- `outputs/pilot_runs/*`
- `outputs/pilot_extension_runs/*`
- `outputs/pilot_illumination_runs/*`
- `outputs/analysis_reports/smoke_report/*`
- `src/eval/`
- `scripts/`

## Deliverables

- `.plans/017-real-pilot-analysis-and-next-step-selection.md`
- `src/eval/real_pilot_analysis.py`
- `scripts/build_real_pilot_analysis.py`
- `src/eval/real_pilot_analysis_checks.py`
- `scripts/validate_real_pilot_analysis.py`
- `real_pilot_analysis_summary.json`
- `real_pilot_vs_smoke_summary.json`
- `real_pilot_vs_pilot_comparison.csv`
- `real_pilot_blocker_summary.json`
- `next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: real-pilot compact analysis / blocker summary
- [x] Milestone 2: next-step recommendation / acceptance / README / 计划收口

## Surprises & Discoveries

- 当前最大的阻塞已经不再是“没有多条真实 pilot”，而是“没有标签支撑 supervised path”。
- 继续扩无标签 pilot 对当前瓶颈的边际收益已经明显小于引入第一条可审计的 labeled pilot。
- 015 与 016 的现有 artifact 已经足够支撑 017；不需要回改 015/016 的 schema 就能完成 blocker 定位与路线选择。
- 017 的 repeatability 在当前阶段是稳定的，因为它只依赖已经冻结的 summary / registry / baseline artifact。

## Decision Log

- 决策：017 明确把 `missing_ground_truth_labels` 作为当前第一阻塞，而不是继续强调 missingness 或 coverage。
  - 原因：015 已经确认 full intersection 存在，016 也已经证明 rule baseline 可运行，真正阻塞 logistic 的是标签缺失。
  - 影响范围：`real_pilot_blocker_summary.json`、`next_step_recommendation.json`。

- 决策：017 默认推荐路线 B，即 first-labeled-pilot-bootstrap。
  - 原因：这条路线能以最小成本解除 supervised path 的主阻塞，比继续新增无标签 pilot 更能推动项目向“真实实验可写”靠近。
  - 影响范围：README 的 next step、018 计划边界。

- 决策：017 的 recommendation 不额外引入新 dataset / model 候选，而是直接推荐复用现有 illumination contract 进入 labeled bootstrap。
  - 原因：当前目标是先让 supervised path 第一次存在，而不是同时改变资源边界。
  - 影响范围：`next_step_recommendation.json`、018 的 route selection。

## Plan of Work

先读取 015 的 readiness 与 016 的 baseline summary，再把三条真实 pilot 的核心信息统一成 compact analysis、real-vs-smoke summary、pilot-vs-pilot comparison 和 blocker summary。完成这些后，再输出 next-step recommendation，并说明为什么 first-labeled-pilot-bootstrap 在当前阶段是默认优先路线。

## Concrete Steps

1. 创建 `.plans/017-real-pilot-analysis-and-next-step-selection.md`。
2. 实现 `src/eval/real_pilot_analysis.py`。
3. 实现 `scripts/build_real_pilot_analysis.py`。
4. 读取 015 / 016 / 三条真实 pilot / smoke report 的关键 summary。
5. 生成 compact analysis、blocker summary 和 recommendation。
6. 实现 validator 与 repeatability。
7. 更新 README 与计划状态。

## Validation and Acceptance

- `build_real_pilot_analysis.py --help` 可正常显示
- `validate_real_pilot_analysis.py --help` 可正常显示
- 成功生成：
  - `real_pilot_analysis_summary.json`
  - `real_pilot_vs_smoke_summary.json`
  - `real_pilot_vs_pilot_comparison.csv`
  - `real_pilot_blocker_summary.json`
  - `next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- real-pilot analysis 输出写入独立 `output_dir`
- 可重复运行
- 若上游 summary 缺失，应写出结构化 failure summary

## Outputs and Artifacts

- `outputs/real_pilot_analysis/*`
- `real_pilot_analysis_summary.json`
- `real_pilot_vs_smoke_summary.json`
- `real_pilot_vs_pilot_comparison.csv`
- `real_pilot_blocker_summary.json`
- `next_step_recommendation.json`

## Remaining Risks

- 当前 analysis 仍然建立在 pilot-level 小切片与轻量模型上。
- 当前 comparison 更适合说明 readiness 与 blocker，不适合支持研究级性能结论。
- 即使 017 推荐 first-labeled-pilot-bootstrap，标签设计仍然必须诚实约束在 pilot-level controlled supervision。
- 017 只能证明“下一步应优先引入标签”，不能代替 018 的真实执行验证。

## Next Suggested Plan

若 017 完成，下一步建议创建 `.plans/018-first-labeled-pilot-bootstrap.md`。
