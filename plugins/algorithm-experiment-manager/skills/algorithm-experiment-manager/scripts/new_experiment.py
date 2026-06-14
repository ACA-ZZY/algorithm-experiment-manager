#!/usr/bin/env python3
"""Create a new reproducible algorithm experiment record."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_date(value: str | None) -> str:
    if not value:
        return dt.date.today().strftime("%Y%m%d")
    cleaned = re.sub(r"[^0-9]", "", value)
    if len(cleaned) != 8:
        raise SystemExit("date must be in YYYYMMDD or YYYY-MM-DD format")
    try:
        dt.datetime.strptime(cleaned, "%Y%m%d")
    except ValueError as exc:
        raise SystemExit(f"invalid date: {value}") from exc
    return cleaned


def display_date(yyyymmdd: str) -> str:
    return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


def normalize_token(value: str, fallback: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", value or "")
    if not parts:
        return fallback
    return "".join(part[:1].upper() + part[1:] for part in parts)


def next_experiment_id(experiments_dir: Path, date: str, project: str, topic: str) -> str:
    prefix = f"EXP_{date}_{project}_{topic}_"
    max_seen = 0
    for path in experiments_dir.glob(f"{prefix}[0-9][0-9].md"):
        match = re.search(r"_(\d{2})\.md$", path.name)
        if match:
            max_seen = max(max_seen, int(match.group(1)))
    return f"{prefix}{max_seen + 1:02d}"


def replace_field(text: str, label: str, value: str) -> str:
    pattern = re.compile(rf"^{re.escape(label)}[：:].*$", re.MULTILINE)
    replacement = f"{label}：{value}"
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return f"{replacement}\n\n{text}"


def create_record(template: str, args: argparse.Namespace, experiment_id: str, date: str) -> str:
    text = template
    replacements = {
        "实验编号": experiment_id,
        "实验状态": args.status,
        "实验主题": args.topic,
        "实验日期": display_date(date),
        "实验负责人": args.owner,
        "实验类型": args.experiment_type,
    }
    for label, value in replacements.items():
        text = replace_field(text, label, value or "待补充")
    return text.rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new algorithm experiment record.")
    parser.add_argument("--project", required=True, help="Project name or algorithm direction, e.g. GenericML")
    parser.add_argument("--topic", required=True, help="Short English experiment topic, e.g. LearningRateTest")
    parser.add_argument("--date", help="Experiment date in YYYYMMDD or YYYY-MM-DD; default is today")
    parser.add_argument("--type", dest="experiment_type", default="待补充", help="Experiment type")
    parser.add_argument("--owner", default="待补充", help="Experiment owner")
    parser.add_argument("--status", default="计划中", help="Initial experiment status")
    parser.add_argument(
        "--output-dir",
        default=str(skill_root() / "experiments"),
        help="Directory for experiment records; default: <skill>/experiments",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    date = normalize_date(args.date)
    project = normalize_token(args.project, "Project")
    topic = normalize_token(args.topic, "Experiment")

    experiments_dir = Path(args.output_dir).expanduser().resolve()
    experiments_dir.mkdir(parents=True, exist_ok=True)

    experiment_id = next_experiment_id(experiments_dir, date, project, topic)
    output_path = experiments_dir / f"{experiment_id}.md"

    template_path = skill_root() / "templates" / "experiment_record.md"
    if not template_path.exists():
        raise SystemExit(f"template not found: {template_path}")

    record = create_record(template_path.read_text(encoding="utf-8"), args, experiment_id, date)
    output_path.write_text(record, encoding="utf-8")

    print(f"Created experiment record: {output_path}")
    print(f"Experiment ID: {experiment_id}")


if __name__ == "__main__":
    main()
