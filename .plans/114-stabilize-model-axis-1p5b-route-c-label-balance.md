# 114 Stabilize Model-Axis 1.5B Route-C Label Balance

## Purpose / Big Picture

113 已确认 1.5B route_c portability 在 contract、ready-local 和 ready-run 层面都已打通，但小预算 precheck 仍在 benchmark-truth-leaning labels 上塌成单类。114 的目标是在不扩新实验轴、不重做 route_b 的前提下，用最小改动把 route_c 小预算 precheck 先推进到“至少两类可分”的状态。

## Scope

### In Scope

- 诊断 113 route_c precheck 的单类塌缩直接成因。
- 明确可调旋钮：precheck-budget、selection、fallback、truth-leaning label parsing。
- 实现最小 route_c stabilization 逻辑并生成 balanced candidate / precheck artifact。

### Out of Scope

- 3B / 7B 模型切换。
- fusion 同轴扩张。
- proxy substrate 扩容。
- route_c 全量大规模执行。

## Repository Context

- `.plans/112-confirm-model-axis-1p5b-route-b-stability.md`
- `.plans/113-route-c-portability-bootstrap.md`
- `src/eval/model_axis_1p5b_route_b_stabilization.py`
- `src/eval/model_axis_1p5b_route_c_portability.py`
- `src/eval/rerun_route_c_on_labeled_split_v6.py`
- `src/fusion/benchmark_truth_leaning_label.py`
- `outputs/model_axis_1p5b_route_c_portability/default/*`

## Deliverables

- `.plans/114-stabilize-model-axis-1p5b-route-c-label-balance.md`
- `src/eval/model_axis_1p5b_route_c_stabilization.py`
- `scripts/build_model_axis_1p5b_route_c_stabilization.py`
- `outputs/model_axis_1p5b_route_c_stabilization/default/route_c_label_collapse_diagnosis.json`
- `outputs/model_axis_1p5b_route_c_stabilization/default/route_c_label_balance_recovery_plan.json`
- `outputs/model_axis_1p5b_route_c_stabilization/default/route_c_selection_knobs_summary.json`
- `outputs/model_axis_1p5b_route_c_stabilization/default/route_c_balanced_candidate_dataset.jsonl`
- `outputs/model_axis_1p5b_route_c_stabilization/default/route_c_balanced_candidate_summary.json`
- `outputs/model_axis_1p5b_route_c_stabilization/default/route_c_label_balance_precheck.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: diagnose route_c label collapse and define the smallest viable recovery path
- [x] Milestone 2: implement stabilization and emit balanced candidate / precheck artifacts
- [ ] Milestone 3: acceptance / repeatability / README / 收口

## Decision Log

- 决策：114 优先复用 route_b 的稳健 option parser 经验，但不直接照搬 route_b 的 sample-level 选择规则。
  - 原因：route_c 的塌缩发生在 contract-level benchmark-truth-leaning labels，修复点既包括 parser，也包括 1.5B 下的 labeled subset 选择。
- 决策：114 优先通过 route_c labeled illumination 的最小扫描来恢复两类，而不是直接扩预算到全量 route_c rerun。
  - 原因：当前目标是先把 precheck 过掉并找到最小可执行入口，而不是一步做完整 route_c execution。

## Validation and Acceptance

- `python3 scripts/build_model_axis_1p5b_route_c_stabilization.py --help` 可正常显示。
- 产物目录包含 diagnosis / recovery / knobs / balanced candidate / precheck。
- precheck 明确回答：当前 class_balance 是否已至少两类，是否足以进入 115。

## Remaining Risks

- 即便 114 恢复两类，route_c 在 1.5B 下的 truth-leaning labels 仍可能对 seed 或预算敏感。
- 若 1.5B 在全体 labeled contracts 上仍然近乎全对，114 可能只能把阻塞解释得更清楚，而不能直接解锁 115。

## Outcome Snapshot

- 114 已确认 113 的 route_c 单类塌缩是双因素问题：
  - strict parser 把前缀回答全部漏掉，导致 `24/24 -> label_1`
  - 修复 parser 后，原 12-base 子集又在真实 1.5B 输出下变成 `24/24 -> label_0`
- 114 已完成一次全量 1.5B labeled scan：
  - `full_scan_contract_count = 140`
  - `full_scan_class_balance = {label_0: 139, label_1: 1}`
- 114 已物化出可复用的非单类 candidate：
  - `selected_base_ids = [csqa-pilot-021, csqa-pilot-001, ..., csqa-pilot-011]`
  - `selected_contract_count = 24`
  - `class_balance = {label_0: 23, label_1: 1}`
- 当前结论：
  - `ready_for_stable_portability_rerun = true`
  - 下一步可直接推进 115，用 robust parser + stabilized subset 重跑 route_c portability precheck

## Next Suggested Plan

若 114 成功形成非单类 candidate，则创建 `.plans/115-rerun-model-axis-1p5b-route-c-stable-portability-precheck.md` 并用修复后的 parser + selection 逻辑重跑 route_c portability precheck。
