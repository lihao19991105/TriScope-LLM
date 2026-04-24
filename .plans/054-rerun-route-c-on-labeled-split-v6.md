# 054 Rerun Route C On Labeled Split V6

## Purpose / Big Picture

053 已把 shared labeled substrate 从 60 行提升到 70 行，并确认 route B / route C / fusion builder 仍然可接。054 的任务是把 route C 真正 rerun 到 `larger_labeled_split_v6` 上，让 benchmark-truth-leaning proxy supervision 在 v6 substrate 上第一次真实存在，而不是只停留在 substrate bootstrap。

## Scope

### In Scope

- route C on v6 contract / label definition
- v6 route C inputs materialization
- route C on v6 rerun and logistic artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- route B on v6 rerun
- v6 对称比较
- benchmark ground truth 接入
- 更大模型 / 更大数据规模

## Repository Context

本计划主要衔接：

- `outputs/post_v5_next_step_bootstrap/default/*`
- `src/eval/rerun_route_c_on_labeled_split_v5.py`
- `src/fusion/benchmark_truth_leaning_label.py`
- `src/probes/*.py`
- `src/features/*.py`

## Deliverables

- `.plans/054-rerun-route-c-on-labeled-split-v6.md`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`
- `scripts/build_rerun_route_c_on_labeled_split_v6.py`
- `src/eval/rerun_route_c_on_labeled_split_v6_checks.py`
- `scripts/validate_rerun_route_c_on_labeled_split_v6.py`
- `route_c_v6_plan.json`
- `route_c_v6_label_definition.json`
- `route_c_v6_readiness_summary.json`
- `route_c_v6_dataset.jsonl`
- `route_c_v6_summary.json`
- `route_c_v6_logistic_predictions.jsonl`
- `route_c_v6_logistic_summary.json`
- `route_c_v6_model_metadata.json`
- `route_c_v6_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize route C on v6
- [x] Milestone 2: run route C on v6 rerun
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- v6 substrate 已经预先提供了 `70` 条 reasoning / confidence / illumination query contracts，以及 `140` 条 labeled illumination contracts，因此 054 不需要发明新的 route C contract 语义。
- route C 在 v6 上的主要增量仍然不是监督定义变化，而是 substrate 从 `60` 个 base samples 增长到 `70` 个 base samples。
- route C v6 最终稳定产出 `140` 条 contract-level rows、`70` 个 base samples，logistic `mean_prediction_score = 0.09772102727969277`，acceptance / repeatability 都为 `PASS`。

## Decision Log

- 决策：054 继续沿用 benchmark-truth-leaning proxy supervision 语义，只切换 substrate 到 v6。
  - 原因：当前目标是验证更大 shared substrate 的收益，而不是改变 route C 的标签哲学。
  - 影响范围：route C v6 的 label definition、summary 与后续 comparison 语义。

## Plan of Work

先读取 053 的 `post_v5_next_step_plan.json` 和 `materialized_post_v5_inputs/`，确认当前 substrate 已经切到 `larger_labeled_split_v6`。然后复制 v6 inputs，生成 route C v6 plan / label definition / readiness summary。接着复用 reasoning / confidence / illumination / labeled illumination 的稳定 rerun 链路，在 v6 substrate 上生成 fusion dataset、benchmark-truth-leaning dataset 和 logistic bootstrap。最后补 acceptance、repeatability 与 README。

## Concrete Steps

1. 更新 `src/eval/rerun_route_c_on_labeled_split_v6.py` 与配套 CLI / validator。
2. 运行 `build_rerun_route_c_on_labeled_split_v6.py` 生成 route C v6 artifact。
3. 运行同一 build CLI 的 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_rerun_route_c_on_labeled_split_v6.py --help` 可正常显示
- `validate_rerun_route_c_on_labeled_split_v6.py --help` 可正常显示
- 至少生成：
  - `route_c_v6_plan.json`
  - `route_c_v6_label_definition.json`
  - `route_c_v6_readiness_summary.json`
  - `route_c_v6_dataset.jsonl`
  - `route_c_v6_summary.json`
  - `route_c_v6_logistic_predictions.jsonl`
  - `route_c_v6_logistic_summary.json`
  - `route_c_v6_model_metadata.json`
  - `route_c_v6_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

054 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 rerun 中断，可直接重跑 build CLI；若只需要复核 artifact 完整性，可直接重跑 validate CLI。

## Remaining Risks

- route C v6 仍然只是 benchmark-truth-leaning proxy，不是 benchmark ground truth。
- route C v6 仍受 local curated split、`pilot_distilgpt2_hf` 和 self-fit logistic 限制。

## Next Suggested Plan

若 054 完成，下一步建议创建 `.plans/055-rerun-route-b-on-labeled-split-v6.md`，把 route B 也 rerun 到同一 v6 substrate 上，从而形成第一次真正的 v6 对称比较条件。
