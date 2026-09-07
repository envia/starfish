#!/usr/bin/env python3
"""Synchronize a managed module-dependency Mermaid block from module-deps.json.

Only direct, evidence-backed edges already emitted by module_deps.py are rendered.
This intentionally does not infer conceptual or transitive relationships.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

START = "<!-- code2spec:module-dependency:start -->"
END = "<!-- code2spec:module-dependency:end -->"


def render(data: dict) -> str:
    modules = data.get("modules") or []
    edges = data.get("edges") or []
    lines = ["%% code2spec:diagram-type=module-dependency", "graph LR"]
    for module in modules:
        label = module.replace("_", "-")
        lines.append(f'  {module}["{label}"]')
    for edge in edges:
        lines.append(f'  {edge["from"]} --> {edge["to"]}')
    return "\n".join(lines) + "\n"


def managed_block(mermaid: str) -> str:
    return f"{START}\n```mermaid\n{mermaid}```\n{END}"


def sync_page(path: Path, block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    start, end = text.find(START), text.find(END)
    if start >= 0 and end > start:
        end += len(END)
        updated = text[:start] + block + text[end:]
    else:
        updated = text.rstrip() + "\n\n## Module Dependencies\n\n" + block + "\n"
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki-dir", required=True)
    ap.add_argument("--page", default="02-architecture.md")
    ap.add_argument("--no-page", action="store_true")
    args = ap.parse_args()
    wiki = Path(args.wiki_dir)
    artifact = wiki / ".analysis" / "state" / "delta" / "module-deps.json"
    if not artifact.is_file():
        print(f"[module-diagram] skipped: missing {artifact}")
        return 0
    data = json.loads(artifact.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1:
        raise SystemExit("[module-diagram] invalid module-deps schema")
    mermaid = render(data)
    out = wiki / "diagrams" / "module-dependencies.mmd"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(mermaid, encoding="utf-8")
    changed = False
    if not args.no_page:
        page = wiki / args.page
        if page.is_file():
            changed = sync_page(page, managed_block(mermaid))
    print(f"[module-diagram] wrote {out}; page_updated={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
