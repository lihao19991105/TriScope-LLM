# Codex Smart Exec Usage

## Codex reasoning effort 配置规范

Codex CLI 当前有效推理强度参数：

```bash
-c model_reasoning_effort="medium"
-c model_reasoning_effort="high"
-c model_reasoning_effort="xhigh"
```

当前 CLI 不应使用：

```bash
-c reasoning_effort="high"
```

该参数形式可能被 CLI 接受，但实测不会真正设置推理强度，运行头会显示 `reasoning effort: none`。

推荐在自动化任务中使用：

```bash
codex exec --cd "$REPO" --full-auto --model gpt-5.5 -c model_reasoning_effort="high" "$PROMPT"
```

长时间 autorun 默认使用 `high`，不要默认使用 `xhigh`。`xhigh` 只用于复杂 blocker 根因分析、gate / orchestrator / worktree runner 设计或论文方法与实验设计。
