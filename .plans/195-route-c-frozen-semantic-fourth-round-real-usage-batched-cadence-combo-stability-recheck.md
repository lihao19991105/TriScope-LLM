# 195 Route-C Frozen Semantic Fourth-Round Real Usage Batched-Cadence Combo Stability Recheck

## Background

本阶段按 194 的单一 final verdict 自动进入，当前分支为 validated 后的第四轮真实使用 batched-cadence combo 稳定性复检线。

## Goal

执行第四轮更高层真实使用 batched-cadence combo stability recheck，并输出单一 verdict 与唯一 recommendation。

## Frozen scope

- benchmark truth / gate 语义冻结。
- 不扩模型轴、budget、prompt family、attack family。
- 仅允许小步、局部、可审计推进。

## Validation design

- 使用 stage-195 独立窗口集合（41 windows，205 cases）。
- 复用真实运行锚点与最小 controlled-format-variant。

## Validation criteria

- recoverable: pass_formatted_to_parser
- normal: pass_raw_to_parser
- nonrecoverable: degeneration_blocked
- gate_status=PASS 且 logistic_status=PASS
- 无 drift / handoff contract violation / label-health anomaly

## Risks

- 组合稳定性层可能引入局部不稳。

## Milestones

- [x] M1: validation set and criteria frozen
- [x] M2: stage validation completed
- [x] M3: single verdict and single recommendation completed

## Exit criteria

- 产出 suite/rules/summary/details/report/recommendation/verdict。
- 单一 final verdict，唯一 recommendation。
