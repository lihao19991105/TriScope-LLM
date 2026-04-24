# 041 Post V2 Next Step Bootstrap

## Purpose / Big Picture

040 会把 route B v2 与 route C v2 放到真正对称的 substrate 上。如果 recommendation 依然清楚地指向 shared substrate ceiling，那么下一步最自然的动作就是把 `larger_labeled_split_v3` 至少 bootstrap 起步，而不是停留在 recommendation 文本层。

## Scope

### In Scope

- chosen next step materialization
- larger labeled split v3 contract / readiness
- larger split v3 artifact and bridge compatibility
- acceptance / repeatability / README / 收口

### Out of Scope

- 在 v3 substrate 上立即 rerun B/C
- benchmark-scale 数据
- 更大模型 / 大规模训练

## Repository Context

本计划主要衔接：

- `outputs/post_symmetric_next_step_bootstrap/default/*`
- `outputs/post_v2_symmetric_comparison/default/*`
- `src/eval/post_symmetric_next_step_bootstrap.py`
- `src/eval/labeled_pilot_bootstrap.py`
- `src/eval/pilot_execution.py`
- `src/eval/pilot_extension.py`
- `src/eval/pilot_illumination.py`

## Deliverables

- `.plans/041-post-v2-next-step-bootstrap.md`
- `src/eval/post_v2_next_step_bootstrap.py`
- `scripts/build_post_v2_next_step_bootstrap.py`
- `src/eval/post_v2_next_step_bootstrap_checks.py`
- `scripts/validate_post_v2_next_step_bootstrap.py`
- `post_v2_next_step_plan.json`
- `post_v2_next_step_readiness_summary.json`
- `larger_labeled_split_v3.jsonl`
- `larger_labeled_split_v3_summary.json`
- `post_v2_next_step_bridge_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize chosen next step
- [x] Milestone 2: emit first executable bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 一旦 B/C 在 v2 substrate 上都真正存在，下一层最高收益动作很可能再次回到 shared labeled substrate 的增长。
- 041 不需要改变 supervision 路线定义；只需要把 shared substrate 从 30-row 再抬到 40-row，并继续保持 B/C/fusion builder 可接。
- 当前最小可行的 v3 选择是把 substrate 从 30 rows 扩到 40 rows，这样仍然保持 local curated 可控成本。

## Decision Log

- 决策：041 默认选择 `larger_labeled_split_v3` 作为 post-v2 next step。
  - 原因：040 若确认共同 bottleneck 仍是 substrate ceiling，则 v3 是最稳妥的 shared enabler。
  - 影响范围：bootstrap artifact、README、后续 rerun 计划建议。

## Plan of Work

先读取 040 的 recommendation，确认 chosen next step 是 `prepare_larger_labeled_split_v3`。然后把 037 的 30-row v2 split 作为 base substrate，再补 10 条新的 local curated rows 形成 40-row v3 split。接着复用稳定 builder 生成 reasoning / confidence / illumination / labeled illumination contracts，并执行 dry-run bridge compatibility。最后补 acceptance、repeatability 与 README。

## Validation and Acceptance

- `build_post_v2_next_step_bootstrap.py --help` 可正常显示
- `validate_post_v2_next_step_bootstrap.py --help` 可正常显示
- 至少生成：
  - `post_v2_next_step_plan.json`
  - `post_v2_next_step_readiness_summary.json`
  - `larger_labeled_split_v3.jsonl`
  - `larger_labeled_split_v3_summary.json`
  - `post_v2_next_step_bridge_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

041 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 dry-run bridge 中断，可直接重跑 build CLI。

## Remaining Risks

- larger split v3 仍然只是 local curated split，不是 benchmark-scale substrate。
- 041 证明的是 next-step bootstrap readiness，不是 v3 substrate 上的真实 rerun 结果。

## Next Suggested Plan

若 041 完成，下一步建议在 `larger_labeled_split_v3` 上优先 rerun route C，再 rerun route B，或根据资源情况选择其中一条作为下一次更大 substrate 的 first-pass validation。
