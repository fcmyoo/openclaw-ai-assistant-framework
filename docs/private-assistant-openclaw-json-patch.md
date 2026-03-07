# private_assistant 精确配置补丁

这份补丁基于新加坡服务器当前实际配置结构生成。

参考源：

- [openclaw.exact-append.patch.md](/H:/code/github/openclaw-ai-assistant-framework/runtime/private-assistant/openclaw.exact-append.patch.md)
- [openclaw-json-merge-guide.md](/H:/code/github/openclaw-ai-assistant-framework/docs/openclaw-json-merge-guide.md)

## 现状摘要

当前远端：

1. `agents.list` 中已有 7 个 agent
2. `bindings` 中已有 7 条规则
3. 最后一个 agent 是 `feishu_group_bot_all`
4. 最后一条 binding 也是 `feishu_group_bot_all`

因此本次改造不需要重排结构，只需要在两个数组末尾各追加 1 个对象。

## 推荐追加对象

### 追加到 `agents.list`

```json
{
  "id": "private_assistant",
  "name": "private_assistant",
  "description": "用户专属技术助手",
  "workspace": "/root/.openclaw/workspace-private-assistant",
  "model": {
    "primary": "packycode/gpt-5.3-codex"
  },
  "memorySearch": {
    "enabled": true,
    "provider": "openai",
    "remote": {
      "baseUrl": "https://openrouter.ai/api/v1",
      "apiKey": "${OPENROUTER_API_KEY}",
      "headers": {
        "HTTP-Referer": "https://openclaw.ai",
        "X-Title": "OpenClaw"
      }
    },
    "model": "text-embedding-3-small"
  },
  "compaction": {
    "mode": "safeguard"
  },
  "maxConcurrent": 2
}
```

### 追加到 `bindings`

```json
{
  "agentId": "private_assistant",
  "match": {
    "channel": "discord",
    "accountId": "private"
  }
}
```

## 不要改的部分

不要动这些现有对象：

1. `boss`
2. `dev`
3. `app`
4. `finance`
5. `strategy`
6. `telegram`
7. `feishu_group_bot_all`

也不要动：

1. `channels`
2. `plugins`
3. `gateway`
4. `agents.defaults`

## 推荐操作方式

1. 先备份 `openclaw.json`
2. 参考运行时补丁文档手工追加
3. 用 `python3 -m json.tool` 校验合法性
4. 手动跑脚本验证
5. 再上最小 cron 集
