# 025 More Natural Vs Controlled Supervision Comparison

## Purpose / Big Picture

024 已经证明：当前仓库里既存在 route A 的 controlled supervision expansion，也存在 route B 的 more-natural proxy bootstrap。025 的目标是把 A / B / C 放到同一层统一比较，并明确下一步到底该继续哪条监督路线。

## Scope

### In Scope

- route A / B / C compact comparison
- supervision value / ceiling / cost / risk summary
- next-step ranking and recommendation
- 026 bootstrap contract definition
- acceptance / repeatability / README / 收口

### Out of Scope

- 直接扩大 benchmark 数据规模
- 更大模型
- 研究级监督结论

## Repository Context

本计划将衔接：

- `outputs/labeled_real_pilot_fusion/*`
- `outputs/labeled_real_pilot_fusion_runs/*`
- `outputs/labeled_fusion_analysis/*`
- `outputs/controlled_supervision_expansion/*`
- `outputs/more_natural_label_analysis/*`
- `outputs/more_natural_label_bootstrap/*`
- `outputs/real_pilot_fusion_readiness/*`
- `outputs/real_pilot_fusion_runs/*`

## Deliverables

- `.plans/025-more-natural-vs-controlled-supervision-comparison.md`
- `src/eval/supervision_route_comparison.py`
- `scripts/build_supervision_route_comparison.py`
- `src/eval/supervision_route_comparison_checks.py`
- `scripts/validate_supervision_route_comparison.py`
- `supervision_route_comparison_summary.json`
- `route_A_vs_B_vs_C_comparison.json`
- `supervision_tradeoff_matrix.csv`
- `supervision_ceiling_and_cost_summary.json`
- `supervision_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: route A / B / C compact comparison
- [x] Milestone 2: recommendation / bootstrap contract / acceptance / 收口

## Surprises & Discoveries

- route B 虽然比 route A 更自然，但它当前已经覆盖了全部 `5` 个 aligned base sample，因此继续扩大 B 的第一步也会撞到 current local slice ceiling。
- current repo 已经存在一个比 B 更接近 truth、但成本依然很低的 C 候选：直接使用 labeled illumination contract rows 的 `query_answer_key` correctness。
- 这个 C 候选可以在当前仓库上自然 materialize 为 `10` 条 contract-level rows，并且已经具备双类分布 `6 / 4`。
- 因此当前真正的下一步不是“继续在 B 上小修小补”，而是把 C 这条更接近 truth 的路线先 bootstrap 出来。

## Decision Log

- 决策：025 推荐方向 C，进入 benchmark-truth-leaning label bootstrap。
  - 原因：A 已接近 current slice ceiling；B 已把 base-sample scope 跑满；C 已具备 low-cost、low-friction、10-row、direct-answer-correctness 的候选。
  - 影响范围：`supervision_next_step_recommendation.json`、026 plan。

- 决策：025 将方向 C 明确定义为 `benchmark_truth_leaning_supervision_proxy`，而不是 benchmark ground truth。
  - 原因：当前 label 仍然来自 local slice 的 answer correctness，缺少更大规模 benchmark coverage 与更强 truth guarantees。
  - 影响范围：README、Remaining Risks、026 dataset schema。

## Plan of Work

先统一读取 A/B/C 对应的 artifact，比较它们在覆盖面、自然性、成本、可解释性和 ceiling 上的差异。然后产出结构化 ranking 和 recommendation。如果 recommendation 清楚，就直接定义 026 的 bootstrap contract，并把 025 做 acceptance / repeatability 收口。

## Validation and Acceptance

- `build_supervision_route_comparison.py --help` 可正常显示
- `validate_supervision_route_comparison.py --help` 可正常显示
- 成功生成：
  - `supervision_route_comparison_summary.json`
  - `route_A_vs_B_vs_C_comparison.json`
  - `supervision_tradeoff_matrix.csv`
  - `supervision_ceiling_and_cost_summary.json`
  - `supervision_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

### Validation Snapshot

- `outputs/supervision_route_comparison/default/supervision_route_comparison_summary.json`
  - route A rows = `10`
  - route B rows = `5`
  - route C candidate rows = `10`
- `outputs/supervision_route_comparison/default/supervision_next_step_recommendation.json`
  - `chosen_route = C`
  - `chosen_route_name = benchmark_truth_leaning_label_bootstrap`
- `outputs/supervision_route_comparison/default/supervision_route_comparison_summary.json`
  - route C candidate class balance = `{label_0: 6, label_1: 4}`
- `outputs/supervision_route_comparison/repeatability_default/repeatability_summary.json`
  - `all_key_metrics_match = true`

## Remaining Risks

- 当前 comparison 仍建立在同一 local slice 与同一轻量模型上。
- 当前 C 只是 benchmark-truth-leaning，而不是 benchmark ground truth。
- 当前 ranking 证明的是“下一步最值得做什么”，不是“哪条监督路线已经具备研究级可信度”。

## Next Suggested Plan

若 025 完成，下一步建议创建 `.plans/026-benchmark-truth-leaning-label-bootstrap.md`。
