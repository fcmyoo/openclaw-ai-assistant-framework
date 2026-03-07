#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版 skill 知识提取脚本。
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path


DEFAULT_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))


def parse_args():
    parser = argparse.ArgumentParser(description="提取单个 skill 的增强知识")
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
        "api_interfaces": [],
        "config_params": [],
        "use_cases": [],
        "dependencies": [],
        "learned_at": datetime.now().isoformat(),
    }

    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        knowledge["knowledge_points"] = extract_points(content)
        knowledge["use_cases"] = extract_use_cases(content)
        knowledge["best_practices"] = extract_best_practices_from_doc(content)

    for filename in ["index.js", "main.py", "skill.js", "skill.py", "index.ts", "main.ts"]:
        filepath = skill_dir / filename
        if not filepath.exists():
            continue
        code = filepath.read_text(encoding="utf-8")
        knowledge["patterns"].extend(extract_patterns(code))
        knowledge["api_interfaces"].extend(extract_api_interfaces(code))
        knowledge["config_params"].extend(extract_config_params(code))
        knowledge["best_practices"].extend(extract_best_practices(code))
        knowledge["dependencies"].extend(extract_dependencies(code))

    package_json = skill_dir / "package.json"
    if package_json.exists():
        pkg = json.loads(package_json.read_text(encoding="utf-8"))
        if "dependencies" in pkg:
            knowledge["dependencies"].extend(list(pkg["dependencies"].keys()))

    for key in ["patterns", "api_interfaces", "best_practices", "dependencies", "config_params", "use_cases"]:
        knowledge[key] = list(dict.fromkeys(knowledge[key]))

    return knowledge


def extract_points(content):
    points = []
    lines = content.split("\n")
    for line in lines:
        if line.startswith("## ") or line.startswith("### "):
            point = line.strip("# ").strip()
            if point and len(point) > 3:
                points.append(point)

    keywords = ["功能", "特性", "features", "usage", "使用", "说明", "description"]
    for line in lines:
        for keyword in keywords:
            if keyword in line.lower() and len(line) > 10:
                clean_line = line.strip()
                if clean_line and not clean_line.startswith("#"):
                    points.append(clean_line[:100])
                break
    return points[:10]


def extract_use_cases(content):
    use_cases = []
    patterns = [
        r"使用场景[：:]\s*(.*?)(?=\n\n|\n#|$)",
        r"Use Cases[：:]\s*(.*?)(?=\n\n|\n#|$)",
        r"When to Use[：:]\s*(.*?)(?=\n\n|\n#|$)",
        r"何时使用[：:]\s*(.*?)(?=\n\n|\n#|$)",
        r"Usage[：:]\s*(.*?)(?=\n\n|\n#|$)",
        r"使用方法[：:]\s*(.*?)(?=\n\n|\n#|$)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            for line in match.strip().split("\n")[:5]:
                clean = re.sub(r"^[#\-\*]\s*", "", line.strip())
                if clean and len(clean) > 5 and not clean.startswith("```"):
                    use_cases.append(clean[:150])

    if not use_cases:
        features_match = re.search(r"Features[：:]\s*(.*?)(?=\n\n|\n#|$)", content, re.DOTALL | re.IGNORECASE)
        if features_match:
            for line in features_match.group(1).strip().split("\n")[:5]:
                clean = re.sub(r"^[#\-\*]\s*", "", line.strip())
                if clean and len(clean) > 5:
                    use_cases.append(clean[:150])
    return use_cases[:8]


def extract_best_practices_from_doc(content):
    practices = []
    patterns = [
        r"最佳实践[：:](.*?)(?=\n\n|\n#|$)",
        r"Best Practices[：:](.*?)(?=\n\n|\n#|$)",
        r"注意事项[：:](.*?)(?=\n\n|\n#|$)",
        r"Notes[：:](.*?)(?=\n\n|\n#|$)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        for match in matches:
            for sentence in match.strip().split("\n")[:3]:
                clean = sentence.strip()
                if clean and len(clean) > 5:
                    practices.append(clean[:150])
    return practices[:5]


def extract_patterns(code):
    patterns = []
    if "async" in code and "await" in code:
        patterns.append("异步模式（async/await）")
    if "class " in code:
        patterns.append("面向对象编程（OOP）")
    if "try" in code and ("catch" in code or "except" in code):
        patterns.append("异常处理机制")
    if "callback" in code.lower() or "=> {" in code:
        patterns.append("回调模式")
    if "event" in code.lower() or "emit(" in code or "on(" in code:
        patterns.append("事件驱动模式")
    if "factory" in code.lower() or "create" in code.lower():
        patterns.append("工厂模式")
    if "singleton" in code.lower() or "getInstance" in code:
        patterns.append("单例模式")
    if "Promise" in code or ".then(" in code:
        patterns.append("Promise模式")
    if "config" in code.lower() or "settings" in code.lower():
        patterns.append("配置管理模式")
    if "plugin" in code.lower() or "middleware" in code.lower():
        patterns.append("插件/中间件模式")
    return patterns


def extract_api_interfaces(code):
    apis = []
    func_patterns = [
        r"function\s+(\w+)\s*\(",
        r"const\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>",
        r"def\s+(\w+)\s*\(",
        r"async\s+(\w+)\s*\(",
        r"export\s+(?:async\s+)?function\s+(\w+)",
    ]
    for pattern in func_patterns:
        apis.extend(re.findall(pattern, code)[:5])
    apis.extend(re.findall(r"\.(\w+)\s*=\s*(?:async\s*)?\(", code)[:5])
    apis.extend(re.findall(r"exports\.(\w+)", code)[:5])
    for match in re.findall(r"module\.exports\s*=\s*{([^}]+)}", code, re.DOTALL):
        apis.extend(re.findall(r"(\w+)\s*:", match)[:5])
    return list(dict.fromkeys(apis))[:15]


def extract_config_params(code):
    configs = []
    configs.extend(re.findall(r"process\.env\.(\w+)", code)[:5])
    configs.extend(re.findall(r"const\s+(\w+Config|\w+Settings)\s*=", code)[:3])
    return configs[:8]


def extract_best_practices(code):
    practices = []
    comment_patterns = [
        r"//\s*(.*?best.*?practice.*?)\n",
        r"#\s*(.*?best.*?practice.*?)\n",
        r"/\*\*(.*?)\*/",
        r"//\s*(.*?注意.*?)\n",
        r"#\s*(.*?注意.*?)\n",
    ]
    for pattern in comment_patterns:
        matches = re.findall(pattern, code, re.IGNORECASE | re.DOTALL)
        for match in matches:
            clean = match.strip()
            if clean and len(clean) > 10:
                practices.append(clean[:150])
    return practices[:5]


def extract_dependencies(code):
    deps = []
    for pattern in [
        r"require\(['\"](.*?)['\"]\)",
        r"import.*?from\s+['\"](.*?)['\"]",
        r"from\s+(\w+)\s+import",
    ]:
        deps.extend(re.findall(pattern, code)[:5])
    return deps[:10]


def infer_category(skill_name):
    name_lower = skill_name.lower()
    if any(word in name_lower for word in ["image", "photo", "visual", "picture"]):
        return "视觉创作"
    if any(word in name_lower for word in ["video", "remotion", "demo"]):
        return "视频制作"
    if any(word in name_lower for word in ["content", "writing", "copy", "blog", "seo"]):
        return "内容创作"
    if any(word in name_lower for word in ["social", "twitter", "weibo", "instagram", "engagement"]):
        return "社交媒体"
    if any(word in name_lower for word in ["analytics", "data", "report", "metric"]):
        return "数据分析"
    if any(word in name_lower for word in ["agent", "automation", "workflow"]):
        return "自动化代理"
    if any(word in name_lower for word in ["docker", "k8s", "terraform", "aws"]):
        return "DevOps"
    return "通用"


def save_knowledge(knowledge, knowledge_base):
    if knowledge_base.exists():
        kb = json.loads(knowledge_base.read_text(encoding="utf-8"))
    else:
        kb = {"skills": []}

    kb["skills"] = [item for item in kb.get("skills", []) if item.get("name") != knowledge["name"]]
    kb["skills"].append(knowledge)
    knowledge_base.parent.mkdir(parents=True, exist_ok=True)
    knowledge_base.write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    args = parse_args()
    workspace = Path(args.workspace)
    knowledge_base = workspace / "data" / "skill-knowledge-base.json"
    knowledge = extract_skill_knowledge(args.skill_name, workspace / "skills")
    if not knowledge:
        print(f"无法提取 {args.skill_name} 的知识点")
        return 1
    save_knowledge(knowledge, knowledge_base)
    print(f"已提取 {args.skill_name} 的增强知识")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
