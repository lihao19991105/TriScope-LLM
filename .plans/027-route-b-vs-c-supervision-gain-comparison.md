# 027 Route B vs C Supervision Gain Comparison

## Purpose / Big Picture

026 之后，仓库已经同时具备 route B（more-natural supervision proxy）和 route C（benchmark-truth-leaning supervision proxy）的最小 runnable bootstrap。当前真正的问题不再是“这两条路能不能存在”，而是“下一步最值得继续投哪条”。027 的目标是把 B / C 与一个新的候选方向 D（先扩大 labeled slice）放到同一个决策层里比较，并给出结构化 recommendation。

## Scope

### In Scope

- route B / C / D 的统一比较
- 当前收益、真实性、成本、ceiling 的结构化总结
- 下一步路线推荐
- acceptance / repeatability
- README 最小补充

### Out of Scope

- 直接扩大 route B 的真实执行
- 直接扩大 route C 的真实执行
- 下载新 benchmark 或新模型
- 新一轮 supervised 训练矩阵

## Repository Context

本计划主要衔接：

- `outputs/more_natural_label_bootstrap/*`
- `outputs/benchmark_truth_leaning_label_bootstrap/*`
- `outputs/controlled_supervision_expansion/*`
- `outputs/supervision_route_comparison/*`
- `outputs/pilot_materialization/pilot_csqa_reasoning_local/*`
- `src/eval/`
- `scripts/`

## Deliverables

- `.plans/027-route-b-vs-c-supervision-gain-comparison.md`
- `src/eval/route_b_vs_c_analysis.py`
- `scripts/build_route_b_vs_c_analysis.py`
- `src/eval/route_b_vs_c_analysis_checks.py`
- `scripts/validate_route_b_vs_c_analysis.py`
- `outputs/route_b_vs_c_analysis/default/route_b_vs_c_gain_summary.json`
- `outputs/route_b_vs_c_analysis/default/route_b_vs_c_vs_d_comparison.json`
- `outputs/route_b_vs_c_analysis/default/supervision_route_gain_matrix.csv`
- `outputs/route_b_vs_c_analysis/default/supervision_realism_cost_summary.json`
- `outputs/route_b_vs_c_analysis/default/route_b_vs_c_next_step_recommendation.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: route B / C / D compact comparison
- [x] Milestone 2: structured recommendation / acceptance / README / 收口

## Surprises & Discoveries

- route B 虽然更自然，但已经覆盖了当前全部 `5` 个 aligned base sample，因此它的下一步收益已经明显受当前 slice ceiling 限制。
- route C 虽然比 B 更接近 task truth，并且已经有 `10` 条 contract row，但它仍然锚定在同一个 `5`-sample local slice 上。
- 这意味着 B 与 C 的当前差异，更多体现在 supervision realism 层，而不是基础样本覆盖层；两者继续扩之前，共同的瓶颈已经变成了 labeled slice 太小。

## Decision Log

- 决策：027 引入 direction D（先扩大 labeled slice）作为和 B / C 同层比较的候选。
  - 原因：如果只比较 B 和 C，会忽略它们共享的上游瓶颈，即当前 slice 过小。
  - 影响范围：路线推荐、028 计划命名与 bootstrap contract。

- 决策：027 默认推荐 D，而不是继续直接扩 B 或 C。
  - 原因：B / C 都已经在当前 5-sample slice 上完成了可运行证明；下一步最小成本增益来自扩大 shared labeled substrate，而不是继续在同一 slice 上重复加 proxy 层。
  - 影响范围：028 选择 `labeled-slice-expansion-bootstrap`。

## Plan of Work

先读取 022、024、026 以及已有无标签 fusion 层的核心 summary，整理 route B 与 route C 的 supervision semantics、样本规模、logistic executability 和 ceiling。然后把 D 作为“为后续 B / C 解锁更大空间”的候选方向引入 comparison，并输出 route ranking 与 recommendation。最后补 validator、repeatability 和 README，确保 027 本身可交接。

## Concrete Steps

1. 新增 `src/eval/route_b_vs_c_analysis.py`，统一读取 B / C / D 所需 artifact 并导出 comparison summary。
2. 新增 `scripts/build_route_b_vs_c_analysis.py` 作为 CLI。
3. 新增 validator：
   - `src/eval/route_b_vs_c_analysis_checks.py`
   - `scripts/validate_route_b_vs_c_analysis.py`
4. 运行 comparison CLI，生成 default / default_repeat / repeatability artifact。
5. 更新 README 与本计划。

## Validation and Acceptance

- `build_route_b_vs_c_analysis.py --help` 可正常显示
- `validate_route_b_vs_c_analysis.py --help` 可正常显示
- default run 至少生成：
  - `route_b_vs_c_gain_summary.json`
  - `route_b_vs_c_vs_d_comparison.json`
  - `supervision_route_gain_matrix.csv`
  - `supervision_realism_cost_summary.json`
  - `route_b_vs_c_next_step_recommendation.json`
- recommendation 必须明确给出 B / C / D 的排序与推荐路线
- validator 输出 `artifact_acceptance.json`
- repeatability 输出 `repeatability_summary.json`

## Idempotence and Recovery

027 的 build 和 validate 都是幂等的；重复运行会覆盖同名输出。若只完成了 build，之后可直接重跑 validate；若 comparison 逻辑中断，只需重新执行 build CLI 即可恢复。

## Remaining Risks

- 当前 B / C / D 的比较仍然建立在同一个 local CSQA-style slice 和同一个 `pilot_distilgpt2_hf` 上。
- 路线推荐是“下一步工程增益”导向，而不是研究结论导向。
- 即使推荐 D，也只意味着“先扩 shared labeled substrate”，不等于已经解决更大规模 supervision 的真实性问题。

## Next Suggested Plan

若 027 完成，下一步建议创建 `.plans/028-labeled-slice-expansion-bootstrap.md`，先把 shared labeled slice 扩到一个更大的、可复用的 local pilot substrate，再让后续 B / C 在上面继续扩。
