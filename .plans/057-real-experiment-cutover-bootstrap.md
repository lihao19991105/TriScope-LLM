# 057 Real Experiment Cutover Bootstrap

## Purpose / Big Picture

056 若明确判断继续扩 proxy substrate 的边际收益已经下降，那么下一步最自然的动作不应再机械滚到 v7，而应把项目切向第一轮更像样的小规模真实 labeled experiment 准备。057 的目标不是直接跑论文主实验，而是把这个切换动作做成一个真实、可执行、可验证的 bootstrap 对象。

## Scope

### In Scope

- real-experiment candidate selection
- dataset / model / label readiness summary
- first real-experiment input contract
- materialized bootstrap inputs
- acceptance / README / 收口

### Out of Scope

- 直接执行 benchmark-scale 主实验
- 下载大型外部数据集
- 引入更大模型矩阵
- 新增第四条 / 第五条监督路线

## Repository Context

本计划主要衔接：

- `outputs/post_v6_symmetric_comparison/default/*`
- `outputs/post_v5_next_step_bootstrap/default/*`
- `outputs/experiment_bootstrap/pilot_refresh/*`
- `outputs/rerun_route_b_on_labeled_split_v6/default/*`
- `outputs/rerun_route_c_on_labeled_split_v6/default/*`
- `configs/datasets.yaml`
- `configs/models.yaml`
- `configs/experiments.yaml`

## Deliverables

- `.plans/057-real-experiment-cutover-bootstrap.md`
- `src/eval/real_experiment_cutover_bootstrap.py`
- `scripts/build_real_experiment_cutover_bootstrap.py`
- `src/eval/real_experiment_cutover_bootstrap_checks.py`
- `scripts/validate_real_experiment_cutover_bootstrap.py`
- `real_experiment_cutover_plan.json`
- `real_experiment_candidate_selection.json`
- `real_experiment_readiness_summary.json`
- `materialized_real_experiment_inputs/`
- `real_experiment_input_contract.json`
- `real_experiment_bootstrap_summary.json`

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: candidate selection / readiness summary
- [x] Milestone 2: input contract / bootstrap artifact
- [x] Milestone 3: acceptance / repeatability / README / 收口

## Surprises & Discoveries

- 当前仓库里最“现实可做”的切换路线，并不是直接跳到 benchmark ground truth，而是把现有 v6 substrate、现有 local model、现有 experiment registry 组合成一个更像样的小规模真实实验 contract。
- 057 成功与否的关键，不是结果分数，而是能否让“从 proxy substrate 扩容”正式切到“real experiment preparation”的对象第一次存在。
- 这个对象必须诚实说明：它比纯 proxy substrate expansion 更接近真实实验，但仍不是最终 benchmark 主实验。
- 057 已稳定选出 `small_real_labeled_csqa_triscope_cutover_v1` 作为 first cutover candidate，并成功 materialize `70` 行输入，acceptance / repeatability 都为 `PASS`。

## Decision Log

- 决策：057 优先选择一个最小但可执行的 cutover candidate，而不是追求理想但阻塞严重的 benchmark 主实验。
  - 原因：当前最重要的是结束“继续扩 substrate 才有工作可做”的循环，让真实实验切换第一次 materialize。
  - 影响范围：candidate selection、input contract、bootstrap summary 与 README。

## Plan of Work

先读取 056 recommendation、已有 experiment bootstrap registry、v6 split summary 与 v6 route outputs，确定一个最小但更真实的实验候选。然后输出 candidate selection、readiness summary 与 input contract，并 materialize 一份可直接衔接后续 experiment pipeline 的 bootstrap inputs。最后补 validator、repeatability 与 README。

## Concrete Steps

1. 实现 `src/eval/real_experiment_cutover_bootstrap.py` 与配套 CLI / validator。
2. 运行 build CLI 生成 cutover artifact。
3. 运行 repeat run 与 validator。
4. 更新 README 与 plan 进度。

## Validation and Acceptance

- `build_real_experiment_cutover_bootstrap.py --help` 可正常显示
- `validate_real_experiment_cutover_bootstrap.py --help` 可正常显示
- 至少生成：
  - `real_experiment_cutover_plan.json`
  - `real_experiment_candidate_selection.json`
  - `real_experiment_readiness_summary.json`
  - `materialized_real_experiment_inputs/`
  - `real_experiment_input_contract.json`
  - `real_experiment_bootstrap_summary.json`
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

057 的 build / validate 都是幂等的；重复运行会覆盖同名输出。若只想复核 cutover recommendation，可直接重跑 build 与 validate。

## Remaining Risks

- cutover object 仍然不是 benchmark ground truth 主实验，只是更像样的小规模真实 labeled experiment 准备。
- 当前模型仍以 `pilot_distilgpt2_hf` 为主，因此 057 证明的是切换 readiness，而不是最终研究结论。

## Next Suggested Plan

若 057 完成，下一步建议基于 `materialized_real_experiment_inputs/` 去实现第一轮 minimal real-experiment dry-run 或 first-pass materialized execution，而不是继续机械扩 proxy substrate。
