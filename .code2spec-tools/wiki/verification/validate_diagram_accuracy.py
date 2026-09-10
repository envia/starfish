#!/usr/bin/env python3
"""L5 diagram accuracy: are the edges drawn in the wiki's mermaid diagrams real?

Every edge of every ``graph``/``flowchart`` block is looked up against the code's own
relations (the AST import graph, plus calls/inherits/implements/contains/depends_on
when the extractor produced them) and graded:

* **supported** — the relation exists in the code
* **questionable** — both endpoints are known, but no relation connects them
* **unknown-node** — an endpoint is not a name found anywhere in the code
* **external** — an endpoint is explicitly marked external, so the edge is not scored

Two limits are inherent: runtime coupling that is not an import (an HTTP boundary, a
shared SQLite file) does not appear in the AST at all, and the mermaid parsing is
regex-based, so a complex label (multi-line, HTML tags) may not be read exactly.

Usage:
  python3 validate_diagram_accuracy.py [<deps-json>] <wiki-dir> [--graph-json <path>]
    [--threshold 0.7]

  <deps-json>     .ast/deps.json. Optional — a repo the TypeScript extractor cannot
                  read can pass only --graph-json.
  <wiki-dir>      wiki root
  --graph-json    graphify graph.json (NetworkX node_link_data), which also covers
                  C/C++ and other languages
  --threshold     passing edge-support ratio (default 0.7)
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import sys
import traceback
from collections.abc import Iterator
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

# External system names that recur in this domain; an edge touching one of these
# is treated as a known endpoint even though no code declares it.
KNOWN_EXTERNAL_SYSTEMS = {
    "qdrant", "openai", "gauss", "github", "gitlab", "bitbucket", "ad", "sso", "oidc",
    "allowlist", "artifactory", "pm2", "sqlite", "redis", "postgres", "mysql",
    "http", "https", "grpc", "websocket", "sse", "fetch",
    "llm", "mcp", "rag", "kpi", "python", "node",
    "tizen.org", "samsung", "aws", "gcp", "azure",
    "client", "server", "browser", "user", "host",
}

_MERMAID_BLOCK_RE = re.compile(r"^```mermaid\s*\n([\s\S]*?)\n```", re.M)
_GRAPH_TYPE_RE = re.compile(r"^(graph|flowchart)(?![A-Za-z0-9_])", re.IGNORECASE)
# A node's bracket-delimited label, matched per opening-bracket type so a closing
# character that belongs to a *different* bracket pair (e.g. the `)` in a `[...]`
# label's parenthetical aside, "mcp-server (HTTP)") doesn't truncate the match early.
_BRACKET_LABEL_RE = r"(?:\s*(?:\[[^\]]*\]|\([^)]*\)|<[^>]*>|\{[^}]*\}))?"
# A trailing Mermaid class-assignment shorthand, e.g. `Node["label"]:::external`.
_CLASS_SUFFIX_RE = r"(?:\s*:::[A-Za-z_][A-Za-z0-9_\-]*)?"
_EDGE_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_.\-]*)" + _BRACKET_LABEL_RE + _CLASS_SUFFIX_RE + r"\s*"
    r"(-->|-\.->|==>|---|-\.-|===)(?:\s*\|[^|]*\|)?\s*"
    r"([A-Za-z_][A-Za-z0-9_.\-]*)" + _BRACKET_LABEL_RE + _CLASS_SUFFIX_RE)
_INLINE_EXTERNAL_RE = re.compile(
    r"([A-Za-z_][A-Za-z0-9_.\-]*)" + _BRACKET_LABEL_RE + r"\s*:::external(?![A-Za-z0-9_])")
_CLASS_EXTERNAL_RE = re.compile(
    r"^\s*class\s+([A-Za-z_][A-Za-z0-9_.,\s\-]*?)\s+external\s*;?\s*$")


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


def as_text(value: Any) -> str:
    """A JSON-derived value as a string; a missing/null value becomes ""."""
    return "" if value is None else str(value)


def stem(path: str) -> str:
    """Filename without its extension (``pkg/svc.ts`` → ``svc``)."""
    return posixpath.splitext(posixpath.basename(path.rstrip("/")))[0]


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


def extract_mermaid_blocks(text: str) -> list[str]:
    """The body of every ```mermaid block on a page."""
    return [m.group(1) for m in _MERMAID_BLOCK_RE.finditer(text)]


def parse_edges(block: str) -> list[dict[str, str]]:
    """Edges of a graph/flowchart block; other diagram types have no edges to grade."""
    parts = block.strip().split("\n")
    first_line = parts[0] if parts else ""
    if not _GRAPH_TYPE_RE.search(first_line):
        return []
    edges: list[dict[str, str]] = []
    for line in block.split("\n"):
        for m in _EDGE_RE.finditer(line):
            edges.append({"from": m.group(1), "op": m.group(2), "to": m.group(3)})
    return edges


def external_ids(block: str) -> set[str]:
    """Nodes a diagram explicitly marks as external, so their edges are not scored.

    Both mermaid spellings are recognised: the inline ``NodeId:::external`` and the
    ``class NodeId1,NodeId2 external`` statement.
    """
    ids: set[str] = set()
    for line in block.split("\n"):
        for m in _INLINE_EXTERNAL_RE.finditer(line):
            ids.add(m.group(1))
        cm = _CLASS_EXTERNAL_RE.match(line)
        if cm:
            for id_ in (s.strip() for s in cm.group(1).split(",")):
                if id_:
                    ids.add(id_)
    return ids


def symbol_forms(value: Any) -> list[str]:
    """Every lowercase token a ``file::Symbol`` (or bare ``Symbol``) could match as.

    Returns the whole string, the part after ``::``, and the file's name without its
    extension, so a diagram may cite any of the three.
    """
    forms: list[str] = []
    raw = as_text(value).strip() if value else ""
    if not raw:
        return forms
    forms.append(raw.lower())
    sep_idx = raw.find("::")
    if sep_idx >= 0:
        file_part = raw[:sep_idx]
        sym_part = raw[sep_idx + 2:]
        if sym_part:
            forms.append(sym_part.lower())
        base = stem(file_part)
        if base:
            forms.append(base.lower())
    return forms


def build_known_set(deps: dict[str, Any]) -> set[str]:
    """Every lowercase name a diagram node is allowed to refer to."""
    known: set[str] = set()
    # Package / workspace names
    for ext in (deps.get("external") or []):
        if ext.get("from"):
            known.add(ext["from"].lower())
        if ext.get("to"):
            known.add(ext["to"].lower())
    for int_ in (deps.get("internal") or []):
        if int_.get("from"):
            known.add(int_["from"].lower())
            # The bare filename is a candidate too, not just the full path.
            base = stem(int_["from"])
            known.add(base.lower())
        if int_.get("to"):
            known.add(int_["to"].lower())
            base = stem(re.sub(r"^@[^/]+/", "", int_["to"]))
            known.add(base.lower())
    # packageGraph (workspace dependencies) — legacy schema.
    pkg_graph = deps.get("packageGraph") or deps.get("workspaceGraph") or {}
    if isinstance(pkg_graph, dict):
        for k in pkg_graph.keys():
            known.add(k.lower())
        for arr in pkg_graph.values():
            if isinstance(arr, list):
                for v in arr:
                    known.add(as_text(v).lower())
    # depends_on (directory/module level dependencies) — current schema
    for d in (deps.get("depends_on") or []):
        if d.get("from"):
            known.add(as_text(d["from"]).lower())
        if d.get("to"):
            known.add(as_text(d["to"]).lower())
    # calls / inherits / implements (`file::Symbol` relations) — symbol/class names
    for arr in ((deps.get("calls") or []), (deps.get("inherits") or []),
                (deps.get("implements") or [])):
        for rel in arr:
            for form in symbol_forms(rel.get("from")):
                known.add(form)
            for form in symbol_forms(rel.get("to")):
                known.add(form)
    # contains (class → method) — class and method names
    for c in (deps.get("contains") or []):
        if c.get("class"):
            known.add(as_text(c["class"]).lower())
        if c.get("method"):
            known.add(as_text(c["method"]).lower())
    # Well-known external systems
    for s in KNOWN_EXTERNAL_SYSTEMS:
        known.add(s)
    return known


def build_edge_index(deps: dict[str, Any]) -> set[str]:
    """``from->to`` keys for every directed relation the code actually declares."""
    idx: set[str] = set()
    for i in (deps.get("internal") or []):
        if i.get("from") and i.get("to"):
            idx.add(f"{i['from'].lower()}->{i['to'].lower()}")
    for e in (deps.get("external") or []):
        if e.get("from") and e.get("to"):
            idx.add(f"{e['from'].lower()}->{e['to'].lower()}")
    # packageGraph as well — legacy schema
    pkg_graph = deps.get("packageGraph") or deps.get("workspaceGraph") or {}
    if isinstance(pkg_graph, dict):
        for from_, arr in pkg_graph.items():
            if isinstance(arr, list):
                for to in arr:
                    idx.add(f"{from_.lower()}->{as_text(to).lower()}")

    # Current-schema relations: register the cross product of both ends' candidate
    # forms, so a diagram citing either spelling still resolves.
    def add_rel_edges(rel: dict[str, Any]) -> None:
        froms = symbol_forms(rel.get("from"))
        tos = symbol_forms(rel.get("to"))
        for f in froms:
            for t in tos:
                idx.add(f"{f}->{t}")
    for rel in (deps.get("calls") or []):
        add_rel_edges(rel)
    for rel in (deps.get("inherits") or []):
        add_rel_edges(rel)
    for rel in (deps.get("implements") or []):
        add_rel_edges(rel)
    for d in (deps.get("depends_on") or []):
        if d.get("from") and d.get("to"):
            idx.add(f"{as_text(d['from']).lower()}->{as_text(d['to']).lower()}")
    return idx


def merge_graphify_into(graph: dict[str, Any], known: set[str],
                        edge_idx: set[str]) -> tuple[int, int]:
    """Union a graphify graph into the known-name set and the edge index, in place."""
    added_nodes = 0
    added_edges = 0
    for n in (graph.get("nodes") or []):
        id_ = as_text(n.get("id")).lower()
        label = as_text(n.get("label")).lower()
        norm_label = as_text(n.get("norm_label")).lower()
        label_stripped = re.sub(r"\s*\([^)]*\)\s*$", "", label).strip()
        if id_:
            known.add(id_)
        if label:
            known.add(label)
        if norm_label:
            known.add(norm_label)
        if label_stripped:
            known.add(label_stripped)
        sf = as_text(n.get("source_file")).lower()
        if sf:
            known.add(sf)
            base = sf.split("/")[-1] if sf.split("/") else ""
            if base:
                known.add(base)
                base_no_ext = re.sub(r"\.[^.]+$", "", base)
                if base_no_ext:
                    known.add(base_no_ext)
            for p in sf.split("/"):
                if p:
                    known.add(p)
        added_nodes += 1
    for e in (graph.get("links") or []):
        if e.get("source") and e.get("target"):
            s = as_text(e["source"]).lower()
            t = as_text(e["target"]).lower()
            edge_idx.add(f"{s}->{t}")
            added_edges += 1
    return added_nodes, added_edges


def classify(node: str, known: set[str]) -> str:
    """Whether a diagram node names something the code knows about."""
    n = node.lower()
    if n in known:
        return "known"
    # Weak match: a known token contained in the node name (or vice versa) counts,
    # so `AuthService` still resolves against `auth-service`.
    for k in known:
        if len(k) >= 4 and (k in n or n in k):
            return "known"
    return "unknown"


def edge_supported(from_: str, to: str, known: set[str],
                   edge_idx: set[str]) -> str:
    """Grade one diagram edge: supported / questionable / unknown-node."""
    f = classify(from_, known)
    t = classify(to, known)
    if f == "unknown" or t == "unknown":
        return "unknown-node"
    if f"{from_.lower()}->{to.lower()}" in edge_idx:
        return "supported"
    # Substring fallback, for when only one end matches a declared name exactly
    for key in edge_idx:
        a, _, b = key.partition("->")
        if from_.lower() in a and to.lower() in b:
            return "supported"
    return "questionable"


def main() -> int:
    args = parse_args(sys.argv[1:])
    # Positionals come in two shapes: `<deps-json> <wiki-dir>`, or just `<wiki-dir>`
    # when the relations come from --graph-json instead.
    deps_json = None
    wiki_dir = None
    if len(args["positional"]) == 2:
        deps_json, wiki_dir = args["positional"]
    elif len(args["positional"]) == 1:
        wiki_dir = args["positional"][0]
    else:
        print("Usage: python3 validate_diagram_accuracy.py [<deps-json>] <wiki-dir> "
              "[--graph-json X] [--threshold 0.7]", file=sys.stderr)
        return 2
    graph_json = args.get("graph-json")
    if not wiki_dir:
        print("Missing <wiki-dir>", file=sys.stderr)
        return 2
    if not deps_json and not graph_json:
        print("Must provide <deps-json> (positional) or --graph-json (or both)",
              file=sys.stderr)
        return 2
    threshold = parse_ratio(args.get("threshold"), 0.7)

    sources: list[str] = []
    deps: dict[str, Any] = {"internal": [], "external": [], "packageGraph": {}}
    if deps_json:
        try:
            with open(deps_json, encoding="utf-8", errors="replace") as f:
                deps = json.loads(f.read())
        except Exception as e:
            print(f"Failed to read deps json: {e}", file=sys.stderr)
            return 3
        sources.append(f"deps-json ({len(deps.get('internal') or [])} internal + "
                       f"{len(deps.get('external') or [])} external edges)")

    known = build_known_set(deps)
    edge_idx = build_edge_index(deps)

    if graph_json:
        try:
            with open(graph_json, encoding="utf-8", errors="replace") as f:
                graph = json.loads(f.read())
        except Exception as e:
            print(f"Failed to read graph json: {e}", file=sys.stderr)
            return 3
        added_nodes, added_edges = merge_graphify_into(graph, known, edge_idx)
        sources.append(f"graphify (+{added_nodes} nodes, +{added_edges} edges)")

    all_edges: list[dict[str, Any]] = []   # {file, from, op, to, status}
    mermaid_files = 0
    total_blocks = 0
    for fp in walk_markdown(wiki_dir):
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            continue
        blocks = extract_mermaid_blocks(text)
        if len(blocks) == 0:
            continue
        mermaid_files += 1
        total_blocks += len(blocks)
        for blk in blocks:
            ext = external_ids(blk)
            edges = parse_edges(blk)
            for e in edges:
                status = "external" if (e["from"] in ext or e["to"] in ext) \
                    else edge_supported(e["from"], e["to"], known, edge_idx)
                all_edges.append({"file": os.path.relpath(fp, wiki_dir), **e,
                                  "status": status})

    counts = {"supported": 0, "questionable": 0, "unknown-node": 0, "external": 0}
    for e in all_edges:
        counts[e["status"]] += 1
    # The denominator excludes explicitly-external edges. An empty denominator
    # reports N/A rather than a fake 100%.
    verifiable = len(all_edges) - counts["external"]
    is_empty = verifiable == 0
    supported_ratio = 0.0 if is_empty else counts["supported"] / verifiable

    print("L5 Diagram Accuracy")
    print(f"  sources:         {' + '.join(sources)}")
    print(f"  wiki:            {wiki_dir}")
    print(f"  mermaid files:   {mermaid_files}")
    print(f"  mermaid blocks:  {total_blocks}")
    print(f"  parsed edges:    {len(all_edges)} (verifiable {verifiable}, "
          f"external {counts['external']} 제외)")
    ratio_text = "N/A" if is_empty else format_pct(supported_ratio * 100, 1) + "%"
    print(f"    supported:      {counts['supported']}  ({ratio_text})")
    print(f"    questionable:   {counts['questionable']}  (likely fictional)")
    print(f"    unknown-node:   {counts['unknown-node']}  (자유 이름)")
    print(f"    external:       {counts['external']}  (명시적 외부 노드, 채점 제외)")
    print(f"  threshold:       {format_pct(threshold * 100, 0)}%")
    print()

    flagged = [e for e in all_edges
               if e["status"] != "supported" and e["status"] != "external"]
    if len(flagged) > 0:
        print(f"  미지원 edge {len(flagged)}개:")
        for e in flagged[:40]:
            print(f"    [{e['status'].ljust(13)}] {e['from']} {e['op']} {e['to']}   "
                  f"in {e['file']}")
        if len(flagged) > 40:
            print(f"    ... (+{len(flagged) - 40} more)")

    if is_empty:
        print("\nN/A — no graph/flowchart edges parsed (nothing to validate)")
        return 0
    if supported_ratio < threshold:
        print(f"\n❌ supported edges {format_pct(supported_ratio * 100, 1)}% < threshold "
              f"{format_pct(threshold * 100, 0)}%", file=sys.stderr)
        return 1
    print(f"\n✅ supported edges {format_pct(supported_ratio * 100, 1)}% ≥ threshold "
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
