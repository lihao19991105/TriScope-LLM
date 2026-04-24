# 023 More Natural Label Bootstrap Decision

## Purpose / Big Picture

022 已经把 current controlled supervision 从 `4` 行扩到 `10` 行，并把当前 local slice 的 aligned coverage 跑满。023 的目标是判断：在这个节点上，项目是否应该继续停留在 `pilot_level_controlled_supervision`，还是应该开始引入第一条更自然的标签路线。

## Scope

### In Scope

- 022 之后的 supervised fusion 边际收益分析
- route A vs route B 的结构化比较
- more-natural-label 候选可执行性分析
- 下一步推荐路线与 bootstrap contract
- acceptance / repeatability / README / 计划收口

### Out of Scope

- 直接扩更大模型
- 引入 benchmark 级真值标签
- 大规模监督实验
- 新开第四条 / 第五条 pilot

## Repository Context

本计划将衔接：

- `outputs/labeled_fusion_analysis/*`
- `outputs/controlled_supervision_expansion/*`
- `outputs/labeled_real_pilot_fusion/*`
- `outputs/labeled_real_pilot_fusion_runs/*`
- `outputs/real_pilot_fusion_readiness/*`
- `outputs/real_pilot_fusion_runs/*`

## Deliverables

- `.plans/023-more-natural-label-bootstrap-decision.md`
- `src/eval/more_natural_label_analysis.py`
- `scripts/build_more_natural_label_analysis.py`
- `src/eval/more_natural_label_analysis_checks.py`
- `scripts/validate_more_natural_label_analysis.py`
- `controlled_supervision_scaling_summary.json`
- `route_A_vs_route_B_comparison.json`
- `supervision_ceiling_summary.json`
- `route_decision_inputs.csv`
- `more_natural_label_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: controlled supervision after-expansion analysis
- [x] Milestone 2: recommendation / bootstrap contract / acceptance / 收口

## Surprises & Discoveries

- 022 的 route A 已经把当前 local slice 的 aligned base sample 跑满到了 `5`，所以继续扩大 A 的首要阻塞点不再是 orchestration，而是 slice ceiling。
- 当前仓库里已经存在一个低成本的 route B 候选：使用 local CSQA-style slice 中的 `answerKey`，结合 expanded reasoning / confidence / illumination 原始输出，构造 base-sample 级 `task_correctness_violation_label`。
- 这个候选不是 benchmark ground truth，但它明显比 `control / targeted` contract label 更自然，因为它依赖任务答案正确性而不是人为 contract 变体。
- 当前 more-natural 候选在 5-row slice 上已经具备双类分布，可直接支撑最小 bootstrap。

## Decision Log

- 决策：023 推荐 route B，开始 first more-natural-label bootstrap。
  - 原因：route A 已达到当前 local slice ceiling，继续扩大它必须先扩数据切片；而 route B 已经有一个无需新资源的 low-cost 候选。
  - 影响范围：`more_natural_label_next_step_recommendation.json`、024 plan。

- 决策：023 将 more-natural label 明确定义为 pilot-level task-truth proxy，而不是 benchmark supervision。
  - 原因：当前标签来自 local slice 的 `answerKey` 与 observed pilot outputs，只能诚实地描述为更自然但仍有限的监督源。
  - 影响范围：recommendation contract、README、Remaining Risks。

## Plan of Work

先汇总 020/022 的监督 fusion 状态，明确 route A 从 `4 -> 10` 的收益和 ceiling。然后分析 route B 的最小可执行候选，重点验证它是否能利用当前 local slice 的 `answerKey` 在 base-sample 层生成更自然的监督信号。最后形成结构化 recommendation，并把 023 做 acceptance / repeatability 收口。

## Concrete Steps

1. 创建 `.plans/023-more-natural-label-bootstrap-decision.md`。
2. 实现 `src/eval/more_natural_label_analysis.py`。
3. 实现 `scripts/build_more_natural_label_analysis.py`。
4. 生成 scaling summary、route comparison、ceiling summary、recommendation。
5. 实现 validator 与 repeatability。
6. 更新 README 与计划状态。

## Validation and Acceptance

- `build_more_natural_label_analysis.py --help` 可正常显示
- `validate_more_natural_label_analysis.py --help` 可正常显示
- 成功生成：
  - `controlled_supervision_scaling_summary.json`
  - `route_A_vs_route_B_comparison.json`
  - `supervision_ceiling_summary.json`
  - `route_decision_inputs.csv`
  - `more_natural_label_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

### Validation Snapshot

- `outputs/more_natural_label_analysis/default/controlled_supervision_scaling_summary.json`
  - `expanded_labeled_rows = 10`
  - `expanded_aligned_base_samples = 5`
- `outputs/more_natural_label_analysis/default/route_A_vs_route_B_comparison.json`
  - route A 标记为 `near_current_slice_ceiling`
  - route B 标记为 `ready_low_cost_candidate`
- `outputs/more_natural_label_analysis/default/more_natural_label_next_step_recommendation.json`
  - `chosen_route = B`
  - `chosen_route_name = bootstrap_more_natural_label`
- `outputs/more_natural_label_analysis/default/controlled_supervision_scaling_summary.json`
  - `expanded_supervised_logistic.mean_prediction_score = 0.5007625981729338`
- `outputs/more_natural_label_analysis/repeatability_default/repeatability_summary.json`
  - `all_key_metrics_match = true`

## Idempotence and Recovery

- 输出写入独立 `output_dir`
- 可重复运行
- 若上游 artifact 缺失，应写出结构化 failure summary

## Outputs and Artifacts

- `outputs/more_natural_label_analysis/*`

## Remaining Risks

- 当前推荐的 more-natural label 仍然不是 benchmark ground truth。
- 当前可用候选仍然依赖同一个 local CSQA-style 小切片与轻量模型。
- 当前 analysis 证明的是“route B 已经值得启动”，而不是“route B 已经足够支撑研究级监督结论”。

## Next Suggested Plan

若 023 完成，下一步建议创建 `.plans/024-more-natural-label-bootstrap.md`。
