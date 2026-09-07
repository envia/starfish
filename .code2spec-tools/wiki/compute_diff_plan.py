#!/usr/bin/env python3
"""Classify every source file as added / modified / deleted / unchanged.

Compares the *current* state of the sources against spec-cache (the state as of the
last documentation run) and writes the result as a diff plan.

The current state comes from one of two places:

* ``--from-git`` (preferred) — hash every ``git ls-files`` entry. Covers manifests
  and config files too, so nothing falls outside the AST's scope.
* default — read ``parse-cache.json`` (legacy; limited to what the AST pass saw).

``--out <filename>`` names the output file inside ``--analysis-dir``. The launcher
passes ``wiki-diff-plan.json`` because the base delta pipeline writes its own
``diff-plan.json`` there with a different schema.

Usage:
  python3 compute_diff_plan.py --root <repo> --from-git --analysis-dir <dir> [--out <filename>]
  python3 compute_diff_plan.py --root <repo> [--cache-dir <dir>] [--analysis-dir <dir>]
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


def _iso_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def compute_diff_plan(parse_cache: dict[str, Any], spec_cache: dict[str, Any],
                      root: str) -> dict[str, Any]:
    """Diff the current state against the documented state.

    ``parse_cache.entries`` is keyed by absolute path, ``spec_cache.entries`` by
    repo-relative path; both map to ``{file_hash, ...}``.
    """
    plan: dict[str, Any] = {
        "generated_at": _iso_now(),
        "summary": {"added": 0, "modified": 0, "deleted": 0, "unchanged": 0, "total": 0},
        "added": [],
        "modified": [],
        "deleted": [],
        "unchanged": [],
    }

    parsed_files: dict[str, Any] = {}
    for abs_path, entry in (parse_cache.get("entries") or {}).items():
        rel = os.path.relpath(abs_path, root).replace(os.sep, "/")
        parsed_files[rel] = entry.get("file_hash")

    spec_files = spec_cache.get("entries") or {}

    # First-seen order: current files first, then the ones only spec-cache still knows
    # (i.e. deletions). Keeps the written plan stable across runs.
    all_keys = list(dict.fromkeys([*parsed_files, *spec_files]))

    for rel in all_keys:
        in_parse = rel in parsed_files
        in_spec = rel in spec_files

        if in_parse and not in_spec:
            plan["added"].append({"file": rel, "hash": parsed_files[rel]})
            plan["summary"]["added"] += 1
        elif not in_parse and in_spec:
            entry = {"file": rel}
            # Keys absent from spec-cache are left out rather than serialised as null.
            if "documented_at" in spec_files[rel]:
                entry["last_documented"] = spec_files[rel]["documented_at"]
            plan["deleted"].append(entry)
            plan["summary"]["deleted"] += 1
        elif parsed_files[rel] != (spec_files.get(rel) or {}).get("file_hash"):
            spec_entry = spec_files.get(rel) or {}
            entry = {"file": rel, "current_hash": parsed_files[rel]}
            if "file_hash" in spec_entry:
                entry["documented_hash"] = spec_entry["file_hash"]
            if "documented_at" in spec_entry:
                entry["last_documented"] = spec_entry["documented_at"]
            plan["modified"].append(entry)
            plan["summary"]["modified"] += 1
        else:
            plan["unchanged"].append({"file": rel})
            plan["summary"]["unchanged"] += 1

    plan["summary"]["total"] = len(all_keys)
    return plan


def git_current_state(root: str) -> dict[str, Any]:
    """Hash every tracked file into the ``{entries: {absPath: {file_hash}}}`` shape
    that :func:`compute_diff_plan` expects."""
    try:
        proc = subprocess.run(["git", "ls-files"], cwd=root,
                              stdout=subprocess.PIPE, encoding="utf-8", errors="replace")
    except OSError:
        return {"entries": {}}
    if proc.returncode != 0:
        return {"entries": {}}
    files = [line for line in re.split(r"\r?\n", proc.stdout) if line]
    entries: dict[str, Any] = {}
    for rel in files:
        abs_ = os.path.join(root, rel)
        try:
            with open(abs_, "rb") as f:
                entries[abs_] = {"file_hash": hashlib.sha256(f.read()).hexdigest()}
        except OSError:
            # Unreadable (dangling symlink, deleted-but-tracked): absent from the
            # current state, so it shows up as deleted.
            pass
    return {"entries": entries}


def main() -> int:
    args = parse_args(sys.argv[1:])
    root = os.path.abspath(str(args["root"])) if args.get("root") else os.getcwd()
    cache_dir = os.path.abspath(str(args["cache-dir"])) if args.get("cache-dir") \
        else os.path.join(root, ".analysis")
    analysis_dir = os.path.abspath(str(args["analysis-dir"])) \
        if args.get("analysis-dir") else os.path.join(root, ".analysis")

    spec_cache_path = os.path.join(analysis_dir, "spec-cache.json")
    if not os.path.exists(spec_cache_path):
        print(f"[diff-plan] Missing spec-cache: {spec_cache_path}", file=sys.stderr)
        print("[diff-plan] Run spec_cache_manager.py --action mark-all first "
              "(or finalize a full build).", file=sys.stderr)
        return 1
    with open(spec_cache_path, encoding="utf-8", errors="replace") as f:
        spec_cache = json.load(f)

    if args.get("from-git"):
        current_state = git_current_state(root)
        if len(current_state["entries"]) == 0:
            print(f"[diff-plan] git ls-files returned no files under {root} "
                  f"(not a git repo?)", file=sys.stderr)
            return 1
    else:
        parse_cache_path = os.path.join(cache_dir, "parse-cache.json")
        if not os.path.exists(parse_cache_path):
            print(f"[diff-plan] Missing parse-cache: {parse_cache_path}", file=sys.stderr)
            print("[diff-plan] Pass --from-git to use the git working tree as "
                  "the current state.", file=sys.stderr)
            return 1
        with open(parse_cache_path, encoding="utf-8", errors="replace") as f:
            current_state = json.load(f)

    plan = compute_diff_plan(current_state, spec_cache, root)

    os.makedirs(analysis_dir, exist_ok=True)
    out_name = args["out"] if isinstance(args.get("out"), str) else "diff-plan.json"
    # Keep the output inside --analysis-dir even if --out is given as an absolute path.
    out_path = os.path.normpath(analysis_dir + "/" + str(out_name))
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")

    s = plan["summary"]
    print(f"[diff-plan] wrote {os.path.relpath(out_path, os.getcwd())}", file=sys.stderr)
    print(f"  added:{s['added']} modified:{s['modified']} deleted:{s['deleted']} "
          f"unchanged:{s['unchanged']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
