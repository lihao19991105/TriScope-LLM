# 092 Post-v8 Real-Experiment Matrix Analysis

## Purpose / Big Picture

091 已经把 `next_axis_after_v7_real_experiment_matrix_v8` 推进到 execution 成立，092 的任务是统一分析这个 support-ablation-sweep-aware v8 矩阵，并明确下一步最值得扩的真实实验轴。

## Scope

### In Scope

- v8 matrix analysis summary
- v8 对 v7 / v6 / v5 / v4 / 更早阶段的关键比较
- blocker summary
- next-step recommendation
- acceptance / repeatability

### Out of Scope

- 直接运行下一轮完整矩阵
- 模型 / dataset 轴的大规模扩展

## Repository Context

本计划主要衔接：

- `outputs/next_axis_after_v7_matrix_execution/default/*`
- `outputs/post_v7_real_experiment_matrix_analysis/default/*`
- 全部 057~091 关键 lineage artifacts

## Deliverables

- `.plans/092-post-v8-real-experiment-matrix-analysis.md`
- `src/eval/post_v8_real_experiment_matrix_analysis.py`
- `src/eval/post_v8_real_experiment_matrix_analysis_checks.py`
- `scripts/build_post_v8_real_experiment_matrix_analysis.py`
- `scripts/validate_post_v8_real_experiment_matrix_analysis.py`
- `next_axis_after_v7_matrix_analysis_summary.json`
- `fusion_support_ablation_sweep_vs_support_ablation_comparison.json`
- `fusion_support_ablation_sweep_vs_support_sweep_comparison.json`
- `fusion_support_ablation_sweep_vs_refined_comparison.json`
- `fusion_support_ablation_sweep_vs_candidate_comparison.json`
- `fusion_support_ablation_sweep_vs_summary_comparison.json`
- `v8_vs_v7_matrix_comparison.json`
- `v8_matrix_blocker_summary.json`
- `v8_matrix_tradeoff_matrix.csv`
- `next_axis_after_v7_matrix_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: unify v8 matrix analysis
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Surprises & Discoveries

- v8 的新增价值不是“出现更高分数”，而是把 support-isolated floor 在继续 sweep 后是否变化这件事显式化。
- 在当前 lightweight setting 下，support-ablation-sweep 很可能继续贴近 candidate floor；这不是坏事，反而是下一轮 floor-invariance probe 的直接依据。

## Decision Log

- 决策：092 优先把 support-ablation-sweep 与 support-ablation / support-sweep / refined / candidate / summary 做清晰对照，而不急于切换到模型轴或 dataset 轴。
  - 原因：当前仓库最成熟、最可复现的新增信息仍然来自 fusion residual stability 链条。
  - 影响范围：comparison files、tradeoff matrix、recommendation。

## Plan of Work

先统一读取 057~091 的关键 lineage artifacts，再形成 v8 summary、核心比较、blocker summary 和 tradeoff matrix。随后输出 recommendation，并通过 repeatability validator 收口，最后更新 README 与计划。

## Concrete Steps

1. 创建 v8 analysis 实现与 CLI。
2. 聚合 lineage artifacts 并生成 comparison files。
3. 生成 blocker summary、tradeoff matrix 和 recommendation。
4. 跑 default / default_repeat 两次 analysis。
5. 跑 validator 并确认 recommendation 稳定。
6. 更新 README 与计划进度。

## Validation and Acceptance

- `build_post_v8_real_experiment_matrix_analysis.py --help` 可正常显示
- `validate_post_v8_real_experiment_matrix_analysis.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v7_matrix_analysis_summary.json`
  - `fusion_support_ablation_sweep_vs_support_ablation_comparison.json`
  - `fusion_support_ablation_sweep_vs_support_sweep_comparison.json`
  - `v8_vs_v7_matrix_comparison.json`
  - `v8_matrix_blocker_summary.json`
  - `v8_matrix_tradeoff_matrix.csv`
  - `next_axis_after_v7_matrix_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- analysis 可以重复执行，覆盖目标输出目录中的同名文件。
- 若单次 run 失败，可直接重跑 build CLI。
- 若 build 成功但 validator 失败，可保留 run 目录并单独重跑 validator。

## Remaining Risks

- 当前分析仍然建立在一个 ready-local dataset slice 和一个 lightweight model 之上。
- v8 证明的是 support-residual stability coverage 可以被持续刻画，而不是论文级最终研究结论。

## Outcome Summary

- `outputs/post_v8_real_experiment_matrix_analysis/default/next_axis_after_v7_matrix_analysis_summary.json` 已确认 v8 matrix execution 成立。
- `outputs/post_v8_real_experiment_matrix_analysis/default/next_axis_after_v7_matrix_next_step_recommendation.json` 已明确推荐 `bootstrap_next_axis_after_v8_matrix`。
- `outputs/post_v8_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json` 已确认 acceptance / repeatability 为 `PASS`。

## Next Suggested Plan

若 092 完成，下一步应进入 093，优先把 support-floor invariance 方向 bootstrap 成下一轮真实实验矩阵对象。
