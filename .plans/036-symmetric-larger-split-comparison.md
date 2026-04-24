# 036 Symmetric Larger Split Comparison

## Purpose / Big Picture

035 把 route C 真正 rerun 到 larger split 上之后，项目第一次具备了 larger-split 条件下的对称比较基础。036 的目标是把 old route B、larger route B、larger route C 放到同一层统一比较，并明确下一步应继续扩哪条路线，还是直接准备 larger labeled split v2。

## Scope

### In Scope

- larger-split 对称比较
- progression summary
- tradeoff matrix
- next-step recommendation
- acceptance / repeatability / README / 收口

### Out of Scope

- 实际继续扩 B/C
- 直接 materialize larger split v2
- 切换模型或引入 benchmark ground truth

## Repository Context

本计划主要衔接：

- `outputs/more_natural_label_bootstrap/default/*`
- `outputs/chosen_route_rerun_on_larger_split/default/*`
- `outputs/rerun_route_c_on_larger_split/default/*`
- `outputs/expanded_route_c_bootstrap/default/*`
- `outputs/post_rerun_comparison/default/*`
- `outputs/larger_labeled_split_bootstrap/default/*`

## Deliverables

- `.plans/036-symmetric-larger-split-comparison.md`
- `src/eval/symmetric_larger_split_comparison.py`
- `scripts/build_symmetric_larger_split_comparison.py`
- `src/eval/symmetric_larger_split_comparison_checks.py`
- `scripts/validate_symmetric_larger_split_comparison.py`
- `symmetric_larger_split_comparison_summary.json`
- `route_b_larger_vs_route_c_larger_comparison.csv`
- `supervision_progression_after_symmetric_rerun.json`
- `symmetric_rerun_tradeoff_matrix.csv`
- `symmetric_rerun_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: unified symmetric comparison / tradeoff matrix
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Surprises & Discoveries

- larger-split route B 与 larger-split route C 在 substrate 规模上终于对齐，但 supervision semantics 仍然不同：B 是 sample-level task-truth proxy，C 是 contract-level truth-leaning proxy。
- 对称比较之后，新的共同 ceiling 变成了 shared substrate 本身，而不再只是“某一条路线还没 rerun”。
- 因此 036 的价值主要在于把推荐路线从“继续补齐 rerun”升级为“下一层 substrate 该如何继续扩”。

## Decision Log

- 决策：036 推荐下一步优先准备 `larger labeled split v2`。
  - 原因：B/C 已经在同一 20-row shared substrate 上具备对称结果，当前最大的共同限制重新回到了 substrate ceiling。
  - 影响范围：next-step recommendation 与 037 的 bootstrap 方向。

## Plan of Work

先统一读取 old route B、larger route B、larger route C、expanded route C 和 earlier comparison artifacts。然后输出 larger-split 对称比较 summary、CSV 和 tradeoff matrix，明确 larger-split rerun 后 B/C 的新增信息与剩余差异。最后生成 next-step recommendation，并补 validator、repeatability 与 README。

## Validation and Acceptance

- `build_symmetric_larger_split_comparison.py --help` 可正常显示
- `validate_symmetric_larger_split_comparison.py --help` 可正常显示
- 至少生成：
  - `symmetric_larger_split_comparison_summary.json`
  - `route_b_larger_vs_route_c_larger_comparison.csv`
  - `supervision_progression_after_symmetric_rerun.json`
  - `symmetric_rerun_tradeoff_matrix.csv`
  - `symmetric_rerun_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

036 的 build / validate 都是幂等的；重复运行会覆盖同名输出。中断后可直接重跑。

## Remaining Risks

- larger-split 对称比较仍然只是 proxy supervision 层面的工程比较，而不是 benchmark-grade 实验结论。
- 当前所有路线仍然绑定 local curated split 和 lightweight model。

## Next Suggested Plan

若 036 完成，下一步建议创建 `.plans/037-post-symmetric-rerun-next-step-bootstrap.md`，把 `larger labeled split v2` 作为下一层 shared substrate 继续 bootstrap 起步。
