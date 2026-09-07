#!/usr/bin/env python3
"""Build direct logical-module dependencies from canonical W2 groups and AST imports.

The output is deliberately narrower than a general architecture graph: an edge exists
only when one resolved, direct repository import connects files owned by two distinct
entries in ``.analysis/state/delta/module-groups.yaml``.  Each aggregate edge retains
the source file, target file, and source line that justify it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml


def module_id(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def norm_path(value: Any) -> str:
    return str(value or "").replace("\\", "/").lstrip("/")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_owners(groups_path: Path) -> tuple[dict[str, str], list[str]]:
    """Return unambiguous file→module ownership and ambiguous paths.

    ``files`` is the W2-approved ownership list.  Prefix matching and inferred
    ownership are intentionally forbidden: either would make a conceptual diagram
    appear code-backed without a traceable source-file decision.
    """
    raw = yaml.safe_load(groups_path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(raw, dict) or not isinstance(raw.get("modules"), list):
        raise ValueError("module-groups.yaml must contain a modules list")
    candidates: dict[str, set[str]] = {}
    for group in raw["modules"]:
        if not isinstance(group, dict) or not isinstance(group.get("name"), str):
            continue
        owner = module_id(group["name"])
        for file_path in group.get("files") or []:
            path = norm_path(file_path)
            if path:
                candidates.setdefault(path, set()).add(owner)
    ambiguous = sorted(path for path, owners in candidates.items() if len(owners) != 1)
    owners = {path: next(iter(values)) for path, values in candidates.items()
              if len(values) == 1}
    return owners, ambiguous


def build_edges(deps: dict[str, Any], owners: dict[str, str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for imp in deps.get("internal") or []:
        if not isinstance(imp, dict):
            continue
        frm = norm_path(imp.get("from"))
        to = norm_path(imp.get("resolved_to"))
        source_module, target_module = owners.get(frm), owners.get(to)
        if not source_module or not target_module or source_module == target_module:
            continue
        evidence = {"from": frm, "to": to, "line": imp.get("line")}
        grouped.setdefault((source_module, target_module), []).append(evidence)
    edges: list[dict[str, Any]] = []
    for (frm, to), evidence in sorted(grouped.items()):
        # Stable output makes the artifact safe to use in diffs and as validator input.
        evidence.sort(key=lambda e: (e["from"], e["to"], int(e["line"] or 0)))
        edges.append({"from": frm, "to": to, "evidence": evidence})
    return edges


def build_artifact(groups_path: Path, deps_path: Path) -> dict[str, Any]:
    owners, ambiguous = load_owners(groups_path)
    deps = json.loads(deps_path.read_text(encoding="utf-8", errors="replace"))
    if not isinstance(deps, dict):
        raise ValueError("deps.json must be an object")
    return {
        "schemaVersion": 1,
        "input": {
            "moduleGroups": str(groups_path), "moduleGroupsSha256": sha256(groups_path),
            "deps": str(deps_path), "depsSha256": sha256(deps_path),
        },
        "modules": sorted(set(owners.values())),
        "ownedFileCount": len(owners),
        "ambiguousFiles": ambiguous,
        "edges": build_edges(deps, owners),
    }


def atomic_json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wiki-dir", required=True)
    ap.add_argument("--module-groups")
    ap.add_argument("--deps")
    ap.add_argument("--out")
    args = ap.parse_args()
    wiki = Path(args.wiki_dir).resolve()
    groups = Path(args.module_groups) if args.module_groups else \
        wiki / ".analysis" / "state" / "delta" / "module-groups.yaml"
    deps = Path(args.deps) if args.deps else wiki / ".ast" / "deps.json"
    out = Path(args.out) if args.out else wiki / ".analysis" / "state" / "delta" / "module-deps.json"
    if not groups.is_file():
        print(f"[module-deps] skipped: no canonical module groups at {groups}")
        return 0
    if not deps.is_file():
        print(f"[module-deps] skipped: no AST dependencies at {deps}")
        return 0
    try:
        artifact = build_artifact(groups, deps)
        atomic_json_write(out, artifact)
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"[module-deps] failed: {exc}", file=sys.stderr)
        return 2
    print(f"[module-deps] wrote {out}: {len(artifact['modules'])} modules, "
          f"{len(artifact['edges'])} direct edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
