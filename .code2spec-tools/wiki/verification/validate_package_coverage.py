#!/usr/bin/env python3
"""L4 package coverage: is every package/module of the repo covered by the wiki?

Packages are discovered from the manifest when there is one (npm workspaces, plus the
well-known monorepo directory layouts) and from the repo's top-level directories
otherwise. A package counts as covered when either

1. a wiki category directory carries a trace of its name (fuzzy slug match), or
2. its path or its name appears in the body text anywhere.

Usage: python3 validate_package_coverage.py <repo-root> <wiki-dir> [--threshold 1.0]
"""

from __future__ import annotations

import json
import os
import re
import sys
import traceback
from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

# filesystem top-level dir 만으로 발견 — manifest 없는 단일 코드베이스 repo 대비.
# hardcoded exclude: 빌드 산출물 · 캐시 · 외부 자산 · 백업.
FILESYSTEM_EXCLUDE = {
    # VCS / IDE
    ".git", ".github", ".vscode", ".idea", ".cache", ".code-wiki",
    # 빌드 산출물
    "build", "dist", "target", "out", "_build",
    # 캐시
    "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".tox",
    # 외부 자산 / vendored
    "roms", "pc-bios", "third_party", "vendor", "subprojects",
    # 백업 / archive
    "_archive", "archive",
    # 문서 / 설정
    "docs", "scripts",
    # 도구 산출물 (graphify CLI 가 대상 repo 안에 떨구는 출력)
    "graphify-out",
}


def parse_args(argv: list[str]) -> dict[str, Any]:
    """Parse ``--key value`` / ``--flag`` pairs plus positionals."""
    out: dict[str, Any] = {"positional": []}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            k = a[2:]
            nxt = argv[i + 1] if i + 1 < len(argv) else None
            if nxt and not nxt.startswith("--"):
                i += 1
                out[k] = argv[i]
            else:
                out[k] = "true"
        else:
            out["positional"].append(a)
        i += 1
    return out


def parse_ratio(value: str | None, default: float) -> float:
    """A ``--threshold``-style ratio, falling back to the default when unparsable.

    Falling back matters: treating a typo as "no threshold" would silently disable
    the gate.
    """
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def format_pct(x: float, digits: int) -> str:
    """A percentage to ``digits`` decimals, with ties rounded up.

    Ties are reached at realistic denominators (13/16 → 81.25), and the built-in
    formatter would resolve them to even and report 81.2.
    """
    q = Decimal(x).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return format(q, "f")


def walk_markdown(dir_: str) -> Iterator[str]:
    """Every ``.md`` under ``dir_``, skipping dot-dirs (bar ``.code-wiki``) and symlinks."""
    try:
        entries = list(os.scandir(dir_))
    except OSError:
        return
    for e in entries:
        if e.name.startswith(".") and e.name != ".code-wiki":
            continue
        if e.name == "node_modules":
            continue
        fp = os.path.join(dir_, e.name)
        if e.is_dir(follow_symlinks=False):
            yield from walk_markdown(fp)
        elif e.is_file(follow_symlinks=False) and fp.endswith(".md"):
            yield fp


def discover_packages_from_filesystem(repo_root: str) -> list[dict[str, Any]]:
    """Top-level directories as packages — for a plain codebase with no manifest."""
    packages: list[dict[str, Any]] = []
    try:
        entries = list(os.scandir(repo_root))
    except OSError:
        return packages
    for e in entries:
        if not e.is_dir(follow_symlinks=False):
            continue
        if e.name.startswith("."):
            continue
        if e.name in FILESYSTEM_EXCLUDE:
            continue
        packages.append({"name": e.name, "dir": e.name, "source": "filesystem"})
    # Case-insensitive ordering, so `Api/` and `api/` sort next to each other; the
    # original spelling breaks ties so the listing is deterministic.
    return sorted(packages, key=lambda p: (p["name"].casefold(), p["name"]))


def _read_json(path: str) -> Any:
    with open(path, encoding="utf-8", errors="replace") as f:
        return json.loads(f.read())


def discover_packages(repo_root: str) -> list[dict[str, Any]]:
    """Packages declared by a manifest, or implied by a monorepo directory layout."""
    packages: list[dict[str, Any]] = []   # {name, dir, source}

    # 1. package.json workspaces
    root_pkg_path = os.path.join(repo_root, "package.json")
    if os.path.exists(root_pkg_path):
        try:
            pkg = _read_json(root_pkg_path)
            ws = pkg.get("workspaces") if isinstance(pkg, dict) else None
            patterns: list[Any] = []
            if isinstance(ws, list):
                patterns = ws
            elif isinstance(ws, dict) and isinstance(ws.get("packages"), list):
                patterns = ws["packages"]
            for pattern in patterns:
                # Minimal glob support: only a trailing /* or /**
                base = re.sub(r"/\*\*?$", "", pattern)
                base_dir = os.path.join(repo_root, base)
                if not os.path.exists(base_dir):
                    continue
                try:
                    sub_entries = list(os.scandir(base_dir))
                except OSError:
                    continue
                for sub in sub_entries:
                    if not sub.is_dir(follow_symlinks=False):
                        continue
                    sub_path = os.path.join(base_dir, sub.name)
                    sub_pkg = os.path.join(sub_path, "package.json")
                    if os.path.exists(sub_pkg):
                        try:
                            sp = _read_json(sub_pkg)
                            packages.append({
                                "name": (sp.get("name") if isinstance(sp, dict) else None)
                                        or sub.name,
                                "dir": os.path.relpath(sub_path, repo_root),
                                "source": "workspaces",
                            })
                        except Exception:
                            pass
        except Exception:
            pass

    # 2. fallback A — *monorepo 시그널* 이 있을 때만 (npm workspaces 잡혔거나
    #    pnpm-workspace.yaml 존재) 잘 알려진 디렉토리 패턴으로 추가 보강.
    has_pnpm_workspace = os.path.exists(os.path.join(repo_root, "pnpm-workspace.yaml"))
    if len(packages) > 0 or has_pnpm_workspace:
        fallback_patterns = ["packages", "tools", "services", "apps", "crates",
                             "cmd", "pkg", "modules"]
        for top in fallback_patterns:
            base = os.path.join(repo_root, top)
            if not os.path.exists(base):
                continue
            try:
                subs = list(os.scandir(base))
            except OSError:
                continue
            for sub in subs:
                if not sub.is_dir(follow_symlinks=False) or sub.name.startswith(".") \
                        or sub.name == "_archive":
                    continue
                if any(p["dir"] == f"{top}/{sub.name}" for p in packages):
                    continue
                packages.append({"name": sub.name, "dir": f"{top}/{sub.name}",
                                 "source": "fallback"})

    # 3. top-level 단일 패키지 (예: mcp_server) 도 후보 — 위에서 안 잡힌 경우
    top_level = list(os.scandir(repo_root))
    for e in top_level:
        if not e.is_dir(follow_symlinks=False):
            continue
        if e.name.startswith(".") or e.name in ("node_modules", "_archive", "docs",
                                                "utils", "scripts", "data", "dist",
                                                "build"):
            continue
        sub_pkg_json = os.path.join(repo_root, e.name, "package.json")
        if os.path.exists(sub_pkg_json):
            exists = any(p["dir"] == e.name for p in packages)
            if not exists:
                try:
                    sp = _read_json(sub_pkg_json)
                    packages.append({
                        "name": (sp.get("name") if isinstance(sp, dict) else None) or e.name,
                        "dir": e.name, "source": "top-level"})
                except Exception:
                    pass

    return packages


def aggregate_wiki(wiki_dir: str) -> dict[str, Any]:
    """The whole wiki as one searchable buffer, plus its top-level category dirs."""
    buffer: list[str] = []
    category_dirs: list[str] = []
    try:
        entries = list(os.scandir(wiki_dir))
    except OSError:
        return {"buffer": "", "categoryDirs": []}
    for e in entries:
        if e.is_dir(follow_symlinks=False):
            category_dirs.append(e.name)
    for fp in walk_markdown(wiki_dir):
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                buffer.append(f.read())
        except OSError:
            pass
    return {"buffer": "\n\n".join(buffer), "categoryDirs": category_dirs}


def is_package_covered(pkg: dict[str, Any], wiki: dict[str, Any]) -> dict[str, Any]:
    """Whether the wiki covers one package, and by which of the two criteria."""
    name, dir_ = pkg["name"], pkg["dir"]

    # Does a wiki category directory carry a trace of the package name?
    def slug(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", s.lower())

    name_slug = slug(name)
    dir_slug = slug(dir_.replace("/", "-"))
    base_slug = slug(os.path.basename(dir_))
    hit_category = any(
        (base_slug in slug(cat)) or (name_slug in slug(cat)) or (dir_slug in slug(cat))
        for cat in wiki["categoryDirs"])
    if hit_category:
        return {"covered": True, "via": "category"}

    # Does the body mention the package path or name?
    if dir_ in wiki["buffer"] or ("`" + name + "`") in wiki["buffer"] \
            or name in wiki["buffer"]:
        return {"covered": True, "via": "body"}

    return {"covered": False, "via": None}


def main() -> int:
    args = parse_args(sys.argv[1:])
    positional = args["positional"]
    repo_root = positional[0] if len(positional) > 0 else None
    wiki_dir = positional[1] if len(positional) > 1 else None
    if not repo_root or not wiki_dir:
        print("Usage: python3 validate_package_coverage.py <repo-root> <wiki-dir> "
              "[--threshold 1.0]", file=sys.stderr)
        return 2
    threshold = parse_ratio(args.get("threshold"), 1.0)

    # Manifest-declared packages win; the filesystem scan is the fallback.
    packages = discover_packages(repo_root)
    discovery_source = "manifest (workspaces)" if len(packages) > 0 else ""

    if len(packages) == 0:
        packages = discover_packages_from_filesystem(repo_root)
        if len(packages) > 0:
            discovery_source = (f"filesystem top-level (excluded "
                                f"{len(FILESYSTEM_EXCLUDE)} well-known patterns)")

    if len(packages) == 0:
        print(f"No packages discovered in {repo_root} — exiting silently")
        return 0

    wiki = aggregate_wiki(wiki_dir)

    covered = 0
    rows: list[dict[str, Any]] = []
    for pkg in packages:
        r = is_package_covered(pkg, wiki)
        if r["covered"]:
            covered += 1
        rows.append({"pkg": pkg, **r})

    ratio = covered / len(packages)
    print(f"L4 Package Coverage — {repo_root}")
    print(f"  source:    {discovery_source}")
    print(f"  wiki:      {wiki_dir}")
    print(f"  packages:  {len(packages)} discovered")
    print(f"  covered:   {covered}  ({format_pct(ratio * 100, 1)}%)")
    print(f"  threshold: {format_pct(threshold * 100, 0)}%")
    print()
    print("  per-package:")
    for row in rows:
        pkg = row["pkg"]
        mark = "✓" if row["covered"] else "✗"
        via_str = f"via {row['via']}" if row["via"] else "NOT COVERED"
        print(f"    {mark} {pkg['dir'].ljust(40)} {pkg['name'].ljust(28)} {via_str}")

    if ratio < threshold:
        print(f"\n❌ package coverage {format_pct(ratio * 100, 1)}% < threshold "
              f"{format_pct(threshold * 100, 0)}%", file=sys.stderr)
        return 1
    print(f"\n✅ package coverage {format_pct(ratio * 100, 1)}% ≥ threshold "
          f"{format_pct(threshold * 100, 0)}%")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        sys.exit(3)
