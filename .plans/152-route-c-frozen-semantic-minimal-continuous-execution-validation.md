# 152 Route-C Frozen Semantic Minimal Continuous Execution Validation

## Background

151 已完成最小真实 execution 验证，并给出单一结论 `Minimal real execution validated`。该结论确认 recoverable-boundary 修正在最小真实链路上成立，但 151 重点是单次最小真实 execution，并不等价于连续 route_c execution 窗口验证。

因此 152 的唯一任务是在冻结语义与 gate 不变前提下，进入最小、受控、连续 execution 场景，验证局部修正在连续链路上仍然只影响 recoverable boundary，不污染 normal 与 nonrecoverable guardrail。

## Why 151 enables minimal continuous execution validation

- 151 已给出可审计的 case-level 证据链与零 mismatch 结论，可作为连续窗口验证的直接锚点。
- 151 已覆盖 recoverable / normal / nonrecoverable 三类路径，并明确 code-fence-like recoverable handoff 可通过。
- 152 可在不扩模型轴、不扩预算、不改语义的前提下，复用 151 证据样例构造最小连续窗口，专注检查 path-level drift / gate 回退 / label health 异常。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结：不改标签定义，不引入猜测式语义映射。
- gate 语义冻结：不改阈值，不改 PASS/BLOCKED 定义。
- recoverable-boundary 规则冻结：仅沿用 148 已确认的收口规则与 149/150/151 冻结参考。
- 不扩模型轴、不扩 budget、不扩 prompt family、不扩 attack family。
- 只做最小 route_c 连续 execution 验证，不做新稳定性工程扩张。

## Goal

在冻结语义与 gate 不变前提下，完成最小 route_c 连续 execution 验证，并同时确认：

1. recoverable formatting boundary 在连续 execution 上继续正确放行。
2. 正常路径在连续 execution 上继续不被误伤。
3. 非可恢复路径在连续 execution 上继续稳定 blocked。
4. 连续链路未引入新的 path-level drift、gate 回退或 label health 异常。

## Non-goals

- 不修改 benchmark truth 语义。
- 不修改 gate 阈值或 gate 判定逻辑。
- 不扩模型轴、预算、prompt family、attack family。
- 不做大规模 rerun、时间分离 replay 或主实验矩阵扩张。
- 不把 152 变成新的大稳定性工程。

## Minimal continuous execution validation design

- 连续窗口设计：使用 2 个最小连续窗口（window_01, window_02），每个窗口各含 recoverable / normal / nonrecoverable 1 条，共 6 条样例。
- 样例来源：优先复用 151 真实链路锚点与 150/149 冻结参考，仅保留必要的 code-fence-like controlled variants。
- 窗口组成：
  - window_01: recoverable code-fence + real normal + real nonrecoverable
  - window_02: recoverable language-tag code-fence + second real normal + near-boundary nonrecoverable code-fence
- 每条样例均记录：来源类型、路径类型、连续窗口编号、窗口顺序、是否真实 execution 原始输入。

## Continuous-execution validation criteria

1. recoverable continuous-execution criteria
- recoverable case 必须保持 `pass_formatted_to_parser` 或等价合法 recoverable handoff。
- 不允许回退到 `degeneration_blocked`。
- 不允许借助语义猜测完成恢复。

2. normal continuous-execution criteria
- normal case 必须保持正常 path（`pass_raw_to_parser`）。
- 不允许新增误伤。
- 不允许新增不必要的 anti-degradation 过拦截。

3. nonrecoverable continuous-execution criteria
- nonrecoverable case 必须保持 blocked（`degeneration_blocked`）。
- 不允许因 recoverable-boundary 修正产生漏放。

4. continuous-execution consistency criteria
- parser / gate / label health / handoff 语义保持一致。
- 影响范围必须局限在 recoverable boundary。
- 不得在连续窗口中出现新的 path-level drift。
- 不得出现 gate 回退、logistic 非预期抖动或 label health 异常。

## Validation plan

1. 冻结最小连续窗口 suite 与 rules（M1）。
2. 运行完整最小连续 execution 链路（dataset -> gate -> logistic），产出 case-level details 与 summary（M2）。
3. 执行最小 collateral continuous-execution analysis，输出单一 verdict 与唯一下一步建议（M3）。

## Risks

- 152 是最小连续窗口验证，不等价于长期稳定性或大规模真实连续实验。
- 连续窗口仅 2 个，覆盖受控且克制，结论不自动外推到未覆盖 wrapper 家族。
- 若出现连续窗口内部漂移，必须保守降级为 `Partially validated` 或 `Not validated`。

## Milestones

- [x] M1: minimal continuous execution set and criteria frozen
- [x] M2: minimal continuous execution validation completed
- [x] M3: single verdict and single recommendation completed

## Completion Notes

- 152 采用 2-window 最小连续执行设计（window_01 / window_02），共 6 条样例，覆盖 recoverable=2、normal=2、nonrecoverable=2。
- continuous-execution summary 显示：
  - `recoverable_continuous_pass_rate = 1.0`
  - `normal_continuous_pass_rate = 1.0`
  - `nonrecoverable_continuous_block_rate = 1.0`
  - `gate_status = PASS`
  - `logistic_status = PASS`
- `mismatch_type_counts = {match: 6}`，无 recoverable 回退、无 normal 误伤、无 nonrecoverable 漏放。
- 连续窗口一致性检查通过：
  - `path_level_drift_detected = false`
  - `parser_source_drift_detected = false`
  - `handoff_contract_violation_count = 0`
  - `label_health_anomaly_count = 0`
- 最小 collateral continuous-execution analysis 为：
  - `new_false_block_count = 0`
  - `new_leak_count = 0`
  - `real_execution_correct_but_continuous_unstable = false`
- 152 单一结论：`Minimal continuous execution validated`。
- 152 唯一下一步建议：进入冻结语义与 gate 不变前提下的最小 route_c 真实连续执行验证线。

## Exit criteria

- 152 计划文件完整且可恢复。
- 已产出 suite / rules / summary / details / report / verdict / recommendation 七类 artifacts。
- 已完成 focused minimal continuous execution validation 与 minimal collateral continuous-execution analysis。
- 最终仅输出一个 152 verdict 与唯一下一步建议。
- 全程未改 benchmark truth 语义、未改 gate 语义、未做轴向扩张。
