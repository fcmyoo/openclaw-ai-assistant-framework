# private_assistant Cron 命令清单与上线顺序

## 目标

为新加坡服务器上的 `private_assistant` 提供一套最小可执行的定时任务，并按低风险顺序上线。

## 适用前提

以下条件未满足前，不要执行 cron 上线：

1. 已完成 `private_assistant` 工作区同步
2. 已在 `openclaw.json` 中追加 `private_assistant` agent 和 binding
3. 远端仓库目录已存在
4. `python3` 和 `openclaw` 在远端可执行
5. 已确认工作区路径：
   - `/root/.openclaw/workspace-private-assistant`

## 推荐远端目录约定

```bash
REPO_ROOT="/root/openclaw-ai-assistant-framework"
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant"
```

如果你的远端仓库不在 `/root/openclaw-ai-assistant-framework`，先替换下面命令中的 `REPO_ROOT`。

## 上线顺序

按这个顺序执行，不要一口气全上：

### 第 1 步：只上健康检查

目的：

- 验证 `python3`
- 验证脚本路径
- 验证 `OPENCLAW_WORKSPACE`
- 验证 `openclaw cron` 可用

命令：

```bash
cd /root/openclaw-ai-assistant-framework
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant" python3 scripts/model-health-check.py
```

预期结果：

- 生成 `data/model-health-status.json`
- 生成 `logs/model-health.log`

确认正常后，再添加 cron：

```bash
openclaw cron add --name "private-assistant-model-health" --cron "0 */6 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/model-health-check.py >/dev/null"
```

### 第 2 步：上线日报任务

先手动跑一次：

```bash
cd /root/openclaw-ai-assistant-framework
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant" python3 scripts/daily-evolution.py --stdout
```

预期结果：

- 生成 `data/evolution-reports/evolution-report-YYYY-MM-DD.md`
- 生成 `data/evolution-reports/evolution-report-latest.md`

确认正常后，添加每天摘要任务：

```bash
openclaw cron add --name "private-assistant-daily-summary" --cron "30 21 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/daily-evolution.py >/dev/null"
```

### 第 3 步：上线 heartbeat

说明：

- 当前仓库里没有独立 heartbeat 脚本
- 第一阶段用 `daily-evolution.py --date $(date +%F)` 作为轻量占位整理任务
- 它会刷新 latest 报告，不会改 agent 主配置

先手动执行一次：

```bash
cd /root/openclaw-ai-assistant-framework
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant" python3 scripts/daily-evolution.py --date "$(date +%F)"
```

确认正常后，添加 cron：

```bash
openclaw cron add --name "private-assistant-heartbeat" --cron "*/30 * * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/daily-evolution.py --date \$(date +%F) >/dev/null"
```

### 第 4 步：上线知识提取

这一步不是核心运行链，建议在前三步稳定 1 天后再做。

先手动跑一次：

```bash
cd /root/openclaw-ai-assistant-framework
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant" python3 scripts/batch-extract-knowledge.py
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant" python3 scripts/integrate-knowledge.py
```

确认正常后，添加两个任务：

```bash
openclaw cron add --name "private-assistant-knowledge-batch" --cron "10 2 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/batch-extract-knowledge.py >/dev/null"

openclaw cron add --name "private-assistant-knowledge-integrate" --cron "40 2 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/integrate-knowledge.py >/dev/null"
```

## 最小上线集

第一阶段建议只启用这 3 个：

1. `private-assistant-model-health`
2. `private-assistant-daily-summary`
3. `private-assistant-heartbeat`

知识提取类任务等稳定后再开。

## 一次性打印全部命令

远端可执行：

```bash
cd /root/openclaw-ai-assistant-framework
bash ops/print-private-assistant-cron-commands.sh
```

如果仓库目录不同：

```bash
REPO_ROOT="/your/repo/path" OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant" bash ops/print-private-assistant-cron-commands.sh
```

## 上线后验证

```bash
openclaw cron list
ls -lah /root/.openclaw/workspace-private-assistant/data
ls -lah /root/.openclaw/workspace-private-assistant/data/evolution-reports
cat /root/.openclaw/workspace-private-assistant/data/model-health-status.json
tail -50 /root/.openclaw/workspace-private-assistant/logs/model-health.log
```

## 回滚顺序

如果上线后出现问题，按反向顺序回滚：

1. 删除 `private-assistant-knowledge-integrate`
2. 删除 `private-assistant-knowledge-batch`
3. 删除 `private-assistant-heartbeat`
4. 删除 `private-assistant-daily-summary`
5. 删除 `private-assistant-model-health`

然后再检查：

```bash
openclaw cron list
```

## 风险说明

1. `heartbeat` 当前是日报脚本占位，不是真正独立的记忆整理器
2. 如果工作区里还没有 `config/model-pools.json`，健康检查会失败
3. 如果 `skills/` 目录为空，知识提取任务不会有产出，但不应影响主流程
