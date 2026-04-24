# 190 Route-C Frozen Semantic Fourth-Round Real Usage Batched Regression

## Background

本阶段按 189 的单一 final verdict 自动进入，当前分支为 validated 后的第四轮真实使用 batched 回归线。

## Goal

执行第四轮更高层真实使用 batched regression，并输出单一 verdict 与唯一 recommendation。

## Frozen scope

- benchmark truth / gate 语义冻结。
- 不扩模型轴、budget、prompt family、attack family。
- 仅允许小步、局部、可审计推进。

## Validation design

- 使用 stage-190 独立窗口集合（36 windows，180 cases）。
- 复用真实运行锚点与最小 controlled-format-variant。
- 输出 case-level details 与 before/after 参考快照。

## Validation criteria

- recoverable: pass_formatted_to_parser
- normal: pass_raw_to_parser
- nonrecoverable: degeneration_blocked
- gate_status=PASS 且 logistic_status=PASS
- 无 drift / handoff contract violation / label-health anomaly

## Risks

- batched 组合可能引入局部路径漂移。
- 若 guardrail 失稳，需要保守进入压缩或收口分支。

## Milestones

- [x] M1: validation set and criteria frozen
- [x] M2: stage validation completed
- [x] M3: single verdict and single recommendation completed

## Exit criteria

- 产出 suite/rules/summary/details/report/recommendation/verdict。
- 单一 final verdict，唯一 recommendation。
- 190 的单一 verdict 决定 191 唯一分支。
