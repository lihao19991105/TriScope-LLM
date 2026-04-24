# 105 Model-Axis 1.5B Bootstrap

## Purpose / Big Picture

104 已明确建议切到模型轴。105 的目标是在不破坏当前 ready-local 主线的前提下，第一次把 1.5B 级别单模型纳入真实实验矩阵世界，形成一个克制的 model-axis bootstrap。

## Scope

### In Scope

- 1.5B 候选模型选择
- ready-local / ready-run / fallback 规则
- model-axis definition / readiness / materialized inputs
- acceptance / repeatability / README

### Out of Scope

- 直接下载 1.5B 权重
- 3B / 7B 模型扩张
- 正式 model-axis execution

## Repository Context

- `configs/models.yaml`
- `outputs/post_v11_real_experiment_matrix_analysis/default/*`
- `outputs/next_axis_after_v10_matrix_bootstrap/default/*`

## Deliverables

- `.plans/105-model-axis-1p5b-bootstrap.md`
- `src/eval/model_axis_1p5b_bootstrap.py`
- `src/eval/model_axis_1p5b_bootstrap_checks.py`
- `scripts/build_model_axis_1p5b_bootstrap.py`
- `scripts/validate_model_axis_1p5b_bootstrap.py`
- `outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_candidate_selection.json`
- `outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_bootstrap_summary.json`
- `outputs/model_axis_1p5b_bootstrap/default/materialized_model_axis_1p5b_inputs/`
- `outputs/model_axis_1p5b_bootstrap/repeatability_default/artifact_acceptance.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: select 1.5B candidate and define bootstrap rules
- [x] Milestone 2: materialize model-axis 1.5B inputs and summary artifacts
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：105 选择 `pilot_small_hf` 作为首个 1.5B 候选，并把 `reference` 作为配置等价 fallback。
  - 原因：它已经存在于仓库模型配置体系中，接入成本最低，也最符合“先验证 matrix contract 可迁移性”的目标。
- 决策：105 诚实标记为 config-only / not-ready-local。
  - 原因：当前环境没有本地 1.5B 权重缓存，且本轮明确不默认下载大模型。

## Validation and Acceptance

- `build_model_axis_1p5b_bootstrap.py --help` 可正常显示
- `validate_model_axis_1p5b_bootstrap.py --help` 可正常显示
- `outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_bootstrap_summary.json` 为 `PASS`
- `outputs/model_axis_1p5b_bootstrap/default/model_axis_1p5b_candidate_selection.json` 已生成
- `outputs/model_axis_1p5b_bootstrap/repeatability_default/artifact_acceptance.json` 为 `PASS`

## Outcome Summary

- 1.5B 模型轴对象已第一次存在。
- 当前选定模型为 `pilot_small_hf -> Qwen/Qwen2.5-1.5B-Instruct`。
- 当前结论是：结构上可接入，但在当前环境下 `ready_local = false`、`ready_run = false`，因此不继续自动推进 106/107。

## Next Suggested Plan

若未来补齐本地 1.5B 权重或允许受控下载，下一步应进入 106，对 model-axis 1.5B 做一次最小 dry-run。
