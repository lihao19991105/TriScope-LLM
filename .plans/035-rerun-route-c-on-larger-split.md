# 035 Rerun Route C On Larger Split

## Purpose / Big Picture

034 已经明确指出：route B 已在 larger split 上完成 rerun，但 route C 仍停留在较小 substrate，因此 B/C 还不具备真正对称的 larger-split 比较条件。035 的目标就是把 route C 真正接到 current larger labeled split 上，生成 larger-split 版 benchmark-truth-leaning supervised bootstrap artifact。

## Scope

### In Scope

- route C on larger split contract / label definition
- larger-split route C inputs materialization
- larger-split route C rerun and supervised logistic artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- 扩更大 substrate
- 引入 benchmark ground truth
- 切换到更大模型或更大真实实验

## Repository Context

本计划主要衔接：

- `outputs/larger_labeled_split_bootstrap/default/*`
- `outputs/post_rerun_comparison/default/*`
- `outputs/chosen_route_rerun_on_larger_split/default/*`
- `outputs/expanded_route_c_bootstrap/default/*`
- `src/eval/expanded_route_c_bootstrap.py`
- `src/fusion/benchmark_truth_leaning_label.py`
- `src/fusion/feature_alignment.py`
- `scripts/run_reasoning_probe.py`
- `scripts/run_confidence_probe.py`
- `scripts/run_illumination_probe.py`

## Deliverables

- `.plans/035-rerun-route-c-on-larger-split.md`
- `src/eval/rerun_route_c_on_larger_split.py`
- `scripts/build_rerun_route_c_on_larger_split.py`
- `src/eval/rerun_route_c_on_larger_split_checks.py`
- `scripts/validate_rerun_route_c_on_larger_split.py`
- `larger_split_route_c_plan.json`
- `larger_split_route_c_label_definition.json`
- `larger_split_route_c_readiness_summary.json`
- `larger_split_route_c_dataset.jsonl`
- `larger_split_route_c_summary.json`
- `larger_split_route_c_logistic_predictions.jsonl`
- `larger_split_route_c_logistic_summary.json`
- `larger_split_route_c_model_metadata.json`
- `larger_split_route_c_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize route C on larger split
- [x] Milestone 2: run larger-split route C rerun
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 035 不需要设计新的 route C supervision semantics；当前 benchmark-truth-leaning label builder 已经能直接消费 labeled illumination raw results 和 aligned fusion rows。
- 031 已经把 labeled illumination contracts 扩到了 40 rows，因此 larger-split route C 的 contract-level dataset 可以自然达到 `40 rows / 20 base samples`。
- 035 的主要新增不是 label semantics，而是把 route C 从 `expanded substrate` 推进到 `larger substrate`，从而恢复 B/C 的 substrate 对称性。

## Decision Log

- 决策：035 继续使用 `task_answer_incorrect_label` 作为 route C 的 supervision label。
  - 原因：该 label 已经是当前最 truth-leaning 的低成本路径，且与 larger split 的 labeled illumination contracts 直接兼容。
  - 影响范围：label definition、summary、comparison 语义。

- 决策：035 复用 029 的 route C orchestration，但把 substrate 切换为 031 的 larger split。
  - 原因：这样能最大限度复用已验证的 probe / feature / alignment / logistic 路径，不重写稳定模块。
  - 影响范围：runner、validator、artifact 命名。

## Plan of Work

先读取 031 的 `materialized_larger_labeled_inputs/` 和 034 的 recommendation，确认当前 next step 的确是 rerun route C on larger split。然后把这些 larger-split inputs 复制到 035 的 materialized inputs 目录，并生成 route C plan / label definition / readiness summary。接着复用 reasoning / confidence / illumination / labeled illumination 的 stable rerun 链路，在 larger split 上跑出新的 fusion dataset，再用 benchmark-truth-leaning label builder 生成 contract-level supervised dataset，最后运行 logistic bootstrap，并补 acceptance、repeatability 与 README。

## Validation and Acceptance

- `build_rerun_route_c_on_larger_split.py --help` 可正常显示
- `validate_rerun_route_c_on_larger_split.py --help` 可正常显示
- 至少生成：
  - `larger_split_route_c_plan.json`
  - `larger_split_route_c_label_definition.json`
  - `larger_split_route_c_readiness_summary.json`
  - `larger_split_route_c_dataset.jsonl`
  - `larger_split_route_c_summary.json`
  - `larger_split_route_c_logistic_predictions.jsonl`
  - `larger_split_route_c_logistic_summary.json`
  - `larger_split_route_c_model_metadata.json`
  - `larger_split_route_c_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

035 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若单个 probe 阶段失败，可直接重跑 build CLI。

## Remaining Risks

- larger-split route C 仍然只是 benchmark-truth-leaning proxy，不是 benchmark ground truth。
- 当前 rerun 仍然受 local curated split、轻量模型和 self-fit logistic 限制。

## Next Suggested Plan

若 035 完成，下一步建议创建 `.plans/036-symmetric-larger-split-comparison.md`，把 old route B、larger route B、larger route C 放到真正对称的 substrate 语境里统一比较。
