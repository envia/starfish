#!/usr/bin/env python3
"""Lint the layout of the generated SDD tree.

Catches the three ways an agent tends to break the agreed layout:

* a mandatory chapter filed under an ad-hoc subfolder such as ``sdd/`` (ERROR)
* non-standard loose pages left at the root (``logic-extraction.md``,
  ``pattern-mapping.md``) or documents in an unexpected subfolder (WARN)
* `[Source:]` citations that were never converted into deep-links (WARN)

Exit 1 on any ERROR, 0 otherwise — warnings do not block the pipeline.

Usage: python3 validate_layout.py --wiki-dir <dir>
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

_WIKI_DIR = Path(__file__).resolve().parent.parent
if str(_WIKI_DIR) not in sys.path:
    sys.path.insert(0, str(_WIKI_DIR))

from page_model import ALL_CHAPTERS, CONDITIONAL_CHAPTERS, MANDATORY_CHAPTERS  # noqa: E402

# Generated artefacts and tooling; never part of the documentation layout.
ARTIFACT_DIRS = {".ast", ".trust", ".claims", ".analysis", ".git", "node_modules"}
# Subfolders documents may live in. The order is user-visible: it is joined into the
# WARN message that lists the allowed names.
ALLOWED_DOC_DIRS = [
    "modules", "functional-requirements", "api", "architecture", "dependency",
    "operation", "components",
]
# Markdown allowed at the root: the SDD chapters plus README, the evidence-gated
# chapters and the standard W3 outputs (quick reference, history, verification report).
ALLOWED_ROOT_MD = {
    "README.md", "index.md", "code2spec-quick-reference.md", "history.md",
    "verification-report.md",
    *ALL_CHAPTERS, *CONDITIONAL_CHAPTERS,
}


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """Parse ``--key value`` / ``--flag`` pairs; a flag without a value becomes True."""
    args: dict[str, str | bool] = {}
    i = 0
    while i < len(argv):
        k = argv[i]
        if not k.startswith("--"):
            i += 1
            continue
        nxt = argv[i + 1] if i + 1 < len(argv) else None
        if not nxt or nxt.startswith("--"):
            args[k[2:]] = True
        else:
            args[k[2:]] = nxt
            i += 1
        i += 1
    return args


def opt(args: dict[str, str | bool], key: str) -> str | None:
    """Value of ``--key`` when it was given with a non-empty string."""
    value = args.get(key)
    return value if isinstance(value, str) and value else None


def list_md(dir_: str, wiki_dir: str) -> list[str]:
    """Every ``.md`` under ``dir_``, as paths relative to ``wiki_dir``."""
    out: list[str] = []

    def walk(d: str) -> None:
        for e in os.scandir(d):
            if e.is_dir(follow_symlinks=False):
                if e.name in ARTIFACT_DIRS or e.name.startswith("."):
                    continue
                walk(e.path)
            elif e.is_file(follow_symlinks=False) and e.name.endswith(".md"):
                out.append(os.path.relpath(os.path.join(d, e.name), wiki_dir)
                           .replace(os.sep, "/"))
    walk(dir_)
    return out


def check_misplaced_chapters(wiki_dir: str, all_md: list[str]) -> list[str]:
    """ERROR for each mandatory chapter that exists, but not at the root.

    A chapter missing everywhere is not reported here — the orchestrator's
    requiredSlots gate covers that case.
    """
    errors: list[str] = []
    for ch in MANDATORY_CHAPTERS:
        if os.path.exists(os.path.join(wiki_dir, ch)):
            continue
        misplaced = next((p for p in all_md if p.endswith("/" + ch)), None)
        if misplaced:
            errors.append(f"필수 문서 '{ch}' 가 루트가 아닌 '{misplaced}' 에 있습니다 "
                          f"— OUTPUT_DIR 루트에 직접 두세요(sdd/ 등 하위폴더 금지).")
    return errors


def check_unexpected_dirs(wiki_dir: str) -> list[str]:
    """WARN for each unexpected top-level directory that actually holds documents."""
    warnings: list[str] = []
    for e in os.scandir(wiki_dir):
        if not e.is_dir(follow_symlinks=False) or e.name in ARTIFACT_DIRS \
                or e.name.startswith("."):
            continue
        if e.name in ALLOWED_DOC_DIRS:
            continue
        if len(list_md(os.path.join(wiki_dir, e.name), wiki_dir)) > 0:
            warnings.append(f"예상 밖 문서 하위폴더 '{e.name}/' — 서브페이지는 허용 폴더"
                            f"({'/'.join(ALLOWED_DOC_DIRS)})만 사용하세요.")
    return warnings


def check_loose_root_md(wiki_dir: str) -> list[str]:
    """WARN for each root-level page that is not part of the standard set."""
    warnings: list[str] = []
    for e in os.scandir(wiki_dir):
        if not e.is_file(follow_symlinks=False) or not e.name.endswith(".md"):
            continue
        if e.name not in ALLOWED_ROOT_MD:
            warnings.append(f"비표준 top-level 문서 '{e.name}' — 내용을 해당 챕터/모듈 카드에 "
                            f"흡수하고 loose 파일은 남기지 마세요.")
    return warnings


def count_source_tags(wiki_dir: str, all_md: list[str]) -> int:
    """Total `[Source:` occurrences left across the tree."""
    total = 0
    for rel in all_md:
        with open(os.path.join(wiki_dir, rel), encoding="utf-8", errors="replace") as f:
            total += len(re.findall(r"\[Source:", f.read(), re.IGNORECASE))
    return total


def main() -> int:
    args = parse_args(sys.argv[1:])
    wiki_dir_arg = opt(args, "wiki-dir")
    if not wiki_dir_arg:
        print("usage: python3 validate_layout.py --wiki-dir <dir>", file=sys.stderr)
        return 2
    wiki_dir = os.path.abspath(wiki_dir_arg)

    all_md = list_md(wiki_dir, wiki_dir)
    errors = check_misplaced_chapters(wiki_dir, all_md)
    warnings = check_unexpected_dirs(wiki_dir) + check_loose_root_md(wiki_dir)

    source_tags = count_source_tags(wiki_dir, all_md)
    if source_tags > 0:
        warnings.append(f"{source_tags} 개 [Source:] 인용이 deep-link로 변환되지 않고 "
                        f"남았습니다 — convert-source-tags 또는 생성 규율을 확인하세요.")

    for e in errors:
        print(f"[layout] ERROR — {e}")
    for w in warnings:
        print(f"[layout] WARN — {w}")
    if len(errors) == 0 and len(warnings) == 0:
        print(f"[layout] OK — 루트 배치 정상, 예상 밖 폴더/파일·[Source:] 잔존 없음 "
              f"(md {len(all_md)}개)")
    print(f"[layout] SUMMARY — errors={len(errors)} warnings={len(warnings)}")
    return 1 if len(errors) > 0 else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
