#!/usr/bin/env python3
"""Extract sanitized Git/Gerrit identity for AX Artifact MCP calls."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

REQUIRED_MCP_FIELDS = ("remote_url", "branch", "commit_id")
LOOKUP_REQUIRED_MCP_FIELDS = ("remote_url",)
GERRIT_MAGIC_PREFIXES = {"a", "r"}
GERRIT_DEFAULT_PORT = 29418

_CHANGE_ID_RE = re.compile(r"^Change-Id:\s*I[a-fA-F0-9]+\s*$")
_SCP_LIKE_RE = re.compile(r"^(?:[^@]+@)?([^:]+):(.+)$")


def _base_context(repo_path: Path) -> dict[str, Any]:
    return {
        "status": "error",
        "reason": None,
        "repo_path": str(repo_path.resolve()),
        "repo_root": None,
        "scm": None,
        "remote_name": None,
        "remote_url": None,
        "branch": None,
        "commit_id": None,
        "vcs_host": None,
        "vcs_org": None,
        "vcs_repo": None,
        "repository": None,
        "gerrit_project": None,
        "missing": list(REQUIRED_MCP_FIELDS),
        "lookup_status": "error",
        "lookup_missing": list(LOOKUP_REQUIRED_MCP_FIELDS),
    }


def _run_git(path: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    output = result.stdout.strip()
    return output or None


def redact_remote_url(remote_url: str | None) -> str | None:
    """Remove URL credentials so they never reach prompts or telemetry."""
    if not remote_url:
        return None
    value = remote_url.strip()
    parsed = urlsplit(value)
    if not parsed.scheme or not parsed.hostname:
        scp_like = _SCP_LIKE_RE.match(value)
        if scp_like:
            path = scp_like.group(2).split("?", 1)[0].split("#", 1)[0]
            return f"{scp_like.group(1)}:{path}"
        return value

    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    # Query strings and fragments may also carry access tokens.
    return urlunsplit((parsed.scheme, host, parsed.path, "", ""))


def _split_remote_url(remote_url: str | None) -> tuple[str | None, list[str], int | None]:
    if not remote_url:
        return None, [], None

    value = remote_url.strip()
    parsed = urlsplit(value)
    if parsed.scheme and parsed.hostname:
        parts = [part for part in parsed.path.removesuffix(".git").split("/") if part]
        return parsed.hostname, parts, parsed.port

    scp_like = _SCP_LIKE_RE.match(value.removesuffix(".git"))
    if scp_like:
        parts = [part for part in scp_like.group(2).split("/") if part]
        return scp_like.group(1), parts, None

    parts = [part for part in value.removesuffix(".git").split("/") if part]
    return None, parts, None


def _remote_names(repo_root: Path) -> list[str]:
    output = _run_git(repo_root, "remote")
    return output.splitlines() if output else []


def _select_remote(repo_root: Path, branch: str | None) -> str | None:
    remotes = _remote_names(repo_root)
    if not remotes:
        return None

    if branch:
        branch_remote = _run_git(repo_root, "config", "--get", f"branch.{branch}.remote")
        if branch_remote and branch_remote != "." and branch_remote in remotes:
            return branch_remote

    push_default = _run_git(repo_root, "config", "--get", "remote.pushDefault")
    if push_default in remotes:
        return push_default
    if "origin" in remotes:
        return "origin"
    if len(remotes) == 1:
        return remotes[0]
    return None


def _has_change_id(repo_root: Path) -> bool:
    message = _run_git(repo_root, "log", "-1", "--pretty=%B")
    if not message:
        return False
    return any(_CHANGE_ID_RE.match(line.strip()) for line in message.splitlines())


def extract_git_context(repo_path: Path) -> dict[str, Any]:
    """Return a stable JSON-compatible context for AX Artifact operations."""
    requested_path = repo_path.expanduser().resolve()
    context = _base_context(requested_path)

    if not requested_path.exists():
        context["reason"] = "path_not_found"
        return context
    if shutil.which("git") is None:
        context["reason"] = "git_not_available"
        return context

    candidate = requested_path.parent if requested_path.is_file() else requested_path
    repo_root_text = _run_git(candidate, "rev-parse", "--show-toplevel")
    if not repo_root_text:
        context["status"] = "not_git"
        context["reason"] = "no_git_repository"
        return context

    repo_root = Path(repo_root_text).resolve()
    branch = _run_git(repo_root, "branch", "--show-current")
    review_branch = _run_git(repo_root, "config", "--get", "review.branch")
    if not branch:
        branch = review_branch
    if not branch:
        symbolic_branch = _run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
        branch = None if symbolic_branch == "HEAD" else symbolic_branch

    remote_name = _select_remote(repo_root, branch)
    remote_url = redact_remote_url(
        _run_git(repo_root, "remote", "get-url", remote_name) if remote_name else None
    )
    commit_id = _run_git(repo_root, "rev-parse", "HEAD")
    host, remote_parts, port = _split_remote_url(remote_url)

    review_url = redact_remote_url(_run_git(repo_root, "config", "--get", "review.url"))
    review_project = _run_git(repo_root, "config", "--get", "review.project")
    push_url = redact_remote_url(
        _run_git(repo_root, "config", "--get", f"remote.{remote_name}.pushurl")
        if remote_name
        else None
    )
    gerrit_hint = review_url or push_url or remote_url
    gerrit_host, gerrit_parts, gerrit_port = _split_remote_url(gerrit_hint)
    is_gerrit = bool(
        review_url
        or review_project
        or review_branch
        or _has_change_id(repo_root)
        or (gerrit_host and "gerrit" in gerrit_host.lower())
        or gerrit_port == GERRIT_DEFAULT_PORT
        or (gerrit_hint and "/a/" in gerrit_hint)
    )

    identity_parts = list(remote_parts)
    if is_gerrit and identity_parts and identity_parts[0].lower() in GERRIT_MAGIC_PREFIXES:
        identity_parts = identity_parts[1:]
    vcs_repo = identity_parts[-1] if identity_parts else None
    vcs_org = "/".join(identity_parts[:-1]) or None
    repository = "/".join(part for part in (host, vcs_org, vcs_repo) if part) or None

    gerrit_project = review_project
    if is_gerrit and not gerrit_project:
        project_parts = list(gerrit_parts)
        if project_parts and project_parts[0].lower() in GERRIT_MAGIC_PREFIXES:
            project_parts = project_parts[1:]
        gerrit_project = "/".join(project_parts) or None

    context.update(
        {
            "repo_root": str(repo_root),
            "scm": "gerrit" if is_gerrit else "git",
            "remote_name": remote_name,
            "remote_url": remote_url,
            "branch": branch,
            "commit_id": commit_id,
            "vcs_host": host,
            "vcs_org": vcs_org,
            "vcs_repo": vcs_repo,
            "repository": repository,
            "gerrit_project": gerrit_project,
        }
    )
    lookup_missing = [
        field for field in LOOKUP_REQUIRED_MCP_FIELDS if not context[field]
    ]
    context["lookup_missing"] = lookup_missing
    context["lookup_status"] = "ok" if not lookup_missing else "incomplete"

    missing = [field for field in REQUIRED_MCP_FIELDS if not context[field]]
    context["missing"] = missing
    if missing:
        context["status"] = "incomplete"
        context["reason"] = "missing_required_fields"
    else:
        context["status"] = "ok"
        context["reason"] = None
    return context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract sanitized Git/Gerrit metadata for AX Artifact MCP calls."
    )
    parser.add_argument("--repo", required=True, type=Path, help="Project or repository path")
    parser.add_argument("--format", choices=("json",), default="json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    context = extract_git_context(args.repo)
    print(json.dumps(context, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if context["status"] == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
