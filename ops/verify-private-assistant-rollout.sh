#!/usr/bin/env bash
set -euo pipefail

: "${OPENCLAW_HOME:=/root/.openclaw}"
: "${OPENCLAW_CONFIG:=${OPENCLAW_HOME}/openclaw.json}"
: "${OPENCLAW_WORKSPACE:=/root/.openclaw/workspace-private-assistant}"
: "${REPO_ROOT:=/root/openclaw-ai-assistant-framework}"

echo "[1/7] 检查配置合法性"
python3 -m json.tool "${OPENCLAW_CONFIG}" >/dev/null

echo "[2/7] 检查 private_assistant 是否已写入"
python3 - <<PY
import json
with open("${OPENCLAW_CONFIG}", "r", encoding="utf-8") as f:
    data = json.load(f)
agent_ids = [item.get("id") for item in data.get("agents", {}).get("list", [])]
binding_ids = [item.get("agentId") for item in data.get("bindings", [])]
print("agent_ids=", agent_ids)
print("binding_ids=", binding_ids)
assert "private_assistant" in agent_ids, "private_assistant not found in agents.list"
assert "private_assistant" in binding_ids, "private_assistant not found in bindings"
PY

echo "[3/7] 检查工作区文件"
find "${OPENCLAW_WORKSPACE}" -maxdepth 2 -type f | sort

echo "[4/7] 手动执行模型健康检查"
cd "${REPO_ROOT}"
OPENCLAW_WORKSPACE="${OPENCLAW_WORKSPACE}" python3 scripts/model-health-check.py || true

echo "[5/7] 手动执行每日报告"
OPENCLAW_WORKSPACE="${OPENCLAW_WORKSPACE}" python3 scripts/daily-evolution.py --stdout || true

echo "[6/7] 当前 cron"
openclaw cron list || true

echo "[7/7] 结果文件"
find "${OPENCLAW_WORKSPACE}/data" -maxdepth 3 -type f 2>/dev/null | sort || true
