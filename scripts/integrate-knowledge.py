#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识整合脚本。
"""

import argparse
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path


DEFAULT_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))


def parse_args():
    parser = argparse.ArgumentParser(description="整合技能知识库并生成组合能力")
    parser.add_argument("--workspace", default=DEFAULT_WORKSPACE, help="OpenClaw 工作区目录")
    return parser.parse_args()


def integrate_knowledge(workspace):
    knowledge_base = workspace / "data" / "skill-knowledge-base.json"
    skill_combinations = workspace / "data" / "skill-combinations.json"
    new_capabilities = workspace / "data" / "new-capabilities.json"

    if not knowledge_base.exists():
        print("知识库不存在")
        return 1

    kb = json.loads(knowledge_base.read_text(encoding="utf-8"))
    skills = kb.get("skills", [])
    if len(skills) < 2:
        print("知识库技能太少，暂不整合")
        return 0

    patterns = find_patterns(skills)
    combinations = find_combinations(skills)
    capabilities = create_new_capabilities(patterns, combinations)
    save_results(skill_combinations, new_capabilities, combinations, capabilities)

    print(f"当前知识库: {len(skills)} 个技能")
    print(f"发现设计模式: {len(patterns)} 种")
    print(f"发现技能组合: {len(combinations)} 个")
    print(f"创造新能力: {len(capabilities)} 个")
    print("知识整合完成")
    return 0


def find_patterns(skills):
    all_patterns = []
    for skill in skills:
        all_patterns.extend(skill.get("patterns", []))
    return [pattern for pattern, _count in Counter(all_patterns).most_common(10)]


def find_combinations(skills):
    combinations = []
    categories = {}
    for skill in skills:
        category = skill.get("category", "通用")
        categories.setdefault(category, []).append(skill["name"])

    for category, skill_names in categories.items():
        if len(skill_names) >= 2:
            combinations.append(
                {
                    "name": f"{category}工作流",
                    "skills": skill_names,
                    "description": f"整合 {len(skill_names)} 个 {category} 相关技能",
                    "created_at": datetime.now().isoformat(),
                    "usage_count": 0,
                }
            )

    combinations.extend(find_cross_category_combinations(skills))
    return combinations


def find_cross_category_combinations(skills):
    combinations = []
    visual_skills = [item for item in skills if item.get("category") == "视觉创作"]
    content_skills = [item for item in skills if item.get("category") == "内容创作"]
    social_skills = [item for item in skills if item.get("category") == "社交媒体"]
    analytics_skills = [item for item in skills if item.get("category") == "数据分析"]

    if visual_skills and content_skills:
        combinations.append(
            {
                "name": "完整内容生产流程",
                "skills": [item["name"] for item in visual_skills[:2]] + [item["name"] for item in content_skills[:2]],
                "description": "视觉创作 + 内容创作 = 完整内容生产",
                "created_at": datetime.now().isoformat(),
                "usage_count": 0,
                "type": "cross_category",
            }
        )

    if social_skills and analytics_skills:
        combinations.append(
            {
                "name": "智能社交媒体运营",
                "skills": [item["name"] for item in social_skills[:2]]
                + [item["name"] for item in analytics_skills[:2]],
                "description": "社交媒体 + 数据分析 = 智能运营",
                "created_at": datetime.now().isoformat(),
                "usage_count": 0,
                "type": "cross_category",
            }
        )

    return combinations


def create_new_capabilities(patterns, combinations):
    capabilities = []
    if "异步模式（async/await）" in patterns:
        capabilities.append(
            {
                "name": "高效异步处理能力",
                "description": "整合异步模式，提升任务处理效率",
                "source_patterns": ["异步模式（async/await）"],
                "created_at": datetime.now().isoformat(),
                "status": "ready",
            }
        )
    if "事件驱动模式" in patterns:
        capabilities.append(
            {
                "name": "实时事件响应能力",
                "description": "基于事件驱动，实时响应各类事件",
                "source_patterns": ["事件驱动模式"],
                "created_at": datetime.now().isoformat(),
                "status": "ready",
            }
        )
    for combo in combinations:
        if combo.get("type") == "cross_category":
            capabilities.append(
                {
                    "name": combo["name"],
                    "description": combo["description"],
                    "source_skills": combo["skills"],
                    "created_at": datetime.now().isoformat(),
                    "status": "ready",
                }
            )
    return capabilities


def save_results(skill_combinations, new_capabilities, combinations, capabilities):
    skill_combinations.parent.mkdir(parents=True, exist_ok=True)
    skill_combinations.write_text(json.dumps({"combinations": combinations}, ensure_ascii=False, indent=2), encoding="utf-8")
    new_capabilities.write_text(json.dumps({"capabilities": capabilities}, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    args = parse_args()
    return integrate_knowledge(Path(args.workspace))


if __name__ == "__main__":
    raise SystemExit(main())
