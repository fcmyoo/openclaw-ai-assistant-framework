#!/usr/bin/env bash
set -euo pipefail

: "${OPENCLAW_HOME:=/root/.openclaw}"

echo "== OpenClaw 版本 =="
openclaw --version || true

echo
echo "== 配置文件 =="
ls -lah "${OPENCLAW_HOME}/openclaw.json" || true

echo
echo "== Agent 目录 =="
find "${OPENCLAW_HOME}/agents" -maxdepth 2 -type d | sort || true

echo
echo "== Workspace 目录 =="
find "${OPENCLAW_HOME}" -maxdepth 1 -type d -name "workspace*" | sort || true

echo
echo "== Cron =="
openclaw cron list || true
