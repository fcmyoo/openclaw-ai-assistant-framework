# TOOLS.md

## SSH

- `新加坡服务器` -> `124.156.198.237`，用户 `root`

## OpenClaw

- 主配置：`~/.openclaw/openclaw.json`
- 当前已存在多 agent 和多渠道绑定
- 当前没有可见 cron jobs

## 工作原则

- 远端默认先做只读检查
- 所有增量改造优先以新 agent 方式落地
- 不直接覆盖现有 `boss/dev/app/finance/strategy/telegram` agent
