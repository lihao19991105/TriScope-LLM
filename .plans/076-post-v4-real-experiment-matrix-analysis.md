# 076 Post-v4 Real Experiment Matrix Analysis

## Purpose / Big Picture

075 如果已经把 refined fusion 推进到 execution，那么 076 的任务就是回答：`fusion_cell_refined` 相比 `fusion_cell_candidate` 与 `fusion_summary` 是否真的提供了新的判断信息。

## Scope

### In Scope

- v4 unified analysis
- refined vs candidate / summary comparison
- blocker summary
- next-step recommendation

### Out of Scope

- 直接执行下一轮矩阵
- 大规模论文主实验

## Repository Context

本计划主要衔接：

- `outputs/next_axis_real_experiment_matrix_execution/default/*`
- `outputs/post_v3_real_experiment_matrix_analysis/default/*`
- `outputs/next_axis_real_experiment_matrix_bootstrap/default/*`

## Deliverables

- `.plans/076-post-v4-real-experiment-matrix-analysis.md`
- `src/eval/post_v4_real_experiment_matrix_analysis.py`
- `src/eval/post_v4_real_experiment_matrix_analysis_checks.py`
- `scripts/build_post_v4_real_experiment_matrix_analysis.py`
- `scripts/validate_post_v4_real_experiment_matrix_analysis.py`
- `next_axis_matrix_analysis_summary.json`
- `fusion_refined_vs_candidate_comparison.json`
- `fusion_refined_vs_summary_comparison.json`
- `v4_vs_v3_matrix_comparison.json`
- `v4_matrix_blocker_summary.json`
- `v4_matrix_tradeoff_matrix.csv`
- `next_axis_matrix_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: run v4 matrix analysis
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Decision Log

- 决策：076 默认不回头做 proxy substrate，而是优先评估 refined fusion coverage 是否值得继续扩。
  - 原因：当前研究增量已经集中在 real-experiment matrix 的 fusion 语义上。
  - 影响范围：tradeoff matrix、recommendation。

## Validation and Acceptance

- `build_post_v4_real_experiment_matrix_analysis.py --help` 可正常显示
- `validate_post_v4_real_experiment_matrix_analysis.py --help` 可正常显示
- 至少生成：
  - `next_axis_matrix_analysis_summary.json`
  - `fusion_refined_vs_candidate_comparison.json`
  - `fusion_refined_vs_summary_comparison.json`
  - `v4_vs_v3_matrix_comparison.json`
  - `v4_matrix_blocker_summary.json`
  - `v4_matrix_tradeoff_matrix.csv`
  - `next_axis_matrix_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- 即使 v4 analysis 明确了 refined fusion 的新增价值，这个“新增价值”仍然不是 benchmark 级结论。
- 如果后续要扩模型或数据轴，仍缺更成熟的本地 ready object。

## Outcome Summary

- `outputs/post_v4_real_experiment_matrix_analysis/default/next_axis_matrix_analysis_summary.json` 已给出 v4 matrix 是否成立的结论。
- `outputs/post_v4_real_experiment_matrix_analysis/default/next_axis_matrix_next_step_recommendation.json` 已给出下一步推荐轴。
- `outputs/post_v4_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 076 完成，下一步应进入 077，把 recommendation 对应的下一轮矩阵先 bootstrap 起步。
