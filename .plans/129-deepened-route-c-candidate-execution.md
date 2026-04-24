# 129 Deepened Route-C Candidate Execution

## Purpose / Big Picture

128 已经物化了 deepened candidate，但还没有进入真实 1.5B route_c execution。本计划目标是把 deepened candidate 从“可选输入对象”推进成“真实 execution 对象”，并判断它是仅守住 refined floor，还是足以升级为新 working baseline 候选。

## Scope

### In Scope

- 定义 deepened execution path，并生成 selection / plan / readiness artifact。
- 运行真实 1.5B route_c deepened execution。
- 输出 run summary / metrics / logistic summary / density comparison。
- 明确 deepened 相对 refined 与 anchor-aware 的价值判断。

### Out of Scope

- 3B / 7B。
- fusion 同轴扩张。
- proxy substrate 扩张。
- blind budget expansion。
- dataset 轴扩张。

## Repository Context

- `.plans/126-confirm-anchor-aware-route-c-stability.md`
- `.plans/127-post-anchor-aware-route-c-stability-analysis.md`
- `.plans/128-anchor-aware-route-c-selection-deepening-or-budget-decision.md`
- `src/eval/model_axis_1p5b_route_c_anchor_deepening.py`
- `src/eval/model_axis_1p5b_route_c_anchor_execution.py`
- `outputs/model_axis_1p5b_route_c_anchor_deepening/default/*`
- `outputs/model_axis_1p5b_route_c_anchor_execution/default/*`
- `outputs/model_axis_1p5b_route_c_refined_execution/default/*`

## Deliverables

- `.plans/129-deepened-route-c-candidate-execution.md`
- `src/eval/model_axis_1p5b_route_c_deepened_execution.py`
- `scripts/build_model_axis_1p5b_route_c_deepened_execution.py`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_execution_selection.json`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_execution_plan.json`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_execution_readiness_summary.json`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_execution_run_summary.json`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_execution_metrics.json`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/model_axis_1p5b_route_c_deepened_summary.json`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/model_axis_1p5b_route_c_deepened_logistic_summary.json`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_positive_support_breakdown.json`
- `outputs/model_axis_1p5b_route_c_deepened_execution/default/route_c_deepened_density_comparison.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: define deepened execution path and materialize inputs
- [x] Milestone 2: run 1.5B route_c deepened execution and evaluate value vs refined/anchor
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- deepened candidate 在真实 execution 中保持两类与 anchor continuity，但密度仅等于 refined floor（1/8），未维持 anchor 1/6 优势。

## Decision Log

- 决策：129 复用 124 的 execution 骨架，仅替换输入来源为 128 deepened registry，避免引入新的 pipeline 变量。
  - 原因：当前目标是验证 deepened candidate 本身，而不是重写稳定模块。

## Plan of Work

先以 128 registry 物化 deepened execution 输入，并输出 readiness。随后执行 1.5B deepened run，提取 class balance、density、anchor 保留与 logistic 结果。最后根据 deepened 相对 refined/anchor 的表现给出是否可升级为 working baseline 的判断，并补齐 README 最小用法。

## Concrete Steps

1. 新增 deepened execution 模块与 CLI。
2. 运行 deepened execution 生成 M1+M2 产物。
3. 检查 run summary / metrics / logistic summary。
4. 输出 deepened positive support 与 density comparison。
5. 更新 README 深度执行入口与恢复点。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_deepened_execution.py --help` 正常显示。
- 必须输出 selection / plan / readiness / run summary / metrics / deepened summary / deepened logistic summary。
- run summary 必须显式回答：
  - `used_local_weights`
  - `entered_model_inference`
  - `class_balance`
  - `num_rows`
  - `deepened_density`
  - `density_vs_refined`
  - `density_vs_anchor`
  - `reference_anchor_preserved`
  - deepened 是“守住 refined floor”还是“可升级 baseline 候选”。

## Idempotence and Recovery

- 脚本可重复运行；同一输出目录会覆盖同名摘要文件。
- 若执行中断，可直接重跑同一命令恢复全量产物。
- 若仅需保留历史快照，改用新的 output-dir 子目录。

## Outputs and Artifacts

- `outputs/model_axis_1p5b_route_c_deepened_execution/default/*`

## Remaining Risks

- deepened 可能仅维持 refined floor 而无法保持 anchor 1/6 优势。
- deepened 可能稳定执行但不带来新增正类支持。

## Outcome Snapshot

- 129 已完成并真实进入本地 1.5B 模型推理。
- 关键结果：
  - `summary_status = PASS`
  - `execution_status = FULL_EXECUTE`
  - `used_local_weights = true`
  - `entered_model_inference = true`
  - `class_balance = {label_0: 7, label_1: 1}`
  - `deepened_density = 0.125`
  - `density_vs_refined = 1.0`
  - `density_vs_anchor = 0.75`
  - `reference_anchor_preserved = true`
  - `baseline_upgrade_assessment = holds_refined_floor_but_fall_back_to_anchor_baseline`
- 结论：
  - deepened 当前属于“守住 refined floor”，不是“可直接替换 anchor-aware 的新 baseline”。

## Next Suggested Plan

- 进入 `.plans/130-confirm-deepened-route-c-stability.md`，验证 deepened floor 是否稳定并最终确认回退/保留决策。