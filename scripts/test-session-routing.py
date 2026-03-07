#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话路由测试脚本。
"""

import argparse
import json
import os
from pathlib import Path


DEFAULT_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))


def parse_args():
    parser = argparse.ArgumentParser(description="测试模型池路由规则")
    parser.add_argument("--workspace", default=DEFAULT_WORKSPACE, help="OpenClaw 工作区目录")
    return parser.parse_args()


def load_config(config_file):
    with Path(config_file).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def identify_task_type(user_input):
    vision_keywords = ["图片", "图像", "照片", "截图", "视频", "影片", "画面", "看图", "识图", "分析图", "多模态"]
    for keyword in vision_keywords:
        if keyword in user_input:
            return "vision"

    keywords_map = {
        "fast": ["快速", "简单", "闲聊", "随便", "查询", "搜索", "查找", "修改", "调整", "更新"],
        "smart": ["分析", "推理", "思考", "研究", "编程", "代码", "开发", "编写", "策略", "规划", "方案", "计划", "深度", "详细", "全面", "透彻"],
        "text": ["文档", "文章", "报告", "内容", "长文本", "大段", "全文", "写作", "创作", "撰写", "总结", "摘要", "提炼"],
    }

    for pool_name, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword in user_input:
                return pool_name
    return "smart"


def test_routing(workspace):
    config = load_config(Path(workspace) / "config" / "model-pools.json")
    test_cases = [
        "快速回复一下",
        "分析一下B站数据",
        "帮我写一篇文章",
        "看图分析这张截图",
        "随便聊聊",
        "编写一个Python脚本",
        "总结这段长文本",
        "优化视频内容",
    ]

    print("=" * 60)
    print("Session Routing Test")
    print("=" * 60)

    for test_input in test_cases:
        pool_name = identify_task_type(test_input)
        pool = config["pools"].get(pool_name)
        if not pool:
            print(f"\nInput: {test_input}")
            print(f"Pool not configured: {pool_name}")
            continue
        print(f"\nInput: {test_input}")
        print(f"Identified Pool: {pool['name']} ({pool_name})")
        print(f"Primary Model: {pool['primary']}")
        print(f"Fallback Model: {pool['fallback']}")
        print(f"Output: 当前任务属于{pool['name']}，应该使用{pool_name}模型池")

    print("\n" + "=" * 60)


def main():
    args = parse_args()
    test_routing(args.workspace)


if __name__ == "__main__":
    main()
