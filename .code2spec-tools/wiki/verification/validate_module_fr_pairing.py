#!/usr/bin/env python3
"""Module/FR pairing: does every Module Design Card have exactly one matching
Functional Requirements doc, and vice versa?

W2 (code2spec-modules) is contracted to write one ``modules/<name>.md`` paired
with one ``functional-requirements/<name>-fr.md`` for every Core module —
Light-mode's documented FR skip (``--fr-doc ""``) only leaves the FR reference
blank *inside* the Module Design Card, it does not license omitting the paired
file. A module with no FR, or an FR with no module, is a broken W2 contract:
either an artifact silently went missing or the two trees drifted (a rename on
one side without the other, a stray leftover file, ...).

Usage: python3 validate_module_fr_pairing.py <wiki-dir> [--threshold 1.0]
"""

from __future__ import annotations

import os
import sys
import traceback
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

MODULES_DIRNAME = "modules"
FR_DIRNAME = "functional-requirements"
FR_SUFFIX = "-fr.md"
IGNORED_BASENAMES = {"README.md", "index.md"}


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
    """A ``--threshold``-style ratio, falling back to the default when unparsable."""
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def format_pct(x: float, digits: int) -> str:
    """A percentage to ``digits`` decimals, with ties rounded up."""
    q = Decimal(x).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return format(q, "f")


def _is_content_md(name: str) -> bool:
    return name.endswith(".md") and name not in IGNORED_BASENAMES \
        and not name.startswith("_")


def discover_modules(wiki_dir: str) -> list[str] | None:
    """Module slugs from ``modules/*.md``, or None when the directory is absent."""
    d = os.path.join(wiki_dir, MODULES_DIRNAME)
    if not os.path.isdir(d):
        return None
    try:
        entries = list(os.scandir(d))
    except OSError:
        return None
    return sorted(e.name[:-3] for e in entries
                 if e.is_file(follow_symlinks=False) and _is_content_md(e.name))


def discover_frs(wiki_dir: str) -> tuple[list[str], list[str]] | None:
    """FR slugs from ``functional-requirements/*-fr.md``, plus any misnamed file
    that doesn't follow the ``-fr.md`` convention (so it cannot pair with a
    module by name even though it lives in the right directory). None when the
    directory is absent."""
    d = os.path.join(wiki_dir, FR_DIRNAME)
    if not os.path.isdir(d):
        return None
    try:
        entries = list(os.scandir(d))
    except OSError:
        return None
    slugs: list[str] = []
    malformed: list[str] = []
    for e in sorted(entries, key=lambda e: e.name):
        if not e.is_file(follow_symlinks=False) or not _is_content_md(e.name):
            continue
        if e.name.endswith(FR_SUFFIX):
            slugs.append(e.name[:-len(FR_SUFFIX)])
        else:
            malformed.append(e.name)
    return slugs, malformed


def main() -> int:
    args = parse_args(sys.argv[1:])
    positional = args["positional"]
    wiki_dir = positional[0] if len(positional) > 0 else None
    if not wiki_dir:
        print("Usage: python3 validate_module_fr_pairing.py <wiki-dir> "
              "[--threshold 1.0]", file=sys.stderr)
        return 2
    threshold = parse_ratio(args.get("threshold"), 1.0)

    modules = discover_modules(wiki_dir)
    fr_result = discover_frs(wiki_dir)
    fr_slugs, malformed = fr_result if fr_result is not None else (None, [])

    if modules is None and fr_slugs is None:
        print(f"[module-fr-pairing] N/A — neither {MODULES_DIRNAME}/ nor "
              f"{FR_DIRNAME}/ exists under {wiki_dir}")
        return 0

    modules = modules or []
    fr_slugs = fr_slugs or []
    module_set, fr_set = set(modules), set(fr_slugs)

    if len(module_set) == 0 and len(fr_set) == 0 and len(malformed) == 0:
        print(f"[module-fr-pairing] N/A — {MODULES_DIRNAME}/ and {FR_DIRNAME}/ "
              f"are both empty under {wiki_dir}")
        return 0

    missing_fr = sorted(module_set - fr_set)      # module with no FR
    orphan_fr = sorted(fr_set - module_set)        # FR with no module
    matched = sorted(module_set & fr_set)
    union = module_set | fr_set

    ratio = len(matched) / len(union) if union else 1.0

    print("L? Module/FR Pairing")
    print(f"  wiki:      {wiki_dir}")
    print(f"  modules:   {len(module_set)} ({MODULES_DIRNAME}/*.md)")
    print(f"  fr docs:   {len(fr_set)} ({FR_DIRNAME}/*{FR_SUFFIX})")
    print(f"  matched:   {len(matched)}  ({format_pct(ratio * 100, 1)}%)")
    print(f"  threshold: {format_pct(threshold * 100, 0)}%")

    if missing_fr:
        print(f"\n  모듈에 매칭되는 FR 없음 ({len(missing_fr)}개):")
        for name in missing_fr:
            print(f"    ✗ {MODULES_DIRNAME}/{name}.md  →  "
                  f"{FR_DIRNAME}/{name}{FR_SUFFIX} 없음")
    if orphan_fr:
        print(f"\n  매칭되는 모듈 없는 FR ({len(orphan_fr)}개):")
        for name in orphan_fr:
            print(f"    ✗ {FR_DIRNAME}/{name}{FR_SUFFIX}  →  "
                  f"{MODULES_DIRNAME}/{name}.md 없음")
    if malformed:
        print(f"\n  명명 규칙({FR_SUFFIX}) 미준수로 어떤 모듈과도 매칭 불가 "
              f"({len(malformed)}개):")
        for name in malformed:
            print(f"    ✗ {FR_DIRNAME}/{name}")

    ok = not missing_fr and not orphan_fr and not malformed and ratio >= threshold
    if not ok:
        print(f"\n❌ module/FR pairing {format_pct(ratio * 100, 1)}% < threshold "
              f"{format_pct(threshold * 100, 0)}%, or naming-convention violations "
              f"present", file=sys.stderr)
        return 1
    print(f"\n✅ module/FR pairing {format_pct(ratio * 100, 1)}% — "
          f"every module has exactly one FR and vice versa")
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
