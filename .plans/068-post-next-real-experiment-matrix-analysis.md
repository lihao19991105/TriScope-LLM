# 068 Post Next Real Experiment Matrix Analysis

## Purpose / Big Picture

067 完成后，仓库第一次拥有 richer matrix v2 execution。068 的任务是判断这轮 richer coverage 是否真的提供了比 minimal matrix v1 更多的信息，并据此决定下一轮真实实验矩阵应该往哪里扩。

## Scope

### In Scope

- richer matrix vs minimal matrix 对比
- richer matrix vs earlier cutover 对比
- blocker summary
- next-step recommendation

### Out of Scope

- 直接执行下一轮完整矩阵
- 回退去继续 proxy substrate 扩容

## Repository Context

本计划主要衔接：

- `outputs/next_real_experiment_matrix_execution/default/*`
- `outputs/post_minimal_real_experiment_matrix_analysis/default/*`
- `outputs/first_minimal_real_experiment_matrix_execution/default/*`

## Deliverables

- `.plans/068-post-next-real-experiment-matrix-analysis.md`
- `src/eval/post_next_real_experiment_matrix_analysis.py`
- `src/eval/post_next_real_experiment_matrix_analysis_checks.py`
- `scripts/build_post_next_real_experiment_matrix_analysis.py`
- `scripts/validate_post_next_real_experiment_matrix_analysis.py`
- `next_matrix_analysis_summary.json`
- `richer_matrix_vs_minimal_matrix_comparison.json`
- `richer_matrix_vs_cutover_comparison.json`
- `richer_matrix_blocker_summary.json`
- `richer_matrix_tradeoff_matrix.csv`
- `next_matrix_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: richer matrix analysis
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Decision Log

- 决策：068 把分析重点放在 richer route coverage 与 ablation 信息增益上，而不是重新讨论 proxy substrate。
  - 原因：当前主线已经明确转入 real-experiment matrix 世界。
  - 影响范围：recommendation 会优先围绕 next matrix enrichment，而不是 proxy rollback。

## Validation and Acceptance

- `build_post_next_real_experiment_matrix_analysis.py --help` 可正常显示
- `validate_post_next_real_experiment_matrix_analysis.py --help` 可正常显示
- 至少生成：
  - `next_matrix_analysis_summary.json`
  - `richer_matrix_vs_minimal_matrix_comparison.json`
  - `richer_matrix_vs_cutover_comparison.json`
  - `richer_matrix_blocker_summary.json`
  - `richer_matrix_tradeoff_matrix.csv`
  - `next_matrix_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- richer matrix 仍然不代表 benchmark-grade matrix。
- 新增信息主要来自 route coverage 与 ablation coverage，还不是模型或数据维度的扩展。

## Outcome Summary

- `outputs/post_next_real_experiment_matrix_analysis/default/next_matrix_analysis_summary.json` 说明 richer matrix v2 已经成立，并给出新增信息的总结。
- `outputs/post_next_real_experiment_matrix_analysis/default/next_matrix_next_step_recommendation.json` 明确下一轮矩阵的推荐扩展方向。
- `outputs/post_next_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 068 完成，下一步应进入 `069-post-next-real-experiment-matrix-bootstrap`，把推荐的下一轮 richer matrix 路线 materialize 出来。
