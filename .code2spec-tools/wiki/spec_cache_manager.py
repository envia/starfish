#!/usr/bin/env python3
"""Track the content hash each source file had when it was last documented.

Two caches describe a repository's state:

* parse-cache — the *current* state of the sources (written by ``cli.py export``)
* spec-cache  — the state as of the last documentation run (written here, at finalize)

``compute_diff_plan.py`` compares the two to decide which files need regenerating.
The canonical location is ``.analysis/state/delta/spec-cache.json``; the launcher
passes that directory explicitly via ``--analysis-dir``.

Usage:
  python3 spec_cache_manager.py --action mark     --root <repo> --analysis-dir <dir> --files <a,b,...>
  python3 spec_cache_manager.py --action mark-all --root <repo> --analysis-dir <dir>
  python3 spec_cache_manager.py --action status   --root <repo> --analysis-dir <dir>
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from typing import Any

CACHE_VERSION = "1.0"


def _iso_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def git_files(root: str) -> list[str]:
    """Tracked files (repo-relative) under ``root``; empty when this is not a repo.

    stderr is inherited so git's own message (``fatal: not a git repository``) is
    what the user sees.
    """
    try:
        proc = subprocess.run(["git", "ls-files"], cwd=root,
                              stdout=subprocess.PIPE, encoding="utf-8", errors="replace")
    except OSError:
        return []
    if proc.returncode != 0:
        return []
    return [line for line in re.split(r"\r?\n", proc.stdout) if line]


class SpecCacheManager:
    """Read/modify/write one ``spec-cache.json``."""

    def __init__(self, cache_file_path: str) -> None:
        self.cache_file_path = cache_file_path
        self.cache: dict[str, Any] = self._load()

    @staticmethod
    def _normalise(cache: dict[str, Any]) -> dict[str, Any]:
        """Guarantee the keys the rest of this class indexes into.

        A file is accepted on its ``version`` alone, but ``version`` is not unique to
        this schema: the delta pipeline writes its own ``spec-cache.json`` carrying the
        same ``"1.0"`` with ``mode``/``analysis_scope`` and no ``metadata`` block. Both
        ``save()`` and ``stats()`` then died on ``cache["metadata"]``, taking finalize
        down with them. Establishing the shape once here beats defending each use — and
        bumping ``CACHE_VERSION`` to reject the foreign file would silently discard the
        delta baseline it holds.
        """
        cache.setdefault("version", CACHE_VERSION)
        entries = cache.get("entries")
        cache["entries"] = entries if isinstance(entries, dict) else {}
        metadata = cache.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        metadata.setdefault("created_at", _iso_now())
        metadata.setdefault("last_updated", None)
        cache["metadata"] = metadata
        return cache

    def _load(self) -> dict[str, Any]:
        """Load the cache, or start a fresh one when it is absent, unreadable or
        written by a different schema version."""
        try:
            if os.path.exists(self.cache_file_path):
                with open(self.cache_file_path, encoding="utf-8", errors="replace") as f:
                    parsed = json.load(f)
                if isinstance(parsed, dict) and parsed.get("version") == CACHE_VERSION:
                    return self._normalise(parsed)
        except (OSError, ValueError):
            pass
        return self._normalise({})

    def save(self) -> None:
        """Write atomically so a crash cannot leave a half-written cache behind."""
        tmp = f"{self.cache_file_path}.tmp"
        self.cache["metadata"]["last_updated"] = _iso_now()
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(self.cache, indent=2, ensure_ascii=False) + "\n")
        os.replace(tmp, self.cache_file_path)

    def _hash(self, file_path: str) -> str | None:
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except OSError:
            return None

    def mark_documented(self, abs_file_path: str, rel_file_path: str) -> bool:
        """Record a file's current content hash. False when it cannot be read."""
        file_hash = self._hash(abs_file_path)
        if not file_hash:
            return False
        self.cache["entries"][rel_file_path] = {
            "file_hash": file_hash,
            "documented_at": _iso_now(),
        }
        return True

    def mark_all(self, root: str, rel_file_paths: list[str]) -> int:
        """Mark many files; returns how many were hashed successfully."""
        count = 0
        for rel in rel_file_paths:
            if self.mark_documented(os.path.join(root, rel), rel):
                count += 1
        return count

    def get_entry(self, rel_file_path: str) -> dict[str, Any] | None:
        return self.cache["entries"].get(rel_file_path)

    def all(self) -> dict[str, Any]:
        """All tracked entries."""
        return self.cache["entries"]

    def is_documentation_current(self, abs_file_path: str, rel_file_path: str) -> bool:
        """True when the file's current hash matches the recorded one."""
        entry = self.cache["entries"].get(rel_file_path)
        if not entry:
            return False
        return self._hash(abs_file_path) == entry.get("file_hash")

    def stats(self) -> dict[str, Any]:
        return {
            "total_tracked": len(self.cache["entries"]),
            "last_updated": self.cache["metadata"]["last_updated"],
        }


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """Parse ``--key value`` / ``--flag`` pairs; a flag without a value becomes True."""
    args: dict[str, str | bool] = {}
    i = 0
    while i < len(argv):
        flag = argv[i]
        if not flag.startswith("--"):
            i += 1
            continue
        key = flag[2:]
        nxt = argv[i + 1] if i + 1 < len(argv) else None
        if not nxt or nxt.startswith("--"):
            args[key] = True
        else:
            args[key] = nxt
            i += 1
        i += 1
    return args


def main() -> int:
    args = parse_args(sys.argv[1:])
    root = os.path.abspath(str(args["root"])) if args.get("root") else os.getcwd()
    analysis_dir = os.path.abspath(str(args["analysis-dir"])) \
        if args.get("analysis-dir") else os.path.join(root, ".analysis")
    cache_file = os.path.join(analysis_dir, "spec-cache.json")
    action = args.get("action") or "status"

    os.makedirs(analysis_dir, exist_ok=True)
    mgr = SpecCacheManager(cache_file)

    if action == "mark":
        raw_files = args.get("files")
        files = [s for s in (t.strip() for t in str(raw_files).split(",")) if s] \
            if isinstance(raw_files, str) else []
        if len(files) == 0:
            print("[spec-cache] --files required for mark action", file=sys.stderr)
            return 1
        count = mgr.mark_all(root, files)
        mgr.save()
        print(f"[spec-cache] marked {count} files as documented → {cache_file}",
              file=sys.stderr)
    elif action == "mark-all":
        files = git_files(root)
        if len(files) == 0:
            print(f"[spec-cache] git ls-files returned no files under {root} "
                  f"(not a git repo?)", file=sys.stderr)
            return 1
        count = mgr.mark_all(root, files)
        mgr.save()
        print(f"[spec-cache] marked {count}/{len(files)} git-tracked files as documented "
              f"→ {cache_file}", file=sys.stderr)
    else:
        print(json.dumps(mgr.stats(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
