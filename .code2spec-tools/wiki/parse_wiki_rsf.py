#!/usr/bin/env python3
"""Decide which wiki pages need regenerating, from their `Relevant source files`.

Each page declares the sources it documents in an RSF blockquote. This tool parses
those declarations, splits them into files and directories, and crosses them with a
diff plan:

* a **file** reference triggers on any change — added, modified or deleted
* a **directory** reference triggers only on structural change (added or deleted);
  editing a file inside it does not invalidate the page

Usage:
  python3 parse_wiki_rsf.py --wiki-dir <code2spec> --repo-root <repo>
      (print the RSF map only)
  python3 parse_wiki_rsf.py --wiki-dir <code2spec> --repo-root <repo> \\
      --diff-plan <diff-plan.json> [--out <decision.json>]
      (print the regeneration decision)
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import stat
import sys
from datetime import UTC, datetime
from typing import Any

_RSF_HEADER_RE = re.compile(r"^>\s*\*\*\s*relevant source files\s*\*\*", re.IGNORECASE)
_RSF_ITEM_RE = re.compile(r"^>\s*-\s*\[([^\]]+)\]\(")


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


def opt(args: dict[str, str | bool], key: str) -> str | None:
    """Value of ``--key`` when it was given with a non-empty string."""
    value = args.get(key)
    return value if isinstance(value, str) and value else None


def _iso_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def walk_markdown(dir_: str, base_dir: str | None = None) -> list[str]:
    """Every ``.md`` page under ``dir_``, as paths relative to ``base_dir``.

    Includes ``modules/`` and ``functional-requirements/``; skips dot-directories
    (the generated ``.ast``/``.trust``/``.claims``/``.analysis`` trees) and symlinks.
    """
    if base_dir is None:
        base_dir = dir_
    out: list[str] = []
    for e in os.scandir(dir_):
        if e.name.startswith("."):
            continue
        if e.is_dir(follow_symlinks=False):
            if e.name == "node_modules":
                continue
            out.extend(walk_markdown(e.path, base_dir))
        elif e.is_file(follow_symlinks=False) and e.name.endswith(".md"):
            out.append(os.path.relpath(e.path, base_dir).replace(os.sep, "/"))
    return out


def classify_path(rel_path: str, repo_root: str) -> str:
    """``'dir'`` or ``'file'``, checked against the repo and falling back to the
    extension when the path no longer exists (e.g. it was deleted)."""
    abs_ = os.path.join(repo_root, rel_path)
    try:
        if stat.S_ISDIR(os.stat(abs_).st_mode):
            return "dir"
        return "file"
    except OSError:
        return "file" if posixpath.splitext(rel_path.rstrip("/"))[1] else "dir"


def parse_rsf_block(markdown: str, repo_root: str) -> dict[str, list[str]]:
    """Parse one page's RSF block into ``{files, dirs}``."""
    items: list[str] = []
    in_block = False

    for line in re.split(r"\r?\n", markdown):
        if not in_block:
            if _RSF_HEADER_RE.search(line):
                in_block = True
            continue
        if not line.startswith(">"):
            break            # the blockquote ended
        # `> - [label](url)` — capture the label; strip wrapping backticks, which
        # code2spec omits but the older code2wiki format used.
        m = _RSF_ITEM_RE.search(line)
        if m:
            label = re.sub(r"^`+|`+$", "", m.group(1).strip()).strip()
            if label:
                items.append(label)

    files: list[str] = []
    dirs: list[str] = []
    for p in items:
        if classify_path(p, repo_root) == "dir":
            dirs.append(p)
        else:
            files.append(p)
    return {"files": files, "dirs": dirs}


def build_rsf_map(wiki_dir: str, repo_root: str) -> dict[str, dict[str, list[str]]]:
    """RSF map for every page under ``wiki_dir``, keyed by relative page path."""
    result: dict[str, dict[str, list[str]]] = {}
    for rel in walk_markdown(wiki_dir):
        with open(os.path.join(wiki_dir, rel), encoding="utf-8", errors="replace") as f:
            md = f.read()
        result[rel] = parse_rsf_block(md, repo_root)
    return result


def changed_files_by_kind(diff_plan: dict[str, Any]) -> dict[str, list[str]]:
    """Changed files per category, as repo-relative paths."""
    def pick(arr: list[dict[str, Any]] | None) -> list[str]:
        return [x.get("file") for x in (arr or [])]
    return {
        "added": pick(diff_plan.get("added")),
        "modified": pick(diff_plan.get("modified")),
        "deleted": pick(diff_plan.get("deleted")),
    }


def is_under_dir(rel_path: str, d: str) -> bool:
    """Whether ``rel_path`` is ``d`` itself or lives under it."""
    dd = d if d.endswith("/") else d + "/"
    return rel_path == d or rel_path.startswith(dd)


def decide_regeneration(rsf_map: dict[str, dict[str, list[str]]],
                        diff_plan: dict[str, Any]) -> dict[str, Any]:
    """Cross the RSF map with the diff plan and split pages into regenerate/skip."""
    changed = changed_files_by_kind(diff_plan)
    # For file references: last writer wins, so a file both added and deleted counts
    # as deleted.
    file_change_kind: dict[str, str] = {}
    for f in changed["added"]:
        file_change_kind[f] = "added"
    for f in changed["modified"]:
        file_change_kind[f] = "modified"
    for f in changed["deleted"]:
        file_change_kind[f] = "deleted"
    # For directory references: only structural change. A move shows up as an
    # add plus a delete, so it is covered.
    structural_changes = (
        [{"file": f, "change": "added"} for f in changed["added"]]
        + [{"file": f, "change": "deleted"} for f in changed["deleted"]]
    )

    regenerate: list[dict[str, Any]] = []
    skip: list[str] = []

    for page, rsf in rsf_map.items():
        reasons: list[dict[str, Any]] = []

        for rsf_file in rsf["files"]:
            kind = file_change_kind.get(rsf_file)
            if kind:
                reasons.append({"type": "file", "rsf": rsf_file, "change": kind})

        for rsf_dir in rsf["dirs"]:
            for sc in structural_changes:
                if is_under_dir(sc["file"], rsf_dir):
                    reasons.append({"type": "dir", "rsf": rsf_dir,
                                    "change": sc["change"], "file": sc["file"]})

        if len(reasons) > 0:
            regenerate.append({"page": page, "reasons": reasons})
        else:
            skip.append(page)

    return {"regenerate": regenerate, "skip": skip}


def main() -> int:
    args = parse_args(sys.argv[1:])
    wiki_dir_arg = opt(args, "wiki-dir")
    wiki_dir = os.path.abspath(wiki_dir_arg) if wiki_dir_arg else None
    repo_root = os.path.abspath(opt(args, "repo-root") or os.getcwd())

    if not wiki_dir or not os.path.exists(wiki_dir):
        print("Usage: python3 parse_wiki_rsf.py --wiki-dir <code2spec> --repo-root <repo> "
              "[--diff-plan <path>] [--out <path>]", file=sys.stderr)
        print(f"[rsf] wiki-dir not found: {wiki_dir or '(not given)'}", file=sys.stderr)
        return 1

    rsf_map = build_rsf_map(wiki_dir, repo_root)

    diff_plan_arg = opt(args, "diff-plan")
    if not diff_plan_arg:
        sys.stdout.write(json.dumps(rsf_map, indent=2, ensure_ascii=False) + "\n")
        total_files = sum(len(r["files"]) for r in rsf_map.values())
        total_dirs = sum(len(r["dirs"]) for r in rsf_map.values())
        print(f"[rsf] parsed {len(rsf_map)} pages — {total_files} file refs, "
              f"{total_dirs} dir refs", file=sys.stderr)
        return 0

    diff_plan_path = os.path.abspath(diff_plan_arg)
    if not os.path.exists(diff_plan_path):
        print(f"[rsf] diff-plan not found: {diff_plan_path}", file=sys.stderr)
        return 1
    with open(diff_plan_path, encoding="utf-8", errors="replace") as f:
        diff_plan = json.load(f)
    decision = decide_regeneration(rsf_map, diff_plan)

    output = {
        "generated_at": _iso_now(),
        "regenerate": decision["regenerate"],
        "skip": decision["skip"],
        "summary": {"regenerate": len(decision["regenerate"]),
                    "skip": len(decision["skip"])},
    }

    out_arg = opt(args, "out")
    if out_arg:
        out_path = os.path.abspath(out_arg)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
        print(f"[rsf] wrote {os.path.relpath(out_path, os.getcwd())}", file=sys.stderr)
    else:
        sys.stdout.write(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(f"[rsf] regenerate:{output['summary']['regenerate']} "
          f"skip:{output['summary']['skip']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
