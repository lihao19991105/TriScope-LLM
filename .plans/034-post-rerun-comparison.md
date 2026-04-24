# 034 Post Rerun Comparison

## Purpose / Big Picture

033 已经把 chosen route B 真正在 larger split 上 rerun 出来了。034 的目标是把 old route B、expanded route C、new larger-split route B 放到同一层比较，并明确 rerun 后项目最自然的下一步到底是什么。

## Scope

### In Scope

- rerun 后 unified comparison
- route progression summary
- next-step recommendation
- acceptance / repeatability / README / 收口

### Out of Scope

- 实际 rerun route C on larger split
- 再扩 shared substrate
- 更大模型 / 更大数据接入

## Repository Context

本计划主要衔接：

- `outputs/more_natural_label_bootstrap/default/*`
- `outputs/expanded_route_c_bootstrap/default/*`
- `outputs/chosen_route_rerun_on_larger_split/default/*`
- `outputs/larger_labeled_split_bootstrap/default/*`
- `outputs/expanded_supervision_comparison/default/*`
- `outputs/larger_split_route_rerun_decision/default/*`

## Deliverables

- `.plans/034-post-rerun-comparison.md`
- `src/eval/post_rerun_comparison.py`
- `scripts/build_post_rerun_comparison.py`
- `src/eval/post_rerun_comparison_checks.py`
- `scripts/validate_post_rerun_comparison.py`
- `post_rerun_comparison_summary.json`
- `route_progression_after_rerun.csv`
- `post_rerun_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: unified post-rerun comparison / progression summary
- [x] Milestone 2: next-step recommendation / acceptance / README / 收口

## Surprises & Discoveries

- 033 把 route B 从 `5 rows / 5 base samples` 提升到了 `20 rows / 20 base samples`，因此 route B 的“是否值得继续看”这个问题已经不再主要受 tiny substrate 限制。
- 但 rerun 后新的不对称点也变得更明显：route C 仍停留在 10-base-sample expanded substrate，而 route B 已经在 larger split 上完成了对称增长。
- 因此 034 的主要价值不是重新证明 B 更强或 C 更强，而是明确下一步应先补 route C 的 larger-split 对称 rerun。

## Decision Log

- 决策：034 推荐下一步优先 rerun route C on larger split。
  - 原因：route B 已经拿到 larger-split rerun，当前最大的剩余信息缺口是 route C 缺少同 substrate 条件下的对称结果。
  - 影响范围：post-rerun recommendation 与后续计划建议。

## Plan of Work

先读取 old route B、expanded route C、new larger-split route B 三组 artifact，并把 supervision semantics、substrate size、row/base-sample coverage、logistic bootstrap 输出统一到同一 schema。然后输出 progression CSV，明确 rerun 后 route B 相比旧结果的增量，以及它相对 expanded route C 仍然存在的 substrate 不对称。最后生成 next-step recommendation，并补 validator、repeatability 和 README。

## Validation and Acceptance

- `build_post_rerun_comparison.py --help` 可正常显示
- `validate_post_rerun_comparison.py --help` 可正常显示
- 至少生成：
  - `post_rerun_comparison_summary.json`
  - `route_progression_after_rerun.csv`
  - `post_rerun_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

034 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若中断，可直接重跑 build 或 validate。

## Remaining Risks

- comparison 仍然建立在 pilot-level proxy supervision 与 lightweight model 上。
- route B 与 route C 当前还不在完全相同的 substrate 上，因此本轮比较更偏“下一步调度价值”而不是研究级优劣判断。

## Next Suggested Plan

若 034 完成，下一步建议直接创建一个 route C on larger split 的 rerun 计划，以恢复 B / C 的 substrate 对称性。
