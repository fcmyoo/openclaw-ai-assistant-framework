# OpenClaw 专属助手改造方案

## 目标

把当前仓库从“概念型框架”改造成“面向现有新加坡实例的专属助手源码仓库”，并以增量方式接入远端 OpenClaw。

## 已确认现状

### 远端运行态

- 服务器：`124.156.198.237`
- OpenClaw 版本：`2026.3.2`
- 主配置：`~/.openclaw/openclaw.json`
- 已有多个 agent：`boss`、`dev`、`app`、`finance`、`strategy`、`telegram`、`feishu_group_bot_all`
- 已配置多个渠道：`telegram`、`discord`、`qqbot`、`wecom`、`feishu`
- 当前 `openclaw cron list` 返回空

### 当前仓库问题

1. `install.sh` 面向全新环境，不适合现网增量接入
2. 多个脚本写死作者环境路径
3. 部分“能力”只是演示脚本，不是 OpenClaw 运行时集成
4. 文档与真实运行态之间存在映射缺口

## 设计原则

### KISS

- 第一阶段只新增一个独立 agent
- 第一阶段只接一个私有入口
- 第一阶段只落 4 个最小任务

### YAGNI

- 不先做自动技能安装
- 不先做自我进化闭环
- 不先改造所有现有 agent

### DRY

- 工作区模板统一放在 `workspace/private-assistant/`
- 运行态补丁统一放在 `runtime/private-assistant/`
- 运维脚本统一放在 `ops/`

### SOLID

- 工作区文件负责行为和记忆
- 运行态补丁负责 OpenClaw 配置接入
- 运维脚本负责同步和审计

## 目标目录

```text
workspace/private-assistant/
runtime/private-assistant/
ops/
docs/
```

## 分阶段实施

### 阶段 1：安全基线

1. 备份远端 `openclaw.json`
2. 外置密钥到环境变量或 `.env`
3. 轮换已暴露的密钥
4. 冻结现有 agent 与 channel 绑定表

### 阶段 2：新建专属 agent

1. 新增 `private_assistant` agent
2. 使用独立 workspace：`/root/.openclaw/workspace-private-assistant`
3. 单独绑定私有入口
4. 保持现有 agent 不变

### 阶段 3：沉淀专属上下文

1. 完成 `IDENTITY.md`
2. 完成 `USER.md`
3. 完成 `TOOLS.md`
4. 建立 `MEMORY.md` 和 `memory/YYYY-MM-DD.md`

### 阶段 4：恢复最小自动化

1. `heartbeat`
2. `daily-summary`
3. `workspace-backup`
4. `model-health`

### 阶段 5：灰度验证

1. 仅绑定单个私有入口
2. 验证会话、记忆、部署辅助、日报能力
3. 稳定后再扩展第二入口

## 本次仓库新增内容

- 工作区模板：`workspace/private-assistant/`
- 运行态补丁样例：`runtime/private-assistant/openclaw.agent-patch.example.json`
- 环境变量模板：`runtime/private-assistant/.env.example`
- 运维脚本：`ops/deploy-private-assistant.sh`、`ops/audit-openclaw.sh`

## 下一步建议

1. 先补全工作区中的身份和用户信息
2. 生成面向远端真实 `openclaw.json` 的精确合并补丁
3. 审核后再决定是否执行服务器写入
