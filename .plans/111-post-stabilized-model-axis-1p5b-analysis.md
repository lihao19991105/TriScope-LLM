# 111 Post Stabilized Model-Axis 1.5B Analysis

## Purpose / Big Picture

110 已完成 stabilized 1.5B route_b rerun，并解除单类阻塞。111 的目标是分析 stabilized 110 相比 lightweight baseline 与 107 原始版本的新增价值，判断模型轴下一步应优先扩 route_c/fusion 还是继续稳住 1.5B route_b。

## Scope

### In Scope

- 对比 lightweight baseline / 107 / stabilized 110 的 execution 与标签可分性状态。
- 输出 blocker 变化与可分析性结论。
- 形成下一步建议并明确优先级。

### Out of Scope

- 新一轮 3B / 7B 扩展。
- fusion 轴回退或扩张。
- 新训练主线。

## Repository Context

- `outputs/model_axis_1p5b_analysis/default/*`
- `outputs/model_axis_1p5b_execution/default/*`
- `outputs/model_axis_1p5b_route_b_stable_execution/default/*`
- `outputs/rerun_route_b_on_labeled_split_v6/default/*`

## Deliverables

- `.plans/111-post-stabilized-model-axis-1p5b-analysis.md`
- `src/eval/post_stabilized_model_axis_1p5b_analysis.py`
- `scripts/build_post_stabilized_model_axis_1p5b_analysis.py`
- `outputs/model_axis_1p5b_stable_analysis/default/model_axis_1p5b_stable_analysis_summary.json`
- `outputs/model_axis_1p5b_stable_analysis/default/model_axis_1p5b_stable_vs_original_comparison.json`
- `outputs/model_axis_1p5b_stable_analysis/default/model_axis_1p5b_stable_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: compare lightweight baseline / original 107 / stabilized 110 and summarize blockers
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Decision Log

- 决策：111 继续以 route_b 为主分析对象。
  - 原因：当前 stabilized 成果来自 route_b，且问题核心是从“可运行”迈向“可分析”。
- 决策：111 重点比较 blocker 状态变化与分析可行性，不以分数高低作为主目标。
  - 原因：当前阶段的研究价值在于解除结构性阻塞并稳定模型轴证据链。

## Validation and Acceptance

- `python3 scripts/build_post_stabilized_model_axis_1p5b_analysis.py --help` 可正常显示。
- 三份分析 JSON 成功落盘。
- recommendation 明确下一步优先方向与不建议方向。

## Remaining Risks

- 当前 stabilized class balance 仍偏斜，指标稳定性有限。
- 结论仍局限于 route_b，尚未覆盖 route_c/fusion_summary 的并行可比性。

## Outcome Snapshot

- 111 已确认 1.5B route_b 从 `PARTIAL_SINGLE_CLASS_LABEL_COLLAPSE` 进入 `FULL_EXECUTE`。
- 主要 blocker 已从“单类导致 logistic BLOCKED”转为“类别偏斜但可分析”。
- 下一步建议为：`expand_route_c_after_one_route_b_stability_confirmation`。

## Next Suggested Plan

若 111 显示 route_b 已稳定可分析，下一步建议受控推进 route_c portability 或 route_b/route_c 最小联合分析，而非直接切更大模型。
