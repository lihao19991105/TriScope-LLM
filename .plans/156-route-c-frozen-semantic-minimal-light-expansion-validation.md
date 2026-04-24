# 156 Route-C Frozen Semantic Minimal Light Expansion Validation

## Background

Stage-155 已完成最小 batched continuous stability recheck，并给出单一结论：在冻结 benchmark truth 与 gate 语义前提下，recoverable/normal/nonrecoverable 三路径均稳定，且无 parser/gate/health/handoff 漂移。

## Why 155 enables minimal light expansion validation

- 155 已确认 recoverable boundary 修正在连续窗口链下可稳定复现。
- 155 已提供可复用的窗口级 case-level 证据，可作为 156 冻结参考。
- 因此 156 可以在不扩模型轴和预算的前提下，做小步轻量扩展，验证规则是否仍局限在 recoverable boundary。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结：不改标签定义，不引入猜测式语义映射。
- gate 语义冻结：不改阈值，不改 PASS/BLOCKED 判定。
- recoverable-boundary 规则冻结：仅复用 148-155 已确认行为。
- parser normalization 范围冻结：保持 conservative normalization + anti-degradation 约束。
- 不扩模型轴、不扩预算、不扩 prompt family、不扩 attack family。

## Goal

在冻结语义与 gate 前提下，完成最小 route_c 轻量扩展验证，并检查：

1. recoverable formatting boundary 继续正确放行。
2. normal path 继续无误伤。
3. nonrecoverable path 继续无漏放。
4. parser / gate / health / handoff 无新漂移。
5. 规则影响范围继续局限在 recoverable boundary。

## Non-goals

- 不做模型轴扩张，不进入 7B/8B。
- 不做预算扩张。
- 不做新 attack family / prompt family。
- 不改 benchmark truth / gate 语义。
- 不做大规模稳定性工程。

## Minimal light expansion validation design

- 规模保持小而精：3 个轻量窗口、18 个 case。
- 路径覆盖：recoverable/normal/nonrecoverable 三路径均覆盖。
- 样例优先复用 155 锚点，仅做必要 controlled-format-variant。
- 与 155 做冻结参考对照；同时对照 153/154/155 summary 快照。

## Light-expansion validation criteria

1. recoverable criteria
- recoverable case 必须保持 pass_formatted_to_parser。
- code-fence-like recoverable case 不得回退到 degeneration_blocked。

2. normal criteria
- normal case 必须保持 pass_raw_to_parser。
- 不得新增 false block。

3. nonrecoverable criteria
- nonrecoverable case 必须保持 degeneration_blocked。
- 不得出现漏放。

4. consistency criteria
- 不得出现 path-level drift 或 parser-source drift。
- 不得出现 handoff contract violation 或 label health anomaly。
- gate_status 必须 PASS，logistic_status 必须 PASS。

## Validation plan

1. 冻结 suite/rules/criteria（M1）。
2. 运行主流程并输出 case-level details + summary + report（M2）。
3. 运行 post-analysis 并给出单一 verdict 与唯一 recommendation（M3）。

## Risks

- 真实 nonrecoverable 锚点仍稀缺，需复用 illumination_0000。
- 轻量扩展仍是受控验证，不能外推为大规模稳定性结论。
- 若出现链路漂移，必须保守降级为 Partially validated 或 Not validated。

## Milestones

- [x] M1: minimal light expansion validation set and criteria frozen
- [x] M2: minimal light expansion validation completed
- [x] M3: single verdict and single recommendation completed

## Completion Notes

- 已生成 3-window / 18-case 的最小轻量扩展验证集并冻结 criteria。
- 主流程产物与后分析产物均已落盘到独立目录。
- 单一 final verdict: Minimal light expansion validated。

## Exit criteria

- 产出 suite/rules/summary/details/report/recommendation/verdict 七类 artifacts。
- 有 case-level 证据，且能对照 153/154/155 before/after。
- 最终仅给出一个 156 verdict 与一个下一步建议。
- 全程不改 benchmark truth 语义、不改 gate 语义、不扩轴线。
