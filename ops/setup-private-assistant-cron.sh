#!/usr/bin/env bash
set -euo pipefail

: "${OPENCLAW_HOME:=/root/.openclaw}"
: "${OPENCLAW_WORKSPACE:=/root/.openclaw/workspace-private-assistant}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

HEALTH_SCRIPT="${REPO_ROOT}/scripts/model-health-check.py"
EVOLUTION_SCRIPT="${REPO_ROOT}/scripts/daily-evolution.py"

echo "[1/3] 环境检查"
command -v openclaw >/dev/null 2>&1
command -v python3 >/dev/null 2>&1
test -d "${OPENCLAW_WORKSPACE}"
test -f "${HEALTH_SCRIPT}"
test -f "${EVOLUTION_SCRIPT}"

echo "[2/3] 配置最小 cron 任务"
openclaw cron add \
  --name "private-assistant-heartbeat" \
  --cron "*/30 * * * *" \
  --exact \
  --command "cd ${REPO_ROOT} && OPENCLAW_WORKSPACE=${OPENCLAW_WORKSPACE} python3 ${EVOLUTION_SCRIPT} --date \$(date +%F) >/dev/null"

openclaw cron add \
  --name "private-assistant-daily-summary" \
  --cron "30 21 * * *" \
  --exact \
  --command "cd ${REPO_ROOT} && OPENCLAW_WORKSPACE=${OPENCLAW_WORKSPACE} python3 ${EVOLUTION_SCRIPT} --stdout >/dev/null"

openclaw cron add \
  --name "private-assistant-model-health" \
  --cron "0 */6 * * *" \
  --exact \
  --command "cd ${REPO_ROOT} && OPENCLAW_WORKSPACE=${OPENCLAW_WORKSPACE} python3 ${HEALTH_SCRIPT} >/dev/null"

echo "[3/3] 当前 cron 列表"
openclaw cron list
