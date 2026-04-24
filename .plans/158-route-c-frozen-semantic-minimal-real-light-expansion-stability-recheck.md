# 158 Route-C Frozen Semantic Minimal Real Light Expansion Stability Recheck

## Background

若 157-A 的单一 verdict 为 Minimal real light expansion validated，则 158 进入冻结语义与 gate 不变前提下的最小 route_c 轻量真实扩展稳定性复检线。

## Why 157 enables minimal real light expansion stability recheck

- 157-A 已在轻量真实扩展场景验证三路径基本正确性。
- 157-A 已形成稳定可复用 case 结构，可用于多窗口复检。
- 因此 158 在不扩张前提下进行更高一层但仍克制的稳定性复检。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结。
- gate 语义冻结。
- recoverable-boundary 规则冻结。
- parser normalization 范围冻结。
- 不扩模型轴、预算、prompt family、attack family。

## Goal

在多窗口稳定性复检中继续验证：

1. recoverable boundary 放行持续稳定。
2. normal path 无误伤。
3. nonrecoverable path 无漏放。
4. parser/gate/health/handoff/source 无新增漂移。

## Non-goals

- 不做模型轴扩张或预算扩张。
- 不引入新语义映射。
- 不做大规模稳定性工程。

## Stability recheck design

- 规模仍受控：4 个窗口、20 个 case。
- 样例优先复用 157 的真实轻量扩展结构，新增一个最小 recheck 窗口。
- 继续保持 recoverable/normal/nonrecoverable 三路径覆盖。
- 与 157 进行冻结 reference 对照，同时保留 155/156/157 before/after 快照。

## Stability recheck criteria

- recoverable 继续 pass_formatted_to_parser。
- normal 继续 pass_raw_to_parser 且无新 false block。
- nonrecoverable 继续 degeneration_blocked 且无漏放。
- path-level drift / parser-source drift / handoff-contract / label-health 全部为零。
- gate/logistic 必须 PASS。

## Validation plan

1. 冻结 158 suite/rules/criteria（M1）。
2. 运行 158 主流程并输出 case-level 证据（M2）。
3. 运行 158 post-analysis 并输出单一 verdict + 唯一 recommendation（M3）。

## Risks

- 真实 nonrecoverable 锚点单一，稳定性结论仍是受控范围。
- 158 结果不能替代更大规模泛化验证。

## Milestones

- [x] M1: minimal real light expansion stability recheck set and criteria frozen
- [x] M2: minimal real light expansion stability recheck completed
- [x] M3: single verdict and single recommendation completed

## Completion Notes

- 已完成 4-window / 20-case 的最小真实轻量扩展稳定性复检配置与执行。
- 主流程与后分析独立产物均已落盘。
- 单一 final verdict: Minimal real light expansion stability recheck validated。

## Exit criteria

- 产出 suite/rules/summary/details/report/recommendation/verdict 七类 artifacts。
- 形成单一 final verdict 与唯一 recommendation。
- 不覆盖 156/157 或更早阶段结果。
