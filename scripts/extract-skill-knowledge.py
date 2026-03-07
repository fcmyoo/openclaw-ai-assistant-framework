#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取单个 skill 的基础知识点。
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path


DEFAULT_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))


def parse_args():
    parser = argparse.ArgumentParser(description="提取单个 skill 的基础知识点")
    parser.add_argument("skill_name", help="技能目录名")
    parser.add_argument("--workspace", default=DEFAULT_WORKSPACE, help="OpenClaw 工作区目录")
    return parser.parse_args()


def extract_skill_knowledge(skill_name, skills_dir):
    skill_dir = skills_dir / skill_name
    if not skill_dir.exists():
        return None

    knowledge = {
        "name": skill_name,
        "category": infer_category(skill_name),
        "knowledge_points": [],
        "best_practices": [],
        "patterns": [],
        "learned_at": datetime.now().isoformat(),
    }

    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        knowledge["knowledge_points"] = extract_points(content)

    for filename in ["index.js", "main.py", "skill.js", "skill.py"]:
        filepath = skill_dir / filename
        if not filepath.exists():
            continue
        code = filepath.read_text(encoding="utf-8")
        knowledge["best_practices"] = extract_best_practices(code)
        knowledge["patterns"] = extract_patterns(code)

    return knowledge


def extract_points(content):
    points = []
    for line in content.split("\n"):
        if line.startswith("# ") or line.startswith("## "):
            points.append(line.strip("# ").strip())
    return points[:5]


def extract_best_practices(code):
    practices = []
    for line in code.split("\n"):
        if "best practice" in line.lower() or "最佳实践" in line:
            practices.append(line.strip())
    return practices[:3]


def extract_patterns(code):
    patterns = []
    if "async" in code and "await" in code:
        patterns.append("异步模式")
    if "class" in code:
        patterns.append("面向对象")
    if "try" in code and "catch" in code:
        patterns.append("错误处理")
    return patterns


def infer_category(skill_name):
    if "image" in skill_name or "photo" in skill_name:
        return "视觉创作"
    if "video" in skill_name:
        return "视频制作"
    if "content" in skill_name or "writing" in skill_name:
        return "内容创作"
    if "social" in skill_name or "twitter" in skill_name:
        return "社交媒体"
    if "analytics" in skill_name or "data" in skill_name:
        return "数据分析"
    return "通用"


def save_knowledge(knowledge, knowledge_base):
    if knowledge_base.exists():
        kb = json.loads(knowledge_base.read_text(encoding="utf-8"))
    else:
        kb = {"skills": []}

    kb["skills"].append(knowledge)
    knowledge_base.parent.mkdir(parents=True, exist_ok=True)
    knowledge_base.write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    args = parse_args()
    workspace = Path(args.workspace)
    skills_dir = workspace / "skills"
    knowledge_base = workspace / "data" / "skill-knowledge-base.json"
    knowledge = extract_skill_knowledge(args.skill_name, skills_dir)

    if not knowledge:
        print(f"无法提取 {args.skill_name} 的知识点")
        return 1

    save_knowledge(knowledge, knowledge_base)
    print(f"已提取 {args.skill_name} 的知识点")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
