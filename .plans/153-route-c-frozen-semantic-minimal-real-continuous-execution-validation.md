# 153 Route-C Frozen Semantic Minimal Real Continuous Execution Validation

## Background

152 已在冻结语义与 gate 不变前提下完成 minimal continuous execution validation，并给出单一结论 `Minimal continuous execution validated`。但 152 的窗口仍以受控连续验证为主，不等价于“最小真实连续 route_c execution 场景”验证。

153 的任务是把 148 的 recoverable-boundary 收口放入最小真实连续 route_c execution 场景，确认其在真实连续链上仍然成立，且不污染 normal 与 nonrecoverable guardrail。

## Why 152 enables minimal real continuous execution validation

- 152 已证明 recoverable / normal / nonrecoverable 在最小连续窗口下同时成立，并且 gate/logistic/health 一致。
- 152 已给出可审计 case-level 证据与 drift=0 参考，可作为 153 的 frozen baseline。
- 因此 153 不需要扩模型轴、扩预算或新矩阵，只需将验证焦点切换到“真实连续执行锚点 + 最小受控补充”。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结：不改标签定义，不引入猜测式语义映射。
- gate 语义冻结：不改阈值，不改 PASS/BLOCKED 定义。
- recoverable-boundary 规则冻结：仅沿用 148/149/150/151/152 已确认规则。
- parser normalization 能力范围冻结：只允许既有 conservative normalization 与 anti-degradation 允许步骤。
- 不扩模型轴、不扩 budget、不扩 prompt family、不扩 attack family。

## Goal

在冻结语义与 gate 不变前提下，完成最小真实连续 route_c execution 验证，并同时确认：

1. recoverable formatting boundary 在真实连续 execution 上继续稳定 `pass_formatted_to_parser`。
2. normal 路径在真实连续 execution 上继续 `pass_raw_to_parser`，无新增误伤。
3. nonrecoverable 路径在真实连续 execution 上继续 `degeneration_blocked`，无漏放。
4. 真实连续链路上无新增 gate 回退、health 异常、parser source drift、handoff contract violation。

## Non-goals

- 不修改 benchmark truth 语义。
- 不修改 gate 判定逻辑或阈值。
- 不扩大战线到 route_b / 7B/8B / 大规模稳定性工程。
- 不做新主实验矩阵、时间分离 replay 或大批量 rerun。
- 不覆盖 143/144/145/146/147/148/149/150/151/152 既有产物。

## Minimal real continuous execution validation design

- 真实连续锚点：复用稳定 real run `extension_rerun_01` 的连续 prompt 顺序片段（`illumination_0000 -> illumination_0001 -> illumination_0002`）作为单一最小真实连续场景。
- 样例总量：6（小而精）。
- 路径覆盖：
  - recoverable real-continuous: 2（code-fence / language-tag code-fence，均由真实连续锚点 parser-reachable 响应构造）。
  - normal real-continuous guardrail: 2（真实连续锚点原始输入）。
  - nonrecoverable real-continuous guardrail: 2（真实连续锚点 nonrecoverable 原始输入 + near-boundary code-fence variant）。
- 每条样例记录：来源、路径类型、连续窗口信息、真实 prompt_id 锚点、是否真实连续原始输入。

## Real-continuous-execution validation criteria

1. recoverable real-continuous criteria
- 必须保持 `pass_formatted_to_parser` 或等价合法 recoverable handoff。
- 不允许回退到 `degeneration_blocked`。
- 不允许借助语义猜测恢复。

2. normal real-continuous criteria
- 正常样例必须保持 `pass_raw_to_parser`。
- 不允许新增误伤。
- 不允许新增 anti-degradation 过拦截。

3. nonrecoverable real-continuous criteria
- 非可恢复样例必须保持 `degeneration_blocked`。
- 不允许因 recoverable-boundary 修正而漏放。

4. real-continuous consistency criteria
- parser / gate / label health / handoff 语义一致。
- 影响范围局限于 recoverable boundary。
- 不得出现 parser source drift / handoff contract violation / label health anomaly。
- 不得出现连续窗口中的 gate/logistic/health 非预期抖动。

## Validation plan

1. 冻结 153 suite 与 rules（M1）。
2. 在最小真实连续链路上跑 dataset -> gate -> logistic，并输出 case-level details（M2）。
3. 做 minimal collateral real-continuous analysis，输出单一 verdict 与唯一 recommendation（M3）。

## Risks

- 153 是最小真实连续验证，不等价于长期稳定性结论。
- recoverable 真实连续样例通常稀缺，需要极少量 controlled-format variant 才能覆盖 code-fence boundary。
- 若出现连续链路 drift，结论必须保守降级为 `Partially validated` 或 `Not validated`。

## Milestones

- [x] M1: minimal real continuous execution set and criteria frozen
- [x] M2: minimal real continuous execution validation completed
- [x] M3: single verdict and single recommendation completed

## Completion Notes

- 153 使用单一最小真实连续窗口 `real_window_01`，共 6 条样例：recoverable=2、normal=2、nonrecoverable=2。
- 真实连续锚点来自稳定 real run 的连续 prompt 片段：`illumination_0000 -> illumination_0001 -> illumination_0002`。
- focused validation 结果：
  - `recoverable_real_continuous_pass_rate = 1.0`
  - `normal_real_continuous_pass_rate = 1.0`
  - `nonrecoverable_real_continuous_block_rate = 1.0`
  - `mismatch_type_counts = {match: 6}`
- 一致性与副作用检查通过：
  - `gate_status = PASS`
  - `logistic_status = PASS`
  - `path_level_drift_detected = false`
  - `parser_source_drift_detected = false`
  - `handoff_contract_violation_count = 0`
  - `label_health_anomaly_count = 0`
  - `new_false_block_count = 0`
  - `new_leak_count = 0`
- 153 单一结论：`Minimal real continuous execution validated`。
- 153 唯一下一步建议：进入“冻结语义与 gate 不变前提下的最小 route_c 连续真实执行回归线”。

## Exit criteria

- 153 计划文件完整，scope 与非目标边界明确。
- 已产出 suite / rules / summary / details / report / verdict / recommendation 七类 artifacts。
- focused minimal real continuous execution validation 与 minimal collateral analysis 均已完成。
- 最终仅输出一个 verdict 与唯一下一步建议。
- 全程未改 benchmark truth 语义、未改 gate 语义、未做轴向扩张。
