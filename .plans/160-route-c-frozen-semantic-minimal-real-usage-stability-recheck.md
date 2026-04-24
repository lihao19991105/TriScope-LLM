# 160 Route-C Frozen Semantic Minimal Real Usage Stability Recheck

## Background

本阶段按 159 的单一 final verdict 自动进入。若 159=Minimal real usage validated，则进入最小真实使用稳定性复检线。

## Purpose

验证 159 的通过结果是否在额外窗口下持续成立，且不引入新的 parser/gate/health/handoff 异常。

## Scope

### In Scope

- 增加一个受控复检窗口，继续三路径覆盖。
- 产出独立 suite/rules/summary/details/report/recommendation/verdict。

### Out of Scope

- 不改 benchmark truth 或 gate。
- 不扩模型轴、预算、prompt/attack family。
- 不做大规模稳定性工程。

## Validation criteria

- recoverable 必须 pass_formatted_to_parser。
- normal 必须 pass_raw_to_parser。
- nonrecoverable 必须 degeneration_blocked。
- 无 drift、无 handoff/health 异常，gate/logistic 均 PASS。

## Milestones

- [x] M1: minimal real usage stability recheck set and criteria frozen
- [x] M2: minimal real usage stability recheck completed
- [x] M3: single verdict and single recommendation completed

## Risks

- 仍为受控验证，不等价于主实验矩阵。

## Exit criteria

- 独立产物齐全且单一 verdict 可驱动 161 自动分支。
