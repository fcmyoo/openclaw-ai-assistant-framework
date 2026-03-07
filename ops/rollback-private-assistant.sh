#!/usr/bin/env bash
set -euo pipefail

: "${OPENCLAW_HOME:=/root/.openclaw}"
: "${OPENCLAW_CONFIG:=${OPENCLAW_HOME}/openclaw.json}"

echo "[1/3] 删除 private_assistant 相关 cron"
openclaw cron remove --name "private-assistant-knowledge-integrate" || true
openclaw cron remove --name "private-assistant-knowledge-batch" || true
openclaw cron remove --name "private-assistant-heartbeat" || true
openclaw cron remove --name "private-assistant-daily-summary" || true
openclaw cron remove --name "private-assistant-model-health" || true

echo "[2/3] 请人工恢复配置备份"
echo "可用备份："
ls -lah "${OPENCLAW_HOME}"/openclaw.json.before-private-assistant* "${OPENCLAW_HOME}"/openclaw.json.backup* 2>/dev/null || true

echo "[3/3] 当前 cron 列表"
openclaw cron list || true
