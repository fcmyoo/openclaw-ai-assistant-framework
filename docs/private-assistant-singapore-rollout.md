# 新加坡服务器上线手册

## 适用对象

- 服务器别名：`新加坡服务器`
- 主机：`124.156.198.237`
- 用户：`root`
- OpenClaw Home：`/root/.openclaw`

## 目标

将当前仓库中的 `private_assistant` 方案，以增量方式部署到新加坡服务器，不影响现有 agent。

## 约定路径

远端统一使用：

```bash
REPO_ROOT="/root/openclaw-ai-assistant-framework"
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant"
OPENCLAW_CONFIG="/root/.openclaw/openclaw.json"
```

## 第 0 步：连通与现状确认

本地执行：

```powershell
ssh "新加坡服务器" "hostname && whoami && openclaw --version"
```

预期：

- 主机可连
- 用户为 `root`
- OpenClaw 版本正常输出

## 第 1 步：同步仓库到远端

如果远端还没有该仓库：

```powershell
ssh "新加坡服务器" "cd /root && git clone https://github.com/fcmyoo/openclaw-ai-assistant-framework.git"
```

如果远端已经有仓库：

```powershell
scp -r "H:/code/github/openclaw-ai-assistant-framework/docs" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp -r "H:/code/github/openclaw-ai-assistant-framework/ops" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp -r "H:/code/github/openclaw-ai-assistant-framework/runtime" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp -r "H:/code/github/openclaw-ai-assistant-framework/workspace" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp "H:/code/github/openclaw-ai-assistant-framework/.gitignore" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp "H:/code/github/openclaw-ai-assistant-framework/scripts/"*.py "新加坡服务器:/root/openclaw-ai-assistant-framework/scripts/"
```

同步后确认：

```powershell
ssh "新加坡服务器" "find /root/openclaw-ai-assistant-framework -maxdepth 2 -type d | sort | sed -n '1,120p'"
```

## 第 2 步：备份现网配置

远端执行：

```bash
cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.backup.$(date +%Y%m%d-%H%M%S)
```

确认：

```bash
ls -lah /root/.openclaw/openclaw.json*
```

## 第 3 步：创建专属工作区

远端执行：

```bash
mkdir -p /root/.openclaw/workspace-private-assistant/memory
cd /root/openclaw-ai-assistant-framework
bash ops/deploy-private-assistant.sh
```

说明：

- 该脚本只会同步工作区模板
- 不会自动改写 `openclaw.json`

确认：

```bash
find /root/.openclaw/workspace-private-assistant -maxdepth 2 -type f | sort
```

## 第 4 步：补全工作区核心信息

远端至少手工补这两个文件：

```bash
vi /root/.openclaw/workspace-private-assistant/IDENTITY.md
vi /root/.openclaw/workspace-private-assistant/USER.md
```

最低要求：

- `IDENTITY.md`：名称、角色、风格
- `USER.md`：称呼、时区、主要目标、沟通偏好

## 第 5 步：准备配置合并

先查看指引：

```bash
cat /root/openclaw-ai-assistant-framework/docs/openclaw-json-merge-guide.md
cat /root/openclaw-ai-assistant-framework/runtime/private-assistant/openclaw.merge-snippet.json
```

这一步的原则：

1. 只向 `agents.list` 追加一个 `private_assistant`
2. 只向 `bindings` 追加一个私有入口规则
3. 不修改其他现有 agent
4. 不修改 `channels/plugins/gateway`

## 第 6 步：人工合并 `openclaw.json`

建议流程：

```bash
cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.before-private-assistant
vi /root/.openclaw/openclaw.json
```

合并完成后，至少做一次 JSON 合法性校验：

```bash
python3 -m json.tool /root/.openclaw/openclaw.json >/dev/null
```

如果失败，立即回退：

```bash
cp /root/.openclaw/openclaw.json.before-private-assistant /root/.openclaw/openclaw.json
```

## 第 7 步：手动验证脚本

先不要上 cron，先手动跑。

### 7.1 模型健康检查

```bash
cd /root/openclaw-ai-assistant-framework
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant" python3 scripts/model-health-check.py
```

### 7.2 每日报告

```bash
cd /root/openclaw-ai-assistant-framework
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant" python3 scripts/daily-evolution.py --stdout
```

### 7.3 路由测试

如果工作区里已放置 `config/model-pools.json`：

```bash
cd /root/openclaw-ai-assistant-framework
OPENCLAW_WORKSPACE="/root/.openclaw/workspace-private-assistant" python3 scripts/test-session-routing.py
```

## 第 8 步：上线最小 cron 集

先打印命令：

```bash
cd /root/openclaw-ai-assistant-framework
bash ops/print-private-assistant-cron-commands.sh
```

第一阶段只执行这 3 条：

```bash
openclaw cron add --name "private-assistant-model-health" --cron "0 */6 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/model-health-check.py >/dev/null"

openclaw cron add --name "private-assistant-daily-summary" --cron "30 21 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/daily-evolution.py >/dev/null"

openclaw cron add --name "private-assistant-heartbeat" --cron "*/30 * * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/daily-evolution.py --date \$(date +%F) >/dev/null"
```

确认：

```bash
openclaw cron list
```

## 第 9 步：灰度观察

建议至少观察 24 小时，再决定是否打开知识类任务。

重点看：

```bash
ls -lah /root/.openclaw/workspace-private-assistant/data
ls -lah /root/.openclaw/workspace-private-assistant/data/evolution-reports
cat /root/.openclaw/workspace-private-assistant/data/model-health-status.json
tail -50 /root/.openclaw/workspace-private-assistant/logs/model-health.log
```

## 第 10 步：第二阶段再开知识类任务

确认前三个任务稳定后，再执行：

```bash
openclaw cron add --name "private-assistant-knowledge-batch" --cron "10 2 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/batch-extract-knowledge.py >/dev/null"

openclaw cron add --name "private-assistant-knowledge-integrate" --cron "40 2 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/integrate-knowledge.py >/dev/null"
```

## 回滚顺序

如果任一步出现问题，按顺序回滚：

### 回滚 cron

```bash
openclaw cron remove --name "private-assistant-knowledge-integrate" || true
openclaw cron remove --name "private-assistant-knowledge-batch" || true
openclaw cron remove --name "private-assistant-heartbeat" || true
openclaw cron remove --name "private-assistant-daily-summary" || true
openclaw cron remove --name "private-assistant-model-health" || true
```

### 回滚配置

```bash
cp /root/.openclaw/openclaw.json.before-private-assistant /root/.openclaw/openclaw.json
```

### 保留工作区

不要立刻删除：

```bash
/root/.openclaw/workspace-private-assistant
```

先保留做审计和排查。

## 风险提示

1. 当前 `heartbeat` 还是占位实现，不是独立记忆整理器
2. 如果 `private_assistant` 绑定规则写错，消息不会命中该 agent
3. 如果 `config/model-pools.json` 未同步到工作区，健康检查和路由测试会失败
