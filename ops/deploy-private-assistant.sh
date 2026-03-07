#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

: "${OPENCLAW_HOME:=/root/.openclaw}"
: "${OPENCLAW_WORKSPACE:=/root/.openclaw/workspace-private-assistant}"

echo "[1/4] 创建专属工作区目录"
mkdir -p "${OPENCLAW_WORKSPACE}/memory"

echo "[2/4] 同步工作区模板"
cp "${REPO_ROOT}/workspace/private-assistant/AGENTS.md" "${OPENCLAW_WORKSPACE}/AGENTS.md"
cp "${REPO_ROOT}/workspace/private-assistant/IDENTITY.md" "${OPENCLAW_WORKSPACE}/IDENTITY.md"
cp "${REPO_ROOT}/workspace/private-assistant/USER.md" "${OPENCLAW_WORKSPACE}/USER.md"
cp "${REPO_ROOT}/workspace/private-assistant/TOOLS.md" "${OPENCLAW_WORKSPACE}/TOOLS.md"
cp "${REPO_ROOT}/workspace/private-assistant/SOUL.md" "${OPENCLAW_WORKSPACE}/SOUL.md"
cp "${REPO_ROOT}/workspace/private-assistant/MEMORY.md" "${OPENCLAW_WORKSPACE}/MEMORY.md"

echo "[3/4] 输出待人工合并的配置补丁"
cat "${REPO_ROOT}/runtime/private-assistant/openclaw.agent-patch.example.json"

echo
echo "[4/4] 完成"
echo "已同步工作区模板到 ${OPENCLAW_WORKSPACE}"
echo "注意：此脚本不会直接改写 ${OPENCLAW_HOME}/openclaw.json"
echo "请先人工审阅补丁，再决定如何合并。"
