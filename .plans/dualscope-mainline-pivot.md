# DualScope Mainline Pivot

## Purpose / Big Picture

本计划用于执行一次项目级主线改轨：停止把 TriScope-LLM / route_c 递归验证链当作默认主论文推进线，并正式把仓库顶层主线切换为 **DualScope-LLM**。

这项工作解决的是“仓库治理与研究主线失配”问题。138–198 已经充分证明 route_c 执行链、recoverable-boundary 修正与多轮真实使用链的工程可靠性，但继续生成 199+ 的链式计划，对论文主叙事和实验收益已经明显下降。现在需要把这些成果归档为 **reliability foundation / implementation robustness / appendix support**，并重写顶层规则，让后续所有计划优先服务于 DualScope 的 illumination + confidence + budget-aware fusion 主线。

## Scope

### In Scope
- 修改 `AGENTS.md`，把仓库默认主线切换到 DualScope-LLM。
- 修改 `PLANS.md`，把项目级规划、默认未来计划生成规则、旧链归档方式改成 DualScope 叙事。
- 新增一个 DualScope 总计划文件，作为今后的唯一主入口。
- 更新适合作为旧主线入口的文档，使仓库用户能一眼看出 TriScope 主线已降级、route_c 旧链已归档。

### Out of Scope
- 不新增 199+ 的 route_c 链式计划。
- 不改 benchmark truth 语义。
- 不改 gate 语义。
- 不新增模型、预算、prompt family、attack family 实验。
- 不删除 138–198 历史成果。

## Repository Context

- 顶层治理文件：`AGENTS.md`、`PLANS.md`
- 项目入口文档：`README.md`
- 既有执行计划：`.plans/138-198...`
- 新主入口：`DUALSCOPE_MASTER_PLAN.md`

## Deliverables

- 更新后的 `AGENTS.md`
- 更新后的 `PLANS.md`
- 更新后的 `README.md`
- 新增 `DUALSCOPE_MASTER_PLAN.md`
- 明确把 138–198 标记为 historical engineering chain / reliability foundation 的仓库内说明

## Progress

- [x] 冻结改轨范围与交付物
- [x] 修改 `AGENTS.md`
- [x] 修改 `PLANS.md`
- [x] 更新 `README.md` 的主线入口说明
- [x] 新增 `DUALSCOPE_MASTER_PLAN.md`
- [x] 校验仓库默认主线已切换为 DualScope-LLM

## Surprises & Discoveries

- 改轨前，`AGENTS.md` 与 `PLANS.md` 仍完整保留 TriScope 三支主线叙事。
- 改轨前，仓库中不存在现成的 DualScope 总计划文件或 master plan 入口。
- `README.md` 也是旧主线入口之一，因此必须同步更新，否则会与新的治理文件冲突。

## Decision Log

- 决策：不删除 138–198 的旧链计划。
  - 原因：它们已经形成重要的工程可靠性证据链，适合作为附录、实现可信度和补充材料支撑。
  - 影响范围：`.plans/138-198...` 与对应 outputs 被保留，但主线定位降级。

- 决策：新增一个独立的 `DUALSCOPE_MASTER_PLAN.md` 作为新主入口。
  - 原因：只改 `AGENTS.md` / `PLANS.md` 不足以给研究主线提供清晰、可执行、可恢复的统一入口。
  - 影响范围：后续新计划应优先引用该主计划。

- 决策：同步更新 `README.md`。
  - 原因：`README.md` 是仓库使用者最先看到的主入口之一，若不更新会与新主线冲突。
  - 影响范围：项目定位、方法概览、开发状态将改写为 DualScope 叙事。

## Plan of Work

先冻结本次主线改轨的边界：只改顶层治理、主入口和主计划，不碰实验语义或已有历史成果。随后重写 `AGENTS.md`，把默认任务优先级、命名规范、默认计划生成规则改到 DualScope。再重写 `PLANS.md` 的项目级方向章节与默认未来计划类别，让其不再鼓励继续 route_c 递归链。接着更新 `README.md`，确保仓库首页也明确完成主线切换。最后新增 `DUALSCOPE_MASTER_PLAN.md`，把方法、实验、可靠性基础和停止事项统一落盘，并校验这些顶层文件已经形成一致的 DualScope 接管状态。

## Concrete Steps

1. 新建本计划并冻结本次 pivot 的作用域。
2. 修改 `AGENTS.md`，加入 DualScope 主线切换、旧链降级、默认不再生成 199+ 的明确规则。
3. 修改 `PLANS.md`，加入项目方向变更、DualScope phases、historical engineering chain 说明、默认新计划类别。
4. 修改 `README.md`，把仓库当前定位从 TriScope 主线改为 DualScope 主线，并加入历史说明。
5. 新增 `DUALSCOPE_MASTER_PLAN.md`，写清项目定位、方法、实验、可靠性基础、交付物和 stop-doing list。
6. 校验这些文件之间没有互相冲突的主线表述。

## Validation and Acceptance

完成标准：

- `AGENTS.md` 明确写出 DualScope-LLM 已接管主线。
- `PLANS.md` 明确写出 TriScope → DualScope transition、未来默认计划类型、旧链归档方式。
- `README.md` 不再把 TriScope 当作当前唯一主线。
- 仓库存在一个新的 `DUALSCOPE_MASTER_PLAN.md`，且内容完整覆盖方法、实验、可靠性基础和 stop-doing list。
- 文档中明确禁止默认继续 199+ route_c 递归链。

## Idempotence and Recovery

- 本次改动可重复执行，覆盖式更新顶层文档即可。
- 若中断，优先检查 `AGENTS.md`、`PLANS.md`、`README.md` 与 `DUALSCOPE_MASTER_PLAN.md` 是否一致。
- 历史 `.plans/138-198...` 与对应 outputs 不应删除或移动。

## Outputs and Artifacts

- `AGENTS.md`
- `PLANS.md`
- `README.md`
- `DUALSCOPE_MASTER_PLAN.md`
- `.plans/dualscope-mainline-pivot.md`

## Remaining Risks

- 仓库内部仍会保留大量历史 TriScope / route_c 文件名，这是保留证据链的结果，不能完全消失。
- 若后续有人只看早期 `.plans/00x-0xx` 文件，仍可能看到旧叙事，因此顶层入口必须足够显眼。
- 这次改轨解决的是顶层治理与研究计划，不自动完成 DualScope 具体实验设计实现。

## Next Suggested Plan

下一步建议优先创建以下 DualScope 主线计划之一：

- illumination screening pipeline freeze
- confidence verification pipeline freeze
- budget-aware two-stage fusion experimental design
