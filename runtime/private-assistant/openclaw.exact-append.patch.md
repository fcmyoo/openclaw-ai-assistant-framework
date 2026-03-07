# `openclaw.json` 精确追加补丁

适用文件：

- `/root/.openclaw/openclaw.json`

适用环境：

- 新加坡服务器 `124.156.198.237`
- 当前 `agents.list` 已有 7 个元素
- 当前 `bindings` 已有 7 个元素

## 追加位置

### 1. `agents.list`

当前最后一个元素是：

```json
{
  "id": "feishu_group_bot_all",
  "name": "feishu_group_bot_all",
  "workspace": "/root/.openclaw/workspace-feishu-bot",
  "agentDir": "/root/.openclaw/agents/feishu_group_bot_all/agent",
  "model": {
    "primary": "packycode/gpt-5.2"
  },
  "tools": {
    "allow": [
      "*"
    ]
  }
}
```

在它后面补一个逗号，然后追加下面这个第 8 个元素：

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

### 2. `bindings`

当前最后一个元素是：

```json
{
  "agentId": "feishu_group_bot_all",
  "match": {
    "channel": "feishu",
    "peer": {
      "kind": "group",
      "id": "oc_2d1bfca27d6395dccd7376038c37680b"
    }
  }
}
```

在它后面补一个逗号，然后追加下面这个第 8 个元素：

```json
{
  "agentId": "private_assistant",
  "match": {
    "channel": "discord",
    "accountId": "private"
  }
}
```

## 合并后的最小检查

保存前至少确认：

1. `private_assistant` 没有和现有 agent 重名
2. `bindings` 里的 `discord/private` 没有被现有规则占用
3. `apiKey` 仍保持环境变量占位或你自己的外置方案，不要写回明文

保存后执行：

```bash
python3 -m json.tool /root/.openclaw/openclaw.json >/dev/null
```

## 手动校验命令

```bash
python3 - <<'PY'
import json
with open('/root/.openclaw/openclaw.json','r',encoding='utf-8') as f:
    data=json.load(f)
print('agent_ids=', [x.get('id') for x in data.get('agents',{}).get('list',[])])
print('bindings=', data.get('bindings',[]))
PY
```
