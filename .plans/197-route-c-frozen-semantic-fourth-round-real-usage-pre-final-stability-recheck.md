# 197 Route-C Frozen Semantic Fourth-Round Real Usage Pre-Final Stability Recheck

## Background

本阶段按 196 的单一 final verdict 自动进入，当前分支为 validated 后的第四轮真实使用 pre-final 稳定性复检线。

## Goal

执行第四轮更高层真实使用 pre-final stability recheck，并输出单一 verdict 与唯一 recommendation。

## Frozen scope

- benchmark truth / gate 语义冻结。
- 不扩模型轴、budget、prompt family、attack family。
- 仅允许小步、局部、可审计推进。

## Validation design

- 使用 stage-197 独立窗口集合（43 windows，215 cases）。
- 复用真实运行锚点与最小 controlled-format-variant。

## Validation criteria

- recoverable: pass_formatted_to_parser
- normal: pass_raw_to_parser
- nonrecoverable: degeneration_blocked
- gate_status=PASS 且 logistic_status=PASS
- 无 drift / handoff contract violation / label-health anomaly

## Risks

- pre-final 层可能暴露更细粒度不稳。

## Milestones

- [x] M1: validation set and criteria frozen
- [x] M2: stage validation completed
- [x] M3: single verdict and single recommendation completed

## Exit criteria

- 产出 suite/rules/summary/details/report/recommendation/verdict。
- 单一 final verdict，唯一 recommendation。
