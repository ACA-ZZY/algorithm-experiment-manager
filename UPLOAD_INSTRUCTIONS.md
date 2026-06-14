# Upload Instructions

This folder is the Codex plugin marketplace version of Algorithm Experiment Manager.

Important: upload hidden folders too:

```text
.claude-plugin/
.agents/
.github/
plugins/algorithm-experiment-manager/.codex-plugin/
```

If these hidden folders are missing on GitHub, Codex will show:

```text
marketplace root does not contain a supported manifest
```

## Recommended Upload With Git

```bash
cd ~/Desktop/algorithm-experiment-manager-upload
git init
git add -A
git commit -m "Add Codex plugin marketplace"
git branch -M main
git remote add origin https://github.com/ACA-ZZY/algorithm-experiment-manager.git
git push -u origin main --force
```

GitHub no longer accepts account passwords for `git push`. If prompted for password, paste a GitHub Personal Access Token with repository write permission.

## Recommended Upload With GitHub Desktop

1. Open GitHub Desktop.
2. Add local repository: `~/Desktop/algorithm-experiment-manager-upload`.
3. Confirm the changed files include `.claude-plugin/`, `.agents/`, `.github/`, and `.codex-plugin/`.
4. Commit and push to `ACA-ZZY/algorithm-experiment-manager`.

## Test In Codex After Upload

In Add plugin marketplace:

```text
Source: https://github.com/ACA-ZZY/algorithm-experiment-manager.git
Git ref: main
Sparse paths: leave empty
```

Then install:

```bash
codex plugin add algorithm-experiment-manager@aca-zzy
```
