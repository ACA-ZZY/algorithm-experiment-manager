#!/usr/bin/env python3
"""Validate the Codex plugin marketplace repository layout."""

from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
LEGACY_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_ROOT = ROOT / "plugins" / "algorithm-experiment-manager"
PLUGIN_JSON = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "algorithm-experiment-manager"


REQUIRED_SKILL_FILES = [
    "SKILL.md",
    "README.md",
    "templates/experiment_plan.md",
    "templates/experiment_record.md",
    "templates/incremental_log.md",
    "templates/comparison_table.md",
    "templates/failure_record.md",
    "templates/project_index.md",
    "templates/metric_registry.md",
    "templates/reproducibility_checklist.md",
    "templates/paper_evidence_notes.md",
    "examples/generic_algorithm_experiment.md",
    "scripts/new_experiment.py",
    "scripts/append_log.py",
    "scripts/summarize_experiments.py",
]


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def read_json(path: Path) -> dict:
    if not path.exists():
        fail(f"missing JSON file: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")


def check_marketplace() -> None:
    data = read_json(MARKETPLACE)
    if data.get("name") != "aca-zzy":
        fail("marketplace name must be aca-zzy")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        fail("marketplace plugins must be a non-empty list")
    entry = next((item for item in plugins if item.get("name") == "algorithm-experiment-manager"), None)
    if not entry:
        fail("marketplace must include algorithm-experiment-manager")
    if entry.get("source", {}).get("source") != "local":
        fail("marketplace source.source must be local")
    if entry.get("source", {}).get("path") != "./plugins/algorithm-experiment-manager":
        fail("marketplace source.path must be ./plugins/algorithm-experiment-manager")
    policy = entry.get("policy", {})
    if policy.get("installation") != "AVAILABLE":
        fail("marketplace policy.installation must be AVAILABLE")
    if policy.get("authentication") != "ON_INSTALL":
        fail("marketplace policy.authentication must be ON_INSTALL")
    if entry.get("category") != "Productivity":
        fail("marketplace category must be Productivity")
    if LEGACY_MARKETPLACE.exists():
        legacy = read_json(LEGACY_MARKETPLACE)
        if legacy != data:
            fail(".agents/plugins/marketplace.json must match .claude-plugin/marketplace.json when both exist")


def check_plugin_manifest() -> None:
    data = read_json(PLUGIN_JSON)
    expected = {
        "name": "algorithm-experiment-manager",
        "version": "0.1.0",
        "skills": "./skills/",
        "license": "MIT",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            fail(f"plugin.json {key} must be {value}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", data.get("version", "")):
        fail("plugin.json version must be strict semver")
    if data.get("repository") != "https://github.com/ACA-ZZY/algorithm-experiment-manager":
        fail("plugin.json repository must point to ACA-ZZY/algorithm-experiment-manager")
    interface = data.get("interface", {})
    for key in ["displayName", "shortDescription", "longDescription", "developerName", "category", "capabilities"]:
        if key not in interface:
            fail(f"plugin.json interface.{key} is required")


def parse_skill_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        fail("SKILL.md must start with YAML front matter")
    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip('"')
    return frontmatter


def check_skill() -> None:
    for rel_path in REQUIRED_SKILL_FILES:
        if not (SKILL_ROOT / rel_path).exists():
            fail(f"missing skill file: {SKILL_ROOT.relative_to(ROOT) / rel_path}")
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = parse_skill_frontmatter(text)
    if frontmatter.get("name") != "algorithm-experiment-manager":
        fail("SKILL.md name must be algorithm-experiment-manager")
    description = frontmatter.get("description", "")
    if not description.startswith("Use when"):
        fail("SKILL.md description must start with 'Use when'")


def check_python_scripts() -> None:
    for path in sorted((SKILL_ROOT / "scripts").glob("*.py")):
        py_compile.compile(str(path), doraise=True)


def run(command: list[str], cwd: Path = ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def smoke_test_skill_scripts() -> None:
    with tempfile.TemporaryDirectory(prefix="algorithm-exp-marketplace-") as tmp:
        tmp_path = Path(tmp)
        experiments_dir = tmp_path / "experiments"
        index_path = tmp_path / "project_index.md"
        run(
            [
                sys.executable,
                "scripts/new_experiment.py",
                "--project",
                "GenericML",
                "--topic",
                "LearningRateTest",
                "--date",
                "20260614",
                "--output-dir",
                str(experiments_dir),
            ],
            cwd=SKILL_ROOT,
        )
        record = experiments_dir / "EXP_20260614_GenericML_LearningRateTest_01.md"
        if not record.exists():
            fail("new_experiment.py did not create the expected record")
        run(
            [
                sys.executable,
                "scripts/append_log.py",
                "--experiment",
                "EXP_20260614_GenericML_LearningRateTest_01",
                "--type",
                "参数修改",
                "--content",
                "learning rate 从 1e-3 调整为 5e-4",
                "--result",
                "validation loss 更稳定",
                "--next",
                "继续单因素验证",
                "--experiments-dir",
                str(experiments_dir),
            ],
            cwd=SKILL_ROOT,
        )
        if "增量记录编号" not in record.read_text(encoding="utf-8"):
            fail("append_log.py did not append a log entry")
        run(
            [
                sys.executable,
                "scripts/summarize_experiments.py",
                "--experiments-dir",
                str(experiments_dir),
                "--output",
                str(index_path),
            ],
            cwd=SKILL_ROOT,
        )
        if "EXP_20260614_GenericML_LearningRateTest_01" not in index_path.read_text(encoding="utf-8"):
            fail("summarize_experiments.py did not include the test experiment")


def main() -> None:
    check_marketplace()
    check_plugin_manifest()
    check_skill()
    check_python_scripts()
    smoke_test_skill_scripts()
    print("[OK] marketplace validation passed")


if __name__ == "__main__":
    main()
