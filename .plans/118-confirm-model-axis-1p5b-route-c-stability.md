# 118 Confirm Model-Axis 1.5B Route-C Stability

## Purpose / Big Picture

117 若确认 route_c 当前是“可执行但极稀”，118 的目标就是判断它到底是“稳定但稀”，还是“只有一次偶然出现了唯一正类”。本计划只做轻量复跑 / 小扰动，不开新模型轴，也不做大矩阵。

## Scope

### In Scope

- 定义 route_c stability confirmation protocol / success criteria / run plan。
- 用固定 subset 做轻量复跑，确认正类是否持续出现、两类是否持续存在、logistic 是否持续成立。
- 输出 run registry / JSONL 结果 / summary / comparison CSV。

### Out of Scope

- 3B / 7B 扩张。
- 新 dataset 轴。
- 大规模 budget expansion。
- route_c full matrix。

## Repository Context

- `.plans/117-analyze-model-axis-1p5b-route-c-sparsity.md`
- `src/eval/model_axis_1p5b_route_c_execution.py`
- `outputs/model_axis_1p5b_route_c_execution/default/*`
- `outputs/model_axis_1p5b_route_c_sparsity/default/*`

## Deliverables

- `.plans/118-confirm-model-axis-1p5b-route-c-stability.md`
- `src/eval/model_axis_1p5b_route_c_stability.py`
- `scripts/build_model_axis_1p5b_route_c_stability.py`
- `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_protocol.json`
- `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_success_criteria.json`
- `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_run_plan.json`
- `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_run_registry.json`
- `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_results.jsonl`
- `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_summary.json`
- `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_comparison.csv`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define route_c stability protocol and success criteria
- [x] Milestone 2: run lightweight stability confirmation and aggregate results
- [x] Milestone 3: README / 收口

## Decision Log

- 决策：118 只在固定 stabilized subset 上做 seed 轻扰动复跑。
  - 原因：当前要判断的是“唯一正类支持点是否稳定”，不是开新选择空间。
- 决策：对 route_c 的“稳定”要求增加一条：唯一正类支持点不能消失。
  - 原因：route_c 当前正类极稀，若唯一正类在轻扰动下消失，就不能称为“稳定但稀”。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_stability.py --help` 可正常显示。
- 产物目录包含 protocol/success_criteria/run_plan/run_registry/results/summary/comparison。
- summary 明确回答：当前 route_c 是“稳定但稀”，还是“本身不稳”。

## Remaining Risks

- 即便稳定性确认通过，当前正类厚度仍然很薄，统计结论依然受限。
- route_c 仍然是 benchmark-truth-leaning proxy，不是 benchmark ground truth。

## Outcome Snapshot

- 118 已完成 3 个轻量 rerun 场景（seed=42/43/44）。
- 所有 run 均保持：
  - `used_local_weights=true`
  - `entered_model_inference=true`
  - `class_balance={label_0:23,label_1:1}`
  - `logistic PASS`
  - `csqa-pilot-021__targeted` 持续作为唯一正类 anchor 出现
- 当前结论：
  - `stability_established=true`
  - `stability_characterization=stable_but_sparse`
- 当前结果快照见：
  - `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_summary.json`
  - `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_run_registry.json`
  - `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_results.jsonl`
  - `outputs/model_axis_1p5b_route_c_stability/default/route_c_stability_comparison.csv`

## Next Suggested Plan

若 118 确认 `stable_but_sparse=true`，创建 `.plans/119-route-c-budget-expansion-or-selection-refinement.md`。
