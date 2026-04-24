# 166 Route-C Frozen Semantic Next-Level Real Usage Validation

## Background

159-165 全链在冻结 benchmark truth 与 gate 语义前提下连续通过，已证明 recoverable-boundary 修正能在最小真实使用链稳定成立。

## Why 165 enables next-level real usage validation

- 165 已完成上一轮真实使用链最终收口复检。
- 159-165 已连续给出单一 validated verdict，形成稳定前置锚点。
- 因此可在不扩模型轴与预算前提下进入“更高一层但仍受控”的真实使用验证。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结，不改标签定义与语义映射。
- gate 语义冻结，不改阈值，不改 PASS/BLOCKED 定义。
- recoverable-boundary 规则作用域冻结，不扩大 formatter 能力范围。
- parser/handoff/label-health 语义冻结，不引入推断式放宽。
- 不扩模型轴、不扩预算、不扩 prompt family、不扩 attack family。

## Goal

验证在更高一层真实使用条件（较 165 增一层覆盖）下，recoverable/normal/nonrecoverable 三路径与 parser-gate-health-handoff 一致性仍成立，并保持规则影响范围仅限 recoverable boundary。

## Non-goals

- 不进入 7B/8B 轴，不开启主实验矩阵。
- 不扩 route_b，不新增 attack/prompt family。
- 不做大而泛稳定性工程。

## Next-level real usage validation design

- 使用 stage-166 专属窗口集合（12 windows，较 stage-165 增 1 window）。
- 优先复用真实执行锚点，仅保留最小 controlled-format-variant。
- 每窗口固定 recoverable/normal/nonrecoverable 排布，保证可审计。

## Validation criteria

- recoverable: pass_formatted_to_parser。
- normal: pass_raw_to_parser。
- nonrecoverable: degeneration_blocked。
- gate_status=PASS 且 logistic_status=PASS。
- 无 handoff_contract_violation / label_health_anomaly。
- 无 path-level drift / parser-source drift。

## Validation plan

1. 冻结 suite/rules 与 stage-166 criteria。
2. 运行 stage-166 主流程并导出 suite/rules/summary/details/report。
3. 运行 stage-166 post-analysis，输出 recommendation/verdict。
4. 将 stage-166 单一 verdict 作为 167 唯一分支输入。

## Risks

- 更高层窗口仍是受控真实使用近似，外推性有限。
- 若出现轻微漂移，需保守进入压缩或收口分支。

## Milestones

- [x] M1: next-level real usage validation set and criteria frozen
- [x] M2: next-level real usage validation completed
- [x] M3: single verdict and single recommendation completed

## Exit criteria

- 产出 suite/rules/summary/details/report/recommendation/verdict 七类 artifacts。
- 单一 final verdict 为三选一：Next-level real usage validated / Partially validated / Not validated。
- recommendation 唯一且可直接驱动 167 自动分支。
