# 037 Post Symmetric Rerun Next Step Bootstrap

## Purpose / Big Picture

036 的对称比较会把 B/C 都放到 same larger split 上。若 recommendation 依然清楚地指向 shared substrate ceiling，那么下一步最自然的动作就是把 `larger labeled split v2` 至少 bootstrap 起步，而不是停留在 recommendation 文本层。

## Scope

### In Scope

- chosen next step materialization
- larger labeled split v2 contract / readiness
- larger split v2 artifact and bridge compatibility
- acceptance / repeatability / README / 收口

### Out of Scope

- 在 v2 substrate 上立即 rerun B/C
- benchmark-scale 数据
- 更大模型 / 大规模训练

## Repository Context

本计划主要衔接：

- `outputs/larger_labeled_split_bootstrap/default/*`
- `outputs/symmetric_larger_split_comparison/default/*`
- `src/eval/larger_labeled_split_bootstrap.py`
- `src/eval/labeled_pilot_bootstrap.py`
- `src/eval/pilot_execution.py`
- `src/eval/pilot_extension.py`
- `src/eval/pilot_illumination.py`

## Deliverables

- `.plans/037-post-symmetric-rerun-next-step-bootstrap.md`
- `src/eval/post_symmetric_next_step_bootstrap.py`
- `scripts/build_post_symmetric_next_step_bootstrap.py`
- `src/eval/post_symmetric_next_step_bootstrap_checks.py`
- `scripts/validate_post_symmetric_next_step_bootstrap.py`
- `post_symmetric_next_step_plan.json`
- `post_symmetric_next_step_readiness_summary.json`
- `larger_labeled_split_v2.jsonl`
- `larger_labeled_split_v2_summary.json`
- `post_symmetric_next_step_bridge_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize chosen next step
- [x] Milestone 2: emit first executable bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 当 B/C 都已经在同一个 20-row larger split 上对称存在后，下一层收益最高的动作确实会回到 substrate 扩展本身。
- 037 不需要改变 supervision 路线定义；只需要把 shared labeled substrate 从 20-row 再向上抬一层，并继续保持 B/C/fusion builder 可接。
- 当前最小可行的 v2 选择是把 substrate 从 20 rows 扩到 30 rows，这样仍然保持 local curated 可控成本。

## Decision Log

- 决策：037 选择 `larger_labeled_split_v2` 作为 post-symmetric next step。
  - 原因：036 会把共同 bottleneck 重新定位到 shared substrate ceiling。
  - 影响范围：bootstrap artifact、README、后续 rerun 计划建议。

## Plan of Work

先读取 036 的 recommendation，确认 chosen next step 是 `prepare_larger_labeled_split_v2`。然后把 031 的 20-row larger split 作为 base substrate，再补 10 条新的 local curated rows 形成 30-row v2 split。接着复用稳定 builder 生成 reasoning / confidence / illumination / labeled illumination contracts，并执行 dry-run bridge compatibility。最后补 acceptance、repeatability 与 README。

## Validation and Acceptance

- `build_post_symmetric_next_step_bootstrap.py --help` 可正常显示
- `validate_post_symmetric_next_step_bootstrap.py --help` 可正常显示
- 至少生成：
  - `post_symmetric_next_step_plan.json`
  - `post_symmetric_next_step_readiness_summary.json`
  - `larger_labeled_split_v2.jsonl`
  - `larger_labeled_split_v2_summary.json`
  - `post_symmetric_next_step_bridge_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

037 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 dry-run bridge 中断，可直接重跑 build CLI。

## Remaining Risks

- larger split v2 仍然只是 local curated split，不是 benchmark-scale substrate。
- 037 证明的是 next-step bootstrap readiness，不是 v2 substrate 上的真实 rerun 结果。

## Next Suggested Plan

若 037 完成，下一步建议在 `larger_labeled_split_v2` 上优先 rerun route C，再 rerun route B，或根据资源情况选择其中一条作为下一次较大 substrate 的 first-pass validation。
