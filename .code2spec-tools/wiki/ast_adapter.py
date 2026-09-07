#!/usr/bin/env python3
"""Convert a code2spec tree-sitter graph into the wiki `.ast/` views.

Input is ``graph-raw.json`` (absolute paths, ``<abs>::Class.method`` symbols) as
produced by ``cli.py export``. Output is the schema the wiki validators, writers
and dashboard consume:

* ``api.json``  — per-file export catalogue (signature synthesised from name+params)
* ``deps.json`` — relations split by kind: internal/external/calls/unresolved_calls/
  tested_by/depends_on/files/inherits/implements/contains
* ``metadata.json`` and ``README.md`` alongside them, for provenance

Usage:
  python3 ast_adapter.py --repo-root <repo> --graph <graph-raw.json> \
    --out <api.json> --out-deps <deps.json> [--lang <label>]

Canonical paths (wired by the wiki launcher; this adapter itself is repo-agnostic):
  --graph    <target>/code2spec/.analysis/cache/code-to-ast/graph-raw.json
  --out      <target>/code2spec/wiki/.ast/api.json
  --out-deps <target>/code2spec/wiki/.ast/deps.json

Schema contract: docs/wiki/ast-schema.md
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import sys
from typing import Any

# Repository root, resolved once in main(); rel() and rel_qualified() read it.
REPO_ROOT: str | None = None


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """Parse ``--key value`` / ``--flag`` pairs; a flag without a value becomes True."""
    args: dict[str, str | bool] = {}
    i = 1
    while i < len(argv):
        flag = argv[i]
        if flag.startswith("--"):
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


def rel(abs_: Any) -> Any:
    if not isinstance(abs_, str):
        return abs_
    r = os.path.relpath(abs_, REPO_ROOT).replace(os.sep, "/")
    # A path equal to the repo root is not a file inside it.
    return "" if r == "." else r


# "abspath::Class.method" → "relpath::Class.method"
def rel_qualified(q: str) -> str:
    idx = q.find("::")
    if idx == -1:
        return rel(q)
    return rel(q[:idx]) + "::" + q[idx + 2:]


def is_inside_repo(rel_path: Any) -> bool:
    return bool(rel_path) and isinstance(rel_path, str) \
        and not rel_path.startswith("..") and not os.path.isabs(rel_path)


# Deliberately loose: a root-level `tests/` directory and pytest's `test_*.py`
# prefix are NOT matched — only `<sep>tests?/`, `__tests__/` and the
# `[._-](test|spec).<ext>` suffix. re.ASCII keeps `[a-z]` from matching
# non-ASCII letters under IGNORECASE.
_TEST_PATH_RE = re.compile(
    r"[/\\](tests?[/\\]|__tests__[/\\])|[._-](test|spec)\.[a-z]+\Z",
    re.IGNORECASE | re.ASCII)


def is_test_file_path(p: str) -> bool:
    return _TEST_PATH_RE.search(p) is not None


# code2spec params "()"·"(a: T, b)" → deep-wiki "a: T, b"
def norm_params(params: Any) -> str:
    if not params or not isinstance(params, str):
        return ""
    s = params.strip()
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1]
    return s.strip()


# return_type ": void" → "void"
def norm_return(rt: Any) -> str:
    if not rt or not isinstance(rt, str):
        return ""
    return re.sub(r"^\s*:\s*", "", rt, count=1).strip()


def _write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def main() -> int:
    global REPO_ROOT

    # The summary lines contain an em-dash and Korean text; pin UTF-8 so a
    # non-UTF-8 locale cannot raise UnicodeEncodeError.
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:  # pragma: no cover
        pass

    args = parse_args(sys.argv)
    REPO_ROOT = os.path.abspath(str(args["repo-root"])) if args.get("repo-root") else None
    graph_path = os.path.abspath(str(args["graph"])) if args.get("graph") else None
    out_api = opt(args, "out")
    out_deps = opt(args, "out-deps")
    lang_label = args.get("lang") or "auto"

    if not REPO_ROOT or not graph_path or not out_api or not out_deps:
        print("usage: python3 ast_adapter.py --repo-root <repo> --graph <graph-raw.json> "
              "--out <api.json> --out-deps <deps.json>", file=sys.stderr)
        return 2

    with open(graph_path, encoding="utf-8", errors="replace") as fh:
        graph = json.loads(fh.read())
    nodes = (graph.get("nodes") if isinstance(graph, dict) else None) or []
    edges = (graph.get("edges") if isinstance(graph, dict) else None) or []

    # ── api.json: exports per file ───────────────────────────────────────────
    file_meta: dict[str, dict[str, Any]] = {}       # relpath → language, is_test
    exports_by_file: dict[str, list[dict[str, Any]]] = {}   # relpath → exports

    for n in nodes:
        if n.get("kind") == "File":
            p = rel(n.get("file_path") or n.get("name"))
            if is_inside_repo(p):
                file_meta[p] = {"language": n.get("language") or "unknown",
                                "is_test": bool(n.get("is_test"))}
            continue
        if n.get("kind") in ("Function", "Class", "Method"):
            p = rel(n.get("file_path"))
            if not is_inside_repo(p):
                continue
            params = norm_params(n.get("params"))
            line = n.get("line_start")
            if line is None:
                line = n.get("line")
            if line is None:
                line = 1
            line_end = n.get("line_end")
            if line_end is None:
                line_end = n.get("line_start")
            if line_end is None:
                line_end = 1
            ex = {
                "name": n.get("name"),
                "kind": n.get("kind"),
                "line": line,
                "line_end": line_end,
                "signature": f"{n.get('name')}({params})",
                "params": params,
                "return_type": norm_return(n.get("return_type")),
                "modifiers": n["modifiers"] if isinstance(n.get("modifiers"), list) else [],
                "is_test": bool(n.get("is_test")),
                "parent_name": n.get("parent_name") or "",
                "extra": n.get("extra") or {},
            }
            exports_by_file.setdefault(p, []).append(ex)

    api_files = []
    for p, exps in exports_by_file.items():
        exps.sort(key=lambda e: (e["line"], e["name"]))
        api_files.append({"path": p,
                          "language": (file_meta.get(p) or {}).get("language") or "unknown",
                          "exports": exps})
    api_files.sort(key=lambda f: f["path"])
    api_result = {"files": api_files}

    # 심볼 인덱스 (2차 해소용)
    symbol_map: dict[str, set[str]] = {}            # relpath → symbol names
    global_symbol_index: dict[str, set[str]] = {}   # symbol name → relpaths
    for f in api_files:
        names = set()
        for e in f["exports"]:
            names.add(e["name"])
            global_symbol_index.setdefault(e["name"], set()).add(f["path"])
        symbol_map[f["path"]] = names

    # ── deps.json ────────────────────────────────────────────────────────────
    deps: dict[str, Any] = {
        "internal": [], "external": [], "calls": [], "unresolved_calls": [],
        "tested_by": [], "depends_on": [], "files": [], "inherits": [],
        "implements": [], "contains": [],
    }

    # IMPORTS_FROM
    for e in edges:
        if e.get("kind") != "IMPORTS_FROM":
            continue
        frm = rel(e.get("source"))
        if not is_inside_repo(frm):
            continue
        to = e.get("target")
        line = e.get("line")
        if line is None:
            line = 1
        entry = {"from": frm, "to": to, "specifiers": [], "line": line}
        internal = isinstance(to, str) and (to.startswith(".") or to.startswith("/"))
        deps["internal" if internal else "external"].append(entry)

    # INHERITS
    for e in edges:
        if e.get("kind") != "INHERITS":
            continue
        frm = rel_qualified(e.get("source"))
        if not is_inside_repo(frm.split("::")[0]):
            continue
        line = e.get("line")
        if line is None:
            line = 1
        deps["inherits"].append({"from": frm, "to": e.get("target"), "line": line})
    # IMPLEMENTS (있으면)
    for e in edges:
        if e.get("kind") != "IMPLEMENTS":
            continue
        frm = rel_qualified(e.get("source"))
        if not is_inside_repo(frm.split("::")[0]):
            continue
        line = e.get("line")
        if line is None:
            line = 1
        deps["implements"].append({"from": frm, "to": e.get("target"), "line": line})

    # contains: api exports의 parent_name에서 파생 (deep-wiki와 동일)
    for f in api_files:
        for ex in f["exports"]:
            if ex["parent_name"]:
                deps["contains"].append({"file": f["path"], "class": ex["parent_name"],
                                         "method": ex["name"], "line": ex["line"]})

    # CALLS: resolved(양끝 ::) + bare 2차 해소
    recovered = 0
    bare_total = 0
    for e in edges:
        if e.get("kind") != "CALLS":
            continue
        frm = rel_qualified(e.get("source"))
        from_file = frm.split("::")[0]
        if not is_inside_repo(from_file):
            continue
        target = e.get("target") or ""
        line = e.get("line")
        if line is None:
            line = 1

        if "::" in target:
            # 이미 해소됨 — 상대화
            to = rel_qualified(target)
            if is_inside_repo(to.split("::")[0]):
                deps["calls"].append({"from": frm, "to": to, "line": line})
            else:
                deps["unresolved_calls"].append(
                    {"from": frm, "callee": target.split("::")[-1], "line": line})
            continue

        # bare — 2차 해소 시도
        bare_total += 1
        callee = target
        to_file = None
        if callee in symbol_map.get(from_file, ()):
            to_file = from_file                                # same-file 정의
        else:
            defs = global_symbol_index.get(callee)
            if defs and len(defs) == 1:
                to_file = next(iter(defs))                     # 전역 유일 정의 (모호하지 않음)
        if to_file:
            deps["calls"].append({"from": frm, "to": f"{to_file}::{callee}", "line": line})
            recovered += 1
        else:
            deps["unresolved_calls"].append({"from": frm, "callee": callee, "line": line})

    # depends_on: directory-level edges derived from the internal imports.
    dir_deps = {}
    for imp in deps["internal"]:
        from_dir = "/".join(imp["from"].split("/")[:-1]) if "/" in imp["from"] else "."
        to_abs = imp["to"]
        if imp["to"].startswith("./") or imp["to"].startswith("../"):
            to_abs = posixpath.normpath(posixpath.join(from_dir, imp["to"]))
            # path.posix.normalize 는 trailing '/'를 보존하지만 normpath 는 제거한다.
            if imp["to"].endswith("/") and not to_abs.endswith("/"):
                to_abs += "/"
        to_dir = "/".join(to_abs.split("/")[:-1]) if "/" in to_abs else "."
        if from_dir != to_dir:
            key = f"{from_dir}→{to_dir}"
            if key not in dir_deps:
                dir_deps[key] = {"from": from_dir, "to": to_dir, "kind": "module"}
    deps["depends_on"] = list(dir_deps.values())

    # tested_by: a call from a test file into non-test code.
    for c in deps["calls"]:
        from_file = c["from"].split("::")[0]
        to_file = c["to"].split("::")[0]
        if is_test_file_path(from_file) and not is_test_file_path(to_file):
            deps["tested_by"].append({"production": c["to"], "test": c["from"],
                                      "line": c["line"]})

    # files[]
    deps["files"] = [{"path": f["path"],
                      "language": f["language"],
                      "is_test": is_test_file_path(f["path"]),
                      "export_count": len(f["exports"])} for f in api_files]

    # 정렬
    for k in ("internal", "external"):
        deps[k].sort(key=lambda x: (x["from"], x["line"]))

    # ── 출력 ─────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(out_api) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(out_deps) or ".", exist_ok=True)
    _write(out_api, json.dumps(api_result, indent=2, ensure_ascii=False) + "\n")
    _write(out_deps, json.dumps(deps, indent=2, ensure_ascii=False) + "\n")

    # metadata.json + README.md — provenance for the generated .ast/ tree.
    ast_dir = os.path.dirname(out_api)
    total_exports = sum(len(f["exports"]) for f in api_files)
    _write(os.path.join(ast_dir, "metadata.json"),
           json.dumps({"repoRoot": REPO_ROOT, "lang": lang_label,
                       "extractor": "ast_adapter.py (code2spec tree-sitter)",
                       "include": "code2spec code-to-ast graph"},
                      indent=2, ensure_ascii=False) + "\n")
    _write(os.path.join(ast_dir, "README.md"),
           "# .ast/ — Deterministic AST baseline (code2spec-derived)\n\n"
           "code2spec code-to-ast(tree-sitter) 그래프를 deep-wiki 스키마로 변환한 검증 재현용 baseline.\n\n"
           "| 항목 | 값 |\n|---|---|\n"
           f"| sourceRepo | `{REPO_ROOT}` |\n| extractor | `ast_adapter.py` |\n"
           f"| files | {len(api_files)} |\n| symbols | {total_exports} |\n")

    print(f"[adapter] api.json — {len(api_files)} files, {total_exports} symbols",
          file=sys.stderr)
    print(f"[adapter] deps.json — internal:{len(deps['internal'])} "
          f"external:{len(deps['external'])} "
          f"calls:{len(deps['calls'])} (bare 2차해소 {recovered}/{bare_total}) "
          f"unresolved:{len(deps['unresolved_calls'])} "
          f"inherits:{len(deps['inherits'])} implements:{len(deps['implements'])} "
          f"contains:{len(deps['contains'])} "
          f"depends_on:{len(deps['depends_on'])} tested_by:{len(deps['tested_by'])} "
          f"files:{len(deps['files'])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
