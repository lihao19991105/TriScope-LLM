# 154 Route-C Frozen Semantic Minimal Real Batched Continuous Regression

## Background

153 已完成最小真实连续执行验证，并给出单一结论 `Minimal real continuous execution validated`。当前下一步是把该验证从“单窗口最小连续”提升到“小批量 batched continuous regression”，用于确认冻结语义与 gate 不变前提下，recoverable/normal/nonrecoverable 三路径在连续批次上仍保持稳定。

## Why 153 enables minimal real batched continuous regression

- 153 已验证真实连续链路下 recoverable boundary 稳定且无 collateral damage。
- 153 已建立可复用的 real-continuous case construction、dataset->gate->logistic 闭环和 case-level 审计格式。
- 因此 154 仅做最小增量：扩展为小批量 batched windows regression，不扩轴、不改语义。

## Frozen semantic / gate / rule scope

- benchmark truth 语义冻结：不改标签定义，不引入语义猜测。
- gate 语义冻结：不改阈值，不改 PASS/BLOCKED 逻辑。
- recoverable-boundary 规则冻结：仅沿用 148/149/150/151/152/153 已确认规则。
- parser normalization 范围冻结：仅使用 conservative normalization 与既有 anti-degradation 允许步骤。
- 不扩模型轴、不扩 budget、不扩 prompt family、不扩 attack family。

## Goal

在冻结语义与 gate 不变前提下完成最小 route_c 真实连续 batched regression，并同时确认：

1. recoverable formatting boundary 在 batched continuous windows 上继续稳定 `pass_formatted_to_parser`。
2. normal 路径继续 `pass_raw_to_parser`，无新增误伤。
3. nonrecoverable 路径继续 `degeneration_blocked`，无漏放。
4. batch-level 与 path-level 无新增 drift、handoff contract violation、label health anomaly。

## Non-goals

- 不修改 benchmark truth 语义。
- 不修改 gate 判定逻辑或阈值。
- 不扩大战线到 route_b / 7B/8B / 大规模稳定性工程。
- 不做新主实验矩阵、时间分离 replay 或大批量 rerun。
- 不覆盖 148~153 既有 artifacts。

## Minimal real batched continuous regression design

- 数据来源：复用稳定 real run `extension_rerun_01`。
- batched continuous windows：构造两个最小批次（batch_window_01 / batch_window_02）。
- 每个批次覆盖 recoverable + normal + nonrecoverable 路径；总样例规模保持小批量（目标 12 条）。
- 受限事实：当前 real run 只有一个稳定 nonrecoverable 真值锚点（`illumination_0000`），第二批次复用该 nonrecoverable 锚点用于 guardrail 回归，不改语义。
- 每条样例记录来源、窗口、位置、真实 prompt 锚点、是否真实输入、参考阶段映射。

## Batched continuous regression criteria

1. recoverable criteria
- 必须保持 `pass_formatted_to_parser`。
- 不允许回退到 `degeneration_blocked`。
- 不允许语义猜测恢复。

2. normal criteria
- 必须保持 `pass_raw_to_parser`。
- 不允许新增 false block。

3. nonrecoverable criteria
- 必须保持 `degeneration_blocked`。
- 不允许漏放到 parser。

4. batch/path consistency criteria
- batch window 内有序 case 均满足预期。
- 不得出现 path-level handoff drift 或 parser-source drift。
- 不得出现 handoff contract violation / label health anomaly。
- gate=PASS 后才允许 logistic continuation。

## Validation plan

1. 冻结 154 suite 与 rules（M1）。
2. 跑最小 batched continuous regression 主流程（dataset -> gate -> logistic），输出 case-level details（M2）。
3. 生成 post-analysis，输出单一 verdict 与唯一 recommendation（M3）。

## Risks

- 154 仍是小批量真实连续回归，不等价于长期稳定性结论。
- nonrecoverable 真实锚点稀缺，batch 间需复用单锚点进行 guardrail 检测。
- 若出现批次级 drift，结论必须降级为 `Partially validated` 或 `Not validated`。

## Milestones

- [x] M1: minimal real batched continuous suite and criteria frozen
- [x] M2: minimal real batched continuous regression completed
- [x] M3: single verdict and single recommendation completed

## Completion Notes

- 154 采用两个批次窗口（`batch_window_01` / `batch_window_02`），共 12 条样例：recoverable=4、normal=4、nonrecoverable=4。
- 真实锚点来自稳定 real run `extension_rerun_01` 的 `illumination_0000~0005`；nonrecoverable 真值锚点仅有 `illumination_0000`，在第二批次按冻结语义复用。
- 主流程结果：
	- `recoverable_real_continuous_pass_rate = 1.0`
	- `normal_real_continuous_pass_rate = 1.0`
	- `nonrecoverable_real_continuous_block_rate = 1.0`
	- `mismatch_type_counts = {match: 12}`
- 一致性与副作用检查通过：
	- `gate_status = PASS`
	- `logistic_status = PASS`
	- `path_level_drift_detected = false`
	- `parser_source_drift_detected = false`
	- `handoff_contract_violation_count = 0`
	- `label_health_anomaly_count = 0`
	- `new_false_block_count = 0`
	- `new_leak_count = 0`
- 154 单一结论：`Minimal real batched continuous regression validated`。
- 154 唯一下一步建议：`下一步进入冻结语义与 gate 不变前提下的最小 route_c batched continuous 稳定性复检`。

## Exit criteria

- 154 计划文件完整，scope 与 non-goals 明确。
- 已产出 suite / rules / summary / details / report / verdict / recommendation 七类 artifacts。
- focused batched continuous regression 与 minimal collateral analysis 均完成。
- 最终仅输出一个 verdict 与唯一下一步建议。
- 全程未改 benchmark truth 语义、未改 gate 语义、未做轴向扩张。