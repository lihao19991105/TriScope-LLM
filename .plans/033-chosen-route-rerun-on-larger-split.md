# 033 Chosen Route Rerun On Larger Split

## Purpose / Big Picture

032 已经给出明确 recommendation：在 larger labeled split 已存在的前提下，下一步最有信息增益的是先 rerun route B。033 的目标就是把这个 recommendation 变成真实 artifact，让 route B 第一次在 20-row larger substrate 上完成对称 rerun，并生成新的 supervised bootstrap 结果。

## Scope

### In Scope

- chosen route B rerun contract 定义
- larger split 上的 reasoning / confidence / illumination rerun
- larger-split real-pilot fusion dataset
- expanded more-natural labeled dataset / logistic / summary artifact
- acceptance / repeatability / README / 收口

### Out of Scope

- rerun route C on the larger split
- 更大模型 / 更大真实数据
- 新的 supervision 语义设计

## Repository Context

本计划主要衔接：

- `outputs/larger_labeled_split_bootstrap/default/*`
- `outputs/larger_split_route_rerun_decision/default/*`
- `outputs/more_natural_label_bootstrap/default/*`
- `src/eval/expanded_route_c_bootstrap.py`
- `src/fusion/more_natural_label_fusion.py`
- `src/fusion/feature_alignment.py`
- `scripts/run_reasoning_probe.py`
- `scripts/run_confidence_probe.py`
- `scripts/run_illumination_probe.py`

## Deliverables

- `.plans/033-chosen-route-rerun-on-larger-split.md`
- `src/eval/chosen_route_rerun_on_larger_split.py`
- `scripts/build_chosen_route_rerun_on_larger_split.py`
- `src/eval/chosen_route_rerun_on_larger_split_checks.py`
- `scripts/validate_chosen_route_rerun_on_larger_split.py`
- `chosen_route_rerun_plan.json`
- `chosen_route_rerun_readiness_summary.json`
- `expanded_more_natural_dataset.jsonl`
- `expanded_more_natural_summary.json`
- `expanded_more_natural_logistic_predictions.jsonl`
- `expanded_more_natural_logistic_summary.json`
- `chosen_route_rerun_run_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize chosen route B rerun on larger split
- [x] Milestone 2: run chosen route rerun and emit supervised artifacts
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 033 不需要发明新的 route B builder；当前 more-natural supervision builder 已经能直接消费 fusion dataset + three-module raw outputs + pilot slice。
- 031 的 larger split 已经把 query contracts 与 labeled illumination contracts 一次性准备好，因此 033 的关键只是把 stable probe链路真正 rerun 一遍。
- 与 029 的 expanded route C 相比，033 的主要增益不是“更 truth-leaning”，而是把 route B 从 5-row 直接抬到 20-row，并形成更对称的比较基础。

## Decision Log

- 决策：033 固定 chosen route 为 `B`。
  - 原因：032 已明确 route B 在 larger split 上拥有更高的 comparative information gain。
  - 影响范围：plan 命名、run summary、next-step 比较语境。

- 决策：033 复用 expanded route C 的 orchestration 结构，但 supervision head 改为 more-natural label builder。
  - 原因：这样能最大化复用已验证的 probe / feature / alignment 路径，同时避免对稳定模块做重构。
  - 影响范围：`src/eval/chosen_route_rerun_on_larger_split.py`、CLI、validator。

## Plan of Work

先把 031 的 `materialized_larger_labeled_inputs/` 作为 shared substrate 复制到 033 的 materialized inputs 目录，并生成 chosen route plan / readiness summary。然后在 larger split 上顺序 rerun reasoning、confidence、illumination 三条 probe，提取 feature 后构建 inner-join real-pilot fusion dataset。接着把该 fusion dataset 与 larger split pilot slice 和三路 raw outputs 送入 more-natural label builder，生成 expanded route-B labeled dataset，并运行 logistic bootstrap。最后补 acceptance、repeatability 与 README。

## Concrete Steps

1. 新建 `src/eval/chosen_route_rerun_on_larger_split.py`
2. 新建 `scripts/build_chosen_route_rerun_on_larger_split.py`
3. 新建 validator 与 CLI
4. 运行：
   - `python3 scripts/build_chosen_route_rerun_on_larger_split.py --output-dir outputs/chosen_route_rerun_on_larger_split/default`
   - `python3 scripts/build_chosen_route_rerun_on_larger_split.py --output-dir outputs/chosen_route_rerun_on_larger_split/default_repeat`
   - `python3 scripts/validate_chosen_route_rerun_on_larger_split.py --run-dir ... --compare-run-dir ... --output-dir ...`
5. 检查 summary、predictions、run summary 与 validator 输出

## Validation and Acceptance

- `build_chosen_route_rerun_on_larger_split.py --help` 可正常显示
- `validate_chosen_route_rerun_on_larger_split.py --help` 可正常显示
- 至少生成：
  - `chosen_route_rerun_plan.json`
  - `chosen_route_rerun_readiness_summary.json`
  - `expanded_more_natural_dataset.jsonl`
  - `expanded_more_natural_summary.json`
  - `expanded_more_natural_logistic_predictions.jsonl`
  - `expanded_more_natural_logistic_summary.json`
  - `chosen_route_rerun_run_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

033 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若单个 probe 阶段失败，可直接重跑整个 build CLI；已有结果不影响恢复。

## Remaining Risks

- rerun 出来的 route B 仍然只是 more-natural supervision proxy，不是 benchmark ground truth。
- 当前 larger split 仍然只是 local curated split，且仍然绑定 `pilot_distilgpt2_hf`。
- rerun 完成后，route B 与 route C 仍然可能处在不同 substrate 层级，需要 034 明确下一步怎么比较。

## Next Suggested Plan

若 033 完成，下一步建议创建 `.plans/034-post-rerun-comparison.md`，把 new route-B rerun、old route B、expanded route C 和 larger split 条件放到同一层统一比较。
