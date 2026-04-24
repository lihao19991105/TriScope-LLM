# 161 Route-C Frozen Semantic Minimal Real Usage Batched Regression

## Background

本阶段按 160 的单一 final verdict 自动进入。在 160-A validated 情况下，161 进入最小真实使用 batched 回归线。

## Goal

在不扩张前提下把验证推进到 batched 回归层，持续检查 recoverable/normal/nonrecoverable 三路径与链路一致性。

## Frozen scope

- benchmark truth / gate / recoverable-boundary 语义保持冻结。
- 不扩模型轴、预算、prompt family、attack family。

## Milestones

- [x] M1: minimal real usage batched regression set and criteria frozen
- [x] M2: minimal real usage batched regression completed
- [x] M3: single verdict and single recommendation completed

## Exit criteria

- 独立 artifacts 完整，单一 verdict 可驱动 162 自动分支。
