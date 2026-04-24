# 016 Real Pilot Fusion Baselines

## Purpose / Big Picture

015 会把三条真实 pilot 的 cross-pilot reporting 与 fusion readiness 做实。下一步最自然的工作是：在这份 real-pilot fusion dataset 上跑出一版最小 fusion baseline，让“真实 pilot 级融合链路”不仅存在，而且已经具备最小可执行预测 artifact。

016 的目标不是得到稳定的研究分数，而是尽量用当前极小 real-pilot 数据跑通一版 rule-based baseline，并在条件允许时评估 logistic 的可行性与阻塞。

## Scope

### In Scope

- real-pilot fusion baseline 设计
- real-pilot prediction schema
- real-pilot rule baseline
- 如可行，real-pilot logistic baseline
- baseline summary / metadata artifact

### Out of Scope

- 大规模监督训练
- 超参搜索
- 复杂 classifier 矩阵
- benchmark-level 结果解读

## Repository Context

本计划将衔接：

- `outputs/real_pilot_fusion_readiness/*`
- `src/fusion/fusion_baselines.py`
- `src/fusion/`
- `scripts/`

## Deliverables

- `.plans/016-real-pilot-fusion-baselines.md`
- `src/fusion/real_pilot_baselines.py`
- `scripts/run_real_pilot_fusion_baselines.py`
- `real_pilot_rule_predictions.jsonl`
- `real_pilot_rule_summary.json`
- 如可行：`real_pilot_logistic_predictions.jsonl`
- 如可行：`real_pilot_logistic_summary.json`
- `real_pilot_fusion_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: baseline 设计 / prediction schema / feasibility 判定
- [x] Milestone 2: 真实 pilot 级 baseline artifact
- [x] Milestone 3: acceptance / repeatability / README / 计划收口

## Surprises & Discoveries

- 当前 real-pilot fusion dataset 虽然能 full-intersection 对齐，但仍然没有 backdoor ground-truth label，因此 logistic baseline 的监督训练前提并不成立。
- rule-based baseline 在当前 2 条 full-intersection 样本上可以稳定产出 prediction artifact，并且 rerun 结果一致，因此当前 real-pilot fusion 链路已经具备最小“存在性验证”。

## Decision Log

- 决策：016 优先保证 rule-based baseline 存在，并把 logistic baseline 设计成“可行性判定 + 如实跳过”的路径。
  - 原因：当前用户更需要真实 pilot 融合链路存在，而不是在没有真实标签的情况下硬造一个看似可跑的监督式分类器。
  - 影响范围：`src/fusion/real_pilot_baselines.py`、`real_pilot_logistic_summary.json`、README 的解释边界。

## Plan of Work

先读取 015 的 readiness summary，明确 real-pilot 数据是否具备监督标签和 full intersection 条件。然后定义与 007 一致的 prediction schema，先落一版 rule-based real-pilot baseline；若 logistic 仍然缺少标签，则输出结构化 skip summary，而不是硬塞一个没有研究意义的模型。

## Concrete Steps

1. 创建 `.plans/016-real-pilot-fusion-baselines.md`。
2. 实现 `src/fusion/real_pilot_baselines.py`。
3. 实现 `scripts/run_real_pilot_fusion_baselines.py`。
4. 读取 015 的 real-pilot fusion dataset 和 readiness summary。
5. 跑 rule-based baseline。
6. 判断 logistic 是否具备标签前提；若无，则写出 skip summary。

## Validation and Acceptance

- `run_real_pilot_fusion_baselines.py --help` 可正常显示
- 至少成功生成：
  - `real_pilot_rule_predictions.jsonl`
  - `real_pilot_rule_summary.json`
  - `real_pilot_fusion_summary.json`
- 若 logistic 可行，应再生成 logistic artifact；若不可行，应生成结构化 skip summary

## Idempotence and Recovery

- baseline 输出写入独立 `output_dir`
- 可重复运行
- 若 logistic 不可行，不应导致整个脚本失败

## Outputs and Artifacts

- `outputs/real_pilot_fusion_runs/*`
- `real_pilot_rule_predictions.jsonl`
- `real_pilot_rule_summary.json`
- `real_pilot_logistic_summary.json`
- `real_pilot_fusion_summary.json`

## Remaining Risks

- 当前 real-pilot baseline 仍然运行在极小样本上。
- 当前 rule-based 分数仍然只是 pilot-level 透明组合，不代表真实 fusion detector。
- logistic baseline 当前很可能只能停留在 “skip with reason”。

## Validation Snapshot

- `outputs/real_pilot_fusion_runs/default/real_pilot_rule_summary.json`
  - num predictions: `2`
  - mean prediction score: `0.8670376699699167`
- `outputs/real_pilot_fusion_runs/default/real_pilot_logistic_summary.json`
  - summary status: `SKIP`
  - reason: `missing_ground_truth_labels`
- `outputs/real_pilot_fusion_runs/repeatability_default/artifact_acceptance.json`
  - acceptance status: `PASS`
- `outputs/real_pilot_fusion_runs/repeatability_default/repeatability_summary.json`
  - repeatability status: `PASS`
  - all key metrics match: `true`

## Next Suggested Plan

若 016 完成，下一步建议创建 `.plans/017-real-pilot-analysis-and-next-step-selection.md`。
