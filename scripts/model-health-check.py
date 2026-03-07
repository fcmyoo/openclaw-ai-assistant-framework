#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型池健康检查脚本

默认从 OPENCLAW_WORKSPACE 读取配置，也支持命令行参数覆盖。
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
DEFAULT_CONFIG_FILE = Path(DEFAULT_WORKSPACE) / "config" / "model-pools.json"
DEFAULT_LOG_FILE = Path(DEFAULT_WORKSPACE) / "logs" / "model-health.log"
DEFAULT_STATUS_FILE = Path(DEFAULT_WORKSPACE) / "data" / "model-health-status.json"


def parse_args():
    parser = argparse.ArgumentParser(description="检查 OpenClaw 模型池健康状态")
    parser.add_argument("--workspace", default=DEFAULT_WORKSPACE, help="OpenClaw 工作区目录")
    parser.add_argument("--config", help="模型池配置文件路径")
    parser.add_argument("--log-file", help="日志文件路径")
    parser.add_argument("--status-file", help="状态输出文件路径")
    parser.add_argument("--command-timeout", type=int, default=10, help="openclaw 命令超时时间，单位秒")
    return parser.parse_args()


def log(message, log_file, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {message}"
    print(line)

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run_openclaw_models_status(timeout_seconds):
    return subprocess.run(
        ["openclaw", "models", "status"],
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )


def check_model_health(model_name, timeout_seconds):
    checked_at = datetime.now().isoformat()

    try:
        result = run_openclaw_models_status(timeout_seconds)
    except FileNotFoundError:
        return {
            "status": "error",
            "api_reachable": False,
            "error": "openclaw command not found",
            "last_check": checked_at,
        }
    except Exception as exc:
        return {
            "status": "error",
            "api_reachable": False,
            "error": str(exc)[:160],
            "last_check": checked_at,
        }

    if result.returncode != 0:
        return {
            "status": "error",
            "api_reachable": False,
            "error": (result.stderr or "unknown error").strip()[:160],
            "last_check": checked_at,
        }

    if model_name in result.stdout:
        return {
            "status": "healthy",
            "api_reachable": True,
            "last_check": checked_at,
        }

    return {
        "status": "not_configured",
        "api_reachable": False,
        "last_check": checked_at,
    }


def load_config(config_file):
    with Path(config_file).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    args = parse_args()
    workspace = Path(args.workspace)
    config_file = Path(args.config) if args.config else workspace / "config" / "model-pools.json"
    log_file = Path(args.log_file) if args.log_file else workspace / "logs" / "model-health.log"
    status_file = Path(args.status_file) if args.status_file else workspace / "data" / "model-health-status.json"

    log("=" * 60, log_file)
    log("模型池健康检查开始", log_file)
    log("=" * 60, log_file)

    try:
        config = load_config(config_file)
    except Exception as exc:
        log(f"读取配置失败: {exc}", log_file, "ERROR")
        return 1

    pools = config.get("pools", {})
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "workspace": str(workspace),
        "config_file": str(config_file),
        "pools": {},
    }

    for pool_name in ["fast", "smart", "text", "vision"]:
        pool_config = pools.get(pool_name)
        if not pool_config:
            continue

        pool_display_name = pool_config.get("name", pool_name)
        primary_model = pool_config.get("primary")
        fallback_model = pool_config.get("fallback")

        log(f"检查模型池: {pool_display_name} ({pool_name})", log_file)
        pool_status = {"name": pool_display_name, "primary": {}, "fallback": {}}

        if primary_model:
            pool_status["primary"] = check_model_health(primary_model, args.command_timeout)
            log(f"  Primary {primary_model}: {pool_status['primary']['status']}", log_file)
        else:
            pool_status["primary"] = {"status": "missing", "api_reachable": False}
            log("  Primary missing", log_file, "WARN")

        if fallback_model:
            pool_status["fallback"] = check_model_health(fallback_model, args.command_timeout)
            log(f"  Fallback {fallback_model}: {pool_status['fallback']['status']}", log_file)
        else:
            pool_status["fallback"] = {"status": "missing", "api_reachable": False}
            log("  Fallback missing", log_file, "WARN")

        health_status["pools"][pool_name] = pool_status

    status_file.parent.mkdir(parents=True, exist_ok=True)
    with status_file.open("w", encoding="utf-8") as handle:
        json.dump(health_status, handle, indent=2, ensure_ascii=False)

    total_count = len(health_status["pools"])
    healthy_count = sum(
        1 for pool_status in health_status["pools"].values() if pool_status["primary"].get("status") == "healthy"
    )
    health_rate = (healthy_count / total_count * 100) if total_count else 0

    log("=" * 60, log_file)
    log(f"健康率: {healthy_count}/{total_count} ({health_rate:.0f}%)", log_file)
    log(f"状态文件: {status_file}", log_file)
    log("=" * 60, log_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
