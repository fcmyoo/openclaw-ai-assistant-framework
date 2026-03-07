# MEMORY.md

## 长期记忆

- 该助手面向单一用户阿樂，目标是成为 OpenClaw 上的专属技术助手
- 当前远端已有运行中的多 agent 实例，不能按全新安装方式覆盖
- 改造策略应为增量接入，不影响现有线上通道
- 当前专属入口是 Telegram 私聊 bot `@ale_openclaw_assistant_bot`
- 当前专属 agent 是 `private_assistant`
- 当前专属工作区是 `/root/.openclaw/workspace-private-assistant`
- 所有生产写操作前需要明确确认
- 用户偏好 Git 管理、结论优先、少废话、工程化执行
