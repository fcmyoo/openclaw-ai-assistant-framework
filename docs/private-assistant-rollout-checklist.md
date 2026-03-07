# private_assistant 上线检查清单

## 目标

以不影响当前新加坡服务器既有 agent 的方式，上线一个独立的 `private_assistant`。

## 上线前

1. 确认已在分支 `codex/private-assistant-upgrade`
2. 确认已备份远端 `~/.openclaw/openclaw.json`
3. 确认已轮换或准备外置密钥
4. 确认目标私有入口已经存在
5. 确认远端工作区目录将使用：
   - `/root/.openclaw/workspace-private-assistant`

## 工作区同步

1. 同步以下模板文件到远端工作区：
   - `AGENTS.md`
   - `IDENTITY.md`
   - `USER.md`
   - `TOOLS.md`
   - `SOUL.md`
   - `MEMORY.md`
2. 先补全 `IDENTITY.md` 和 `USER.md`
3. 检查 `memory/` 目录是否存在

## 配置合并

1. 参考 [openclaw-json-merge-guide.md](/H:/code/github/openclaw-ai-assistant-framework/docs/openclaw-json-merge-guide.md)
2. 只向 `agents.list` 追加 `private_assistant`
3. 只向 `bindings` 追加目标私有入口规则
4. 不修改现有 agent、channels、plugins、gateway

## 自动化配置

建议第一阶段只启用：

1. `private-assistant-heartbeat`
2. `private-assistant-daily-summary`
3. `private-assistant-model-health`

使用脚本：

- [setup-private-assistant-cron.sh](/H:/code/github/openclaw-ai-assistant-framework/ops/setup-private-assistant-cron.sh)

## 验证项

1. 私有入口消息能命中 `private_assistant`
2. `MEMORY.md` 不会被群聊上下文读取
3. `data/evolution-reports/` 能生成日报
4. `data/model-health-status.json` 能生成健康状态
5. 现有 `boss/dev/app/...` 不受影响

## 回滚

1. 从 `agents.list` 删除 `private_assistant`
2. 从 `bindings` 删除其匹配规则
3. 删除对应 cron 任务
4. 保留工作区目录用于审计
