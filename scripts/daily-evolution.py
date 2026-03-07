#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日进化报告脚本

基于工作区中的记忆、技能和历史数据生成日报。
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


DEFAULT_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))


def parse_args():
    parser = argparse.ArgumentParser(description="生成 OpenClaw 每日进化报告")
    parser.add_argument("--workspace", default=DEFAULT_WORKSPACE, help="OpenClaw 工作区目录")
    parser.add_argument("--date", help="指定报告日期，格式 YYYY-MM-DD，默认今天")
    parser.add_argument("--stdout", action="store_true", help="输出报告正文到标准输出")
    return parser.parse_args()


class EvolutionEngine:
    """基于工作区文件生成每日进化报告。"""

    def __init__(self, workspace, report_date):
        self.workspace = Path(workspace)
        self.report_date = report_date
        self.memory_dir = self.workspace / "memory"
        self.reports_dir = self.workspace / "data" / "evolution-reports"
        self.skill_status_file = self.workspace / ".skill-install-status-v2.json"
        self.skills_dir = self.workspace / "skills"
        self.today_memory_file = self.memory_dir / f"{self.report_date}.md"
        self.yesterday_memory_file = self.memory_dir / f"{self.previous_date(self.report_date)}.md"
        self.report_data = {
            "date": self.report_date,
            "sessions": 0,
            "tasks_completed": 0,
            "tokens_used": 0,
            "skills_learned": 0,
            "new_knowledge": [],
            "mistakes": [],
            "skills_to_solidify": [],
            "improvements": [],
            "data_sources": [],
        }

    @staticmethod
    def previous_date(date_text):
        return (datetime.strptime(date_text, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")

    def read_text(self, path):
        if not path.exists():
            return ""
        self.report_data["data_sources"].append(str(path))
        return path.read_text(encoding="utf-8")

    def analyze_memory_file(self, path):
        content = self.read_text(path)
        if not content:
            return

        self.report_data["sessions"] += content.count("## 会话")
        self.report_data["tasks_completed"] += content.count("✅")

        for keyword, summary in [
            ("学会", "记录了新的学习成果"),
            ("学习", "记录了新的学习成果"),
            ("复盘", "进行了任务复盘"),
            ("自动化", "推进了自动化相关能力"),
        ]:
            if keyword in content and summary not in self.report_data["new_knowledge"]:
                self.report_data["new_knowledge"].append(summary)

        for keyword, summary in [
            ("错误", "出现错误并已记录"),
            ("失败", "出现失败案例并已记录"),
            ("回滚", "发生过需要回滚的操作"),
            ("告警", "出现需要关注的告警"),
        ]:
            if keyword in content and summary not in self.report_data["mistakes"]:
                self.report_data["mistakes"].append(summary)

        token_markers = ["Token消耗:", "tokens:", "Tokens:"]
        for marker in token_markers:
            if marker in content:
                self.report_data["tokens_used"] = max(self.report_data["tokens_used"], 1)

    def analyze_today(self):
        self.analyze_memory_file(self.today_memory_file)
        self.analyze_memory_file(self.yesterday_memory_file)

        if not self.skill_status_file.exists():
            return

        try:
            status = json.loads(self.skill_status_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return

        installed_today = []
        for item in status.get("installed", []):
            if not isinstance(item, dict):
                continue
            install_time = str(item.get("time", ""))
            if install_time.startswith(self.report_date):
                installed_today.append(item.get("name", "unknown"))

        self.report_data["skills_learned"] = len(installed_today)
        if installed_today:
            preview = ", ".join(installed_today[:5])
            self.report_data["new_knowledge"].append(f"今日安装技能: {preview}")

    def identify_solidifiable_skills(self):
        if not self.skills_dir.exists():
            return

        skill_names = sorted([item.name for item in self.skills_dir.iterdir() if item.is_dir()])
        if self.report_data["skills_learned"] == 0:
            self.report_data["skills_learned"] = len(skill_names)

        self.report_data["skills_to_solidify"] = skill_names[:3]

    def build_improvements(self):
        if self.report_data["tasks_completed"] == 0:
            self.report_data["improvements"].append("补全每日记忆记录，保证第二天可追溯")
        if not self.report_data["mistakes"]:
            self.report_data["improvements"].append("继续保持低风险变更，重点补可观测性")
        if not self.report_data["skills_to_solidify"]:
            self.report_data["improvements"].append("从本周高频任务中提炼 1 个可复用技能")

    def generate_report(self):
        self.build_improvements()

        lines = [
            f"# 每日进化报告 - {self.report_date}",
            "",
            "## 今日数据",
            "",
            f"- 会话次数: {self.report_data['sessions']}",
            f"- 完成任务: {self.report_data['tasks_completed']}",
            f"- Token消耗: {self.report_data['tokens_used']}",
            f"- 学习技能: {self.report_data['skills_learned']}",
            "",
            "## 学会的新东西",
            "",
        ]

        if self.report_data["new_knowledge"]:
            lines.extend(f"{idx}. {item}" for idx, item in enumerate(self.report_data["new_knowledge"], start=1))
        else:
            lines.append("1. 今日没有检测到明确的新学习记录")

        lines.extend(["", "## 风险与错误", ""])
        if self.report_data["mistakes"]:
            lines.extend(f"{idx}. {item}" for idx, item in enumerate(self.report_data["mistakes"], start=1))
        else:
            lines.append("1. 今日未检测到显式错误记录")

        lines.extend(["", "## 可固化技能", ""])
        if self.report_data["skills_to_solidify"]:
            lines.extend(
                f"{idx}. {item}" for idx, item in enumerate(self.report_data["skills_to_solidify"], start=1)
            )
        else:
            lines.append("1. 今日没有识别到可直接固化的技能目录")

        lines.extend(["", "## 明日改进计划", ""])
        lines.extend(f"{idx}. {item}" for idx, item in enumerate(self.report_data["improvements"], start=1))

        lines.extend(
            [
                "",
                "## 数据来源",
                "",
            ]
        )
        if self.report_data["data_sources"]:
            lines.extend(f"- {item}" for item in self.report_data["data_sources"])
        else:
            lines.append("- 无")

        lines.extend(["", f"_Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_", ""])
        return "\n".join(lines)

    def save_report(self, report):
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = self.reports_dir / f"evolution-report-{self.report_date}.md"
        latest_file = self.reports_dir / "evolution-report-latest.md"
        report_file.write_text(report, encoding="utf-8")
        latest_file.write_text(report, encoding="utf-8")
        return report_file

    def run(self):
        self.analyze_today()
        self.identify_solidifiable_skills()
        report = self.generate_report()
        report_file = self.save_report(report)
        return report, report_file


def main():
    args = parse_args()
    report_date = args.date or datetime.now().strftime("%Y-%m-%d")
    engine = EvolutionEngine(args.workspace, report_date)
    report, report_file = engine.run()

    print(f"报告已生成: {report_file}")
    if args.stdout:
        print()
        print(report)


if __name__ == "__main__":
    main()
