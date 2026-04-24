# 026 Benchmark Truth Leaning Label Bootstrap

## Purpose / Big Picture

025 会说明：在当前 route A / B / C 的比较下，最值得推进的是方向 C，也就是第一条 benchmark-truth-leaning label bootstrap。026 的目标是在不引入新资源的前提下，把这条路线 materialize，并让它第一次产出可执行的 supervised artifact。

## Scope

### In Scope

- benchmark-truth-leaning label selection / definition / readiness
- contract-level labeled fusion dataset materialization
- 最小 supervised logistic bootstrap
- acceptance / repeatability / README / 收口

### Out of Scope

- benchmark ground truth
- 大规模 benchmark 监督实验
- 更大模型 / 更大数据切片

## Repository Context

本计划将衔接：

- `outputs/labeled_pilot_runs/*`
- `outputs/controlled_supervision_expansion/*`
- `outputs/supervision_route_comparison/*`
- `outputs/pilot_materialization/*`
- `src/fusion/`
- `scripts/`

## Deliverables

- `.plans/026-benchmark-truth-leaning-label-bootstrap.md`
- `src/fusion/benchmark_truth_leaning_label.py`
- `scripts/build_benchmark_truth_leaning_label_bootstrap.py`
- `src/fusion/benchmark_truth_leaning_label_checks.py`
- `scripts/validate_benchmark_truth_leaning_label_bootstrap.py`
- `benchmark_truth_leaning_label_selection.json`
- `benchmark_truth_leaning_label_definition.json`
- `benchmark_truth_leaning_readiness_summary.json`
- `benchmark_truth_leaning_dataset.jsonl`
- `benchmark_truth_leaning_summary.json`
- `benchmark_truth_leaning_logistic_predictions.jsonl`
- `benchmark_truth_leaning_logistic_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize benchmark-truth-leaning label route
- [x] Milestone 2: runnable supervised bootstrap
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 当前 C 路线完全不需要新下载：`outputs/labeled_pilot_runs/default/illumination_probe/raw_results.jsonl` 已经包含 `10` 条 contract-level real responses。
- 使用同一份 labeled illumination raw results，可以直接根据 `query_answer_key` 定义 contract-level `task_answer_incorrect_label`，类别分布为 `6 / 4`。
- 这意味着 C 既比 current B 更贴近 truth，又和 current A 一样具备 `10` 条 row 规模。
- current 10-row contract-level route 仍会复用 reasoning / confidence base features，但这一点可以诚实保留在 schema 和 summary 里。

## Decision Log

- 决策：026 选择 `task_answer_incorrect_label` 作为 benchmark-truth-leaning label。
  - 原因：它直接由 query answer correctness 决定，比 controlled label 和 sample-level proxy 都更接近 task truth。
  - 影响范围：dataset schema、summary、README。

- 决策：026 在 `base_sample_id + contract_variant` 层 materialize dataset。
  - 原因：当前可执行 truth-leaning signal 来自 labeled illumination contract rows，天然是 contract-level。
  - 影响范围：dataset、prediction schema、validator。

## Plan of Work

先把 selection / definition / readiness 结构化落盘，明确当前 label 是 contract-level answer correctness。然后把 10 条 labeled illumination rows 接回 expanded real-pilot fusion 的 reasoning / confidence base features，生成 benchmark-truth-leaning labeled fusion dataset，并在上面跑一版最小 logistic bootstrap。最后补 acceptance / repeatability 和 README。

## Validation and Acceptance

- `build_benchmark_truth_leaning_label_bootstrap.py --help` 可正常显示
- `validate_benchmark_truth_leaning_label_bootstrap.py --help` 可正常显示
- M1 至少成功生成：
  - `benchmark_truth_leaning_label_selection.json`
  - `benchmark_truth_leaning_label_definition.json`
  - `benchmark_truth_leaning_readiness_summary.json`
- M2 至少成功生成：
  - `benchmark_truth_leaning_dataset.jsonl`
  - `benchmark_truth_leaning_summary.json`
  - `benchmark_truth_leaning_logistic_predictions.jsonl`
  - `benchmark_truth_leaning_logistic_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

### Validation Snapshot

- `outputs/benchmark_truth_leaning_label_bootstrap/default/benchmark_truth_leaning_summary.json`
  - `num_rows = 10`
  - `label_name = task_answer_incorrect_label`
  - `class_balance = {label_0: 6, label_1: 4}`
- `outputs/benchmark_truth_leaning_label_bootstrap/default/benchmark_truth_leaning_logistic_summary.json`
  - `summary_status = PASS`
  - `num_predictions = 10`
  - `mean_prediction_score = 0.4290342710148841`
- `outputs/benchmark_truth_leaning_label_bootstrap/repeatability_default/repeatability_summary.json`
  - `all_key_metrics_match = true`

## Remaining Risks

- 当前 label 仍然只是 benchmark-truth-leaning proxy，不是 benchmark ground truth。
- 当前 10 行 dataset 依然复用 reasoning / confidence base features到 contract variants。
- 当前 slice 仍然很小，模型仍然很轻，因此 logistic 仍只是 bootstrap executability 证明。

## Next Suggested Plan

若 026 完成，下一步建议比较 B 与 C 的实际监督增益差异，并决定是否要开始 materialize 更接近 benchmark-scale 的 labeled slice。
