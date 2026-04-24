# 028 Labeled Slice Expansion Bootstrap

## Purpose / Big Picture

027 会说明：当前 route B 和 route C 都已经在当前 `5`-sample local slice 上证明了自身可运行，但它们下一步的共同瓶颈已经变成 shared labeled substrate 太小。028 的目标不是立刻再跑一轮更大的 supervision baseline，而是先把 shared labeled slice 扩大并 materialize 成一套可复用的 bridge inputs，让后续 route B / C 能在更大的 base 上继续执行。

## Scope

### In Scope

- 10-row expanded local labeled slice
- reasoning / confidence / illumination / labeled-illumination bridge contracts
- 最小 bridge dry-run 验证
- acceptance / repeatability / README / 收口

### Out of Scope

- 新 benchmark 下载
- 更大模型
- 直接运行新的 route B / route C full supervised baseline
- 研究级标签体系

## Repository Context

本计划主要衔接：

- `outputs/pilot_materialization/pilot_csqa_reasoning_local/*`
- `src/eval/pilot_execution.py`
- `src/eval/pilot_extension.py`
- `src/eval/pilot_illumination.py`
- `src/eval/labeled_pilot_bootstrap.py`
- `scripts/run_reasoning_probe.py`
- `scripts/run_confidence_probe.py`
- `scripts/run_illumination_probe.py`

## Deliverables

- `.plans/028-labeled-slice-expansion-bootstrap.md`
- `src/eval/labeled_slice_expansion.py`
- `scripts/build_labeled_slice_expansion.py`
- `src/eval/labeled_slice_expansion_checks.py`
- `scripts/validate_labeled_slice_expansion.py`
- `outputs/labeled_slice_expansion/default/labeled_slice_expansion_plan.json`
- `outputs/labeled_slice_expansion/default/labeled_slice_expansion_readiness_summary.json`
- `outputs/labeled_slice_expansion/default/expanded_labeled_slice.jsonl`
- `outputs/labeled_slice_expansion/default/expanded_labeled_slice_summary.json`
- `outputs/labeled_slice_expansion/default/bridge_artifact_summary.json`
- `outputs/labeled_slice_expansion/default/materialized_labeled_slice_inputs/*`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: materialize expanded labeled slice
- [x] Milestone 2: bridge artifacts / dry-run executability
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- route D 不需要新模型也不需要新下载，只要把当前 local CSQA-style pilot slice 扩到 `10` 条，并且按现有 builder 重新 materialize 一套 bridge contracts，就已经能为后续 B / C 同时解锁更大的输入空间。
- 现有 reasoning / confidence / illumination / labeled-illumination contract builder 都已经稳定存在，因此 028 的主要工作不是发明新 schema，而是把 expanded slice 做成兼容这些 builder 的 shared substrate。
- 使用 dry-run probe 即可低成本验证 expanded contracts 已经能进入现有执行链路，而不需要现在就再跑一轮真实模型执行。

## Decision Log

- 决策：028 直接创建 10-row expanded slice，而不是只写 plan 不落数据。
  - 原因：当前最需要的是一个真正可复用的 shared substrate，而不是只停留在 recommendation。
  - 影响范围：`expanded_labeled_slice.jsonl`、bridge contracts、README。

- 决策：028 用 bridge dry-run 验证 executability，而不是立刻跑新一轮 full probe。
  - 原因：当前阶段要证明 expanded substrate 已接入现有链路，dry-run 的信息量已经足够且成本更低。
  - 影响范围：`bridge_dry_run/*`、acceptance / repeatability。

## Plan of Work

先读取当前 5-row local slice，补入额外的 5 条本地 curated CSQA-style 样本，形成一个 10-row expanded slice。然后复用稳定的 builder，生成 reasoning / confidence / illumination / labeled-illumination query contracts，并把它们放进 `materialized_labeled_slice_inputs/` 作为后续 route B / C 的 shared bridge artifacts。接着通过现有 probe 模块做 dry-run，验证这些 expanded contracts 可以被现有 CLI 正常消费。最后补 validator、repeatability 和 README。

## Concrete Steps

1. 新增 `src/eval/labeled_slice_expansion.py`，实现 expanded slice materialization 和 bridge dry-run。
2. 新增 `scripts/build_labeled_slice_expansion.py` 作为 CLI。
3. 新增 validator：
   - `src/eval/labeled_slice_expansion_checks.py`
   - `scripts/validate_labeled_slice_expansion.py`
4. 运行 build CLI 生成 default / default_repeat / repeatability artifact。
5. 更新 README 与本计划。

## Validation and Acceptance

- `build_labeled_slice_expansion.py --help` 可正常显示
- `validate_labeled_slice_expansion.py --help` 可正常显示
- default run 至少生成：
  - `labeled_slice_expansion_plan.json`
  - `labeled_slice_expansion_readiness_summary.json`
  - `expanded_labeled_slice.jsonl`
  - `expanded_labeled_slice_summary.json`
  - `bridge_artifact_summary.json`
- `materialized_labeled_slice_inputs/` 中至少包含：
  - `csqa_reasoning_pilot_slice.jsonl`
  - `reasoning_query_contracts.jsonl`
  - `confidence_query_contracts.jsonl`
  - `illumination_query_contracts.jsonl`
  - `labeled_illumination_query_contracts.jsonl`
- bridge dry-run summary 状态必须为 `PASS`
- validator 输出 `artifact_acceptance.json`
- repeatability 输出 `repeatability_summary.json`

## Idempotence and Recovery

028 的 build 和 validate 都是幂等的；重复运行会覆盖同名输出。若只 materialize 成功但 dry-run 中断，可重跑 build CLI 完整恢复；若只完成 build，可单独再跑 validate。

## Remaining Risks

- expanded slice 仍然是本地 curated pilot substrate，不是 benchmark-scale labeled split。
- 028 只是为后续 B / C 扩展准备更大输入，不等于已经完成更大的 supervised run。
- bridge dry-run 只能证明 executability，不能替代真实模型行为验证。

## Next Suggested Plan

若 028 完成，下一步建议在 expanded slice 上重新 materialize 一版 route B 或 route C，并比较 expanded more-natural / expanded benchmark-truth-leaning supervision 的真实增益。
