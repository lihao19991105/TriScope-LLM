# 010 Real Run Pilot Execution

## Purpose / Big Picture

TriScope-LLM 已经具备 smoke 级别的 probing、feature extraction、fusion、reporting 和 real-experiment bootstrap。下一步需要把仓库从“配置上已经准备好”推进到“至少一条 pilot experiment 真正可执行并尽量跑通”的状态。

010 的目标不是开一整套大规模真实实验，而是选一条成本最低、成功概率最高的 pilot 路线，把它从 blocked / config-only materialize 成可执行的真实 run，并让这条 run 至少生成一组真实 artifact。完成后，仓库将首次具备“真实 pilot 已落地”的执行能力，为后续 011 的 pilot analysis 和更大规模 experiment 扩展打基础。

## Scope

### In Scope

- 从 009 的 experiment registry 中选择一条最小 pilot 路线
- materialize pilot dataset / model / experiment 输入契约
- 增加 pilot materialization CLI 与 pilot execution CLI
- 跑一条最小真实 pilot run
- 若成本可控，补 pilot feature extraction
- 输出 pilot registry / summary / acceptance artifact
- README 中补 pilot 最小用法

### Out of Scope

- 大规模真实训练
- 多条 pilot 路线并行推进
- 下载大模型或大数据集
- 完整 tri-probe + fusion + reporting 的真实大实验
- 复杂 scheduler / dashboard

## Repository Context

本计划将衔接：

- `configs/datasets.yaml`
- `configs/models.yaml`
- `configs/experiments.yaml`
- `scripts/run_reasoning_probe.py`
- `scripts/extract_reasoning_features.py`
- `src/probes/reasoning_probe.py`
- `src/features/reasoning_features.py`
- `src/eval/`
- `outputs/experiment_bootstrap/*`

## Deliverables

- 010 real-run-pilot-execution ExecPlan
- pilot 选择与 materialization 逻辑
- pilot-specific dataset profile / model profile / experiment row
- `scripts/materialize_pilot_experiment.py`
- `scripts/run_pilot_experiment.py`
- pilot materialization artifacts
- pilot raw run artifacts
- pilot feature artifacts（若 pilot run 成功）
- pilot acceptance artifact
- README pilot 用法补充

## Progress

- [x] 创建 ExecPlan 初稿
- [x] Milestone 1: 选定 pilot 路线、materialize 输入契约、生成 pilot readiness artifact
- [x] Milestone 2: pilot execution CLI、真实 pilot run、结构化 run artifact
- [x] Milestone 3: README、acceptance、必要时最小 repeatability、计划收口

## Surprises & Discoveries

- 本机没有现成的本地 causal LM 权重，当前可见的 `CodeLlama-7b-hf` 缓存只有 tokenizer 文件，不足以直接作为真实推理模型。
- 这意味着本轮最稳妥的 pilot 路径应优先选择“单模块 + 小型真实模型 + 本地 materialized dataset slice”，而不是把 010 绑在尚未本地可用的大模型上。
- `distilgpt2` 在本机 HuggingFace cache 中已经存在完整 snapshot，但 probe 共享 loader 起初没有真正使用 `local_path`，导致 pilot 首次运行仍试图联网。

## Decision Log

- 决策：从 009 的 blocked 行中优先继承 `pilot_csqa_reasoning_probe`，而不是 `pilot_advbench_reasoning_confidence` 或 full multi-module 路线。
  - 原因：它只需要单模块 reasoning 链路，输入契约最轻，最容易在一轮内从 config-only 推进到真实可执行。
  - 影响范围：pilot dataset schema、execution CLI、后续 feature artifact 选择。

- 决策：pilot dataset 先 materialize 成本地小型 reasoning slice，而不是等待完整 benchmark 下载。
  - 原因：当前阶段目标是让一条 pilot route 真实落地，不是立刻覆盖全量数据；小型 local slice 更符合最小成本、最高成功率原则。
  - 影响范围：`configs/datasets.yaml`、pilot materialization outputs、pilot readiness summary。

- 决策：pilot execution 优先复用现有 reasoning probe 与 reasoning feature extraction，不重写 probe 主逻辑。
  - 原因：004~009 的稳定模块已经可用，010 应只补 pilot orchestration 与 materialization，而不是重构稳定链路。
  - 影响范围：`scripts/run_pilot_experiment.py`、`src/eval/pilot_execution.py`、pilot outputs。

- 决策：把 `pilot_distilgpt2_hf` 固定到本地 HuggingFace snapshot，并让 probe loader 优先使用 `local_path`。
  - 原因：这样可以避免 pilot execution 再次被沙箱网络或远端解析阻塞，同时保留“真实 HuggingFace 模型”属性。
  - 影响范围：`configs/models.yaml`、`src/probes/illumination_probe.py`、pilot execution 稳定性。

- 决策：M2 的真实 pilot run 采用 `--smoke-mode` 作为默认执行深度。
  - 原因：本轮目标是先把真实 pilot execution path 落地并重复跑通，而不是在首条 pilot 上拉高预算和时延。
  - 影响范围：`pilot_run_summary.json`、repeatability 指标、README 用法说明。

## Plan of Work

先从 009 的 experiment registry 中选定最轻的 blocked row，并将它 materialize 成本地可执行的 pilot 版本。具体做法是：新增一个 pilot-specific dataset profile、本地小型 reasoning slice、以及与之配套的小模型 profile。M1 完成后，用一个薄 orchestration CLI 把 materialized query contract 接到现有 reasoning probe，再尽量接 reasoning feature extraction，形成最小真实 pilot chain。最后在 M3 用 acceptance 和 README 收口，让 010 可交接。

## Concrete Steps

1. 创建 `.plans/010-real-run-pilot-execution.md` 并固定 milestone 边界。
2. 在 `configs/datasets.yaml` 中增加 pilot-local dataset profile。
3. 在 `configs/models.yaml` 中增加最小真实 pilot model profile。
4. 在 `configs/experiments.yaml` 中增加 materialized pilot experiment row。
5. 实现 `src/eval/pilot_execution.py`：
   - 选择 pilot experiment
   - materialize local dataset slice
   - 生成 reasoning query contracts
   - 调用 reasoning probe 与 feature extraction
6. 实现 `scripts/materialize_pilot_experiment.py`。
7. 实现 `scripts/run_pilot_experiment.py`。
8. 运行 pilot materialization。
9. 运行至少一条真实 pilot execution。
10. 若成功，补 acceptance artifact 与 README。

## Validation and Acceptance

- `materialize_pilot_experiment.py --help` 可正常显示
- `run_pilot_experiment.py --help` 可正常显示
- `validate_pilot_run.py --help` 可正常显示
- M1 成功生成：
  - `pilot_experiment_selection.json`
  - `pilot_dataset_materialization_summary.json`
  - `pilot_model_materialization_summary.json`
  - `pilot_readiness_summary.json`
- M2 至少成功生成：
  - `pilot_run_summary.json`
  - `pilot_run_config_snapshot.json`
  - `pilot_execution.log`
  - reasoning raw run artifact
- 若 feature extraction 成功，还应生成 reasoning feature artifact
- M3 若完成，则应生成 pilot acceptance artifact
- acceptance validator 结果为 `PASS`
- repeatability validator 结果为 `PASS`

## Idempotence and Recovery

- pilot materialization 与 pilot execution 都写入独立 `output_dir`
- 重新运行不会依赖隐式全局状态
- 如果真实模型不可用，应写出结构化 failure summary，而不是只留下长堆栈
- 若 materialization 已完成，则 execution 可以直接复用已生成的 query contracts 继续运行

## Outputs and Artifacts

- `outputs/pilot_materialization/*`
- `outputs/pilot_runs/*`
- `pilot_experiment_selection.json`
- `pilot_dataset_materialization_summary.json`
- `pilot_model_materialization_summary.json`
- `pilot_readiness_summary.json`
- `pilot_run_summary.json`
- `pilot_run_config_snapshot.json`
- `pilot_execution.log`

## Remaining Risks

- 当前 pilot 数据切片是最小 local reasoning slice，不代表完整 CommonsenseQA benchmark。
- 当前 pilot 只覆盖 reasoning 模块，不代表真实 tri-probe + fusion 已经整体落地。
- 当前真实模型选择为 `distilgpt2`，更偏向 execution practicality，而不是最终论文实验模型。
- 当前 pilot repeatability 只验证固定小切片与固定 seed，不代表 larger pilot 或 full runs 的稳定性。

## Validation Snapshot

- `outputs/pilot_materialization/pilot_csqa_reasoning_local/pilot_readiness_summary.json`
  - selected experiment: `pilot_csqa_reasoning_local`
  - ready to run: `true`
- `outputs/experiment_bootstrap/pilot_refresh/experiment_bootstrap_summary.json`
  - dataset profiles: `6`
  - model profiles: `8`
  - experiments: `5`
  - ready local experiments: `2`
- `outputs/pilot_runs/pilot_csqa_reasoning_local_ready/pilot_run_summary.json`
  - model profile: `pilot_distilgpt2_hf`
  - query_budget_realized: `2`
  - feature extraction completed: `true`
- `outputs/pilot_runs/repeatability_pilot_csqa_reasoning_local/artifact_acceptance.json`
  - acceptance status: `PASS`
- `outputs/pilot_runs/repeatability_pilot_csqa_reasoning_local/repeatability_summary.json`
  - repeatability status: `PASS`
  - all key metrics match: `true`

## Next Suggested Plan

若 010 完成，下一步建议创建 `.plans/011-pilot-run-analysis.md`。
