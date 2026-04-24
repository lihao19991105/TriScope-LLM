# 113 Route-C Portability Bootstrap

## Purpose / Big Picture

112 已确认 1.5B stabilized route_b 在小范围复跑和预算扰动下保持非单类且 logistic PASS。113 的目标是在不直接展开全量 route_c 执行的前提下，完成 1.5B route_c portability 合同、ready 输入与 precheck/dry-run 验证，为后续 route_c minimal execution 建立明确入口。

## Scope

### In Scope

- 定义 route_c portability contract、selection 与 readiness。
- materialize 1.5B route_c portability 轻量输入。
- 运行 route_c portability precheck / dry-run 并输出 module/cell/run 状态。

### Out of Scope

- 3B / 7B 扩展。
- fusion 同轴扩张。
- dataset/proxy substrate 扩容。
- route_c 全量大规模执行。

## Repository Context

- `.plans/112-confirm-model-axis-1p5b-route-b-stability.md`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`
- `outputs/model_axis_1p5b_route_b_stability/default/*`
- `outputs/model_axis_1p5b_dry_run/default/materialized_model_axis_1p5b_dry_run_inputs/*`

## Deliverables

- `.plans/113-route-c-portability-bootstrap.md`
- `src/eval/model_axis_1p5b_route_c_portability.py`
- `scripts/build_model_axis_1p5b_route_c_portability.py`
- `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_contract.json`
- `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_selection.json`
- `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_readiness_summary.json`
- `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_run_summary.json`
- `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_module_status.json`
- `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_cell_status.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define route_c portability contract and readiness bridge
- [x] Milestone 2: run route_c portability precheck/dry-run and emit status artifacts
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：113 采用 route_c 轻量 precheck/dry-run，而不是直接全量 rerun。
  - 原因：当前目标是 portability bootstrap，不是 route_c 性能评估。
- 决策：113 使用 112 已确认稳定的 route_b 作为 gate，先确认 route_c 在 1.5B 下 contract-compatible 与 ready-run 条件。
  - 原因：与 111 recommendation 保持一致，降低跨轴风险。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_portability.py --help` 可正常显示。
- 产物目录包含 contract/selection/readiness/run_summary/module_status/cell_status。
- 明确回答：contract-compatible、ready-dry-run、ready-run 是否成立。

## Remaining Risks

- portability precheck 通过不等于 route_c 全量稳定。
- route_c 合同包含 labeled_illumination 分支，未来仍可能引入额外波动。

## Outcome Snapshot

- 113 已产出 contract/selection/readiness/run/module/cell 全套 portability artifact。
- `contract_compatible=true`、`ready_dry_run=true`、`ready_run=true` 在 1.5B 下均成立。
- 但当前 portability precheck 执行仍为 `PARTIAL`，失败点为 labels（`Benchmark-truth-leaning dataset must contain at least two classes.`）。
- 当前具体快照为：
  - `selected_base_sample_count = 12`
  - `selected_labeled_contract_count = 24`
  - `selection_diagnostics.expected_reference_contract_class_balance = {label_0: 15, label_1: 9}`
  - 但真实 precheck 仍在小预算子集上塌成单类，因此 `execution_status = PRECHECK_FAILED`
- 当前结论：route_c portability bridge 已建立，但 route_c minimal execution 前仍需先消解小预算合同下的标签单类风险。
- 当前恢复入口已经明确：
  - contract: `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_contract.json`
  - readiness: `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_readiness_summary.json`
  - materialized inputs: `outputs/model_axis_1p5b_route_c_portability/default/materialized_route_c_portability_inputs/`
  - run snapshot: `outputs/model_axis_1p5b_route_c_portability/default/route_c_portability_run_summary.json`

## Next Suggested Plan

若继续推进，优先不是盲目放大 route_c，而是先稳定 route_c 小预算合同下的标签两类可分性；完成后再进入受控的 route_c minimal execution 计划（仍保持 1.5B 和小规模约束）。
