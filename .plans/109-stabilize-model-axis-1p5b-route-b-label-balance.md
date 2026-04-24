# 109 Stabilize Model-Axis 1.5B Route-B Label Balance

## Purpose / Big Picture

107 已在本地 1.5B 上真实进入 route_b 推理，但 more-natural labeled dataset 在 32-row 最小 execution 中出现单类塌缩（label_1=32, label_0=0），导致 logistic 前置条件失败。109 的目标是在不扩模型轴、不扩数据轴、不改大模块的前提下，稳定修复 route_b 标签可分性，使后续 rerun 可以进入可分析状态。

## Scope

### In Scope

- 基于 107/108 真实 artifact 诊断 route_b 单类塌缩直接成因。
- 实现最小改动的 route_b 标签稳定化逻辑（仅围绕 1.5B route_b）。
- 产出 balanced candidate dataset 与 precheck，验证 logistic 前置条件是否恢复。
- 若恢复成立，衔接 110 stabilized rerun 计划。

### Out of Scope

- 3B / 7B 模型扩张。
- fusion v12/v13 或 proxy substrate 扩容。
- 新训练主线。
- route_c / fusion_summary 扩展执行。

## Repository Context

- `src/eval/model_axis_1p5b_execution.py`
- `src/eval/rerun_route_b_on_labeled_split_v6.py`
- `src/fusion/more_natural_label_fusion.py`
- `scripts/build_model_axis_1p5b_execution.py`
- `outputs/model_axis_1p5b_execution/default/*`
- `outputs/model_axis_1p5b_analysis/default/*`

## Deliverables

- `.plans/109-stabilize-model-axis-1p5b-route-b-label-balance.md`
- `outputs/model_axis_1p5b_route_b_stabilization/default/route_b_label_collapse_diagnosis.json`
- `outputs/model_axis_1p5b_route_b_stabilization/default/route_b_label_balance_recovery_plan.json`
- `outputs/model_axis_1p5b_route_b_stabilization/default/route_b_selection_knobs_summary.json`
- `outputs/model_axis_1p5b_route_b_stabilization/default/route_b_balanced_candidate_dataset.jsonl`
- `outputs/model_axis_1p5b_route_b_stabilization/default/route_b_balanced_candidate_summary.json`
- `outputs/model_axis_1p5b_route_b_stabilization/default/route_b_label_balance_precheck.json`
- `src/eval/model_axis_1p5b_route_b_stabilization.py`
- `scripts/build_model_axis_1p5b_route_b_stabilization.py`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 诊断单类塌缩成因并形成 recovery 方案
- [x] Milestone 2: 实现最小改动稳定化并产出 precheck
- [ ] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：109 优先在 route_b 标签构造与执行前检查层面做最小改动，不触碰更大实验轴。
  - 原因：当前 blocker 已被 108 明确为 route_b 单类塌缩，不是模型本地化或矩阵编排问题。
- 决策：109 先产出 candidate 与 precheck，再决定是否推进 110 rerun。
  - 原因：先用低成本验证“至少两类”是否可恢复，避免盲目重跑。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_b_stabilization.py --help` 可正常显示。
- 产物目录存在且包含 109 要求的 6 个核心 JSON/JSONL 文件。
- precheck 明确记录 class_balance 与 logistic 前置条件（至少两类）是否恢复。

## Idempotence and Recovery

- 109 输出默认写入 `outputs/model_axis_1p5b_route_b_stabilization/default/`，可重复运行覆盖。
- 若中断，保留已写入的 diagnosis/recovery artifacts，继续 rerun 同一命令即可。

## Remaining Risks

- 若 1.5B 在 rerun 时行为漂移，candidate 预检查通过不保证 rerun 必然通过。
- 若 illumination 文本格式继续变化，label 稳定化需要保持对解析规则的可解释约束。

## Outcome Snapshot

- 109/M1 已定位主因：illumination 选项解析对前缀格式（例如 `AHuman:`）失配，导致 illumination correctness 全量为 false，并放大为单类标签塌缩。
- 109/M2 产出的 candidate dataset 已恢复双类：`label_0=30, label_1=2`，logistic 两类前置条件为 true。
- 当前已满足推进 110 stabilized rerun 的前置条件。

## Next Suggested Plan

若 109 precheck 表明 `class_balance` 已包含两类，下一步创建并执行 `.plans/110-rerun-model-axis-1p5b-route-b-stable-execution.md`。
