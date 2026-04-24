# 029 Expanded Route C Bootstrap

## Purpose / Big Picture

028 已经把 shared labeled substrate 从 5-row 扩到了 10-row，并且把 reasoning / confidence / illumination / labeled-illumination 的 bridge contracts 全部 materialize 出来。029 的目标是把这层 expanded substrate 真正接回 route C，让 expanded benchmark-truth-leaning supervision proxy 第一次形成完整的 runnable bootstrap。

## Scope

### In Scope

- expanded route C 输入契约
- expanded reasoning / confidence / illumination / labeled-illumination 真正 rerun
- expanded real-pilot fusion dataset
- expanded benchmark-truth-leaning dataset / logistic / summary
- acceptance / repeatability / README / 收口

### Out of Scope

- benchmark ground truth
- 更大模型 / 更大数据下载
- route B rerun
- 新的监督路线设计

## Repository Context

本计划主要衔接：

- `outputs/labeled_slice_expansion/default/materialized_labeled_slice_inputs/*`
- `outputs/benchmark_truth_leaning_label_bootstrap/*`
- `src/probes/`
- `src/features/`
- `src/fusion/feature_alignment.py`
- `src/fusion/benchmark_truth_leaning_label.py`
- `scripts/`

## Deliverables

- `.plans/029-expanded-route-c-bootstrap.md`
- `src/eval/expanded_route_c_bootstrap.py`
- `scripts/build_expanded_route_c_bootstrap.py`
- `src/eval/expanded_route_c_bootstrap_checks.py`
- `scripts/validate_expanded_route_c_bootstrap.py`
- `expanded_route_c_selection.json`
- `expanded_route_c_label_definition.json`
- `expanded_route_c_readiness_summary.json`
- `expanded_benchmark_truth_leaning_dataset.jsonl`
- `expanded_benchmark_truth_leaning_summary.json`
- `expanded_benchmark_truth_leaning_logistic_predictions.jsonl`
- `expanded_benchmark_truth_leaning_logistic_summary.json`
- `expanded_benchmark_truth_leaning_model_metadata.json`
- `expanded_route_c_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize expanded route C contract
- [x] Milestone 2: runnable expanded route C bootstrap
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 029 不需要重新设计 route C label logic；核心 label 仍然是 `task_answer_incorrect_label`，只是把输入 substrate 从 old 5-sample slice 换成了 028 的 expanded 10-sample substrate。
- expanded route C 的关键不是单独 rerun illumination，而是需要 reasoning / confidence / illumination 三路都在 expanded slice 上真实 rerun，这样 contract-level correctness label 才能接回 expanded real-pilot fusion features。
- 当前 expanded route C 在 row 级别上会自然从 old `10` row 增长到 `20` row，因为 labeled illumination contract 仍然是 `2 x base_sample_id` 的结构。

## Decision Log

- 决策：029 复用 028 的 `materialized_labeled_slice_inputs/` 作为全部输入源。
  - 原因：这样能最大化复用 028 的 shared substrate，不引入新的输入岔路。
  - 影响范围：CLI 默认路径、config snapshot、readiness summary。

- 决策：029 继续使用 `task_answer_incorrect_label` 作为 route C label。
  - 原因：当前要验证的是 expanded substrate 是否能把 route C rerun 放大，而不是更换 supervision semantics。
  - 影响范围：dataset schema、summary、comparison artifact。

## Plan of Work

先在计划层定义 expanded route C 的 selection / definition / readiness，并把 028 的 expanded contracts 拷贝进本次运行目录作为 materialized inputs。然后真实 rerun expanded reasoning / confidence / illumination 和 expanded labeled illumination，再对三路特征做 inner-join 得到 expanded real-pilot fusion dataset。最后在这个 expanded fusion dataset 上复用 benchmark-truth-leaning label builder 与 logistic bootstrap，产出 expanded route C 的 supervised artifact，并补 acceptance / repeatability / README。

## Validation and Acceptance

- `build_expanded_route_c_bootstrap.py --help` 可正常显示
- `validate_expanded_route_c_bootstrap.py --help` 可正常显示
- M1 至少生成：
  - `expanded_route_c_selection.json`
  - `expanded_route_c_label_definition.json`
  - `expanded_route_c_readiness_summary.json`
- M2 至少生成：
  - `expanded_benchmark_truth_leaning_dataset.jsonl`
  - `expanded_benchmark_truth_leaning_summary.json`
  - `expanded_benchmark_truth_leaning_logistic_predictions.jsonl`
  - `expanded_benchmark_truth_leaning_logistic_summary.json`
  - `expanded_route_c_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

029 的 build 和 validate 都是幂等的；重复运行会覆盖同名输出。若 rerun 中断，可直接重跑 build CLI 恢复；若只完成 build，可单独执行 validate。

## Remaining Risks

- expanded route C 仍然只是 `benchmark_truth_leaning_supervision_proxy`，不是 benchmark ground truth。
- 当前 expanded substrate 虽然从 5 base sample 增长到 10，但仍然是本地 pilot-level curated slice。
- logistic 仍是 self-fit bootstrap，只证明 executability，不证明泛化。

## Next Suggested Plan

若 029 完成，下一步建议创建 `.plans/030-expanded-supervision-comparison.md`，把 route B、old route C、expanded route C 放到同一层做统一比较。
