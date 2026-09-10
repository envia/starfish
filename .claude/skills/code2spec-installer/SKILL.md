---
name: code2spec-installer
metadata:
  code-skills:
    id: code2spec/code2spec-installer
description: Install or upgrade code2spec in a Cline project using the latest GitHub Enterprise Release asset. Use when a user asks to set up, bootstrap, or update code2spec for Cline.
---

# Code2spec Installer

Install from the latest published `install.py` asset. Do not clone a local checkout and do not use an unverified URL or branch.

## Install

1. Resolve the target project's build-unit root. In a monorepo, choose the individual package or service root.
2. Confirm that the GitHub CLI is authenticated for `github.sec.samsung.net` and that `python` and `git` are available.
3. Download the latest Release's `install.py` to a temporary directory and run it for Cline. Do not add `--yes` unless replacement of existing code2spec files is authorized.

```bash
PROJECT="<target-project>"
REPO="github.sec.samsung.net/CODEGrok/code2spec"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

TAG="$(gh release view --repo "$REPO" --json tagName --jq .tagName)"
gh release download "$TAG" --repo "$REPO" \
  --pattern install.py --output "$TMP_DIR/install.py"
python "$TMP_DIR/install.py" --project "$PROJECT" --cline
```

## Verify

Verify these files exist in the target project:

- `.cline/skills/code2spec-discovery/SKILL.md`
- `.clinerules/workflows/code2spec-discovery.md`
- `.code2spec-venv/`
- `.code2spec-tools/build-info.json`

Read `build-info.json` and report its `version`, `source`, and `tag` values. Stop with the GitHub authentication error if release download fails; do not fall back to a different artifact.
