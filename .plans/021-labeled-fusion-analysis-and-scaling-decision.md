# 021 Labeled Fusion Analysis And Scaling Decision

## Purpose / Big Picture

020 已经让 supervised real-pilot fusion 第一次存在，但它仍然只是极小规模的 pilot-level controlled supervision。021 的目标是把这条路径的最小价值、主要局限和下一步扩展路线做成结构化分析，明确“现在最该扩什么、为什么”。

## Scope

### In Scope

- labeled fusion compact analysis
- blocker / scaling boundary summary
- route A vs route B comparison
- next-step recommendation
- acceptance / repeatability
- README 极简补充

### Out of Scope

- 新的 pilot 路线
- 更大模型 / 更大数据
- benchmark-level 监督体系
- 复杂监督实验矩阵

## Repository Context

本计划将衔接：

- `outputs/labeled_pilot_analysis/*`
- `outputs/labeled_real_pilot_fusion/*`
- `outputs/labeled_real_pilot_fusion_runs/*`
- `outputs/real_pilot_fusion_readiness/*`
- `outputs/real_pilot_fusion_runs/*`
- `outputs/pilot_runs/*`
- `outputs/pilot_extension_runs/*`
- `outputs/pilot_illumination_runs/*`

## Deliverables

- `.plans/021-labeled-fusion-analysis-and-scaling-decision.md`
- `src/eval/labeled_fusion_analysis.py`
- `scripts/build_labeled_fusion_analysis.py`
- `src/eval/labeled_fusion_analysis_checks.py`
- `scripts/validate_labeled_fusion_analysis.py`
- `labeled_fusion_analysis_summary.json`
- `labeled_fusion_scaling_blocker_summary.json`
- `route_comparison_A_vs_B.json`
- `labeled_fusion_vs_unlabeled_fusion_comparison.csv`
- `labeled_fusion_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: labeled fusion compact analysis / blocker summary / route comparison
- [x] Milestone 2: scaling recommendation / acceptance / README / 计划收口

## Surprises & Discoveries

- 当前 local slice 明明已经 materialize 出 `5` 条 reasoning / confidence / illumination query contracts，但之前 real-pilot execution 一直停留在 `smoke_mode` 的 `2` 条预算。
- 现有 labeled pilot 也已经覆盖完整 `10` 条 `control / targeted` contract rows，因此当前 4-row labeled fusion bootstrap 的真正瓶颈不是“没有更多标签”，而是“real-pilot coverage 没有被跑满”。
- 021 的 repeatability 已验证：reference 与 rerun 都推荐路线 A，且当前 labeled fusion row 数一致为 `4`。

## Decision Log

- 决策：021 显式比较路线 A 与路线 B，但默认推荐路线 A。
  - 原因：路线 A 不需要新标签定义、不需要新资源，而且能立刻把 supervised fusion 从 `4` 行 bootstrap 扩成更大的可执行集合。
  - 影响范围：022 选择 `controlled-supervision-coverage-expansion`，而不是先做更自然标签 bootstrap。

- 决策：把当前 bottleneck 定义为 `coverage_before_label_naturalness`。
  - 原因：在当前仓库与资源条件下，先扩大已有 controlled supervision 的覆盖面，增益更直接、风险更低。
  - 影响范围：`labeled_fusion_next_step_recommendation.json` 的 bootstrap contract。

## Plan of Work

先统一读取 019/020、015/016 和三条 real pilot 的关键 artifact，明确当前 supervised fusion 已有的价值与真正瓶颈。然后比较“扩大当前 controlled supervision 覆盖面”和“引入更自然标签来源”两条路线，若推荐清晰，则直接给出下一步 bootstrap contract。

## Concrete Steps

1. 创建 `.plans/021-labeled-fusion-analysis-and-scaling-decision.md`。
2. 实现 `src/eval/labeled_fusion_analysis.py`。
3. 实现 `scripts/build_labeled_fusion_analysis.py`。
4. 生成 analysis / blocker / route comparison / recommendation artifacts。
5. 实现 validator 与 repeatability。
6. 更新 README 与计划状态。

## Validation and Acceptance

- `build_labeled_fusion_analysis.py --help` 可正常显示
- `validate_labeled_fusion_analysis.py --help` 可正常显示
- 成功生成：
  - `labeled_fusion_analysis_summary.json`
  - `labeled_fusion_scaling_blocker_summary.json`
  - `route_comparison_A_vs_B.json`
  - `labeled_fusion_vs_unlabeled_fusion_comparison.csv`
  - `labeled_fusion_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

### Validation Snapshot

- `outputs/labeled_fusion_analysis/default/labeled_fusion_analysis_summary.json`
  - `real_pilot_modules = [illumination, reasoning, confidence]`
  - `labeled_real_pilot_fusion.num_rows = 4`
  - `labeled_real_pilot_fusion.num_base_samples = 2`
- `outputs/labeled_fusion_analysis/default/labeled_fusion_next_step_recommendation.json`
  - `chosen_route = A`
  - `chosen_route_name = expand_current_controlled_supervision_coverage`
- `outputs/labeled_fusion_analysis/repeatability_default/repeatability_summary.json`
  - `all_key_metrics_match = true`

## Idempotence and Recovery

- 输出写入独立 `output_dir`
- 可重复运行
- 若任一上游 artifact 缺失，应输出结构化 failure summary

## Outputs and Artifacts

- `outputs/labeled_fusion_analysis/*`

## Remaining Risks

- 当前分析仍建立在 pilot-level controlled supervision 上。
- 当前 comparison 只基于 local CSQA-style slice 和轻量模型。
- 当前路线 A 的推荐虽然合理，但仍然只是“先扩 coverage，再决定是否引入更自然标签来源”的阶段性结论。

## Next Suggested Plan

若 021 推荐路线明确，下一步建议创建 `.plans/022-controlled-supervision-coverage-expansion.md`。
