# 056 Post V6 Symmetric Comparison

## Purpose / Big Picture

当 route C v6 与 route B v6 都存在后，项目第一次可以在 `larger_labeled_split_v6` 这个 shared substrate 上做真正的对称比较。056 的目标是把 route B 和 route C 的历史版本与 v6 版本放到同一层统一比较，并明确下一步最值得继续扩的是 route、substrate，还是更像样的小规模真实 labeled experiment。

## Scope

### In Scope

- unified v6 symmetric comparison
- progression summary
- tradeoff matrix
- next-step recommendation
- acceptance / README / 收口

### Out of Scope

- 直接执行下一步推荐路线
- benchmark ground truth 接入
- 更大模型 / 更大数据规模

## Repository Context

本计划主要衔接：

- `outputs/rerun_route_b_on_labeled_split_v6/default/*`
- `outputs/rerun_route_c_on_labeled_split_v6/default/*`
- `outputs/post_v5_next_step_bootstrap/default/*`
- `src/eval/post_v5_symmetric_comparison.py`

## Deliverables

- `.plans/056-post-v6-symmetric-comparison.md`
- `src/eval/post_v6_symmetric_comparison.py`
- `scripts/build_post_v6_symmetric_comparison.py`
- `src/eval/post_v6_symmetric_comparison_checks.py`
- `scripts/validate_post_v6_symmetric_comparison.py`
- `v6_symmetric_comparison_summary.json`
- `route_b_v6_vs_route_c_v6_comparison.csv`
- `supervision_progression_after_v6_rerun.json`
- `v6_tradeoff_matrix.csv`
- `v6_symmetric_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: unified v6 symmetric comparison
- [x] Milestone 2: recommendation / acceptance / README / 收口

## Surprises & Discoveries

- v6 substrate 让 B/C 的比较第一次同时具备 shared substrate 和 `70`-row 容量，但 supervision semantics 仍然不同：B 是 sample-level task-truth proxy，C 是 contract-level benchmark-truth-leaning proxy。
- 当 B/C 都已经到 v6 时，新的共同 ceiling 很可能再次回到 shared substrate 本身，而不只是某一条路线没 rerun。
- 056 的关键新增判断不是“默认继续 v7”，而是要显式比较：继续扩 proxy substrate 的收益，是否已经低于切向第一轮更像样的小规模真实 labeled experiment。
- 056 的实际 recommendation 已稳定落到 `prepare_small_real_labeled_experiment`，并显式给出 `continue_proxy_substrate_expansion = false`，说明 v6 已经足以触发从 proxy 扩容向 real-experiment cutover 的第一次分流。

## Decision Log

- 决策：056 将以 `route_b_v6` 与 `route_c_v6` 为核心，但保留历史版本作为 progression 参考。
  - 原因：用户要的是 v6 条件下的第一次真正对称比较，而不是只看两个最新 summary。
  - 影响范围：comparison CSV、tradeoff matrix 与 next-step recommendation 结构。

## Plan of Work

先统一读取 old route B、larger route B、route B v2、route B v3、route B v4、route B v5、route B v6、old route C、larger route C、route C v2、route C v3、route C v4、route C v5、route C v6，以及 earlier comparison artifacts。然后输出 v6 对称比较 summary、CSV 与 tradeoff matrix，明确 B-v6 与 C-v6 相比历史版本的新增信息，并单独判断 `continue_proxy_substrate_expansion` 是否仍然值得。最后生成 next-step recommendation，并补 validator、repeatability 与 README。

## Concrete Steps

1. 更新 `src/eval/post_v6_symmetric_comparison.py` 与配套 CLI / validator。
2. 运行 `build_post_v6_symmetric_comparison.py` 生成 comparison artifact。
3. 运行 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_post_v6_symmetric_comparison.py --help` 可正常显示
- `validate_post_v6_symmetric_comparison.py --help` 可正常显示
- 至少生成：
  - `v6_symmetric_comparison_summary.json`
  - `route_b_v6_vs_route_c_v6_comparison.csv`
  - `supervision_progression_after_v6_rerun.json`
  - `v6_tradeoff_matrix.csv`
  - `v6_symmetric_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

056 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若只想复核 recommendation，可直接重跑 build 与 validate。

## Remaining Risks

- v6 对称比较仍然只是 proxy supervision 层面的工程比较，而不是 benchmark-grade 结论。
- 所有结论仍受 local curated split、`pilot_distilgpt2_hf` 和 self-fit logistic 影响。

## Next Suggested Plan

若 056 完成，下一步建议优先创建 `.plans/057-real-experiment-cutover-bootstrap.md`，把“切向第一轮更像样的小规模真实 labeled experiment”的 bootstrap 至少做成一个可执行对象，而不是机械继续 v7。
