# 112 Confirm Model-Axis 1.5B Route-B Stability

## Purpose / Big Picture

111 已确认 1.5B route_b 从可运行推进到可分析，但当前 class balance 仍偏斜（30/2）。112 的目标是在不扩新实验轴的前提下，用最小复跑与轻微扰动确认 stabilized route_b 不是一次性偶然成功，而是可复现、可作为后续 route_c portability 的基线。

## Scope

### In Scope

- 定义 route_b stability confirmation protocol（seed、target-budget 小扰动、成功标准）。
- 执行多次稳定性确认 run 并聚合结果。
- 输出 run registry / JSONL 结果 / summary / comparison CSV。
- 若稳定性成立，给出推进 113 的依据。

### Out of Scope

- 3B / 7B 模型切换。
- fusion 同轴扩张。
- dataset / proxy substrate 扩容。
- 新训练主线。

## Repository Context

- `.plans/109-stabilize-model-axis-1p5b-route-b-label-balance.md`
- `.plans/110-rerun-model-axis-1p5b-route-b-stable-execution.md`
- `.plans/111-post-stabilized-model-axis-1p5b-analysis.md`
- `src/eval/model_axis_1p5b_route_b_stable_execution.py`
- `outputs/model_axis_1p5b_route_b_stable_execution/default/*`

## Deliverables

- `.plans/112-confirm-model-axis-1p5b-route-b-stability.md`
- `src/eval/model_axis_1p5b_route_b_stability.py`
- `scripts/build_model_axis_1p5b_route_b_stability.py`
- `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_protocol.json`
- `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_success_criteria.json`
- `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_run_plan.json`
- `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_run_registry.json`
- `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_results.jsonl`
- `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_summary.json`
- `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_comparison.csv`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define stability confirmation protocol and success criteria
- [x] Milestone 2: run stability confirmation and aggregate results
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：112 采用小规模 protocol（固定 route_b、1.5B、本地权重），只对 seed 和 target_budget 做轻微扰动。
  - 原因：当前目标是确认稳定性，不是开新实验轴。
- 决策：112 至少覆盖 `target_budget=32` 的复跑和 `31/33` 的邻域扰动。
  - 原因：直接对应 110 现有配置，且可检验对小扰动的脆弱性。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_b_stability.py --help` 可正常显示。
- 产物目录包含 protocol/success_criteria/run_plan/run_registry/results/summary/comparison。
- summary 明确回答：是否持续两类、是否持续 logistic PASS、是否出现回退。

## Remaining Risks

- 即便小扰动稳定，仍不代表更大预算或不同数据切片一定稳定。
- 类别偏斜若进一步放大，后续统计波动仍可能影响结论可信度。

## Outcome Snapshot

- 112 已完成 4 个轻量确认场景（seed=42/43，target_budget=31/32/33）。
- 所有 run 均保持 `used_local_weights=true`、`entered_model_inference=true`、`class_balance` 至少两类、`logistic PASS`。
- 当前结论：`stability_established=true`，可作为 113 route_c portability 的基线。
- 当前结果快照见：
  - `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_summary.json`
  - `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_run_registry.json`
  - `outputs/model_axis_1p5b_route_b_stability/default/route_b_stability_comparison.csv`
- 恢复时优先读取 `route_b_stability_run_registry.json`：
  - 它已经把 4 个确认场景各自的 `run_dir / run_summary / metrics / route_b_summary / route_b_logistic_summary` 全部串起来了。

## Next Suggested Plan

若 112 判定稳定性成立，创建 `.plans/113-route-c-portability-bootstrap.md` 并推进 route_c portability precheck。
