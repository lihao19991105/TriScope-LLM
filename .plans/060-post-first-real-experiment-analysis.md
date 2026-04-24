# 060 Post First Real Experiment Analysis

## Purpose / Big Picture

059 若已经让第一轮真实实验风格执行真正发生，那么 060 的任务就是把它与最近一轮 proxy 结果放到同一层做分析，回答真实实验切换是否已经开始成立、当前最大 blocker 是什么、下一步最值得扩什么。

## Scope

### In Scope

- unify first real-experiment analysis
- compare against latest proxy stage
- blocker summary
- next-step recommendation

### Out of Scope

- 直接执行下一轮真实实验矩阵
- 回头继续机械扩 proxy substrate

## Repository Context

本计划主要衔接：

- `outputs/real_experiment_cutover_bootstrap/default/*`
- `outputs/real_experiment_first_dry_run/default/*`
- `outputs/first_real_experiment_execution/default/*`
- `outputs/post_v6_symmetric_comparison/default/*`
- `outputs/rerun_route_b_on_labeled_split_v6/default/*`
- `outputs/rerun_route_c_on_labeled_split_v6/default/*`

## Deliverables

- `.plans/060-post-first-real-experiment-analysis.md`
- `src/eval/post_first_real_experiment_analysis.py`
- `scripts/build_post_first_real_experiment_analysis.py`
- `src/eval/post_first_real_experiment_analysis_checks.py`
- `scripts/validate_post_first_real_experiment_analysis.py`
- `first_real_experiment_analysis_summary.json`
- `first_real_vs_proxy_comparison.json`
- `first_real_experiment_blocker_summary.json`
- `first_real_experiment_tradeoff_matrix.csv`
- `first_real_experiment_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: first real-experiment analysis and proxy comparison
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Surprises & Discoveries

- 当前最关键的分析问题已经不再是“proxy substrate 还能不能继续扩”，而是“real execution 到底成立到什么程度”。
- 060 的价值在于把 readiness、dry-run、execution 三层真正串起来，明确项目是否已经从 proxy 世界迈到真实实验风格执行世界。
- 实际分析结果很一致：`real_execution_established = true`，并且 recommendation 没有回头要求继续扩 proxy substrate，而是直接指向 `bootstrap_minimal_real_experiment_matrix`。

## Decision Log

- 决策：060 默认把 `first_real_execution` 与 `latest_proxy_v6` 放在同一层比较。
  - 原因：只有这样才能明确真实实验切换的新增价值与剩余 blocker。
  - 影响范围：comparison summary、tradeoff matrix、next-step recommendation。

## Plan of Work

先读取 057 cutover、058 dry-run、059 execution 以及 056/054/055 的 proxy v6 artifacts。然后输出 first-real analysis summary、first-real vs proxy comparison、blocker summary 与 tradeoff matrix。最后生成 next-step recommendation，并补 validator、repeatability 与 README。

## Concrete Steps

1. 实现 `src/eval/post_first_real_experiment_analysis.py` 与配套 CLI / validator。
2. 运行 build CLI 生成 analysis artifact。
3. 运行 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_post_first_real_experiment_analysis.py --help` 可正常显示
- `validate_post_first_real_experiment_analysis.py --help` 可正常显示
- 至少生成：
  - `first_real_experiment_analysis_summary.json`
  - `first_real_vs_proxy_comparison.json`
  - `first_real_experiment_blocker_summary.json`
  - `first_real_experiment_tradeoff_matrix.csv`
  - `first_real_experiment_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

060 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若只想复核 recommendation，可直接重跑 build 与 validate。

## Remaining Risks

- 060 的分析仍然基于小规模 local setup，而不是正式 benchmark 主实验。
- 若 059 的 first execution 仍然较轻，060 的 recommendation 也会带有过渡阶段属性。

## Outcome Summary

- `outputs/post_first_real_experiment_analysis/default/first_real_experiment_analysis_summary.json` 明确 `real_execution_established = true`。
- `outputs/post_first_real_experiment_analysis/default/first_real_experiment_next_step_recommendation.json` 推荐 `bootstrap_minimal_real_experiment_matrix`。
- `outputs/post_first_real_experiment_analysis/repeatability_default/artifact_acceptance.json` 显示 acceptance / repeatability 为 PASS。

## Next Suggested Plan

若 060 完成，下一步建议创建 `.plans/061-minimal-real-experiment-matrix-bootstrap.md`，把下一轮更像真实实验的最小矩阵先做成具体对象。
