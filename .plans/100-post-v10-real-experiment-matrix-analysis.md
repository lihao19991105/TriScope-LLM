# 100 Post-v10 Real-Experiment Matrix Analysis

## Purpose / Big Picture

099 已把 `fusion_cell_refined_support_ablation_floor_stress` 推进到 execution 层。100 的目标是统一比较 v10 与 v9/v8/v7/v6/v5/v4/v3/v2/v1/earlier cutover，回答 explicit support floor 在 direct stress 下是否仍 invariant，以及下一步最自然应继续扩什么。

## Scope

### In Scope

- v10 matrix analysis summary
- floor-stress vs floor-probe / support-ablation-sweep / support-ablation / support-sweep / refined / candidate / summary comparisons
- blocker summary
- next-step recommendation

### Out of Scope

- 新的执行层 rerun
- 模型轴和数据轴的直接扩张实现

## Repository Context

- `outputs/next_axis_after_v9_matrix_execution/default/*`
- `outputs/post_v9_real_experiment_matrix_analysis/default/*`
- 全部更早阶段 bootstrap / dry-run / execution / analysis lineage artifacts

## Deliverables

- `.plans/100-post-v10-real-experiment-matrix-analysis.md`
- `src/eval/post_v10_real_experiment_matrix_analysis.py`
- `src/eval/post_v10_real_experiment_matrix_analysis_checks.py`
- `scripts/build_post_v10_real_experiment_matrix_analysis.py`
- `scripts/validate_post_v10_real_experiment_matrix_analysis.py`
- `outputs/post_v10_real_experiment_matrix_analysis/default/next_axis_after_v9_matrix_analysis_summary.json`
- `outputs/post_v10_real_experiment_matrix_analysis/default/next_axis_after_v9_matrix_next_step_recommendation.json`
- `outputs/post_v10_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: unify v10 matrix analysis
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Decision Log

- 决策：100 不回头扩 proxy substrate，而是把新增价值定义为“explicit support floor 在 direct stress 下是否还保持 invariant”。
  - 原因：v10 已把 floor stress 变成显式执行对象，当前最自然的下一步就是继续 stress / invariance coverage，而不是回到 proxy 世界。

## Validation and Acceptance

- `build_post_v10_real_experiment_matrix_analysis.py --help` 可正常显示
- `validate_post_v10_real_experiment_matrix_analysis.py --help` 可正常显示
- `outputs/post_v10_real_experiment_matrix_analysis/default/next_axis_after_v9_matrix_analysis_summary.json` 为 `PASS`
- `outputs/post_v10_real_experiment_matrix_analysis/default/next_axis_after_v9_matrix_next_step_recommendation.json` 为 `PASS`
- `outputs/post_v10_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- v10 analysis 已完成，并确认 `matrix_execution_established = true`。
- 当前主结论是：`fusion_cell_refined_support_ablation_floor_stress` 把 explicit support floor 在 direct stress 下是否变化从“只能间接推断”推进成“可直接执行与比较”的对象。
- recommendation 已明确：`recommended_next_step = bootstrap_next_axis_after_v10_matrix`，`preferred_expansion_axis = fusion_support_floor_stress_invariance_coverage`。

## Next Suggested Plan

若 100 完成，下一步应进入 101，优先把 direct support-floor-stress invariance coverage 物化成 `next_axis_after_v10_real_experiment_matrix_v11`。
