# 159 Route-C Frozen Semantic Minimal Real Usage Validation

## Background

Stage-158 已完成最小真实轻量扩展稳定性复检，并给出单一结论：在冻结 benchmark truth 与 gate 语义前提下，recoverable/normal/nonrecoverable 三路径继续稳定。

## Why 158 enables minimal real usage validation

- 158 已覆盖多窗口复检并确认无链路漂移。
- 158 已形成可复用锚点和 before/after 参考快照。
- 因此 159 可在不扩轴线前提下进入更接近真实 route_c 使用方式的最小验证层。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结，不改标签定义与映射。
- gate 语义冻结，不改阈值，不改 PASS/BLOCKED 定义。
- recoverable-boundary 规则冻结，不扩大 formatter 能力边界。
- parser/handoff/label-health 语义冻结，不做推断性放宽。
- 不扩模型轴、不扩预算、不扩 prompt family、不扩 attack family。

## Goal

在更接近真实 route_c 使用方式但仍克制的最小场景中验证：

1. recoverable formatting boundary 继续正确放行。
2. normal path 继续无误伤。
3. nonrecoverable path 继续无漏放。
4. parser/gate/label-health/handoff 一致性保持。
5. 规则影响范围仍局限在 recoverable boundary。

## Non-goals

- 不做模型轴扩张或预算扩张。
- 不进入新 attack/prompt family。
- 不进入 route_b 扩展。
- 不开启主实验矩阵。

## Minimal real usage validation design

- 验证集由 5 个窗口构成，覆盖 recoverable/normal/nonrecoverable 三路径。
- 尽量复用 156-158 锚点，新增仅限 controlled-format-variant 最小补充。
- 每个窗口固定 case 顺序，保持可审计和可重跑。

## Real-usage validation criteria

- recoverable: 必须 pass_formatted_to_parser。
- normal: 必须 pass_raw_to_parser。
- nonrecoverable: 必须 degeneration_blocked。
- 无 path-level drift / parser-source drift。
- 无 handoff-contract violation / label-health anomaly。
- gate_status 与 logistic_status 必须 PASS。

## Validation plan

1. 冻结 suite/rules/criteria。
2. 运行主流程并导出 case-level details + summary + report。
3. 运行 post-analysis 输出单一 verdict 和唯一 recommendation。

## Risks

- nonrecoverable 真实锚点仍偏集中，外推范围有限。
- 若出现链路级漂移，必须保守降级为 Partially validated 或 Not validated。

## Milestones

- [x] M1: minimal real usage validation set and criteria frozen
- [x] M2: minimal real usage validation completed
- [x] M3: single verdict and single recommendation completed

## Exit criteria

- 产出 suite/rules/summary/details/report/recommendation/verdict 七类 artifacts。
- 形成单一 final verdict 与唯一 next-step recommendation。
- 不覆盖 158 及更早阶段产物。
