#!/usr/bin/env bash
set -euo pipefail

: "${REPO_ROOT:=/root/openclaw-ai-assistant-framework}"
: "${OPENCLAW_WORKSPACE:=/root/.openclaw/workspace-private-assistant}"

HEALTH_SCRIPT="${REPO_ROOT}/scripts/model-health-check.py"
EVOLUTION_SCRIPT="${REPO_ROOT}/scripts/daily-evolution.py"
KNOWLEDGE_BATCH_SCRIPT="${REPO_ROOT}/scripts/batch-extract-knowledge.py"
KNOWLEDGE_INTEGRATE_SCRIPT="${REPO_ROOT}/scripts/integrate-knowledge.py"

cat <<EOF
# 1. heartbeat / 每30分钟整理日报
openclaw cron add --name "private-assistant-heartbeat" --cron "*/30 * * * *" --exact --command "cd ${REPO_ROOT} && OPENCLAW_WORKSPACE=${OPENCLAW_WORKSPACE} python3 ${EVOLUTION_SCRIPT} --date \$(date +%F) >/dev/null"

# 2. daily-summary / 每天21:30生成最新日报
openclaw cron add --name "private-assistant-daily-summary" --cron "30 21 * * *" --exact --command "cd ${REPO_ROOT} && OPENCLAW_WORKSPACE=${OPENCLAW_WORKSPACE} python3 ${EVOLUTION_SCRIPT} >/dev/null"

# 3. model-health / 每6小时检查模型池
openclaw cron add --name "private-assistant-model-health" --cron "0 */6 * * *" --exact --command "cd ${REPO_ROOT} && OPENCLAW_WORKSPACE=${OPENCLAW_WORKSPACE} python3 ${HEALTH_SCRIPT} >/dev/null"

# 4. knowledge-batch / 每天02:10提取新增技能知识
openclaw cron add --name "private-assistant-knowledge-batch" --cron "10 2 * * *" --exact --command "cd ${REPO_ROOT} && OPENCLAW_WORKSPACE=${OPENCLAW_WORKSPACE} python3 ${KNOWLEDGE_BATCH_SCRIPT} >/dev/null"

# 5. knowledge-integrate / 每天02:40整合知识库
openclaw cron add --name "private-assistant-knowledge-integrate" --cron "40 2 * * *" --exact --command "cd ${REPO_ROOT} && OPENCLAW_WORKSPACE=${OPENCLAW_WORKSPACE} python3 ${KNOWLEDGE_INTEGRATE_SCRIPT} >/dev/null"

# 6. 查看结果
openclaw cron list
EOF
