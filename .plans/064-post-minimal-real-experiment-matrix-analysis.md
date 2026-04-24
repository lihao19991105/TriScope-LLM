# 064 Post Minimal Real Experiment Matrix Analysis

## Purpose / Big Picture

063 若已经让第一轮 matrix-level 真实执行真正发生，那么 064 的任务就是把它与 single-cutover execution 和最近 proxy v6 结果放到同一层分析，明确 matrix-level real experiment 是否已经开始成立，以及下一步最值得扩什么。

## Scope

### In Scope

- matrix-level analysis
- compare against first-cutover execution and latest proxy stage
- blocker summary
- next-step recommendation

### Out of Scope

- 直接执行下一轮真实实验矩阵
- 回头继续 proxy substrate 扩容

## Repository Context

本计划主要衔接：

- `outputs/minimal_real_experiment_matrix_bootstrap/default/*`
- `outputs/first_minimal_real_experiment_matrix_dry_run/default/*`
- `outputs/first_minimal_real_experiment_matrix_execution/default/*`
- `outputs/first_real_experiment_execution/default/*`
- `outputs/post_v6_symmetric_comparison/default/*`

## Deliverables

- `.plans/064-post-minimal-real-experiment-matrix-analysis.md`
- `src/eval/post_minimal_real_experiment_matrix_analysis.py`
- `src/eval/post_minimal_real_experiment_matrix_analysis_checks.py`
- `scripts/build_post_minimal_real_experiment_matrix_analysis.py`
- `scripts/validate_post_minimal_real_experiment_matrix_analysis.py`
- `minimal_matrix_analysis_summary.json`
- `matrix_vs_cutover_comparison.json`
- `matrix_vs_proxy_comparison.json`
- `minimal_matrix_blocker_summary.json`
- `minimal_matrix_tradeoff_matrix.csv`
- `minimal_matrix_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: matrix-level analysis and comparison
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Decision Log

- 决策：064 默认把 `first_matrix_execution`、`first_real_execution` 与 `latest_proxy_v6` 放到同一层比较。
  - 原因：这样才能回答 matrix-level real experiment 到底有没有超过 single-cutover execution。
  - 影响范围：comparison summary、tradeoff matrix、next-step recommendation。

## Validation and Acceptance

- `build_post_minimal_real_experiment_matrix_analysis.py --help` 可正常显示
- `validate_post_minimal_real_experiment_matrix_analysis.py --help` 可正常显示
- 至少生成：
  - `minimal_matrix_analysis_summary.json`
  - `matrix_vs_cutover_comparison.json`
  - `matrix_vs_proxy_comparison.json`
  - `minimal_matrix_blocker_summary.json`
  - `minimal_matrix_tradeoff_matrix.csv`
  - `minimal_matrix_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Remaining Risks

- 064 的结论仍然基于小规模 local setup。
- recommendation 仍然带有“过渡到下一轮矩阵”的阶段属性。

## Outcome Summary

- `outputs/post_minimal_real_experiment_matrix_analysis/default/minimal_matrix_analysis_summary.json` 明确 `matrix_execution_established = true`。
- `outputs/post_minimal_real_experiment_matrix_analysis/default/minimal_matrix_next_step_recommendation.json` 推荐 `bootstrap_next_real_experiment_matrix`，扩张轴为 `route_and_fusion_coverage`。
- `outputs/post_minimal_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 064 完成，下一步建议创建 `.plans/065-next-real-experiment-matrix-bootstrap.md`，把下一轮矩阵先做成具体对象。
