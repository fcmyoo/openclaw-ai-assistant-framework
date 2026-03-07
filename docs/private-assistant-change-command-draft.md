# private_assistant 远端变更命令草稿

## 目标

提供一套在新加坡服务器上可直接执行的命令顺序，用于：

1. 备份现网配置
2. 同步专属工作区
3. 人工合并 `openclaw.json`
4. 执行上线前校验
5. 上线 cron
6. 验证与回滚

## 说明

这些命令默认仍然不会自动改写 `openclaw.json` 内容。

原因：

1. 当前是生产实例
2. `openclaw.json` 存在现网 agent 和敏感配置
3. 手工审阅合并比自动 JSON 重写更稳

## 本地到远端同步

本地 PowerShell 执行：

```powershell
scp -r "H:/code/github/openclaw-ai-assistant-framework/docs" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp -r "H:/code/github/openclaw-ai-assistant-framework/ops" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp -r "H:/code/github/openclaw-ai-assistant-framework/runtime" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp -r "H:/code/github/openclaw-ai-assistant-framework/workspace" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp "H:/code/github/openclaw-ai-assistant-framework/.gitignore" "新加坡服务器:/root/openclaw-ai-assistant-framework/"
scp "H:/code/github/openclaw-ai-assistant-framework/scripts/"*.py "新加坡服务器:/root/openclaw-ai-assistant-framework/scripts/"
```

## 远端准备阶段

登录远端后执行：

```bash
cd /root/openclaw-ai-assistant-framework
bash ops/prepare-private-assistant-rollout.sh
```

这个脚本会做：

1. 检查 `openclaw/python3`
2. 备份 `openclaw.json`
3. 创建并同步专属工作区模板
4. 指向精确补丁文档

## 人工编辑配置

远端执行：

```bash
vi /root/.openclaw/openclaw.json
```

编辑时参考：

```bash
cat /root/openclaw-ai-assistant-framework/runtime/private-assistant/openclaw.exact-append.patch.md
cat /root/openclaw-ai-assistant-framework/docs/private-assistant-openclaw-json-patch.md
```

## 编辑后校验

远端执行：

```bash
cd /root/openclaw-ai-assistant-framework
bash ops/verify-private-assistant-rollout.sh
```

这个脚本会做：

1. 校验 `openclaw.json` 合法性
2. 检查 `private_assistant` 是否已写入 `agents.list/bindings`
3. 检查工作区文件
4. 手动跑健康检查和日报脚本
5. 输出当前 cron 和结果文件

## 上线最小 cron 集

验证通过后执行：

```bash
cd /root/openclaw-ai-assistant-framework
bash ops/print-private-assistant-cron-commands.sh
```

第一阶段建议只执行：

```bash
openclaw cron add --name "private-assistant-model-health" --cron "0 */6 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/model-health-check.py >/dev/null"

openclaw cron add --name "private-assistant-daily-summary" --cron "30 21 * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/daily-evolution.py >/dev/null"

openclaw cron add --name "private-assistant-heartbeat" --cron "*/30 * * * *" --exact --command "cd /root/openclaw-ai-assistant-framework && OPENCLAW_WORKSPACE=/root/.openclaw/workspace-private-assistant python3 scripts/daily-evolution.py --date \$(date +%F) >/dev/null"
```

## 验证

```bash
openclaw cron list
find /root/.openclaw/workspace-private-assistant/data -maxdepth 3 -type f | sort
tail -50 /root/.openclaw/workspace-private-assistant/logs/model-health.log
```

## 回滚草稿

如果要回滚，远端执行：

```bash
cd /root/openclaw-ai-assistant-framework
bash ops/rollback-private-assistant.sh
```

然后手工恢复备份配置：

```bash
cp /root/.openclaw/openclaw.json.before-private-assistant.<timestamp> /root/.openclaw/openclaw.json
```
