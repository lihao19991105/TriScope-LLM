# 157-A Route-C Frozen Semantic Minimal Real Light Expansion Validation

## Background

156 的目标是在冻结语义与 gate 下完成最小轻量扩展验证。若 156 给出单一 verdict 为 Minimal light expansion validated，则 157 进入最小 route_c 轻量真实扩展验证线。

## Why 156 enables minimal real light expansion validation

- 156 已确认轻量扩展链在 recoverable/normal/nonrecoverable 三路径上保持正确性。
- 156 已形成可复用 case-level 证据与冻结参考，可用于更接近真实使用方式的下一步验证。
- 因此 157-A 可在不扩轴线前提下提升真实输入占比，做最小真实轻量扩展验证。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结。
- gate 语义冻结。
- recoverable-boundary 规则冻结。
- parser normalization 范围冻结。
- 不扩模型轴、预算、prompt family、attack family。

## Goal

在更接近真实 route_c 使用方式的轻量场景中验证：

1. recoverable 继续正确 handoff。
2. normal 继续无误伤。
3. nonrecoverable 继续无漏放。
4. parser/gate/health/handoff/source 无新异常。

## Non-goals

- 不做模型轴扩张。
- 不做预算扩张。
- 不做新实验矩阵。
- 不改 benchmark truth / gate。

## Minimal real light expansion validation design

- 规模保持最小：3 个窗口、15 个 case。
- 路径覆盖三类路径，提升 real 输入占比。
- 非必要不引入新的 controlled variant。
- 与 156 做冻结 reference 对照，同时参考 154/155/156 快照。

## Light-expansion validation criteria

- recoverable 必须 pass_formatted_to_parser。
- normal 必须 pass_raw_to_parser 且无新 false block。
- nonrecoverable 必须 degeneration_blocked 且无漏放。
- path-level drift / parser-source drift / handoff-contract / label-health 全部为零。
- gate/logistic 必须保持 PASS。

## Validation plan

1. 冻结 157-A suite/rules/criteria（M1）。
2. 运行 157-A 主流程并完成 case-level 证据输出（M2）。
3. 运行 157-A post-analysis 并输出单一 verdict + 唯一 recommendation（M3）。

## Risks

- nonrecoverable 真实锚点依赖 illumination_0000，覆盖广度有限。
- 157-A 仍是克制验证，不等价于大规模部署结论。

## Milestones

- [x] M1: minimal real light expansion validation set and criteria frozen
- [x] M2: minimal real light expansion validation completed
- [x] M3: single verdict and single recommendation completed

## Completion Notes

- 已完成 3-window / 15-case 的最小真实轻量扩展验证集与 criteria 冻结。
- 主流程与后分析独立产物均已生成。
- 单一 final verdict: Minimal real light expansion validated。

## Exit criteria

- 产出 suite/rules/summary/details/report/recommendation/verdict 七类 artifacts。
- 形成单一 final verdict 与唯一 recommendation。
- 不覆盖 156 或更早阶段结果。
