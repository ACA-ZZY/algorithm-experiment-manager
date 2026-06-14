# Algorithm Experiment Manager Marketplace

This repository is a Codex plugin marketplace for **Algorithm Experiment Manager**, a general research algorithm experiment management skill.

It helps Codex plan, record, compare, review, archive, and track reproducible algorithm experiments across machine learning, deep learning, finite element methods, optimization, reliability analysis, inverse problems, numerical simulation, ablation studies, parameter sensitivity analysis, and engineering simulations.

## Install In Codex

Clone this repository:

```bash
git clone https://github.com/ACA-ZZY/algorithm-experiment-manager.git
cd algorithm-experiment-manager
```

Add this repository as a Codex plugin marketplace:

```bash
codex plugin marketplace add "$(pwd)"
```

Install the plugin:

```bash
codex plugin add algorithm-experiment-manager@aca-zzy
```

Start a new Codex thread after installation so the skill is loaded.

## Use

After installation, ask Codex things like:

```text
使用 algorithm-experiment-manager，帮我设计一个参数敏感性实验。
```

```text
记录这次有限元边界条件实验，并追加增量日志。
```

```text
比较这些实验，检查是否公平可比，并整理成论文证据。
```

## Repository Structure

```text
.
├── .claude-plugin/
│   └── marketplace.json
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── plugins/
│   └── algorithm-experiment-manager/
│       ├── .codex-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── algorithm-experiment-manager/
│               ├── SKILL.md
│               ├── templates/
│               ├── examples/
│               └── scripts/
├── scripts/
│   └── validate_marketplace.py
└── README.md
```

## Validate

Run:

```bash
python3 scripts/validate_marketplace.py
```

The validation checks:

- Marketplace file shape and plugin entry.
- Plugin manifest fields.
- Skill front matter.
- Required templates and scripts.
- Python syntax.
- A smoke test for creating an experiment, appending a log, and generating an index.

## Plugin Metadata

- Marketplace manifest: `.claude-plugin/marketplace.json`
- Marketplace name: `aca-zzy`
- Plugin name: `algorithm-experiment-manager`
- Category: `Productivity`
- License: `MIT`
- Repository: `https://github.com/ACA-ZZY/algorithm-experiment-manager`

## Release

```bash
python3 scripts/validate_marketplace.py
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main --tags
```

## License

MIT License. See [LICENSE](LICENSE).
