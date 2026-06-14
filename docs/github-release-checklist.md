# GitHub Marketplace Release Checklist

## Before Push

- [ ] Run `python3 scripts/validate_marketplace.py`.
- [ ] Confirm `.claude-plugin/marketplace.json` has marketplace name `aca-zzy`.
- [ ] Confirm `.agents/plugins/marketplace.json` matches `.claude-plugin/marketplace.json` for compatibility.
- [ ] Confirm `plugins/algorithm-experiment-manager/.codex-plugin/plugin.json` has version `0.1.0`.
- [ ] Confirm repository URLs point to `https://github.com/ACA-ZZY/algorithm-experiment-manager`.
- [ ] Confirm the GitHub workflow exists at `.github/workflows/validate.yml`.

## Upload Or Push

If this folder is already connected to GitHub:

```bash
git add -A
git commit -m "Convert to Codex plugin marketplace"
git push
```

If you upload through the GitHub web interface, upload the whole repository root, including hidden folders:

```text
.agents/
.claude-plugin/
.github/
plugins/
scripts/
```

## Install Test

After the repository is on GitHub, test installation locally:

```bash
git clone https://github.com/ACA-ZZY/algorithm-experiment-manager.git
cd algorithm-experiment-manager
codex plugin marketplace add "$(pwd)"
codex plugin add algorithm-experiment-manager@aca-zzy
```

Start a new Codex thread and ask:

```text
使用 algorithm-experiment-manager，帮我设计一个算法实验。
```

## Tag A Release

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main --tags
```
