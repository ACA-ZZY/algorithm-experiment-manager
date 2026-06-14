#!/usr/bin/env python3
"""Append an incremental log entry to an experiment record."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append an incremental log to an experiment record.")
    parser.add_argument("--experiment", required=True, help="Experiment ID, e.g. EXP_20260614_GenericML_LearningRateTest_01")
    parser.add_argument("--type", required=True, help="Update type, e.g. 参数修改")
    parser.add_argument("--content", required=True, help="Update content")
    parser.add_argument("--result", default="待补充", help="New result or result change")
    parser.add_argument("--next", required=True, help="Next action")
    parser.add_argument("--before", default="待补充", help="Previous state")
    parser.add_argument("--after", default=None, help="New state; defaults to --content")
    parser.add_argument("--params", default="待补充", help="New parameters")
    parser.add_argument("--files", default="待补充", help="New file locations")
    parser.add_argument("--observation", default="待补充", help="Observed phenomena")
    parser.add_argument("--diff", default=None, help="Difference from previous version; defaults to --content")
    parser.add_argument("--judgement", default="待补充", help="Judgement")
    parser.add_argument("--file", help="Explicit experiment record file")
    parser.add_argument(
        "--experiments-dir",
        default=str(skill_root() / "experiments"),
        help="Directory containing experiment records; default: <skill>/experiments",
    )
    return parser.parse_args()


def resolve_record_path(args: argparse.Namespace) -> Path:
    if args.file:
        path = Path(args.file).expanduser().resolve()
    else:
        path = Path(args.experiments_dir).expanduser().resolve() / f"{args.experiment}.md"
    if not path.exists():
        raise SystemExit(f"experiment record not found: {path}")
    return path


def build_entry(args: argparse.Namespace) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_id = "LOG_" + dt.datetime.now().strftime("%Y%m%d%H%M%S")
    after = args.after if args.after is not None else args.content
    diff = args.diff if args.diff is not None else args.content
    return f"""
### {log_id}

更新时间：{now}

增量记录编号：{log_id}

关联实验编号：{args.experiment}

本次更新类型：{args.type}

修改前状态：{args.before}

修改后状态：{after}

新增参数：{args.params}

新增结果：{args.result}

新增文件位置：{args.files}

现象观察：{args.observation}

与上一版本的差异：{diff}

判断：{args.judgement}

下一步动作：{args.next}
""".strip()


def append_log(path: Path, entry: str) -> None:
    text = path.read_text(encoding="utf-8")
    marker = "## 增量日志"
    if marker not in text:
        text = text.rstrip() + f"\n\n{marker}\n\n{entry}\n"
    elif f"{marker}\n\n暂无" in text:
        text = text.replace(f"{marker}\n\n暂无", f"{marker}\n\n{entry}", 1)
        text = text.rstrip() + "\n"
    else:
        text = text.rstrip() + f"\n\n{entry}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    path = resolve_record_path(args)
    entry = build_entry(args)
    append_log(path, entry)
    print(f"Appended log to: {path}")


if __name__ == "__main__":
    main()
