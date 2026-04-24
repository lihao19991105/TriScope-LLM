# 031 Larger Labeled Split Bootstrap

## Purpose / Big Picture

030 已经明确指出：当前 expanded route C 已经把 10-row substrate 基本吃满，下一步真正的共同 bottleneck 是 shared labeled substrate 仍然太小。031 的目标是把当前 10-row substrate 再向上扩一层，生成一个更大的、仍然可控且与现有 route B / route C / fusion builder 兼容的 larger labeled split。

## Scope

### In Scope

- larger labeled split contract 定义
- 20-row local curated larger split materialization
- reasoning / confidence / illumination / labeled-illumination bridge contracts
- route B / route C / fusion compatibility summary
- acceptance / repeatability / README / 收口

### Out of Scope

- 真实 rerun route B
- 真实 rerun route C
- benchmark-scale 数据接入
- 新模型 / 大规模训练

## Repository Context

本计划主要衔接：

- `outputs/labeled_slice_expansion/default/materialized_labeled_slice_inputs/*`
- `src/eval/labeled_slice_expansion.py`
- `src/eval/pilot_execution.py`
- `src/eval/pilot_extension.py`
- `src/eval/pilot_illumination.py`
- `src/eval/labeled_pilot_bootstrap.py`
- `scripts/run_reasoning_probe.py`
- `scripts/run_confidence_probe.py`
- `scripts/run_illumination_probe.py`

## Deliverables

- `.plans/031-larger-labeled-split-bootstrap.md`
- `src/eval/larger_labeled_split_bootstrap.py`
- `scripts/build_larger_labeled_split_bootstrap.py`
- `src/eval/larger_labeled_split_bootstrap_checks.py`
- `scripts/validate_larger_labeled_split_bootstrap.py`
- `larger_labeled_split_plan.json`
- `larger_labeled_split_definition.json`
- `larger_labeled_split_readiness_summary.json`
- `larger_labeled_split.jsonl`
- `larger_labeled_split_summary.json`
- `larger_labeled_bridge_artifact_summary.json`
- `larger_split_route_compatibility_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: larger split contract / readiness
- [x] Milestone 2: materialize larger split / bridge / compatibility
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 031 不需要重写 route B / route C builder；只要 larger split 的字段与 028 一致，现有 builder 就可以直接复用。
- 当前最自然的“更大但仍可控”对象是把 substrate 从 10-row 抬到 20-row，这样 route B 预期可达 20 sample-level rows，route C 预期可达 40 contract-level rows。
- 由于本轮重点是 substrate bootstrap，不是 full rerun，因此 bridge dry-run 已足以证明 larger split 可以被现有 route B / route C / fusion pipeline 消费。

## Decision Log

- 决策：031 选择 20-row larger split 作为当前最小可行 larger split。
  - 原因：它在当前 10-row expanded substrate 基础上继续翻倍，增量明显，同时仍保持本地 curated 可控成本。
  - 影响范围：split contract、bridge counts、compatibility summary。

- 决策：031 继续使用现有 builder + dry-run compatibility，而不是直接 rerun route B/C。
  - 原因：本轮目标是先把 substrate 做大并验证兼容性，rerun 决策留给 032。
  - 影响范围：bridge dry-run outputs、route compatibility summary。

## Plan of Work

先读取 028 的 10-row substrate，把它与新增 10 条本地 curated CSQA-style 样本组合成 20-row larger labeled split。然后复用稳定 builder，生成 reasoning / confidence / illumination / labeled-illumination query contracts，并把它们放进 `materialized_larger_labeled_inputs/`。接着用 dry-run 方式验证这些 contracts 可以被现有 probe CLI 正常消费，并输出 route B / route C / fusion compatibility summary。最后补 validator、repeatability 和 README。

## Validation and Acceptance

- `build_larger_labeled_split_bootstrap.py --help` 可正常显示
- `validate_larger_labeled_split_bootstrap.py --help` 可正常显示
- 至少生成：
  - `larger_labeled_split_plan.json`
  - `larger_labeled_split_definition.json`
  - `larger_labeled_split_readiness_summary.json`
  - `larger_labeled_split.jsonl`
  - `larger_labeled_split_summary.json`
  - `larger_labeled_bridge_artifact_summary.json`
  - `larger_split_route_compatibility_summary.json`
- `materialized_larger_labeled_inputs/` 至少包含：
  - `csqa_reasoning_pilot_slice.jsonl`
  - `reasoning_query_contracts.jsonl`
  - `confidence_query_contracts.jsonl`
  - `illumination_query_contracts.jsonl`
  - `labeled_illumination_query_contracts.jsonl`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

031 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若 dry-run bridge 中断，可重跑 build CLI；若只完成 build，可单独再跑 validate。

## Remaining Risks

- 当前 larger split 仍然只是 local curated split，不是 benchmark-scale 数据。
- 031 证明的是 compatibility 与 readiness，不是 rerun 结果本身。
- larger split 虽然更大，但仍建立在同一个轻量模型与同一套 prompt stack 假设上。

## Next Suggested Plan

若 031 完成，下一步建议创建 `.plans/032-larger-split-route-rerun-decision.md`，在 larger split 已经存在且兼容性明确的前提下，决定先 rerun route B 还是 route C。
