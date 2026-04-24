# 088 Post-v7 Real Experiment Matrix Analysis

## Purpose / Big Picture

087 如果已经把 refined-fusion-support-ablation 推进到 execution，那么 088 的任务就是回答：`fusion_cell_refined_support_ablation` 相比 `fusion_cell_refined_support_sweep`、`fusion_cell_refined_ablation`、`fusion_cell_refined`、`fusion_cell_candidate`、`fusion_summary` 是否真的提供了新的可解释信息。

## Scope

### In Scope

- v7 unified analysis
- support-ablation vs support-sweep / refined-ablation / refined / candidate / summary comparison
- blocker summary
- next-step recommendation

### Out of Scope

- 直接执行下一轮矩阵
- 大规模论文主实验

## Repository Context

本计划主要衔接：

- `outputs/next_axis_after_v6_matrix_execution/default/*`
- `outputs/post_v6_real_experiment_matrix_analysis/default/*`
- `outputs/next_axis_after_v6_matrix_bootstrap/default/*`

## Deliverables

- `.plans/088-post-v7-real-experiment-matrix-analysis.md`
- `src/eval/post_v7_real_experiment_matrix_analysis.py`
- `src/eval/post_v7_real_experiment_matrix_analysis_checks.py`
- `scripts/build_post_v7_real_experiment_matrix_analysis.py`
- `scripts/validate_post_v7_real_experiment_matrix_analysis.py`
- `next_axis_after_v6_matrix_analysis_summary.json`
- `fusion_support_ablation_vs_support_sweep_comparison.json`
- `fusion_support_ablation_vs_refined_comparison.json`
- `fusion_support_ablation_vs_refined_ablation_comparison.json`
- `fusion_support_ablation_vs_candidate_comparison.json`
- `fusion_support_ablation_vs_summary_comparison.json`
- `v7_vs_v6_matrix_comparison.json`
- `v7_matrix_blocker_summary.json`
- `v7_matrix_tradeoff_matrix.csv`
- `next_axis_after_v6_matrix_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: run v7 matrix analysis
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Surprises & Discoveries

- v7 的新增价值不只是“多一个 cell”，而是把 support-retained residue 从 support-sweep 里显式分离出来。
- 在当前 repo reality 下，继续扩 support-residual stability 比直接跳模型轴或 dataset 轴更诚实也更可执行。

## Decision Log

- 决策：088 默认不回头做 proxy substrate，而是优先评估 support-ablation 是否已经把 refined fusion 的 support-isolation 增量刻画得足够清楚。
  - 原因：当前研究增量已经集中在 real-experiment matrix 的 fusion support isolation 语义上。
  - 影响范围：tradeoff matrix、recommendation。

## Plan of Work

先统一读取从 057 到 087 的关键 lineage，重点聚焦 v7 execution 中的 support-ablation summary。随后生成多组对比 JSON 和 tradeoff matrix，最后给出下一轮矩阵的推荐扩张轴，并完成 validator 与文档收口。

## Concrete Steps

1. 创建 v7 analysis 实现与 CLI。
2. 读取 v7 support-ablation / support-sweep / refined-ablation / refined / candidate / summary artifacts。
3. 生成 comparison、blocker、tradeoff、recommendation。
4. 跑 default / default_repeat 两次 analysis。
5. 跑 validator。
6. 更新 README 与计划进度。

## Validation and Acceptance

- `build_post_v7_real_experiment_matrix_analysis.py --help` 可正常显示
- `validate_post_v7_real_experiment_matrix_analysis.py --help` 可正常显示
- 至少生成：
  - `next_axis_after_v6_matrix_analysis_summary.json`
  - `fusion_support_ablation_vs_support_sweep_comparison.json`
  - `fusion_support_ablation_vs_refined_comparison.json`
  - `fusion_support_ablation_vs_refined_ablation_comparison.json`
  - `fusion_support_ablation_vs_candidate_comparison.json`
  - `fusion_support_ablation_vs_summary_comparison.json`
  - `v7_vs_v6_matrix_comparison.json`
  - `v7_matrix_blocker_summary.json`
  - `v7_matrix_tradeoff_matrix.csv`
  - `next_axis_after_v6_matrix_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- analysis 可重复运行，覆盖目标输出目录中的同名文件。
- 若 build 失败，可直接重跑 build CLI。
- 若 compare-run 失败，可单独重跑 repeat 目录和 validator。

## Remaining Risks

- 即使 v7 analysis 明确了 support-ablation 的新增价值，这个“新增价值”仍然不是 benchmark 级结论。
- 如果后续要扩模型或数据轴，仍缺更成熟的本地 ready object。

## Outcome Summary

- `outputs/post_v7_real_experiment_matrix_analysis/default/next_axis_after_v6_matrix_analysis_summary.json` 已确认 v7 matrix execution 成立。
- `outputs/post_v7_real_experiment_matrix_analysis/default/next_axis_after_v6_matrix_next_step_recommendation.json` 已明确推荐 `bootstrap_next_axis_after_v7_matrix`。
- `outputs/post_v7_real_experiment_matrix_analysis/repeatability_default/artifact_acceptance.json` 已确认 acceptance / repeatability 为 `PASS`。

## Next Suggested Plan

若 088 完成，下一步应进入 089，把 recommendation 对应的下一轮矩阵先 bootstrap 起步。
