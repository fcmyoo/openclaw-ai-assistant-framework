#!/usr/bin/env bash
set -euo pipefail

: "${OPENCLAW_HOME:=/root/.openclaw}"
: "${OPENCLAW_CONFIG:=${OPENCLAW_HOME}/openclaw.json}"
: "${OPENCLAW_WORKSPACE:=/root/.openclaw/workspace-private-assistant}"
: "${REPO_ROOT:=/root/openclaw-ai-assistant-framework}"

BACKUP_FILE="${OPENCLAW_CONFIG}.before-private-assistant.$(date +%Y%m%d-%H%M%S)"

echo "[1/6] 基础检查"
command -v openclaw >/dev/null 2>&1
command -v python3 >/dev/null 2>&1
test -f "${OPENCLAW_CONFIG}"
test -d "${REPO_ROOT}"

echo "[2/6] 备份 openclaw.json"
cp "${OPENCLAW_CONFIG}" "${BACKUP_FILE}"
echo "备份文件: ${BACKUP_FILE}"

echo "[3/6] 同步专属工作区模板"
mkdir -p "${OPENCLAW_WORKSPACE}/memory"
cd "${REPO_ROOT}"
bash ops/deploy-private-assistant.sh

echo "[4/6] 输出精确补丁位置"
echo "请人工参考以下文件编辑 ${OPENCLAW_CONFIG}:"
echo "  ${REPO_ROOT}/runtime/private-assistant/openclaw.exact-append.patch.md"
echo "  ${REPO_ROOT}/docs/private-assistant-openclaw-json-patch.md"

echo "[5/6] 编辑完成后执行 JSON 校验"
echo "python3 -m json.tool ${OPENCLAW_CONFIG} >/dev/null"

echo "[6/6] 后续建议"
echo "1. 手动跑 scripts/model-health-check.py"
echo "2. 手动跑 scripts/daily-evolution.py --stdout"
echo "3. 再执行 bash ops/print-private-assistant-cron-commands.sh"
