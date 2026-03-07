#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量提取所有已安装技能的知识点。
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


DEFAULT_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))


def parse_args():
    parser = argparse.ArgumentParser(description="批量提取技能知识")
    parser.add_argument("--workspace", default=DEFAULT_WORKSPACE, help="OpenClaw 工作区目录")
    parser.add_argument(
        "--extract-script",
        help="单技能提取脚本路径，默认使用当前仓库下的 extract-skill-knowledge-enhanced.py",
    )
    parser.add_argument("--timeout", type=int, default=30, help="单次提取超时时间，单位秒")
    return parser.parse_args()


def get_installed_skills(skills_dir):
    if not skills_dir.exists():
        return []
    return sorted([item.name for item in skills_dir.iterdir() if item.is_dir()])


def get_extracted_skills(knowledge_base):
    if not knowledge_base.exists():
        return []
    with knowledge_base.open("r", encoding="utf-8") as handle:
        kb = json.load(handle)
    return [item["name"] for item in kb.get("skills", []) if isinstance(item, dict) and item.get("name")]


def main():
    args = parse_args()
    workspace = Path(args.workspace)
    skills_dir = workspace / "skills"
    knowledge_base = workspace / "data" / "skill-knowledge-base.json"
    default_extract_script = Path(__file__).with_name("extract-skill-knowledge-enhanced.py")
    extract_script = Path(args.extract_script) if args.extract_script else default_extract_script

    all_skills = get_installed_skills(skills_dir)
    extracted_skills = get_extracted_skills(knowledge_base)
    to_extract = [skill for skill in all_skills if skill not in extracted_skills]

    print(f"已安装技能: {len(all_skills)} 个")
    print(f"已提取知识: {len(extracted_skills)} 个")
    print(f"待提取知识: {len(to_extract)} 个")

    if not to_extract:
        print("所有技能知识已提取完毕")
        return 0

    success_count = 0
    failed_count = 0
    python_executable = sys.executable or "python3"

    for index, skill in enumerate(to_extract, start=1):
        print(f"[{index}/{len(to_extract)}] 提取: {skill}")
        try:
            result = subprocess.run(
                [python_executable, str(extract_script), skill, "--workspace", str(workspace)],
                capture_output=True,
                text=True,
                timeout=args.timeout,
                check=False,
            )
            if result.returncode == 0:
                success_count += 1
                print("  成功")
            else:
                failed_count += 1
                print(f"  失败: {(result.stderr or result.stdout).strip()[:120]}")
        except Exception as exc:
            failed_count += 1
            print(f"  异常: {str(exc)[:120]}")

        if index % 10 == 0:
            time.sleep(1)

    print("=" * 60)
    print("批量提取完成")
    print(f"成功: {success_count} 个")
    print(f"失败: {failed_count} 个")
    print("=" * 60)
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
