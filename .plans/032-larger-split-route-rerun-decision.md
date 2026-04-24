# 032 Larger Split Route Rerun Decision

## Purpose / Big Picture

031 会把 shared labeled substrate 从 10-row 再抬到 20-row。032 的目标是在这个 larger split 已存在且 bridge 兼容性明确之后，判断下一步应该优先 rerun route B 还是 route C。

## Scope

### In Scope

- larger split 条件下的 rerun 优先级比较
- route B / route C tradeoff matrix
- next-step recommendation
- acceptance / repeatability / README / 收口

### Out of Scope

- 实际 rerun route B
- 实际 rerun route C
- 更大模型 / 更大数据

## Repository Context

本计划主要衔接：

- `outputs/larger_labeled_split_bootstrap/*`
- `outputs/more_natural_label_bootstrap/*`
- `outputs/expanded_route_c_bootstrap/*`
- `outputs/expanded_supervision_comparison/*`
- `src/eval/`
- `scripts/`

## Deliverables

- `.plans/032-larger-split-route-rerun-decision.md`
- `src/eval/larger_split_route_rerun_decision.py`
- `scripts/build_larger_split_route_rerun_decision.py`
- `src/eval/larger_split_route_rerun_decision_checks.py`
- `scripts/validate_larger_split_route_rerun_decision.py`
- `larger_split_route_rerun_comparison.json`
- `larger_split_route_rerun_tradeoff_matrix.csv`
- `larger_split_route_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: larger split rerun tradeoff comparison
- [x] Milestone 2: next-step recommendation / acceptance / README / 收口

## Surprises & Discoveries

- 在 larger split 条件下，route C 仍然是更 truth-leaning 的 supervision path，但它已经在 10-row substrate 上拿到了 expanded rerun 结果。
- route B 目前最大的短板不是 supervision semantics 本身，而是还没有在 expanded / larger substrate 上对称 rerun。
- 因此 larger split 之下最有信息增益的下一步，不一定是“继续做更强 truth path”，而可能是先让 route B 在更大的 shared substrate 上补齐对称比较。

## Decision Log

- 决策：032 推荐 larger split 上优先 rerun route B。
  - 原因：route C 已经在 10-row substrate 上完成了 expanded rerun，而 route B 还没有获得对称机会；在 larger split 上先 rerun B，能带来更高的 comparative information gain。
  - 影响范围：next-step recommendation、后续计划建议。

## Plan of Work

先统一读取 031 的 larger split artifact、024 的 route B artifact、029 的 expanded route C artifact 和 030 的 comparison artifact。然后把 route B 与 route C 在 larger split 上的预期收益、现实性、成本、信息增益放到统一矩阵里。最后给出 rerun priority recommendation，并补 validator 与 README。

## Validation and Acceptance

- `build_larger_split_route_rerun_decision.py --help` 可正常显示
- `validate_larger_split_route_rerun_decision.py --help` 可正常显示
- 至少生成：
  - `larger_split_route_rerun_comparison.json`
  - `larger_split_route_rerun_tradeoff_matrix.csv`
  - `larger_split_route_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

032 的 build / validate 都是幂等的；重复运行会覆盖同名输出。中断后可直接重跑。

## Remaining Risks

- rerun priority recommendation 仍然建立在 pilot-level substrate 和轻量模型前提上。
- 推荐先 rerun B 并不意味着 B 一定会优于 C，只意味着它在当前阶段拥有更高的信息增益。

## Next Suggested Plan

若 032 完成，下一步建议直接在 larger split 上 rerun route B，并把它与 expanded route C 做真正对称比较。
