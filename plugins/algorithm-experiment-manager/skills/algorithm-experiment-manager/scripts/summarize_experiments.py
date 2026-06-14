#!/usr/bin/env python3
"""Summarize experiment records into a project index table."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


MISSING = "待补充"


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate project_index.md from experiment records.")
    parser.add_argument(
        "--experiments-dir",
        default=str(skill_root() / "experiments"),
        help="Directory containing experiment records; default: <skill>/experiments",
    )
    parser.add_argument(
        "--output",
        default=str(skill_root() / "project_index.md"),
        help="Output markdown file; default: <skill>/project_index.md",
    )
    return parser.parse_args()


def field_value(text: str, label: str) -> str:
    pattern = re.compile(rf"^{re.escape(label)}[：:]\s*(.*)$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return MISSING
    value = match.group(1).strip()
    return value or MISSING


def section_value(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=\n##\s+|\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return MISSING
    lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    if not lines or lines[0] == "暂无":
        return MISSING
    return shorten(" ".join(lines))


def shorten(value: str, limit: int = 120) -> str:
    value = " ".join(value.split())
    if not value:
        return MISSING
    if len(value) <= limit:
        return value
    return value[: limit - 1] + "…"


def escape_cell(value: str) -> str:
    return (value or MISSING).replace("|", "\\|").replace("\n", " ")


def summarize_file(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    return {
        "实验编号": field_value(text, "实验编号"),
        "实验主题": field_value(text, "实验主题"),
        "状态": field_value(text, "实验状态"),
        "核心修改": section_value(text, "变化变量"),
        "主要结果": section_value(text, "核心结果"),
        "是否保留": section_value(text, "是否保留该实验"),
        "备注": section_value(text, "初步结论"),
    }


def build_index(rows: list[dict[str, str]]) -> str:
    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 项目实验索引",
        "",
        f"生成时间：{generated}",
        "",
        "| 实验编号 | 实验主题 | 状态 | 核心修改 | 主要结果 | 是否保留 | 备注 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not rows:
        lines.append(f"| {MISSING} | {MISSING} | {MISSING} | {MISSING} | {MISSING} | {MISSING} | {MISSING} |")
    else:
        for row in rows:
            lines.append(
                "| "
                + " | ".join(
                    escape_cell(row[key])
                    for key in ["实验编号", "实验主题", "状态", "核心修改", "主要结果", "是否保留", "备注"]
                )
                + " |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    experiments_dir = Path(args.experiments_dir).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    rows: list[dict[str, str]] = []
    if experiments_dir.exists():
        for path in sorted(experiments_dir.glob("EXP_*.md")):
            if path.is_file():
                rows.append(summarize_file(path))

    output_path.write_text(build_index(rows), encoding="utf-8")
    print(f"Wrote project index: {output_path}")
    print(f"Experiments summarized: {len(rows)}")


if __name__ == "__main__":
    main()
