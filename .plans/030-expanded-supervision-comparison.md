# 030 Expanded Supervision Comparison

## Purpose / Big Picture

029 已经把 expanded route C 真正 rerun 出来了，因此现在第一次具备了一个有意义的三方比较面：route B、old route C、expanded route C。030 的目标就是把这三者放到同一层做统一比较，并根据真实 artifact 给出下一步 recommendation。

## Scope

### In Scope

- route B / old route C / expanded route C 的统一 comparison
- progression summary
- next-step recommendation
- acceptance / repeatability / README / 收口

### Out of Scope

- rerun route B
- 再次扩 route C
- 更大 labeled split 的实际 materialization

## Repository Context

本计划主要衔接：

- `outputs/more_natural_label_bootstrap/*`
- `outputs/benchmark_truth_leaning_label_bootstrap/*`
- `outputs/expanded_route_c_bootstrap/*`
- `outputs/labeled_slice_expansion/*`
- `src/eval/`
- `scripts/`

## Deliverables

- `.plans/030-expanded-supervision-comparison.md`
- `src/eval/expanded_supervision_comparison.py`
- `scripts/build_expanded_supervision_comparison.py`
- `src/eval/expanded_supervision_comparison_checks.py`
- `scripts/validate_expanded_supervision_comparison.py`
- `expanded_supervision_comparison_summary.json`
- `route_b_oldc_expandedc_comparison.csv`
- `supervision_progression_summary.json`
- `expanded_supervision_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: unified comparison across B / old C / expanded C
- [x] Milestone 2: structured recommendation / acceptance / README / 收口

## Surprises & Discoveries

- expanded route C 的增长是实质性的：从 old route C 的 `10 rows / 5 base samples` 增长到了 `20 rows / 10 base samples`，并且仍然保持 benchmark-truth-leaning supervision semantics。
- route B 仍然在 supervision semantics 上有价值，但当前 artifact 层面它已经明显落后于 expanded route C 的 row coverage 和 truth anchoring。
- 这意味着下一步如果还想继续让 supervision “更进一步”，与其回头先扩 B，不如优先准备更大的 labeled split，让 expanded route C 不至于再次很快撞到 substrate ceiling。

## Decision Log

- 决策：030 以 expanded route C 作为当前 strongest supervision path。
  - 原因：它相对 old route C 增加了 substrate 规模，同时保留了更 truth-leaning 的 label semantics。
  - 影响范围：comparison summary、next-step recommendation。

- 决策：030 推荐下一步优先准备更大的 labeled split。
  - 原因：expanded route C 已经证明继续扩大 truth-leaning route 是有效的，但当前 10-row substrate 很快会再次成为共同 ceiling。
  - 影响范围：next-step recommendation 与后续计划建议。

## Plan of Work

先统一读取 route B、old route C、expanded route C 的 summary / logistic artifact，并把 row 数、base sample 数、label semantics、truth anchoring、executability 放到统一 comparison schema 里。然后输出 progression summary，明确 expanded route C 相比 old route C 的增益，以及它相对 route B 的当前优势。最后生成 next-step recommendation，并补 validator、repeatability 和 README。

## Validation and Acceptance

- `build_expanded_supervision_comparison.py --help` 可正常显示
- `validate_expanded_supervision_comparison.py --help` 可正常显示
- 至少生成：
  - `expanded_supervision_comparison_summary.json`
  - `route_b_oldc_expandedc_comparison.csv`
  - `supervision_progression_summary.json`
  - `expanded_supervision_next_step_recommendation.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

030 的 build 与 validate 都是幂等的；重复运行会覆盖同名输出。若中断，可直接重跑 build 或 validate。

## Remaining Risks

- 三条路线仍然都来自同一个轻量模型和本地 pilot-level substrate。
- comparison 体现的是工程推进价值和当前 supervision realism 差异，不是研究级效果优劣。
- 推荐“更大的 labeled split”不等于已经确定了 benchmark-grade label source。

## Next Suggested Plan

若 030 完成，下一步建议创建一个面向更大 labeled split bootstrap 的计划，让 expanded route C 与潜在 expanded route B 都能站在更大的共享 substrate 上继续比较。
