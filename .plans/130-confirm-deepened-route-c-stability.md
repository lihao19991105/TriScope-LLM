# 130 Confirm Deepened Route-C Stability

## Purpose / Big Picture

129 已证明 deepened candidate 可以真实执行并保持两类，但它当前只守住 refined floor，尚未证明能替代 anchor-aware baseline。130 的目标是验证 deepened 结果是否可重复，并给出明确结论：`stable_enough_to_keep` 或 `should_fall_back_to_anchor_baseline`。

## Scope

### In Scope

- 定义 deepened stability protocol / success criteria / run plan。
- 在固定 deepened subset 上做轻量 rerun。
- 输出 registry / results / summary / comparison。

### Out of Scope

- 3B / 7B。
- dataset 轴。
- blind budget expansion。
- fusion 同轴扩张。

## Repository Context

- `.plans/129-deepened-route-c-candidate-execution.md`
- `.plans/126-confirm-anchor-aware-route-c-stability.md`
- `src/eval/model_axis_1p5b_route_c_deepened_execution.py`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/*`

## Deliverables

- `.plans/130-confirm-deepened-route-c-stability.md`
- `src/eval/model_axis_1p5b_route_c_deepened_stability.py`
- `scripts/build_model_axis_1p5b_route_c_deepened_stability.py`
- `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_protocol.json`
- `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_success_criteria.json`
- `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_run_plan.json`
- `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_run_registry.json`
- `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_results.jsonl`
- `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_summary.json`
- `outputs/model_axis_1p5b_route_c_deepened_stability/default/route_c_deepened_stability_comparison.csv`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define deepened stability protocol and success criteria
- [x] Milestone 2: run deepened stability confirmation and aggregate results
- [x] Milestone 3: acceptance / README / 收口

## Surprises & Discoveries

- deepened 在 3 次 rerun 中完全稳定地维持 1/8 floor，但三次都未达到 anchor 1/6，且无新增正类支持。

## Decision Log

- 决策：130 复用 126 的轻量 rerun 结构，但 decision rule 改为“深度路线是否值得保留，还是应回退 anchor-aware baseline”。
  - 原因：当前关键分歧不在可执行性，而在是否有 baseline 级新增价值。

## Plan of Work

先定义 protocol 和 success criteria，明确可接受波动与回退条件。随后执行 3 次轻量 rerun，统计 deepened 的两类保持、density floor、anchor 保留和 logistic 通过情况，最终给出 baseline 决策。

## Concrete Steps

1. 新增 deepened stability 模块与 CLI。
2. 运行 deepened stability 脚本产出 protocol 和 run artifacts。
3. 汇总 comparison 与 baseline 决策。
4. 更新 README 最小命令与恢复点。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_deepened_stability.py --help` 正常显示。
- 必须输出 protocol / success_criteria / run_plan / run_registry / results / summary / comparison。
- summary 必须明确回答：
  - deepened 是否持续保持至少两类
  - density 是否持续不低于 refined floor
  - reference anchor 是否持续保留
  - logistic 是否持续 PASS
  - `baseline_decision` 是 `stable_enough_to_keep` 还是 `should_fall_back_to_anchor_baseline`

## Idempotence and Recovery

- 脚本可重复运行；同一输出目录会覆盖摘要类产物。
- rerun 中断后可直接重跑同一命令恢复完整结果。

## Outputs and Artifacts

- `outputs/model_axis_1p5b_route_c_deepened_stability/default/*`

## Remaining Risks

- deepened 可能稳定但持续低于 anchor density。
- 即使稳定，deepened 可能仍不提供新增正类支持。

## Outcome Snapshot

- 130 已完成 3 个 deepened rerun 场景（seed=42/43/44）。
- 所有 run 均保持：
  - `used_local_weights = true`
  - `entered_model_inference = true`
  - `class_balance = {label_0: 7, label_1: 1}`
  - `deepened_density = 0.125`
  - `density_not_below_refined_floor = true`
  - `reference_anchor_preserved = true`
  - `logistic PASS`
- 但所有 run 同时满足：
  - `density_not_below_anchor = false`
  - `positive_support_count = 1`（无新增）
- 当前结论：
  - `stability_established = true`
  - `baseline_decision = should_fall_back_to_anchor_baseline`

## Next Suggested Plan

- 进入 `.plans/131-post-deepened-route-c-analysis-and-baseline-decision.md` 做四层 baseline 统一决策。