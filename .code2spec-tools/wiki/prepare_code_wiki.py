#!/usr/bin/env python3
"""Write ``repo.json`` — the dashboard context and deep-link configuration.

Normalises the git remote into a host-specific deep-link base (the URL prefix that
backtick deep-links are built from) and merges the result into the SDD root's
``repo.json``. Dashboard fields written later by ``write_wiki_metadata.py`` and by
the validation pipeline (description / languages / qualityScore) are preserved on
re-run.

No page skeleton is created: the single output tree is code2spec's existing SDD at
``<repo>/code2spec/``, and ``topLevelEntries`` simply lists its chapters.

Usage:
  python3 prepare_code_wiki.py [--repo-root <repo>] [--out <outDir>]
    [--remote-url <url>] [--branch <name>] [--out-root <serverRoot>]
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_WIKI_DIR = Path(__file__).resolve().parent
if str(_WIKI_DIR) not in sys.path:
    sys.path.insert(0, str(_WIKI_DIR))

from page_model import TOP_LEVEL_ENTRIES  # noqa: E402

# Dashboard fields owned by later stages; carried over when repo.json already exists.
PRESERVED_FIELDS = ("description", "languages", "qualityScore", "qualityBreakdown")


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """Parse ``--key value`` / ``--flag`` pairs; a flag without a value becomes True.

    Tokens that do not start with ``--`` are ignored (this CLI has no positionals)
    and a repeated flag keeps its last value.
    """
    args: dict[str, str | bool] = {}
    i = 0
    while i < len(argv):
        key = argv[i]
        if key.startswith("--"):
            nxt = argv[i + 1] if i + 1 < len(argv) else None
            if not nxt or nxt.startswith("--"):
                args[key[2:]] = True
            else:
                args[key[2:]] = nxt
                i += 1
        i += 1
    return args


def opt(args: dict[str, str | bool], key: str) -> str | None:
    """Value of ``--key`` when it was given with a non-empty string."""
    value = args.get(key)
    return value if isinstance(value, str) and value else None


def write_json(path: str, obj: object) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def run_git(repo_root: str, args: list[str], fallback: str = "") -> str:
    """Run git and return its trimmed stdout, or ``fallback`` when it fails.

    stderr is inherited on purpose so git's own diagnostics (``fatal: ref
    refs/remotes/origin/HEAD is not a symbolic ref`` and friends) still reach the user.
    """
    try:
        proc = subprocess.run(
            ["git", *args], cwd=repo_root,
            stdout=subprocess.PIPE, encoding="utf-8", errors="replace",
        )
    except OSError:
        return fallback
    if proc.returncode != 0:
        return fallback
    return proc.stdout.strip()


def resolve_remote_url(repo_root: str, args: dict[str, str | bool]) -> str:
    """Pick the remote URL that deep-links should be built from.

    A working copy often lacks the real ``origin`` (e.g. a GitHub "Download ZIP"
    extract that was later ``git init``ed), which would degrade every link to
    ``https://local/local/<dirname>/...``. Priority:
    ``--remote-url`` > ``origin`` > first configured remote > ``$CODE2SPEC_WIKI_REMOTE``.
    """
    explicit = opt(args, "remote-url")
    if explicit:
        return explicit
    remotes = [r for r in re.split(r"\r?\n", run_git(repo_root, ["remote"])) if r]
    ordered = (["origin"] + [r for r in remotes if r != "origin"]) \
        if "origin" in remotes else remotes
    for name in ordered:
        url = run_git(repo_root, ["remote", "get-url", name])
        if url:
            return url
    return os.environ.get("CODE2SPEC_WIKI_REMOTE") or ""


def normalize_remote(remote_url: str, repo_root: str) -> dict[str, str]:
    """Split any remote URL form (scp, ssh, git, https) into host/owner/repo."""
    if not remote_url:
        return {
            "host": "local",
            "ownerPath": "local",
            "ownerSlug": "local",
            "repo": os.path.basename(repo_root),
        }
    value = remote_url
    value = re.sub(r"^git@([^:]+):", r"https://\1/", value)
    value = re.sub(r"^ssh://(?:[^@]+@)?([^/:]+)(?::[0-9]+)?/", r"https://\1/", value)
    value = re.sub(r"^git://([^/]+)/", r"https://\1/", value)
    value = re.sub(r"\.git$", "", value)
    value = re.sub(r"^https?://", "", value)
    parts = [p for p in value.split("/") if p]
    host = parts.pop(0) if parts else "local"
    repo = parts.pop() if parts else os.path.basename(repo_root)
    owner_path = "/".join(parts) or "local"
    return {
        "host": host,
        "ownerPath": owner_path,
        "ownerSlug": owner_path.replace("/", "-"),
        "repo": repo,
    }


def deep_link_for(host: str, owner_path: str, repo: str, branch: str) -> dict[str, str]:
    """Deep-link config for a hosting provider. The branch is baked into ``base``,
    so branch names containing ``/`` stay intact."""
    if host == "git.tizen.org":
        return {
            "type": "cgit",
            "base": f"https://{host}/cgit/{owner_path}/{repo}/tree",
            "suffix": f"?h={branch}",
            "lineAnchorPrefix": "#n",
        }
    if host == "github.com" or host.startswith("github."):
        return {
            "type": "github",
            "base": f"https://{host}/{owner_path}/{repo}/blob/{branch}",
            "suffix": "",
            "lineAnchorPrefix": "#L",
        }
    if host == "gitlab.com" or host.startswith("gitlab."):
        return {
            "type": "gitlab",
            "base": f"https://{host}/{owner_path}/{repo}/-/blob/{branch}",
            "suffix": "",
            "lineAnchorPrefix": "#L",
        }
    # Cloud 전용. self-hosted Server/DC는 경로 체계가 달라(/projects/<KEY>/repos/…/browse/…)
    # 여기서 매칭하면 안 된다 — github-fallback + unknown host 경고로 흘려보낸다.
    if host == "bitbucket.org":
        return {
            "type": "bitbucket",
            "base": f"https://{host}/{owner_path}/{repo}/src/{branch}",
            "suffix": "",
            "lineAnchorPrefix": "#lines-",
        }
    # 아래 `/gerrit/gitweb` 접두사는 review.tizen.org 배포에 종속된 값이다. Gerrit은 인스턴스마다
    # gitweb/gitiles 마운트 지점이 달라(`/gitweb`·`/plugins/gitiles`) 호스트명으로 일반화할 수 없고,
    # `review.` 접두사는 아예 GitLab 인스턴스를 오판할 수 있다. 검증된 호스트만 매칭한다.
    if host == "review.tizen.org":
        return {
            "type": "gerrit-gitweb",
            "base": f"https://{host}/gerrit/gitweb?p={owner_path}/{repo}.git;a=blob;f=",
            "suffix": f";hb=refs/heads/{branch}",
            "lineAnchorPrefix": "#l",
        }
    return {
        "type": "github-fallback",
        "base": f"https://{host}/{owner_path}/{repo}/blob/{branch}",
        "suffix": "",
        "lineAnchorPrefix": "#L",
    }


def resolve_branch(repo_root: str, args: dict[str, str | bool]) -> str:
    """``--branch`` > current branch > origin/HEAD > ``main``."""
    explicit = opt(args, "branch")
    if explicit:
        return explicit
    current = run_git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"], "HEAD")
    if current and current != "HEAD":
        return current
    origin_head = re.sub(
        r"^refs/remotes/origin/", "",
        run_git(repo_root, ["symbolic-ref", "refs/remotes/origin/HEAD"]))
    return origin_head or "main"


def resolve_out_dir(repo_root: str, args: dict[str, str | bool],
                    meta: dict[str, str]) -> str:
    """``--out`` > ``<out-root>/<host>/<ownerSlug>/<repo>`` > ``<repo>/code2spec``."""
    out = opt(args, "out")
    if out:
        return os.path.abspath(out)
    out_root = opt(args, "out-root")
    if out_root:
        return os.path.abspath(os.path.join(
            os.path.abspath(out_root), meta["host"],
            meta["ownerSlug"] or meta["ownerPath"], meta["repo"]))
    return os.path.abspath(os.path.join(repo_root, "code2spec"))


def main() -> int:
    args = parse_args(sys.argv[1:])
    repo_root = os.path.abspath(
        opt(args, "repo-root")
        or run_git(os.getcwd(), ["rev-parse", "--show-toplevel"], os.getcwd()))
    remote_url = resolve_remote_url(repo_root, args)
    meta = normalize_remote(remote_url, repo_root)
    branch = resolve_branch(repo_root, args)
    out_dir = resolve_out_dir(repo_root, args, meta)
    os.makedirs(out_dir, exist_ok=True)

    context: dict[str, Any] = {
        "repoRoot": repo_root,
        "outDir": out_dir,
        "host": meta["host"],
        "ownerPath": meta["ownerPath"],
        "ownerSlug": meta["ownerSlug"],
        "repo": meta["repo"],
        "branch": branch,
        "defaultBranch": branch,
        "remoteUrl": remote_url,
        "deepLink": deep_link_for(meta["host"], meta["ownerPath"], meta["repo"], branch),
        "topLevelEntries": TOP_LEVEL_ENTRIES,
        "generatedAt": datetime.now(UTC)
                       .isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    }

    repo_json_path = os.path.join(out_dir, "repo.json")
    existing: dict[str, Any] = {}
    if os.path.exists(repo_json_path):
        try:
            with open(repo_json_path, encoding="utf-8", errors="replace") as f:
                loaded = json.loads(f.read())
            existing = loaded if isinstance(loaded, dict) else {}
        except (OSError, ValueError):
            pass          # a corrupt repo.json is rebuilt from scratch
    preserved = {k: existing[k] for k in PRESERVED_FIELDS if k in existing}
    write_json(repo_json_path, {**context, **preserved})

    print(json.dumps(context, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
