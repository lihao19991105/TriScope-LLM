# 104 Post-v11 Real-Experiment Matrix Analysis

## Purpose / Big Picture

103 已把 `fusion_cell_refined_support_ablation_floor_stress_sweep` 推进到 execution 层。104 的目标是统一比较 v11 与 v10/v9/v8/v7/v6/v5/v4/v3/v2/v1/earlier cutover，并明确判断当前 fusion 同轴细化是否已经接近边际收益上限，以及是否应该切向 1.5B 模型轴。

## Scope

### In Scope

- v11 matrix analysis summary
- floor-stress-sweep vs floor-stress / floor-probe / support-ablation-sweep / refined comparisons
- blocker summary
- next-step recommendation

### Out of Scope

- 继续滚 v12 fusion bootstrap
- 直接执行 1.5B 模型

## Repository Context

- `outputs/next_axis_after_v10_matrix_execution/default/*`
- `outputs/post_v10_real_experiment_matrix_analysis/default/*`
- 全部更早阶段 bootstrap / dry-run / execution / analysis lineage artifacts

## Deliverables

- `.plans/104-post-v11-real-experiment-matrix-analysis.md`
- `src/eval/post_v11_real_experiment_matrix_analysis.py`
- `src/eval/post_v11_real_experiment_matrix_analysis_checks.py`
- `scripts/build_post_v11_real_experiment_matrix_analysis.py`
- `scripts/validate_post_v11_real_experiment_matrix_analysis.py`
- `outputs/post_v11_real_experiment_matrix_analysis/default/next_axis_after_v10_matrix_analysis_summary.json`
- `outputs/post_v11_real_experiment_matrix_analysis/default/next_axis_after_v10_matrix_next_step_recommendation.json`
- `outputs/post_v11_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: unify v11 matrix analysis
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Decision Log

- 决策：104 不继续默认推荐同轴 fusion v12/v13，而是把重点放在判断边际新增是否已经变小，以及是否应切模型轴。
  - 原因：当前 v11 的新增更偏向 confirmatory invariance evidence，已经非常接近“再多一个 cell 但结论变化不大”的边界。

## Validation and Acceptance

- `build_post_v11_real_experiment_matrix_analysis.py --help` 可正常显示
- `validate_post_v11_real_experiment_matrix_analysis.py --help` 可正常显示
- `outputs/post_v11_real_experiment_matrix_analysis/default/next_axis_after_v10_matrix_analysis_summary.json` 为 `PASS`
- `outputs/post_v11_real_experiment_matrix_analysis/default/next_axis_after_v10_matrix_next_step_recommendation.json` 为 `PASS`
- `outputs/post_v11_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- v11 analysis 已完成，并确认 `matrix_execution_established = true`。
- 当前主结论是：同轴 fusion 细化仍成立，但新增价值已明显转向 confirmatory / marginal。
- recommendation 已明确：`recommended_next_step = bootstrap_model_axis_1p5b`。

## Next Suggested Plan

若 104 完成，下一步不应继续机械创建 v12 fusion bootstrap，而应进入 105，先做 1.5B 单模型轴 bootstrap。
