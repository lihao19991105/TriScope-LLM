# 072 Post V3 Real Experiment Matrix Analysis

## Purpose / Big Picture

071 完成后，仓库第一次拥有 fusion-cell-aware matrix v3 execution。072 的任务是判断 `fusion_cell_candidate` 是否真的带来了新增判断信息，并据此决定下一轮真实实验矩阵最值得扩的轴。

## Scope

### In Scope

- v3 vs v2 / v1 / earlier cutover 对比
- fusion cell vs fusion summary 对比
- blocker summary
- next-step recommendation

### Out of Scope

- 直接执行 next-axis matrix
- 回退去继续 proxy substrate 扩容

## Repository Context

本计划主要衔接：

- `outputs/post_next_real_experiment_matrix_execution/default/*`
- `outputs/next_real_experiment_matrix_execution/default/*`
- `outputs/post_next_real_experiment_matrix_bootstrap/default/*`

## Deliverables

- `.plans/072-post-v3-real-experiment-matrix-analysis.md`
- `src/eval/post_v3_real_experiment_matrix_analysis.py`
- `src/eval/post_v3_real_experiment_matrix_analysis_checks.py`
- `scripts/build_post_v3_real_experiment_matrix_analysis.py`
- `scripts/validate_post_v3_real_experiment_matrix_analysis.py`
- `post_next_matrix_analysis_summary.json`
- `fusion_cell_vs_fusion_summary_comparison.json`
- `v3_vs_v2_matrix_comparison.json`
- `v3_matrix_blocker_summary.json`
- `v3_matrix_tradeoff_matrix.csv`
- `post_next_matrix_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: fusion-cell-aware matrix analysis
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Decision Log

- 决策：072 把分析核心聚焦在 `fusion_cell_candidate` 与 `fusion_summary` 的差异上，而不是再去讨论 proxy substrate。
  - 原因：本轮最重要的新增对象就是 fusion cell coverage。
  - 影响范围：recommendation 会优先围绕 fusion cell refinement 或其下一轴，不会回到 proxy 世界。

## Validation and Acceptance

- `build_post_v3_real_experiment_matrix_analysis.py --help` 可正常显示
- `validate_post_v3_real_experiment_matrix_analysis.py --help` 可正常显示
- 至少生成：
  - `post_next_matrix_analysis_summary.json`
  - `fusion_cell_vs_fusion_summary_comparison.json`
  - `v3_vs_v2_matrix_comparison.json`
  - `v3_matrix_blocker_summary.json`
  - `v3_matrix_tradeoff_matrix.csv`
  - `post_next_matrix_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- fusion cell 的新增信息仍然来自当前 small-scale matrix，不代表更大真实实验就会同样成立。
- 当前仍然没有第二个 ready-local 模型，模型轴扩展依然不成熟。

## Outcome Summary

- `outputs/post_v3_real_experiment_matrix_analysis/default/post_next_matrix_analysis_summary.json` 说明 fusion-cell-aware v3 已经成立。
- `outputs/post_v3_real_experiment_matrix_analysis/default/post_next_matrix_next_step_recommendation.json` 明确给出下一轮真实实验矩阵的推荐扩展轴。
- `outputs/post_v3_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 072 完成，下一步应进入 `073-next-axis-real-experiment-matrix-bootstrap`，把推荐的下一轴矩阵先 materialize 出来。
