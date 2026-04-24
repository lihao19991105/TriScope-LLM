# 053 Post V5 Next Step Bootstrap

## Purpose / Big Picture

052 会把 route B v5 与 route C v5 放到真正对称的 substrate 上。如果 recommendation 依然清楚地指向 shared substrate ceiling，那么下一步最自然的动作就是把 `larger_labeled_split_v6` 至少 bootstrap 起步，而不是停留在 recommendation 文本层。

## Scope

### In Scope

- chosen next step materialization
- larger labeled split v6 contract / readiness
- larger split v6 artifact and bridge compatibility
- acceptance / repeatability / README / 收口

### Out of Scope

- 在 v6 substrate 上立即 rerun B/C
- benchmark-scale 数据
- 更大模型 / 大规模训练

## Repository Context

本计划主要衔接：

- `outputs/post_v4_next_step_bootstrap/default/*`
- `outputs/post_v5_symmetric_comparison/default/*`
- `src/eval/post_v4_next_step_bootstrap.py`
- `src/eval/labeled_pilot_bootstrap.py`
- `src/eval/pilot_execution.py`
- `src/eval/pilot_extension.py`
- `src/eval/pilot_illumination.py`

## Deliverables

- `.plans/053-post-v5-next-step-bootstrap.md`
- `src/eval/post_v5_next_step_bootstrap.py`
- `scripts/build_post_v5_next_step_bootstrap.py`
- `src/eval/post_v5_next_step_bootstrap_checks.py`
- `scripts/validate_post_v5_next_step_bootstrap.py`
- `post_v5_next_step_plan.json`
- `post_v5_next_step_readiness_summary.json`
- `larger_labeled_split_v6.jsonl`
- `larger_labeled_split_v6_summary.json`
- `post_v5_next_step_bridge_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize chosen next step
- [x] Milestone 2: emit first executable bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 一旦 B/C 在 v5 substrate 上都真正存在，下一层最高收益动作很可能再次回到 shared labeled substrate 的增长。
- 053 不需要改变 supervision 路线定义；只需要把 shared substrate 从 60-row 再抬到 70-row，并继续保持 B/C/fusion builder 可接。
- 053 已稳定生成 `larger_labeled_split_v6`，包含 `70` 行 / `70` 个 base samples，bridge dry-run 与 repeatability 都为 `PASS`，因此 v6 已经是一个可直接衔接下轮 rerun 的 substrate 对象。

## Decision Log

- 决策：053 默认选择 `larger_labeled_split_v6` 作为 post-v5 next step。
  - 原因：若 052 再次确认共同 bottleneck 仍是 substrate ceiling，那么 v6 依旧是最稳妥的 shared enabler。
  - 影响范围：bootstrap artifact、README、后续 rerun 计划建议。

## Plan of Work

先读取 052 的 recommendation，确认 chosen next step 是 `prepare_larger_labeled_split_v6`。然后把 049 的 60-row v5 split 作为 base substrate，再补 10 条新的 local curated rows 形成 70-row v6 split。接着复用稳定 builder 生成 reasoning / confidence / illumination / labeled illumination contracts，并执行 dry-run bridge compatibility。最后补 acceptance、repeatability 与 README。

## Concrete Steps

1. 更新 `src/eval/post_v5_next_step_bootstrap.py` 与配套 CLI / validator。
2. 运行 `build_post_v5_next_step_bootstrap.py` 生成 v6 bootstrap artifact。
3. 运行 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_post_v5_next_step_bootstrap.py --help` 可正常显示
- `validate_post_v5_next_step_bootstrap.py --help` 可正常显示
- 至少生成：
  - `post_v5_next_step_plan.json`
  - `post_v5_next_step_readiness_summary.json`
  - `larger_labeled_split_v6.jsonl`
  - `larger_labeled_split_v6_summary.json`
  - `post_v5_next_step_bridge_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

053 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 dry-run bridge 中断，可直接重跑 build CLI。

## Remaining Risks

- larger split v6 仍然只是 local curated split，不是 benchmark-scale substrate。
- 053 证明的是 next-step bootstrap readiness，不是 v6 substrate 上的真实 rerun 结果。

## Next Suggested Plan

若 053 完成，下一步建议在 `larger_labeled_split_v6` 上优先 rerun route C，再 rerun route B，或根据资源情况选择其中一条作为下一次更大 substrate 的 first-pass validation。
