# 048 Post V4 Symmetric Comparison

## Purpose / Big Picture

当 route C v4 与 route B v4 都存在后，项目第一次可以在 `larger_labeled_split_v4` 这个 shared substrate 上做真正的对称比较。048 的目标是把 route B 和 route C 的历史版本与 v4 版本放到同一层统一比较，并明确下一步最值得继续扩的是 route、substrate，还是更像样的小规模真实 labeled experiment。

## Scope

### In Scope

- unified v4 symmetric comparison
- progression summary / tradeoff matrix
- next-step recommendation
- acceptance / repeatability / README / 收口

### Out of Scope

- 直接 rerun v5
- 切换模型
- benchmark ground truth 接入

## Repository Context

本计划主要衔接：

- `outputs/more_natural_label_bootstrap/default/*`
- `outputs/chosen_route_rerun_on_larger_split/default/*`
- `outputs/rerun_route_b_on_labeled_split_v2/default/*`
- `outputs/rerun_route_b_on_labeled_split_v3/default/*`
- `outputs/rerun_route_b_on_labeled_split_v4/default/*`
- `outputs/expanded_route_c_bootstrap/default/*`
- `outputs/rerun_route_c_on_larger_split/default/*`
- `outputs/rerun_route_c_on_labeled_split_v2/default/*`
- `outputs/rerun_route_c_on_labeled_split_v3/default/*`
- `outputs/rerun_route_c_on_labeled_split_v4/default/*`
- `outputs/post_v3_next_step_bootstrap/default/*`

## Deliverables

- `.plans/048-post-v4-symmetric-comparison.md`
- `src/eval/post_v4_symmetric_comparison.py`
- `scripts/build_post_v4_symmetric_comparison.py`
- `src/eval/post_v4_symmetric_comparison_checks.py`
- `scripts/validate_post_v4_symmetric_comparison.py`
- `v4_symmetric_comparison_summary.json`
- `route_b_v4_vs_route_c_v4_comparison.csv`
- `supervision_progression_after_v4_rerun.json`
- `v4_tradeoff_matrix.csv`
- `v4_symmetric_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: unified v4 symmetric comparison
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Surprises & Discoveries

- v4 substrate 让 B/C 的比较第一次同时具备 shared substrate 和 `50`-row 容量，但 supervision semantics 仍然不同：B 是 sample-level task-truth proxy，C 是 contract-level benchmark-truth-leaning proxy。
- 当 B/C 都已经到 v4 时，新的共同 ceiling 很可能再次回到 shared substrate 本身，而不只是某一条路线没 rerun。
- 因此 048 的核心价值不是继续证明某条路径存在，而是给出“下一个 shared enabler”。

## Decision Log

- 决策：048 若确认 B/C 在 v4 上都已存在，则默认优先考虑 `prepare_larger_labeled_split_v5`。
  - 原因：当 B/C 都共享同一个 50-row substrate 后，再做单一路线扩展的边际收益通常低于继续抬 shared substrate。
  - 影响范围：049 的 bootstrap 方向。

## Plan of Work

先统一读取 old route B、larger route B、route B v2、route B v3、route B v4、expanded route C、larger route C、route C v2、route C v3、route C v4，以及 earlier comparison artifacts。然后输出 v4 对称比较 summary、CSV 与 tradeoff matrix，明确 B-v4 与 C-v4 相比历史版本的新增信息。最后生成 next-step recommendation，并补 validator、repeatability 与 README。

## Validation and Acceptance

- `build_post_v4_symmetric_comparison.py --help` 可正常显示
- `validate_post_v4_symmetric_comparison.py --help` 可正常显示
- 至少生成：
  - `v4_symmetric_comparison_summary.json`
  - `route_b_v4_vs_route_c_v4_comparison.csv`
  - `supervision_progression_after_v4_rerun.json`
  - `v4_tradeoff_matrix.csv`
  - `v4_symmetric_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

048 的 build / validate 都是幂等的；重复运行会覆盖同名输出。中断后可直接重跑。

## Remaining Risks

- v4 对称比较仍然只是 proxy supervision 层面的工程比较，而不是 benchmark-grade 结论。
- 当前所有路线仍绑定同一个 local curated split 和 lightweight model。

## Next Suggested Plan

若 048 完成，下一步建议创建 `.plans/049-post-v4-next-step-bootstrap.md`，把 048 推荐的 next step 至少 bootstrap 起步，而不是停留在 comparison 结论。
