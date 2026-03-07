# `openclaw.json` 精确合并指引

## 适用对象

当前新加坡服务器的 `~/.openclaw/openclaw.json`。

## 已确认的远端结构

远端当前顶层关键字段包括：

- `agents`
- `bindings`
- `channels`
- `plugins`
- `tools`
- `gateway`
- `messages`
- `wizard`

其中：

- `agents` 是对象，包含 `defaults` 和 `list`
- `bindings` 是数组

因此新增专属助手时，应当：

1. 向 `agents.list` 追加一个新对象
2. 向 `bindings` 追加一个新对象
3. 不修改 `agents.defaults`
4. 不修改现有 channel 配置
5. 不修改现有 plugin 配置

## 建议追加的 agent

将以下对象追加到 `agents.list`：

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

## 建议追加的 binding

将以下对象追加到 `bindings`：

```json
{
  "agentId": "private_assistant",
  "match": {
    "channel": "discord",
    "accountId": "private"
  }
}
```

如果你后续决定不用 Discord 私有账号，而是走 Telegram 或 Feishu 私聊，只替换 `match` 即可，不要改 agent 本体。

## 明确不要动的部分

第一阶段不要修改：

- 现有 `boss`
- 现有 `dev`
- 现有 `app`
- 现有 `finance`
- 现有 `strategy`
- 现有 `telegram`
- 现有 `feishu_group_bot_all`
- 现有 `channels`
- 现有 `plugins.entries`
- 现有 `gateway`

## 合并后应检查

1. `private_assistant` 不与现有 `agentId` 重名
2. 新 `binding` 不与现有渠道规则冲突
3. `workspace` 目录已存在且已同步模板文件
4. 密钥不再写死在 `openclaw.json`
5. 重载后能被目标私有入口命中

## 回滚方式

如果上线后有问题，只需回滚两处：

1. 从 `agents.list` 删除 `private_assistant`
2. 从 `bindings` 删除对应规则

不需要触碰其他 agent。
